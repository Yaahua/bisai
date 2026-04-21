#!/usr/bin/env python3
"""
make_v34_extended.py — 在 v32_plus_abs_var 基础上探索更多关系类型组合

此脚本专注于：
1. 利用训练集中的白名单规则，从 test_A 文本中直接抽取更多关系
2. 生成基于文本规则的补充版本（不依赖 safe/allx 的模型预测）

核心思路：
- v32_plus_abs_var 已经用了 safe+allx 双重背书的 ABS-AFF-TRT 和 VAR-HAS-TRT
- 现在尝试用更精准的文本规则，直接从 test_A 文本中补充 GENE-AFF-TRT、CROP-HAS-TRT 等
- 同时探索 BM-AFF-TRT（11条双重背书）和 QTL-AFF-TRT（12条双重背书）
"""
import json
import re
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v32_plus_abs_var.json'
TEST_PATH = Path('/home/ubuntu/bisai/数据/官方原始数据/test_A.json')
REPORT = Path('/home/ubuntu/bisai/分析报告/v34_extended_report.txt')

# 额外的白名单规则（针对 v32 之后的缺口类型）
EXTRA_WHITELIST_RULES = [
    # GENE/QTL/BM affects/regulates TRT
    (
        'AFF',
        ['GENE'],
        ['TRT'],
        re.compile(r'\b(regulates|affects|mediates|influences|determines|controls|encodes|confers|contributes|responsible for|involved in)\b', re.I),
        50,
        'GENE regulates/affects TRT'
    ),
    # CROP/VAR showed/exhibited/had TRT (CROP-HAS-TRT)
    (
        'HAS',
        ['CROP'],
        ['TRT'],
        re.compile(r'\b(showed|showing|exhibited|exhibiting|displayed|displaying|had|has|with high|with improved|with enhanced|with greater|with better|with increased|with superior|with excellent)\b', re.I),
        40,
        'CROP showed/had TRT'
    ),
    # BM affects/influences TRT
    (
        'AFF',
        ['BM'],
        ['TRT'],
        re.compile(r'\b(associated with|were associated with|significantly associated with|correlated with|linked to|related to)\b', re.I),
        40,
        'BM associated with TRT'
    ),
    # QTL affects TRT (QTL-AFF-TRT)
    (
        'AFF',
        ['QTL'],
        ['TRT'],
        re.compile(r'\b(associated with|were associated with|significantly associated with|affects|controls|influences|regulates|for)\b', re.I),
        40,
        'QTL associated with/affects TRT'
    ),
    # ABS affects GENE (ABS-AFF-GENE)
    (
        'AFF',
        ['ABS'],
        ['GENE'],
        re.compile(r'\b(regulates|affects|mediates|influences|determines|controls|encodes|confers|contributes|responsible for|involved in|expressed in|expressed by)\b', re.I),
        50,
        'ABS regulates/affects GENE'
    ),
    # GENE-LOI-TRT: GENE located on/for TRT
    (
        'LOI',
        ['GENE'],
        ['TRT'],
        re.compile(r'\b(for|associated with|were associated with|significantly associated with|controlling|controlling for)\b', re.I),
        30,
        'GENE for/associated with TRT'
    ),
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


def get_between(text, h, t):
    h_start, h_end = h['start'], h['end']
    t_start, t_end = t['start'], t['end']
    if h_end <= t_start:
        return text[h_end:t_start], t_start - h_end
    elif t_end <= h_start:
        return text[t_end:h_start], h_start - t_end
    return None, -1


def is_cross_sentence(between):
    return bool(re.search(r'[.!?;]', between))


def apply_extra_whitelist(item, rules):
    """在现有关系基础上，用文本规则补充新关系"""
    text = item['text']
    entities = item.get('entities', [])

    existing_rels = set()
    for r in item.get('relations', []):
        existing_rels.add((r['head'].strip().lower(), r['tail'].strip().lower(), r['label']))

    new_rels = []

    for rule_label, head_types, tail_types, pattern, max_dist, desc in rules:
        for h in entities:
            if h['label'] not in head_types:
                continue
            for t in entities:
                if t['label'] not in tail_types:
                    continue
                if h['text'] == t['text']:
                    continue

                key = (h['text'].strip().lower(), t['text'].strip().lower(), rule_label)
                if key in existing_rels:
                    continue

                between, dist = get_between(text, h, t)
                if between is None or dist < 0:
                    continue
                if dist > max_dist:
                    continue
                if is_cross_sentence(between):
                    continue

                if pattern.search(between):
                    new_rel = {
                        'head': h['text'],
                        'head_type': h['label'],
                        'head_start': h['start'],
                        'head_end': h['end'],
                        'tail': t['text'],
                        'tail_type': t['label'],
                        'tail_start': t['start'],
                        'tail_end': t['end'],
                        'label': rule_label,
                    }
                    new_rels.append(new_rel)
                    existing_rels.add(key)

    return new_rels


def stats(data):
    n = len(data)
    ent = sum(len(x.get('entities', [])) for x in data) / n
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return ent, rel, no_rel


print("加载底座（v32_plus_abs_var）...")
base = load(BASE)

report = [f"base={BASE}"]
base_ent, base_rel, base_no_rel = stats(base)
report.append(f"base: ent_avg={base_ent:.2f} rel_avg={base_rel:.2f} no_rel={base_no_rel:.1f}%")
report.append("")

# 版本1：仅加 GENE-AFF-TRT 白名单规则
print("\n生成 v34_gene_trt_rule...")
data_gene_trt = deepcopy(base)
added_gene_trt = Counter()
for item in data_gene_trt:
    new_rels = apply_extra_whitelist(item, [EXTRA_WHITELIST_RULES[0]])  # GENE-AFF-TRT
    item['relations'].extend(new_rels)
    for r in new_rels:
        added_gene_trt[(r['head_type'], r['label'], r['tail_type'])] += 1
total_gene_trt = sum(added_gene_trt.values())
save_json_zip('submit_v34_gene_trt_rule', data_gene_trt)
ent, rel, no_rel = stats(data_gene_trt)
line = f"submit_v34_gene_trt_rule: added={total_gene_trt} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
report.append(line)
report.append(f"  types={dict(added_gene_trt)}")
print(line)

# 版本2：加 CROP-HAS-TRT 白名单规则
print("生成 v34_crop_has_rule...")
data_crop_has = deepcopy(base)
added_crop_has = Counter()
for item in data_crop_has:
    new_rels = apply_extra_whitelist(item, [EXTRA_WHITELIST_RULES[1]])  # CROP-HAS-TRT
    item['relations'].extend(new_rels)
    for r in new_rels:
        added_crop_has[(r['head_type'], r['label'], r['tail_type'])] += 1
total_crop_has = sum(added_crop_has.values())
save_json_zip('submit_v34_crop_has_rule', data_crop_has)
ent, rel, no_rel = stats(data_crop_has)
line = f"submit_v34_crop_has_rule: added={total_crop_has} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
report.append(line)
report.append(f"  types={dict(added_crop_has)}")
print(line)

# 版本3：加 ABS-AFF-GENE 白名单规则
print("生成 v34_abs_gene_rule...")
data_abs_gene = deepcopy(base)
added_abs_gene = Counter()
for item in data_abs_gene:
    new_rels = apply_extra_whitelist(item, [EXTRA_WHITELIST_RULES[4]])  # ABS-AFF-GENE
    item['relations'].extend(new_rels)
    for r in new_rels:
        added_abs_gene[(r['head_type'], r['label'], r['tail_type'])] += 1
total_abs_gene = sum(added_abs_gene.values())
save_json_zip('submit_v34_abs_gene_rule', data_abs_gene)
ent, rel, no_rel = stats(data_abs_gene)
line = f"submit_v34_abs_gene_rule: added={total_abs_gene} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
report.append(line)
report.append(f"  types={dict(added_abs_gene)}")
print(line)

# 版本4：全部额外白名单规则（探索上限）
print("生成 v34_all_rules...")
data_all = deepcopy(base)
added_all = Counter()
for item in data_all:
    new_rels = apply_extra_whitelist(item, EXTRA_WHITELIST_RULES)
    item['relations'].extend(new_rels)
    for r in new_rels:
        added_all[(r['head_type'], r['label'], r['tail_type'])] += 1
total_all = sum(added_all.values())
save_json_zip('submit_v34_all_rules', data_all)
ent, rel, no_rel = stats(data_all)
line = f"submit_v34_all_rules: added={total_all} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
report.append(line)
report.append(f"  types={dict(added_all)}")
print(line)

REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f"\n报告已写入: {REPORT}")
print("所有 v34 候选已生成！")
