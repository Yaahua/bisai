#!/usr/bin/env python3
"""
make_v33_from_v32best.py — 在 v32_plus_abs_var（当前最高分 0.4479）基础上继续小步加法

策略：
- 底座：submit_v32_plus_abs_var.json（已含 ABS-AFF-TRT:29 + VAR-HAS-TRT:27）
- 候选来源：safe 中有 + allx 中有 + base 中没有（双重背书）
- 重点类型（按双重背书候选数量排序）：
    ABS-AFF-GENE: 33 条  （训练集 91 条，高频高价值）
    GENE-AFF-TRT: 22 条  （训练集 177 条，第5高频）
    CROP-HAS-TRT: 18 条  （训练集 165 条，第6高频）
    CROP-CON-VAR: 17 条  （训练集 222 条，第4高频，v32 已加了部分）
    QTL-LOI-TRT:  30 条  （训练集 224 条，第3高频）
    QTL-LOI-CHR:  25 条  （训练集 141 条）

版本设计：
  v33_gene_abs:    在 v32best 上加 ABS-AFF-GENE（33条）
  v33_gene_trt:    在 v32best 上加 GENE-AFF-TRT（22条）
  v33_crop_has:    在 v32best 上加 CROP-HAS-TRT（18条）
  v33_gene_combo:  在 v32best 上加 ABS-AFF-GENE + GENE-AFF-TRT（55条，中等风险）
  v33_safe_trio:   在 v32best 上加 ABS-AFF-GENE + CROP-HAS-TRT + CROP-CON-VAR（68条）
  v33_qtl_gene:    在 v32best 上加 QTL-LOI-TRT + QTL-LOI-CHR（55条）
  v33_mega:        在 v32best 上加所有主要类型（激进版，用于探索上限）
"""
import json
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
# 底座：当前最高分版本
BASE = ROOT / 'submit_v32_plus_abs_var.json'
# 候选来源
V30_SAFE = ROOT / 'submit_v30_safe.json'
V30_ALL = ROOT / 'submit_v30_supported_alltypes.json'
REPORT = Path('/home/ubuntu/bisai/分析报告/v33_candidates_report.txt')


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


# 加载数据
print("加载底座（v32_plus_abs_var）...")
base = load(BASE)
print("加载 v30_safe...")
safe = load(V30_SAFE)
print("加载 v30_supported_alltypes...")
allx = load(V30_ALL)

# 收集双重背书候选（safe有 + allx有 + base没有）
print("\n收集双重背书候选关系...")
candidates_by_type = defaultdict(list)
for idx, (b, s, a) in enumerate(zip(base, safe, allx)):
    kb = {rel_key(r) for r in b.get('relations', [])}
    ks = {rel_key(r): r for r in s.get('relations', [])}
    ka = {rel_key(r) for r in a.get('relations', [])}
    for k, r in ks.items():
        if k not in kb and k in ka:
            candidates_by_type[triplet(r)].append((idx, r))

print("双重背书候选分布：")
for t, items in sorted(candidates_by_type.items(), key=lambda x: -len(x[1])):
    print(f"  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条")

# 定义各版本的加法集合（按优先级排序）
VERSIONS = {
    # 单类型测试版（最保守，用于精确定位每类关系的贡献）
    'submit_v33_gene_abs': [
        ('ABS', 'AFF', 'GENE'),   # 33条，训练集91条
    ],
    'submit_v33_gene_trt': [
        ('GENE', 'AFF', 'TRT'),   # 22条，训练集177条
    ],
    'submit_v33_crop_has': [
        ('CROP', 'HAS', 'TRT'),   # 18条，训练集165条
    ],
    # 双类型组合版
    'submit_v33_gene_combo': [
        ('ABS', 'AFF', 'GENE'),   # 33条
        ('GENE', 'AFF', 'TRT'),   # 22条
    ],
    'submit_v33_safe_trio': [
        ('ABS', 'AFF', 'GENE'),   # 33条
        ('CROP', 'HAS', 'TRT'),   # 18条
        ('CROP', 'CON', 'VAR'),   # 17条
    ],
    # QTL 系列
    'submit_v33_qtl_gene': [
        ('QTL', 'LOI', 'TRT'),    # 30条
        ('QTL', 'LOI', 'CHR'),    # 25条
    ],
    # 激进全量版（探索上限）
    'submit_v33_mega': [
        ('ABS', 'AFF', 'GENE'),   # 33条
        ('QTL', 'LOI', 'TRT'),    # 30条
        ('QTL', 'LOI', 'CHR'),    # 25条
        ('GENE', 'AFF', 'TRT'),   # 22条
        ('CROP', 'HAS', 'TRT'),   # 18条
        ('CROP', 'CON', 'VAR'),   # 17条
    ],
}

report = [f"base={BASE}"]
report.append(f"base stats: rel_avg={sum(len(x.get('relations',[])) for x in base)/len(base):.2f}")
report.append("")

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
print("所有 v33 候选已生成！")
