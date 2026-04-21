"""
v39 系列：基于 POSW-Vote 方法的多次采样聚合
学术来源：Hoang Van Toan et al., "POSW-Vote", JMST 2025

策略：
1. 对 test_A 中 111 个无关系样本，再次用 LLM 运行 2 轮（加上已有 1 轮，共 3 轮）
2. 用 POSW-Vote 算法聚合：只保留在 ≥2/3 轮中出现的关系（多数投票）
3. 结合 Jaccard 相似度进行实体归一化（处理轻微变体）
4. 过滤幻觉类型，生成最终候选

注意：缓存 key 是 str(idx)，idx 是 best_base 列表中的 0-based 索引
"""

import json
import os
import re
import zipfile
from openai import OpenAI
from collections import defaultdict

# ─── 配置 ───────────────────────────────────────────────────────────────────
BASE_DIR = '/home/ubuntu/bisai'
CACHE1_FILE = f'{BASE_DIR}/分析报告/llm_re_cache.json'
CACHE2_FILE = f'{BASE_DIR}/分析报告/llm_re_cache_run2.json'
CACHE3_FILE = f'{BASE_DIR}/分析报告/llm_re_cache_run3.json'
BEST_BASE = f'{BASE_DIR}/数据/A榜/submit_v36_gene_abs.json'

# 训练集中存在的有效关系类型
VALID_TYPES = {
    'ABS-AFF-GENE', 'ABS-AFF-TRT', 'ABS-AFF-VAR',
    'BM-AFF-TRT', 'BM-USE-GENE',
    'CROP-CON-CROP', 'CROP-CON-VAR', 'CROP-HAS-TRT',
    'CROSS-CON-VAR',
    'GENE-AFF-TRT', 'GENE-LOI-TRT',
    'MRK-LOI-CHR', 'MRK-USE-GENE',
    'QTL-AFF-TRT', 'QTL-LOI-CHR', 'QTL-LOI-TRT',
    'VAR-CON-VAR', 'VAR-HAS-TRT',
}

# 训练集关系类型频次（用于置信度加权）
TYPE_FREQ = {
    'VAR-HAS-TRT': 328, 'QTL-LOI-TRT': 224, 'CROP-CON-VAR': 222,
    'GENE-AFF-TRT': 177, 'QTL-LOI-CHR': 141, 'CROP-HAS-TRT': 165,
    'ABS-AFF-TRT': 132, 'GENE-LOI-TRT': 85, 'ABS-AFF-GENE': 91,
    'MRK-USE-GENE': 47, 'TRT-AFF-TRT': 48, 'BM-AFF-TRT': 33,
    'CROSS-CON-VAR': 28, 'QTL-AFF-TRT': 26, 'CROP-CON-CROP': 21,
    'MRK-LOI-CHR': 14, 'VAR-CON-VAR': 12, 'ABS-AFF-VAR': 5,
    'BM-USE-GENE': 3,
}

client = OpenAI()

# ─── 加载数据 ────────────────────────────────────────────────────────────────
with open(BEST_BASE) as f:
    best_base = json.load(f)

# 找出无关系样本（底座中没有关系的样本），key = str(idx)
no_rel_indices = [i for i, item in enumerate(best_base) if not item.get('relations')]
print(f'无关系样本数: {len(no_rel_indices)}')

# 加载已有缓存（第 1 轮）
with open(CACHE1_FILE) as f:
    cache1 = json.load(f)
print(f'第 1 轮缓存: {len(cache1)} 个样本')

# ─── Few-shot 示例 ───────────────────────────────────────────────────────────
FEW_SHOT_EXAMPLES = """Example 1:
Text: "The QTL qGY1-1 was mapped to chromosome 1 and significantly affected grain yield in rice."
Relations: [{"head":"qGY1-1","head_type":"QTL","label":"LOI","tail":"chromosome 1","tail_type":"CHR"},{"head":"qGY1-1","head_type":"QTL","label":"AFF","tail":"grain yield","tail_type":"TRT"}]

Example 2:
Text: "The gene OsNAC45 positively regulated drought tolerance in rice cultivar Nipponbare."
Relations: [{"head":"OsNAC45","head_type":"GENE","label":"AFF","tail":"drought tolerance","tail_type":"TRT"},{"head":"Nipponbare","head_type":"VAR","label":"HAS","tail":"drought tolerance","tail_type":"TRT"}]

Example 3:
Text: "Wheat (Triticum aestivum) showed resistance to Fusarium head blight."
Relations: [{"head":"Triticum aestivum","head_type":"CROP","label":"HAS","tail":"resistance to Fusarium head blight","tail_type":"TRT"}]"""

