#!/usr/bin/env python3
"""
postprocess_v3_rules.py v2 — 精准规则后处理，零 API 调用
=========================================================
只在两个实体之间的文本中有明确触发词时才添加关系。
不做全句匹配，避免过度添加。

目标：关系均值从 2.16 → 2.60~2.80，无关系比例从 38.2% → 32~35%
"""
import json
import re
from collections import defaultdict

V3_PATH    = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v16_rules.json'

with open(V3_PATH, encoding='utf-8') as f:
    v3_data = json.load(f)
with open(TRAIN_PATH, encoding='utf-8') as f:
    train_data = json.load(f)

print(f"v3: {len(v3_data)} 条 | 训练集: {len(train_data)} 条")

# ===== 精确触发词（必须出现在两个实体之间的文本中）=====

# CON: CROP 包含 VAR — 实体间文本需有包含关系词
CON_BETWEEN = [
    r'\bincluding\b', r'\binclude\b', r'\bsuch as\b', r'\bnamely\b',
    r'\bcomprising\b', r'\bcomprised of\b', r'\bconsisting of\b',
    r'\bcontains\b', r'\bcontain\b', r'\bcontaining\b',
    r'\bwas\b', r'\bwere\b', r'\bis\b', r'\bare\b',  # CROP is/are VAR
]

# USE: VAR/CROSS → BM — 实体间有 "using", "by", "via", "through" 等
USE_BETWEEN = [
    r'\busing\b', r'\bused\b', r'\bby\b', r'\bvia\b', r'\bthrough\b',
    r'\bemploying\b', r'\bemployed\b', r'\bapplied\b', r'\bapplying\b',
    r'\bperformed\b', r'\bconducted\b', r'\banalyzed\b', r'\banalysis\b',
]

# AFF: QTL/GENE/BM → TRT — 实体间有因果关系词
AFF_BETWEEN = [
    r'\bassociated with\b', r'\bassociation with\b',
    r'\bcontrolling\b', r'\bcontrolled\b', r'\bcontrols\b',
    r'\bregulating\b', r'\bregulated\b', r'\bregulates\b',
    r'\baffecting\b', r'\baffected\b', r'\baffects\b',
    r'\binfluencing\b', r'\binfluenced\b', r'\binfluences\b',
    r'\bdetermining\b', r'\bdetermined\b', r'\bdetermines\b',
    r'\bfor\b',  # "QTL for grain yield"
    r'\bof\b',   # "QTL of plant height"
]

# LOI: MRK/QTL → CHR — 实体间有定位词
LOI_BETWEEN = [
    r'\bon\b', r'\bat\b', r'\bin\b',
    r'\bmapped to\b', r'\bmapped on\b', r'\blocated on\b', r'\blocated at\b',
    r'\bdetected on\b', r'\bdetected at\b', r'\bidentified on\b',
    r'\blinked to\b', r'\bassociated with\b', r'\bflanking\b', r'\bflanked by\b',
]

# OCI: TRT/ABS → GST — 实体间有时间关系词
OCI_BETWEEN = [
    r'\bat\b', r'\bduring\b', r'\bin\b',
    r'\bat the\b', r'\bduring the\b',
]

def between_text(text, e1, e2):
    """获取两个实体之间的文本（按位置顺序）"""
    if e1['end'] <= e2['start']:
        return text[e1['end']:e2['start']]
    elif e2['end'] <= e1['start']:
        return text[e2['end']:e1['start']]
    return ""  # 重叠，返回空

def has_pattern(text_between, patterns):
    """检查文本是否匹配任一正则模式"""
    t = text_between.lower()
    for p in patterns:
        if re.search(p, t):
            return True
    return False

def rel_exists(relations, head_text, tail_text):
    for r in relations:
        if r['head'] == head_text and r['tail'] == tail_text:
            return True
    return False

def add_rel(relations, h, t, label):
    if rel_exists(relations, h['text'], t['text']):
        return False
    relations.append({
        'head': h['text'], 'head_start': h['start'], 'head_end': h['end'], 'head_type': h['label'],
        'tail': t['text'], 'tail_start': t['start'], 'tail_end': t['end'], 'tail_type': t['label'],
        'label': label
    })
    return True

stats = defaultdict(int)
results = []

