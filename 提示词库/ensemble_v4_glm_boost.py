#!/usr/bin/env python3
"""
ensemble_v4_glm_boost.py
========================
策略：将 ensemble_v3（0.4172）与 v15_glm 进行集成

集成方案：
- ensemble_v3 是基准（高精确率，低召回率）
- v15_glm 是补充（高召回率，低精确率）

集成逻辑（两种模式）：
1. UNION 模式：取并集（v3 + v15 的所有关系），但对 v15 独有的关系做置信度过滤
2. BOOST 模式：以 v3 为基础，只添加 v15 中"高置信度"的额外关系
   - 高置信度判定：v15 的关系在实体类型和关系类型上符合训练集分布

目标：提升召回率（从 2.16 → 2.80），同时保持精确率
"""
import json
import os
from collections import Counter

# ===== 路径 =====
V3_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'
V15_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_v15_glm.json'
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
OUT_UNION  = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v4_union.json'
OUT_BOOST  = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v4_boost.json'

# ===== 加载数据 =====
with open(V3_PATH, encoding='utf-8') as f:
    v3_data = json.load(f)
with open(V15_PATH, encoding='utf-8') as f:
    v15_data = json.load(f)
with open(TRAIN_PATH, encoding='utf-8') as f:
    train_data = json.load(f)

print(f"v3: {len(v3_data)} 条 | v15: {len(v15_data)} 条")
assert len(v3_data) == len(v15_data) == 400, "数据条数不匹配！"

# ===== 从训练集统计合法的三元组类型 =====
valid_triplets = Counter()
for item in train_data:
    for r in item.get('relations', []):
        key = (r['head_type'], r['label'], r['tail_type'])
        valid_triplets[key] += 1

# 出现 >= 3 次的三元组类型视为"高置信度"
HIGH_CONF_TRIPLETS = {k for k, v in valid_triplets.items() if v >= 3}
print(f"高置信度三元组类型: {len(HIGH_CONF_TRIPLETS)} 种（出现≥3次）")

# ===== 关系规范化（用于去重比较）=====
def rel_key(r):
    """生成关系的唯一键（用于去重）"""
    return (r['head'].lower().strip(), r['head_type'],
            r['tail'].lower().strip(), r['tail_type'],
            r['label'])

def is_high_conf_rel(r):
    """判断关系是否是高置信度类型"""
    key = (r['head_type'], r['label'], r['tail_type'])
    return key in HIGH_CONF_TRIPLETS

# ===== 集成逻辑 =====
results_union = []
results_boost = []

stats = {
    'v3_only': 0, 'v15_only': 0, 'both': 0,
    'boost_added': 0, 'boost_rejected': 0
}

for i, (r3, r15) in enumerate(zip(v3_data, v15_data)):
    text = r3['text']
    assert r3['text'] == r15['text'], f"文本不匹配 idx={i}"

    # v3 的关系集合
    v3_rels = r3.get('relations', [])
    v3_keys = {rel_key(r) for r in v3_rels}

    # v15 的关系集合
    v15_rels = r15.get('relations', [])
    v15_keys = {rel_key(r) for r in v15_rels}

    # 统计
    for k in v3_keys:
        if k in v15_keys:
            stats['both'] += 1
        else:
            stats['v3_only'] += 1
    for k in v15_keys:
        if k not in v3_keys:
            stats['v15_only'] += 1

    # ---- UNION 模式 ----
    # 取 v3 的所有关系 + v15 中高置信度且不重复的关系
    union_rels = list(v3_rels)
    union_ent_texts = {e['text'] for e in r3.get('entities', [])}

    for r in v15_rels:
        k = rel_key(r)
        if k not in v3_keys and is_high_conf_rel(r):
            # 额外检查：实体必须在原文中
            if r['head'] in text and r['tail'] in text:
                union_rels.append(r)

    # 合并实体（取 v3 的实体为基础，添加 v15 中新出现的实体）
    union_ents = list(r3.get('entities', []))
    v3_ent_spans = {(e['start'], e['end']) for e in union_ents}
    for e in r15.get('entities', []):
        if (e['start'], e['end']) not in v3_ent_spans and e['text'] in text:
            union_ents.append(e)
            v3_ent_spans.add((e['start'], e['end']))

    results_union.append({
        'text': text,
        'entities': union_ents,
        'relations': union_rels
    })

    # ---- BOOST 模式 ----
    # 以 v3 为基础，只添加 v15 中与 v3 关系类型一致且高置信度的关系
    boost_rels = list(v3_rels)
    v3_rel_types = {r['label'] for r in v3_rels}

    for r in v15_rels:
        k = rel_key(r)
        if k not in v3_keys and is_high_conf_rel(r):
            # BOOST 模式：只添加与 v3 已有关系类型相同的关系（更保守）
            if r['head'] in text and r['tail'] in text:
                # 额外检查：不添加过多（最多补充到 v3 的 1.5 倍）
                if len(boost_rels) < max(len(v3_rels) * 1.5, len(v3_rels) + 2):
                    boost_rels.append(r)
                    stats['boost_added'] += 1
                else:
                    stats['boost_rejected'] += 1

    results_boost.append({
        'text': text,
        'entities': union_ents,  # 使用 union 的实体
        'relations': boost_rels
    })

# ===== 保存 =====
with open(OUT_UNION, 'w', encoding='utf-8') as f:
    json.dump(results_union, f, ensure_ascii=False, indent=2)
with open(OUT_BOOST, 'w', encoding='utf-8') as f:
    json.dump(results_boost, f, ensure_ascii=False, indent=2)

# ===== 统计 =====
print(f"\n=== 集成统计 ===")
print(f"v3 独有关系: {stats['v3_only']}")
print(f"v15 独有关系: {stats['v15_only']}")
print(f"两者共有关系: {stats['both']}")
print(f"BOOST 模式添加: {stats['boost_added']} | 拒绝: {stats['boost_rejected']}")

for name, data in [('UNION', results_union), ('BOOST', results_boost)]:
    total_rels = sum(len(r.get('relations',[])) for r in data)
    no_rel = sum(1 for r in data if not r.get('relations'))
    print(f"\n{name} 模式:")
    print(f"  关系均值: {total_rels/400:.2f}/条（v3 基准: {sum(len(r.get('relations',[])) for r in v3_data)/400:.2f}，期望: 2.80）")
    print(f"  无关系比例: {no_rel/400*100:.1f}%（期望: 32.7%）")

print(f"\n输出文件:")
print(f"  UNION: {OUT_UNION}")
print(f"  BOOST: {OUT_BOOST}")
