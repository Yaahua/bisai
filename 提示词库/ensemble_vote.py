#!/usr/bin/env python3
"""
MGBIE Track-A 多模型集成投票脚本 (Ensemble Majority Voting)
============================================================
学术依据：
  Lu et al. (2025). CROSSAGENTIE: Cross-Type and Cross-Task Multi-Agent LLM
  Collaboration for Zero-Shot Information Extraction. ACL 2025 Findings.
  https://aclanthology.org/2025.findings-acl.718/

功能说明：
  1. 接收多个模型的预测结果（如 v6_rag.json, v7_cicl.json, v8_xxx.json）
  2. 对每条文本，统计各实体和关系三元组在多个预测中出现的次数
  3. 只保留出现次数 >= MIN_VOTES 的实体/关系（多数投票）
  4. 输出最终集成结果 submit_ensemble.json

使用方法：
  python ensemble_vote.py

投票策略说明：
  - 实体投票：以 (text, label) 为 key，出现次数 >= MIN_VOTES 则保留
  - 关系投票：以 (head_text, head_type, tail_text, tail_type, label) 为 key
  - 偏移量：取第一个投票通过的模型的偏移量（保证精确性）
  - MIN_VOTES=2 时（3个模型中2个同意）：精确率最大化，适合冲高分
  - MIN_VOTES=1 时（任意模型预测）：召回率最大化，适合保底

注意：
  运行前请先分别运行 predict_track_a_v6_rag.py 和 predict_track_a_v7_cicl.py
  生成对应的预测文件。
"""
import json
import os
from collections import Counter, defaultdict

# ===== 配置 =====
# 参与集成的预测文件列表（至少 2 个，推荐 3 个）
PREDICTION_FILES = [
    '/home/ubuntu/bisai/数据/A榜/submit_v6_rag.json',     # 第一阶段：RAG 动态提示词
    '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl.json',    # 第二阶段：RAG + c-ICL
    # 如果有第三个模型（如 Claude 或 Qwen），在此添加路径：
    # '/home/ubuntu/bisai/数据/A榜/submit_v8_claude.json',
]

# 最小投票数（出现次数 >= MIN_VOTES 才保留）
# 建议：2个文件时用1（OR合并），3个文件时用2（多数投票）
MIN_VOTES = 2  # 当只有2个文件时，建议设为1；3个文件时设为2

OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_ensemble.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


def load_predictions(file_paths: list) -> list:
    """加载所有预测文件，返回列表 [pred_list_1, pred_list_2, ...]"""
    all_preds = []
    for fp in file_paths:
        if not os.path.exists(fp):
            print(f"⚠ 文件不存在，跳过：{fp}")
            continue
        with open(fp, encoding='utf-8') as f:
            data = json.load(f)
        all_preds.append(data)
        print(f"✓ 加载 {len(data)} 条：{os.path.basename(fp)}")
    return all_preds


def ensemble_one(text: str, all_item_preds: list, min_votes: int) -> dict:
    """
    对单条文本的多个预测结果进行集成投票。
    
    all_item_preds: 各模型对该条文本的预测 [{"entities": [...], "relations": [...]}, ...]
    """
    # ===== 实体投票 =====
    entity_votes = Counter()    # (text, label) -> count
    entity_data  = {}           # (text, label) -> 第一个出现时的完整数据（含偏移量）

    for pred in all_item_preds:
        for e in pred.get("entities", []):
            key = (e["text"], e["label"])
            entity_votes[key] += 1
            if key not in entity_data:
                entity_data[key] = e

    # 保留投票数 >= min_votes 的实体
    kept_entities = []
    kept_entity_keys = set()
    for key, count in entity_votes.items():
        if count >= min_votes:
            kept_entities.append(entity_data[key])
            kept_entity_keys.add(key)

    # 按 start 位置排序
    kept_entities.sort(key=lambda e: e.get("start", 0))

    # ===== 关系投票 =====
    relation_votes = Counter()  # (head, head_type, tail, tail_type, label) -> count
    relation_data  = {}         # key -> 第一个出现时的完整数据（含偏移量）

    for pred in all_item_preds:
        for r in pred.get("relations", []):
            key = (
                r["head"], r["head_type"],
                r["tail"], r["tail_type"],
                r["label"]
            )
            relation_votes[key] += 1
            if key not in relation_data:
                relation_data[key] = r

    # 保留投票数 >= min_votes 的关系
    # 同时要求 head 和 tail 实体都在 kept_entity_keys 中
    kept_relations = []
    for key, count in relation_votes.items():
        if count >= min_votes:
            head_text, head_type, tail_text, tail_type, label = key
            # 验证实体是否通过了实体投票
            if (head_text, head_type) in kept_entity_keys and \
               (tail_text, tail_type) in kept_entity_keys:
                kept_relations.append(relation_data[key])

    return {
        "text": text,
        "entities": kept_entities,
        "relations": kept_relations
    }


