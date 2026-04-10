#!/usr/bin/env python3
"""分析当前预测结果的弱点，与官方训练集规律对比，找出失分模式"""
import json
from collections import Counter, defaultdict

# 加载数据
with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    train = json.load(f)
with open('/home/ubuntu/bisai_clone/数据/A榜/submit.json') as f:
    pred = json.load(f)

# ===== 1. 训练集基准统计 =====
train_ent_labels = Counter()
train_rel_labels = Counter()
train_rel_pairs = Counter()  # (head_type, label, tail_type)
train_ents_per_sent = []
train_rels_per_sent = []
train_no_rel = 0

for item in train:
    ents = item.get('entities', [])
    rels = item.get('relations', [])
    train_ents_per_sent.append(len(ents))
    train_rels_per_sent.append(len(rels))
    if len(rels) == 0:
        train_no_rel += 1
    for e in ents:
        train_ent_labels[e['label']] += 1
    for r in rels:
        train_rel_labels[r['label']] += 1
        train_rel_pairs[(r['head_type'], r['label'], r['tail_type'])] += 1

# ===== 2. 预测结果统计 =====
pred_ent_labels = Counter()
pred_rel_labels = Counter()
pred_rel_pairs = Counter()
pred_ents_per_sent = []
pred_rels_per_sent = []
pred_no_rel = 0

for item in pred:
    ents = item.get('entities', [])
    rels = item.get('relations', [])
    pred_ents_per_sent.append(len(ents))
    pred_rels_per_sent.append(len(rels))
    if len(rels) == 0:
        pred_no_rel += 1
    for e in ents:
        pred_ent_labels[e['label']] += 1
    for r in rels:
        pred_rel_labels[r['label']] += 1
        pred_rel_pairs[(r['head_type'], r['label'], r['tail_type'])] += 1

# ===== 3. 打印对比报告 =====
print("=" * 60)
print("【1】每句平均实体数对比")
print(f"  训练集: {sum(train_ents_per_sent)/len(train_ents_per_sent):.2f}")
print(f"  预测集: {sum(pred_ents_per_sent)/len(pred_ents_per_sent):.2f}")
print(f"  差异: {(sum(pred_ents_per_sent)/len(pred_ents_per_sent)) - (sum(train_ents_per_sent)/len(train_ents_per_sent)):+.2f}")

print("\n【2】每句平均关系数对比")
print(f"  训练集: {sum(train_rels_per_sent)/len(train_rels_per_sent):.2f}")
print(f"  预测集: {sum(pred_rels_per_sent)/len(pred_rels_per_sent):.2f}")
print(f"  差异: {(sum(pred_rels_per_sent)/len(pred_rels_per_sent)) - (sum(train_rels_per_sent)/len(train_rels_per_sent)):+.2f}")

print(f"\n【3】无关系句比例")
print(f"  训练集: {train_no_rel}/{len(train)} = {train_no_rel/len(train)*100:.1f}%")
print(f"  预测集: {pred_no_rel}/{len(pred)} = {pred_no_rel/len(pred)*100:.1f}%")

print("\n【4】实体类型分布对比（训练集比例 vs 预测集比例）")
total_train_ent = sum(train_ent_labels.values())
total_pred_ent = sum(pred_ent_labels.values())
all_ent_types = sorted(set(list(train_ent_labels.keys()) + list(pred_ent_labels.keys())))
print(f"  {'类型':<8} {'训练集%':>8} {'预测集%':>8} {'偏差':>8}")
for t in all_ent_types:
    tr = train_ent_labels[t] / total_train_ent * 100
    pr = pred_ent_labels[t] / total_pred_ent * 100 if total_pred_ent > 0 else 0
    flag = " ⚠" if abs(tr - pr) > 3 else ""
    print(f"  {t:<8} {tr:>7.1f}% {pr:>7.1f}% {pr-tr:>+7.1f}%{flag}")

print("\n【5】关系类型分布对比")
total_train_rel = sum(train_rel_labels.values())
total_pred_rel = sum(pred_rel_labels.values())
all_rel_types = sorted(set(list(train_rel_labels.keys()) + list(pred_rel_labels.keys())))
print(f"  {'类型':<8} {'训练集%':>8} {'预测集%':>8} {'偏差':>8} {'训练集数':>8} {'预测集数':>8}")
for t in all_rel_types:
    tr = train_rel_labels[t] / total_train_rel * 100 if total_train_rel > 0 else 0
    pr = pred_rel_labels[t] / total_pred_rel * 100 if total_pred_rel > 0 else 0
    flag = " ⚠" if abs(tr - pr) > 3 else ""
    print(f"  {t:<8} {tr:>7.1f}% {pr:>7.1f}% {pr-tr:>+7.1f}%{flag}  {train_rel_labels[t]:>8} {pred_rel_labels[t]:>8}")

print("\n【6】Top-20 关系三元组对比（训练集 vs 预测集）")
print("  --- 训练集 Top-20 ---")
for (h, l, t), cnt in train_rel_pairs.most_common(20):
    pred_cnt = pred_rel_pairs.get((h, l, t), 0)
    ratio = pred_cnt / (cnt * len(pred) / len(train))
    flag = " ⚠" if ratio < 0.6 or ratio > 1.6 else ""
    print(f"  ({h}, {l}, {t}): 训练={cnt} 预测={pred_cnt}{flag}")

print("\n  --- 预测集独有 Top-10（训练集没有的三元组）---")
pred_only = [(k, v) for k, v in pred_rel_pairs.items() if train_rel_pairs[k] == 0]
pred_only.sort(key=lambda x: -x[1])
for (h, l, t), cnt in pred_only[:10]:
    print(f"  ({h}, {l}, {t}): 预测={cnt} ⚠ 训练集无此模式")

print("\n【7】预测集中数量异常多的关系三元组（可能过标）")
for (h, l, t), pred_cnt in pred_rel_pairs.most_common(30):
    train_cnt = train_rel_pairs.get((h, l, t), 0)
    expected = train_cnt * len(pred) / len(train)
    if pred_cnt > expected * 1.8 and pred_cnt > 5:
        print(f"  ({h}, {l}, {t}): 预测={pred_cnt} 期望≈{expected:.0f} 过标{pred_cnt/max(expected,1):.1f}x ⚠")

print("\n【8】预测集中数量异常少的关系三元组（可能漏标）")
for (h, l, t), train_cnt in train_rel_pairs.most_common(30):
    pred_cnt = pred_rel_pairs.get((h, l, t), 0)
    expected = train_cnt * len(pred) / len(train)
    if pred_cnt < expected * 0.5 and expected > 3:
        print(f"  ({h}, {l}, {t}): 预测={pred_cnt} 期望≈{expected:.0f} 漏标{pred_cnt/max(expected,1):.2f}x ⚠")
