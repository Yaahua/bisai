#!/usr/bin/env python3
"""
分析被 ensemble_v3 多数投票丢弃的单模型关系
找出"只有1票但可能是正确的"高价值关系
"""
import json
from collections import Counter, defaultdict

V7_PATH = '数据/A榜/submit_v7_cicl_v2.json'
V9_PATH = '数据/A榜/submit_v9_targeted.json'
V10_PATH = '数据/A榜/submit_v10_gemini.json'
E3_PATH = '数据/A榜/submit_ensemble_v3.json'
V18_PATH = '数据/A榜/submit_v18_whitelist.json'
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'

v7 = json.load(open(V7_PATH, encoding='utf-8'))
v9 = json.load(open(V9_PATH, encoding='utf-8'))
v10 = json.load(open(V10_PATH, encoding='utf-8'))
e3 = json.load(open(E3_PATH, encoding='utf-8'))
v18 = json.load(open(V18_PATH, encoding='utf-8'))
train = json.load(open(TRAIN_PATH, encoding='utf-8'))

# 构建训练集合法三元组
train_triplets = set()
for item in train:
    for r in item.get('relations', []):
        train_triplets.add((r['head_type'], r['label'], r['tail_type']))

def rel_key(r):
    """关系的唯一键"""
    return (r['head'].strip().lower(), r['tail'].strip().lower(), r['label'])

def rel_key_typed(r):
    """带类型的关系键"""
    return (r.get('head_type',''), r['label'], r.get('tail_type',''))

# 分析每条数据中被丢弃的关系
print("=" * 80)
print("【1】被 ensemble_v3 丢弃的单票关系统计")
print("=" * 80)

single_vote_rels = []  # (idx, rel, source_models)
two_vote_not_in_e3 = []  # 两票但不在e3中的

for i in range(400):
    # 收集每个模型的关系
    model_rels = {
        'v7': {rel_key(r): r for r in v7[i].get('relations', [])},
        'v9': {rel_key(r): r for r in v9[i].get('relations', [])},
        'v10': {rel_key(r): r for r in v10[i].get('relations', [])},
    }
    e3_rels = {rel_key(r) for r in e3[i].get('relations', [])}
    
    # 统计每个关系的投票数
    all_keys = set()
    for m_rels in model_rels.values():
        all_keys.update(m_rels.keys())
    
    for key in all_keys:
        if key in e3_rels:
            continue  # 已在集成中
        
        voters = [name for name, m_rels in model_rels.items() if key in m_rels]
        vote_count = len(voters)
        
        # 取第一个有这个关系的模型的完整数据
        rel_data = None
        for name in voters:
            rel_data = model_rels[name][key]
            break
        
        if vote_count == 1:
            single_vote_rels.append((i, rel_data, voters))
        elif vote_count >= 2:
            two_vote_not_in_e3.append((i, rel_data, voters))

print(f"单票关系总数: {len(single_vote_rels)}")
print(f"两票但不在e3中: {len(two_vote_not_in_e3)}")

# 分析两票但不在e3中的关系（可能是字符串匹配问题）
if two_vote_not_in_e3:
    print(f"\n两票但不在e3中的关系样本（前10条）:")
    for i, rel, voters in two_vote_not_in_e3[:10]:
        trip = rel_key_typed(rel)
        print(f"  [{i}] [{rel.get('head_type','')}]{rel['head']} --{rel['label']}--> [{rel.get('tail_type','')}]{rel['tail']} | 投票: {voters}")

# 按三元组类型统计单票关系
print(f"\n单票关系按三元组类型分布:")
single_trip_cnt = Counter()
for i, rel, voters in single_vote_rels:
    trip = rel_key_typed(rel)
    single_trip_cnt[trip] += 1

for trip, cnt in single_trip_cnt.most_common(20):
    legal = "合法" if trip in train_triplets else "非法"
    print(f"  {trip[0]}-{trip[1]}-{trip[2]:<15} {cnt:>5} ({legal})")

# 按来源模型统计
print(f"\n单票关系按来源模型:")
source_cnt = Counter()
for i, rel, voters in single_vote_rels:
    for v in voters:
        source_cnt[v] += 1
print(f"  {dict(source_cnt)}")

# ===== 分析v18中仍然无关系的句子 =====
print("\n" + "=" * 80)
print("【2】v18 中无关系句子的单模型预测情况")
print("=" * 80)

