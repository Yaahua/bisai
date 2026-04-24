#!/usr/bin/env python3
"""
make_v41_subtract.py — 减法策略：分析底座中可能的假阳性关系并生成删除候选

核心思路：
1. 分析训练集中每种关系类型的 between 词分布（两实体之间的文本特征）
2. 对底座中的每条关系，检查其 between 词是否匹配训练集模式
3. 找出 between 词不匹配的关系（可能是假阳性）
4. 结合多种信号（between 词、实体距离、实体边界模糊度）综合打分
5. 生成多个删除版本，测试是否涨分

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
TEST = Path('/home/ubuntu/bisai/数据/官方原始数据/test_A.json')
REPORT = Path('/home/ubuntu/bisai/分析报告/v41_subtract_report.txt')


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


def get_between_text(text, r):
    """获取两个实体之间的文本"""
    h_start = r.get('head_start', 0)
    h_end = r.get('head_end', 0)
    t_start = r.get('tail_start', 0)
    t_end = r.get('tail_end', 0)

    if h_end <= t_start:
        between = text[h_end:t_start].strip()
    elif t_end <= h_start:
        between = text[t_end:h_start].strip()
    else:
        between = ""
    return between.lower()


def get_entity_distance(r):
    """获取两个实体之间的字符距离"""
    h_start = r.get('head_start', 0)
    h_end = r.get('head_end', 0)
    t_start = r.get('tail_start', 0)
    t_end = r.get('tail_end', 0)

    if h_end <= t_start:
        return t_start - h_end
    elif t_end <= h_start:
        return h_start - t_end
    else:
        return 0


# ===== 1. 分析训练集 between 词模式 =====
print("=" * 60)
print("步骤 1: 分析训练集 between 词模式")
print("=" * 60)

train = load(TRAIN)
base = load(BASE)
test = load(TEST)

# 构建训练集 between 词库
train_between_words = defaultdict(Counter)  # {triplet_type: {between_word: count}}
train_between_patterns = defaultdict(list)  # {triplet_type: [between_text]}
train_distances = defaultdict(list)  # {triplet_type: [distance]}

for item in train:
    text = item['text']
    for r in item.get('relations', []):
        t = triplet(r)
        between = get_between_text(text, r)
        dist = get_entity_distance(r)
        train_between_patterns[t].append(between)
        train_distances[t].append(dist)
        # 提取关键词
        words = re.findall(r'[a-z]+', between)
        for w in words:
            train_between_words[t][w] += 1

# 打印每种类型的 top between 词
report_lines = ["=" * 60, "v41 减法策略分析报告", "=" * 60, ""]
report_lines.append("训练集 between 词模式（前10类型）:")
for t in sorted(train_between_words.keys(), key=lambda x: -sum(train_between_words[x].values()))[:15]:
    top_words = train_between_words[t].most_common(10)
    avg_dist = sum(train_distances[t]) / len(train_distances[t]) if train_distances[t] else 0
    max_dist = max(train_distances[t]) if train_distances[t] else 0
    line = f"\n  {t[0]}-{t[1]}-{t[2]} (n={len(train_between_patterns[t])}, avg_dist={avg_dist:.0f}, max_dist={max_dist}):"
    report_lines.append(line)
    print(line)
    for w, c in top_words:
        word_line = f"    '{w}': {c}"
        report_lines.append(word_line)
        print(word_line)


# ===== 2. 对底座中每条关系进行假阳性评分 =====
print("\n" + "=" * 60)
print("步骤 2: 对底座中每条关系进行假阳性评分")
print("=" * 60)

# 假阳性信号：
# 1. between 词不在训练集模式中
# 2. 实体距离异常（远超训练集平均）
# 3. 实体文本是泛称（如 "varieties", "genotypes", "genes" 等）
# 4. 关系类型覆盖率已经很高（不太需要更多）

GENERIC_ENTITIES = {
    'varieties', 'genotypes', 'genes', 'traits', 'markers', 'chromosomes',
    'qtls', 'cultivars', 'lines', 'accessions', 'populations', 'species',
    'breeding lines', 'reference set', 'inbred lines', 'landraces',
    'germplasm', 'strains', 'alleles', 'loci', 'snps', 'ssrs',
    'candidate genes', 'major genes', 'minor genes',
    'these', 'those', 'other', 'several', 'many', 'some', 'all',
    'various', 'different', 'multiple', 'numerous',
}

suspicious_rels = []  # [(idx, rel_idx, score, reasons)]

for idx, item in enumerate(base):
    text = item.get('text', '')
    for ri, r in enumerate(item.get('relations', [])):
        score = 0
        reasons = []
        t = triplet(r)

        # 信号 1: between 词匹配度
        between = get_between_text(text, r)
        between_words = set(re.findall(r'[a-z]+', between))
        if t in train_between_words:
            train_words = set(train_between_words[t].keys())
            if between_words:
                overlap = between_words & train_words
                match_ratio = len(overlap) / len(between_words) if between_words else 0
                if match_ratio < 0.3 and len(between_words) >= 2:
                    score += 2
                    reasons.append(f"between词匹配度低({match_ratio:.0%}): '{between[:50]}'")
            if not between and len(train_between_patterns[t]) > 5:
                # 实体重叠或紧邻，但训练集中通常有 between 词
                avg_train_between_len = sum(len(b) for b in train_between_patterns[t]) / len(train_between_patterns[t])
                if avg_train_between_len > 10:
                    score += 1
                    reasons.append("实体紧邻但训练集通常有间距")

        # 信号 2: 实体距离异常
        dist = get_entity_distance(r)
        if t in train_distances and train_distances[t]:
            avg_dist = sum(train_distances[t]) / len(train_distances[t])
            std_dist = (sum((d - avg_dist)**2 for d in train_distances[t]) / len(train_distances[t])) ** 0.5
            if dist > avg_dist + 2 * std_dist and dist > 100:
                score += 2
                reasons.append(f"实体距离异常(dist={dist}, avg={avg_dist:.0f}±{std_dist:.0f})")
            elif dist > avg_dist + 1.5 * std_dist and dist > 80:
                score += 1
                reasons.append(f"实体距离偏大(dist={dist}, avg={avg_dist:.0f})")

        # 信号 3: 泛称实体
        head_lower = r['head'].strip().lower()
        tail_lower = r['tail'].strip().lower()
        if head_lower in GENERIC_ENTITIES:
            score += 2
            reasons.append(f"head是泛称: '{r['head']}'")
        if tail_lower in GENERIC_ENTITIES:
            score += 2
            reasons.append(f"tail是泛称: '{r['tail']}'")

        # 信号 4: 实体文本过短（1-2个字符，可能是标注错误）
        if len(r['head'].strip()) <= 2 and r['head_type'] not in ('CHR',):
            score += 1
            reasons.append(f"head过短: '{r['head']}'")
        if len(r['tail'].strip()) <= 2 and r['tail_type'] not in ('CHR',):
            score += 1
            reasons.append(f"tail过短: '{r['tail']}'")

        # 信号 5: 关系类型在底座中已经过多（相对训练集比例）
        # 这个信号较弱，仅作参考

        if score >= 2:
            suspicious_rels.append((idx, ri, score, reasons, r, between))

# 按分数排序
suspicious_rels.sort(key=lambda x: -x[2])

print(f"\n疑似假阳性关系总数: {len(suspicious_rels)}")
report_lines.append(f"\n\n疑似假阳性关系总数: {len(suspicious_rels)}")

# 按类型统计
suspicious_by_type = Counter()
for idx, ri, score, reasons, r, between in suspicious_rels:
    suspicious_by_type[triplet(r)] += 1

print("\n按类型统计:")
report_lines.append("\n按类型统计:")
for t, c in suspicious_by_type.most_common(20):
    line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条疑似假阳性"
    print(line)
    report_lines.append(line)

# 打印 top 30 最可疑的关系
print("\nTop 30 最可疑关系:")
report_lines.append("\nTop 30 最可疑关系:")
for idx, ri, score, reasons, r, between in suspicious_rels[:30]:
    t = triplet(r)
    line = f"  样本{idx} [{t[0]}-{t[1]}-{t[2]}] score={score}: {r['head']} → {r['tail']}"
    reason_str = '; '.join(reasons)
    print(line)
    print(f"    原因: {reason_str}")
    report_lines.append(line)
    report_lines.append(f"    原因: {reason_str}")


# ===== 3. 生成减法候选版本 =====
print("\n" + "=" * 60)
print("步骤 3: 生成减法候选版本")
print("=" * 60)

# 版本 1: 删除 score >= 4 的关系（最保守）
# 版本 2: 删除 score >= 3 的关系（中等）
# 版本 3: 删除 score >= 2 的关系（激进）
# 版本 4: 只删除特定类型（GENE-AFF-TRT 中的可疑关系）
# 版本 5: 只删除泛称实体相关的关系

versions = {}

for threshold, label in [(4, 'conservative'), (3, 'moderate'), (2, 'aggressive')]:
    data = deepcopy(base)
    removed = 0
    removed_by_type = Counter()

    # 按样本索引和关系索引倒序删除（避免索引偏移）
    to_remove = defaultdict(set)
    for idx, ri, score, reasons, r, between in suspicious_rels:
        if score >= threshold:
            to_remove[idx].add(ri)

    for idx in to_remove:
        rels = data[idx].get('relations', [])
        new_rels = []
        for ri, r in enumerate(rels):
            if ri in to_remove[idx]:
                removed += 1
                removed_by_type[triplet(r)] += 1
            else:
                new_rels.append(r)
        data[idx]['relations'] = new_rels

    name = f'submit_v41_sub_{label}'
    save_json_zip(name, data)
    ent, rel, no_rel = stats(data)
    versions[name] = {
        'removed': removed,
        'threshold': threshold,
        'ent_avg': ent,
        'rel_avg': rel,
        'no_rel': no_rel,
        'removed_by_type': removed_by_type,
    }
    line = f"{name}: removed={removed}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%"
    print(line)
    report_lines.append(f"\n{line}")
    for t, c in removed_by_type.most_common(10):
        type_line = f"  删除 {t[0]}-{t[1]}-{t[2]}: {c}条"
        print(type_line)
        report_lines.append(type_line)

# 版本 4: 只删除泛称实体相关的关系
data = deepcopy(base)
removed = 0
removed_by_type = Counter()
for idx, ri, score, reasons, r, between in suspicious_rels:
    if any('泛称' in reason for reason in reasons):
        pass  # 标记
to_remove_generic = defaultdict(set)
for idx, ri, score, reasons, r, between in suspicious_rels:
    if any('泛称' in reason for reason in reasons):
        to_remove_generic[idx].add(ri)

for idx in to_remove_generic:
    rels = data[idx].get('relations', [])
    new_rels = []
    for ri, r in enumerate(rels):
        if ri in to_remove_generic[idx]:
            removed += 1
            removed_by_type[triplet(r)] += 1
        else:
            new_rels.append(r)
    data[idx]['relations'] = new_rels

name = 'submit_v41_sub_generic'
save_json_zip(name, data)
ent, rel, no_rel = stats(data)
versions[name] = {
    'removed': removed,
    'ent_avg': ent,
    'rel_avg': rel,
    'no_rel': no_rel,
    'removed_by_type': removed_by_type,
}
line = f"{name}: removed={removed}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in removed_by_type.most_common(10):
    type_line = f"  删除 {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 5: 只删除 GENE-AFF-TRT 中的可疑关系（已知加法掉分的类型）
data = deepcopy(base)
removed = 0
removed_by_type = Counter()
to_remove_gene_trt = defaultdict(set)
for idx, ri, score, reasons, r, between in suspicious_rels:
    if triplet(r) == ('GENE', 'AFF', 'TRT') and score >= 2:
        to_remove_gene_trt[idx].add(ri)

for idx in to_remove_gene_trt:
    rels = data[idx].get('relations', [])
    new_rels = []
    for ri, r in enumerate(rels):
        if ri in to_remove_gene_trt[idx]:
            removed += 1
            removed_by_type[triplet(r)] += 1
        else:
            new_rels.append(r)
    data[idx]['relations'] = new_rels

name = 'submit_v41_sub_gene_trt'
save_json_zip(name, data)
ent, rel, no_rel = stats(data)
versions[name] = {
    'removed': removed,
    'ent_avg': ent,
    'rel_avg': rel,
    'no_rel': no_rel,
    'removed_by_type': removed_by_type,
}
line = f"{name}: removed={removed}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in removed_by_type.most_common(10):
    type_line = f"  删除 {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# 版本 6: 删除距离异常的关系
data = deepcopy(base)
removed = 0
removed_by_type = Counter()
to_remove_dist = defaultdict(set)
for idx, ri, score, reasons, r, between in suspicious_rels:
    if any('距离' in reason for reason in reasons):
        to_remove_dist[idx].add(ri)

for idx in to_remove_dist:
    rels = data[idx].get('relations', [])
    new_rels = []
    for ri, r in enumerate(rels):
        if ri in to_remove_dist[idx]:
            removed += 1
            removed_by_type[triplet(r)] += 1
        else:
            new_rels.append(r)
    data[idx]['relations'] = new_rels

name = 'submit_v41_sub_distance'
save_json_zip(name, data)
ent, rel, no_rel = stats(data)
versions[name] = {
    'removed': removed,
    'ent_avg': ent,
    'rel_avg': rel,
    'no_rel': no_rel,
    'removed_by_type': removed_by_type,
}
line = f"{name}: removed={removed}, rel_avg={rel:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in removed_by_type.most_common(10):
    type_line = f"  删除 {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)

# ===== 4. 汇总 =====
print("\n" + "=" * 60)
print("汇总")
print("=" * 60)

report_lines.append("\n\n" + "=" * 60)
report_lines.append("提交建议")
report_lines.append("=" * 60)

base_ent, base_rel, base_no_rel = stats(base)
print(f"底座: rel_avg={base_rel:.2f}, no_rel={base_no_rel:.1f}%")
report_lines.append(f"\n底座: rel_avg={base_rel:.2f}, no_rel={base_no_rel:.1f}%")

for name, v in sorted(versions.items()):
    line = f"{name}: removed={v['removed']}, rel_avg={v['rel_avg']:.2f}, no_rel={v['no_rel']:.1f}%"
    print(line)
    report_lines.append(line)

suggestion = """
建议提交顺序:
1. submit_v41_sub_generic（只删泛称，最精准）
2. submit_v41_sub_gene_trt（只删 GENE-AFF-TRT 可疑关系）
3. submit_v41_sub_conservative（score>=4，保守删除）
"""
print(suggestion)
report_lines.append(suggestion)

REPORT.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
print(f"报告已写入: {REPORT}")
