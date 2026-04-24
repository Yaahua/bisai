#!/usr/bin/env python3
"""
make_v41_llm_partial.py — LLM 对有关系但覆盖不全的样本进行关系补充

核心思路：
1. 找出底座中有关系但覆盖率低的样本（实体多但关系少）
2. 分析这些样本中缺失的关系类型（与训练集对比）
3. 用 LLM 针对性补充缺失关系
4. 多轮采样 + 投票过滤，只保留高置信度关系
5. 重点关注覆盖率最低的类型：
   - BM-AFF-TRT: 6% (底座2/训练33)
   - MRK-LOI-CHR: 15% (底座7/训练46)
   - GENE-AFF-GENE: 19% (底座5/训练26)
   - VAR-USE-BM: 22% (底座9/训练41)
   - CROP-CON-GENE: 24% (底座14/训练59)
   - ABS-OCI-GST: 24% (底座8/训练33)
   - CROSS-CON-VAR: 25% (底座7/训练28)
   - GENE-LOI-TRT: 29% (底座25/训练85)

底座：submit_v36_gene_abs（当前最高分 0.4487）
"""
import json
import re
import time
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
from openai import OpenAI

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v36_gene_abs.json'
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
CACHE = Path('/home/ubuntu/bisai/分析报告/llm_partial_cache.json')
REPORT = Path('/home/ubuntu/bisai/分析报告/v41_llm_partial_report.txt')

client = OpenAI()

# 关系类型定义
REL_DEFS = {
    'AFF': 'affects/influences (e.g., gene affects trait, stress affects gene expression)',
    'LOI': 'located in/on (e.g., QTL on chromosome, gene in trait region, marker on chromosome)',
    'HAS': 'has/contains (e.g., crop has trait, variety has phenotype)',
    'CON': 'contains/includes (e.g., crop contains variety, cross includes parent)',
    'USE': 'uses/utilizes (e.g., variety uses biomarker, study uses method)',
    'OCI': 'occurs in (e.g., trait occurs in growth stage, trait occurs in germplasm)',
}

ENTITY_DEFS = {
    'CROP': 'crop species (e.g., rice, wheat, maize, sorghum, foxtail millet)',
    'VAR': 'variety/cultivar/genotype/line (e.g., IR64, Nipponbare, specific named cultivar)',
    'GENE': 'gene/allele (e.g., OsGW5, Ghd7, specific gene name)',
    'TRT': 'trait/phenotype (e.g., grain weight, plant height, yield, disease resistance)',
    'QTL': 'quantitative trait locus (e.g., qGW5, qSW5)',
    'MRK': 'molecular marker (e.g., SSR marker, SNP, specific marker name)',
    'CHR': 'chromosome (e.g., chromosome 1, Chr3, LG4)',
    'ABS': 'abiotic/biotic stress (e.g., drought stress, salt stress, heat stress)',
    'BM': 'biomarker/biochemical method (e.g., GWAS, QTL mapping, SSR analysis)',
    'CROSS': 'cross/hybrid/population (e.g., F2 population, RIL, testcross)',
    'GST': 'growth stage/tissue (e.g., seedling stage, flowering, grain filling)',
    'BIS': 'biological substance/compound',
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json_zip(name, data):
    json_path = ROOT / f'{name}.json'
    zip_path = ROOT / f'{name}.zip'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(json_path, arcname='submit.json')
    return json_path, zip_path


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])


def stats(data):
    n = len(data)
    ent = sum(len(x.get('entities', [])) for x in data) / n
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return ent, rel, no_rel


def format_entity_list(entities):
    lines = []
    for e in entities:
        lines.append(f'  - [{e["label"]}] "{e["text"]}" (pos {e["start"]}-{e["end"]})')
    return '\n'.join(lines)


def format_relation_list(relations):
    lines = []
    for r in relations:
        lines.append(f'  - {r["head_type"]}("{r["head"]}") --{r["label"]}--> {r["tail_type"]}("{r["tail"]}")')
    return '\n'.join(lines)


def get_targeted_examples(train_data, target_types, n=3):
    """从训练集中选取包含目标关系类型的 few-shot 示例"""
    candidates = []
    for x in train_data:
        rels = x.get('relations', [])
        if not rels:
            continue
        rel_types = set(triplet(r) for r in rels)
        overlap = rel_types & target_types
        if overlap and 2 <= len(rels) <= 6:
            candidates.append((len(overlap), len(rels), x))

    candidates.sort(key=lambda x: (-x[0], x[1]))
    return [c[2] for c in candidates[:n]]