def main():
    print(f"===== MGBIE Track-A 多模型集成投票 =====")
    print(f"最小投票数 (MIN_VOTES): {MIN_VOTES}")
    print(f"参与集成的文件数: {len(PREDICTION_FILES)}")
    print()

    # 加载所有预测
    all_preds = load_predictions(PREDICTION_FILES)
    if len(all_preds) < 2:
        print("❌ 至少需要 2 个预测文件才能进行集成！")
        return

    n_files = len(all_preds)
    n_samples = len(all_preds[0])

    # 验证所有文件长度一致
    for i, preds in enumerate(all_preds):
        if len(preds) != n_samples:
            print(f"⚠ 文件 {i} 长度 {len(preds)} 与第一个文件 {n_samples} 不一致！")

    print(f"\n开始集成 {n_samples} 条预测结果...")

    results = []
    stats = {
        'total_ent_before': 0,
        'total_ent_after':  0,
        'total_rel_before': 0,
        'total_rel_after':  0,
    }

    for i in range(n_samples):
        text = all_preds[0][i]["text"]
        item_preds = [all_preds[j][i] for j in range(n_files)]

        # 统计集成前的数量
        for pred in item_preds:
            stats['total_ent_before'] += len(pred.get("entities", []))
            stats['total_rel_before'] += len(pred.get("relations", []))

        merged = ensemble_one(text, item_preds, MIN_VOTES)
        results.append(merged)

        stats['total_ent_after'] += len(merged["entities"])
        stats['total_rel_after'] += len(merged["relations"])

        if (i + 1) % 50 == 0:
            print(f"  进度: {i+1}/{n_samples}")

    # 保存结果
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 统计报告
    avg_before_ent = stats['total_ent_before'] / n_files / n_samples
    avg_after_ent  = stats['total_ent_after']  / n_samples
    avg_before_rel = stats['total_rel_before'] / n_files / n_samples
    avg_after_rel  = stats['total_rel_after']  / n_samples

    print(f"\n===== 集成完成 =====")
    print(f"输出文件: {OUTPUT_PATH}")
    print(f"\n实体统计（每条平均）:")
    print(f"  集成前（各模型均值）: {avg_before_ent:.2f}")
    print(f"  集成后:              {avg_after_ent:.2f}")
    print(f"  保留率:              {avg_after_ent/avg_before_ent*100:.1f}%")
    print(f"\n关系统计（每条平均）:")
    print(f"  集成前（各模型均值）: {avg_before_rel:.2f}")
    print(f"  集成后:              {avg_after_rel:.2f}")
    print(f"  保留率:              {avg_after_rel/avg_before_rel*100:.1f}%")
    print(f"\n期望值参考（基于训练集 1000 条 → 测试集 400 条）:")
    print(f"  期望实体数/条: ~5.92")
    print(f"  期望关系数/条: ~2.80")
    print(f"  期望无关系比例: ~32.7%")

    # 无关系比例统计
    no_rel_count = sum(1 for r in results if len(r["relations"]) == 0)
    print(f"\n  集成后无关系比例: {no_rel_count}/{n_samples} = {no_rel_count/n_samples*100:.1f}%")


if __name__ == '__main__':
    main()
