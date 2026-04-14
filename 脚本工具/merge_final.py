#!/usr/bin/env python3
"""
merge_final.py — 最终合并脚本
将多个来源的关系进行智能合并，生成多个候选提交版本

来源：
1. ensemble_v3（三模型严格投票，精确率最高）
2. v18_whitelist（v3 + 白名单规则补充）
3. v19_recovered（v18 + 宽松匹配两票恢复）
4. sc_gemini（Gemini自一致性采样投票）

合并策略：
- 版本A（保守）：v18 + SC中与v18重叠的关系（交集增强）
- 版本B（均衡）：v19 + SC中至少2票的关系（并集，但排除非法三元组）
- 版本C（激进）：v19 + SC全部关系
- 版本D（四源交叉验证）：在4个来源中出现>=2次的关系
"""
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy

sys.stdout.reconfigure(line_buffering=True)

E3_PATH = '数据/A榜/submit_ensemble_v3.json'
V18_PATH = '数据/A榜/submit_v18_whitelist.json'
V19_PATH = '数据/A榜/submit_v19_recovered.json'
SC_PATH = '数据/A榜/submit_sc_gemini.json'
V7_PATH = '数据/A榜/submit_v7_cicl_v2.json'
V9_PATH = '数据/A榜/submit_v9_targeted.json'
V10_PATH = '数据/A榜/submit_v10_gemini.json'
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'

e3 = json.load(open(E3_PATH, encoding='utf-8'))
v18 = json.load(open(V18_PATH, encoding='utf-8'))
v19 = json.load(open(V19_PATH, encoding='utf-8'))
sc = json.load(open(SC_PATH, encoding='utf-8'))
v7 = json.load(open(V7_PATH, encoding='utf-8'))
v9 = json.load(open(V9_PATH, encoding='utf-8'))
v10 = json.load(open(V10_PATH, encoding='utf-8'))
train = json.load(open(TRAIN_PATH, encoding='utf-8'))

# 合法三元组
train_triplets = set()
for item in train:
    for r in item.get('relations', []):
        train_triplets.add((r['head_type'], r['label'], r['tail_type']))

ILLEGAL_TRIPLETS = {
    ('VAR','CON','CROP'), ('GENE','CON','CROP'), ('CROSS','CON','CROP'),
    ('MRK','AFF','TRT'), ('GENE','AFF','ABS'),
    ('TRT','HAS','VAR'), ('TRT','HAS','CROP'),
    ('VAR','OCI','TRT'), ('VAR','AFF','BIS'),
    ('QTL','LOI','VAR'), ('CROP','HAS','ABS'),
    ('VAR','HAS','ABS'), ('VAR','HAS','BIS'),
    ('BM','USE','CROP'), ('CHR','LOI','VAR'),
    ('TRT','LOI','TRT'), ('ABS','LOI','CHR'),
    ('BIS','LOI','CHR'), ('GST','AFF','TRT'),
    ('CROP','AFF','TRT'), ('ABS','AFF','ABS'),
}


def rel_key(r):
    return (r['head'].strip().lower(), r['tail'].strip().lower(), r['label'])


def is_legal(r):
    trip = (r.get('head_type',''), r['label'], r.get('tail_type',''))
    return trip in train_triplets and trip not in ILLEGAL_TRIPLETS


def merge_into(base, additions, check_legal=True):
    """将 additions 中的关系合并到 base 中（去重）"""
    output = deepcopy(base)
    total_new = 0
    for i in range(400):
        existing = {rel_key(r) for r in output[i].get('relations', [])}
        for r in additions[i].get('relations', []):
            key = rel_key(r)
            if key not in existing:
                if check_legal and not is_legal(r):
                    continue
                output[i]['relations'].append(r)
                existing.add(key)
                total_new += 1
    return output, total_new


def cross_validate(sources, threshold=2):
    """多源交叉验证：在 threshold 个以上来源中出现的关系"""
    output = deepcopy(sources[0])
    for i in range(400):
        # 统计每个关系在多少个来源中出现
        rel_votes = Counter()
        rel_data = {}
        for src in sources:
            seen = set()
            for r in src[i].get('relations', []):
                key = rel_key(r)
                if key not in seen:
                    rel_votes[key] += 1
                    seen.add(key)
                    if key not in rel_data:
                        rel_data[key] = r
        
        # 保留投票 >= threshold 的关系
        output[i]['relations'] = []
        for key, count in rel_votes.items():
            if count >= threshold:
                r = rel_data[key]
                if is_legal(r):
                    output[i]['relations'].append(r)
    
    return output


def stats(data, name):
    total = sum(len(x.get('relations',[])) for x in data)
    norel = sum(1 for x in data if not x.get('relations'))
    by_label = Counter()
    for item in data:
        for r in item.get('relations', []):
            by_label[r['label']] += 1
    print(f"  {name:<30} 关系={total:>5}, 均值={total/400:.2f}, 无关系={norel}({norel/4:.1f}%)")
    return total


