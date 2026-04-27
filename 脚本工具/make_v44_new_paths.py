"""
v44 冲榜脚本 - 全新路径
基于深度分析发现的三条新道路：

路径A：关系方向修正（减法+加法组合）
  - 删除 VAR-CON-CROSS（4条，方向错误，训练集CROSS-CON-VAR=28条）
  - 删除 GENE-LOI-MRK（5条，方向错误，训练集MRK-LOI-GENE=22条）
  - 可选：添加正确方向的 CROSS-CON-VAR 和 MRK-LOI-GENE

路径B：高风险假阳性清除
  - 删除训练集频次<5的关系类型（底座中共24条）
  - 包括：GENE-CON-TRT(4条), QTL-AFF-BIS(3条), BM-USE-TRT(3条), VAR-OCI-GST(2条)等

路径C：精准减法（只删最高风险的）
  - 组合路径A + 路径B中最高风险的几类
"""

import json
import copy
from collections import Counter

BASE_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v41_sub_conservative.json'
OUTPUT_DIR = '/home/ubuntu/bisai/数据/A榜'

with open(BASE_PATH) as f:
    base = json.load(f)
with open('/home/ubuntu/bisai/数据/官方原始数据/test_A.json') as f:
    test_a = json.load(f)
with open('/home/ubuntu/bisai/数据/官方原始数据/train.json') as f:
    train = json.load(f)

def save_submission(data, name):
    import os, zipfile
    json_path = f"{OUTPUT_DIR}/{name}.json"
    zip_path = f"{OUTPUT_DIR}/{name}.zip"
    with open(json_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(json_path, 'submit.json')
    n_rel = sum(len(item.get('relations', [])) for item in data)
    n_no_rel = sum(1 for item in data if not item.get('relations'))
    print(f"  {name}: {n_rel}条关系, 均值{n_rel/len(data):.2f}, 无关系{n_no_rel}个({n_no_rel/len(data)*100:.1f}%)")
    return json_path

base_rel_total = sum(len(item.get('relations', [])) for item in base)
print(f"底座: {base_rel_total}条关系, 均值{base_rel_total/len(base):.2f}, 无关系{sum(1 for item in base if not item.get('relations'))}个")

# ============================================================
# 路径A1：只删 VAR-CON-CROSS（4条，方向错误）
# ============================================================
print("\n=== 路径A1：删除 VAR-CON-CROSS（方向错误）===")
data_a1 = copy.deepcopy(base)
removed_a1 = 0
for item in data_a1:
    orig = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', [])
                         if not (r['head_type'] == 'VAR' and r['label'] == 'CON' and r['tail_type'] == 'CROSS')]
    removed_a1 += orig - len(item['relations'])
print(f"  删除 VAR-CON-CROSS: {removed_a1}条")
save_submission(data_a1, 'submit_v44_del_var_con_cross')

# ============================================================
# 路径A2：只删 GENE-LOI-MRK（5条，方向错误）
# ============================================================
print("\n=== 路径A2：删除 GENE-LOI-MRK（方向错误）===")
data_a2 = copy.deepcopy(base)
removed_a2 = 0
for item in data_a2:
    orig = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', [])
                         if not (r['head_type'] == 'GENE' and r['label'] == 'LOI' and r['tail_type'] == 'MRK')]
    removed_a2 += orig - len(item['relations'])
print(f"  删除 GENE-LOI-MRK: {removed_a2}条")
save_submission(data_a2, 'submit_v44_del_gene_loi_mrk')

# ============================================================
# 路径A3：同时删除 VAR-CON-CROSS + GENE-LOI-MRK（共9条）
# ============================================================
print("\n=== 路径A3：删除 VAR-CON-CROSS + GENE-LOI-MRK（共9条）===")
data_a3 = copy.deepcopy(base)
removed_a3 = 0
for item in data_a3:
    orig = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', [])
                         if not (r['head_type'] == 'VAR' and r['label'] == 'CON' and r['tail_type'] == 'CROSS')
                         and not (r['head_type'] == 'GENE' and r['label'] == 'LOI' and r['tail_type'] == 'MRK')]
    removed_a3 += orig - len(item['relations'])
print(f"  删除: {removed_a3}条")
save_submission(data_a3, 'submit_v44_del_direction_errors')

