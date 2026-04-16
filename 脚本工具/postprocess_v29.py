#!/usr/bin/env python3
"""
postprocess_v29.py — v29 集成结果后处理
1. 清理非法三元组（训练集中从未出现的类型组合）
2. 用白名单规则补充 CROP-CON-VAR 等高缺口三元组
3. 输出最终提交文件
"""
import json
import re
import os
from copy import deepcopy
from collections import Counter

INPUT_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_v29_ensemble.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v29_postprocessed.json'
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'

# ===== 加载训练集，构建合法三元组集合 =====
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)

LEGAL_TRIPLETS = set()
for item in TRAIN_DATA:
    for r in item.get('relations', []):
        LEGAL_TRIPLETS.add((r['head_type'], r['label'], r['tail_type']))

# 额外的非法三元组（即使训练集有少量也禁止，因为模型过标严重）
EXTRA_ILLEGAL = {
    ('GENE', 'CON', 'GENE'),   # 训练集无
    ('TRT',  'AFF', 'TRT'),    # 训练集无
    ('CROP', 'CON', 'CROP'),   # 训练集无
    ('VAR',  'CON', 'VAR'),    # 训练集无
    ('MRK',  'LOI', 'QTL'),    # 训练集无（QTL-LOI-MRK 有，但反向没有）
    ('ABS',  'AFF', 'ABS'),    # 训练集无
    ('TRT',  'OCI', 'GST'),    # 训练集有但方向错误（应该是 X-OCI-GST，X 不是 TRT）
    ('MRK',  'AFF', 'TRT'),    # 训练集无
    ('GENE', 'AFF', 'ABS'),    # 训练集无
    ('VAR',  'CON', 'CROP'),   # 方向错误
    ('GENE', 'CON', 'CROP'),   # 方向错误
    ('CROSS','CON', 'CROP'),   # 方向错误
    ('TRT',  'HAS', 'VAR'),    # 方向错误
    ('TRT',  'HAS', 'CROP'),   # 方向错误
    ('CROP', 'HAS', 'ABS'),    # 训练集无
    ('VAR',  'HAS', 'ABS'),    # 训练集无
    ('VAR',  'HAS', 'BIS'),    # 训练集无
    ('BM',   'USE', 'CROP'),   # 方向错误
    ('CHR',  'LOI', 'VAR'),    # 训练集无
    ('TRT',  'LOI', 'TRT'),    # 训练集无
    ('ABS',  'LOI', 'CHR'),    # 训练集无
    ('BIS',  'LOI', 'CHR'),    # 训练集无
    ('GST',  'AFF', 'TRT'),    # 训练集无
    ('CROP', 'AFF', 'TRT'),    # 训练集无
    ('QTL',  'LOI', 'VAR'),    # 训练集无
    ('QTL',  'LOI', 'MRK'),    # 训练集无
    ('VAR',  'OCI', 'TRT'),    # 训练集无
    ('VAR',  'AFF', 'BIS'),    # 训练集无
}

FINAL_ILLEGAL = EXTRA_ILLEGAL
# 从合法集合中移除非法的
FINAL_LEGAL = LEGAL_TRIPLETS - FINAL_ILLEGAL

print(f"合法三元组类型: {len(FINAL_LEGAL)}")
print(f"非法三元组类型: {len(FINAL_ILLEGAL)}")

# ===== 白名单规则（补充高缺口三元组）=====
# 格式: (label, head_types, tail_types, pattern, max_dist, description)
WHITELIST_RULES = [
    # ---- CROP-CON-VAR 规则（缺口最大）----
    # CROP variety/cultivar/accession/genotype/line VAR
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'\b(variet|cultivar|cv\.|accession|genotype|line|lines|germplasm)\b', re.I),
        50,
        'CROP variety/cultivar VAR'
    ),
    # CROP (VAR) — 括号内是品种名
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'^\s*\(\s*$', re.I),
        3,
        'CROP (VAR)'
    ),
    # CROP including/such as VAR
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'\b(including|such as|namely|i\.e\.|e\.g\.)\b', re.I),
        40,
        'CROP including VAR'
    ),
    # ---- LOI 规则 ----
    # QTL/MRK/GENE for TRT
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['TRT'],
        re.compile(r'^\s*for\s*$', re.I),
        5,
        'QTL/MRK/GENE for TRT'
    ),
    # QTL/MRK/GENE on CHR
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'^\s*on\s*$', re.I),
        5,
        'QTL/MRK/GENE on CHR'
    ),
    # mapped to / located on / identified on
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'\b(mapped to|located on|identified on|detected on|were identified on|were located on)\b', re.I),
        50,
        'mapped to/located on CHR'
    ),
    # associated with → LOI
    (
        'LOI',
        ['QTL', 'MRK'],
        ['TRT'],
        re.compile(r'\b(associated with|were associated with|significantly associated with)\b', re.I),
        30,
        'QTL/MRK associated with TRT'
    ),
    # ---- AFF 规则 ----
    # GENE/QTL regulates/affects TRT
    (
        'AFF',
        ['GENE', 'QTL'],
        ['TRT'],
        re.compile(r'\b(regulates|affects|mediates|influences|determines)\b', re.I),
        40,
        'GENE/QTL regulates TRT'
    ),
    # ---- HAS 规则 ----
    # CROP/VAR showed/exhibited TRT
    (
        'HAS',
        ['CROP', 'VAR'],
        ['TRT'],
        re.compile(r'\b(showed|showing|exhibited|exhibiting|displayed|displaying)\b', re.I),
        40,
        'CROP/VAR showed TRT'
    ),
    # CROP/VAR with high/improved TRT
    (
        'HAS',
        ['CROP', 'VAR'],
        ['TRT'],
        re.compile(r'\bwith (high|improved|enhanced|greater|better|increased|superior|excellent)\b', re.I),
        30,
        'CROP/VAR with high TRT'
    ),
]

