#!/usr/bin/env python3
"""
自动硬负样本生成脚本（基于 Self-Consistency）
==============================================
学术依据：
  Mo et al. (2024). c-ICL: Contrastive In-context Learning for Information Extraction.
  EMNLP 2024 Findings. Section 3.4: Hard Negative Construction via Self-Consistency

原理：
  1. 从训练集中随机抽取样本，用 LLM 预测 3 次（不同温度/随机种子）
  2. 计算预测结果与 Gold 标注的 F1 分数
  3. 筛选"接近正确但有错误"的样本（0.3 < F1 < 0.85）作为硬负样本
  4. 每个硬负样本包含：原文、错误预测、正确标注、错误类型说明

输出：hard_negatives.json（供 predict_track_a_v7_cicl_v2.py 使用）

注意：
  - 此脚本只需运行一次，生成的硬负样本可重复使用
  - 建议在 train.json 的前 200 条上运行（节省 API 费用）
  - 预计 API 调用次数：200 × 3 = 600 次（约 $0.3 费用）
"""
import json
import os
import re
import random
import time
from openai import OpenAI

# ===== 配置 =====
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
OUTPUT_PATH = '/home/ubuntu/bisai/提示词库/hard_negatives.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

MODEL = "gpt-4.1-mini"
SAMPLE_SIZE = 150       # 从训练集中抽取的样本数
N_PREDICTIONS = 3       # 每个样本预测次数（Self-Consistency）
F1_LOWER = 0.25         # 硬负样本 F1 下界（太差的不用）
F1_UPPER = 0.85         # 硬负样本 F1 上界（太好的不是负样本）
MAX_HARD_NEGATIVES = 8  # 最终保留的硬负样本数量（正负比例 2:1 原则）
TEMPERATURES = [0.3, 0.6, 0.9]  # 文献推荐的温度参数

client = OpenAI()

# ===== 简化版系统提示词（用于生成预测）=====
SIMPLE_SYSTEM = """You are an expert NER and RE annotator for crop breeding literature.
Entity types: CROP, VAR, GENE, QTL, MRK, TRT, ABS, BIS, BM, CHR, CROSS, GST
Relation types: AFF, LOI, HAS, CON, USE, OCI
Output valid JSON only: {"entities": [{"text": "...", "label": "..."}], "relations": [{"head": "...", "head_type": "...", "tail": "...", "tail_type": "...", "label": "..."}]}"""


def predict_with_temperature(text: str, temperature: float) -> dict:
    """用指定温度对文本进行预测"""
    for attempt in range(2):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SIMPLE_SYSTEM},
                    {"role": "user",   "content": f"Input: {text}\nOutput:"}
                ],
                temperature=temperature,
                max_tokens=1024
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'^```\s*',     '', raw)
            raw = re.sub(r'\s*```$',     '', raw)
            return json.loads(raw)
        except Exception:
            time.sleep(1)
    return {"entities": [], "relations": []}


def compute_entity_f1(pred_entities: list, gold_entities: list) -> float:
    """计算实体 F1（基于 text+label 精确匹配）"""
    pred_set = {(e.get("text", ""), e.get("label", "")) for e in pred_entities}
    gold_set = {(e.get("text", ""), e.get("label", "")) for e in gold_entities}
    if not pred_set and not gold_set:
        return 1.0
    if not pred_set or not gold_set:
        return 0.0
    tp = len(pred_set & gold_set)
    p  = tp / len(pred_set)
    r  = tp / len(gold_set)
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


def compute_relation_f1(pred_rels: list, gold_rels: list) -> float:
    """计算关系 F1（基于 head+head_type+tail+tail_type+label 精确匹配）"""
    pred_set = {(r.get("head",""), r.get("head_type",""), r.get("tail",""), r.get("tail_type",""), r.get("label","")) for r in pred_rels}
    gold_set = {(r.get("head",""), r.get("head_type",""), r.get("tail",""), r.get("tail_type",""), r.get("label","")) for r in gold_rels}
    if not pred_set and not gold_set:
        return 1.0
    if not pred_set or not gold_set:
        return 0.0
    tp = len(pred_set & gold_set)
    p  = tp / len(pred_set)
    r  = tp / len(gold_set)
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0


def compute_combined_f1(pred: dict, gold_item: dict) -> float:
    """计算综合 F1（NER + RE 加权）"""
    ner_f1 = compute_entity_f1(pred.get("entities", []), gold_item.get("entities", []))
    re_f1  = compute_relation_f1(pred.get("relations", []), gold_item.get("relations", []))
    return 0.4 * ner_f1 + 0.6 * re_f1


