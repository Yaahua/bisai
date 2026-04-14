#!/usr/bin/env python3
"""
postprocess_v18_whitelist.py — 精确率优先版
在 ensemble_v3 基础上补充高置信度漏标关系

基于训练集验证结果，只保留精确率 >= 70% 的规则：
- 剔除: TRT-AFF-TRT(and), QTL-AFF-TRT(controlling), BIS-AFF-CROP(in),
         ABS-stress-on-TRT, CROP(CROP)括号, CROSS-CON-VAR(of/from),
         GENE-confers-TRT, GENE-in-CROP, VAR-USE-BM(using), genes-from-CROP,
         BM-USE-MRK(with)
- 保留并优化: mapped-to-CHR(收紧距离), CROP-with-high-TRT(收紧)
- 新增验证通过: TRT-OCI-GST(86.7%), ABS-OCI-GST(100%), BIS-OCI-GST(100%),
                ABS-reduced-TRT(85.7%), ABS-induced-GENE(81.8%),
                CROP-including-VAR(100%)
"""

import json
import re
import sys
from copy import deepcopy
from collections import defaultdict, Counter

INPUT_PATH  = '数据/A榜/submit_ensemble_v3.json'
OUTPUT_PATH = '数据/A榜/submit_v18_whitelist.json'
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'

# ===== 白名单规则定义 =====
# 只保留训练集验证精确率 >= 70% 的规则

WHITELIST_RULES = [
    # ================================================================
    # LOI 规则（精确率 75.6% 整体，逐条优化）
    # ================================================================
    # QTL/MRK/GENE for TRT — 77.8%
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['TRT'],
        re.compile(r'^\s*for\s*$', re.I),
        5,
        'QTL/MRK/GENE for TRT'
    ),
    # QTL/MRK/GENE on CHR — 87.0%
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'^\s*on\s*$', re.I),
        5,
        'QTL/MRK/GENE on CHR'
    ),
    # "mapped to" / "located on" → LOI CHR — 只保留最安全的触发词，距离15
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'\b(mapped to|located on|mapped on)\b', re.I),
        15,
        'mapped to/located on CHR'
    ),
    # "were identified for" → LOI TRT — 100%
    (
        'LOI',
        ['QTL', 'MRK'],
        ['TRT'],
        re.compile(r'\b(were identified for|is for|were detected for|were mapped for|identified for)\b', re.I),
        30,
        'were identified for TRT'
    ),
    # "associated with" → LOI TRT — 82.9%
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['TRT'],
        re.compile(r'\b(associated with|were associated with|significantly associated with|is associated with)\b', re.I),
        30,
        'QTL/MRK/GENE associated with TRT'
    ),
    # [v18] "on chromosome" 长触发词 — 最安全
    (
        'LOI',
        ['QTL', 'MRK', 'GENE'],
        ['CHR'],
        re.compile(r'\bon chromosome\b', re.I),
        20,
        '[v18] on chromosome'
    ),

    # ================================================================
    # AFF 规则（只保留高精确率子规则）
    # ================================================================
    # GENE/QTL mediates/determines TRT — 移除 regulates（50%精确率太低）
    (
        'AFF',
        ['GENE'],
        ['TRT'],
        re.compile(r'\b(mediates|determines|modulates)\b', re.I),
        30,
        'GENE mediates/determines TRT'
    ),
    # "by increasing/decreasing" → AFF — 保留但收紧
    (
        'AFF',
        ['GENE', 'QTL'],
        ['TRT'],
        re.compile(r'\b(increasing|decreasing|enhancing|reducing|improving|promoting|inhibiting)\b', re.I),
        30,
        'GENE by increasing/decreasing TRT'
    ),
    # [v18] ABS-AFF-TRT — "reduced/affected" — 85.7%
    (
        'AFF',
        ['ABS'],
        ['TRT'],
        re.compile(r'\b(reduced|affected|decreased|inhibited|impaired|increased|enhanced)\b', re.I),
        30,
        '[v18] ABS reduced/affected TRT'
    ),
    # [v18] ABS-AFF-GENE — "induced/upregulated" — 81.8%
    (
        'AFF',
        ['ABS'],
        ['GENE'],
        re.compile(r'\b(induced|upregulated|downregulated|activated|repressed)\b', re.I),
        30,
        '[v18] ABS induced/regulated GENE'
    ),
    # [v18] BIS-AFF-TRT — 只用 "resistance to" 短距离
    (
        'AFF',
        ['BIS'],
        ['TRT'],
        re.compile(r'\b(resistance to|tolerance to)\b', re.I),
        15,
        '[v18] BIS resistance/tolerance to TRT'
    ),

    # ================================================================
    # HAS 规则（精确率 80.0% 整体）
    # ================================================================
    # CROP/VAR showed TRT — 高精确率
    (
        'HAS',
        ['CROP', 'VAR', 'CROSS'],
        ['TRT'],
        re.compile(r'\b(showed|showing|exhibited|exhibiting|displayed|displaying|demonstrated)\b', re.I),
        40,
        'CROP/VAR showed TRT'
    ),
    # CROP/VAR with high TRT — 收紧距离到20
    (
        'HAS',
        ['CROP', 'VAR', 'CROSS'],
        ['TRT'],
        re.compile(r'\bwith (high|improved|enhanced|greater|better|increased|superior|excellent)\b', re.I),
        20,
        'CROP/VAR with high TRT (tight)'
    ),
    # CROP/VAR have TRT — 短距离
    (
        'HAS',
        ['CROP', 'VAR', 'CROSS'],
        ['TRT'],
        re.compile(r'\b(have|has|had)\b', re.I),
        15,
        'CROP/VAR have TRT'
    ),

    # ================================================================
    # CON 规则（只保留高精确率子规则）
    # ================================================================
    # CROP (VAR) — 括号 — 原v17规则
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'^\s*\(\s*$', re.I),
        3,
        'CROP (VAR)'
    ),
    # CROP variety/cultivar VAR — 原v17规则
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'\b(variety|cultivar|cv\.|genotype|accession|line|landrace)\b', re.I),
        30,
        'CROP variety VAR'
    ),
    # [v18] CROP including VAR — 100%
    (
        'CON',
        ['CROP'],
        ['VAR'],
        re.compile(r'\b(including|such as|namely)\b', re.I),
        40,
        '[v18] CROP including VAR'
    ),

    # ================================================================
    # OCI 规则（v18 全新，验证精确率极高）
    # ================================================================
    # [v18] TRT-OCI-GST — "at the" / "during the" — 86.7%
    (
        'OCI',
        ['TRT'],
        ['GST'],
        re.compile(r'\b(at the|during the|at|during)\b', re.I),
        20,
        '[v18] TRT at the GST'
    ),
    # [v18] ABS-OCI-GST — 100%
    (
        'OCI',
        ['ABS'],
        ['GST'],
        re.compile(r'\b(at the|during the|at|during|in the)\b', re.I),
        20,
        '[v18] ABS at the GST'
    ),
    # [v18] BIS-OCI-GST — 100%
    (
        'OCI',
        ['BIS'],
        ['GST'],
        re.compile(r'\b(at the|during the|at|during|in the)\b', re.I),
        20,
        '[v18] BIS at the GST'
    ),
]


