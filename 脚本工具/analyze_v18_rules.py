#!/usr/bin/env python3
"""
深度分析训练集触发词，挖掘 v18 白名单可扩展的新规则
对比 v17 已有规则，找出高置信度但尚未覆盖的关系模式
"""
import json
import re
from collections import defaultdict, Counter

TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
V17_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v17_whitelist.json'
E3_PATH = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'

train = json.load(open(TRAIN_PATH, encoding='utf-8'))
v17 = json.load(open(V17_PATH, encoding='utf-8'))
e3 = json.load(open(E3_PATH, encoding='utf-8'))

# ===== 1. 训练集中各关系的 between_text 触发词统计 =====
print("=" * 80)
print("【1】训练集中各关系类型的 between_text 触发词统计")
print("=" * 80)

rel_triggers = defaultdict(lambda: defaultdict(int))  # label -> between_text -> count
rel_triplet_triggers = defaultdict(lambda: defaultdict(int))  # (h,l,t) -> between -> count

for item in train:
    text = item['text']
    for rel in item.get('relations', []):
        h_end = rel['head_end']
        t_start = rel['tail_start']
        h_start = rel['head_start']
        t_end = rel['tail_end']
        if h_end <= t_start:
            between = text[h_end:t_start].strip()
        elif t_end <= h_start:
            between = text[t_end:h_start].strip()
        else:
            between = ""
        distance = abs(t_start - h_end) if h_end <= t_start else abs(h_start - t_end)
        if between and len(between) <= 60:
            between_lower = between.lower()
            rel_triggers[rel['label']][between_lower] += 1
            key = (rel['head_type'], rel['label'], rel['tail_type'])
            rel_triplet_triggers[key][between_lower] += 1

for label in ['LOI', 'AFF', 'HAS', 'CON', 'USE', 'OCI']:
    triggers = rel_triggers[label]
    high_freq = [(t, c) for t, c in triggers.items() if c >= 2]
    high_freq.sort(key=lambda x: -x[1])
    print(f"\n  [{label}] 高频触发词（出现>=2次，前30）：")
    for t, c in high_freq[:30]:
        print(f"    [{c:>3}次] \"{t}\"")

# ===== 2. 分析 v17 vs ensemble_v3 的差异 =====
print("\n" + "=" * 80)
print("【2】v17 相对 ensemble_v3 新增的关系统计")
print("=" * 80)

def rel_set(data):
    """提取所有关系的集合"""
    result = []
    for i, item in enumerate(data):
        for r in item.get('relations', []):
            result.append((i, r.get('head',''), r.get('head_type',''), r['label'], r.get('tail',''), r.get('tail_type','')))
    return set(result)

v17_rels = rel_set(v17)
e3_rels = rel_set(e3)
new_rels = v17_rels - e3_rels
print(f"v17 总关系: {len(v17_rels)}, e3 总关系: {len(e3_rels)}")
print(f"v17 新增关系: {len(new_rels)}")

new_by_label = Counter()
for r in new_rels:
    new_by_label[r[3]] += 1
print(f"新增关系按类型: {dict(new_by_label.most_common())}")

# ===== 3. 分析 v17 中仍然"无关系"的句子 =====
print("\n" + "=" * 80)
print("【3】v17 中仍然无关系的句子分析")
print("=" * 80)

no_rel_indices = [i for i, item in enumerate(v17) if not item.get('relations')]
print(f"v17 中无关系句子: {len(no_rel_indices)} / {len(v17)} ({len(no_rel_indices)/len(v17)*100:.1f}%)")

# 看这些句子的实体情况
has_ent_no_rel = 0
ent_type_in_no_rel = Counter()
for i in no_rel_indices:
    ents = v17[i].get('entities', [])
    if ents:
        has_ent_no_rel += 1
        for e in ents:
            ent_type_in_no_rel[e['label']] += 1
print(f"其中有实体但无关系: {has_ent_no_rel}")
print(f"这些句子中的实体类型分布: {dict(ent_type_in_no_rel.most_common())}")

# ===== 4. 分析各单模型的独有关系（被集成丢弃的） =====
print("\n" + "=" * 80)
print("【4】各单模型预测统计（找被集成丢弃的高价值关系）")
print("=" * 80)

model_files = {
    'v7': '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json',
    'v9': '/home/ubuntu/bisai/数据/A榜/submit_v9_targeted.json',
    'v10': '/home/ubuntu/bisai/数据/A榜/submit_v10_gemini.json',
}

model_data = {}
for name, path in model_files.items():
    try:
        data = json.load(open(path, encoding='utf-8'))
        model_data[name] = data
        total_r = sum(len(item.get('relations', [])) for item in data)
        print(f"  {name}: {len(data)} 条, 总关系 {total_r}, 均值 {total_r/len(data):.2f}")
    except:
        print(f"  {name}: 文件不存在")