# ===== 生成各版本 =====
print("=== 基础版本统计 ===", flush=True)
stats(e3, "ensemble_v3 (基线)")
stats(v18, "v18_whitelist")
stats(v19, "v19_recovered")
stats(sc, "sc_gemini")
stats(v7, "v7_单模型")
stats(v9, "v9_单模型")
stats(v10, "v10_单模型")

# 版本A：v18 + SC交集增强（只保留v18和SC都有的关系）
print("\n=== 版本A：v18 + SC交集增强 ===", flush=True)
ver_a = deepcopy(v18)
a_enhanced = 0
for i in range(400):
    v18_keys = {rel_key(r) for r in v18[i].get('relations', [])}
    sc_keys = {rel_key(r) for r in sc[i].get('relations', [])}
    # SC中有但v18没有，且在e3中也没有的 → 不加（太冒险）
    # 只保留v18已有的
# 版本A就是v18本身
stats(ver_a, "版本A (v18)")

# 版本B：v19 + SC合法关系（均衡）
print("\n=== 版本B：v19 + SC合法关系 ===", flush=True)
ver_b, b_new = merge_into(v19, sc, check_legal=True)
stats(ver_b, f"版本B (v19+SC, +{b_new})")

# 版本C：四源交叉验证（e3, sc, v7, v9, v10 中 >=2 票）
print("\n=== 版本C：五源交叉验证 (>=2票) ===", flush=True)
ver_c = cross_validate([e3, sc, v7, v9, v10], threshold=2)
stats(ver_c, "版本C (5源>=2票)")

# 版本D：v18 + SC中与至少一个单模型一致的关系
print("\n=== 版本D：v18 + SC与单模型交叉验证 ===", flush=True)
ver_d = deepcopy(v18)
d_new = 0
for i in range(400):
    v18_keys = {rel_key(r) for r in v18[i].get('relations', [])}
    v7_keys = {rel_key(r) for r in v7[i].get('relations', [])}
    v9_keys = {rel_key(r) for r in v9[i].get('relations', [])}
    v10_keys = {rel_key(r) for r in v10[i].get('relations', [])}
    
    for r in sc[i].get('relations', []):
        key = rel_key(r)
        if key in v18_keys:
            continue
        if not is_legal(r):
            continue
        # SC预测 + 至少一个原始单模型也预测了
        if key in v7_keys or key in v9_keys or key in v10_keys:
            ver_d[i]['relations'].append(r)
            v18_keys.add(key)
            d_new += 1

stats(ver_d, f"版本D (v18+SC∩单模型, +{d_new})")

# 版本E：v19 + SC与单模型交叉验证
print("\n=== 版本E：v19 + SC与单模型交叉验证 ===", flush=True)
ver_e = deepcopy(v19)
e_new = 0
for i in range(400):
    v19_keys = {rel_key(r) for r in v19[i].get('relations', [])}
    v7_keys = {rel_key(r) for r in v7[i].get('relations', [])}
    v9_keys = {rel_key(r) for r in v9[i].get('relations', [])}
    v10_keys = {rel_key(r) for r in v10[i].get('relations', [])}
    
    for r in sc[i].get('relations', []):
        key = rel_key(r)
        if key in v19_keys:
            continue
        if not is_legal(r):
            continue
        if key in v7_keys or key in v9_keys or key in v10_keys:
            ver_e[i]['relations'].append(r)
            v19_keys.add(key)
            e_new += 1

stats(ver_e, f"版本E (v19+SC∩单模型, +{e_new})")

# 版本F：纯SC结果（作为对照）
print("\n=== 版本F：纯SC结果 ===", flush=True)
stats(sc, "版本F (纯SC)")

# ===== 保存所有版本 =====
versions = {
    'submit_v20_verA_v18only.json': ver_a,
    'submit_v20_verB_v19_sc.json': ver_b,
    'submit_v20_verC_5source_2vote.json': ver_c,
    'submit_v20_verD_v18_sc_cross.json': ver_d,
    'submit_v20_verE_v19_sc_cross.json': ver_e,
    'submit_v20_verF_sc_only.json': sc,
}

print("\n=== 保存所有版本 ===", flush=True)
for fname, data in versions.items():
    path = f'数据/A榜/{fname}'
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    total = sum(len(x.get('relations',[])) for x in data)
    print(f"  {fname}: {total} 关系", flush=True)

# ===== 推荐提交顺序 =====
print("\n=== 推荐提交顺序 ===", flush=True)
print("1. 版本D (v18+SC交叉验证) — 最安全的增量，SC预测+单模型确认", flush=True)
print("2. 版本E (v19+SC交叉验证) — 在D基础上加入宽松匹配恢复", flush=True)
print("3. 版本C (五源>=2票) — 完全重新投票，可能改变基线", flush=True)
print("4. 版本B (v19+SC全量) — 激进，可能引入FP", flush=True)