# ============================================================
# 路径B：删除训练集频次<3的高风险类型
# 包括：GENE-LOI-MRK(5条,训练2), GENE-CON-TRT(4条,训练1), 
#        QTL-AFF-BIS(3条,训练1), VAR-OCI-GST(2条,训练1), GENE-LOI-CROP(1条,训练2)
# ============================================================
print("\n=== 路径B：删除训练集频次<3的高风险类型 ===")
HIGH_RISK_TYPES = {
    ('GENE', 'LOI', 'MRK'),   # 底座5条，训练集2条（且方向可能错）
    ('GENE', 'CON', 'TRT'),   # 底座4条，训练集1条
    ('QTL', 'AFF', 'BIS'),    # 底座3条，训练集1条
    ('VAR', 'OCI', 'GST'),    # 底座2条，训练集1条
    ('BM', 'AFF', 'GENE'),    # 底座2条，训练集2条
    ('GENE', 'LOI', 'CROP'),  # 底座1条，训练集2条
    ('BIS', 'CON', 'BIS'),    # 底座1条，训练集2条
}

data_b = copy.deepcopy(base)
removed_b = Counter()
for item in data_b:
    orig_rels = item.get('relations', [])
    new_rels = []
    for r in orig_rels:
        key = (r['head_type'], r['label'], r['tail_type'])
        if key in HIGH_RISK_TYPES:
            removed_b[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels

total_b = sum(removed_b.values())
print(f"  删除高风险类型: {total_b}条")
for t, c in removed_b.most_common():
    print(f"    {t}: {c}条")
save_submission(data_b, 'submit_v44_del_high_risk_types')

# ============================================================
# 路径C：路径A3 + 路径B（最全面的清理）
# ============================================================
print("\n=== 路径C：方向修正 + 高风险清除（组合）===")
data_c = copy.deepcopy(base)
removed_c = Counter()
for item in data_c:
    orig_rels = item.get('relations', [])
    new_rels = []
    for r in orig_rels:
        key = (r['head_type'], r['label'], r['tail_type'])
        # 方向错误
        if key == ('VAR', 'CON', 'CROSS') or key == ('GENE', 'LOI', 'MRK'):
            removed_c[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
        # 高风险类型（排除已删的）
        elif key in HIGH_RISK_TYPES - {('GENE', 'LOI', 'MRK')}:
            removed_c[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels

total_c = sum(removed_c.values())
print(f"  删除: {total_c}条")
for t, c in removed_c.most_common():
    print(f"    {t}: {c}条")
save_submission(data_c, 'submit_v44_direction_plus_risk')

# ============================================================
# 路径D：在底座基础上，把 VAR-CON-CROSS 改为 CROSS-CON-VAR（方向修正+重新添加）
# ============================================================
print("\n=== 路径D：VAR-CON-CROSS → CROSS-CON-VAR（方向修正）===")
data_d = copy.deepcopy(base)
fixed_d = 0
for idx, item in enumerate(data_d):
    new_rels = []
    for r in item.get('relations', []):
        if r['head_type'] == 'VAR' and r['label'] == 'CON' and r['tail_type'] == 'CROSS':
            # 交换 head 和 tail
            new_r = copy.deepcopy(r)
            new_r['head'] = r['tail']
            new_r['head_type'] = r['tail_type']
            new_r['head_start'] = r['tail_start']
            new_r['head_end'] = r['tail_end']
            new_r['tail'] = r['head']
            new_r['tail_type'] = r['head_type']
            new_r['tail_start'] = r['head_start']
            new_r['tail_end'] = r['head_end']
            new_rels.append(new_r)
            fixed_d += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels

print(f"  方向修正: {fixed_d}条 VAR-CON-CROSS → CROSS-CON-VAR")
save_submission(data_d, 'submit_v44_fix_cross_direction')

# ============================================================
# 路径E：路径D（方向修正）+ 删除 GENE-LOI-MRK + 删除高风险类型
# ============================================================
print("\n=== 路径E：全面修正（方向修正+删高风险）===")
data_e = copy.deepcopy(data_d)  # 基于已修正方向的版本
removed_e = Counter()
for item in data_e:
    orig_rels = item.get('relations', [])
    new_rels = []
    for r in orig_rels:
        key = (r['head_type'], r['label'], r['tail_type'])
        if key == ('GENE', 'LOI', 'MRK') or key in HIGH_RISK_TYPES - {('GENE', 'LOI', 'MRK')}:
            removed_e[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels

total_e = sum(removed_e.values())
print(f"  额外删除: {total_e}条")
for t, c in removed_e.most_common():
    print(f"    {t}: {c}条")
save_submission(data_e, 'submit_v44_full_correction')

print("\n=== 生成完成 ===")
print("推荐提交顺序:")
print("1. submit_v44_del_var_con_cross  (只删4条方向错误，风险最低)")
print("2. submit_v44_fix_cross_direction (方向修正为CROSS-CON-VAR，净变化0条)")
print("3. submit_v44_del_direction_errors (删9条方向错误)")
print("4. submit_v44_del_high_risk_types (删训练集极低频类型)")
print("5. submit_v44_full_correction (全面修正)")
