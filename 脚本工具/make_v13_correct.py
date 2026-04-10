#!/usr/bin/env python3.11
"""
v13 正确策略：
- 以 ensemble_v3（0.4172）为基础，保持原有关系不变
- 用完整的 153 种训练集三元组类型过滤 v12 的新增关系
- 只补充 ensemble_v3 没有、但 v12 有且合法的关系
- 目标：在不损失精确率的前提下，提升召回率
"""
import json
from collections import Counter

E3_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'
V12_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v12_reverse_scir.json'
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
OUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v13_e3plus.json'

# 从训练集动态加载所有合法三元组
with open(TRAIN_PATH) as f:
    train = json.load(f)

VALID_TRIPLES = set()
for item in train:
    for rel in item.get('relations', []):
        h = rel.get('head_type','')
        l = rel.get('label','')
        t = rel.get('tail_type','')
        if h and l and t:
            VALID_TRIPLES.add(f"{h}-{l}-{t}")

print(f"从训练集加载合法三元组: {len(VALID_TRIPLES)} 种")

VALID_ENTITY_TYPES = set()
for item in train:
    for e in item.get('entities', []):
        lb = e.get('label','')
        if lb:
            VALID_ENTITY_TYPES.add(lb)
print(f"合法实体类型: {VALID_ENTITY_TYPES}")

def clean_type(t):
    if not t:
        return ""
    if t in VALID_ENTITY_TYPES:
        return t
    for vt in VALID_ENTITY_TYPES:
        if t.startswith(vt):
            return vt
    return ""

def rel_key(rel):
    return (rel.get("head","").strip(), rel.get("label",""), rel.get("tail","").strip())

# 加载数据
with open(E3_PATH) as f:
    e3_data = json.load(f)
with open(V12_PATH) as f:
    v12_data = json.load(f)

# v12 索引
v12_index = {item.get("id", item.get("text","")): item for item in v12_data}

added_from_v12 = 0
merged_data = []

for e3_item in e3_data:
    key  = e3_item.get("id", e3_item.get("text",""))
    text = e3_item.get("text","")

    # 保持 ensemble_v3 的所有关系不变
    existing_keys = {rel_key(r) for r in e3_item.get("relations",[])}
    new_rels = list(e3_item.get("relations",[]))

    # 从 v12 补充新增合法关系
    v12_item = v12_index.get(key)
    if v12_item:
        # v12 实体映射
        v12_emap = {}
        for e in v12_item.get("entities", []):
            et = e.get("entity", e.get("text","")).strip()
            el = e.get("type",   e.get("label",""))
            if et:
                v12_emap[et] = clean_type(el)

        for rel in v12_item.get("relations", []):
            rk = rel_key(rel)
            if rk in existing_keys:
                continue  # 已存在，跳过

            h = rel.get("head","").strip()
            t = rel.get("tail","").strip()
            l = rel.get("label","")
            h_type = clean_type(rel.get("head_type", v12_emap.get(h,"")))
            t_type = clean_type(rel.get("tail_type", v12_emap.get(t,"")))

            if not h_type or not t_type:
                continue
            triple_key = f"{h_type}-{l}-{t_type}"
            if triple_key not in VALID_TRIPLES:
                continue
            # 实体文本必须在原文中出现
            if h not in text or t not in text:
                continue

            new_rels.append({
                "head": h, "head_type": h_type,
                "tail": t, "tail_type": t_type,
                "label": l
            })
            existing_keys.add(rk)
            added_from_v12 += 1

    merged_data.append({
        "id":        e3_item.get("id",""),
        "text":      text,
        "entities":  e3_item.get("entities",[]),
        "relations": new_rels
    })

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

# 统计
total = len(merged_data)
total_rels = sum(len(r.get("relations",[])) for r in merged_data)
no_rel = sum(1 for r in merged_data if not r.get("relations"))

print(f"\n=== v13_e3plus ===")
print(f"  从 v12 新增合法关系: {added_from_v12} 条")
print(f"  关系均值: {total_rels/total:.2f}/条 (期望 2.80，ensemble_v3 为 2.16)")
print(f"  无关系比例: {no_rel/total*100:.1f}% (期望 32.7%，ensemble_v3 为 38.2%)")
print(f"  输出: {OUT_PATH}")

rel_types = Counter()
for r in merged_data:
    for rel in r.get("relations",[]):
        k = f"{rel.get('head_type','?')}-{rel.get('label','?')}-{rel.get('tail_type','?')}"
        rel_types[k] += 1
print("\n  Top 10 关系类型:")
for k,v in rel_types.most_common(10):
    print(f"    {k}: {v}")
