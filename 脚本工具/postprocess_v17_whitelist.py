#!/usr/bin/env python3
"""
postprocess_v17_whitelist.py
基于训练集触发词分析的极保守白名单后处理
在 ensemble_v3 基础上补充高置信度漏标关系

核心设计原则：
1. 只使用训练集中出现频率高且语义明确的触发词
2. 严格限制实体类型组合（只允许训练集中出现的组合）
3. 不允许跨句（间隔文本不含句号/分号）
4. 距离约束：不同规则有不同的最大距离
5. 每对实体只补一条关系（已存在则跳过）

训练集分析结论：
- LOI "for": QTL/MRK/GENE → TRT，间距通常 1-5 字符（直接接触）
- LOI "on": QTL/MRK/GENE → CHR，间距通常 1-5 字符
- LOI "on chromosome": 最安全的 LOI 规则
- CON "(": CROP → VAR，括号内是品种缩写
- AFF "regulates/controls/affects": GENE/QTL → TRT
"""

import json
import re
import sys
from copy import deepcopy

INPUT_PATH  = '数据/A榜/submit_ensemble_v3.json'
OUTPUT_PATH = '数据/A榜/submit_v17_whitelist.json'
TRAIN_PATH  = '/home/ubuntu/CCL2026-BreedIE/dataset/train.json'

# ===== 白名单规则定义 =====
# 格式: (label, head_types, tail_types, pattern, max_dist, description)
# max_dist: 头尾实体之间的最大字符距离（不含实体本身）
# pattern: 在 between 文本上匹配

WHITELIST_RULES = [
    # ---- LOI 规则（最安全，训练集中 on/for 出现频率最高）----
    # QTL/MRK/GENE for TRT（QTL for drought tolerance 等）
    # 注意：必须是 "X for Y" 且 X 是 QTL/MRK/GENE，Y 是 TRT
    # 距离限制：<= 5 字符（直接 "for" 连接）
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['TRT'],
        re.compile(r'^\s*for\s*$', re.I),
        5,
        'QTL/MRK/GENE for TRT'
    ),
    # QTL/MRK/GENE on CHR（QTL on chromosome 3H 等）
    # 注意：移除 TRT，因为训练集中 TRT on CHR 不是 LOI（是 "QTL for TRT on CHR" 结构）
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'^\s*on\s*$', re.I),
        5,
        'QTL/MRK/GENE on CHR'
    ),
    # "mapped to" / "located on" / "identified on" → LOI
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'\b(mapped to|located on|identified on|detected on|were identified on|were located on)\b', re.I),
        50,
        'mapped to/located on CHR'
    ),
    # "were identified for" / "is for" → LOI（QTL for TRT）
    (
        'LOI',
        ['QTL', 'MRK'],
        ['TRT'],
        re.compile(r'\b(were identified for|is for|were detected for|were mapped for)\b', re.I),
        30,
        'were identified for TRT'
    ),
    # "associated with" 短距离 → LOI（QTL/MRK associated with TRT）
    (
        'LOI',
        ['QTL', 'MRK'],
        ['TRT'],
        re.compile(r'\b(associated with|were associated with|significantly associated with)\b', re.I),
        30,
        'QTL/MRK associated with TRT'
    ),

    # ---- AFF 规则 ----
    # GENE/QTL regulates/controls/affects TRT
    # 注意：移除 confers（训练集中是 LOI/HAS）
    # controls 需要短距离（训练集中远距离的 controls 往往是跨句的 AFF，不安全）
    (
        'AFF',
        ['GENE', 'QTL', 'BM'],
        ['TRT'],
        re.compile(r'\b(regulates|affects|mediates|influences|determines)\b', re.I),
        40,
        'GENE/QTL regulates TRT'
    ),
    # controls 单独处理，限制短距离
    (
        'AFF',
        ['GENE', 'QTL'],
        ['TRT'],
        re.compile(r'^\s*controls\s*(the)?\s*$', re.I),
        20,
        'GENE/QTL controls TRT（短距离）'
    ),
    # "by increasing/decreasing/enhancing" → AFF
    (
        'AFF',
        ['GENE', 'QTL'],
        ['TRT'],
        re.compile(r'\bby (increasing|decreasing|enhancing|reducing|improving|promoting)\b', re.I),
        40,
        'GENE/QTL by increasing TRT'
    ),
    # "causes" → AFF
    (
        'AFF',
        ['GENE', 'QTL', 'MRK'],
        ['TRT'],
        re.compile(r'\bcauses\b', re.I),
        30,
        'GENE causes TRT'
    ),

    # ---- HAS 规则 ----
    # CROP/VAR showed/showing TRT
    (
        'HAS',
        ['CROP', 'VAR', 'CROSS'],
        ['TRT'],
        re.compile(r'\b(showed|showing|exhibited|exhibiting|displayed|displaying)\b', re.I),
        40,
        'CROP/VAR showed TRT'
    ),
    # CROP/VAR with high/improved/enhanced TRT
    (
        'HAS',
        ['CROP', 'VAR', 'CROSS'],
        ['TRT'],
        re.compile(r'\bwith (high|improved|enhanced|greater|better|increased|superior|excellent)\b', re.I),
        30,
        'CROP/VAR with high TRT'
    ),
    # CROP/VAR have/has TRT
    (
        'HAS',
        ['CROP', 'VAR', 'CROSS'],
        ['TRT'],
        re.compile(r'\b(have|has)\b', re.I),
        15,
        'CROP/VAR have TRT（短距离）'
    ),

    # ---- CON 规则 ----
    # CROP (VAR) — 括号内是品种名
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'^\s*\(\s*$', re.I),
        3,
        'CROP (VAR)'
    ),
    # CROP variety/cultivar VAR
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'\b(variety|cultivar|cv\.|genotype|accession|line)\b', re.I),
        30,
        'CROP variety VAR'
    ),

    # ---- OCI 规则 ----
    # 注意：'at the' 规则在训练集上精确率为 0，暂时禁用
    # 只保留最确定的 OCI 解析：实体直接接触生长阶段
    # (
    #     'OCI',
    #     ['CROP', 'VAR', 'GENE', 'QTL'],
    #     ['GST'],
    #     re.compile(r'\bat (the)?\b', re.I),
    #     20,
    #     'X at the GST'
    # ),
]