def build_prompt(text, entities):
    entity_str = '; '.join([f"{e.get('text', e.get('name',''))} ({e.get('type','')})" for e in entities]) if entities else 'None'
    return f"""Extract binary relations from the plant breeding text.

Valid full relation types: {', '.join(sorted(VALID_TYPES))}
Format: {{"head":"entity","head_type":"TYPE","label":"MIDDLE","tail":"entity","tail_type":"TYPE"}}
(full type = head_type-label-tail_type)

{FEW_SHOT_EXAMPLES}

Text: "{text}"
Entities: {entity_str}

Return ONLY a JSON array. If no relations, return []."""

def call_llm(text, entities, temperature=0.3):
    prompt = build_prompt(text, entities)
    try:
        resp = client.chat.completions.create(
            model='gpt-4.1-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=temperature,
            max_tokens=800,
        )
        content = resp.choices[0].message.content.strip()
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            rels = json.loads(match.group())
            valid_rels = []
            for r in rels:
                if isinstance(r, dict) and 'head' in r and 'tail' in r and 'label' in r:
                    ht = r.get('head_type', '')
                    tt = r.get('tail_type', '')
                    lb = r.get('label', '')
                    full_type = f"{ht}-{lb}-{tt}"
                    if full_type in VALID_TYPES:
                        r['relation_type'] = full_type
                        valid_rels.append(r)
            return valid_rels
    except Exception as e:
        pass
    return []

def add_relation_type(rels):
    result = []
    for r in rels:
        r = dict(r)
        if 'relation_type' not in r:
            ht = r.get('head_type', '')
            tt = r.get('tail_type', '')
            lb = r.get('label', '')
            r['relation_type'] = f"{ht}-{lb}-{tt}"
        if r['relation_type'] in VALID_TYPES:
            result.append(r)
    return result

# ─── 运行第 2 轮 ─────────────────────────────────────────────────────────────
if os.path.exists(CACHE2_FILE):
    with open(CACHE2_FILE) as f:
        cache2 = json.load(f)
    print(f'第 2 轮缓存已存在: {len(cache2)} 个样本')
else:
    print('运行第 2 轮 LLM（temperature=0.4）...')
    cache2 = {}
    for i, idx in enumerate(no_rel_indices):
        item = best_base[idx]
        text = item.get('text', '')
        entities = item.get('entities', [])
        rels = call_llm(text, entities, temperature=0.4)
        cache2[str(idx)] = rels
        if (i + 1) % 20 == 0:
            print(f'  进度: {i+1}/{len(no_rel_indices)}')
            with open(CACHE2_FILE, 'w') as f:
                json.dump(cache2, f, ensure_ascii=False, indent=2)
    with open(CACHE2_FILE, 'w') as f:
        json.dump(cache2, f, ensure_ascii=False, indent=2)
    print(f'第 2 轮完成: {len(cache2)} 个样本')

# ─── 运行第 3 轮 ─────────────────────────────────────────────────────────────
if os.path.exists(CACHE3_FILE):
    with open(CACHE3_FILE) as f:
        cache3 = json.load(f)
    print(f'第 3 轮缓存已存在: {len(cache3)} 个样本')
else:
    print('运行第 3 轮 LLM（temperature=0.5）...')
    cache3 = {}
    for i, idx in enumerate(no_rel_indices):
        item = best_base[idx]
        text = item.get('text', '')
        entities = item.get('entities', [])
        rels = call_llm(text, entities, temperature=0.5)
        cache3[str(idx)] = rels
        if (i + 1) % 20 == 0:
            print(f'  进度: {i+1}/{len(no_rel_indices)}')
            with open(CACHE3_FILE, 'w') as f:
                json.dump(cache3, f, ensure_ascii=False, indent=2)
    with open(CACHE3_FILE, 'w') as f:
        json.dump(cache3, f, ensure_ascii=False, indent=2)
    print(f'第 3 轮完成: {len(cache3)} 个样本')

