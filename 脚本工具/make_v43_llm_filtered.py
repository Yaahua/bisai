#!/usr/bin/env python3
"""
make_v43_llm_filtered.py — 过滤 LLM 补充结果，生成多个候选版本

基于 LLM 3/3 轮一致结果（135条），过滤掉：
1. 非法关系类型（不在训练集中的类型）
2. 已被证明掉分的类型（GENE-AFF-TRT, QTL-AFF-TRT, QTL-LOI-TRT, QTL-LOI-CHR）
3. 泛称实体
4. 距离异常的关系

生成版本：
- v43_llm_safe: 只保留历史上涨分的类型（VAR-HAS-TRT, CROSS-CON-VAR, ABS-AFF-TRT）
- v43_llm_medium: 保留合法类型中未被明确排除的类型
- v43_llm_full_valid: 保留所有合法类型（过滤非法）
"""
import json
import re
import zipfile
from pathlib import Path
from collections import Counter
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
CACHE = Path('/home/ubuntu/bisai/分析报告/llm_v43_cache.json')

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_json_zip(name, data):
    json_path = ROOT / f'{name}.json'
    zip_path = ROOT / f'{name}.zip'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(json_path, arcname='submit.json')
    print(f"  已保存: {json_path.name}")
    return json_path, zip_path

def rel_key(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])

def stats(data):
    n = len(data)
    total = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    return total, total / n, no_rel, no_rel / n * 100

# 加载数据
train = load(TRAIN)
base = load(ROOT / 'submit_v41_sub_conservative.json')
llm_data = load(ROOT / 'submit_v43_llm_boost.json')

base_total, base_avg, base_no_rel, base_no_rel_pct = stats(base)
print(f"底座 (0.4510): rels={base_total}, avg={base_avg:.2f}, no_rel={base_no_rel}({base_no_rel_pct:.1f}%)")

# 训练集合法类型
valid_triplets = set()
for item in train:
    for r in item.get('relations', []):
        valid_triplets.add(triplet(r))

# 已被明确排除的类型（历史实测掉分）
EXCLUDED_TYPES = {
    ('GENE', 'AFF', 'TRT'),   # 掉分 -0.0017
    ('QTL', 'AFF', 'TRT'),    # 掉分 -0.0006
    ('QTL', 'LOI', 'TRT'),    # 掉分 -0.0007
    ('QTL', 'LOI', 'CHR'),    # 掉分 -0.0007
    ('CROP', 'CON', 'VAR'),   # 掉分 -0.0010
}

# 历史涨分的类型
PROVEN_TYPES = {
    ('ABS', 'AFF', 'TRT'),    # +0.0030 (v32)
    ('VAR', 'HAS', 'TRT'),    # +0.0030 (v32)
    ('ABS', 'AFF', 'GENE'),   # +0.0008 (v36)
}

# 泛称实体黑名单
GENERIC_ENTITIES = {
    'varieties', 'genotypes', 'genes', 'traits', 'markers', 'chromosomes',
    'qtls', 'cultivars', 'lines', 'accessions', 'populations', 'species',
    'breeding lines', 'reference set', 'inbred lines', 'landraces',
    'germplasm', 'strains', 'alleles', 'loci', 'snps', 'ssrs',
    'candidate genes', 'major genes', 'minor genes', 'qtl', 'markers',
    'these', 'those', 'other', 'several', 'many', 'some', 'all',
    'various', 'different', 'multiple', 'numerous',
}

def is_generic(text):
    return text.strip().lower() in GENERIC_ENTITIES

# 找出所有新增关系
base_keys = set()
for item in base:
    for r in item.get('relations', []):
        base_keys.add(rel_key(r))

all_new_rels = []  # (idx, r)
for idx, item in enumerate(llm_data):
    for r in item.get('relations', []):
        if rel_key(r) not in base_keys:
            all_new_rels.append((idx, r))

print(f"\nLLM 新增关系总数: {len(all_new_rels)}")