def get_between(text, rel_or_ent1, rel_or_ent2):
    """获取两个实体之间的文本及距离"""
    # 支持 entity dict 格式（有 start/end）
    if 'start' in rel_or_ent1:
        h_start = rel_or_ent1['start']
        h_end = rel_or_ent1['end']
    else:
        h_start = rel_or_ent1.get('head_start', 0)
        h_end = rel_or_ent1.get('head_end', 0)
    
    if 'start' in rel_or_ent2:
        t_start = rel_or_ent2['start']
        t_end = rel_or_ent2['end']
    else:
        t_start = rel_or_ent2.get('tail_start', 0)
        t_end = rel_or_ent2.get('tail_end', 0)
    
    if h_end <= t_start:
        between = text[h_end:t_start]
        dist = t_start - h_end
        direction = 'h->t'
    elif t_end <= h_start:
        between = text[t_end:h_start]
        dist = h_start - t_end
        direction = 't->h'
    else:
        return None, -1, None
    
    return between, dist, direction


def is_cross_sentence(between):
    """判断是否跨句（含有句子终止符）"""
    return bool(re.search(r'[.!?;]', between))


def apply_whitelist(item, rules):
    """对一条数据应用白名单规则，返回新增的关系列表"""
    text = item['text']
    entities = item.get('entities', [])
    
    # 已有关系的集合（用于去重）
    existing_rels = set()
    for r in item.get('relations', []):
        existing_rels.add((r['head'].strip().lower(), r['tail'].strip().lower(), r['label']))
        # 双向去重（避免 A-B 和 B-A 同时存在）
        existing_rels.add((r['tail'].strip().lower(), r['head'].strip().lower(), r['label']))
    
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
                
                # 去重检查
                key = (h['text'].strip().lower(), t['text'].strip().lower(), rule_label)
                if key in existing_rels:
                    continue
                
                # 获取间隔文本
                between, dist, direction = get_between(text, h, t)
                if between is None or dist < 0:
                    continue
                
                # 距离约束
                if dist > max_dist:
                    continue
                
                # 不跨句约束
                if is_cross_sentence(between):
                    continue
                
                # 触发词匹配
                if pattern.search(between):
                    # 确定头尾方向（规则定义的是 head->tail）
                    if direction == 'h->t':
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
                            'trigger': between.strip(),
                            'rule': desc
                        }
                    else:
                        # t 在 h 前面，交换
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
                            'trigger': between.strip(),
                            'rule': desc
                        }
                    
                    new_rels.append(new_rel)
                    existing_rels.add(key)
                    existing_rels.add((t['text'].strip().lower(), h['text'].strip().lower(), rule_label))
    
    return new_rels