# ─── POSW-Vote 聚合 ──────────────────────────────────────────────────────────
def jaccard_sim(a, b):
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def posw_vote(runs, min_votes=2, jaccard_threshold=0.5):
    """POSW-Vote 聚合多轮输出，返回通过投票的关系列表"""
    by_type = defaultdict(list)
    for run_idx, run_rels in enumerate(runs):
        for rel in run_rels:
            rtype = rel.get('relation_type', '')
            if rtype in VALID_TYPES:
                by_type[rtype].append((run_idx, rel))

    final_rels = []
    for rtype, type_rels in by_type.items():
        clusters = []
        for run_idx, rel in type_rels:
            head = rel.get('head', '').strip().lower()
            tail = rel.get('tail', '').strip().lower()
            placed = False
            for cluster in clusters:
                rep_run, rep_rel = cluster[0]
                rep_head = rep_rel.get('head', '').strip().lower()
                rep_tail = rep_rel.get('tail', '').strip().lower()
                if jaccard_sim(head, rep_head) >= jaccard_threshold and \
                   jaccard_sim(tail, rep_tail) >= jaccard_threshold:
                    cluster.append((run_idx, rel))
                    placed = True
                    break
            if not placed:
                clusters.append([(run_idx, rel)])

        for cluster in clusters:
            run_indices = set(ri for ri, _ in cluster)
            if len(run_indices) >= min_votes:
                # 超字符串选择：选最长的
                best_rel = max(cluster, key=lambda x: len(x[1].get('head','')) + len(x[1].get('tail','')))[1]
                final_rels.append({'vote_count': len(run_indices), 'rel': best_rel})

    return final_rels

def build_submission(min_votes, name_suffix, freq_threshold=0):
    """构建提交文件"""
    total_added = 0
    samples_with_new = 0
    type_counts = defaultdict(int)

    new_submission = []
    for idx, item in enumerate(best_base):
        new_item = {k: v for k, v in item.items() if k != 'relations'}
        idx_str = str(idx)

        run1 = add_relation_type(cache1.get(idx_str, []))
        run2 = add_relation_type(cache2.get(idx_str, []))
        run3 = add_relation_type(cache3.get(idx_str, []))

        voted = posw_vote([run1, run2, run3], min_votes=min_votes)

        existing_rels = list(item.get('relations', []))
        existing_set = set(
            (r.get('head','').lower(), r.get('relation_type',''), r.get('tail','').lower())
            for r in existing_rels
        )

        for v in voted:
            rel = v['rel']
            rtype = rel.get('relation_type', '')
            if freq_threshold > 0 and TYPE_FREQ.get(rtype, 0) < freq_threshold:
                continue
            key = (rel.get('head','').lower(), rtype, rel.get('tail','').lower())
            if key not in existing_set:
                new_rel = {
                    'head': rel['head'],
                    'head_type': rel.get('head_type', rtype.split('-')[0]),
                    'relation_type': rtype,
                    'tail': rel['tail'],
                    'tail_type': rel.get('tail_type', rtype.split('-')[2]),
                }
                existing_rels.append(new_rel)
                existing_set.add(key)
                total_added += 1
                type_counts[rtype] += 1

        if len(existing_rels) > len(item.get('relations', [])):
            samples_with_new += 1

        new_item['relations'] = existing_rels
        new_submission.append(new_item)

    # 保存
    out_json = f'{BASE_DIR}/数据/A榜/submit_{name_suffix}.json'
    out_zip = f'{BASE_DIR}/数据/A榜/submit_{name_suffix}.zip'
    with open(out_json, 'w') as f:
        json.dump(new_submission, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(out_json, f'submit_{name_suffix}.json')

    total_rels = sum(len(item.get('relations', [])) for item in new_submission)
    avg_rels = total_rels / len(new_submission)
    print(f'\n[{name_suffix}]')
    print(f'  新增关系: {total_added}，有新关系样本: {samples_with_new}')
    print(f'  总关系: {total_rels}，均值: {avg_rels:.2f}')
    print(f'  类型分布: {dict(sorted(type_counts.items(), key=lambda x: -x[1]))}')
    print(f'  文件: {out_zip}')
    return new_submission

print('\n=== 生成 v39 系列 ===')

# v39_posw_2of3: ≥2/3 轮投票，无频次过滤
build_submission(min_votes=2, name_suffix='v39_posw_2of3')

# v39_posw_3of3: 3/3 轮投票（最保守）
build_submission(min_votes=3, name_suffix='v39_posw_3of3')

# v39_posw_2of3_highfreq: ≥2/3 轮 + 只保留训练集频次 ≥ 50 的类型
build_submission(min_votes=2, name_suffix='v39_posw_2of3_highfreq', freq_threshold=50)

print('\n全部完成！')
