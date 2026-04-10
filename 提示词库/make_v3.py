#!/usr/bin/env python3
"""
v3 = v1 预测结果 + 后处理过滤非法关系
策略：只删除训练集中从未出现过的关系三元组（纯 FP），保留所有其他预测不变。
这是最稳健的方案：只减少 FP，不影响 TP 和 FN，理论上一定比 v1 高。
"""
import json, zipfile
from collections import Counter

# 1. 加载 v1（从 zip 中读取）
with zipfile.ZipFile('/home/ubuntu/bisai_clone/数据/A榜/submit.zip') as z:
    with z.open('submit.json') as f:
        v1 = json.load(f)

# 2. 提取训练集合法关系三元组
with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    train = json.load(f)

valid_triples = set()
for item in train:
    for r in item.get('relations', []):
        valid_triples.add((r['head_type'], r['label'], r['tail_type']))

print(f"训练集合法关系三元组: {len(valid_triples)} 种")

# 3. 过滤非法关系
filtered_count = 0
filtered_types = Counter()
v3 = []

for item in v1:
    new_item = dict(item)
    valid_rels = []
    for r in item.get('relations', []):
        triple = (r['head_type'], r['label'], r['tail_type'])
        if triple in valid_triples:
            valid_rels.append(r)
        else:
            filtered_count += 1
            filtered_types[triple] += 1
    new_item['relations'] = valid_rels
    v3.append(new_item)

print(f"\n过滤掉 {filtered_count} 个非法关系（纯 FP）：")
for triple, cnt in filtered_types.most_common():
    print(f"  {triple}: {cnt} 个")

# 4. 统计对比
v1_rels = sum(len(r['relations']) for r in v1)
v3_rels = sum(len(r['relations']) for r in v3)
print(f"\nv1 总关系数: {v1_rels}")
print(f"v3 总关系数: {v3_rels} (减少了 {v1_rels - v3_rels} 个纯FP)")

# 5. 格式验证
errors = []
for i, item in enumerate(v3):
    for e in item.get('entities', []):
        s, en, t = e.get('start', 0), e.get('end', 0), e.get('text', '')
        if item['text'][s:en] != t:
            errors.append(f'[{i}] 边界错误: {t!r}')
print(f"\n格式错误: {len(errors)} 个")
print("✓ 格式验证通过！" if not errors else "⚠ 有格式错误")

# 6. 保存
output = '/home/ubuntu/bisai_clone/数据/A榜/submit_v3.json'
with open(output, 'w') as f:
    json.dump(v3, f, ensure_ascii=False, indent=2)
print(f"\n✓ v3 已保存: {output}")