no_rel_in_v18 = [i for i, item in enumerate(v18) if not item.get('relations')]
print(f"v18 无关系句子: {len(no_rel_in_v18)}")

# 这些句子在各单模型中有多少关系
recoverable = []
for idx in no_rel_in_v18:
    v7_rels = v7[idx].get('relations', [])
    v9_rels = v9[idx].get('relations', [])
    v10_rels = v10[idx].get('relations', [])
    
    # 收集所有单模型关系及投票
    all_rels = {}
    for r in v7_rels:
        k = rel_key(r)
        all_rels.setdefault(k, {'rel': r, 'votes': 0})
        all_rels[k]['votes'] += 1
    for r in v9_rels:
        k = rel_key(r)
        all_rels.setdefault(k, {'rel': r, 'votes': 0})
        all_rels[k]['votes'] += 1
    for r in v10_rels:
        k = rel_key(r)
        all_rels.setdefault(k, {'rel': r, 'votes': 0})
        all_rels[k]['votes'] += 1
    
    # 找出合法的单票/双票关系
    for k, info in all_rels.items():
        trip = rel_key_typed(info['rel'])
        if trip in train_triplets:
            recoverable.append((idx, info['rel'], info['votes']))

print(f"无关系句子中可恢复的合法关系: {len(recoverable)}")
print(f"  其中2票: {sum(1 for _,_,v in recoverable if v >= 2)}")
print(f"  其中1票: {sum(1 for _,_,v in recoverable if v == 1)}")

# 按类型统计可恢复关系
rec_by_label = Counter()
for _, rel, votes in recoverable:
    rec_by_label[rel['label']] += 1
print(f"可恢复关系按类型: {dict(rec_by_label.most_common())}")

# 两票可恢复的详情
two_vote_recoverable = [(idx, rel, v) for idx, rel, v in recoverable if v >= 2]
print(f"\n两票可恢复关系详情（前20条）:")
for idx, rel, votes in two_vote_recoverable[:20]:
    print(f"  [{idx}] [{rel.get('head_type','')}]{rel['head']} --{rel['label']}--> [{rel.get('tail_type','')}]{rel['tail']} ({votes}票)")

# ===== 分析所有两票但被丢弃的关系（宽松匹配） =====
print("\n" + "=" * 80)
print("【3】宽松匹配下的两票关系恢复分析")
print("=" * 80)

def fuzzy_key(r):
    """宽松匹配：取头尾实体的前3个词"""
    h = ' '.join(r['head'].strip().lower().split()[:3])
    t = ' '.join(r['tail'].strip().lower().split()[:3])
    return (h, t, r['label'])

fuzzy_two_vote = []
for i in range(400):
    e3_fuzzy = {fuzzy_key(r) for r in e3[i].get('relations', [])}
    
    all_fuzzy = {}
    for r in v7[i].get('relations', []):
        k = fuzzy_key(r)
        all_fuzzy.setdefault(k, {'rel': r, 'votes': set()})
        all_fuzzy[k]['votes'].add('v7')
    for r in v9[i].get('relations', []):
        k = fuzzy_key(r)
        all_fuzzy.setdefault(k, {'rel': r, 'votes': set()})
        all_fuzzy[k]['votes'].add('v9')
    for r in v10[i].get('relations', []):
        k = fuzzy_key(r)
        all_fuzzy.setdefault(k, {'rel': r, 'votes': set()})
        all_fuzzy[k]['votes'].add('v10')
    
    for k, info in all_fuzzy.items():
        if k not in e3_fuzzy and len(info['votes']) >= 2:
            trip = rel_key_typed(info['rel'])
            if trip in train_triplets:
                fuzzy_two_vote.append((i, info['rel'], info['votes']))

print(f"宽松匹配下两票但不在e3中的合法关系: {len(fuzzy_two_vote)}")
fuzzy_by_label = Counter()
for _, rel, _ in fuzzy_two_vote:
    fuzzy_by_label[rel['label']] += 1
print(f"按类型: {dict(fuzzy_by_label.most_common())}")

print(f"\n样本（前20条）:")
for idx, rel, voters in fuzzy_two_vote[:20]:
    print(f"  [{idx}] [{rel.get('head_type','')}]{rel['head']} --{rel['label']}--> [{rel.get('tail_type','')}]{rel['tail']} | 投票: {voters}")