def get_between(text, ent1, ent2):
    """获取两个实体之间的文本及距离"""
    h_start = ent1['start']
    h_end = ent1['end']
    t_start = ent2['start']
    t_end = ent2['end']
    
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
    """判断是否跨句"""
    return bool(re.search(r'[.!?;]', between))


def apply_whitelist(item, rules):
    """对一条数据应用白名单规则，返回新增的关系列表"""
    text = item['text']
    entities = item.get('entities', [])
    
    existing_rels = set()
    for r in item.get('relations', []):
        existing_rels.add((r['head'].strip().lower(), r['tail'].strip().lower(), r['label']))
        existing_rels.add((r['tail'].strip().lower(), r['head'].strip().lower(), r['label']))
    
    new_rels = []
    
    for rule_label, head_types, tail_types, pattern, max_dist, desc in rules:
        for h in entities:
            if h['label'] not in head_types:
                continue
            for t in entities:
                if t['label'] not in tail_types:
                    continue
                if h['text'] == t['text'] and h['start'] == t['start']:
                    continue
                
                key = (h['text'].strip().lower(), t['text'].strip().lower(), rule_label)
                if key in existing_rels:
                    continue
                
                between, dist, direction = get_between(text, h, t)
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
                        'trigger': between.strip(),
                        'rule': desc
                    }
                    
                    new_rels.append(new_rel)
                    existing_rels.add(key)
                    existing_rels.add((t['text'].strip().lower(), h['text'].strip().lower(), rule_label))
    
    return new_rels


