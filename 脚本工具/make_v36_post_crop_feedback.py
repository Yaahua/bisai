#!/usr/bin/env python3
"""
make_v36_post_crop_feedback.py — 基于 v32_plus_abs_var_crop 掉分反馈调整策略

反馈：
- submit_v32_plus_abs_var（ABS-AFF-TRT:29 + VAR-HAS-TRT:27）→ 0.4479（当前最高）
- submit_v32_plus_abs_var_crop（+CROP-CON-VAR:17）→ 0.4469（掉分 0.001）

掉分原因分析：
- 17条 CROP-CON-VAR 中约6条是假阳性（泛称：'varieties', 'genotypes', 'breeding lines',
  'reference set', 'F-2-derived F-8 lines'）
- 这些假阳性拉低了精度，净效果为负

新策略：
1. 完全避开 CROP-CON-VAR（已证伪）
2. 专注于 ABS-AFF-GENE（33条，训练集91条，高频高价值）
3. 专注于 QTL-LOI-TRT + QTL-LOI-CHR（55条，训练集高频）
4. 尝试 GENE-AFF-TRT（22条）和 CROP-HAS-TRT（18条）单独测试
5. 生成"ABS-AFF-TRT 加量版"：v32 只加了29条，safe 中可能还有更多

底座：submit_v32_plus_abs_var（当前最高分 0.4479）
"""
import json
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v32_plus_abs_var.json'
V30_SAFE = ROOT / 'submit_v30_safe.json'
V30_ALL = ROOT / 'submit_v30_supported_alltypes.json'
# 也检查 v30_fixed 作为另一个候选来源
V30_FIXED = ROOT / 'submit_v30_fixed.json'
REPORT = Path('/home/ubuntu/bisai/分析报告/v36_post_crop_feedback_report.txt')


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


print("加载数据...")
base = load(BASE)
safe = load(V30_SAFE)
allx = load(V30_ALL)

# 收集双重背书候选（safe有 + allx有 + base没有），排除 CROP-CON-VAR
print("收集双重背书候选（排除 CROP-CON-VAR）...")
candidates_by_type = defaultdict(list)
EXCLUDE_TYPES = {('CROP', 'CON', 'VAR')}  # 已证伪

for idx, (b, s, a) in enumerate(zip(base, safe, allx)):
    kb = {rel_key(r) for r in b.get('relations', [])}
    ks = {rel_key(r): r for r in s.get('relations', [])}
    ka = {rel_key(r) for r in a.get('relations', [])}
    for k, r in ks.items():
        if k not in kb and k in ka:
            t = triplet(r)
            if t not in EXCLUDE_TYPES:
                candidates_by_type[t].append((idx, r))

print("可用候选（排除 CROP-CON-VAR）：")
for t, items in sorted(candidates_by_type.items(), key=lambda x: -len(x[1])):
    print(f"  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条")

# 同时检查 safe 中有但 allx 没有的（单重背书，风险稍高）
print("\n检查 safe 单独背书候选（safe有 + allx没有 + base没有）...")
single_candidates_by_type = defaultdict(list)
for idx, (b, s, a) in enumerate(zip(base, safe, allx)):
    kb = {rel_key(r) for r in b.get('relations', [])}
    ks = {rel_key(r): r for r in s.get('relations', [])}
    ka = {rel_key(r) for r in a.get('relations', [])}
    for k, r in ks.items():
        if k not in kb and k not in ka:
            t = triplet(r)
            if t not in EXCLUDE_TYPES:
                single_candidates_by_type[t].append((idx, r))

print("Safe 单独背书候选（前10类）：")
for t, items in sorted(single_candidates_by_type.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条")

report = [f"base={BASE}"]
base_ent, base_rel, base_no_rel = stats(base)
report.append(f"base: ent_avg={base_ent:.2f} rel_avg={base_rel:.2f} no_rel={base_no_rel:.1f}%")
report.append(f"反馈: v32_plus_abs_var_crop(+CROP-CON-VAR:17) → 0.4469 (掉分)")
report.append(f"结论: CROP-CON-VAR 已证伪，后续排除")
report.append("")

# 版本设计（全部排除 CROP-CON-VAR）
VERSIONS = {
    # 核心单类型测试
    'submit_v36_gene_abs': [('ABS', 'AFF', 'GENE')],         # 33条
    'submit_v36_qtl_loi': [('QTL', 'LOI', 'TRT'), ('QTL', 'LOI', 'CHR')],  # 55条
    'submit_v36_gene_trt': [('GENE', 'AFF', 'TRT')],          # 22条
    'submit_v36_crop_has': [('CROP', 'HAS', 'TRT')],          # 18条
    # 组合版
    'submit_v36_gene_abs_qtl': [
        ('ABS', 'AFF', 'GENE'),
        ('QTL', 'LOI', 'TRT'),
        ('QTL', 'LOI', 'CHR'),
    ],  # 88条
    'submit_v36_gene_abs_trt': [
        ('ABS', 'AFF', 'GENE'),
        ('GENE', 'AFF', 'TRT'),
    ],  # 55条
    # 保守组合（只加最高频训练集类型）
    'submit_v36_top3': [
        ('ABS', 'AFF', 'GENE'),   # 33条，训练集91条
        ('GENE', 'AFF', 'TRT'),   # 22条，训练集177条
        ('CROP', 'HAS', 'TRT'),   # 18条，训练集165条
    ],  # 73条
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

    json_path, zip_path = save_json_zip(name, data)
    ent, rel, no_rel = stats(data)

    line = f"{name}: added={added} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
    type_str = ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in added_counter.items())
    report.append(line)
    report.append(f"  types={type_str}")
    print(line)
    print(f"  types={type_str}")

REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f"\n报告已写入: {REPORT}")
print("所有 v36 候选已生成！")
