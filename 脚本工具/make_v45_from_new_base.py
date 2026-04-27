"""
v45 冲榜脚本
新底座：submit_v44_del_var_con_cross（得分 0.4514，+0.0004）
策略：在新底座基础上继续优化

已验证有效的方向：
  - VAR-CON-CROSS 方向错误 → 删除涨分 ✅

待验证的方向（按优先级）：
  A. GENE-LOI-MRK 方向错误（5条，训练集MRK-LOI-GENE=22条）
  B. 训练集极低频假阳性清除（GENE-CON-TRT=4条, QTL-AFF-BIS=3条等）
  C. 方向修正：VAR-CON-CROSS → CROSS-CON-VAR（净变化0，但修正方向）
  D. GENE-LOI-MRK → MRK-LOI-GENE（方向修正）
  E. 组合：A + B
  F. 组合：C + A（修正CROSS方向 + 删GENE-LOI-MRK）
"""

import json
import copy
import zipfile
from collections import Counter

NEW_BASE_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v44_del_var_con_cross.json'
OUTPUT_DIR = '/home/ubuntu/bisai/数据/A榜'

with open(NEW_BASE_PATH) as f:
    base = json.load(f)
with open('/home/ubuntu/bisai/数据/官方原始数据/test_A.json') as f:
    test_a = json.load(f)
with open('/home/ubuntu/bisai/数据/官方原始数据/train.json') as f:
    train = json.load(f)

