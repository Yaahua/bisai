"""
v40 系列：基于深度分析的新策略
关键发现：
- ABS-AFF-GENE 覆盖率78%，加33条后涨分 → 规则精度高
- GENE-AFF-TRT 覆盖率49%，加22条后掉分 → 规则精度低
- QTL-LOI-TRT 覆盖率55%，加55条后掉分 → 规则精度低
- CROP-CON-VAR 覆盖率31%，加17条后掉分 → 规则精度低（泛称问题）

新策略：
1. 在 ABS-AFF-GENE 方向继续挖掘（覆盖率78%，缺口20条）
2. 探索 TRT-OCI-GST（覆盖率70%，缺口13条）
3. 探索 VAR-HAS-TRT（覆盖率49%，缺口169条）—— 数量最大，但需要高精度规则
4. 探索 ABS-AFF-TRT（覆盖率57%，缺口122条）—— 数量大
"""

import json
import zipfile
from collections import Counter, defaultdict

BASE_DIR = '/home/ubuntu/bisai'

with open(f'{BASE_DIR}/数据/官方原始数据/train.json') as f:
    train = json.load(f)
with open(f'{BASE_DIR}/数据/A榜/submit_v36_gene_abs.json') as f:
    best = json.load(f)
with open(f'{BASE_DIR}/数据/A榜/submit_v30_safe.json') as f:
    safe = json.load(f)

# 训练集类型频次
train_types = Counter()
for item in train:
    for r in item.get('relations', []):
        full = f"{r['head_type']}-{r['label']}-{r['tail_type']}"
        train_types[full] += 1

# 当前底座关系集合
best_rels_set = set()
for i, item in enumerate(best):
    for r in item.get('relations', []):
        full = f"{r.get('head_type','')}-{r.get('label','')}-{r.get('tail_type','')}"
        key = (i, r.get('head','').lower(), full, r.get('tail','').lower())
        best_rels_set.add(key)

# safe 候选池（safe 有但 best 没有）
safe_candidates = defaultdict(list)
for i, item in enumerate(safe):
    for r in item.get('relations', []):
        full = f"{r.get('head_type','')}-{r.get('label','')}-{r.get('tail_type','')}"
        key = (i, r.get('head','').lower(), full, r.get('tail','').lower())
        if key not in best_rels_set:
            safe_candidates[full].append({
                'idx': i, 'head': r['head'], 'tail': r['tail'],
                'head_type': r.get('head_type',''), 'tail_type': r.get('tail_type',''),
                'label': r.get('label','')
            })

print('=== safe 候选池（safe 有但 best 没有）===')
for t, cands in sorted(safe_candidates.items(), key=lambda x: -len(x[1])):
    print(f'  {t}: {len(cands)} 条  (训练集: {train_types.get(t, 0)})')

# 加载 v30_supported_alltypes（双重背书）
import os
allx_path = f'{BASE_DIR}/数据/A榜/submit_v30_supported_alltypes.json'
if os.path.exists(allx_path):
    with open(allx_path) as f:
        allx = json.load(f)
    allx_rels_set = set()
    for i, item in enumerate(allx):
        for r in item.get('relations', []):
            full = f"{r.get('head_type','')}-{r.get('label','')}-{r.get('tail_type','')}"
            key = (i, r.get('head','').lower(), full, r.get('tail','').lower())
            allx_rels_set.add(key)

    double_backed = defaultdict(list)
    for t, cands in safe_candidates.items():
        for c in cands:
            key = (c['idx'], c['head'].lower(), t, c['tail'].lower())
            if key in allx_rels_set:
                double_backed[t].append(c)

    print('\n=== 双重背书候选（safe + allx，但 best 没有）===')
    for t, cands in sorted(double_backed.items(), key=lambda x: -len(x[1])):
        print(f'  {t}: {len(cands)} 条  (训练集: {train_types.get(t, 0)})')
        for c in cands[:3]:
            print(f'    [{c["head"]}] -> [{c["tail"]}]')
else:
    print('v30_supported_alltypes 不存在，只用 safe 单背书')
    double_backed = safe_candidates

# ─── 生成候选版本 ─────────────────────────────────────────────────────────────
def build_version(type_list, name_suffix):
    """从双重背书候选中选取指定类型，添加到底座"""
    new_sub = [dict(item) for item in best]
    for item in new_sub:
        item['relations'] = list(item.get('relations', []))

    added = 0
    type_counts = Counter()
    current_best_set = set(best_rels_set)

    for t in type_list:
        for c in double_backed.get(t, []):
            key = (c['idx'], c['head'].lower(), t, c['tail'].lower())
            if key not in current_best_set:
                new_rel = {
                    'head': c['head'],
                    'head_type': c['head_type'],
                    'head_start': 0,
                    'head_end': 0,
                    'tail': c['tail'],
                    'tail_type': c['tail_type'],
                    'tail_start': 0,
                    'tail_end': 0,
                    'label': c['label'],
                }
                new_sub[c['idx']]['relations'].append(new_rel)
                current_best_set.add(key)
                added += 1
                type_counts[t] += 1

    out_json = f'{BASE_DIR}/数据/A榜/submit_{name_suffix}.json'
    out_zip = f'{BASE_DIR}/数据/A榜/submit_{name_suffix}.zip'
    with open(out_json, 'w') as f:
        json.dump(new_sub, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(out_json, f'submit_{name_suffix}.json')

    total_rels = sum(len(item.get('relations', [])) for item in new_sub)
    avg_rels = total_rels / len(new_sub)
    print(f'\n[{name_suffix}]')
    print(f'  新增: {added} 条，类型: {dict(type_counts)}')
    print(f'  总关系: {total_rels}，均值: {avg_rels:.2f}')
    print(f'  文件: {out_zip}')

print('\n=== 生成 v40 系列 ===')

# v40_trt_oci: TRT-OCI-GST（覆盖率70%，缺口13）
build_version(['TRT-OCI-GST'], 'v40_trt_oci')

# v40_abs_trt: ABS-AFF-TRT（覆盖率57%，缺口122）—— 用双重背书过滤
build_version(['ABS-AFF-TRT'], 'v40_abs_trt')

# v40_var_has: VAR-HAS-TRT（覆盖率49%，缺口169）—— 用双重背书过滤
build_version(['VAR-HAS-TRT'], 'v40_var_has')

# v40_abs_gene_plus: ABS-AFF-GENE 继续加（覆盖率78%，缺口20）—— 只用 safe 单背书
build_version(['ABS-AFF-GENE'], 'v40_abs_gene_plus')

# v40_trt_var_combo: TRT-OCI-GST + ABS-AFF-TRT 组合
build_version(['TRT-OCI-GST', 'ABS-AFF-TRT'], 'v40_trt_var_combo')

# v40_abs_trt_gene: ABS-AFF-TRT + ABS-AFF-GENE 组合
build_version(['ABS-AFF-TRT', 'ABS-AFF-GENE'], 'v40_abs_trt_gene')

print('\n全部完成！')
