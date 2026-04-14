#!/usr/bin/env python3
"""
recover_fuzzy_two_vote.py
恢复因实体边界差异被 ensemble_v3 严格匹配丢弃的两票关系

策略：
1. 对三个模型的关系做宽松匹配（取实体前3个词）
2. 如果两个以上模型都预测了同一关系（宽松匹配），但不在 e3 中
3. 验证该关系的三元组类型是否合法
4. 验证实体文本是否确实出现在原文中
5. 选择文本最长（信息最完整）的版本作为最终输出
6. 将恢复的关系追加到 v18_whitelist 上

额外安全措施：
- 排除已知的 FP 模式（如 ABS-AFF-ABS 同义词关系）
- 验证 head/tail 文本是 text 的子串
- 验证 head_start/head_end/tail_start/tail_end 的正确性
"""

import json
import re
from collections import Counter, defaultdict
from copy import deepcopy

V7_PATH = '数据/A榜/submit_v7_cicl_v2.json'
V9_PATH = '数据/A榜/submit_v9_targeted.json'
V10_PATH = '数据/A榜/submit_v10_gemini.json'
E3_PATH = '数据/A榜/submit_ensemble_v3.json'
V18_PATH = '数据/A榜/submit_v18_whitelist.json'
OUTPUT_PATH = '数据/A榜/submit_v19_recovered.json'
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

# 已知的 FP 模式（需要排除）
FP_PATTERNS = {
    # ABS-AFF-ABS 同义词不是真关系
    ('ABS', 'AFF', 'ABS'),
    # BM-USE-CHR 不合法
    ('BM', 'USE', 'CHR'),
    # TRT-USE-BM 在训练集中很少且精确率低
    ('TRT', 'USE', 'BM'),
}


def fuzzy_key(r):
    """宽松匹配键：取头尾实体的前3个词 + 关系标签"""
    h = ' '.join(r['head'].strip().lower().split()[:3])
    t = ' '.join(r['tail'].strip().lower().split()[:3])
    return (h, t, r['label'])


def strict_key(r):
    """严格匹配键"""
    return (r['head'].strip().lower(), r['tail'].strip().lower(), r['label'])


def validate_rel(rel, text):
    """验证关系的实体是否在原文中"""
    head = rel['head']
    tail = rel['tail']
    
    # 检查文本是否是原文的子串
    if head not in text or tail not in text:
        return False
    
    # 检查 offset 是否正确
    h_start = rel.get('head_start', -1)
    h_end = rel.get('head_end', -1)
    t_start = rel.get('tail_start', -1)
    t_end = rel.get('tail_end', -1)
    
    if h_start >= 0 and h_end > h_start:
        if text[h_start:h_end] != head:
            # 尝试修复 offset
            idx = text.find(head)
            if idx >= 0:
                rel['head_start'] = idx
                rel['head_end'] = idx + len(head)
            else:
                return False
    
    if t_start >= 0 and t_end > t_start:
        if text[t_start:t_end] != tail:
            idx = text.find(tail)
            if idx >= 0:
                rel['tail_start'] = idx
                rel['tail_end'] = idx + len(tail)
            else:
                return False
    
    return True


def select_best_version(candidates):
    """从多个候选版本中选择最佳版本（文本最长的）"""
    best = candidates[0]
    best_len = len(best['head']) + len(best['tail'])
    for c in candidates[1:]:
        c_len = len(c['head']) + len(c['tail'])
        if c_len > best_len:
            best = c
            best_len = c_len
    return best


# ===== 主处理 =====
output = deepcopy(v18)
total_recovered = 0
recovered_by_label = Counter()
recovered_by_source = Counter()

for i in range(400):
    text = v18[i]['text']
    
    # 收集 v18 已有关系（严格+宽松）
    v18_strict = {strict_key(r) for r in v18[i].get('relations', [])}
    v18_fuzzy = {fuzzy_key(r) for r in v18[i].get('relations', [])}
    
    # 收集三个模型的关系，按宽松键分组
    fuzzy_groups = defaultdict(lambda: {'rels': [], 'voters': set()})
    
    for model_name, model_data in [('v7', v7), ('v9', v9), ('v10', v10)]:
        for r in model_data[i].get('relations', []):
            fk = fuzzy_key(r)
            fuzzy_groups[fk]['rels'].append(r)
            fuzzy_groups[fk]['voters'].add(model_name)
    
    # 找出两票以上但不在 v18 中的关系
    for fk, info in fuzzy_groups.items():
        if len(info['voters']) < 2:
            continue
        
        # 检查是否已在 v18 中（宽松匹配）
        if fk in v18_fuzzy:
            continue
        
        # 选择最佳版本
        best = select_best_version(info['rels'])
        
        # 检查三元组类型是否合法
        trip = (best.get('head_type', ''), best['label'], best.get('tail_type', ''))
        if trip not in train_triplets:
            continue
        
        # 排除已知 FP 模式
        if trip in FP_PATTERNS:
            continue
        
        # 验证实体文本
        if not validate_rel(best, text):
            continue
        
        # 检查严格匹配是否已存在
        sk = strict_key(best)
        if sk in v18_strict:
            continue
        
        # 恢复这条关系
        clean_rel = {
            'head': best['head'],
            'head_type': best.get('head_type', ''),
            'head_start': best.get('head_start', text.find(best['head'])),
            'head_end': best.get('head_end', text.find(best['head']) + len(best['head'])),
            'tail': best['tail'],
            'tail_type': best.get('tail_type', ''),
            'tail_start': best.get('tail_start', text.find(best['tail'])),
            'tail_end': best.get('tail_end', text.find(best['tail']) + len(best['tail'])),
            'label': best['label']
        }
        
        output[i]['relations'].append(clean_rel)
        v18_strict.add(sk)
        v18_fuzzy.add(fk)
        total_recovered += 1
        recovered_by_label[best['label']] += 1
        recovered_by_source[','.join(sorted(info['voters']))] += 1

# 保存输出
json.dump(output, open(OUTPUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 统计
total_rels = sum(len(x.get('relations', [])) for x in output)
no_rel = sum(1 for x in output if not x.get('relations'))

print(f"=== 语义加权投票恢复结果 ===")
print(f"输入: {V18_PATH}")
print(f"输出: {OUTPUT_PATH}")
print(f"v18 关系数: {sum(len(x.get('relations',[])) for x in v18)}")
print(f"恢复关系数: {total_recovered}")
print(f"最终关系数: {total_rels}")
print(f"关系均值: {total_rels/len(output):.2f}")
print(f"无关系比例: {no_rel/len(output)*100:.1f}%")

print(f"\n恢复关系按类型:")
for label, cnt in recovered_by_label.most_common():
    print(f"  {label}: +{cnt}")

print(f"\n恢复关系按来源模型组合:")
for source, cnt in recovered_by_source.most_common():
    print(f"  {source}: +{cnt}")
