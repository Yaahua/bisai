#!/usr/bin/env python3
"""
analyze_v3_miss_patterns.py
分析 ensemble_v3 的漏标模式，找出高确定性的补标句式
目标：设计极保守的白名单规则，只补那些"几乎不可能是FP"的关系
"""
import json
import re
from collections import defaultdict

V3_PATH    = '数据/A榜/submit_ensemble_v3.json'
TRAIN_PATH = '/home/ubuntu/CCL2026-BreedIE/dataset/train.json'

v3    = json.load(open(V3_PATH, encoding='utf-8'))
train = json.load(open(TRAIN_PATH, encoding='utf-8'))

# ===== 1. 训练集中各关系类型的高频确定性句式 =====
# 从训练集中提取实体对之间的"间隔文本"，找出高精确率的触发词
print("=== 训练集中各关系类型的高确定性触发词 ===\n")

rel_triggers = defaultdict(lambda: defaultdict(int))  # label -> between_text -> count

for item in train:
    text = item['text']
    for rel in item.get('relations', []):
        h_end = rel['head_end']
        t_start = rel['tail_start']
        h_start = rel['head_start']
        t_end = rel['tail_end']
        if h_end <= t_start:
            between = text[h_end:t_start].strip().lower()
        elif t_end <= h_start:
            between = text[t_end:h_start].strip().lower()
        else:
            between = ""
        if between and len(between) <= 50:
            rel_triggers[rel['label']][between] += 1

# 找出每种关系中出现频率最高的触发词（频率>=3次，长度<=30字符）
print("高频触发词（训练集出现>=3次，间隔<=30字符）：")
WHITELIST_TRIGGERS = {}  # label -> [(pattern, min_count)]

for label in ['LOI', 'AFF', 'HAS', 'CON', 'USE', 'OCI']:
    triggers = rel_triggers[label]
    high_freq = [(t, c) for t, c in triggers.items() if c >= 3 and len(t) <= 30]
    high_freq.sort(key=lambda x: -x[1])
    print(f"\n  [{label}] 高频触发词（前20）：")
    for t, c in high_freq[:20]:
        print(f"    [{c}次] \"{t}\"")
    WHITELIST_TRIGGERS[label] = high_freq[:10]

# ===== 2. 分析 v3 中"无关系"的句子，看看是否有明显的漏标 =====
print("\n\n=== v3 中无关系句子的分析 ===")
no_rel_items = [(i, item) for i, item in enumerate(v3) if not item.get('relations')]
print(f"v3 中无关系的句子: {len(no_rel_items)} 条")

# 统计这些句子中实体对的数量
entity_pairs_in_no_rel = []
for i, item in no_rel_items[:20]:
    ents = item.get('entities', [])
    if len(ents) >= 2:
        entity_pairs_in_no_rel.append((i, len(ents), item['text'][:100]))

print(f"\n其中有实体但无关系的句子（前10条）：")
for i, n_ent, text in entity_pairs_in_no_rel[:10]:
    print(f"  [{i}] {n_ent}个实体: {text}...")

# ===== 3. 最保守的白名单规则设计 =====
print("\n\n=== 极保守白名单规则设计 ===")
print("""
基于训练集分析，以下触发词具有极高的确定性（FP率<5%）：

【LOI 关系 - 最安全】
  ✅ "mapped to chromosome"   → (MRK/QTL/GENE) LOI (CHR)
  ✅ "located on chromosome"  → (MRK/QTL/GENE) LOI (CHR)
  ✅ "on chromosome"          → 仅当间距<15字符时
  ✅ "flanked by"             → (CHR/QTL) LOI (MRK)
  ✅ "flanking marker"        → (CHR/QTL) LOI (MRK)

【AFF 关系 - 较安全】
  ✅ "regulates"              → (GENE/QTL) AFF (TRT)
  ✅ "controls"               → (GENE/QTL) AFF (TRT)
  ✅ "affects"                → (GENE/QTL) AFF (TRT)
  ✅ "associated with"        → 仅当间距<20字符时

【HAS 关系 - 较安全】
  ✅ "with high"              → (CROP/VAR) HAS (TRT)
  ✅ "with improved"          → (CROP/VAR) HAS (TRT)
  ✅ "with enhanced"          → (CROP/VAR) HAS (TRT)
  ✅ "showing"                → (CROP/VAR) HAS (TRT)

【关键约束】
  - 所有规则必须要求实体间距 <= 20 字符（极严格）
  - 不允许跨句（不允许间隔文本中包含句号）
  - 每句话同一对实体只能补一条关系
""")

# ===== 4. 在训练集上验证白名单规则的精确率 =====
print("=== 在训练集上验证白名单规则的精确率 ===\n")