def save_submission(data, name):
    json_path = f"{OUTPUT_DIR}/{name}.json"
    zip_path = f"{OUTPUT_DIR}/{name}.zip"
    with open(json_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(json_path, 'submit.json')
    n_rel = sum(len(item.get('relations', [])) for item in data)
    n_no_rel = sum(1 for item in data if not item.get('relations'))
    print(f"  {name}: {n_rel}条关系, 均值{n_rel/len(data):.2f}, 无关系{n_no_rel}({n_no_rel/len(data)*100:.1f}%)")
    return json_path

base_rel_total = sum(len(item.get('relations', [])) for item in base)
print(f"新底座(0.4514): {base_rel_total}条关系, 均值{base_rel_total/len(base):.2f}")
print()

# 统计新底座中各类型数量
base_type_count = Counter()
for item in base:
    for r in item.get('relations', []):
        base_type_count[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1

# 训练集类型频次
train_type_count = Counter()
for item in train:
    for r in item.get('relations', []):
        train_type_count[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1

print("新底座中各类型分布（与训练集对比）：")
for t, c in base_type_count.most_common():
    tc = train_type_count.get(t, 0)
    flag = "⚠️ 高风险" if tc < 5 else ""
    print(f"  {t}: 底座{c}条, 训练集{tc}条 {flag}")

# ============================================================
# 路径A：只删 GENE-LOI-MRK（5条，方向错误）
# ============================================================
print("\n=== 路径A：删除 GENE-LOI-MRK（5条，方向错误）===")
data_a = copy.deepcopy(base)
removed_a = 0
for item in data_a:
    orig = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', [])
                         if not (r['head_type'] == 'GENE' and r['label'] == 'LOI' and r['tail_type'] == 'MRK')]
    removed_a += orig - len(item['relations'])
print(f"  删除: {removed_a}条")
save_submission(data_a, 'submit_v45_del_gene_loi_mrk')

# ============================================================
# 路径B：删除训练集频次<3的高风险类型（不含GENE-LOI-MRK，单独测试）
# ============================================================
print("\n=== 路径B：删除训练集频次<3的高风险类型（排除GENE-LOI-MRK）===")
HIGH_RISK_TYPES = {
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
    new_rels = []
    for r in item.get('relations', []):
        key = (r['head_type'], r['label'], r['tail_type'])
        if key in HIGH_RISK_TYPES:
            removed_b[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels
print(f"  删除: {sum(removed_b.values())}条")
for t, c in removed_b.most_common():
    print(f"    {t}: {c}条")
save_submission(data_b, 'submit_v45_del_low_freq_types')

# ============================================================
# 路径C：方向修正 VAR-CON-CROSS → CROSS-CON-VAR
# 注意：新底座已删除了VAR-CON-CROSS，这里要从原底座重建
# 实际上：新底座 = 原底座 - VAR-CON-CROSS
# 方向修正 = 新底座 + CROSS-CON-VAR（把删掉的4条改方向加回来）
# ============================================================
print("\n=== 路径C：把已删的VAR-CON-CROSS改为CROSS-CON-VAR加回来 ===")
# 先从原底座找到这4条关系
with open('/home/ubuntu/bisai/数据/A榜/submit_v41_sub_conservative.json') as f:
    orig_base = json.load(f)

data_c = copy.deepcopy(base)
added_c = 0
for idx, (orig_item, new_item) in enumerate(zip(orig_base, data_c)):
    for r in orig_item.get('relations', []):
        if r['head_type'] == 'VAR' and r['label'] == 'CON' and r['tail_type'] == 'CROSS':
            # 方向修正：VAR-CON-CROSS → CROSS-CON-VAR
            new_r = copy.deepcopy(r)
            new_r['head'] = r['tail']
            new_r['head_type'] = r['tail_type']
            new_r['head_start'] = r['tail_start']
            new_r['head_end'] = r['tail_end']
            new_r['tail'] = r['head']
            new_r['tail_type'] = r['head_type']
            new_r['tail_start'] = r['head_start']
            new_r['tail_end'] = r['head_end']
            new_item['relations'].append(new_r)
            added_c += 1
print(f"  添加修正后的 CROSS-CON-VAR: {added_c}条")
save_submission(data_c, 'submit_v45_fix_cross_con_var')

# ============================================================
# 路径D：路径A + 路径B（删GENE-LOI-MRK + 删低频类型）
# ============================================================
print("\n=== 路径D：A+B 组合（删GENE-LOI-MRK + 删低频类型）===")
data_d = copy.deepcopy(base)
removed_d = Counter()
for item in data_d:
    new_rels = []
    for r in item.get('relations', []):
        key = (r['head_type'], r['label'], r['tail_type'])
        if key == ('GENE', 'LOI', 'MRK') or key in HIGH_RISK_TYPES:
            removed_d[f"{r['head_type']}-{r['label']}-{r['tail_type']}"] += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels
print(f"  删除: {sum(removed_d.values())}条")
for t, c in removed_d.most_common():
    print(f"    {t}: {c}条")
save_submission(data_d, 'submit_v45_del_all_risks')

# ============================================================
# 路径E：路径C（方向修正CROSS-CON-VAR）+ 路径A（删GENE-LOI-MRK）
# ============================================================
print("\n=== 路径E：方向修正CROSS-CON-VAR + 删GENE-LOI-MRK ===")
data_e = copy.deepcopy(data_c)  # 基于路径C
removed_e = 0
for item in data_e:
    orig = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', [])
                         if not (r['head_type'] == 'GENE' and r['label'] == 'LOI' and r['tail_type'] == 'MRK')]
    removed_e += orig - len(item['relations'])
print(f"  额外删除GENE-LOI-MRK: {removed_e}条")
save_submission(data_e, 'submit_v45_fix_cross_del_gene_mrk')

# ============================================================
# 路径F：MRK-LOI-GENE 方向修正（把GENE-LOI-MRK改为MRK-LOI-GENE）
# ============================================================
print("\n=== 路径F：GENE-LOI-MRK → MRK-LOI-GENE（方向修正）===")
data_f = copy.deepcopy(base)
fixed_f = 0
for item in data_f:
    new_rels = []
    for r in item.get('relations', []):
        if r['head_type'] == 'GENE' and r['label'] == 'LOI' and r['tail_type'] == 'MRK':
            # 方向修正
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
            fixed_f += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels
print(f"  方向修正: {fixed_f}条 GENE-LOI-MRK → MRK-LOI-GENE")
save_submission(data_f, 'submit_v45_fix_gene_mrk_direction')

# ============================================================
# 路径G：路径C + 路径F（两类方向都修正，净变化0）
# ============================================================
print("\n=== 路径G：两类方向全修正（VAR-CON-CROSS→CROSS-CON-VAR + GENE-LOI-MRK→MRK-LOI-GENE）===")
data_g = copy.deepcopy(data_c)  # 已修正CROSS方向
fixed_g = 0
for item in data_g:
    new_rels = []
    for r in item.get('relations', []):
        if r['head_type'] == 'GENE' and r['label'] == 'LOI' and r['tail_type'] == 'MRK':
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
            fixed_g += 1
        else:
            new_rels.append(r)
    item['relations'] = new_rels
print(f"  额外方向修正: {fixed_g}条 GENE-LOI-MRK → MRK-LOI-GENE")
save_submission(data_g, 'submit_v45_fix_both_directions')

print("\n=== 生成完成 ===")
print("\n推荐提交顺序（下一轮）:")
print("1. submit_v45_del_gene_loi_mrk      (只删5条方向错误，与v44同类型，涨分概率高)")
print("2. submit_v45_fix_gene_mrk_direction (GENE-LOI-MRK→MRK-LOI-GENE，净变化0)")
print("3. submit_v45_del_low_freq_types     (删13条低频假阳性)")
print("4. submit_v45_fix_cross_con_var      (把VAR-CON-CROSS改为CROSS-CON-VAR加回)")
print("5. submit_v45_del_all_risks          (删18条，全面清理)")
print("6. submit_v45_fix_both_directions    (两类方向全修正，净变化0)")
