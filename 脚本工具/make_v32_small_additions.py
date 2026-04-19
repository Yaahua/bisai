#!/usr/bin/env python3
import json, zipfile
from pathlib import Path
from collections import Counter
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
TRUE_BEST = ROOT / 'submit_v30_fixed.json'
V30_SAFE = ROOT / 'submit_v30_safe.json'
V30_ALL = ROOT / 'submit_v30_supported_alltypes.json'
REPORT = Path('/home/ubuntu/bisai/分析报告/v32_small_additions_report.txt')

ADD_SETS = {
    'submit_v32_plus_abs_var': {
        ('ABS','AFF','TRT'),
        ('VAR','HAS','TRT'),
    },
    'submit_v32_plus_abs_var_crop': {
        ('ABS','AFF','TRT'),
        ('VAR','HAS','TRT'),
        ('CROP','CON','VAR'),
    },
    'submit_v32_plus_qtl_abs': {
        ('ABS','AFF','TRT'),
        ('QTL','LOI','TRT'),
        ('QTL','LOI','CHR'),
    },
    'submit_v32_plus_balanced_70': {
        ('ABS','AFF','TRT'),
        ('VAR','HAS','TRT'),
        ('CROP','CON','VAR'),
        ('QTL','LOI','TRT'),
    }
}
MAX_ADD = {
    'submit_v32_plus_abs_var': None,
    'submit_v32_plus_abs_var_crop': None,
    'submit_v32_plus_qtl_abs': None,
    'submit_v32_plus_balanced_70': 70,
}
TYPE_PRIORITY = [
    ('ABS','AFF','TRT'),
    ('VAR','HAS','TRT'),
    ('CROP','CON','VAR'),
    ('QTL','LOI','TRT'),
    ('QTL','LOI','CHR'),
]


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json_zip(name, data):
    json_path = ROOT / f'{name}.json'
    zip_path = ROOT / f'{name}.zip'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(json_path, arcname='submit.json')
    return json_path, zip_path


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])


def keyed(item):
    return {rel_key(r): r for r in item.get('relations', [])}


def stats(data):
    n = len(data)
    ent = sum(len(x.get('entities', [])) for x in data) / n
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return ent, rel, no_rel

base = load(TRUE_BEST)
safe = load(V30_SAFE)
allx = load(V30_ALL)

# collect add candidates from safe that are also present in alltypes, grouped by priority
by_type = {t: [] for t in TYPE_PRIORITY}
for idx, (b, s, a) in enumerate(zip(base, safe, allx)):
    kb, ks, ka = keyed(b), keyed(s), keyed(a)
    for k in ks.keys() - kb.keys():
        if k not in ka:
            continue
        r = ks[k]
        t = triplet(r)
        if t in by_type:
            by_type[t].append((idx, r))

report = []
report.append('base=' + str(TRUE_BEST))
for name, typeset in ADD_SETS.items():
    data = deepcopy(base)
    max_add = MAX_ADD[name]
    added = 0
    added_counter = Counter()
    for t in TYPE_PRIORITY:
        if t not in typeset:
            continue
        for idx, r in by_type.get(t, []):
            if max_add is not None and added >= max_add:
                break
            data[idx]['relations'].append(r)
            added += 1
            added_counter[t] += 1
        if max_add is not None and added >= max_add:
            break
    save_json_zip(name, data)
    ent, rel, no_rel = stats(data)
    report.append(f'{name}: added_total={added} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%')
    report.append('  added_types=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in added_counter.items()))

REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print(REPORT)
print(REPORT.read_text(encoding='utf-8'))