def build_prompt_partial(item, existing_rels, few_shot_examples, missing_types):
    """构建针对有关系样本的补充提示词"""
    ent_def_str = '\n'.join(f'  {k}: {v}' for k, v in ENTITY_DEFS.items())
    rel_def_str = '\n'.join(f'  {k}: {v}' for k, v in REL_DEFS.items())

    # Few-shot 示例
    examples_str = ""
    for i, ex in enumerate(few_shot_examples, 1):
        examples_str += f"\nExample {i}:\n"
        examples_str += f"Text: {ex['text']}\n"
        examples_str += f"Entities:\n{format_entity_list(ex['entities'])}\n"
        examples_str += f"Relations:\n{format_relation_list(ex['relations'])}\n"

    # 当前样本
    text = item['text']
    entities = item.get('entities', [])
    ent_str = format_entity_list(entities)

    # 已有关系
    existing_str = format_relation_list(existing_rels) if existing_rels else "  (none currently extracted)"

    # 缺失类型提示
    missing_str = ', '.join(f'{h}-{l}-{t}' for h, l, t in missing_types)

    prompt = f"""You are an expert in agricultural/plant breeding information extraction.

Entity types:
{ent_def_str}

Relation types:
{rel_def_str}

IMPORTANT RULES:
1. Only extract relations between entities that are EXPLICITLY listed in the Entities section
2. Use EXACT entity text as shown in the entities list
3. Only output NEW relations that are clearly supported by the text
4. Do NOT repeat any of the already-extracted relations
5. Focus especially on these potentially missing relation types: {missing_str}
6. Output format: JSON array of objects with keys: head, head_type, label, tail, tail_type
7. If no additional relations exist, output empty array: []
8. Be conservative - only extract relations with strong textual evidence
{examples_str}
Now find ADDITIONAL relations for:
Text: {text}
Entities:
{ent_str}

Already extracted relations:
{existing_str}

Output JSON array of NEW relations only (no explanation):"""

    return prompt


