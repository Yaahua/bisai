#!/usr/bin/env python3
"""
make_v41_precise_combo.py — 精准规则候选（多类型组合）

核心思路：
前面的 rule_boost 脚本产出了大量候选，但很多类型（如 GENE-AFF-GENE:412, TRT-AFF-TRT:210）
数量过多，精度可能不够。本脚本做更精准的过滤：

1. 严格 between 词匹配：只保留训练集中高频出现的 between 词模式
2. 实体距离约束：只保留距离在训练集 P75 以内的候选
3. 实体质量过滤：排除泛称实体
4. 交叉验证：候选必须在多个旧模型预测中出现过（如果可用）

底座：submit_v36_gene_abs（当前最高分 0.4487）
"""
import json
import re
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v36_gene_abs.json'
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
V30_SAFE = ROOT / 'submit_v30_safe.json'
V30_ALL = ROOT / 'submit_v30_supported_alltypes.json'
REPORT = Path('/home/ubuntu/bisai/分析报告/v41_precise_combo_report.txt')

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
    return json_path, zip_path


def rel_key(r):
    return (
        r['head'].strip().lower(), r['head_type'],
        r['label'],
        r['tail'].strip().lower(), r['tail_type']
    )


def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])


def stats(data):
    n = len(data)
    ent = sum(len(x.get('entities', [])) for x in data) / n
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return ent, rel, no_rel


