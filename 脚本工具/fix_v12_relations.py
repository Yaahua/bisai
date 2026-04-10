#!/usr/bin/env python3.11
"""
修复 v12 预测结果中的关系类型键名异常
问题：head_type/tail_type 字段出现重复拼接（如 GENE-GENE、CROP-CROP）
原因：entity_map 查找时，部分实体的 label 字段被重复赋值
"""
import json
from collections import Counter

INPUT_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_v12_reverse_scir.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v12_fixed.json'

VALID_ENTITY_TYPES = {"CROP", "VAR", "GENE", "QTL", "MRK", "TRT", "BM", "LOI", "CHR", "ABS"}
VALID_TRIPLES = {
    "CROP-CON-VAR", "VAR-HAS-TRT", "VAR-USE-BM", "VAR-OCI-GENE",
    "GENE-AFF-TRT", "GENE-LOI-TRT", "GENE-LOI-CHR",
    "QTL-LOI-TRT", "QTL-LOI-CHR", "MRK-LOI-CHR",
    "TRT-HAS-BM", "TRT-AFF-BM",
    "CROP-CON-GENE", "CROP-CON-QTL", "CROP-CON-MRK",
    "VAR-HAS-GENE", "VAR-HAS-QTL",
}

def clean_type(t):
    """修复重复拼接的类型字段，如 GENE-GENE -> GENE"""
    if not t:
        return t
    # 如果是合法类型，直接返回
    if t in VALID_ENTITY_TYPES:
        return t
    # 尝试提取第一个合法类型
    for vt in VALID_ENTITY_TYPES:
        if t.startswith(vt):
            return vt
    return t

with open(INPUT_PATH) as f:
    data = json.load(f)

fixed_data = []
removed_illegal = 0
fixed_types = 0

for item in data:
    # 构建实体映射
    entity_map = {}
    for e in item.get("entities", []):
        label = e.get("label", "")
        text  = e.get("text", "")
        if text:
            entity_map[text] = clean_type(label)

    # 修复关系
    clean_relations = []
    for rel in item.get("relations", []):
        head = rel.get("head", "")
        tail = rel.get("tail", "")
        label = rel.get("label", "")

        # 修复 head_type / tail_type
        h_type = clean_type(rel.get("head_type", entity_map.get(head, "")))
        t_type = clean_type(rel.get("tail_type", entity_map.get(tail, "")))

        if h_type != rel.get("head_type", ""):
            fixed_types += 1
        if t_type != rel.get("tail_type", ""):
            fixed_types += 1

        # 过滤非法三元组
        triple_key = f"{h_type}-{label}-{t_type}"
        if triple_key not in VALID_TRIPLES:
            removed_illegal += 1
            continue

        clean_relations.append({
            "head": head,
            "head_type": h_type,
            "tail": tail,
            "tail_type": t_type,
            "label": label
        })

    fixed_data.append({
        "id": item.get("id", ""),
        "text": item.get("text", ""),
        "entities": item.get("entities", []),
        "relations": clean_relations
    })

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(fixed_data, f, ensure_ascii=False, indent=2)

# 统计
total = len(fixed_data)
total_rels = sum(len(r.get("relations", [])) for r in fixed_data)
no_rel = sum(1 for r in fixed_data if not r.get("relations"))

print(f"修复完成！")
print(f"  修复类型字段: {fixed_types} 处")
print(f"  删除非法关系: {removed_illegal} 条")
print(f"  关系均值: {total_rels/total:.2f}/条 (期望 2.80)")
print(f"  无关系比例: {no_rel/total*100:.1f}% (期望 32.7%)")
print(f"  输出: {OUTPUT_PATH}")

# 关系类型分布
rel_types = Counter()
for r in fixed_data:
    for rel in r.get("relations", []):
        k = f"{rel.get('head_type','?')}-{rel.get('label','?')}-{rel.get('tail_type','?')}"
        rel_types[k] += 1
print("\nTop 10 关系类型（修复后）:")
for k, v in rel_types.most_common(10):
    print(f"  {k}: {v}")
