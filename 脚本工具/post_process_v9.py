#!/usr/bin/env python3
"""
v9 后处理清洗脚本
- 删除所有在训练集中从未出现的三元组（非法关系）
- 生成 submit_v9_clean.json
"""
import json
from collections import Counter

TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
INPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v9_targeted.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v9_clean.json'

with open(TRAIN_PATH, encoding='utf-8') as f:
    train = json.load(f)
with open(INPUT_PATH, encoding='utf-8') as f:
    data = json.load(f)

# 构建训练集中所有合法三元组集合
legal_triplets = set()
for item in train:
    for r in item.get('relations', []):
        legal_triplets.add((r['head_type'], r['label'], r['tail_type']))

print(f"训练集合法三元组数：{len(legal_triplets)}")
print("合法三元组列表：")
for t in sorted(legal_triplets):
    print(f"  {t[0]}-{t[1]}-{t[2]}")

# 后处理：删除非法关系
total_removed = 0
illegal_counter = Counter()
cleaned = []
for item in data:
    new_rels = []
    for r in item.get('relations', []):
        triplet = (r['head_type'], r['label'], r['tail_type'])
        if triplet in legal_triplets:
            new_rels.append(r)
        else:
            total_removed += 1
            illegal_counter[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
    cleaned.append({
        "text": item["text"],
        "entities": item["entities"],
        "relations": new_rels
    })

print(f"\n删除非法关系数：{total_removed}")
print("删除明细：")
for k, v in illegal_counter.most_common():
    print(f"  {k}: {v}次")

# 统计
total_ents = sum(len(item['entities']) for item in cleaned)
total_rels = sum(len(item['relations']) for item in cleaned)
no_rel = sum(1 for item in cleaned if not item['relations'])
print(f"\n清洗后统计：")
print(f"  实体均值/条：{total_ents/len(cleaned):.2f}（期望 5.92）")
print(f"  关系均值/条：{total_rels/len(cleaned):.2f}（期望 2.80）")
print(f"  无关系比例：{no_rel/len(cleaned)*100:.1f}%（期望 32.7%）")

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)
print(f"\n输出：{OUTPUT_PATH}")