def validate_on_train(train_data, rules, sample_size=None):
    """在训练集上验证规则精确率（模拟：假设 v3 已有正确关系，只看新增部分）"""
    from collections import defaultdict
    
    tp_by_label = defaultdict(int)
    fp_by_label = defaultdict(int)
    fp_examples = defaultdict(list)
    
    data = train_data[:sample_size] if sample_size else train_data
    
    for item in data:
        gold_rels = {(r['head'].strip().lower(), r['tail'].strip().lower(), r['label']) 
                     for r in item.get('relations', [])}
        
        # 模拟 v3：假设 v3 已经有了所有正确关系（最坏情况验证）
        # 实际上 v3 已有部分，新增的才是我们关心的
        fake_item = deepcopy(item)
        fake_item['relations'] = []  # 清空，从零开始
        
        new_rels = apply_whitelist(fake_item, rules)
        
        for rel in new_rels:
            key = (rel['head'].strip().lower(), rel['tail'].strip().lower(), rel['label'])
            if key in gold_rels:
                tp_by_label[rel['label']] += 1
            else:
                fp_by_label[rel['label']] += 1
                if len(fp_examples[rel['label']]) < 3:
                    fp_examples[rel['label']].append(rel)
    
    return tp_by_label, fp_by_label, fp_examples


# ===== 主程序 =====
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'validate'
    
    print(f"模式: {mode}")
    
    # 加载训练集
    train_data = json.load(open(TRAIN_PATH, encoding='utf-8'))
    
    if mode == 'validate':
        print("\n=== 在训练集上验证白名单规则精确率 ===\n")
        tp, fp, fp_examples = validate_on_train(train_data, WHITELIST_RULES)
        
        print(f"{'关系':6} {'TP':6} {'FP':6} {'精确率':8} {'召回贡献'}")
        print("-" * 50)
        total_tp = total_fp = 0
        for label in ['LOI', 'AFF', 'HAS', 'CON', 'USE', 'OCI']:
            t = tp[label]
            f = fp[label]
            total = t + f
            prec = t / total if total > 0 else 0
            print(f"{label:6} {t:6} {f:6} {prec:8.1%}")
            total_tp += t
            total_fp += f
        
        total = total_tp + total_fp
        print("-" * 50)
        print(f"{'合计':6} {total_tp:6} {total_fp:6} {total_tp/total if total>0 else 0:8.1%}")
        
        print("\n=== FP 样本分析 ===")
        for label, examples in fp_examples.items():
            print(f"\n[{label}] FP 样本：")
            for ex in examples:
                print(f"  [{ex['head_type']}]{ex['head']} --{ex['label']}--> [{ex['tail_type']}]{ex['tail']}")
                print(f"  触发词: \"{ex['trigger']}\" | 规则: {ex['rule']}")
    
    elif mode == 'apply':
        print("\n=== 应用白名单规则到 ensemble_v3 ===\n")
        v3_data = json.load(open(INPUT_PATH, encoding='utf-8'))
        
        output = []
        total_new = 0
        new_by_label = {}
        
        for item in v3_data:
            new_item = deepcopy(item)
            new_rels = apply_whitelist(new_item, WHITELIST_RULES)
            
            # 只保留提交格式需要的字段
            clean_new_rels = []
            for r in new_rels:
                clean_new_rels.append({
                    'head': r['head'],
                    'head_type': r['head_type'],
                    'head_start': r['head_start'],
                    'head_end': r['head_end'],
                    'tail': r['tail'],
                    'tail_type': r['tail_type'],
                    'tail_start': r['tail_start'],
                    'tail_end': r['tail_end'],
                    'label': r['label']
                })
                new_by_label[r['label']] = new_by_label.get(r['label'], 0) + 1
            
            new_item['relations'] = item['relations'] + clean_new_rels
            output.append(new_item)
            total_new += len(new_rels)
        
        json.dump(output, open(OUTPUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        
        print(f"输入: {INPUT_PATH}")
        print(f"输出: {OUTPUT_PATH}")
        print(f"原始关系数: {sum(len(x.get('relations',[])) for x in v3_data)}")
        print(f"新增关系数: {total_new}")
        print(f"最终关系数: {sum(len(x.get('relations',[])) for x in output)}")
        print(f"\n新增关系分布:")
        for label, cnt in sorted(new_by_label.items()):
            print(f"  {label}: +{cnt}")
        
        print(f"\n文件已保存到: {OUTPUT_PATH}")
