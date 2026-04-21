#!/usr/bin/env python3
"""
make_v35_precise_rules.py — 基于训练集 between 词精准分析，设计高精度补召回规则

核心发现：
- QTL-LOI-TRT: "for" 是最强触发词（28/224），"associated with" 也是
- QTL-AFF-TRT: "has strong effects on", "determine", "controls the", "have positive effects on"
- ABS-AFF-GENE: 关系较复杂，between 词多样，不适合简单规则
- GENE-AFF-TRT: 关系较复杂，between 词多样
- CROP-HAS-TRT: "in" 最常见（22次），但太泛，需要更精准
- BM-AFF-TRT: "enhanced", "increased", "improves" 等

策略：
1. 精准 QTL-LOI-TRT 规则（"for" 触发，短距离）
2. 精准 QTL-AFF-TRT 规则（"effects on", "determine", "controls"）
3. 精准 CROP-HAS-TRT 规则（"including", "such as" 等列举词）
4. 精准 BM-AFF-TRT 规则

底座：submit_v32_plus_abs_var（当前最高分 0.4479）
"""
import json
import re
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v32_plus_abs_var.json'
REPORT = Path('/home/ubuntu/bisai/分析报告/v35_precise_rules_report.txt')

# 精准白名单规则（基于训练集 between 词分析）
PRECISE_RULES = [
    # ---- QTL-LOI-TRT 精准规则 ----
    # "QTL for TRT" 短距离
    (
        'LOI',
        ['QTL'],
        ['TRT'],
        re.compile(r'^\s*for\s*$', re.I),
        5,
        'QTL for TRT (short)'
    ),
    # "QTL is for TRT"
    (
        'LOI',
        ['QTL'],
        ['TRT'],
        re.compile(r'^\s*is\s+for\s*$', re.I),
        8,
        'QTL is for TRT'
    ),
    # QTL associated with TRT（短距离）
    (
        'LOI',
        ['QTL'],
        ['TRT'],
        re.compile(r'^\s*(associated with|were associated with|significantly associated with)\s*$', re.I),
        30,
        'QTL associated with TRT'
    ),
    # ---- QTL-AFF-TRT 精准规则 ----
    # "QTL has/have strong/large/positive effects on TRT"
    (
        'AFF',
        ['QTL'],
        ['TRT'],
        re.compile(r'\b(has|have)\s+(strong|large|positive|significant|major|minor)\s+(effects?|effect)\s+on\b', re.I),
        60,
        'QTL has strong effects on TRT'
    ),
    # "QTL determine/controls TRT"
    (
        'AFF',
        ['QTL'],
        ['TRT'],
        re.compile(r'\b(determine|determines|controls|control|regulates|regulate|affects|affect)\b', re.I),
        30,
        'QTL determine/controls TRT'
    ),
    # ---- CROP-HAS-TRT 精准规则 ----
    # "CROP including/such as ... TRT" 或 "CROP traits including TRT"
    (
        'HAS',
        ['CROP'],
        ['TRT'],
        re.compile(r'\b(including|such as|including traits|traits including|traits such as|traits like|traits:)\b', re.I),
        60,
        'CROP including TRT'
    ),
    # CROP showed/exhibited/displayed TRT
    (
        'HAS',
        ['CROP'],
        ['TRT'],
        re.compile(r'\b(showed|showing|exhibited|exhibiting|displayed|displaying|demonstrated|demonstrating)\b', re.I),
        40,
        'CROP showed TRT'
    ),
    # ---- BM-AFF-TRT 精准规则 ----
    # BM enhanced/increased/improved TRT
    (
        'AFF',
        ['BM'],
        ['TRT'],
        re.compile(r'\b(enhanced|increased|improved|improves|increases|enhances|promotes|promoted)\b', re.I),
        50,
        'BM enhanced/increased TRT'
    ),
    # ---- GENE-LOI-TRT 精准规则 ----
    # GENE for TRT
    (
        'LOI',
        ['GENE'],
        ['TRT'],
        re.compile(r'^\s*for\s*$', re.I),
        5,
        'GENE for TRT (short)'
    ),
    # ---- MRK-LOI-CHR 精准规则 ----
    # MRK on CHR
    (
        'LOI',
        ['MRK'],
        ['CHR'],
        re.compile(r'^\s*on\s*$', re.I),
        5,
        'MRK on CHR (short)'
    ),
    # MRK mapped to/located on CHR
    (
        'LOI',
        ['MRK'],
        ['CHR'],
        re.compile(r'\b(mapped to|located on|identified on|detected on|flanked by|flanking)\b', re.I),
        50,
        'MRK mapped to CHR'
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


def apply_rules(item, rules):
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

# 版本设计
RULE_SETS = {
    # QTL-LOI-TRT 精准规则
    'submit_v35_qtl_loi_trt': PRECISE_RULES[0:3],
    # QTL-AFF-TRT 精准规则
    'submit_v35_qtl_aff_trt': PRECISE_RULES[3:5],
    # CROP-HAS-TRT 精准规则
    'submit_v35_crop_has_trt': PRECISE_RULES[5:7],
    # BM-AFF-TRT 精准规则
    'submit_v35_bm_aff_trt': PRECISE_RULES[7:8],
    # MRK-LOI-CHR 精准规则
    'submit_v35_mrk_loi_chr': PRECISE_RULES[9:11],
    # QTL 系列组合（LOI + AFF）
    'submit_v35_qtl_combo': PRECISE_RULES[0:5],
    # 全精准规则组合
    'submit_v35_all_precise': PRECISE_RULES,
}

for name, rules in RULE_SETS.items():
    data = deepcopy(base)
    added = Counter()
    for item in data:
        new_rels = apply_rules(item, rules)
        item['relations'].extend(new_rels)
        for r in new_rels:
            added[(r['head_type'], r['label'], r['tail_type'])] += 1

    total = sum(added.values())
    save_json_zip(name, data)
    ent, rel, no_rel = stats(data)
    line = f"{name}: added={total} ent_avg={ent:.2f} rel_avg={rel:.2f} no_rel={no_rel:.1f}%"
    type_str = ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in added.items())
    report.append(line)
    report.append(f"  types={type_str}")
    print(line)
    print(f"  types={type_str}")

REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f"\n报告已写入: {REPORT}")
print("所有 v35 候选已生成！")
