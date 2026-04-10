#!/usr/bin/env python3
"""
四模型集成投票 v4
=================
参与模型：
  - v7_cicl_v2   (GPT-4.1-mini, RAG + c-ICL)          关系2.85/条
  - v9_clean     (GPT-4.1-mini, RAG + c-ICL + 修复)    关系3.35/条
  - v10_gemini   (Gemini-2.5-flash, RAG + c-ICL)       关系3.51/条
  - v11_nano     (GPT-4.1-nano, RAG)                   关系2.64/条

策略A: MIN_VOTES=2（四模型中至少2个同意）→ 召回率更高
策略B: MIN_VOTES=3（四模型中至少3个同意）→ 精确率更高

同时生成两个版本供对比提交
"""
import json
import os
from collections import defaultdict

FILES = [
    '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json',
    '/home/ubuntu/bisai/数据/A榜/submit_v9_clean.json',
    '/home/ubuntu/bisai/数据/A榜/submit_v10_gemini.json',
    '/home/ubuntu/bisai/数据/A榜/submit_v11_nano.json',
]
OUTPUT_A = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v4a.json'  # MIN_VOTES=2
OUTPUT_B = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v4b.json'  # MIN_VOTES=3

all_preds = []
for fp in FILES:
    with open(fp, encoding='utf-8') as f:
        data = json.load(f)
    all_preds.append(data)
    print(f"✓ 加载 {len(data)} 条：{os.path.basename(fp)}")

N = len(all_preds[0])
assert all(len(p) == N for p in all_preds), "各文件条数不一致！"

def normalize_entity_key(e):
    return (e['text'].lower().strip(), e['label'])

def normalize_relation_key(r):
    return (
        r['head'].lower().strip(), r['head_type'],
        r['label'],
        r['tail'].lower().strip(), r['tail_type']
    )

def run_ensemble(min_votes, output_path):
    print(f"\n开始四模型集成（MIN_VOTES={min_votes}）...")
    results = []
    ent_total_after = 0
    rel_total_after = 0

    for i in range(N):
        text = all_preds[0][i]['text']

        # 实体集成
        ent_votes = defaultdict(list)
        for model_idx, preds in enumerate(all_preds):
            item = preds[i]
            for e in item.get('entities', []):
                key = normalize_entity_key(e)
                ent_votes[key].append((model_idx, e))

        merged_entities = []
        entity_map = {}
        for key, votes in ent_votes.items():
            if len(votes) >= min_votes:
                # 优先取 v9_clean (index=1) 的偏移量
                votes_sorted = sorted(votes, key=lambda x: (x[0] != 1, x[0]))
                _, best_e = votes_sorted[0]
                merged_entities.append(best_e)
                et = best_e['text'].lower().strip()
                if et not in entity_map:
                    entity_map[et] = best_e

        # 关系集成
        rel_votes = defaultdict(list)
        for model_idx, preds in enumerate(all_preds):
            item = preds[i]
            for r in item.get('relations', []):
                key = normalize_relation_key(r)
                rel_votes[key].append((model_idx, r))

        merged_relations = []
        for key, votes in rel_votes.items():
            if len(votes) >= min_votes:
                votes_sorted = sorted(votes, key=lambda x: (x[0] != 1, x[0]))
                _, best_rel = votes_sorted[0]
                head_key = best_rel['head'].lower().strip()
                tail_key = best_rel['tail'].lower().strip()
                if head_key in entity_map and tail_key in entity_map:
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

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    no_rel = sum(1 for r in results if not r['relations'])
    print(f"\n===== 集成完成（MIN_VOTES={min_votes}）=====")
    print(f"输出: {output_path}")
    print(f"实体均值: {ent_total_after/N:.2f}/条（期望 5.92）")
    print(f"关系均值: {rel_total_after/N:.2f}/条（期望 2.80）")
    print(f"无关系比例: {no_rel/N*100:.1f}%（期望 32.7%）")
    return results

# 生成两个版本
run_ensemble(min_votes=2, output_path=OUTPUT_A)
run_ensemble(min_votes=3, output_path=OUTPUT_B)

print("\n两个版本均已生成，请分别打包提交对比！")
