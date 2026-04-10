#!/usr/bin/env python3
"""从官方 1000 条训练数据中提取比赛级规律，输出提示词库素材"""
import json
from collections import Counter, defaultdict

with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    data = json.load(f)

print(f"总条数: {len(data)}")

# ===== 1. 实体类型分布 =====
ent_counter = Counter()
for d in data:
    for e in d['entities']:
        ent_counter[e['label']] += 1
print("\n===== 实体类型分布（全量1000条）=====")
total_ents = sum(ent_counter.values())
for lbl, cnt in ent_counter.most_common():
    print(f"  {lbl}: {cnt} ({cnt/total_ents*100:.1f}%)")

# ===== 2. 关系类型分布 =====
rel_counter = Counter()
for d in data:
    for r in d['relations']:
        rel_counter[r['label']] += 1
print("\n===== 关系类型分布（全量1000条）=====")
total_rels = sum(rel_counter.values())
for lbl, cnt in rel_counter.most_common():
    print(f"  {lbl}: {cnt} ({cnt/total_rels*100:.1f}%)")

# ===== 3. 每种关系的 head_type → tail_type 组合 =====
print("\n===== 每种关系的 head→tail 实体类型组合 =====")
rel_pairs = defaultdict(Counter)
for d in data:
    for r in d['relations']:
        pair = f"{r['head_type']}→{r['tail_type']}"
        rel_pairs[r['label']][pair] += 1

for rel_lbl in ['AFF', 'LOI', 'HAS', 'CON', 'USE', 'OCI']:
    pairs = rel_pairs[rel_lbl]
    total = sum(pairs.values())
    print(f"\n  [{rel_lbl}] 共{total}条:")
    for pair, cnt in pairs.most_common(8):
        print(f"    {pair}: {cnt} ({cnt/total*100:.1f}%)")

# ===== 4. 无关系样本比例 =====
no_rel = sum(1 for d in data if len(d['relations']) == 0)
no_ent = sum(1 for d in data if len(d['entities']) == 0)
print(f"\n===== 空标注统计 =====")
print(f"  无关系的样本: {no_rel}/1000 ({no_rel/10:.1f}%)")
print(f"  无实体的样本: {no_ent}/1000 ({no_ent/10:.1f}%)")

# ===== 5. 挑选 Few-shot 样本（覆盖所有关系类型，边界正确，文本简短）=====
print("\n===== 挑选 Few-shot 候选样本 =====")
rel_covered = set()
fewshot_candidates = []
target_rels = ['AFF', 'LOI', 'HAS', 'CON', 'USE', 'OCI']

for d in data:
    if len(d['entities']) == 0:
        continue
    # 验证边界
    ok = True
    for e in d['entities']:
        if d['text'][e['start']:e['end']] != e['text']:
            ok = False; break
    if not ok:
        continue
    # 验证关系锚点
    for r in d['relations']:
        if d['text'][r['head_start']:r['head_end']] != r['head']:
            ok = False; break
        if d['text'][r['tail_start']:r['tail_end']] != r['tail']:
            ok = False; break
    if not ok:
        continue
    
    rels_in_sample = {r['label'] for r in d['relations']}
    new_rels = rels_in_sample - rel_covered
    
    # 优先选能覆盖新关系类型的样本，且文本不超过300字符
    if new_rels and len(d['text']) <= 300:
        fewshot_candidates.append((d, new_rels))
        rel_covered |= new_rels

# 补充一条无关系样本
for d in data:
    if len(d['relations']) == 0 and len(d['entities']) > 0 and len(d['text']) <= 200:
        ok = True
        for e in d['entities']:
            if d['text'][e['start']:e['end']] != e['text']:
                ok = False; break
        if ok:
            fewshot_candidates.append((d, {'[无关系]'}))
            break

print(f"  已覆盖关系类型: {rel_covered}")
print(f"  候选样本数: {len(fewshot_candidates)}")
for i, (d, rels) in enumerate(fewshot_candidates):
    print(f"\n  [样本{i+1}] 覆盖关系: {rels}")
    print(f"  文本({len(d['text'])}字): {d['text'][:100]}...")
    print(f"  实体数: {len(d['entities'])}  关系数: {len(d['relations'])}")

# 保存 Few-shot 样本
fewshot_data = [d for d, _ in fewshot_candidates]
with open('/home/ubuntu/fewshot_samples.json', 'w', encoding='utf-8') as f:
    json.dump(fewshot_data, f, ensure_ascii=False, indent=2)
print(f"\n  Few-shot 样本已保存: /home/ubuntu/fewshot_samples.json")
