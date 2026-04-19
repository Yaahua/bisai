#!/usr/bin/env python3
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('/home/ubuntu/bisai/数据/A榜')
FILES = {
    'v17': BASE / 'submit_v17_whitelist.json',
    'v7': BASE / 'submit_v7_cicl_v2.json',
    'v9': BASE / 'submit_v9_clean.json',
    'v10': BASE / 'submit_v10_gemini.json',
    'v21': BASE / 'submit_v21_elite.json',
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def rkey(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def tkey(k):
    return (k[1], k[2], k[4])


data = {name: load(path) for name, path in FILES.items()}
N = len(data['v17'])

support_counter = Counter()
triplet_support = defaultdict(Counter)
item_examples = []

for i in range(N):
    keys = {name: {rkey(r) for r in data[name][i].get('relations', [])} for name in data}
    new_v21 = keys['v21'] - keys['v17']
    for k in new_v21:
        supporters = tuple(sorted([m for m in ('v7','v9','v10') if k in keys[m]]))
        support_counter[supporters] += 1
        triplet_support[tkey(k)][supporters] += 1
    if new_v21:
        counts = {m: len([k for k in new_v21 if k in keys[m]]) for m in ('v7','v9','v10')}
        item_examples.append((i, len(new_v21), counts, data['v21'][i]['text'][:120]))

print('=== v21相对v17的新增关系支持情况 ===')
print(f'总新增关系: {sum(support_counter.values())}')
for supporters, cnt in sorted(support_counter.items(), key=lambda x: (-x[1], x[0])):
    label = '+'.join(supporters) if supporters else 'none'
    print(f'{label:<12} {cnt:>4}')

print('\n=== 各三元组的支持分布（Top 25 by total new relations） ===')
rows = []
for triplet, cnts in triplet_support.items():
    total = sum(cnts.values())
    rows.append((total, triplet, cnts))
rows.sort(reverse=True)
for total, triplet, cnts in rows[:25]:
    parts = []
    for supporters, cnt in sorted(cnts.items(), key=lambda x: (-x[1], x[0])):
        label = '+'.join(supporters) if supporters else 'none'
        parts.append(f'{label}:{cnt}')
    print(f"{'-'.join(triplet):<28} total={total:<3} | {'; '.join(parts)}")

print('\n=== 新增最多的样本（附各旧模型支持数） ===')
for i, total, counts, text in sorted(item_examples, key=lambda x: x[1], reverse=True)[:25]:
    print(f"idx={i:>3} new={total:>2} | v7={counts['v7']:>2} v9={counts['v9']:>2} v10={counts['v10']:>2} | {text}")
