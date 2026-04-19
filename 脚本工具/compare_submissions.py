#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path

BASE = Path('/home/ubuntu/bisai/数据/A榜')
A = BASE / 'submit_v17_whitelist.json'
B = BASE / 'submit_v21_elite.json'


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def triplet_key(r):
    return (r['head_type'], r['label'], r['tail_type'])


a = load(A)
b = load(B)
assert len(a) == len(b)

cnt_a = Counter()
cnt_b = Counter()
only_a = Counter()
only_b = Counter()
inter = Counter()
only_a_items = []
only_b_items = []

for i, (ia, ib) in enumerate(zip(a, b)):
    ra = {rel_key(r): r for r in ia.get('relations', [])}
    rb = {rel_key(r): r for r in ib.get('relations', [])}
    ka = set(ra)
    kb = set(rb)
    for r in ia.get('relations', []):
        cnt_a[triplet_key(r)] += 1
    for r in ib.get('relations', []):
        cnt_b[triplet_key(r)] += 1
    for k in ka & kb:
        inter[triplet_key(ra[k])] += 1
    for k in ka - kb:
        only_a[triplet_key(ra[k])] += 1
    for k in kb - ka:
        only_b[triplet_key(rb[k])] += 1
    if ka - kb:
        only_a_items.append((i, ia['text'][:120], len(ka-kb), len(kb-ka)))
    if kb - ka:
        only_b_items.append((i, ib['text'][:120], len(ka-kb), len(kb-ka)))

print('=== Overall ===')
print(f'v17 total rels: {sum(cnt_a.values())}')
print(f'v21 total rels: {sum(cnt_b.values())}')
print(f'intersection: {sum(inter.values())}')
print(f'only v17: {sum(only_a.values())}')
print(f'only v21: {sum(only_b.values())}')

print('\n=== Triplet comparison ===')
all_keys = sorted(set(cnt_a) | set(cnt_b), key=lambda x: (x[1], x[0], x[2]))
print(f"{'triplet':<28} {'v17':>5} {'v21':>5} {'inter':>5} {'only17':>7} {'only21':>7}")
for k in all_keys:
    print(f"{('-'.join(k)):<28} {cnt_a[k]:>5} {cnt_b[k]:>5} {inter[k]:>5} {only_a[k]:>7} {only_b[k]:>7}")

print('\n=== Items with most v21-only relations ===')
for row in sorted(only_b_items, key=lambda x: x[3], reverse=True)[:20]:
    print(f'idx={row[0]:>3} only17={row[2]:>2} only21={row[3]:>2} | {row[1]}')

print('\n=== Items with most v17-only relations ===')
for row in sorted(only_a_items, key=lambda x: x[2], reverse=True)[:20]:
    print(f'idx={row[0]:>3} only17={row[2]:>2} only21={row[3]:>2} | {row[1]}')