def validate_on_train(train_data, rules):
    """在训练集上验证规则精确率"""
    tp_by_rule = defaultdict(int)
    fp_by_rule = defaultdict(int)
    tp_by_label = defaultdict(int)
    fp_by_label = defaultdict(int)
    fp_examples = defaultdict(list)
    
    for item in train_data:
        gold_rels = set()
        for r in item.get('relations', []):
            gold_rels.add((r['head'].strip().lower(), r['tail'].strip().lower(), r['label']))
        
        fake_item = deepcopy(item)
        fake_item['relations'] = []
        
        new_rels = apply_whitelist(fake_item, rules)
        
        for rel in new_rels:
            key = (rel['head'].strip().lower(), rel['tail'].strip().lower(), rel['label'])
            rule_name = rel['rule']
            if key in gold_rels:
                tp_by_rule[rule_name] += 1
                tp_by_label[rel['label']] += 1
            else:
                fp_by_rule[rule_name] += 1
                fp_by_label[rel['label']] += 1
                if len(fp_examples[rule_name]) < 2:
                    fp_examples[rule_name].append(rel)
    
    return tp_by_rule, fp_by_rule, tp_by_label, fp_by_label, fp_examples


# ===== 主程序 =====
if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'validate'
    
    print(f"模式: {mode}")
    
    train_data = json.load(open(TRAIN_PATH, encoding='utf-8'))
    
    if mode == 'validate':
        print("\n=== 在训练集上验证 v18 白名单规则精确率（精确率优先版）===\n")
        tp_rule, fp_rule, tp_label, fp_label, fp_examples = validate_on_train(train_data, WHITELIST_RULES)
        
        print(f"{'规则':<45} {'TP':>5} {'FP':>5} {'精确率':>8}")
        print("-" * 70)
        all_rules = set(list(tp_rule.keys()) + list(fp_rule.keys()))
        for rule in sorted(all_rules):
            t = tp_rule[rule]
            f = fp_rule[rule]
            total = t + f
            prec = t / total if total > 0 else 0
            flag = " !!!" if prec < 0.5 else (" !" if prec < 0.7 else "")
            print(f"{rule:<45} {t:>5} {f:>5} {prec:>7.1%}{flag}")
        
        print(f"\n{'关系':6} {'TP':>6} {'FP':>6} {'精确率':>8}")
        print("-" * 35)
        total_tp = total_fp = 0
        for label in ['LOI', 'AFF', 'HAS', 'CON', 'USE', 'OCI']:
            t = tp_label[label]
            f = fp_label[label]
            total = t + f
            prec = t / total if total > 0 else 0
            print(f"{label:6} {t:>6} {f:>6} {prec:>7.1%}")
            total_tp += t
            total_fp += f
        
        total = total_tp + total_fp
        print("-" * 35)
        print(f"{'合计':6} {total_tp:>6} {total_fp:>6} {total_tp/total if total>0 else 0:>7.1%}")
        
        print("\n=== 低精确率规则 FP 样本 ===")
        for rule in sorted(fp_examples.keys()):
            t = tp_rule[rule]
            f = fp_rule[rule]
            prec = t / (t+f) if (t+f) > 0 else 0
            if prec < 0.7:
                print(f"\n[{rule}] 精确率={prec:.1%}")
                for ex in fp_examples[rule]:
                    print(f"  [{ex['head_type']}]{ex['head']} --{ex['label']}--> [{ex['tail_type']}]{ex['tail']}")
                    print(f"  触发词: \"{ex['trigger']}\"")
    
    elif mode == 'apply':
        print("\n=== 应用 v18 白名单规则到 ensemble_v3 ===\n")
        v3_data = json.load(open(INPUT_PATH, encoding='utf-8'))
        
        output = []
        total_new = 0
        new_by_label = Counter()
        new_by_rule = Counter()
        
        for item in v3_data:
            new_item = deepcopy(item)
            new_rels = apply_whitelist(new_item, WHITELIST_RULES)
            
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
                new_by_label[r['label']] += 1
                new_by_rule[r['rule']] += 1
            
            new_item['relations'] = item['relations'] + clean_new_rels
            output.append(new_item)
            total_new += len(new_rels)
        
        json.dump(output, open(OUTPUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        
        total_rels = sum(len(x.get('relations', [])) for x in output)
        no_rel = sum(1 for x in output if not x.get('relations'))
        
        print(f"输入: {INPUT_PATH}")
        print(f"输出: {OUTPUT_PATH}")
        print(f"原始关系数: {sum(len(x.get('relations',[])) for x in v3_data)}")
        print(f"新增关系数: {total_new}")
        print(f"最终关系数: {total_rels}")
        print(f"关系均值: {total_rels/len(output):.2f}")
        print(f"无关系比例: {no_rel/len(output)*100:.1f}%")
        
        print(f"\n新增关系按类型:")
        for label, cnt in new_by_label.most_common():
            print(f"  {label}: +{cnt}")
        
        print(f"\n新增关系按规则:")
        for rule, cnt in new_by_rule.most_common():
            print(f"  {rule}: +{cnt}")
        
        print(f"\n文件已保存到: {OUTPUT_PATH}")