def classify_errors(pred: dict, gold_item: dict) -> str:
    """分析错误类型，生成人类可读的错误说明"""
    errors = []
    pred_ents = {(e.get("text",""), e.get("label","")) for e in pred.get("entities", [])}
    gold_ents = {(e.get("text",""), e.get("label","")) for e in gold_item.get("entities", [])}
    fp_ents = pred_ents - gold_ents
    fn_ents = gold_ents - pred_ents

    pred_rels = {(r.get("head",""), r.get("head_type",""), r.get("tail",""), r.get("tail_type",""), r.get("label","")) for r in pred.get("relations", [])}
    gold_rels = {(r.get("head",""), r.get("head_type",""), r.get("tail",""), r.get("tail_type",""), r.get("label","")) for r in gold_item.get("relations", [])}
    fp_rels = pred_rels - gold_rels
    fn_rels = gold_rels - pred_rels

    if fp_ents:
        errors.append(f"Over-predicted entities (FP): {list(fp_ents)[:3]}")
    if fn_ents:
        errors.append(f"Missed entities (FN): {list(fn_ents)[:3]}")
    if fp_rels:
        errors.append(f"Over-predicted relations (FP): {[f'{r[0]}-{r[4]}-{r[2]}' for r in list(fp_rels)[:3]]}")
    if fn_rels:
        errors.append(f"Missed relations (FN): {[f'{r[0]}-{r[4]}-{r[2]}' for r in list(fn_rels)[:3]]}")

    return "; ".join(errors) if errors else "Unknown error"


def main():
    with open(TRAIN_PATH, encoding='utf-8') as f:
        train_data = json.load(f)

    # 随机抽样（优先选择有关系的样本，更容易产生有意义的错误）
    has_rel = [item for item in train_data if item.get("relations")]
    no_rel  = [item for item in train_data if not item.get("relations")]
    sample_pool = has_rel[:int(SAMPLE_SIZE * 0.8)] + no_rel[:int(SAMPLE_SIZE * 0.2)]
    random.seed(42)
    samples = random.sample(sample_pool, min(SAMPLE_SIZE, len(sample_pool)))

    print(f"开始生成硬负样本：{len(samples)} 个样本 × {N_PREDICTIONS} 次预测")
    print(f"F1 筛选范围：{F1_LOWER} ~ {F1_UPPER}")
    print(f"目标硬负样本数：{MAX_HARD_NEGATIVES}")
    print()

    hard_negatives = []
    candidates = []

    for i, item in enumerate(samples):
        text = item["text"]
        gold_ents = [{"text": e["text"], "label": e["label"]} for e in item.get("entities", [])]
        gold_rels = [{"head": r["head"], "head_type": r["head_type"],
                      "tail": r["tail"], "tail_type": r["tail_type"],
                      "label": r["label"]} for r in item.get("relations", [])]
        gold = {"entities": gold_ents, "relations": gold_rels}

        # Self-Consistency：用不同温度预测 3 次
        preds = []
        for temp in TEMPERATURES:
            pred = predict_with_temperature(text, temp)
            f1 = compute_combined_f1(pred, gold)
            preds.append((pred, f1, temp))

        # 取 F1 最低的预测（最典型的错误）
        worst_pred, worst_f1, worst_temp = min(preds, key=lambda x: x[1])

        if F1_LOWER <= worst_f1 <= F1_UPPER:
            error_desc = classify_errors(worst_pred, gold)
            candidates.append({
                "text": text,
                "bad_prediction": worst_pred,
                "gold": gold,
                "f1": worst_f1,
                "error_description": error_desc
            })
            print(f"[{i+1}/{len(samples)}] ✓ 候选硬负样本 (F1={worst_f1:.3f}): {text[:60]}...")
            print(f"  错误：{error_desc[:100]}")
        else:
            print(f"[{i+1}/{len(samples)}] - 跳过 (F1={worst_f1:.3f}): {text[:60]}...")

        # 每 20 条保存一次中间结果
        if (i + 1) % 20 == 0:
            with open(OUTPUT_PATH + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(candidates, f, ensure_ascii=False, indent=2)

    # 按 F1 排序，选取最典型的错误（F1 在中间范围的，既不太差也不太好）
    candidates.sort(key=lambda x: abs(x["f1"] - 0.5))  # 选 F1 最接近 0.5 的（最典型的"接近正确但有错"）
    hard_negatives = candidates[:MAX_HARD_NEGATIVES]

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(hard_negatives, f, ensure_ascii=False, indent=2)

    print(f"\n===== 完成 =====")
    print(f"候选硬负样本总数：{len(candidates)}")
    print(f"最终保留：{len(hard_negatives)} 个")
    print(f"输出：{OUTPUT_PATH}")
    print(f"\n下一步：运行 predict_track_a_v7_cicl_v2.py 使用这些硬负样本")


if __name__ == '__main__':
    main()
