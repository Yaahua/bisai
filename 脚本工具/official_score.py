#!/usr/bin/env python3
"""
按照 CCL2026-MGBIE 官方评分公式计算得分。

评分规则（来自官方 README）：
  NER 评分：Score_NER = 0.5*F1 + 0.25*Precision + 0.25*Recall
  RE  评分：Score_RE  = 0.5*F1 + 0.25*Precision + 0.25*Recall
  最终得分：Total = 0.4*Score_NER + 0.6*Score_RE

评测方式：
  - NER：实体匹配需要 (start, end, label) 三元组完全一致
  - RE ：关系匹配需要 (head_start, head_end, head_type, tail_start, tail_end, tail_type, label) 完全一致

本脚本将 bisai 仓库中已修正的 300 条数据（chunk_001~030）作为"预测结果"，
将官方原始 train.json 中对应的 300 条作为"Gold 标准"，计算得分。
"""

import json
import glob
import os
from collections import defaultdict

# ============================================================
# 1. 加载官方训练集（Gold 标准）
# ============================================================
official_path = '/home/ubuntu/official_mgbie/dataset/train.json'
with open(official_path, 'r', encoding='utf-8') as f:
    official_data = json.load(f)

# 官方前 300 条（对应 chunk_001~030）
gold_300 = official_data[:300]
gold_map = {item['text']: item for item in gold_300}
print(f"Gold 标准条数: {len(gold_300)}")

# ============================================================
# 2. 加载 bisai 修订结果（预测结果）
# ============================================================
corrected_dir = '/home/ubuntu/bisai_clone/数据/训练集/修订结果'
corrected_files = sorted(glob.glob(os.path.join(corrected_dir, '*.json')))

