#!/usr/bin/env python3
"""
make_v43_targeted_subtract.py — 基于深度分析的精准减法策略

关键发现：
- 底座 0.4510（submit_v41_sub_conservative）
- 第一名 0.4560，差距 0.0050
- v41_sub_conservative 已删除 score≥4 的 25 条（涨 +0.0023）
- 现在分析更多可疑类型：TRT-OCI-GST(38.7%超距)、MRK-LOI-TRT(31.8%)、GENE-CON-GENE(35.3%)、TRT-AFF-TRT(33.3%)

策略：
1. v43_sub_trt_oci_gst：删除 TRT-OCI-GST 中高风险关系（score≥2）
2. v43_sub_mrk_loi_trt：删除 MRK-LOI-TRT 中泛称marker关系
3. v43_sub_trt_aff_trt：删除 TRT-AFF-TRT 中高风险关系
4. v43_sub_combined：组合删除（三类型高风险均删）
5. v43_sub_gene_con_gene：删除 GENE-CON-GENE 中高风险关系
"""
import json
import re
import zipfile
import statistics
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v41_sub_conservative.json'  # 底座 0.4510
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')

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
    print(f"  已保存: {json_path.name} + {zip_path.name}")
    return json_path, zip_path

def rel_key(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])

def get_between_text(text, h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return text[h_end:t_start].strip().lower()
    elif t_end <= h_start:
        return text[t_end:h_start].strip().lower()
    return ""

def stats(data):
    n = len(data)
    total = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    return total, total / n, no_rel, no_rel / n * 100

print("加载数据...")
train = load(TRAIN)
base = load(BASE)
base_total, base_avg, base_no_rel, base_no_rel_pct = stats(base)
print(f"底座 (0.4510): rels={base_total}, avg={base_avg:.2f}, no_rel={base_no_rel}({base_no_rel_pct:.1f}%)")

# ===== 分析训练集中各类型的距离分布 =====
train_dists = defaultdict(list)
train_between_words = defaultdict(Counter)
for item in train:
    text = item.get('text', '')
    for r in item.get('relations', []):
        t = triplet(r)
        dist = abs(r.get('head_start', 0) - r.get('tail_start', 0))
        train_dists[t].append(dist)
        between = get_between_text(text, r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        words = re.findall(r'\b[a-z]{3,}\b', between)
        for w in words:
            train_between_words[t][w] += 1

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

def compute_suspicion_score(r, text, t, train_dists, train_between_words):
    """计算关系的可疑分数"""
    score = 0
    dist = abs(r.get('head_start', 0) - r.get('tail_start', 0))
    between = get_between_text(text, r['head_start'], r['head_end'],
                               r['tail_start'], r['tail_end'])
    
    if t in train_dists and train_dists[t]:
        dists = sorted(train_dists[t])
        p75 = dists[int(len(dists)*0.75)]
        p90 = dists[int(len(dists)*0.90)]
        if dist > p90:
            score += 2
        elif dist > p75:
            score += 1
    
    # between 词不匹配
    if t in train_between_words and train_between_words[t]:
        top_words = {w for w, c in train_between_words[t].most_common(30)}
        between_words = set(re.findall(r'\b[a-z]{3,}\b', between))
        if between_words:
            overlap = between_words & top_words
            overlap_ratio = len(overlap) / len(between_words)
            if overlap_ratio < 0.2:
                score += 2
            elif overlap_ratio < 0.4:
                score += 1
    
    # 泛称实体
    if is_generic(r['head']) or is_generic(r['tail']):
        score += 2
    
    # 实体文本过短
    if len(r['head'].strip()) <= 2 and t[0] not in ('CHR',):
        score += 1
    if len(r['tail'].strip()) <= 2 and t[2] not in ('CHR',):
        score += 1
    
    return score, dist, between

# ===== 策略 1：删除 TRT-OCI-GST 高风险关系 =====
print("\n" + "="*60)
print("策略 1: 删除 TRT-OCI-GST 高风险关系（score≥2）")
print("="*60)

ft = ('TRT', 'OCI', 'GST')
to_delete_trt_oci = []
for idx, item in enumerate(base):
    text = item.get('text', '')
    for r in item.get('relations', []):
        if triplet(r) == ft:
            score, dist, between = compute_suspicion_score(r, text, ft, train_dists, train_between_words)
            if score >= 2:
                to_delete_trt_oci.append((idx, rel_key(r), score, r['head'], r['tail'], between[:60]))
                print(f"  score={score} [{r['head']}] → [{r['tail']}] | dist={dist} | between='{between[:50]}'")

print(f"共找到 {len(to_delete_trt_oci)} 条高风险 TRT-OCI-GST 关系")

data = deepcopy(base)
deleted = 0
for idx, key, score, h, t_ent, between in to_delete_trt_oci:
    item = data[idx]
    orig_len = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', []) if rel_key(r) != key]
    deleted += orig_len - len(item['relations'])

save_json_zip('submit_v43_sub_trt_oci_gst', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v43_sub_trt_oci_gst: deleted={deleted}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 策略 2：删除 MRK-LOI-TRT 中泛称marker关系 =====
print("\n" + "="*60)
print("策略 2: 删除 MRK-LOI-TRT 中泛称marker关系（head为泛称或score≥3）")
print("="*60)

ft = ('MRK', 'LOI', 'TRT')
to_delete_mrk = []
for idx, item in enumerate(base):
    text = item.get('text', '')
    for r in item.get('relations', []):
        if triplet(r) == ft:
            score, dist, between = compute_suspicion_score(r, text, ft, train_dists, train_between_words)
            # 只删泛称或高分
            if is_generic(r['head']) or score >= 3:
                to_delete_mrk.append((idx, rel_key(r), score, r['head'], r['tail'], between[:60]))
                print(f"  score={score} generic={is_generic(r['head'])} [{r['head']}] → [{r['tail']}] | dist={dist} | between='{between[:50]}'")

print(f"共找到 {len(to_delete_mrk)} 条高风险 MRK-LOI-TRT 关系")

data = deepcopy(base)
deleted = 0
for idx, key, score, h, t_ent, between in to_delete_mrk:
    item = data[idx]
    orig_len = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', []) if rel_key(r) != key]
    deleted += orig_len - len(item['relations'])

save_json_zip('submit_v43_sub_mrk_loi_trt', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v43_sub_mrk_loi_trt: deleted={deleted}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 策略 3：删除 TRT-AFF-TRT 高风险关系 =====
print("\n" + "="*60)
print("策略 3: 删除 TRT-AFF-TRT 高风险关系（score≥2）")
print("="*60)

ft = ('TRT', 'AFF', 'TRT')
to_delete_trt_aff = []
for idx, item in enumerate(base):
    text = item.get('text', '')
    for r in item.get('relations', []):
        if triplet(r) == ft:
            score, dist, between = compute_suspicion_score(r, text, ft, train_dists, train_between_words)
            if score >= 2:
                to_delete_trt_aff.append((idx, rel_key(r), score, r['head'], r['tail'], between[:60]))
                print(f"  score={score} [{r['head']}] → [{r['tail']}] | dist={dist} | between='{between[:50]}'")

print(f"共找到 {len(to_delete_trt_aff)} 条高风险 TRT-AFF-TRT 关系")

data = deepcopy(base)
deleted = 0
for idx, key, score, h, t_ent, between in to_delete_trt_aff:
    item = data[idx]
    orig_len = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', []) if rel_key(r) != key]
    deleted += orig_len - len(item['relations'])

save_json_zip('submit_v43_sub_trt_aff_trt', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v43_sub_trt_aff_trt: deleted={deleted}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 策略 4：组合删除（三类型高风险均删） =====
print("\n" + "="*60)
print("策略 4: 组合删除（TRT-OCI-GST + MRK-LOI-TRT + TRT-AFF-TRT）")
print("="*60)

all_to_delete = {}  # idx -> set of keys
for idx, key, score, h, t_ent, between in to_delete_trt_oci + to_delete_mrk + to_delete_trt_aff:
    if idx not in all_to_delete:
        all_to_delete[idx] = set()
    all_to_delete[idx].add(key)

data = deepcopy(base)
deleted = 0
for idx, keys in all_to_delete.items():
    item = data[idx]
    orig_len = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', []) if rel_key(r) not in keys]
    deleted += orig_len - len(item['relations'])

save_json_zip('submit_v43_sub_combined', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v43_sub_combined: deleted={deleted}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 策略 5：删除 GENE-CON-GENE 高风险关系 =====
print("\n" + "="*60)
print("策略 5: 删除 GENE-CON-GENE 高风险关系（score≥2）")
print("="*60)

ft = ('GENE', 'CON', 'GENE')
to_delete_gene_con = []
for idx, item in enumerate(base):
    text = item.get('text', '')
    for r in item.get('relations', []):
        if triplet(r) == ft:
            score, dist, between = compute_suspicion_score(r, text, ft, train_dists, train_between_words)
            if score >= 2:
                to_delete_gene_con.append((idx, rel_key(r), score, r['head'], r['tail'], between[:60]))
                print(f"  score={score} [{r['head']}] → [{r['tail']}] | dist={dist} | between='{between[:50]}'")

print(f"共找到 {len(to_delete_gene_con)} 条高风险 GENE-CON-GENE 关系")

data = deepcopy(base)
deleted = 0
for idx, key, score, h, t_ent, between in to_delete_gene_con:
    item = data[idx]
    orig_len = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', []) if rel_key(r) != key]
    deleted += orig_len - len(item['relations'])

save_json_zip('submit_v43_sub_gene_con_gene', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v43_sub_gene_con_gene: deleted={deleted}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 策略 6：全类型高风险组合（score≥2 的所有类型） =====
print("\n" + "="*60)
print("策略 6: 全类型高风险组合（所有类型中 score≥3 的关系）")
print("="*60)

all_types = set(triplet(r) for item in base for r in item.get('relations', []))
to_delete_all = {}  # idx -> set of keys
count_by_type = Counter()

for idx, item in enumerate(base):
    text = item.get('text', '')
    for r in item.get('relations', []):
        t = triplet(r)
        score, dist, between = compute_suspicion_score(r, text, t, train_dists, train_between_words)
        if score >= 3:
            if idx not in to_delete_all:
                to_delete_all[idx] = set()
            to_delete_all[idx].add(rel_key(r))
            count_by_type[f"{t[0]}-{t[1]}-{t[2]}"] += 1

print(f"按类型统计（score≥3）:")
for t, c in count_by_type.most_common():
    print(f"  {t}: {c}条")

data = deepcopy(base)
deleted = 0
for idx, keys in to_delete_all.items():
    item = data[idx]
    orig_len = len(item.get('relations', []))
    item['relations'] = [r for r in item.get('relations', []) if rel_key(r) not in keys]
    deleted += orig_len - len(item['relations'])

save_json_zip('submit_v43_sub_all_score3', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v43_sub_all_score3: deleted={deleted}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 汇总 =====
print("\n" + "="*60)
print("汇总：6个候选版本")
print("="*60)
versions = [
    'submit_v43_sub_trt_oci_gst',
    'submit_v43_sub_mrk_loi_trt',
    'submit_v43_sub_trt_aff_trt',
    'submit_v43_sub_combined',
    'submit_v43_sub_gene_con_gene',
    'submit_v43_sub_all_score3',
]
for name in versions:
    d = load(ROOT / f'{name}.json')
    total, avg, no_rel, no_rel_pct = stats(d)
    diff = total - base_total
    print(f"  {name}: rels={total}(diff={diff:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

print("""
推荐提交顺序：
1. submit_v43_sub_combined — 删除三类型高风险（TRT-OCI-GST+MRK-LOI-TRT+TRT-AFF-TRT），预期最优
2. submit_v43_sub_trt_oci_gst — 只删TRT-OCI-GST，超距比例最高(38.7%)
3. submit_v43_sub_mrk_loi_trt — 只删MRK-LOI-TRT泛称，风险低
""")
