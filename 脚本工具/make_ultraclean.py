#!/usr/bin/env python3.11
"""
生成 v9_ultraclean：彻底清洗 v9_clean 的所有非法关系
同时生成 v9_ultraclean + v12 合并版本（补充合法漏标关系）
"""
import json
from collections import Counter

V9_PATH     = '/home/ubuntu/bisai/数据/A榜/submit_v9_clean.json'
V12_PATH    = '/home/ubuntu/bisai/数据/A榜/submit_v12_reverse_scir.json'
OUT_CLEAN   = '/home/ubuntu/bisai/数据/A榜/submit_v9_ultraclean.zip'
OUT_MERGED  = '/home/ubuntu/bisai/数据/A榜/submit_v9uc_v12merged.json'
OUT_CLEAN_J = '/home/ubuntu/bisai/数据/A榜/submit_v9_ultraclean.json'

VALID_TRIPLES = {
    "CROP-CON-VAR", "VAR-HAS-TRT", "VAR-USE-BM", "VAR-OCI-GENE",
    "GENE-AFF-TRT", "GENE-LOI-TRT", "GENE-LOI-CHR",
    "QTL-LOI-TRT", "QTL-LOI-CHR", "MRK-LOI-CHR",
    "TRT-HAS-BM", "TRT-AFF-BM",
    "CROP-CON-GENE", "CROP-CON-QTL", "CROP-CON-MRK",
    "VAR-HAS-GENE", "VAR-HAS-QTL",
}

VALID_ENTITY_TYPES = {"CROP", "VAR", "GENE", "QTL", "MRK", "TRT", "BM", "LOI", "CHR"}

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
    return (rel.get("head",""), rel.get("label",""), rel.get("tail",""))

def is_valid(rel):
    h_type = clean_type(rel.get("head_type",""))
    t_type = clean_type(rel.get("tail_type",""))
    label  = rel.get("label","")
    if not h_type or not t_type:
        return False, h_type, t_type
    triple_key = f"{h_type}-{label}-{t_type}"
    return triple_key in VALID_TRIPLES, h_type, t_type

with open(V9_PATH) as f:
    v9_data = json.load(f)
with open(V12_PATH) as f:
    v12_data = json.load(f)

# v12 索引
v12_index = {item.get("id", item.get("text","")): item for item in v12_data}

# ── 生成 v9_ultraclean（纯清洗版）──
ultraclean = []
removed = 0
for item in v9_data:
    clean_rels = []
    for rel in item.get("relations", []):
        valid, h_type, t_type = is_valid(rel)
        if valid:
            rel["head_type"] = h_type
            rel["tail_type"] = t_type
            clean_rels.append(rel)
        else:
            removed += 1
    ultraclean.append({
        "id": item.get("id",""),
        "text": item.get("text",""),
        "entities": item.get("entities",[]),
        "relations": clean_rels
    })

with open(OUT_CLEAN_J, 'w', encoding='utf-8') as f:
    json.dump(ultraclean, f, ensure_ascii=False, indent=2)

total = len(ultraclean)
total_rels = sum(len(r.get("relations",[])) for r in ultraclean)
no_rel = sum(1 for r in ultraclean if not r.get("relations"))
print(f"=== v9_ultraclean ===")
print(f"  删除非法关系: {removed} 条")
print(f"  关系均值: {total_rels/total:.2f}/条 (期望 2.80)")
print(f"  无关系比例: {no_rel/total*100:.1f}% (期望 32.7%)")

# ── 生成 v9_ultraclean + v12 合并版（补充漏标）──
merged = []
added = 0
for uc_item in ultraclean:
    key = uc_item.get("id", uc_item.get("text",""))
    text = uc_item.get("text","")
    existing_keys = {rel_key(r) for r in uc_item.get("relations",[])}
    new_rels = list(uc_item.get("relations",[]))

    v12_item = v12_index.get(key)
    if v12_item:
        # v12 实体映射（用于推断类型）
        v12_emap = {}
        for e in v12_item.get("entities", []):
            et = e.get("entity", e.get("text",""))
            el = e.get("type", e.get("label",""))
            if et:
                v12_emap[et] = clean_type(el)

        for rel in v12_item.get("relations", []):
            rk = rel_key(rel)
            if rk in existing_keys:
                continue
            # 推断类型
            h = rel.get("head","")
            t = rel.get("tail","")
            l = rel.get("label","")
            h_type = clean_type(rel.get("head_type", v12_emap.get(h,"")))
            t_type = clean_type(rel.get("tail_type", v12_emap.get(t,"")))
            if not h_type or not t_type:
                continue
            triple_key = f"{h_type}-{l}-{t_type}"
            if triple_key not in VALID_TRIPLES:
                continue
            # 验证实体在原文中存在
            if h not in text or t not in text:
                continue
            new_rels.append({
                "head": h, "head_type": h_type,
                "tail": t, "tail_type": t_type,
                "label": l
            })
            existing_keys.add(rk)
            added += 1

    merged.append({
        "id": uc_item.get("id",""),
        "text": text,
        "entities": uc_item.get("entities",[]),
        "relations": new_rels
    })

with open(OUT_MERGED, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

total_m = len(merged)
total_rels_m = sum(len(r.get("relations",[])) for r in merged)
no_rel_m = sum(1 for r in merged if not r.get("relations"))
print(f"\n=== v9_ultraclean + v12 merged ===")
print(f"  从 v12 补充关系: {added} 条")
print(f"  关系均值: {total_rels_m/total_m:.2f}/条 (期望 2.80)")
print(f"  无关系比例: {no_rel_m/total_m*100:.1f}% (期望 32.7%)")
print(f"  输出: {OUT_MERGED}")

# 关系类型分布
rel_types = Counter()
for r in merged:
    for rel in r.get("relations",[]):
        k = f"{rel.get('head_type','?')}-{rel.get('label','?')}-{rel.get('tail_type','?')}"
        rel_types[k] += 1
print("\nTop 10 关系类型:")
for k,v in rel_types.most_common(10):
    print(f"  {k}: {v}")
