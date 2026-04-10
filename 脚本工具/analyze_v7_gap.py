#!/usr/bin/env python3
"""
深度分析 v7 预测结果与训练集的差距，找出得分瓶颈
"""
import json
from collections import Counter, defaultdict

TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
V7_PATH    = '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json'

with open(TRAIN_PATH, encoding='utf-8') as f:
    train = json.load(f)
with open(V7_PATH, encoding='utf-8') as f:
    v7 = json.load(f)

print("=" * 60)
print("v7 预测结果 vs 训练集深度对比分析")
print("=" * 60)

# ===== 1. 实体类型分布对比 =====
train_ent_labels = Counter()
v7_ent_labels    = Counter()
for item in train:
    for e in item.get('entities', []):
        train_ent_labels[e['label']] += 1
for item in v7:
    for e in item.get('entities', []):
        v7_ent_labels[e['label']] += 1

train_ent_total = sum(train_ent_labels.values())
v7_ent_total    = sum(v7_ent_labels.values())

print("\n【实体类型分布对比】（训练集1000条 vs v7预测400条）")
print(f"{'类型':<8} {'训练集比例':>10} {'v7预测比例':>10} {'偏差':>8} {'风险'}")
print("-" * 55)
all_labels = sorted(set(list(train_ent_labels.keys()) + list(v7_ent_labels.keys())))
for lb in all_labels:
    tr_ratio = train_ent_labels[lb] / train_ent_total * 100
    v7_ratio = v7_ent_labels[lb]    / v7_ent_total    * 100
    diff = v7_ratio - tr_ratio
    risk = "⚠ 过标" if diff > 3 else ("⚠ 漏标" if diff < -3 else "✓")
    print(f"{lb:<8} {tr_ratio:>9.1f}% {v7_ratio:>9.1f}% {diff:>+7.1f}% {risk}")

# ===== 2. 关系类型分布对比 =====
train_rel_labels = Counter()
v7_rel_labels    = Counter()
for item in train:
    for r in item.get('relations', []):
        train_rel_labels[r['label']] += 1
for item in v7:
    for r in item.get('relations', []):
        v7_rel_labels[r['label']] += 1

train_rel_total = sum(train_rel_labels.values())
v7_rel_total    = sum(v7_rel_labels.values())

print(f"\n【关系类型分布对比】（训练集总关系:{train_rel_total} vs v7总关系:{v7_rel_total}）")
print(f"{'类型':<8} {'训练集比例':>10} {'v7预测比例':>10} {'偏差':>8} {'风险'}")
print("-" * 55)
all_rels = sorted(set(list(train_rel_labels.keys()) + list(v7_rel_labels.keys())))
for rl in all_rels:
    tr_ratio = train_rel_labels[rl] / train_rel_total * 100
    v7_ratio = v7_rel_labels[rl]    / v7_rel_total    * 100 if v7_rel_total > 0 else 0
    diff = v7_ratio - tr_ratio
    risk = "⚠ 过标" if diff > 5 else ("⚠ 漏标" if diff < -5 else "✓")
    print(f"{rl:<8} {tr_ratio:>9.1f}% {v7_ratio:>9.1f}% {diff:>+7.1f}% {risk}")

# ===== 3. 关系三元组类型分布对比 =====
train_triplets = Counter()
v7_triplets    = Counter()
for item in train:
    for r in item.get('relations', []):
        train_triplets[(r['head_type'], r['label'], r['tail_type'])] += 1
for item in v7:
    for r in item.get('relations', []):
        v7_triplets[(r['head_type'], r['label'], r['tail_type'])] += 1

print(f"\n【关系三元组分布对比（Top-15 训练集高频）】")
print(f"{'三元组':<30} {'训练集':>8} {'v7预测':>8} {'比率':>8} {'风险'}")
print("-" * 65)
top_triplets = train_triplets.most_common(15)
for (h, l, t), tr_cnt in top_triplets:
    v7_cnt = v7_triplets.get((h, l, t), 0)
    # 按比例缩放（训练集1000条，测试集400条，比例0.4）
    expected = tr_cnt * 0.4
    ratio = v7_cnt / expected if expected > 0 else 0
    risk = "⚠ 过标" if ratio > 1.5 else ("⚠ 漏标" if ratio < 0.5 else "✓")
    print(f"{h+'-'+l+'-'+t:<30} {tr_cnt:>8} {v7_cnt:>8} {ratio:>7.2f}x {risk}")

# ===== 4. 训练集中有但 v7 完全没预测到的三元组 =====
print(f"\n【训练集中有但 v7 完全未预测的三元组（严重漏标）】")
missing = [(k, v) for k, v in train_triplets.items() if v7_triplets.get(k, 0) == 0 and v >= 5]
missing.sort(key=lambda x: -x[1])
for (h, l, t), cnt in missing:
    print(f"  {h}-{l}-{t}: 训练集出现 {cnt} 次，v7 预测 0 次")

# ===== 5. v7 中有但训练集中没有的三元组（非法关系）=====
print(f"\n【v7 预测中出现但训练集中从未出现的三元组（非法关系）】")
illegal = [(k, v) for k, v in v7_triplets.items() if train_triplets.get(k, 0) == 0]
illegal.sort(key=lambda x: -x[1])
if illegal:
    for (h, l, t), cnt in illegal[:10]:
        print(f"  {h}-{l}-{t}: v7 预测 {cnt} 次，训练集 0 次 ← 应删除")
else:
    print("  无非法关系 ✓")

# ===== 6. 每条平均统计 =====
print(f"\n【每条文本平均统计】")
v7_ent_per = v7_ent_total / len(v7)
v7_rel_per = v7_rel_total / len(v7)
tr_ent_per = train_ent_total / len(train)
tr_rel_per = train_rel_total / len(train)
no_rel_v7  = sum(1 for item in v7 if not item.get('relations'))
no_rel_tr  = sum(1 for item in train if not item.get('relations'))
print(f"  实体/条：训练集 {tr_ent_per:.2f} | v7 {v7_ent_per:.2f} | 偏差 {v7_ent_per-tr_ent_per:+.2f}")
print(f"  关系/条：训练集 {tr_rel_per:.2f} | v7 {v7_rel_per:.2f} | 偏差 {v7_rel_per-tr_rel_per:+.2f}")
print(f"  无关系比：训练集 {no_rel_tr/len(train)*100:.1f}% | v7 {no_rel_v7/len(v7)*100:.1f}%")
