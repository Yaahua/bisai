#!/usr/bin/env python3
import json
import hashlib
from pathlib import Path
from collections import Counter

BASE = Path('/home/ubuntu/bisai/数据/A榜')
UP = Path('/home/ubuntu/v30_fixed_upload/submit.json')
OUT = Path('/home/ubuntu/bisai/分析报告/identify_uploaded_baseline.txt')


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def stats(data):
    n = len(data)
    ent = sum(len(x.get('entities', [])) for x in data) / n
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return ent, rel, no_rel


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()

up = load(UP)
up_stats = stats(up)
up_keys = [set(rel_key(r) for r in item.get('relations', [])) for item in up]

lines = []
lines.append('uploaded=' + str(UP))
lines.append(f'uploaded_stats ent_avg={up_stats[0]:.2f} rel_avg={up_stats[1]:.2f} no_rel={up_stats[2]:.1f}%')
lines.append(f'uploaded_md5={md5(UP)}')
lines.append('')
lines.append('=== candidates ===')

rows = []
for fp in sorted(BASE.glob('submit_*.json')):
    try:
        data = load(fp)
        if len(data) != len(up):
            continue
        keys = [set(rel_key(r) for r in item.get('relations', [])) for item in data]
        inter = sum(len(a & b) for a, b in zip(up_keys, keys))
        only_up = sum(len(a - b) for a, b in zip(up_keys, keys))
        only_fp = sum(len(b - a) for a, b in zip(up_keys, keys))
        rows.append((only_up + only_fp, only_up, only_fp, inter, fp.name, *stats(data), md5(fp)))
    except Exception as e:
        lines.append(f'skip {fp.name}: {e}')

rows.sort()
for dist, only_up, only_fp, inter, name, ent, rel, no_rel, m in rows[:15]:
    lines.append(f'{name}\tdiff={dist}\tonly_up={only_up}\tonly_file={only_fp}\tinter={inter}\tent_avg={ent:.2f}\trel_avg={rel:.2f}\tno_rel={no_rel:.1f}%\tmd5={m}')

best_name = rows[0][4]
best = load(BASE / best_name)
lines.append('')
lines.append(f'=== closest file details: {best_name} ===')
trip_up = Counter()
trip_best = Counter()
trip_only_up = Counter()
trip_only_best = Counter()
for iu, ib in zip(up, best):
    ru = {rel_key(r): r for r in iu.get('relations', [])}
    rb = {rel_key(r): r for r in ib.get('relations', [])}
    for r in ru.values():
        trip_up[(r['head_type'], r['label'], r['tail_type'])] += 1
    for r in rb.values():
        trip_best[(r['head_type'], r['label'], r['tail_type'])] += 1
    for k in ru.keys() - rb.keys():
        r = ru[k]
        trip_only_up[(r['head_type'], r['label'], r['tail_type'])] += 1
    for k in rb.keys() - ru.keys():
        r = rb[k]
        trip_only_best[(r['head_type'], r['label'], r['tail_type'])] += 1

lines.append('top_only_uploaded=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in trip_only_up.most_common(20)))
lines.append('top_only_closest=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in trip_only_best.most_common(20)))

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(OUT)
print(OUT.read_text(encoding='utf-8'))