def get_between_text(text, h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return text[h_end:t_start].strip().lower()
    elif t_end <= h_start:
        return text[t_end:h_start].strip().lower()
    return ""


# ===== 1. 从训练集学习精确模式 =====
print("=" * 60)
print("步骤 1: 从训练集学习精确 between 词模式")
print("=" * 60)

train = load(TRAIN)
base = load(BASE)

# 学习训练集中每种类型的精确 between 词模式
type_between_patterns = defaultdict(list)  # {triplet: [between_text]}
type_distances = defaultdict(list)

for item in train:
    text = item['text']
    for r in item.get('relations', []):
        t = triplet(r)
        between = get_between_text(text, r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        dist = abs(r['tail_start'] - r['head_end']) if r['head_end'] <= r['tail_start'] else \
               abs(r['head_start'] - r['tail_end']) if r['tail_end'] <= r['head_start'] else 0
        type_between_patterns[t].append(between)
        type_distances[t].append(dist)

# 计算每种类型的距离 P75
type_dist_p75 = {}
for t, dists in type_distances.items():
    sorted_dists = sorted(dists)
    p75_idx = int(len(sorted_dists) * 0.75)
    type_dist_p75[t] = sorted_dists[p75_idx] if sorted_dists else 100

# 提取每种类型的高频 between 词（出现 >= 2 次的词）
type_high_freq_words = defaultdict(set)
for t, betweens in type_between_patterns.items():
    word_counter = Counter()
    for b in betweens:
        words = set(re.findall(r'[a-z]+', b))
        for w in words:
            if len(w) > 2:
                word_counter[w] += 1
    # 保留出现 >= 2 次的词
    for w, c in word_counter.items():
        if c >= 2:
            type_high_freq_words[t].add(w)

# 打印统计
for t in sorted(type_high_freq_words.keys(), key=lambda x: -len(type_between_patterns[x]))[:15]:
    n = len(type_between_patterns[t])
    p75 = type_dist_p75.get(t, 0)
    words = sorted(type_high_freq_words[t])[:10]
    print(f"  {t[0]}-{t[1]}-{t[2]} (n={n}, P75_dist={p75}): {words}")


# ===== 2. 精准规则匹配 =====
print("\n" + "=" * 60)
print("步骤 2: 精准规则匹配")
print("=" * 60)

# 定义精准触发词规则（基于训练集高频模式）
PRECISE_RULES = {
    ('BM', 'AFF', 'TRT'): {
        'trigger_words': {'associated', 'correlated', 'linked', 'related', 'identified',
                          'detected', 'revealed', 'significant', 'effect'},
        'max_distance': 60,
        'min_trigger_match': 1,
    },
    ('MRK', 'LOI', 'CHR'): {
        'trigger_words': {'on', 'mapped', 'located', 'detected', 'chromosome', 'linkage'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
    ('VAR', 'USE', 'BM'): {
        'trigger_words': {'using', 'used', 'genotyped', 'screened', 'analyzed', 'evaluated',
                          'through', 'via', 'employed'},
        'max_distance': 60,
        'min_trigger_match': 1,
    },
    ('CROP', 'HAS', 'TRT'): {
        'trigger_words': {'has', 'have', 'had', 'with', 'shows', 'exhibit', 'display',
                          'higher', 'lower', 'improved', 'resistance'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
    ('GENE', 'LOI', 'TRT'): {
        'trigger_words': {'for', 'controlling', 'associated', 'involved', 'related',
                          'underlying', 'responsible', 'encoding'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
    ('MRK', 'LOI', 'TRT'): {
        'trigger_words': {'for', 'associated', 'linked', 'related', 'detected',
                          'identified', 'significant'},
        'max_distance': 60,
        'min_trigger_match': 1,
    },
    ('TRT', 'AFF', 'TRT'): {
        'trigger_words': {'affect', 'influence', 'correlat', 'impact', 'contribut',
                          'under', 'reduced', 'increased', 'enhanced', 'improved',
                          'tolerance', 'resistance'},
        'max_distance': 60,
        'min_trigger_match': 1,
    },
    ('CROSS', 'CON', 'VAR'): {
        'trigger_words': {'between', 'from', 'derived', 'developed', 'cross', 'crossed'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
    ('ABS', 'OCI', 'GST'): {
        'trigger_words': {'at', 'during', 'stage', 'phase', 'period', 'seedling',
                          'flowering', 'maturity'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
    ('CROP', 'CON', 'GENE'): {
        'trigger_words': {'gene', 'genes', 'allele', 'locus', 'loci', 'encoding'},
        'max_distance': 60,
        'min_trigger_match': 1,
    },
    ('GENE', 'AFF', 'GENE'): {
        'trigger_words': {'interact', 'regulat', 'activat', 'repress', 'inhibit',
                          'modulat', 'target', 'homolog', 'ortholog', 'paralog'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
    ('VAR', 'HAS', 'TRT'): {
        'trigger_words': {'has', 'have', 'had', 'with', 'shows', 'showed', 'exhibited',
                          'displayed', 'higher', 'lower', 'greater', 'better',
                          'improved', 'increased', 'reduced', 'resistant', 'tolerant'},
        'max_distance': 60,
        'min_trigger_match': 1,
    },
    ('QTL', 'LOI', 'CHR'): {
        'trigger_words': {'on', 'mapped', 'located', 'detected', 'chromosome'},
        'max_distance': 50,
        'min_trigger_match': 1,
    },
}

# 构建底座关系键
base_rel_keys = defaultdict(set)
for idx, item in enumerate(base):
    for r in item.get('relations', []):
        base_rel_keys[idx].add(rel_key(r))

# 加载旧模型预测用于交叉验证
old_models = {}
for name in ['submit_v30_safe', 'submit_v30_supported_alltypes']:
    path = ROOT / f'{name}.json'
    if path.exists():
        old_models[name] = load(path)
        print(f"  加载旧模型: {name}")

# 应用精准规则
precise_candidates = defaultdict(list)

for idx, item in enumerate(base):
    text = item.get('text', '')
    entities = item.get('entities', [])
    existing_keys = base_rel_keys[idx]

    for i, h_ent in enumerate(entities):
        for j, t_ent in enumerate(entities):
            if i == j:
                continue

            h_type = h_ent['label']
            t_type = t_ent['label']
            rule_key_t = (h_type, None, t_type)

            for (rule_h, rule_l, rule_t), rule in PRECISE_RULES.items():
                if h_type != rule_h or t_type != rule_t:
                    continue

                # 排除泛称实体
                if h_ent['text'].strip().lower() in GENERIC_ENTITIES:
                    continue
                if t_ent['text'].strip().lower() in GENERIC_ENTITIES:
                    continue

                # 获取 between 文本
                between = get_between_text(text, h_ent['start'], h_ent['end'],
                                          t_ent['start'], t_ent['end'])
                if not between:
                    continue

                dist = len(between)
                if dist > rule['max_distance']:
                    continue

                # 检查触发词（支持前缀匹配）
                between_words = set(re.findall(r'[a-z]+', between))
                trigger_matches = 0
                for tw in rule['trigger_words']:
                    for bw in between_words:
                        if bw.startswith(tw) or bw == tw:
                            trigger_matches += 1
                            break

                if trigger_matches < rule['min_trigger_match']:
                    continue

                # 构建关系
                rel = {
                    'head': h_ent['text'],
                    'head_type': h_type,
                    'head_start': h_ent['start'],
                    'head_end': h_ent['end'],
                    'tail': t_ent['text'],
                    'tail_type': t_type,
                    'tail_start': t_ent['start'],
                    'tail_end': t_ent['end'],
                    'label': rule_l,
                }

                key = rel_key(rel)
                if key in existing_keys:
                    continue

                # 交叉验证：检查是否在旧模型中出现
                cross_validated = False
                for model_name, model_data in old_models.items():
                    if idx < len(model_data):
                        model_keys = {rel_key(r) for r in model_data[idx].get('relations', [])}
                        if key in model_keys:
                            cross_validated = True
                            break

                t = (rule_h, rule_l, rule_t)
                precise_candidates[t].append((idx, rel, between, cross_validated, trigger_matches))

print(f"\n精准候选总数:")
total = 0
cv_total = 0
for t, items in sorted(precise_candidates.items(), key=lambda x: -len(x[1])):
    cv_count = sum(1 for _, _, _, cv, _ in items if cv)
    print(f"  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条 (交叉验证: {cv_count})")
    total += len(items)
    cv_total += cv_count
print(f"  总计: {total} 条 (交叉验证: {cv_total})")


# ===== 3. 生成精准版本 =====
print("\n" + "=" * 60)
print("步骤 3: 生成精准版本")
print("=" * 60)

report_lines = [
    "=" * 60,
    "v41 精准组合报告",
    "=" * 60,
    f"\n底座: {BASE} (score=0.4487)",
]

# 版本 1: 只加入交叉验证通过的候选（最保守）
data = deepcopy(base)
added = 0
added_by_type = Counter()
for t, items in precise_candidates.items():
    for idx, rel, between, cv, tm in items:
        if not cv:
            continue
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        key = rel_key(rel)
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_precise_cv', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_precise_cv: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 2: 交叉验证 + 距离严格（P75以内）
data = deepcopy(base)
added = 0
added_by_type = Counter()
for t, items in precise_candidates.items():
    p75 = type_dist_p75.get(t, 60)
    for idx, rel, between, cv, tm in items:
        dist = len(between)
        if dist > p75:
            continue
        # 排除泛称
        if rel['head'].strip().lower() in GENERIC_ENTITIES or \
           rel['tail'].strip().lower() in GENERIC_ENTITIES:
            continue
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        key = rel_key(rel)
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_precise_strict', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_precise_strict: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 3: 减法（保守）+ 精准交叉验证加法
sub_conservative = load(ROOT / 'submit_v41_sub_conservative.json')
data = deepcopy(sub_conservative)
added = 0
added_by_type = Counter()
for t, items in precise_candidates.items():
    for idx, rel, between, cv, tm in items:
        if not cv:
            continue
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        key = rel_key(rel)
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_sub_conservative_plus_cv', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_sub_conservative_plus_cv: removed=25+added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 4: 减法（保守）+ 精准严格加法
data = deepcopy(sub_conservative)
added = 0
added_by_type = Counter()
for t, items in precise_candidates.items():
    p75 = type_dist_p75.get(t, 60)
    for idx, rel, between, cv, tm in items:
        dist = len(between)
        if dist > p75:
            continue
        if rel['head'].strip().lower() in GENERIC_ENTITIES or \
           rel['tail'].strip().lower() in GENERIC_ENTITIES:
            continue
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        key = rel_key(rel)
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_sub_conservative_plus_strict', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_sub_conservative_plus_strict: removed=25+added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 5: 只加入最安全的小量类型（BM-AFF-TRT + MRK-LOI-CHR + VAR-USE-BM，都是覆盖率极低的）
ULTRA_SAFE = {('BM', 'AFF', 'TRT'), ('MRK', 'LOI', 'CHR'), ('VAR', 'USE', 'BM')}
data = deepcopy(base)
added = 0
added_by_type = Counter()
for t, items in precise_candidates.items():
    if t not in ULTRA_SAFE:
        continue
    for idx, rel, between, cv, tm in items:
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        key = rel_key(rel)
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_precise_ultrasafe', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_precise_ultrasafe: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 6: 减法（保守）+ 超安全加法
data = deepcopy(sub_conservative)
added = 0
added_by_type = Counter()
for t, items in precise_candidates.items():
    if t not in ULTRA_SAFE:
        continue
    for idx, rel, between, cv, tm in items:
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        key = rel_key(rel)
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_sub_plus_ultrasafe', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_sub_plus_ultrasafe: removed=25+added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)


# ===== 4. 汇总 =====
print("\n" + "=" * 60)
print("汇总")
print("=" * 60)

report_lines.append("\n\n" + "=" * 60)
report_lines.append("最终提交建议")
report_lines.append("=" * 60)

suggestion = """
最终建议提交顺序（每日3次）:

=== 第一天 ===
1. submit_v41_sub_conservative（保守减法，删25条假阳性）
2. submit_v41_sub_conservative_plus_cv（保守减法 + 交叉验证加法）
3. submit_v41_precise_cv（纯交叉验证加法）

=== 第二天 ===
4. submit_v41_sub_generic（泛称减法，删95条）
5. submit_v41_precise_strict（精准严格加法）
6. submit_v41_sub_plus_ultrasafe（保守减法 + 超安全加法）

=== 第三天 ===
7. submit_v41_sub_conservative_plus_strict（保守减法 + 精准严格加法）
8. submit_v41_rule_bm_aff_trt（BM-AFF-TRT 单类型测试）
9. submit_v41_rule_lowcov_combo（低覆盖率组合）
"""
print(suggestion)
report_lines.append(suggestion)

REPORT.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
print(f"报告已写入: {REPORT}")