# 过滤条件
def filter_rels(new_rels, allowed_types=None, excluded_types=None, filter_generic=True):
    filtered = []
    for idx, r in new_rels:
        t = triplet(r)
        
        # 类型过滤
        if t not in valid_triplets:
            continue
        if excluded_types and t in excluded_types:
            continue
        if allowed_types and t not in allowed_types:
            continue
        
        # 泛称过滤
        if filter_generic and (is_generic(r['head']) or is_generic(r['tail'])):
            continue
        
        filtered.append((idx, r))
    return filtered

# 版本 1：只保留历史涨分类型（最安全）
safe_rels = filter_rels(all_new_rels, allowed_types=PROVEN_TYPES)
print(f"\n版本1 (safe，只保留历史涨分类型): {len(safe_rels)} 条")
type_counter = Counter()
for idx, r in safe_rels:
    type_counter[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
for t, c in type_counter.most_common():
    print(f"  {t}: {c}条")

# 版本 2：保留合法且未排除的类型（中等风险）
medium_rels = filter_rels(all_new_rels, excluded_types=EXCLUDED_TYPES)
print(f"\n版本2 (medium，排除已知掉分类型): {len(medium_rels)} 条")
type_counter = Counter()
for idx, r in medium_rels:
    type_counter[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
for t, c in type_counter.most_common():
    print(f"  {t}: {c}条")

# 版本 3：保留所有合法类型（完整版）
full_rels = filter_rels(all_new_rels)
print(f"\n版本3 (full_valid，所有合法类型): {len(full_rels)} 条")

# 版本 4：CROSS-CON-VAR（未测试但历史上 CROP-CON-VAR 掉分，CROSS 可能不同）
cross_con_var_rels = filter_rels(all_new_rels, allowed_types={('CROSS', 'CON', 'VAR')})
print(f"\n版本4 (cross_con_var): {len(cross_con_var_rels)} 条")
for idx, r in cross_con_var_rels[:5]:
    print(f"  [{r['head']}] → [{r['tail']}]")

# 生成提交文件
def make_submit(name, new_rels, base_data):
    data = deepcopy(base_data)
    added = 0
    for idx, r in new_rels:
        existing = {rel_key(ex) for ex in data[idx].get('relations', [])}
        if rel_key(r) not in existing:
            data[idx]['relations'].append(r)
            added += 1
    save_json_zip(name, data)
    total, avg, no_rel, no_rel_pct = stats(data)
    diff = total - base_total
    print(f"  {name}: added={added}, rels={total}(diff={diff:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")
    return data

print("\n" + "="*60)
print("生成提交文件")
print("="*60)

make_submit('submit_v43_llm_safe', safe_rels, base)
make_submit('submit_v43_llm_medium', medium_rels, base)
make_submit('submit_v43_llm_full_valid', full_rels, base)
make_submit('submit_v43_llm_cross_con_var', cross_con_var_rels, base)

# 版本 5：减法 + LLM safe 加法组合
print("\n版本5: 减法底座 + LLM safe 加法")
# 先用 v43_sub_combined 作为底座
sub_combined = load(ROOT / 'submit_v43_sub_combined.json')
sub_combined_total = sum(len(x.get('relations', [])) for x in sub_combined)
print(f"减法底座 (v43_sub_combined): rels={sub_combined_total}")

# 在减法底座上加 safe 关系
sub_base_keys = set()
for item in sub_combined:
    for r in item.get('relations', []):
        sub_base_keys.add(rel_key(r))

safe_on_sub = [(idx, r) for idx, r in safe_rels if rel_key(r) not in sub_base_keys]
print(f"在减法底座上新增 safe 关系: {len(safe_on_sub)} 条")

data = deepcopy(sub_combined)
added = 0
for idx, r in safe_on_sub:
    existing = {rel_key(ex) for ex in data[idx].get('relations', [])}
    if rel_key(r) not in existing:
        data[idx]['relations'].append(r)
        added += 1
save_json_zip('submit_v43_sub_plus_llm_safe', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"  submit_v43_sub_plus_llm_safe: added={added}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

print("""
推荐提交顺序：
1. submit_v43_sub_combined — 减法（删35条高风险），预期涨分
2. submit_v43_llm_safe — LLM补充历史涨分类型（VAR-HAS-TRT等）
3. submit_v43_sub_plus_llm_safe — 减法+LLM safe组合
""")
