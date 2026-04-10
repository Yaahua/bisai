#!/usr/bin/env python3.11
"""
v9_clean + v12 合并策略
=======================
核心思路：
- v9_clean（0.3893）：高质量基础，关系均值 3.35/条，但有过标
- v12（ReverseNER+SCIR）：低召回，但新增了 v9_clean 没有的合法关系

策略：
1. 以 v9_clean 为基础
2. 用 v12 中 v9_clean 没有的合法关系来补充（仅补充合法三元组）
3. 同时对 v9_clean 做最终的非法关系清洗

目标：在 v9_clean 的基础上，通过 v12 的 ReverseNER 示例恢复部分漏标关系
"""
import json
from collections import Counter, defaultdict

V9_PATH     = '/home/ubuntu/bisai/数据/A榜/submit_v9_clean.json'
V12_PATH    = '/home/ubuntu/bisai/数据/A榜/submit_v12_reverse_scir.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v9v12_merged.json'

VALID_TRIPLES = {
    "CROP-CON-VAR", "VAR-HAS-TRT", "VAR-USE-BM", "VAR-OCI-GENE",
    "GENE-AFF-TRT", "GENE-LOI-TRT", "GENE-LOI-CHR",
    "QTL-LOI-TRT", "QTL-LOI-CHR", "MRK-LOI-CHR",
    "TRT-HAS-BM", "TRT-AFF-BM",
    "CROP-CON-GENE", "CROP-CON-QTL", "CROP-CON-MRK",
    "VAR-HAS-GENE", "VAR-HAS-QTL",
}

VALID_ENTITY_TYPES = {"CROP", "VAR", "GENE", "QTL", "MRK", "TRT", "BM", "LOI", "CHR", "ABS"}

def clean_type(t):
    if not t:
        return t
    if t in VALID_ENTITY_TYPES:
        return t
    for vt in VALID_ENTITY_TYPES:
        if t.startswith(vt):
            return vt
    return t

def rel_key(rel):
    """生成关系的唯一标识"""
    return (rel.get("head",""), rel.get("label",""), rel.get("tail",""))

def is_valid_rel(rel, entity_map):
    h = rel.get("head", "")
    t = rel.get("tail", "")
    l = rel.get("label", "")
    h_type = clean_type(rel.get("head_type", entity_map.get(h, "")))
    t_type = clean_type(rel.get("tail_type", entity_map.get(t, "")))
    triple_key = f"{h_type}-{l}-{t_type}"
    return triple_key in VALID_TRIPLES, h_type, t_type

# 加载数据
with open(V9_PATH) as f:
    v9_data = json.load(f)
with open(V12_PATH) as f:
    v12_data = json.load(f)

# 建立 v12 的索引（按 text 或 id）
v12_index = {}
for item in v12_data:
    key = item.get("id", item.get("text", ""))
    v12_index[key] = item

merged_data = []
added_from_v12 = 0
removed_illegal = 0

for v9_item in v9_data:
    key = v9_item.get("id", v9_item.get("text", ""))
    text = v9_item.get("text", "")

    # 构建实体映射
    entity_map = {e.get("text",""): e.get("label","") for e in v9_item.get("entities",[])}

    # 1. 清洗 v9_clean 的关系（删除非法三元组）
    clean_rels = []
    for rel in v9_item.get("relations", []):
        valid, h_type, t_type = is_valid_rel(rel, entity_map)
        if valid:
            rel["head_type"] = h_type
            rel["tail_type"] = t_type
            clean_rels.append(rel)
        else:
            removed_illegal += 1

    # 2. 从 v12 中补充 v9_clean 没有的合法关系
    existing_keys = {rel_key(r) for r in clean_rels}
    v12_item = v12_index.get(key)

    if v12_item:
        # 合并实体映射（v12 可能有 v9 没有的实体）
        v12_entity_map = {e.get("entity", e.get("text","")): e.get("type", e.get("label",""))
                         for e in v12_item.get("entities", [])}
        combined_map = {**entity_map, **v12_entity_map}

        for rel in v12_item.get("relations", []):
            rk = rel_key(rel)
            if rk in existing_keys:
                continue  # 已存在

            valid, h_type, t_type = is_valid_rel(rel, combined_map)
            if valid and h_type and t_type:
                # 补充 v12 新增的合法关系
                new_rel = {
                    "head": rel.get("head", ""),
                    "head_type": h_type,
                    "tail": rel.get("tail", ""),
                    "tail_type": t_type,
                    "label": rel.get("label", "")
                }
                # 验证实体文本在原文中存在
                if new_rel["head"] in text and new_rel["tail"] in text:
                    clean_rels.append(new_rel)
                    existing_keys.add(rk)
                    added_from_v12 += 1

    merged_data.append({
        "id": v9_item.get("id", ""),
        "text": text,
        "entities": v9_item.get("entities", []),
        "relations": clean_rels
    })

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

# 统计
total = len(merged_data)
total_rels = sum(len(r.get("relations",[])) for r in merged_data)
no_rel = sum(1 for r in merged_data if not r.get("relations"))

print(f"合并完成！")
print(f"  从 v12 新增关系: {added_from_v12} 条")
print(f"  删除 v9_clean 非法关系: {removed_illegal} 条")
print(f"  净变化: {added_from_v12 - removed_illegal:+d} 条")
print(f"  关系均值: {total_rels/total:.2f}/条 (期望 2.80)")
print(f"  无关系比例: {no_rel/total*100:.1f}% (期望 32.7%)")
print(f"  输出: {OUTPUT_PATH}")

rel_types = Counter()
for r in merged_data:
    for rel in r.get("relations", []):
        k = f"{rel.get('head_type','?')}-{rel.get('label','?')}-{rel.get('tail_type','?')}"
        rel_types[k] += 1
print("\nTop 10 关系类型:")
for k, v in rel_types.most_common(10):
    print(f"  {k}: {v}")
