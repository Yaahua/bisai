#!/usr/bin/env python3
"""全量分析所有提交文件的统计数据"""
import json, os

submit_dir = '数据/A榜'
files = sorted([f for f in os.listdir(submit_dir) if f.endswith('.json')])

print('=== 所有提交文件统计 ===')
header = f"{'文件名':<45} {'条数':>5} {'实体均值':>8} {'关系均值':>8} {'无关系%':>8}"
print(header)
print('-' * 80)

for fname in files:
    path = os.path.join(submit_dir, fname)
    try:
        data = json.load(open(path, encoding='utf-8'))
        n = len(data)
        total_ent = sum(len(item.get('entities', [])) for item in data)
        total_rel = sum(len(item.get('relations', [])) for item in data)
        no_rel = sum(1 for item in data if not item.get('relations'))
        ent_avg = total_ent / n
        rel_avg = total_rel / n
        no_rel_pct = no_rel / n * 100
        print(f"{fname:<45} {n:>5} {ent_avg:>8.2f} {rel_avg:>8.2f} {no_rel_pct:>7.1f}%")
    except Exception as e:
        print(f"{fname:<45} ERROR: {e}")

# 已知分数表
print("\n\n=== 已知提交分数 ===")
scores = {
    'v1/submit.json': 0.3457,
    'v2': 0.3423,
    'v3': 0.3482,
    'v7_cicl_v2': 0.3746,
    'v9_clean': 0.3893,
    'ensemble_v3': 0.4172,
    'v16_rules': 0.4077,
    'ensemble_v4a': 0.4079,
    'v17_whitelist': 0.4224,
    'v21_nli_v17': 0.4192,
    'v22_schema_filter': 0.4208,
    'v25_ds_validate': 0.4203,
    'v26_filtered': 0.4208,
}
for name, score in sorted(scores.items(), key=lambda x: x[1]):
    print(f"  {name:<30} {score:.4f}")

# 分析v17白名单的关系类型分布
print("\n\n=== v17_whitelist 关系类型分布 ===")
v17_path = os.path.join(submit_dir, 'submit_v17_whitelist.json')
if os.path.exists(v17_path):
    v17 = json.load(open(v17_path, encoding='utf-8'))
    from collections import Counter
    rel_labels = Counter()
    triplet_types = Counter()
    for item in v17:
        for r in item.get('relations', []):
            rel_labels[r['label']] += 1
            triplet_types[(r.get('head_type','?'), r['label'], r.get('tail_type','?'))] += 1
    
    print("\n关系标签分布:")
    total_rels = sum(rel_labels.values())
    for label, count in rel_labels.most_common():
        print(f"  {label:<10} {count:>5} ({count/total_rels*100:.1f}%)")
    
    print(f"\n三元组类型分布 (Top 20):")
    for (h, l, t), count in triplet_types.most_common(20):
        print(f"  {h}-{l}-{t:<20} {count:>5}")
