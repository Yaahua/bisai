#!/usr/bin/env python3.11
"""
v13 生成策略：
1. 以 ensemble_v3（0.4172）为基础
2. 删除非法三元组（ABS-AFF-TRT、CROP-HAS-TRT 等）
3. 用 v12（ReverseNER）的合法关系补充漏标
4. 输出 submit_v13_e3clean.json（纯清洗版）
   和 submit_v13_e3v12.json（清洗+补充版）
"""
import json
from collections import Counter

E3_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'
V12_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v12_reverse_scir.json'
OUT_CLEAN  = '/home/ubuntu/bisai/数据/A榜/submit_v13_e3clean.json'
OUT_MERGED = '/home/ubuntu/bisai/数据/A榜/submit_v13_e3v12.json'

# 官方合法三元组（从训练集统计得出）
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
    return (rel.get("head","").strip(), rel.get("label",""), rel.get("tail","").strip())

def triple_str(rel):
    h = clean_type(rel.get("head_type",""))
    l = rel.get("label","")
    t = clean_type(rel.get("tail_type",""))
    return f"{h}-{l}-{t}"

# 加载数据
with open(E3_PATH) as f:
    e3_data = json.load(f)
with open(V12_PATH) as f:
    v12_data = json.load(f)

# v12 索引
v12_index = {item.get("id", item.get("text","")): item for item in v12_data}

removed_illegal = 0
added_from_v12  = 0

clean_data  = []
merged_data = []

for e3_item in e3_data:
    key  = e3_item.get("id", e3_item.get("text",""))
    text = e3_item.get("text","")

    # ── Step 1：清洗 ensemble_v3 的非法关系 ──
    clean_rels = []
    for rel in e3_item.get("relations", []):
        ts = triple_str(rel)
        if ts in VALID_TRIPLES:
            # 修正 head_type/tail_type
            rel["head_type"] = clean_type(rel.get("head_type",""))
            rel["tail_type"] = clean_type(rel.get("tail_type",""))
            clean_rels.append(rel)
        else:
            removed_illegal += 1

    clean_data.append({
        "id":        e3_item.get("id",""),
        "text":      text,
        "entities":  e3_item.get("entities",[]),
        "relations": clean_rels
    })

    # ── Step 2：从 v12 补充合法漏标关系 ──
    existing_keys = {rel_key(r) for r in clean_rels}
    new_rels = list(clean_rels)

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
                continue

            h = rel.get("head","").strip()
            t = rel.get("tail","").strip()
            l = rel.get("label","")
            h_type = clean_type(rel.get("head_type", v12_emap.get(h,"")))
            t_type = clean_type(rel.get("tail_type", v12_emap.get(t,"")))

            if not h_type or not t_type:
                continue
            if f"{h_type}-{l}-{t_type}" not in VALID_TRIPLES:
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

# 保存
with open(OUT_CLEAN, 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=2)
with open(OUT_MERGED, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

def stats(data, label):
    total = len(data)
    total_rels = sum(len(r.get("relations",[])) for r in data)
    no_rel = sum(1 for r in data if not r.get("relations"))
    print(f"\n=== {label} ===")
    print(f"  关系均值: {total_rels/total:.2f}/条 (期望 2.80)")
    print(f"  无关系比例: {no_rel/total*100:.1f}% (期望 32.7%)")
    rel_types = Counter()
    for r in data:
        for rel in r.get("relations",[]):
            k = f"{rel.get('head_type','?')}-{rel.get('label','?')}-{rel.get('tail_type','?')}"
            rel_types[k] += 1
    print("  Top 8 关系类型:")
    for k,v in rel_types.most_common(8):
        print(f"    {k}: {v}")

print(f"删除 ensemble_v3 非法关系: {removed_illegal} 条")
print(f"从 v12 补充合法关系: {added_from_v12} 条")
stats(clean_data,  "v13_e3clean（纯清洗）")
stats(merged_data, "v13_e3v12（清洗+v12补充）")