for item in v3_data:
    text = item['text']
    entities = item.get('entities', [])
    relations = list(item.get('relations', []))

    by_type = defaultdict(list)
    for e in entities:
        by_type[e['label']].append(e)

    # ===== 规则 1: CROP → CON → VAR =====
    # 两实体间文本有包含关系词，且距离 < 120 字符
    for crop in by_type.get('CROP', []):
        for var in by_type.get('VAR', []):
            if rel_exists(relations, crop['text'], var['text']):
                continue
            bt = between_text(text, crop, var)
            if bt and len(bt) < 100 and has_pattern(bt, CON_BETWEEN):
                if add_rel(relations, crop, var, 'CON'):
                    stats['CON_CROP_VAR'] += 1

    # ===== 规则 2: VAR/CROSS/CROP → USE → BM =====
    for head_type in ['VAR', 'CROSS', 'CROP']:
        for head in by_type.get(head_type, []):
            for bm in by_type.get('BM', []):
                if rel_exists(relations, head['text'], bm['text']):
                    continue
                bt = between_text(text, head, bm)
                if bt and len(bt) < 80 and has_pattern(bt, USE_BETWEEN):
                    if add_rel(relations, head, bm, 'USE'):
                        stats[f'USE_{head_type}_BM'] += 1

    # ===== 规则 3: QTL → AFF → TRT =====
    for qtl in by_type.get('QTL', []):
        for trt in by_type.get('TRT', []):
            if rel_exists(relations, qtl['text'], trt['text']):
                continue
            bt = between_text(text, qtl, trt)
            if bt and len(bt) < 60 and has_pattern(bt, AFF_BETWEEN):
                if add_rel(relations, qtl, trt, 'AFF'):
                    stats['AFF_QTL_TRT'] += 1

    # ===== 规则 4: GENE → AFF → TRT (补充漏标) =====
    for gene in by_type.get('GENE', []):
        for trt in by_type.get('TRT', []):
            if rel_exists(relations, gene['text'], trt['text']):
                continue
            bt = between_text(text, gene, trt)
            if bt and len(bt) < 60 and has_pattern(bt, AFF_BETWEEN):
                if add_rel(relations, gene, trt, 'AFF'):
                    stats['AFF_GENE_TRT'] += 1

    # ===== 规则 5: MRK → LOI → CHR =====
    for mrk in by_type.get('MRK', []):
        for chr_ in by_type.get('CHR', []):
            if rel_exists(relations, mrk['text'], chr_['text']):
                continue
            bt = between_text(text, mrk, chr_)
            if bt and len(bt) < 60 and has_pattern(bt, LOI_BETWEEN):
                if add_rel(relations, mrk, chr_, 'LOI'):
                    stats['LOI_MRK_CHR'] += 1

    # ===== 规则 6: QTL → LOI → CHR (补充) =====
    for qtl in by_type.get('QTL', []):
        for chr_ in by_type.get('CHR', []):
            if rel_exists(relations, qtl['text'], chr_['text']):
                continue
            bt = between_text(text, qtl, chr_)
            if bt and len(bt) < 60 and has_pattern(bt, LOI_BETWEEN):
                if add_rel(relations, qtl, chr_, 'LOI'):
                    stats['LOI_QTL_CHR'] += 1

    # ===== 规则 7: TRT/ABS → OCI → GST =====
    for head_type in ['TRT', 'ABS']:
        for head in by_type.get(head_type, []):
            for gst in by_type.get('GST', []):
                if rel_exists(relations, head['text'], gst['text']):
                    continue
                bt = between_text(text, head, gst)
                if bt and len(bt) < 50 and has_pattern(bt, OCI_BETWEEN):
                    if add_rel(relations, head, gst, 'OCI'):
                        stats[f'OCI_{head_type}_GST'] += 1

    results.append({'text': text, 'entities': entities, 'relations': relations})

# ===== 保存 =====
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# ===== 统计 =====
print(f"\n=== 后处理统计 ===")
for k, v in sorted(stats.items()):
    print(f"  {k}: +{v}")
total_added = sum(stats.values())
print(f"  总计新增关系: {total_added}")

v3_total = sum(len(x.get('relations',[])) for x in v3_data)
v16_total = sum(len(x.get('relations',[])) for x in results)
v16_no_rel = sum(1 for x in results if not x.get('relations'))
print(f"\n=== 对比 ===")
print(f"  v3  关系均值: {v3_total/400:.2f}/条")
print(f"  v16 关系均值: {v16_total/400:.2f}/条（期望 2.80）")
print(f"  v16 无关系比例: {v16_no_rel/400*100:.1f}%（期望 32.7%）")
print(f"\n输出: {OUTPUT_PATH}")
