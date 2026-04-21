#!/usr/bin/env python3
"""
llm_re_extraction.py — 使用 OpenAI API (gpt-4.1-mini) 对 test_A 中无关系样本进行关系抽取

策略：
1. 针对 111 个无关系样本，用 LLM 尝试抽取关系
2. 针对缺口大的类型（GENE-LOI-TRT gap=9, CROP-CON-GENE gap=10, MRK-LOI-CHR gap=11,
   VAR-USE-BM gap=7, CROP-HAS-TRT gap=5, TRT-AFF-TRT gap=3）
3. Few-shot 提示：从训练集中选取 3-5 个高质量示例
4. 输出格式：严格 JSON，只输出在已有实体中找到的关系
5. 双重验证：LLM 输出的关系必须 head/tail 都在 entities 列表中

成本估算：
- 111 个样本，每个约 300 token 输入 + 100 token 输出
- gpt-4.1-mini: $0.4/1M input + $1.6/1M output
- 约 111 * (300+100) token = 44,400 token ≈ $0.02，极低成本

底座：submit_v36_gene_abs（当前最高分 0.4487）
"""
import json
import os
import zipfile
import time
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
from openai import OpenAI

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v36_gene_abs.json'
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
REPORT = Path('/home/ubuntu/bisai/分析报告/llm_re_report.txt')
CACHE = Path('/home/ubuntu/bisai/分析报告/llm_re_cache.json')

client = OpenAI()

# 关系类型定义（用于提示词）
REL_DEFS = {
    'AFF': 'affects/influences (e.g., gene affects trait, QTL affects trait)',
    'LOI': 'located in/on (e.g., QTL located in chromosome, gene located in trait region)',
    'HAS': 'has/contains (e.g., crop has trait, variety has trait)',
    'CON': 'contains/includes (e.g., crop contains variety, cross contains variety)',
    'USE': 'uses/utilizes (e.g., variety uses biomarker)',
    'OCI': 'occurs in (e.g., trait occurs in germplasm)',
}

