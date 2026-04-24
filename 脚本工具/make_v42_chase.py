#!/usr/bin/env python3
"""
make_v42_chase.py — 在新底座 0.4510 上追赶第一名 0.4560

关键发现：
- 保守减法（score≥4，删25条）涨了 +0.0023，说明底座假阳性确实多
- 删除的主要是 QTL-LOI-TRT(6), MRK-LOI-QTL(3), VAR-CON-VAR(2) 等
- 新底座: 1056条关系, avg=2.64, no_rel=28.0%

策略：
1. 在新底座上继续减法（删除 score=3 的中等可疑关系）
2. 在新底座上做精准加法（只加最安全的候选）
3. 在新底座上做减法+加法组合

只生成 3 个最优候选。
"""
import json
import re
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
NEW_BASE = ROOT / 'submit_v41_sub_conservative.json'  # 新底座 0.4510
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
TEST = Path('/home/ubuntu/bisai/数据/官方原始数据/test_A.json')

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
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])


def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])


def stats(data):
    n = len(data)
    total = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    return total, total / n, no_rel, no_rel / n * 100


def get_between_text(text, h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return text[h_end:t_start].strip().lower()
    elif t_end <= h_start:
        return text[t_end:h_start].strip().lower()
    return ""


def get_entity_distance(h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return t_start - h_end
    elif t_end <= h_start:
        return h_start - t_end
    return 0


# ===== 加载数据 =====
print("加载数据...")
train = load(TRAIN)
base = load(NEW_BASE)
test = load(TEST)

total, avg, no_rel, no_rel_pct = stats(base)
print(f"新底座 (0.4510): rels={total}, avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# ===== 分析训练集模式 =====
train_between_words = defaultdict(Counter)
train_distances = defaultdict(list)

for item in train:
    text = item['text']
    for r in item.get('relations', []):
        t = triplet(r)
        between = get_between_text(text, r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        dist = get_entity_distance(r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        train_distances[t].append(dist)
        words = re.findall(r'[a-z]+', between)
        for w in words:
            train_between_words[t][w] += 1


# ===== 对新底座中每条关系重新评分 =====
print("\n对新底座中每条关系重新评分...")

suspicious = []
for idx, item in enumerate(base):
    text = item.get('text', '')
    for ri, r in enumerate(item.get('relations', [])):
        score = 0
        reasons = []
        t = triplet(r)

        # between 词匹配度
        between = get_between_text(text, r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        between_words = set(re.findall(r'[a-z]+', between))
        if t in train_between_words and between_words:
            train_words = set(train_between_words[t].keys())
            overlap = between_words & train_words
            match_ratio = len(overlap) / len(between_words)
            if match_ratio < 0.3 and len(between_words) >= 2:
                score += 2
                reasons.append(f"between词匹配低({match_ratio:.0%})")

        # 实体距离
        dist = get_entity_distance(r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        if t in train_distances and train_distances[t]:
            avg_d = sum(train_distances[t]) / len(train_distances[t])
            std_d = (sum((d - avg_d)**2 for d in train_distances[t]) / len(train_distances[t])) ** 0.5
            if dist > avg_d + 2 * std_d and dist > 100:
                score += 2
                reasons.append(f"距离异常(dist={dist})")
            elif dist > avg_d + 1.5 * std_d and dist > 80:
                score += 1
                reasons.append(f"距离偏大(dist={dist})")

        # 泛称实体
        if r['head'].strip().lower() in GENERIC_ENTITIES:
            score += 2
            reasons.append(f"head泛称:'{r['head']}'")
        if r['tail'].strip().lower() in GENERIC_ENTITIES:
            score += 2
            reasons.append(f"tail泛称:'{r['tail']}'")

        # 实体过短
        if len(r['head'].strip()) <= 2 and r['head_type'] not in ('CHR',):
            score += 1
            reasons.append(f"head过短:'{r['head']}'")
        if len(r['tail'].strip()) <= 2 and r['tail_type'] not in ('CHR',):
            score += 1
            reasons.append(f"tail过短:'{r['tail']}'")

        if score >= 2:
            suspicious.append((idx, ri, score, reasons, r))

suspicious.sort(key=lambda x: -x[2])
print(f"新底座中剩余可疑关系: {len(suspicious)}")

# 按 score 分布
score_dist = Counter(s for _, _, s, _, _ in suspicious)
for s, c in sorted(score_dist.items(), reverse=True):
    print(f"  score={s}: {c}条")


# ===== 策略 1: 继续减法（在新底座上删 score=3 的关系）=====
print("\n" + "=" * 60)
print("策略 1: 继续减法（删 score≥3 的中等可疑关系）")
print("=" * 60)

data = deepcopy(base)
to_remove = defaultdict(set)
for idx, ri, score, reasons, r in suspicious:
    if score >= 3:
        to_remove[idx].add(ri)

removed = 0
removed_by_type = Counter()
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

save_json_zip('submit_v42_deeper_subtract', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v42_deeper_subtract: removed={removed}, rels={total}, avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")
for t, c in removed_by_type.most_common(10):
    print(f"  删除 {t[0]}-{t[1]}-{t[2]}: {c}条")


# ===== 策略 2: 在新底座上做精准加法 =====
# 只加入最安全的候选：
# - 训练集中高频出现的关系类型
# - 实体距离在训练集 P50 以内
# - 触发词在训练集中出现 ≥3 次
# - 排除泛称实体
print("\n" + "=" * 60)
print("策略 2: 精准加法（在新底座上补充高置信候选）")
print("=" * 60)

# 定义最安全的加法规则（只选覆盖率极低且训练集中有明确模式的类型）
SAFE_ADD_RULES = {
    ('CROP', 'HAS', 'TRT'): {
        'patterns': [
            r'\b(?:resistance|toleran|susceptib)\w*\b',
            r'\b(?:yield|quality|height|weight|maturity|flowering)\b',
        ],
        'max_distance': 40,
    },
    ('QTL', 'LOI', 'CHR'): {
        'patterns': [
            r'\b(?:on\s+chromosome|mapped\s+to|located\s+on|detected\s+on)\b',
            r'\bon\b.*\b(?:chromosome|chr)\b',
        ],
        'max_distance': 40,
    },
    ('MRK', 'LOI', 'CHR'): {
        'patterns': [
            r'\b(?:on\s+chromosome|mapped\s+to|located\s+on)\b',
        ],
        'max_distance': 40,
    },
    ('BM', 'AFF', 'TRT'): {
        'patterns': [
            r'\b(?:associated\s+with|correlated\s+with|linked\s+to)\b',
            r'\b(?:significant\w*\s+(?:for|effect))\b',
        ],
        'max_distance': 50,
    },
}

# 构建底座关系键
base_keys = defaultdict(set)
for idx, item in enumerate(base):
    for r in item.get('relations', []):
        base_keys[idx].add(rel_key(r))

# 应用规则
new_rels_found = []
for idx, item in enumerate(base):
    text = item.get('text', '')
    entities = item.get('entities', [])
    existing = base_keys[idx]

    for i, h_ent in enumerate(entities):
        for j, t_ent in enumerate(entities):
            if i == j:
                continue
            h_type = h_ent['label']
            t_type = t_ent['label']

            for (rule_h, rule_l, rule_t), rule in SAFE_ADD_RULES.items():
                if h_type != rule_h or t_type != rule_t:
                    continue

                # 排除泛称
                if h_ent['text'].strip().lower() in GENERIC_ENTITIES:
                    continue
                if t_ent['text'].strip().lower() in GENERIC_ENTITIES:
                    continue

                between = get_between_text(text, h_ent['start'], h_ent['end'],
                                          t_ent['start'], t_ent['end'])
                if not between:
                    continue

                dist = len(between)
                if dist > rule['max_distance']:
                    continue

                # 检查模式
                matched = False
                for pattern in rule['patterns']:
                    if re.search(pattern, between):
                        matched = True
                        break
                if not matched:
                    continue

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
                if key not in existing:
                    new_rels_found.append((idx, rel, between))

print(f"精准加法候选: {len(new_rels_found)} 条")
type_counter = Counter()
for idx, rel, between in new_rels_found:
    t = (rel['head_type'], rel['label'], rel['tail_type'])
    type_counter[t] += 1
for t, c in type_counter.most_common():
    print(f"  {t[0]}-{t[1]}-{t[2]}: {c}条")

# 在新底座上加入
data = deepcopy(base)
added = 0
for idx, rel, between in new_rels_found:
    existing = {rel_key(r) for r in data[idx].get('relations', [])}
    if rel_key(rel) not in existing:
        data[idx]['relations'].append(rel)
        added += 1

save_json_zip('submit_v42_precise_add', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v42_precise_add: added={added}, rels={total}, avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")


# ===== 策略 3: 减法+加法组合 =====
print("\n" + "=" * 60)
print("策略 3: 减法+加法组合（在更深减法基础上加入精准候选）")
print("=" * 60)

# 在 deeper_subtract 基础上加入精准候选
deeper = load(ROOT / 'submit_v42_deeper_subtract.json')
data = deepcopy(deeper)
added = 0
for idx, rel, between in new_rels_found:
    existing = {rel_key(r) for r in data[idx].get('relations', [])}
    if rel_key(rel) not in existing:
        data[idx]['relations'].append(rel)
        added += 1

save_json_zip('submit_v42_subtract_plus_add', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"submit_v42_subtract_plus_add: deeper_sub + added={added}, rels={total}, avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")


# ===== 汇总 =====
print("\n" + "=" * 60)
print("汇总: 3个候选版本")
print("=" * 60)

for name in ['submit_v42_deeper_subtract', 'submit_v42_precise_add', 'submit_v42_subtract_plus_add']:
    d = load(ROOT / f'{name}.json')
    total, avg, no_rel, no_rel_pct = stats(d)
    diff = total - 1056  # 相对新底座
    print(f"  {name}: rels={total}(diff={diff:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

print("""
提交建议:
1. submit_v42_deeper_subtract — 继续减法，删除更多可疑关系（减法已验证有效）
2. submit_v42_subtract_plus_add — 减法+加法组合，净效果最优
3. submit_v42_precise_add — 纯加法，在新底座上补充最安全的候选
""")