# ===== 5. 按三元组类型分析训练集 vs v17 的差距 =====
print("\n" + "=" * 80)
print("【5】训练集 vs v17 三元组类型差距分析")
print("=" * 80)

train_trip_cnt = Counter()
for item in train:
    for r in item.get('relations', []):
        train_trip_cnt[(r['head_type'], r['label'], r['tail_type'])] += 1

v17_trip_cnt = Counter()
for item in v17:
    for r in item.get('relations', []):
        v17_trip_cnt[(r.get('head_type',''), r['label'], r.get('tail_type',''))] += 1

print(f"\n{'三元组':<25} {'训练集':>6} {'v17':>6} {'比率':>8} {'差距':>6}")
print("-" * 60)
for trip, train_c in train_trip_cnt.most_common(30):
    v17_c = v17_trip_cnt.get(trip, 0)
    # 按400/1000比例调整
    expected = train_c * 400 / 1000
    ratio = v17_c / expected if expected > 0 else 0
    gap = expected - v17_c
    trip_str = f"{trip[0]}-{trip[1]}-{trip[2]}"
    flag = " <<<" if ratio < 0.7 else ""
    print(f"{trip_str:<25} {train_c:>6} {v17_c:>6} {ratio:>7.2f}x {gap:>+6.0f}{flag}")

# ===== 6. 深度分析 CON 关系的触发词模式 =====
print("\n" + "=" * 80)
print("【6】CON 关系各三元组的触发词详情")
print("=" * 80)

for trip, triggers in sorted(rel_triplet_triggers.items(), key=lambda x: -sum(x[1].values())):
    if trip[1] == 'CON':
        total = sum(triggers.values())
        if total >= 3:
            print(f"\n  {trip[0]}-{trip[1]}-{trip[2]} (共{total}条):")
            for t, c in sorted(triggers.items(), key=lambda x: -x[1])[:10]:
                print(f"    [{c:>3}次] \"{t}\"")

# ===== 7. 深度分析 AFF 关系的触发词模式 =====
print("\n" + "=" * 80)
print("【7】AFF 关系各三元组的触发词详情")
print("=" * 80)

for trip, triggers in sorted(rel_triplet_triggers.items(), key=lambda x: -sum(x[1].values())):
    if trip[1] == 'AFF':
        total = sum(triggers.values())
        if total >= 3:
            print(f"\n  {trip[0]}-{trip[1]}-{trip[2]} (共{total}条):")
            for t, c in sorted(triggers.items(), key=lambda x: -x[1])[:10]:
                print(f"    [{c:>3}次] \"{t}\"")

# ===== 8. 深度分析 USE 和 OCI 关系 =====
print("\n" + "=" * 80)
print("【8】USE 和 OCI 关系触发词详情")
print("=" * 80)

for label in ['USE', 'OCI']:
    for trip, triggers in sorted(rel_triplet_triggers.items(), key=lambda x: -sum(x[1].values())):
        if trip[1] == label:
            total = sum(triggers.values())
            if total >= 2:
                print(f"\n  {trip[0]}-{trip[1]}-{trip[2]} (共{total}条):")
                for t, c in sorted(triggers.items(), key=lambda x: -x[1])[:10]:
                    print(f"    [{c:>3}次] \"{t}\"")

# ===== 9. 分析距离分布 =====
print("\n" + "=" * 80)
print("【9】各关系类型的实体间距离分布")
print("=" * 80)

rel_distances = defaultdict(list)
for item in train:
    text = item['text']
    for rel in item.get('relations', []):
        h_end = rel['head_end']
        t_start = rel['tail_start']
        h_start = rel['head_start']
        t_end = rel['tail_end']
        if h_end <= t_start:
            dist = t_start - h_end
        elif t_end <= h_start:
            dist = h_start - t_end
        else:
            dist = 0
        rel_distances[rel['label']].append(dist)

for label in ['LOI', 'AFF', 'HAS', 'CON', 'USE', 'OCI']:
    dists = rel_distances[label]
    if dists:
        import numpy as np
        arr = np.array(dists)
        print(f"\n  [{label}] 距离统计 (n={len(dists)}):")
        print(f"    均值: {arr.mean():.1f}, 中位数: {np.median(arr):.1f}")
        print(f"    P25: {np.percentile(arr, 25):.0f}, P75: {np.percentile(arr, 75):.0f}")
        print(f"    P90: {np.percentile(arr, 90):.0f}, 最大: {arr.max()}")
        print(f"    <=5字符: {(arr<=5).sum()} ({(arr<=5).sum()/len(arr)*100:.1f}%)")
        print(f"    <=15字符: {(arr<=15).sum()} ({(arr<=15).sum()/len(arr)*100:.1f}%)")
        print(f"    <=30字符: {(arr<=30).sum()} ({(arr<=30).sum()/len(arr)*100:.1f}%)")
        print(f"    <=60字符: {(arr<=60).sum()} ({(arr<=60).sum()/len(arr)*100:.1f}%)")
