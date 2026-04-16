#!/usr/bin/env python3
"""
ensemble_v29.py — 三模型集成（v27 Gemini + v28 GPT + v7 c-ICL）
策略：MIN_VOTES=2（三选二多数投票），然后用 v17 白名单后处理补召回
"""
import json
import os
from collections import Counter

# ===== 配置 =====
PREDICTION_FILES = [
    '/home/ubuntu/bisai/数据/A榜/submit_v27_gemini_enhanced.json',  # Gemini 增强版
    '/home/ubuntu/bisai/数据/A榜/submit_v28_gpt_enhanced.json',     # GPT 增强版
    '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json',           # v7 c-ICL（最稳定）
]
MIN_VOTES  = 2
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v29_ensemble.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

def load_predictions(file_paths):
    all_preds = []
    for fp in file_paths:
        if not os.path.exists(fp):
            print(f"⚠ 文件不存在，跳过：{fp}")
            continue
        with open(fp, encoding='utf-8') as f:
            data = json.load(f)
        all_preds.append(data)
        total_rels = sum(len(x.get('relations',[])) for x in data)
        print(f"✓ 加载 {len(data)} 条（关系均值 {total_rels/len(data):.2f}）：{os.path.basename(fp)}")
    return all_preds

def ensemble_one(text, all_item_preds, min_votes):
    # 实体投票
    entity_votes = Counter()
    entity_data  = {}
    for pred in all_item_preds:
        for e in pred.get("entities", []):
            key = (e["text"], e["label"])
            entity_votes[key] += 1
            if key not in entity_data:
                entity_data[key] = e
    
    kept_entities = []
    kept_entity_keys = set()
    for key, count in entity_votes.items():
        if count >= min_votes:
            kept_entities.append(entity_data[key])
            kept_entity_keys.add(key)
    kept_entities.sort(key=lambda e: e.get("start", 0))
    
    # 关系投票
    relation_votes = Counter()
    relation_data  = {}
    for pred in all_item_preds:
        for r in pred.get("relations", []):
            key = (r["head"], r["head_type"], r["tail"], r["tail_type"], r["label"])
            relation_votes[key] += 1
            if key not in relation_data:
                relation_data[key] = r
    
    kept_relations = []
    for key, count in relation_votes.items():
        if count >= min_votes:
            head_text, head_type, tail_text, tail_type, label = key
            if (head_text, head_type) in kept_entity_keys and \
               (tail_text, tail_type) in kept_entity_keys:
                kept_relations.append(relation_data[key])
    
    return {"text": text, "entities": kept_entities, "relations": kept_relations}

def main():
    print(f"===== MGBIE Track-A 三模型集成投票 =====")
    print(f"最小投票数: {MIN_VOTES}")
    print()
    
    all_preds = load_predictions(PREDICTION_FILES)
    if len(all_preds) < 2:
        print("❌ 至少需要 2 个预测文件！")
        return
    
    n_files  = len(all_preds)
    n_samples = len(all_preds[0])
    
    # 验证长度
    for i, preds in enumerate(all_preds):
        if len(preds) != n_samples:
            print(f"⚠ 文件 {i} 长度 {len(preds)} 与第一个文件 {n_samples} 不一致！")
    
    print(f"\n开始集成 {n_samples} 条预测结果...")
    results = []
    
    from collections import Counter as C
    rel_type_counter = C()
    
    for i in range(n_samples):
        text = all_preds[0][i]["text"]
        item_preds = [all_preds[j][i] for j in range(n_files)]
        merged = ensemble_one(text, item_preds, MIN_VOTES)
        results.append(merged)
        for r in merged["relations"]:
            rel_type_counter[(r['head_type'], r['label'], r['tail_type'])] += 1
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    total_rels = sum(len(r["relations"]) for r in results)
    no_rel = sum(1 for r in results if not r["relations"])
    
    print(f"\n===== 集成完成 =====")
    print(f"输出文件: {OUTPUT_PATH}")
    print(f"关系均值: {total_rels/n_samples:.2f}")
    print(f"无关系比例: {no_rel}/{n_samples} = {no_rel/n_samples*100:.1f}%")
    print(f"\n关系类型分布（Top 15）:")
    for (ht,l,tt), cnt in sorted(rel_type_counter.items(), key=lambda x: -x[1])[:15]:
        print(f"  {ht}-{l}-{tt}: {cnt}")
    
    print(f"\n期望参考（训练集 1000→测试集 400）:")
    print(f"  期望关系均值: ~2.80")
    print(f"  期望无关系比例: ~32.7%")
    print(f"  ABS-AFF-TRT 期望: ~114")
    print(f"  CROP-CON-VAR 期望: ~89")

if __name__ == '__main__':
    main()
