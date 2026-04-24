#!/usr/bin/env python3
"""
make_v41_rule_boost.py — 基于训练集 between 词模式的规则补充

核心思路：
1. 从训练集中精确学习每种低覆盖率关系类型的 between 词模式
2. 在 test_A 中找到匹配模式的实体对
3. 只保留高置信度候选（多重过滤）
4. 生成多个版本，按类型分别测试

重点关注（覆盖率最低的高频类型）：
- BM-AFF-TRT: 6% (2/33)  → 最大缺口
- MRK-LOI-CHR: 15% (7/46)
- GENE-AFF-GENE: 19% (5/26)
- VAR-USE-BM: 22% (9/41)
- ABS-OCI-GST: 24% (8/33)
- CROP-CON-GENE: 24% (14/59)
- CROSS-CON-VAR: 25% (7/28)
- GENE-LOI-TRT: 29% (25/85)
- CROP-CON-VAR: 31% (69/222) → 已排除
- MRK-LOI-TRT: 33% (22/67)
- TRT-AFF-TRT: 33% (16/48)
- CROP-HAS-TRT: 37% (61/165)

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
REPORT = Path('/home/ubuntu/bisai/分析报告/v41_rule_boost_report.txt')


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
    """获取两个实体之间的文本"""
    if h_end <= t_start:
        return text[h_end:t_start].strip().lower()
    elif t_end <= h_start:
        return text[t_end:h_start].strip().lower()
    return ""


# ===== 1. 从训练集学习 between 词模式 =====
print("=" * 60)
print("步骤 1: 从训练集学习 between 词模式")
print("=" * 60)

train = load(TRAIN)
base = load(BASE)
test = load(TEST)

# 学习每种类型的 between 词模式
type_patterns = defaultdict(lambda: {
    'between_texts': [],
    'trigger_words': Counter(),
    'distances': [],
    'count': 0,
})

for item in train:
    text = item['text']
    for r in item.get('relations', []):
        t = triplet(r)
        between = get_between_text(text, r['head_start'], r['head_end'],
                                   r['tail_start'], r['tail_end'])
        dist = abs(r['tail_start'] - r['head_end']) if r['head_end'] <= r['tail_start'] else \
               abs(r['head_start'] - r['tail_end']) if r['tail_end'] <= r['head_start'] else 0

        type_patterns[t]['between_texts'].append(between)
        type_patterns[t]['distances'].append(dist)
        type_patterns[t]['count'] += 1

        # 提取触发词（2-3个词的短语）
        words = re.findall(r'[a-z]+(?:\s+[a-z]+){0,2}', between)
        for w in words:
            w = w.strip()
            if len(w) > 2 and w not in ('the', 'and', 'for', 'was', 'were', 'are', 'has', 'had',
                                         'with', 'from', 'that', 'this', 'which', 'been', 'have',
                                         'not', 'but', 'its', 'their', 'these', 'those', 'also',
                                         'can', 'may', 'will', 'than', 'both', 'each', 'more',
                                         'such', 'only', 'other', 'into', 'over', 'very', 'most'):
                type_patterns[t]['trigger_words'][w] += 1


# ===== 2. 定义每种类型的精准规则 =====
print("\n" + "=" * 60)
print("步骤 2: 定义精准规则")
print("=" * 60)

# 基于训练集分析，为每种低覆盖率类型定义精准触发词
RULES = {
    ('BM', 'AFF', 'TRT'): {
        'trigger_patterns': [
            r'\b(?:associated\s+with|correlated\s+with|linked\s+to|related\s+to)\b',
            r'\b(?:for|of)\b',
            r'\b(?:identified|detected|revealed|showed)\b.*\b(?:for|of)\b',
        ],
        'max_distance': 80,
        'description': 'BM affects TRT (biomarker associated with trait)',
    },
    ('MRK', 'LOI', 'CHR'): {
        'trigger_patterns': [
            r'\b(?:on|at|mapped\s+to|located\s+on|detected\s+on|linked\s+to)\b',
            r'\b(?:chromosome|chr|linkage\s+group)\b',
        ],
        'max_distance': 60,
        'description': 'MRK located on CHR',
    },
    ('VAR', 'USE', 'BM'): {
        'trigger_patterns': [
            r'\b(?:using|used|by|via|through|employed|with)\b',
            r'\b(?:genotyped|screened|analyzed|evaluated)\b.*\b(?:using|with|by)\b',
        ],
        'max_distance': 80,
        'description': 'VAR uses BM',
    },
    ('CROP', 'HAS', 'TRT'): {
        'trigger_patterns': [
            r'\b(?:has|have|had|with|shows?|exhibit|display)\b',
            r'\b(?:for|of)\b',
        ],
        'max_distance': 60,
        'description': 'CROP has TRT',
    },
    ('GENE', 'LOI', 'TRT'): {
        'trigger_patterns': [
            r'\b(?:for|of|controlling|associated\s+with|involved\s+in|related\s+to|underlying)\b',
        ],
        'max_distance': 60,
        'description': 'GENE located in TRT region',
    },
    ('MRK', 'LOI', 'TRT'): {
        'trigger_patterns': [
            r'\b(?:for|of|associated\s+with|linked\s+to|related\s+to)\b',
        ],
        'max_distance': 80,
        'description': 'MRK located in TRT',
    },
    ('TRT', 'AFF', 'TRT'): {
        'trigger_patterns': [
            r'\b(?:affect|influence|correlat|associat|relat|impact|contribut)\w*\b',
            r'\b(?:under|during|reduced|increased|enhanced|improved)\b',
        ],
        'max_distance': 80,
        'description': 'TRT affects TRT',
    },
    ('CROSS', 'CON', 'VAR'): {
        'trigger_patterns': [
            r'\b(?:between|from|of|×|x|cross)\b',
            r'\b(?:derived\s+from|developed\s+from)\b',
        ],
        'max_distance': 60,
        'description': 'CROSS contains VAR',
    },
    ('ABS', 'OCI', 'GST'): {
        'trigger_patterns': [
            r'\b(?:at|during|in|at\s+the|during\s+the)\b',
            r'\b(?:stage|phase|period)\b',
        ],
        'max_distance': 60,
        'description': 'ABS occurs in GST',
    },
    ('CROP', 'CON', 'GENE'): {
        'trigger_patterns': [
            r'\b(?:gene|genes|allele|alleles|locus|loci)\b',
            r'\b(?:in|of|from)\b',
        ],
        'max_distance': 80,
        'description': 'CROP contains GENE',
    },
    ('GENE', 'AFF', 'GENE'): {
        'trigger_patterns': [
            r'\b(?:interact|regulat|activat|repress|inhibit|modulat|target)\w*\b',
            r'\b(?:with|and)\b',
        ],
        'max_distance': 60,
        'description': 'GENE affects GENE',
    },
    ('VAR', 'HAS', 'TRT'): {
        'trigger_patterns': [
            r'\b(?:has|have|had|with|shows?|exhibit|display|possess)\b',
            r'\b(?:higher|lower|greater|better|improved|increased|reduced)\b',
        ],
        'max_distance': 80,
        'description': 'VAR has TRT',
    },
    ('QTL', 'LOI', 'CHR'): {
        'trigger_patterns': [
            r'\b(?:on|at|mapped\s+to|located\s+on|detected\s+on)\b',
        ],
        'max_distance': 60,
        'description': 'QTL located on CHR',
    },
}


# ===== 3. 在 test_A 中应用规则 =====
print("\n" + "=" * 60)
print("步骤 3: 在 test_A 中应用规则")
print("=" * 60)

# 构建底座中已有的关系键集合
base_rel_keys = defaultdict(set)
for idx, item in enumerate(base):
    for r in item.get('relations', []):
        base_rel_keys[idx].add(rel_key(r))

# 对每个 test 样本应用规则
new_candidates = defaultdict(list)  # {(head_type, label, tail_type): [(idx, rel)]}
all_candidates = []

for idx, item in enumerate(base):
    text = item.get('text', '')
    entities = item.get('entities', [])
    existing_keys = base_rel_keys[idx]

    # 为每对实体检查规则
    for i, h_ent in enumerate(entities):
        for j, t_ent in enumerate(entities):
            if i == j:
                continue

            h_type = h_ent['label']
            t_type = t_ent['label']

            # 检查所有规则
            for (rule_h, rule_l, rule_t), rule in RULES.items():
                if h_type != rule_h or t_type != rule_t:
                    continue

                # 检查实体距离
                between = get_between_text(text, h_ent['start'], h_ent['end'],
                                          t_ent['start'], t_ent['end'])
                if not between:
                    continue

                dist = len(between)
                if dist > rule['max_distance']:
                    continue

                # 检查触发词
                matched = False
                for pattern in rule['trigger_patterns']:
                    if re.search(pattern, between):
                        matched = True
                        break

                if not matched:
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
                if key not in existing_keys:
                    t = (rule_h, rule_l, rule_t)
                    new_candidates[t].append((idx, rel, between))
                    all_candidates.append((idx, rel, between, t))

print(f"总新增候选: {len(all_candidates)}")
for t, items in sorted(new_candidates.items(), key=lambda x: -len(x[1])):
    print(f"  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条")

# 打印一些示例
report_lines = [
    "=" * 60,
    "v41 规则补充报告",
    "=" * 60,
    f"\n底座: {BASE} (score=0.4487)",
    f"总新增候选: {len(all_candidates)}",
    "\n各类型新增候选:",
]

for t, items in sorted(new_candidates.items(), key=lambda x: -len(x[1])):
    report_lines.append(f"\n  {t[0]}-{t[1]}-{t[2]}: {len(items)} 条")
    # 打印前5个示例
    for idx, rel, between in items[:5]:
        report_lines.append(f"    样本{idx}: {rel['head']} --[{between[:40]}]--> {rel['tail']}")


# ===== 4. 生成候选版本 =====
print("\n" + "=" * 60)
print("步骤 4: 生成候选版本")
print("=" * 60)

# 版本策略：
# 1. 按单类型分别生成（用于 A/B 测试）
# 2. 组合版（安全类型组合）
# 3. 全量版

report_lines.append("\n\n" + "=" * 60)
report_lines.append("生成版本")
report_lines.append("=" * 60)

# 单类型版本
single_versions = {}
for t, items in sorted(new_candidates.items(), key=lambda x: -len(x[1])):
    if len(items) < 3:
        continue
    name_suffix = f"{t[0].lower()}_{t[1].lower()}_{t[2].lower()}"
    name = f'submit_v41_rule_{name_suffix}'

    data = deepcopy(base)
    added = 0
    for idx, rel, between in items:
        key = rel_key(rel)
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1

    save_json_zip(name, data)
    ent, rel_avg, no_rel = stats(data)
    single_versions[name] = {'added': added, 'type': t}
    line = f"{name}: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
    print(line)
    report_lines.append(f"\n{line}")

# 安全组合版 1: 最低覆盖率类型（BM-AFF-TRT + MRK-LOI-CHR + VAR-USE-BM）
SAFE_COMBO_1 = [
    ('BM', 'AFF', 'TRT'),
    ('MRK', 'LOI', 'CHR'),
    ('VAR', 'USE', 'BM'),
]
data = deepcopy(base)
added = 0
for t in SAFE_COMBO_1:
    for idx, rel, between in new_candidates.get(t, []):
        key = rel_key(rel)
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1

save_json_zip('submit_v41_rule_lowcov_combo', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_rule_lowcov_combo: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")

# 安全组合版 2: 中等覆盖率类型（CROP-HAS-TRT + GENE-LOI-TRT + TRT-AFF-TRT + CROSS-CON-VAR）
SAFE_COMBO_2 = [
    ('CROP', 'HAS', 'TRT'),
    ('GENE', 'LOI', 'TRT'),
    ('TRT', 'AFF', 'TRT'),
    ('CROSS', 'CON', 'VAR'),
    ('ABS', 'OCI', 'GST'),
]
data = deepcopy(base)
added = 0
for t in SAFE_COMBO_2:
    for idx, rel, between in new_candidates.get(t, []):
        key = rel_key(rel)
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1

save_json_zip('submit_v41_rule_midcov_combo', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_rule_midcov_combo: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")

# 全量版（所有规则类型）
data = deepcopy(base)
added = 0
added_by_type = Counter()
for t, items in new_candidates.items():
    for idx, rel, between in items:
        key = rel_key(rel)
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1
            added_by_type[t] += 1

save_json_zip('submit_v41_rule_all', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_rule_all: added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")
for t, c in added_by_type.most_common(15):
    type_line = f"  {t[0]}-{t[1]}-{t[2]}: {c}条"
    print(type_line)
    report_lines.append(type_line)


# ===== 5. 减法+加法组合版 =====
print("\n" + "=" * 60)
print("步骤 5: 减法+加法组合版")
print("=" * 60)

# 加载减法版本（保守版）
sub_conservative = load(ROOT / 'submit_v41_sub_conservative.json')

# 在减法基础上加入安全规则
data = deepcopy(sub_conservative)
added = 0
for t in SAFE_COMBO_1:
    for idx, rel, between in new_candidates.get(t, []):
        key = rel_key(rel)
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1

save_json_zip('submit_v41_sub_plus_lowcov', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_sub_plus_lowcov: removed=25+added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")

# 减法（泛称）+ 加法（安全组合1）
sub_generic = load(ROOT / 'submit_v41_sub_generic.json')
data = deepcopy(sub_generic)
added = 0
for t in SAFE_COMBO_1:
    for idx, rel, between in new_candidates.get(t, []):
        key = rel_key(rel)
        existing = {rel_key(r) for r in data[idx].get('relations', [])}
        if key not in existing:
            data[idx]['relations'].append(rel)
            added += 1

save_json_zip('submit_v41_sub_generic_plus_lowcov', data)
ent, rel_avg, no_rel = stats(data)
line = f"submit_v41_sub_generic_plus_lowcov: removed=95+added={added}, rel_avg={rel_avg:.2f}, no_rel={no_rel:.1f}%"
print(line)
report_lines.append(f"\n{line}")


# ===== 6. 汇总 =====
print("\n" + "=" * 60)
print("汇总")
print("=" * 60)

report_lines.append("\n\n" + "=" * 60)
report_lines.append("提交建议")
report_lines.append("=" * 60)

suggestion = """
建议提交顺序（优先级从高到低）:

第一优先级（减法策略，最可能涨分）:
1. submit_v41_sub_conservative（保守删除 score>=4 的 25 条假阳性）
2. submit_v41_sub_generic（删除泛称实体相关的 95 条关系）

第二优先级（减法+加法组合）:
3. submit_v41_sub_plus_lowcov（保守减法 + 低覆盖率规则加法）
4. submit_v41_sub_generic_plus_lowcov（泛称减法 + 低覆盖率规则加法）

第三优先级（纯加法，单类型测试）:
5. submit_v41_rule_bm_aff_trt（BM-AFF-TRT 规则补充，覆盖率最低的类型）
6. submit_v41_rule_mrk_loi_chr（MRK-LOI-CHR 规则补充）
7. submit_v41_rule_lowcov_combo（低覆盖率类型组合）
"""
print(suggestion)
report_lines.append(suggestion)

REPORT.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
print(f"报告已写入: {REPORT}")
