#!/usr/bin/env python3
"""
MGBIE Track-A 后处理脚本
基于训练集的真实关系三元组分布，过滤掉预测结果中非法的关系（即训练集中出现次数为 0 的关系组合）。
"""
import json
from collections import Counter

# 1. 提取训练集允许的关系三元组
with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    train = json.load(f)

valid_triples = set()
for item in train:
    for r in item.get('relations', []):
        valid_triples.add((r['head_type'], r['label'], r['tail_type']))

print(f"训练集共有 {len(valid_triples)} 种合法的关系三元组模式。")

# 2. 读取预测结果
with open('/home/ubuntu/bisai_clone/数据/A榜/submit.json') as f:
    pred = json.load(f)

# 3. 过滤非法关系
filtered_count = 0
filtered_types = Counter()

for item in pred:
    original_rels = item.get('relations', [])
    valid_rels = []
    for r in original_rels:
        triple = (r['head_type'], r['label'], r['tail_type'])
        if triple in valid_triples:
            valid_rels.append(r)
        else:
            filtered_count += 1
            filtered_types[triple] += 1
    item['relations'] = valid_rels

print(f"\n共过滤掉 {filtered_count} 个非法关系。")
print("过滤掉的 Top-10 非法模式：")
for triple, cnt in filtered_types.most_common(10):
    print(f"  {triple}: {cnt} 个")

# 4. 保存优化后的结果
output_path = '/home/ubuntu/bisai_clone/数据/A榜/submit_optimized.json'
with open(output_path, 'w') as f:
    json.dump(pred, f, ensure_ascii=False, indent=2)

print(f"\n优化后的结果已保存至: {output_path}")
