#!/usr/bin/env python3
"""
make_v37_on_gene_abs.py — 以 v36_gene_abs(0.4487) 为新底座继续叠加

已验证：
- v32_plus_abs_var (ABS-AFF-TRT:29 + VAR-HAS-TRT:27) → 0.4479
- v36_gene_abs (+ ABS-AFF-GENE:33) → 0.4487 ✓ 新最高

下一步策略（单类型测试，精确定位每类贡献）：
1. v37_qtl_loi   = v36_gene_abs + QTL-LOI-TRT:30 + QTL-LOI-CHR:25  (+55)
2. v37_gene_trt  = v36_gene_abs + GENE-AFF-TRT:22                    (+22)
3. v37_crop_has  = v36_gene_abs + CROP-HAS-TRT:18                    (+18)
4. v37_gene_qtl  = v36_gene_abs + GENE-AFF-TRT:22 + QTL-LOI-TRT:30 + QTL-LOI-CHR:25  (+77)
5. v37_all4      = v36_gene_abs + QTL-LOI-TRT + QTL-LOI-CHR + GENE-AFF-TRT + CROP-HAS-TRT (+95)

底座：submit_v36_gene_abs（当前最高分 0.4487）
"""
import json
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v36_gene_abs.json'   # 新底座：0.4487
V30_SAFE = ROOT / 'submit_v30_safe.json'
V30_ALL = ROOT / 'submit_v30_supported_alltypes.json'
REPORT = Path('/home/ubuntu/bisai/分析报告/v37_on_gene_abs_report.txt')

EXCLUDE_TYPES = {('CROP', 'CON', 'VAR')}  # 已证伪

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

def stats(data):
    n = len(data)
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return rel, no_rel

print("加载数据...")
base = load(BASE)
safe = load(V30_SAFE)
allx = load(V30_ALL)

# 收集双重背书候选（相对新底座 v36_gene_abs）
print("收集双重背书候选（相对 v36_gene_abs 底座）...")
candidates_by_type = defaultdict(list)

for idx, (b, s, a) in enumerate(zip(base, safe, allx)):
    kb = {rel_key(r) for r in b.get('relations', [])}
    ks = {rel_key(r): r for r in s.get('relations', [])}
    ka = {rel_key(r) for r in a.get('relations', [])}
    for k, r in ks.items():
        if k not in kb and k in ka:
            t = triplet(r)
            if t not in EXCLUDE_TYPES:
                candidates_by_type[t].append((idx, r))

print("可用候选（相对 v36_gene_abs 底座）：")
for t, items in sorted(candidates_by_type.items(), key=lambda x: -len(x[1])):
    print(f"  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条")

report = [f"base={BASE} (score=0.4487)"]
base_rel, base_no_rel = stats(base)
report.append(f"base: rel_avg={base_rel:.2f} no_rel={base_no_rel:.1f}%")
report.append("")

VERSIONS = {
    # 单类型（精确定位）
    'submit_v37_qtl_loi':  [('QTL', 'LOI', 'TRT'), ('QTL', 'LOI', 'CHR')],
    'submit_v37_gene_trt': [('GENE', 'AFF', 'TRT')],
    'submit_v37_crop_has': [('CROP', 'HAS', 'TRT')],
    # 组合
    'submit_v37_gene_qtl': [('GENE', 'AFF', 'TRT'), ('QTL', 'LOI', 'TRT'), ('QTL', 'LOI', 'CHR')],
    'submit_v37_all4':     [('QTL', 'LOI', 'TRT'), ('QTL', 'LOI', 'CHR'),
                            ('GENE', 'AFF', 'TRT'), ('CROP', 'HAS', 'TRT')],
}

for name, type_list in VERSIONS.items():
    data = deepcopy(base)
    added = 0
    added_counter = Counter()
    for t in type_list:
        for idx, r in candidates_by_type.get(t, []):
            data[idx]['relations'].append(r)
            added += 1
            added_counter[t] += 1

    save_json_zip(name, data)
    rel, no_rel = stats(data)
    line = f"{name}: added={added} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
    type_str = ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in added_counter.items())
    report.append(line)
    report.append(f"  types={type_str}")
    print(line)
    print(f"  types={type_str}")

REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f"\n报告已写入: {REPORT}")
print("所有 v37 候选已生成！")
