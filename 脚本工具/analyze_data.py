#!/usr/bin/env python3
"""
分析 bisai 仓库的修订结果 vs 官方训练集，检查偏移情况
"""
import json
import os
import glob

# ========== 1. 加载官方训练集 ==========
official_path = '/home/ubuntu/official_mgbie/dataset/train.json'
with open(official_path, 'r', encoding='utf-8') as f:
    official_data = json.load(f)

print(f"官方训练集总条数: {len(official_data)}")

# 建立 text -> 官方标注 的映射
official_map = {item['text']: item for item in official_data}

# ========== 2. 加载 bisai 修订结果 ==========
corrected_dir = '/home/ubuntu/bisai_clone/数据/训练集/修订结果'
corrected_files = sorted(glob.glob(os.path.join(corrected_dir, '*.json')))
print(f"\n修订结果文件数: {len(corrected_files)}")

all_corrected = []
for fp in corrected_files:
    with open(fp, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        all_corrected.extend(data)
    elif isinstance(data, dict):
        all_corrected.append(data)

print(f"修订结果总条数: {len(all_corrected)}")

# ========== 3. 检查 text 字段是否与官方一致 ==========
print("\n===== 文本一致性检查 =====")
text_mismatch = 0
text_not_in_official = 0
for item in all_corrected:
    t = item.get('text', '')
    if t not in official_map:
        text_not_in_official += 1

print(f"修订条目中 text 不在官方训练集的条数: {text_not_in_official}")

# ========== 4. 实体边界一致性检查 ==========
print("\n===== 实体边界一致性检查 =====")
boundary_errors = 0
total_entities = 0
error_examples = []

for item in all_corrected:
    text = item.get('text', '')
    for ent in item.get('entities', []):
        total_entities += 1
        s, e, ent_text = ent.get('start'), ent.get('end'), ent.get('text', '')
        if s is None or e is None:
            boundary_errors += 1
            continue
        actual = text[s:e]
        if actual != ent_text:
            boundary_errors += 1
            if len(error_examples) < 5:
                error_examples.append({
                    'text_snippet': text[:80],
                    'entity_text': ent_text,
                    'start': s, 'end': e,
                    'actual_slice': actual
                })

print(f"总实体数: {total_entities}")
print(f"边界错误数: {boundary_errors}")
if error_examples:
    print("错误示例（最多5条）:")
    for ex in error_examples:
        print(f"  实体声称: '{ex['entity_text']}', 实际切片: '{ex['actual_slice']}', start={ex['start']}, end={ex['end']}")
        print(f"  文本前80字: {ex['text_snippet']}")

# ========== 5. 关系 anchor 一致性检查 ==========
print("\n===== 关系 anchor 一致性检查 =====")
rel_errors = 0
total_rels = 0
rel_error_examples = []

for item in all_corrected:
    text = item.get('text', '')
    for rel in item.get('relations', []):
        total_rels += 1
        hs, he = rel.get('head_start'), rel.get('head_end')
        ts, te = rel.get('tail_start'), rel.get('tail_end')
        head_text = rel.get('head', '')
        tail_text = rel.get('tail', '')
        err = False
        if hs is not None and he is not None:
            if text[hs:he] != head_text:
                err = True
        if ts is not None and te is not None:
            if text[ts:te] != tail_text:
                err = True
        if err:
            rel_errors += 1
            if len(rel_error_examples) < 3:
                rel_error_examples.append({
                    'head': head_text, 'actual_head': text[hs:he] if hs is not None else 'N/A',
                    'tail': tail_text, 'actual_tail': text[ts:te] if ts is not None else 'N/A',
                })

print(f"总关系数: {total_rels}")
print(f"关系 anchor 错误数: {rel_errors}")
if rel_error_examples:
    print("错误示例:")
    for ex in rel_error_examples:
        print(f"  head声称: '{ex['head']}', 实际: '{ex['actual_head']}'")
        print(f"  tail声称: '{ex['tail']}', 实际: '{ex['actual_tail']}'")

# ========== 6. 实体标签分布统计 ==========
print("\n===== 实体标签分布（修订后 vs 官方）=====")
from collections import Counter

corrected_labels = Counter()
for item in all_corrected:
    for ent in item.get('entities', []):
        corrected_labels[ent.get('label', 'UNKNOWN')] += 1

official_labels = Counter()
for item in official_data:
    for ent in item.get('entities', []):
        official_labels[ent.get('label', 'UNKNOWN')] += 1

all_label_keys = sorted(set(list(corrected_labels.keys()) + list(official_labels.keys())))
print(f"{'标签':<12} {'修订后(chunk1-30)':<22} {'官方全量(1000条)':<22} {'修订后比例':<15} {'官方比例':<15}")
print("-" * 85)
for lbl in all_label_keys:
    c = corrected_labels.get(lbl, 0)
    o = official_labels.get(lbl, 0)
    c_total = sum(corrected_labels.values())
    o_total = sum(official_labels.values())
    c_pct = f"{c/c_total*100:.1f}%" if c_total > 0 else "0%"
    o_pct = f"{o/o_total*100:.1f}%" if o_total > 0 else "0%"
    print(f"{lbl:<12} {c:<22} {o:<22} {c_pct:<15} {o_pct:<15}")

# ========== 7. 关系标签分布统计 ==========
print("\n===== 关系标签分布（修订后 vs 官方）=====")
corrected_rels = Counter()
for item in all_corrected:
    for rel in item.get('relations', []):
        corrected_rels[rel.get('label', 'UNKNOWN')] += 1

official_rels = Counter()
for item in official_data:
    for rel in item.get('relations', []):
        official_rels[rel.get('label', 'UNKNOWN')] += 1

all_rel_keys = sorted(set(list(corrected_rels.keys()) + list(official_rels.keys())))
print(f"{'关系标签':<12} {'修订后(chunk1-30)':<22} {'官方全量(1000条)':<22} {'修订后比例':<15} {'官方比例':<15}")
print("-" * 85)
for lbl in all_rel_keys:
    c = corrected_rels.get(lbl, 0)
    o = official_rels.get(lbl, 0)
    c_total = sum(corrected_rels.values())
    o_total = sum(official_rels.values())
    c_pct = f"{c/c_total*100:.1f}%" if c_total > 0 else "0%"
    o_pct = f"{o/o_total*100:.1f}%" if o_total > 0 else "0%"
    print(f"{lbl:<12} {c:<22} {o:<22} {c_pct:<15} {o_pct:<15}")

# ========== 8. 每条平均实体数和关系数 ==========
print("\n===== 平均实体/关系数 =====")
if all_corrected:
    avg_ent_c = sum(len(i.get('entities', [])) for i in all_corrected) / len(all_corrected)
    avg_rel_c = sum(len(i.get('relations', [])) for i in all_corrected) / len(all_corrected)
    print(f"修订后 - 平均实体数: {avg_ent_c:.2f}, 平均关系数: {avg_rel_c:.2f}")

avg_ent_o = sum(len(i.get('entities', [])) for i in official_data) / len(official_data)
avg_rel_o = sum(len(i.get('relations', [])) for i in official_data) / len(official_data)
print(f"官方全量 - 平均实体数: {avg_ent_o:.2f}, 平均关系数: {avg_rel_o:.2f}")

# ========== 9. 检查修订后数据覆盖了哪些 chunk ==========
print(f"\n===== 修订结果文件列表 =====")
for fp in corrected_files:
    with open(fp, 'r', encoding='utf-8') as f:
        data = json.load(f)
    n = len(data) if isinstance(data, list) else 1
    print(f"  {os.path.basename(fp)}: {n} 条")

# ========== 10. 检查 A 榜测试集结构 ==========
print("\n===== A 榜测试集 (test_A.json) 结构 =====")
test_a_path = '/home/ubuntu/official_mgbie/dataset/test_A.json'
with open(test_a_path, 'r', encoding='utf-8') as f:
    test_a = json.load(f)
print(f"总条数: {len(test_a)}")
print(f"第1条字段: {list(test_a[0].keys())}")
print(f"第1条 text 前100字: {test_a[0].get('text','')[:100]}")
has_entities = any('entities' in item for item in test_a)
has_relations = any('relations' in item for item in test_a)
print(f"是否含 entities 字段: {has_entities}")
print(f"是否含 relations 字段: {has_relations}")