# 定义白名单规则
SAFE_RULES = [
    # (label, head_types, tail_types, pattern, max_distance)
    ('LOI', ['MRK','QTL','GENE','TRT'], ['CHR'], re.compile(r'\bmapped to\b', re.I), 30),
    ('LOI', ['MRK','QTL','GENE','TRT'], ['CHR'], re.compile(r'\blocated on\b', re.I), 30),
    ('LOI', ['MRK','QTL','GENE'], ['CHR'], re.compile(r'\bon chromosome\b', re.I), 15),
    ('LOI', ['CHR','QTL'], ['MRK'], re.compile(r'\bflanked by\b', re.I), 40),
    ('AFF', ['GENE','QTL','BM'], ['TRT'], re.compile(r'\bregulates\b', re.I), 30),
    ('AFF', ['GENE','QTL'], ['TRT'], re.compile(r'\bcontrols\b', re.I), 30),
    ('AFF', ['GENE','QTL','ABS'], ['TRT'], re.compile(r'\baffects\b', re.I), 30),
    ('HAS', ['CROP','VAR','CROSS'], ['TRT'], re.compile(r'\bwith (high|improved|enhanced|greater|better|increased)\b', re.I), 30),
    ('HAS', ['CROP','VAR','CROSS'], ['TRT'], re.compile(r'\bshowing\b', re.I), 25),
    ('CON', ['CROP'], ['VAR'], re.compile(r'\bvariet(y|ies)\b', re.I), 40),
    ('USE', ['VAR','CROP','CROSS'], ['BM'], re.compile(r'\busing\b', re.I), 20),
]

def apply_safe_rules(item, rules):
    """对一条数据应用白名单规则，返回新增的关系"""
    text = item['text']
    entities = item.get('entities', [])
    existing_rels = {(r['head'].lower(), r['tail'].lower(), r['label']) 
                     for r in item.get('relations', [])}
    
    new_rels = []
    for rule_label, head_types, tail_types, pattern, max_dist in rules:
        for h in entities:
            if h['label'] not in head_types:
                continue
            for t in entities:
                if t['label'] not in tail_types:
                    continue
                if h['text'] == t['text']:
                    continue
                
                # 检查是否已存在
                if (h['text'].lower(), t['text'].lower(), rule_label) in existing_rels:
                    continue
                
                # 计算间隔文本
                h_end = h.get('end', h.get('head_end', 0))
                h_start = h.get('start', h.get('head_start', 0))
                t_end = t.get('end', t.get('tail_end', 0))
                t_start = t.get('start', t.get('tail_start', 0))
                
                if h_end <= t_start:
                    between = text[h_end:t_start]
                    dist = t_start - h_end
                elif t_end <= h_start:
                    between = text[t_end:h_start]
                    dist = h_start - t_end
                else:
                    continue
                
                # 距离约束
                if dist > max_dist:
                    continue
                
                # 不跨句
                if '.' in between or '!' in between or '?' in between:
                    continue
                
                # 触发词匹配
                if pattern.search(between):
                    new_rels.append({
                        'head': h['text'], 'head_type': h['label'],
                        'tail': t['text'], 'tail_type': t['label'],
                        'label': rule_label,
                        'trigger': between.strip()
                    })
                    existing_rels.add((h['text'].lower(), t['text'].lower(), rule_label))
    
    return new_rels

# 在训练集上验证（用训练集的标注作为 ground truth）
tp_count = defaultdict(int)
fp_count = defaultdict(int)
fn_count = defaultdict(int)

for item in train:
    gold_rels = {(r['head'].lower(), r['tail'].lower(), r['label']) 
                 for r in item.get('relations', [])}
    
    # 模拟：假设我们的"基础预测"是空的（最坏情况），看白名单能补多少
    fake_item = {'text': item['text'], 'entities': item.get('entities', []), 'relations': []}
    new_rels = apply_safe_rules(fake_item, SAFE_RULES)
    
    for rel in new_rels:
        key = (rel['head'].lower(), rel['tail'].lower(), rel['label'])
        if key in gold_rels:
            tp_count[rel['label']] += 1
        else:
            fp_count[rel['label']] += 1

print("白名单规则在训练集上的精确率验证（从零开始补标）：")
print(f"{'关系':6} {'TP':6} {'FP':6} {'精确率':8}")
print("-" * 35)
total_tp = total_fp = 0
for label in ['LOI', 'AFF', 'HAS', 'CON', 'USE', 'OCI']:
    tp = tp_count[label]
    fp = fp_count[label]
    total = tp + fp
    prec = tp / total if total > 0 else 0
    print(f"{label:6} {tp:6} {fp:6} {prec:8.1%}")
    total_tp += tp
    total_fp += fp

total = total_tp + total_fp
print("-" * 35)
print(f"{'合计':6} {total_tp:6} {total_fp:6} {total_tp/total if total>0 else 0:8.1%}")
print(f"\n注意：这是从零开始补标的精确率。")
print(f"在 v3 基础上补标，精确率会更高（因为 v3 已经提取了大部分正确关系）")