def get_between(text, h, t):
    h_start, h_end = h['start'], h['end']
    t_start, t_end = t['start'], t['end']
    if h_end <= t_start:
        return text[h_end:t_start], t_start - h_end, 'h->t'
    elif t_end <= h_start:
        return text[t_end:h_start], h_start - t_end, 't->h'
    return None, -1, None

def is_cross_sentence(between):
    return bool(re.search(r'[.!?;]', between))

def apply_whitelist(item, rules):
    text = item['text']
    entities = item.get('entities', [])
    
    existing_rels = set()
    for r in item.get('relations', []):
        existing_rels.add((r['head'].strip().lower(), r['tail'].strip().lower(), r['label']))
        existing_rels.add((r['tail'].strip().lower(), r['head'].strip().lower(), r['label']))
    
    new_rels = []
    
    for rule_label, head_types, tail_types, pattern, max_dist, desc in rules:
        for h in entities:
            if h['label'] not in head_types:
                continue
            for t in entities:
                if t['label'] not in tail_types:
                    continue
                if h['text'] == t['text']:
                    continue
                
                key = (h['text'].strip().lower(), t['text'].strip().lower(), rule_label)
                if key in existing_rels:
                    continue
                
                between, dist, direction = get_between(text, h, t)
                if between is None or dist < 0:
                    continue
                if dist > max_dist:
                    continue
                if is_cross_sentence(between):
                    continue
                
                if pattern.search(between):
                    new_rel = {
                        'head': h['text'],
                        'head_type': h['label'],
                        'head_start': h['start'],
                        'head_end': h['end'],
                        'tail': t['text'],
                        'tail_type': t['label'],
                        'tail_start': t['start'],
                        'tail_end': t['end'],
                        'label': rule_label,
                    }
                    new_rels.append(new_rel)
                    existing_rels.add(key)
                    existing_rels.add((t['text'].strip().lower(), h['text'].strip().lower(), rule_label))
    
    return new_rels

# ===== 主程序 =====
print(f"\n加载输入文件: {INPUT_PATH}")
with open(INPUT_PATH, encoding='utf-8') as f:
    input_data = json.load(f)

output = []
total_removed = 0
total_added = 0
removed_by_type = Counter()
added_by_type = Counter()

for item in input_data:
    new_item = deepcopy(item)
    
    # 1. 清理非法三元组
    clean_rels = []
    for r in new_item.get('relations', []):
        triplet = (r['head_type'], r['label'], r['tail_type'])
        if triplet in FINAL_ILLEGAL:
            total_removed += 1
            removed_by_type[f"{triplet[0]}-{triplet[1]}-{triplet[2]}"] += 1
        elif triplet not in FINAL_LEGAL:
            total_removed += 1
            removed_by_type[f"{triplet[0]}-{triplet[1]}-{triplet[2]}(未知)"] += 1
        else:
            clean_rels.append(r)
    new_item['relations'] = clean_rels
    
    # 2. 白名单补召回
    new_rels = apply_whitelist(new_item, WHITELIST_RULES)
    for r in new_rels:
        clean_r = {
            'head': r['head'], 'head_type': r['head_type'],
            'head_start': r['head_start'], 'head_end': r['head_end'],
            'tail': r['tail'], 'tail_type': r['tail_type'],
            'tail_start': r['tail_start'], 'tail_end': r['tail_end'],
            'label': r['label']
        }
        new_item['relations'].append(clean_r)
        total_added += 1
        added_by_type[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
    
    output.append(new_item)

# 保存
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

total_rels = sum(len(x.get('relations',[])) for x in output)
no_rel = sum(1 for x in output if not x.get('relations',[]))
rel_types = Counter()
for item in output:
    for r in item.get('relations',[]):
        rel_types[(r['head_type'], r['label'], r['tail_type'])] += 1

print(f"\n===== 后处理完成 =====")
print(f"输出: {OUTPUT_PATH}")
print(f"删除非法关系: {total_removed} 条")
if removed_by_type:
    for t, cnt in sorted(removed_by_type.items(), key=lambda x: -x[1])[:10]:
        print(f"  删除 {t}: {cnt}")
print(f"白名单新增: {total_added} 条")
if added_by_type:
    for t, cnt in sorted(added_by_type.items(), key=lambda x: -x[1])[:10]:
        print(f"  新增 {t}: {cnt}")
print(f"\n最终统计:")
print(f"关系总数: {total_rels}, 均值: {total_rels/len(output):.2f}, 无关系: {no_rel} ({no_rel/len(output)*100:.1f}%)")
print(f"\n关系类型分布（Top 15）:")
for (ht,l,tt), cnt in sorted(rel_types.items(), key=lambda x: -x[1])[:15]:
    print(f"  {ht}-{l}-{tt}: {cnt}")
