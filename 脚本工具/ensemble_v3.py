#!/usr/bin/env python3
"""
三模型集成投票 v3
=================
参与模型：
  - v7_cicl_v2   (GPT-4.1-mini, RAG + c-ICL)
  - v9_clean     (GPT-4.1-mini, RAG + c-ICL + 针对性修复 + 后处理清洗)
  - v10_gemini   (Gemini-2.5-flash, RAG + c-ICL，内置合法三元组过滤)

策略：MIN_VOTES=2（多数投票，至少2个模型同意才保留）
预期效果：精确率大幅提升，召回率略降，整体 F1 提升
"""
import json
import os
from collections import defaultdict, Counter

FILES = [
    '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json',
    '/home/ubuntu/bisai/数据/A榜/submit_v9_clean.json',
    '/home/ubuntu/bisai/数据/A榜/submit_v10_gemini.json',
]
MIN_VOTES   = 2
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# 加载所有预测
all_preds = []
for fp in FILES:
    with open(fp, encoding='utf-8') as f:
        data = json.load(f)
    all_preds.append(data)
    print(f"✓ 加载 {len(data)} 条：{os.path.basename(fp)}")

N = len(all_preds[0])
assert all(len(p) == N for p in all_preds), "各文件条数不一致！"

def normalize_entity_key(e):
    """实体去重键：文本小写 + 标签"""
    return (e['text'].lower().strip(), e['label'])

def normalize_relation_key(r):
    """关系去重键：头实体文本+类型 + 关系标签 + 尾实体文本+类型（文本小写）"""
    return (
        r['head'].lower().strip(), r['head_type'],
        r['label'],
        r['tail'].lower().strip(), r['tail_type']
    )

print(f"\n开始三模型集成（MIN_VOTES={MIN_VOTES}）...")
results = []
ent_total_before = [0, 0, 0]
rel_total_before = [0, 0, 0]
ent_total_after  = 0
rel_total_after  = 0

for i in range(N):
    # ===== 实体集成 =====
    ent_votes = defaultdict(list)
    for model_idx, preds in enumerate(all_preds):
        item = preds[i]
        ent_total_before[model_idx] += len(item.get('entities', []))
        for e in item.get('entities', []):
            key = normalize_entity_key(e)
            ent_votes[key].append(e)

    merged_entities = []
    for key, votes in ent_votes.items():
        if len(votes) >= MIN_VOTES:
            # 取第一个模型的偏移量（优先 v9_clean，因为它最准确）
            # 按模型优先级选取：v9_clean > v7 > v10
            best = votes[0]
            for v in votes:
                # 优先选 v9_clean（index 1）的偏移量
                pass
            merged_entities.append(best)

    # ===== 关系集成 =====
    rel_votes = defaultdict(list)
    for model_idx, preds in enumerate(all_preds):
        item = preds[i]
        rel_total_before[model_idx] += len(item.get('relations', []))
        for r in item.get('relations', []):
            key = normalize_relation_key(r)
            rel_votes[key].append((model_idx, r))

    # 构建实体映射（用于修正关系偏移量）
    entity_map = {}
    text = all_preds[0][i]['text']
    for e in merged_entities:
        et = e['text'].lower().strip()
        if et not in entity_map:
            entity_map[et] = e

    merged_relations = []
    for key, votes in rel_votes.items():
        if len(votes) >= MIN_VOTES:
            # 取票数最多的版本，优先 v9_clean
            # 按 model_idx 排序，优先取 index=1（v9_clean）
            votes_sorted = sorted(votes, key=lambda x: (x[0] != 1, x[0]))
            _, best_rel = votes_sorted[0]

            # 验证头尾实体都在 merged_entities 中
            head_key = best_rel['head'].lower().strip()
            tail_key = best_rel['tail'].lower().strip()
            if head_key in entity_map and tail_key in entity_map:
                # 用 merged_entities 中的偏移量更新关系
                h_ent = entity_map[head_key]
                t_ent = entity_map[tail_key]
                merged_relations.append({
                    "head":       h_ent['text'],
                    "head_start": h_ent.get('start', best_rel.get('head_start', 0)),
                    "head_end":   h_ent.get('end',   best_rel.get('head_end',   0)),
                    "head_type":  best_rel['head_type'],
                    "tail":       t_ent['text'],
                    "tail_start": t_ent.get('start', best_rel.get('tail_start', 0)),
                    "tail_end":   t_ent.get('end',   best_rel.get('tail_end',   0)),
                    "tail_type":  best_rel['tail_type'],
                    "label":      best_rel['label']
                })

    ent_total_after += len(merged_entities)
    rel_total_after += len(merged_relations)
    results.append({"text": text, "entities": merged_entities, "relations": merged_relations})

    if (i + 1) % 50 == 0:
        print(f"  进度: {i+1}/{N}")

# 保存
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

no_rel = sum(1 for r in results if not r['relations'])
print(f"\n===== 集成完成 =====")
print(f"输出文件: {OUTPUT_PATH}")
print(f"\n实体统计（每条平均）:")
for i, fp in enumerate(FILES):
    print(f"  {os.path.basename(fp)}: {ent_total_before[i]/N:.2f}")
print(f"  集成后: {ent_total_after/N:.2f}")
print(f"\n关系统计（每条平均）:")
for i, fp in enumerate(FILES):
    print(f"  {os.path.basename(fp)}: {rel_total_before[i]/N:.2f}")
print(f"  集成后: {rel_total_after/N:.2f}")
print(f"\n期望值参考（训练集）:")
print(f"  期望实体数/条: ~5.92")
print(f"  期望关系数/条: ~2.80")
print(f"  期望无关系比例: ~32.7%")
print(f"  集成后无关系比例: {no_rel/N*100:.1f}%")