all_corrected = []
for fp in corrected_files:
    with open(fp, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        all_corrected.extend(data)
    elif isinstance(data, dict):
        all_corrected.append(data)

print(f"修订结果总条数: {len(all_corrected)}")

# ============================================================
# 3. 对齐：用 text 字段匹配 Gold 和 Pred
# ============================================================
matched_pairs = []   # (gold_item, pred_item)
unmatched_pred = []  # pred 中 text 不在 gold 的条目

for pred_item in all_corrected:
    t = pred_item.get('text', '')
    if t in gold_map:
        matched_pairs.append((gold_map[t], pred_item))
    else:
        unmatched_pred.append(pred_item)

print(f"成功匹配条数（text 一致）: {len(matched_pairs)}")
print(f"pred 中 text 不在 gold 的条数（无法评分）: {len(unmatched_pred)}")

# ============================================================
# 4. NER 评分
#    匹配键：(start, end, label)
# ============================================================
ner_tp = 0
ner_fp = 0
ner_fn = 0

# 按标签细分
ner_tp_by_label = defaultdict(int)
ner_fp_by_label = defaultdict(int)
ner_fn_by_label = defaultdict(int)

for gold_item, pred_item in matched_pairs:
    gold_ents = set(
        (e['start'], e['end'], e['label'])
        for e in gold_item.get('entities', [])
    )
    pred_ents = set(
        (e['start'], e['end'], e['label'])
        for e in pred_item.get('entities', [])
        if isinstance(e.get('start'), int) and isinstance(e.get('end'), int)
    )

    tp = gold_ents & pred_ents
    fp = pred_ents - gold_ents
    fn = gold_ents - pred_ents

    ner_tp += len(tp)
    ner_fp += len(fp)
    ner_fn += len(fn)

    for (s, e, lbl) in tp:
        ner_tp_by_label[lbl] += 1
    for (s, e, lbl) in fp:
        ner_fp_by_label[lbl] += 1
    for (s, e, lbl) in fn:
        ner_fn_by_label[lbl] += 1

ner_precision = ner_tp / (ner_tp + ner_fp) if (ner_tp + ner_fp) > 0 else 0
ner_recall    = ner_tp / (ner_tp + ner_fn) if (ner_tp + ner_fn) > 0 else 0
ner_f1        = 2 * ner_precision * ner_recall / (ner_precision + ner_recall) \
                if (ner_precision + ner_recall) > 0 else 0
score_ner     = 0.5 * ner_f1 + 0.25 * ner_precision + 0.25 * ner_recall

print("\n" + "="*60)
print("NER 评分结果")
print("="*60)
print(f"  TP={ner_tp}, FP={ner_fp}, FN={ner_fn}")
print(f"  Precision : {ner_precision:.4f}")
print(f"  Recall    : {ner_recall:.4f}")
print(f"  F1        : {ner_f1:.4f}")
print(f"  Score_NER : {score_ner:.4f}")

# ============================================================
# 5. RE 评分
#    匹配键：(head_start, head_end, head_type, tail_start, tail_end, tail_type, label)
# ============================================================
re_tp = 0
re_fp = 0
re_fn = 0

re_tp_by_label = defaultdict(int)
re_fp_by_label = defaultdict(int)
re_fn_by_label = defaultdict(int)

for gold_item, pred_item in matched_pairs:
    gold_rels = set(
        (r['head_start'], r['head_end'], r['head_type'],
         r['tail_start'], r['tail_end'], r['tail_type'], r['label'])
        for r in gold_item.get('relations', [])
    )
    pred_rels = set(
        (r['head_start'], r['head_end'], r['head_type'],
         r['tail_start'], r['tail_end'], r['tail_type'], r['label'])
        for r in pred_item.get('relations', [])
        if all(k in r for k in ['head_start','head_end','head_type',
                                  'tail_start','tail_end','tail_type','label'])
    )

    tp = gold_rels & pred_rels
    fp = pred_rels - gold_rels
    fn = gold_rels - pred_rels

    re_tp += len(tp)
    re_fp += len(fp)
    re_fn += len(fn)

    for rel in tp:
        re_tp_by_label[rel[-1]] += 1
    for rel in fp:
        re_fp_by_label[rel[-1]] += 1
    for rel in fn:
        re_fn_by_label[rel[-1]] += 1

re_precision = re_tp / (re_tp + re_fp) if (re_tp + re_fp) > 0 else 0
re_recall    = re_tp / (re_tp + re_fn) if (re_tp + re_fn) > 0 else 0
re_f1        = 2 * re_precision * re_recall / (re_precision + re_recall) \
               if (re_precision + re_recall) > 0 else 0
score_re     = 0.5 * re_f1 + 0.25 * re_precision + 0.25 * re_recall

print("\n" + "="*60)
print("RE 评分结果")
print("="*60)
print(f"  TP={re_tp}, FP={re_fp}, FN={re_fn}")
print(f"  Precision : {re_precision:.4f}")
print(f"  Recall    : {re_recall:.4f}")
print(f"  F1        : {re_f1:.4f}")
print(f"  Score_RE  : {score_re:.4f}")

# ============================================================
# 6. 最终综合得分
# ============================================================
total_score = 0.4 * score_ner + 0.6 * score_re

print("\n" + "="*60)
print("最终综合得分")
print("="*60)
print(f"  Total = 0.4 × {score_ner:.4f} + 0.6 × {score_re:.4f} = {total_score:.4f}")
print(f"  官方 Baseline Track-A: 0.351, Track-B: 0.340")

# ============================================================
# 7. 各实体类别细分得分
# ============================================================
print("\n" + "="*60)
print("NER 各类别细分得分")
print("="*60)
all_ner_labels = sorted(set(
    list(ner_tp_by_label.keys()) +
    list(ner_fp_by_label.keys()) +
    list(ner_fn_by_label.keys())
))
print(f"{'标签':<8} {'TP':>6} {'FP':>6} {'FN':>6} {'Prec':>8} {'Rec':>8} {'F1':>8}")
print("-"*55)
for lbl in all_ner_labels:
    tp = ner_tp_by_label.get(lbl, 0)
    fp = ner_fp_by_label.get(lbl, 0)
    fn = ner_fn_by_label.get(lbl, 0)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0
    f = 2*p*r/(p+r) if (p+r) > 0 else 0
    print(f"{lbl:<8} {tp:>6} {fp:>6} {fn:>6} {p:>8.3f} {r:>8.3f} {f:>8.3f}")

# ============================================================
# 8. 各关系类别细分得分
# ============================================================
print("\n" + "="*60)
print("RE 各类别细分得分")
print("="*60)
all_re_labels = sorted(set(
    list(re_tp_by_label.keys()) +
    list(re_fp_by_label.keys()) +
    list(re_fn_by_label.keys())
))
print(f"{'标签':<8} {'TP':>6} {'FP':>6} {'FN':>6} {'Prec':>8} {'Rec':>8} {'F1':>8}")
print("-"*55)
for lbl in all_re_labels:
    tp = re_tp_by_label.get(lbl, 0)
    fp = re_fp_by_label.get(lbl, 0)
    fn = re_fn_by_label.get(lbl, 0)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0
    f = 2*p*r/(p+r) if (p+r) > 0 else 0
    print(f"{lbl:<8} {tp:>6} {fp:>6} {fn:>6} {p:>8.3f} {r:>8.3f} {f:>8.3f}")

# ============================================================
# 9. 保存结果到 JSON
# ============================================================
result = {
    "matched_pairs": len(matched_pairs),
    "unmatched_pred": len(unmatched_pred),
    "NER": {
        "TP": ner_tp, "FP": ner_fp, "FN": ner_fn,
        "Precision": round(ner_precision, 4),
        "Recall": round(ner_recall, 4),
        "F1": round(ner_f1, 4),
        "Score_NER": round(score_ner, 4),
        "by_label": {
            lbl: {
                "TP": ner_tp_by_label.get(lbl, 0),
                "FP": ner_fp_by_label.get(lbl, 0),
                "FN": ner_fn_by_label.get(lbl, 0),
            }
            for lbl in all_ner_labels
        }
    },
    "RE": {
        "TP": re_tp, "FP": re_fp, "FN": re_fn,
        "Precision": round(re_precision, 4),
        "Recall": round(re_recall, 4),
        "F1": round(re_f1, 4),
        "Score_RE": round(score_re, 4),
        "by_label": {
            lbl: {
                "TP": re_tp_by_label.get(lbl, 0),
                "FP": re_fp_by_label.get(lbl, 0),
                "FN": re_fn_by_label.get(lbl, 0),
            }
            for lbl in all_re_labels
        }
    },
    "Total_Score": round(total_score, 4),
    "Baseline_Track_A": 0.351,
    "Baseline_Track_B": 0.340,
}

with open('/home/ubuntu/score_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n结果已保存到 /home/ubuntu/score_result.json")
