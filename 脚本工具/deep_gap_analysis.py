#!/usr/bin/env python3
"""
deep_gap_analysis.py — 深度分析当前底座与训练集的差距，找出最有价值的冲分方向
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
TEST = Path('/home/ubuntu/bisai/数据/官方原始数据/test_A.json')

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def rel_key(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])

def get_between_text(text, h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return text[h_end:t_start].strip().lower()
    elif t_end <= h_start:
        return text[t_end:h_start].strip().lower()
    return ""

train = load(TRAIN)
base = load(ROOT / 'submit_v41_sub_conservative.json')  # 当前最佳底座 0.4510
test = load(TEST)

print("=" * 70)
print("基本统计")
print("=" * 70)
train_rels = sum(len(x.get('relations', [])) for x in train)
base_rels = sum(len(x.get('relations', [])) for x in base)
train_no_rel = sum(1 for x in train if not x.get('relations'))
base_no_rel = sum(1 for x in base if not x.get('relations'))
print(f"训练集: {len(train)}条, 关系{train_rels}条, avg={train_rels/len(train):.2f}, no_rel={train_no_rel}({train_no_rel/len(train)*100:.1f}%)")
print(f"底座:   {len(base)}条, 关系{base_rels}条, avg={base_rels/len(base):.2f}, no_rel={base_no_rel}({base_no_rel/len(base)*100:.1f}%)")

# 训练集关系类型分布
train_types = Counter()
for item in train:
    for r in item.get('relations', []):
        train_types[triplet(r)] += 1

base_types = Counter()
for item in base:
    for r in item.get('relations', []):
        base_types[triplet(r)] += 1

print("\n" + "=" * 70)
print("关系类型覆盖率分析（训练集 vs 底座，按覆盖率升序）")
print("=" * 70)
all_types = set(list(train_types.keys()) + list(base_types.keys()))
coverage = []
for t in all_types:
    tr = train_types.get(t, 0)
    bs = base_types.get(t, 0)
    # 按比例换算（训练集1000条，测试集400条，比例0.4）
    expected = tr * 0.4
    gap = expected - bs
    if tr >= 5:  # 只分析训练集中出现5次以上的类型
        cov = bs / expected if expected > 0 else 0
        coverage.append((t, tr, int(expected), bs, gap, cov))

coverage.sort(key=lambda x: x[5])
print(f"{'类型':<25} {'训练集':>6} {'期望':>6} {'底座':>6} {'缺口':>6} {'覆盖率':>8}")
print("-" * 70)
for t, tr, exp, bs, gap, cov in coverage:
    name = f"{t[0]}-{t[1]}-{t[2]}"
    flag = " ⚠️" if gap > 5 else ""
    print(f"{name:<25} {tr:>6} {exp:>6} {bs:>6} {gap:>6.1f} {cov:>8.1%}{flag}")

print("\n" + "=" * 70)
print("训练集 between 词模式分析（低覆盖率类型）")
print("=" * 70)

# 分析训练集中低覆盖率类型的 between 词
low_cov_types = [(t, tr, int(tr*0.4), bs, tr*0.4-bs, bs/(tr*0.4) if tr*0.4>0 else 0) 
                  for t, tr, exp, bs, gap, cov in coverage if cov < 0.5 and tr >= 10]
low_cov_types.sort(key=lambda x: x[5])

for t, tr, exp, bs, gap, cov in low_cov_types[:10]:
    name = f"{t[0]}-{t[1]}-{t[2]}"
    print(f"\n--- {name} (训练集{tr}条, 底座{bs}条, 覆盖率{cov:.1%}, 缺口{gap:.1f}条) ---")
    
    # 收集训练集中该类型的 between 词
    between_words = Counter()
    examples = []
    for item in train:
        text = item.get('text', '')
        for r in item.get('relations', []):
            if triplet(r) == t:
                between = get_between_text(text, r['head_start'], r['head_end'],
                                           r['tail_start'], r['tail_end'])
                if between:
                    # 提取关键词
                    words = re.findall(r'\b[a-z]{2,}\b', between.lower())
                    for w in words:
                        between_words[w] += 1
                    if len(examples) < 3:
                        examples.append(f"  [{r['head']}] → [{r['tail']}] | between: '{between[:60]}'")
    
    print(f"  Top between 词: {', '.join([f'{w}({c})' for w, c in between_words.most_common(10)])}")
    for ex in examples:
        print(ex)

print("\n" + "=" * 70)
print("测试集中未被底座覆盖的实体对分析（低覆盖率类型）")
print("=" * 70)

# 分析测试集中低覆盖率类型的实体对
base_keys = defaultdict(set)
for idx, item in enumerate(base):
    for r in item.get('relations', []):
        base_keys[idx].add(rel_key(r))

# 找出测试集中有对应实体类型但底座没有该关系的样本
for t, tr, exp, bs, gap, cov in low_cov_types[:5]:
    name = f"{t[0]}-{t[1]}-{t[2]}"
    h_type, label, tail_type = t
    
    candidates = []
    for idx, item in enumerate(test):
        text = item.get('text', '')
        entities = item.get('entities', [])
        
        h_ents = [e for e in entities if e['label'] == h_type]
        t_ents = [e for e in entities if e['label'] == tail_type]
        
        for h in h_ents:
            for t_ent in t_ents:
                if h == t_ent:
                    continue
                between = get_between_text(text, h['start'], h['end'], t_ent['start'], t_ent['end'])
                if not between or len(between) > 100:
                    continue
                
                key = (h['text'].strip().lower(), h_type, label, t_ent['text'].strip().lower(), tail_type)
                if key not in base_keys[idx]:
                    candidates.append((idx, h['text'], t_ent['text'], between[:60]))
    
    print(f"\n{name}: 测试集中有{len(candidates)}个未覆盖实体对（距离≤100字符）")
    for idx, h, t_ent, between in candidates[:5]:
        print(f"  [{h}] → [{t_ent}] | between: '{between}'")

print("\n" + "=" * 70)
print("底座中可疑关系分析（高假阳性风险）")
print("=" * 70)

# 分析底座中各类型的实体距离分布
train_distances = defaultdict(list)
for item in train:
    text = item.get('text', '')
    for r in item.get('relations', []):
        t = triplet(r)
        dist = abs(r.get('head_start', 0) - r.get('tail_start', 0))
        train_distances[t].append(dist)

import statistics
print(f"{'类型':<25} {'训练集中位距':>12} {'底座中位距':>12} {'底座超距比例':>12}")
print("-" * 65)

base_distances = defaultdict(list)
for item in base:
    text = item.get('text', '')
    for r in item.get('relations', []):
        t = triplet(r)
        dist = abs(r.get('head_start', 0) - r.get('tail_start', 0))
        base_distances[t].append(dist)

for t in sorted(base_types.keys(), key=lambda x: base_types[x], reverse=True)[:15]:
    name = f"{t[0]}-{t[1]}-{t[2]}"
    tr_dists = train_distances.get(t, [])
    bs_dists = base_distances.get(t, [])
    if not tr_dists or not bs_dists:
        continue
    tr_med = statistics.median(tr_dists)
    bs_med = statistics.median(bs_dists)
    # 底座中超过训练集P75距离的比例
    tr_p75 = sorted(tr_dists)[int(len(tr_dists)*0.75)]
    over_pct = sum(1 for d in bs_dists if d > tr_p75) / len(bs_dists)
    print(f"{name:<25} {tr_med:>12.0f} {bs_med:>12.0f} {over_pct:>12.1%}")