ENTITY_DEFS = {
    'CROP': 'crop species (e.g., rice, wheat, maize, soybean)',
    'VAR': 'variety/cultivar/genotype/line (e.g., IR64, Nipponbare)',
    'GENE': 'gene/allele (e.g., OsGW5, Ghd7)',
    'TRT': 'trait/phenotype (e.g., grain weight, plant height, yield)',
    'QTL': 'quantitative trait locus (e.g., qGW5, qSW5)',
    'MRK': 'molecular marker (e.g., SSR marker, SNP)',
    'CHR': 'chromosome (e.g., chromosome 1, Chr3)',
    'ABS': 'abstract/study subject (the main topic of the sentence)',
    'BM': 'biomarker/biochemical marker',
    'CROSS': 'cross/hybrid/population',
    'GST': 'germplasm/strain/accession',
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


def build_few_shot_examples(train_data, n=4):
    """从训练集中选取高质量的 few-shot 示例（有多种关系类型的样本）"""
    # 选取有 2-4 条关系的样本，覆盖多种类型
    candidates = [x for x in train_data if 2 <= len(x.get('relations', [])) <= 4]
    # 按关系多样性排序
    candidates.sort(key=lambda x: len(set(r['label'] for r in x['relations'])), reverse=True)
    return candidates[:n]


def format_entity_list(entities):
    """格式化实体列表用于提示词"""
    lines = []
    for e in entities:
        lines.append(f'  - [{e["label"]}] "{e["text"]}" (pos {e["start"]}-{e["end"]})')
    return '\n'.join(lines)


def format_relation_list(relations):
    """格式化关系列表用于提示词"""
    lines = []
    for r in relations:
        lines.append(f'  - {r["head_type"]}("{r["head"]}") --{r["label"]}--> {r["tail_type"]}("{r["tail"]}")')
    return '\n'.join(lines)


def build_prompt(item, few_shot_examples):
    """构建关系抽取提示词"""
    # 实体类型定义
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

    # 构建实体名称到类型的映射（用于验证）
    ent_map = {e['text']: e['label'] for e in entities}

    prompt = f"""You are an expert in agricultural/plant breeding information extraction.

Entity types:
{ent_def_str}

Relation types:
{rel_def_str}

IMPORTANT RULES:
1. Only extract relations between entities that are EXPLICITLY listed in the Entities section
2. Use EXACT entity text as shown in the entities list
3. Only output relations that are clearly supported by the text
4. Output format: JSON array of objects with keys: head, head_type, label, tail, tail_type
5. If no relations exist, output empty array: []
{examples_str}
Now extract relations for:
Text: {text}
Entities:
{ent_str}

Output JSON array only (no explanation):"""

    return prompt, ent_map


def call_llm(prompt, model="gpt-4.1-mini", max_retries=3):
    """调用 LLM API"""
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


# 训练集中存在的有效关系类型（从训练集动态加载）
VALID_REL_TYPES = None

def get_valid_rel_types():
    global VALID_REL_TYPES
    if VALID_REL_TYPES is None:
        train = load(TRAIN)
        VALID_REL_TYPES = set()
        for x in train:
            for r in x.get('relations', []):
                VALID_REL_TYPES.add((r['head_type'], r['label'], r['tail_type']))
    return VALID_REL_TYPES

def parse_llm_output(output, ent_map):
    """解析 LLM 输出，验证实体存在性"""
    # 提取 JSON 部分
    output = output.strip()
    if output.startswith('```'):
        lines = output.split('\n')
        output = '\n'.join(lines[1:-1])

    try:
        relations = json.loads(output)
    except json.JSONDecodeError:
        # 尝试找到 JSON 数组
        import re
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

    # 验证每条关系
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
        # 验证实体类型匹配
        if ent_map[head] != head_type or ent_map[tail] != tail_type:
            head_type = ent_map[head]
            tail_type = ent_map[tail]
        # 验证关系类型（必须在 REL_DEFS 中，且 (head_type, label, tail_type) 必须在训练集中存在）
        if label not in REL_DEFS:
            continue
        valid_types = get_valid_rel_types()
        if (head_type, label, tail_type) not in valid_types:
            continue

        valid_rels.append({
            'head': head,
            'head_type': head_type,
            'label': label,
            'tail': tail,
            'tail_type': tail_type,
        })

    return valid_rels


def main():
    print("加载数据...")
    base = load(BASE)
    train = load(TRAIN)

    # 加载缓存
    cache = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding='utf-8'))
        print(f"已加载缓存: {len(cache)} 条")

    # 选取 few-shot 示例
    few_shot = build_few_shot_examples(train, n=4)
    print(f"Few-shot 示例数: {len(few_shot)}")

    # 找出无关系样本（按索引）
    no_rel_indices = [i for i, x in enumerate(base) if not x.get('relations')]
    print(f"无关系样本数: {len(no_rel_indices)}")

    # 处理每个无关系样本
    results = {}
    total_added = 0
    skipped = 0

    for i, idx in enumerate(no_rel_indices):
        item = base[idx]
        cache_key = str(idx)

        if cache_key in cache:
            results[idx] = cache[cache_key]
            skipped += 1
            continue

        if not item.get('entities'):
            results[idx] = []
            cache[cache_key] = []
            continue

        print(f"  [{i+1}/{len(no_rel_indices)}] 处理样本 {idx}...")
        prompt, ent_map = build_prompt(item, few_shot)
        output = call_llm(prompt)
        rels = parse_llm_output(output, ent_map)
        results[idx] = rels
        cache[cache_key] = rels
        total_added += len(rels)

        # 每10个保存一次缓存
        if (i + 1) % 10 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"  已处理 {i+1}/{len(no_rel_indices)}，新增关系 {total_added} 条")

        time.sleep(0.1)  # 避免速率限制

    # 保存最终缓存
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

    # 统计结果
    print(f"\n处理完成！跳过（缓存）: {skipped}, 新处理: {len(no_rel_indices)-skipped}")
    total_from_cache = sum(len(v) for v in cache.values())
    print(f"总新增关系: {total_from_cache}")

    # 关系类型分布
    type_counter = Counter()
    for rels in cache.values():
        for r in rels:
            type_counter[(r['head_type'], r['label'], r['tail_type'])] += 1
    print("关系类型分布:")
    for t, n in type_counter.most_common(15):
        print(f"  {t[0]}-{t[1]}-{t[2]}: {n}")

    # 生成新版本
    data = deepcopy(base)
    added_count = 0
    for idx_str, rels in cache.items():
        idx = int(idx_str)
        if idx < len(data) and rels:
            # 将 LLM 关系添加到样本中
            existing = {(r['head'].strip().lower(), r['head_type'], r['label'],
                         r['tail'].strip().lower(), r['tail_type'])
                        for r in data[idx].get('relations', [])}
            for r in rels:
                key = (r['head'].strip().lower(), r['head_type'], r['label'],
                       r['tail'].strip().lower(), r['tail_type'])
                if key not in existing:
                    # 需要添加 start/end 位置信息
                    text = data[idx]['text']
                    entities = {e['text']: e for e in data[idx].get('entities', [])}
                    h_ent = entities.get(r['head'])
                    t_ent = entities.get(r['tail'])
                    if h_ent and t_ent:
                        full_rel = {
                            'head': r['head'],
                            'head_type': r['head_type'],
                            'head_start': h_ent['start'],
                            'head_end': h_ent['end'],
                            'tail': r['tail'],
                            'tail_type': r['tail_type'],
                            'tail_start': t_ent['start'],
                            'tail_end': t_ent['end'],
                            'label': r['label'],
                        }
                        data[idx]['relations'].append(full_rel)
                        added_count += 1
                        existing.add(key)

    print(f"\n实际添加到提交文件的关系: {added_count}")

    # 保存版本
    name = 'submit_v38_llm_no_rel'
    save_json_zip(name, data)
    print(f"已保存: {name}.zip")

    # 报告
    report = [
        f"base={BASE} (score=0.4487)",
        f"策略: 对 {len(no_rel_indices)} 个无关系样本用 gpt-4.1-mini 抽取关系",
        f"实际添加关系: {added_count}",
        f"关系类型分布:",
    ]
    for t, n in type_counter.most_common(15):
        report.append(f"  {t[0]}-{t[1]}-{t[2]}: {n}")
    REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
    print(f"报告已写入: {REPORT}")


if __name__ == '__main__':
    main()