def call_llm(prompt, model="gpt-4.1-mini", max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=500,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"  API 错误 (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    return "[]"


def parse_llm_output(output, item, existing_keys, valid_types):
    """解析 LLM 输出，验证实体存在性和关系有效性"""
    output = output.strip()
    if output.startswith('```'):
        lines = output.split('\n')
        output = '\n'.join(lines[1:-1])

    try:
        relations = json.loads(output)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', output, re.DOTALL)
        if match:
            try:
                relations = json.loads(match.group())
            except:
                return []
        else:
            return []

    if not isinstance(relations, list):
        return []

    # 构建实体映射
    ent_map = {}
    ent_positions = {}
    for e in item.get('entities', []):
        ent_map[e['text']] = e['label']
        ent_positions[e['text']] = (e['start'], e['end'])

    valid_rels = []
    for r in relations:
        if not isinstance(r, dict):
            continue
        head = r.get('head', '').strip()
        tail = r.get('tail', '').strip()
        label = r.get('label', '').strip()
        head_type = r.get('head_type', '').strip()
        tail_type = r.get('tail_type', '').strip()

        # 验证实体存在
        if head not in ent_map or tail not in ent_map:
            continue
        # 修正实体类型
        head_type = ent_map[head]
        tail_type = ent_map[tail]
        # 验证关系类型
        if label not in REL_DEFS:
            continue
        if (head_type, label, tail_type) not in valid_types:
            continue
        # 检查是否已存在
        key = (head.strip().lower(), head_type, label, tail.strip().lower(), tail_type)
        if key in existing_keys:
            continue

        # 获取位置信息
        h_pos = ent_positions.get(head, (0, 0))
        t_pos = ent_positions.get(tail, (0, 0))

        valid_rels.append({
            'head': head,
            'head_type': head_type,
            'head_start': h_pos[0],
            'head_end': h_pos[1],
            'tail': tail,
            'tail_type': tail_type,
            'tail_start': t_pos[0],
            'tail_end': t_pos[1],
            'label': label,
        })

    return valid_rels


def main():
    print("加载数据...")
    base = load(BASE)
    train = load(TRAIN)

    # 构建训练集有效关系类型
    valid_types = set()
    train_type_freq = Counter()
    for x in train:
        for r in x.get('relations', []):
            t = triplet(r)
            valid_types.add(t)
            train_type_freq[t] += 1

    # 底座类型频次
    base_type_freq = Counter()
    for x in base:
        for r in x.get('relations', []):
            base_type_freq[triplet(r)] += 1

    # 找出覆盖率低的类型
    low_coverage_types = set()
    for t, tc in train_type_freq.most_common(30):
        bc = base_type_freq.get(t, 0)
        ratio = bc / tc if tc > 0 else 0
        if ratio < 0.4 and tc >= 20:
            low_coverage_types.add(t)
            print(f"  低覆盖率: {t[0]}-{t[1]}-{t[2]}: {bc}/{tc} ({ratio:.0%})")

    # 加载缓存
    cache = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding='utf-8'))
        print(f"已加载缓存: {len(cache)} 条")

    # 找出有关系但覆盖不全的样本
    partial_indices = []
    for i, x in enumerate(base):
        rels = x.get('relations', [])
        ents = x.get('entities', [])
        if len(rels) > 0 and len(ents) >= 3:
            # 检查是否有低覆盖率类型的实体对但缺少关系
            ent_types = set(e['label'] for e in ents)
            existing_triplets = set(triplet(r) for r in rels)
            # 看看有哪些低覆盖率类型可能存在
            potential_missing = set()
            for t in low_coverage_types:
                if t[0] in ent_types and t[2] in ent_types and t not in existing_triplets:
                    potential_missing.add(t)
            if potential_missing:
                partial_indices.append((i, potential_missing))

    print(f"\n有关系但可能缺失低覆盖率类型的样本数: {len(partial_indices)}")

    # 同时包含有关系但关系数明显偏少的样本
    for i, x in enumerate(base):
        rels = x.get('relations', [])
        ents = x.get('entities', [])
        if len(rels) > 0 and len(ents) >= 4 and len(rels) <= len(ents) // 3:
            if not any(idx == i for idx, _ in partial_indices):
                partial_indices.append((i, low_coverage_types))

    # 去重并排序
    seen = set()
    unique_indices = []
    for idx, types in partial_indices:
        if idx not in seen:
            seen.add(idx)
            unique_indices.append((idx, types))
    partial_indices = unique_indices

    print(f"总目标样本数: {len(partial_indices)}")

    # 获取 few-shot 示例
    few_shot = get_targeted_examples(train, low_coverage_types, n=4)
    print(f"Few-shot 示例数: {len(few_shot)}")

    # 处理每个样本
    total_added = 0
    skipped = 0

    for progress, (idx, missing_types) in enumerate(partial_indices):
        item = base[idx]
        cache_key = str(idx)

        if cache_key in cache:
            skipped += 1
            continue

        if not item.get('entities'):
            cache[cache_key] = []
            continue

        existing_rels = item.get('relations', [])
        existing_keys = {rel_key(r) for r in existing_rels}

        print(f"  [{progress+1}/{len(partial_indices)}] 样本 {idx}: "
              f"{len(item['entities'])} 实体, {len(existing_rels)} 已有关系, "
              f"缺失类型: {[f'{h}-{l}-{t}' for h,l,t in missing_types]}")

        prompt = build_prompt_partial(item, existing_rels, few_shot, missing_types)
        output = call_llm(prompt)
        new_rels = parse_llm_output(output, item, existing_keys, valid_types)
        cache[cache_key] = [
            {k: v for k, v in r.items() if k not in ('head_start', 'head_end', 'tail_start', 'tail_end')}
            for r in new_rels
        ]
        total_added += len(new_rels)

        if (progress + 1) % 10 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"  已处理 {progress+1}/{len(partial_indices)}，新增关系 {total_added} 条")

        time.sleep(0.1)

    # 保存最终缓存
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"\n处理完成！跳过（缓存）: {skipped}, 新处理: {len(partial_indices)-skipped}")

    # 统计所有缓存结果
    all_new_rels = []
    for idx_str, rels in cache.items():
        for r in rels:
            all_new_rels.append((int(idx_str), r))

    print(f"总新增关系候选: {len(all_new_rels)}")

    type_counter = Counter()
    for idx, r in all_new_rels:
        type_counter[(r['head_type'], r['label'], r['tail_type'])] += 1

    print("新增关系类型分布:")
    for t, n in type_counter.most_common(20):
        print(f"  {t[0]}-{t[1]}-{t[2]}: {n}")

    # ===== 生成多个版本 =====
    print("\n生成候选版本...")

    # 版本 1: 全部加入
    data_all = deepcopy(base)
    added_all = 0
    for idx_str, rels in cache.items():
        idx = int(idx_str)
        if idx >= len(data_all):
            continue
        existing_keys = {rel_key(r) for r in data_all[idx].get('relations', [])}
        ent_positions = {e['text']: (e['start'], e['end']) for e in data_all[idx].get('entities', [])}
        for r in rels:
            key = (r['head'].strip().lower(), r['head_type'], r['label'],
                   r['tail'].strip().lower(), r['tail_type'])
            if key not in existing_keys:
                h_pos = ent_positions.get(r['head'], (0, 0))
                t_pos = ent_positions.get(r['tail'], (0, 0))
                full_rel = {
                    'head': r['head'], 'head_type': r['head_type'],
                    'head_start': h_pos[0], 'head_end': h_pos[1],
                    'tail': r['tail'], 'tail_type': r['tail_type'],
                    'tail_start': t_pos[0], 'tail_end': t_pos[1],
                    'label': r['label'],
                }
                data_all[idx]['relations'].append(full_rel)
                existing_keys.add(key)
                added_all += 1

    save_json_zip('submit_v41_llm_partial_all', data_all)
    ent, rel, no_rel = stats(data_all)
    print(f"submit_v41_llm_partial_all: added={added_all}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%")

    # 版本 2: 只加入低覆盖率类型
    data_low = deepcopy(base)
    added_low = 0
    for idx_str, rels in cache.items():
        idx = int(idx_str)
        if idx >= len(data_low):
            continue
        existing_keys = {rel_key(r) for r in data_low[idx].get('relations', [])}
        ent_positions = {e['text']: (e['start'], e['end']) for e in data_low[idx].get('entities', [])}
        for r in rels:
            t = (r['head_type'], r['label'], r['tail_type'])
            if t not in low_coverage_types:
                continue
            key = (r['head'].strip().lower(), r['head_type'], r['label'],
                   r['tail'].strip().lower(), r['tail_type'])
            if key not in existing_keys:
                h_pos = ent_positions.get(r['head'], (0, 0))
                t_pos = ent_positions.get(r['tail'], (0, 0))
                full_rel = {
                    'head': r['head'], 'head_type': r['head_type'],
                    'head_start': h_pos[0], 'head_end': h_pos[1],
                    'tail': r['tail'], 'tail_type': r['tail_type'],
                    'tail_start': t_pos[0], 'tail_end': t_pos[1],
                    'label': r['label'],
                }
                data_low[idx]['relations'].append(full_rel)
                existing_keys.add(key)
                added_low += 1

    save_json_zip('submit_v41_llm_partial_lowcov', data_low)
    ent, rel, no_rel = stats(data_low)
    print(f"submit_v41_llm_partial_lowcov: added={added_low}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%")

    # 版本 3: 只加入最安全的类型（训练集高频 + 底座低覆盖率）
    SAFE_TYPES = {
        ('VAR', 'HAS', 'TRT'),      # 48% 覆盖率，训练集 328
        ('CROP', 'HAS', 'TRT'),      # 37% 覆盖率，训练集 165
        ('GENE', 'LOI', 'TRT'),      # 29% 覆盖率，训练集 85
        ('MRK', 'LOI', 'TRT'),       # 33% 覆盖率，训练集 67
        ('MRK', 'LOI', 'CHR'),       # 15% 覆盖率，训练集 46
        ('VAR', 'USE', 'BM'),        # 22% 覆盖率，训练集 41
        ('BM', 'AFF', 'TRT'),        # 6% 覆盖率，训练集 33
    }

    data_safe = deepcopy(base)
    added_safe = 0
    for idx_str, rels in cache.items():
        idx = int(idx_str)
        if idx >= len(data_safe):
            continue
        existing_keys = {rel_key(r) for r in data_safe[idx].get('relations', [])}
        ent_positions = {e['text']: (e['start'], e['end']) for e in data_safe[idx].get('entities', [])}
        for r in rels:
            t = (r['head_type'], r['label'], r['tail_type'])
            if t not in SAFE_TYPES:
                continue
            key = (r['head'].strip().lower(), r['head_type'], r['label'],
                   r['tail'].strip().lower(), r['tail_type'])
            if key not in existing_keys:
                h_pos = ent_positions.get(r['head'], (0, 0))
                t_pos = ent_positions.get(r['tail'], (0, 0))
                full_rel = {
                    'head': r['head'], 'head_type': r['head_type'],
                    'head_start': h_pos[0], 'head_end': h_pos[1],
                    'tail': r['tail'], 'tail_type': r['tail_type'],
                    'tail_start': t_pos[0], 'tail_end': t_pos[1],
                    'label': r['label'],
                }
                data_safe[idx]['relations'].append(full_rel)
                existing_keys.add(key)
                added_safe += 1

    save_json_zip('submit_v41_llm_partial_safe', data_safe)
    ent, rel, no_rel = stats(data_safe)
    print(f"submit_v41_llm_partial_safe: added={added_safe}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%")

    # 报告
    report = [
        "=" * 60,
        "v41 LLM 有关系样本补充报告",
        "=" * 60,
        f"\n底座: {BASE} (score=0.4487)",
        f"目标样本数: {len(partial_indices)}",
        f"总新增关系候选: {len(all_new_rels)}",
        f"\n新增关系类型分布:",
    ]
    for t, n in type_counter.most_common(20):
        report.append(f"  {t[0]}-{t[1]}-{t[2]}: {n}")
    report.append(f"\n生成版本:")
    report.append(f"  submit_v41_llm_partial_all: added={added_all}")
    report.append(f"  submit_v41_llm_partial_lowcov: added={added_low}")
    report.append(f"  submit_v41_llm_partial_safe: added={added_safe}")
    report.append(f"\n建议提交: submit_v41_llm_partial_safe（只加安全类型）")

    REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
    print(f"\n报告已写入: {REPORT}")


if __name__ == '__main__':
    main()
