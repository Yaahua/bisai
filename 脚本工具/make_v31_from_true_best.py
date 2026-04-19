#!/usr/bin/env python3
import json, zipfile
from pathlib import Path
from collections import Counter
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
TRUE_BEST = Path('/home/ubuntu/v30_fixed_upload/submit.json')
V29 = ROOT / 'submit_v29_postprocessed.json'
V30_SAFE = ROOT / 'submit_v30_safe.json'
V30_ULTRA = ROOT / 'submit_v30_ultrasafe.json'
V30_ALL = ROOT / 'submit_v30_supported_alltypes.json'
OUTDIR = ROOT
REPORT = Path('/home/ubuntu/bisai/分析报告/v31_from_true_best_report.txt')

ILLEGALISH = {
    ('GENE','CON','GENE'), ('TRT','AFF','TRT'), ('CROP','CON','CROP'),
    ('MRK','LOI','QTL'), ('ABS','OCI','GST'), ('VAR','CON','VAR')
}
SAFE_ADD_TYPES = {
    ('ABS','AFF','TRT'), ('VAR','HAS','TRT'), ('CROP','CON','VAR'),
    ('CROP','HAS','TRT'), ('QTL','LOI','TRT'), ('QTL','LOI','CHR'),
    ('GENE','AFF','TRT'), ('ABS','AFF','GENE'), ('GENE','LOI','TRT'),
    ('MRK','LOI','TRT'), ('TRT','OCI','GST')
}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json_zip(name, data):
    json_path = OUTDIR / f'{name}.json'
    zip_path = OUTDIR / f'{name}.zip'
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

true_best = load(TRUE_BEST)
v29 = load(V29)
v30s = load(V30_SAFE)
v30u = load(V30_ULTRA)
v30a = load(V30_ALL)

# 1) 保存标准化真基线
save_json_zip('submit_v30_fixed', true_best)

# true_best 相对 v29 的新增关系按支持来源分桶
add_vs_v29 = []
for i, (tb, b29, s, u, a) in enumerate(zip(true_best, v29, v30s, v30u, v30a)):
    ktb, k29, ks, ku, ka = keyed(tb), keyed(b29), keyed(s), keyed(u), keyed(a)
    bucketed = {'supported': [], 'none': [], 'illegalish': []}
    for k in ktb.keys() - k29.keys():
        r = ktb[k]
        overlap = k in ks or k in ku or k in ka
        if triplet(r) in ILLEGALISH:
            bucketed['illegalish'].append(r)
        elif overlap:
            bucketed['supported'].append(r)
        else:
            bucketed['none'].append(r)
    add_vs_v29.append(bucketed)

# 2) 去掉 true_best 相对 v29 中完全无 v30 支持的 35 条
trim_none = deepcopy(v29)
for item, buckets in zip(trim_none, add_vs_v29):
    item['relations'].extend(buckets['supported'] + buckets['illegalish'])
save_json_zip('submit_v31_trim_none', trim_none)

# 3) 去掉 true_best 里的 suspicious 非法向关系，只保留其余全部
trim_illegalish = deepcopy(v29)
for item, buckets in zip(trim_illegalish, add_vs_v29):
    item['relations'].extend(buckets['supported'] + buckets['none'])
save_json_zip('submit_v31_trim_illegalish', trim_illegalish)

# 4) 在 true_best 上谨慎加入 v30_safe 独有且被 v30_all 背书、且关系类型在白名单中的增量
plus_safe = deepcopy(true_best)
added_counter = Counter()
added_total = 0
for out_item, tb, s, a in zip(plus_safe, true_best, v30s, v30a):
    ktb, ks, ka = keyed(tb), keyed(s), keyed(a)
    existing = set(ktb.keys())
    for k in ks.keys() - ktb.keys():
        r = ks[k]
        if k not in ka:
            continue
        if triplet(r) not in SAFE_ADD_TYPES:
            continue
        out_item['relations'].append(r)
        existing.add(k)
        added_counter[triplet(r)] += 1
        added_total += 1
save_json_zip('submit_v31_plus_safe_selective', plus_safe)

# 5) 更稳一点：只加 v30_safe 独有中的核心四类
core_types = {
    ('ABS','AFF','TRT'), ('VAR','HAS','TRT'), ('CROP','CON','VAR'), ('QTL','LOI','TRT')
}
plus_safe_core = deepcopy(true_best)
added_counter_core = Counter()
added_total_core = 0
for out_item, tb, s, a in zip(plus_safe_core, true_best, v30s, v30a):
    ktb, ks, ka = keyed(tb), keyed(s), keyed(a)
    for k in ks.keys() - ktb.keys():
        r = ks[k]
        if k not in ka:
            continue
        if triplet(r) not in core_types:
            continue
        out_item['relations'].append(r)
        added_counter_core[triplet(r)] += 1
        added_total_core += 1
save_json_zip('submit_v31_plus_safe_core', plus_safe_core)

lines = []
for name in ['submit_v30_fixed','submit_v31_trim_none','submit_v31_trim_illegalish','submit_v31_plus_safe_selective','submit_v31_plus_safe_core']:
    data = load(OUTDIR / f'{name}.json')
    ent, rel, no_rel = stats(data)
    lines.append(f'{name}: ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%')
lines.append('')
lines.append(f'plus_safe_selective_added_total={added_total}')
lines.append('plus_safe_selective_added_types=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in added_counter.most_common(20)))
lines.append(f'plus_safe_core_added_total={added_total_core}')
lines.append('plus_safe_core_added_types=' + ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in added_counter_core.most_common(20)))
REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(REPORT)
print(REPORT.read_text(encoding='utf-8'))
