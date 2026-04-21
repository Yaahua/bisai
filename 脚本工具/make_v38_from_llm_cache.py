#!/usr/bin/env python3
"""
make_v38_from_llm_cache.py — 将 LLM 关系抽取结果（过滤幻觉后）合并到提交文件

LLM 结果统计（111个无关系样本）：
- 有新关系的样本: 67
- 新增关系总数: 248（其中有效196条，幻觉52条）
- 主要有效类型: QTL-AFF-TRT:20, GENE-AFF-TRT:15, VAR-HAS-TRT:13, CROP-HAS-TRT:11...

策略：
1. v38_llm_strict: 只用有效类型（过滤幻觉），+196条
2. v38_llm_highconf: 只用高频有效类型（每类≥5条），更保守
3. v38_llm_plus_v37: v37_qtl_loi + LLM 有效关系（叠加）

底座：submit_v36_gene_abs（当前最高分 0.4487）
"""
import json
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
BASE = ROOT / 'submit_v36_gene_abs.json'
CACHE = Path('/home/ubuntu/bisai/分析报告/llm_re_cache.json')
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
REPORT = Path('/home/ubuntu/bisai/分析报告/v38_llm_results_report.txt')


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


def stats(data):
    n = len(data)
    rel = sum(len(x.get('relations', [])) for x in data) / n
    no_rel = sum(1 for x in data if not x.get('relations')) / n * 100
    return rel, no_rel


print("加载数据...")
base = load(BASE)
cache = load(CACHE)
train = load(TRAIN)

# 加载训练集有效类型
valid_types = set()
for x in train:
    for r in x.get('relations', []):
        valid_types.add((r['head_type'], r['label'], r['tail_type']))

# 统计 LLM 缓存中有效关系
type_counter = Counter()
for rels in cache.values():
    for r in rels:
        t = (r['head_type'], r['label'], r['tail_type'])
        if t in valid_types:
            type_counter[t] += 1

print("有效关系类型分布（Top 15）:")
for t, n in type_counter.most_common(15):
    print(f"  {t[0]}-{t[1]}-{t[2]}: {n}")

# 高置信度类型（≥5条）
high_conf_types = {t for t, n in type_counter.items() if n >= 5}
print(f"\n高置信度类型（≥5条）: {len(high_conf_types)} 种")
for t in sorted(high_conf_types):
    print(f"  {t[0]}-{t[1]}-{t[2]}: {type_counter[t]}")


def apply_llm_cache(base_data, cache_data, allowed_types=None):
    """将 LLM 缓存中的关系应用到底座"""
    data = deepcopy(base_data)
    added = 0
    added_counter = Counter()

    for idx_str, rels in cache_data.items():
        idx = int(idx_str)
        if idx >= len(data) or not rels:
            continue

        item = data[idx]
        # 构建实体名称到实体对象的映射
        ent_map = {e['text']: e for e in item.get('entities', [])}
        existing = {rel_key(r) for r in item.get('relations', [])}

        for r in rels:
            t = (r['head_type'], r['label'], r['tail_type'])
            # 类型过滤
            if t not in valid_types:
                continue
            if allowed_types is not None and t not in allowed_types:
                continue

            head = r['head']
            tail = r['tail']
            h_ent = ent_map.get(head)
            t_ent = ent_map.get(tail)
            if not h_ent or not t_ent:
                continue

            key = (head.strip().lower(), r['head_type'], r['label'],
                   tail.strip().lower(), r['tail_type'])
            if key in existing:
                continue

            full_rel = {
                'head': head,
                'head_type': r['head_type'],
                'head_start': h_ent['start'],
                'head_end': h_ent['end'],
                'tail': tail,
                'tail_type': r['tail_type'],
                'tail_start': t_ent['start'],
                'tail_end': t_ent['end'],
                'label': r['label'],
            }
            item['relations'].append(full_rel)
            existing.add(key)
            added += 1
            added_counter[t] += 1

    return data, added, added_counter


report = [f"base={BASE} (score=0.4487)", "LLM 关系抽取结果（111个无关系样本）:"]

# 版本1：严格过滤（只用训练集存在的类型）
data1, added1, counter1 = apply_llm_cache(base, cache, allowed_types=None)
save_json_zip('submit_v38_llm_strict', data1)
rel1, no_rel1 = stats(data1)
line1 = f"submit_v38_llm_strict: added={added1} rel_avg={rel1:.2f} no_rel={no_rel1:.1f}%"
type_str1 = ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in counter1.most_common(10))
report.append(line1)
report.append(f"  types={type_str1}")
print(f"\n{line1}")
print(f"  types={type_str1}")

# 版本2：高置信度（只用≥5条的类型）
data2, added2, counter2 = apply_llm_cache(base, cache, allowed_types=high_conf_types)
save_json_zip('submit_v38_llm_highconf', data2)
rel2, no_rel2 = stats(data2)
line2 = f"submit_v38_llm_highconf: added={added2} rel_avg={rel2:.2f} no_rel={no_rel2:.1f}%"
type_str2 = ', '.join(f'{a}-{b}-{c}:{n}' for (a,b,c), n in counter2.most_common(10))
report.append(line2)
report.append(f"  types={type_str2}")
print(f"\n{line2}")
print(f"  types={type_str2}")

# 版本3：LLM 严格 + v37_qtl_loi 叠加
v37_qtl = load(ROOT / 'submit_v37_qtl_loi.json')

def rel_key2(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

# 先应用 LLM，再叠加 v37_qtl_loi 的新增
data3 = deepcopy(data1)  # 已有 LLM 结果
added3_extra = 0
counter3_extra = Counter()
for b, q, d in zip(base, v37_qtl, data3):
    kb = {rel_key2(r) for r in b.get('relations', [])}
    kd = {rel_key2(r) for r in d.get('relations', [])}
    for r in q.get('relations', []):
        k = rel_key2(r)
        if k not in kb and k not in kd:
            d['relations'].append(r)
            added3_extra += 1
            counter3_extra[(r['head_type'], r['label'], r['tail_type'])] += 1

save_json_zip('submit_v38_llm_qtl', data3)
rel3, no_rel3 = stats(data3)
line3 = f"submit_v38_llm_qtl: added_llm={added1} added_qtl={added3_extra} total={added1+added3_extra} rel_avg={rel3:.2f}"
report.append(line3)
print(f"\n{line3}")

REPORT.write_text('\n'.join(report) + '\n', encoding='utf-8')
print(f"\n报告已写入: {REPORT}")
print("所有 v38 候选已生成！")
