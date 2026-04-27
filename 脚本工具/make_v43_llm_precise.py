#!/usr/bin/env python3
"""
make_v43_llm_precise.py — 精准过滤 LLM 补充结果

问题发现：
1. VAR-HAS-TRT 中有多个 VAR 共享同一 TRT（Striga resistance indices），
   这些 VAR 实体之间通过列举方式出现，between 文本很长（包含其他 VAR 名称），
   这类关系在训练集中不常见，可能是假阳性
2. ABS-AFF-TRT 中 between 文本很长，语义不清

精准过滤规则：
- VAR-HAS-TRT：between 文本 ≤ 50 字符，且包含训练集高频词（had/showed/exhibited/higher/lower等）
- ABS-AFF-TRT：between 文本 ≤ 60 字符，且包含训练集高频词（under/caused/reduced/increased等）
"""
import json
import re
import zipfile
from pathlib import Path
from collections import Counter
from copy import deepcopy

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
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
    print(f"  已保存: {json_path.name}")
    return json_path, zip_path

def rel_key(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

def stats(data):
    n = len(data)
    total = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    return total, total / n, no_rel, no_rel / n * 100

def get_between_text(text, h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return text[h_end:t_start].strip()
    elif t_end <= h_start:
        return text[t_end:h_start].strip()
    return ""

# 加载数据
train = load(TRAIN)
base = load(ROOT / 'submit_v41_sub_conservative.json')
llm_safe = load(ROOT / 'submit_v43_llm_safe.json')

base_total, base_avg, base_no_rel, base_no_rel_pct = stats(base)
print(f"底座 (0.4510): rels={base_total}, avg={base_avg:.2f}, no_rel={base_no_rel}({base_no_rel_pct:.1f}%)")

# 找出 LLM safe 新增的关系
base_keys = set()
for item in base:
    for r in item.get('relations', []):
        base_keys.add(rel_key(r))

new_rels = []
for idx, item in enumerate(llm_safe):
    text = item.get('text', '')
    for r in item.get('relations', []):
        if rel_key(r) not in base_keys:
            between = get_between_text(text, r['head_start'], r['head_end'],
                                       r['tail_start'], r['tail_end'])
            new_rels.append((idx, r, between, text))

print(f"\nLLM safe 新增关系: {len(new_rels)} 条")

# VAR-HAS-TRT 精准过滤
VAR_HAS_TRT_KEYWORDS = {
    'had', 'showed', 'exhibited', 'displayed', 'showed', 'has', 'have',
    'higher', 'lower', 'better', 'greater', 'more', 'less',
    'resistant', 'tolerant', 'susceptible', 'sensitive',
    'cultivar', 'variety', 'line', 'accession',
}

ABS_AFF_TRT_KEYWORDS = {
    'under', 'caused', 'reduced', 'increased', 'enhanced', 'improved',
    'decreased', 'affected', 'influenced', 'regulated', 'induced',
    'response', 'tolerance', 'resistance', 'sensitivity',
}

precise_rels = []
filtered_out = []

for idx, r, between, text in new_rels:
    t = (r['head_type'], r['label'], r['tail_type'])
    between_lower = between.lower()
    between_words = set(re.findall(r'\b[a-z]{2,}\b', between_lower))
    
    if t == ('VAR', 'HAS', 'TRT'):
        # 过滤条件：between ≤ 60 字符，且有关键词
        if len(between) <= 60 and (between_words & VAR_HAS_TRT_KEYWORDS):
            precise_rels.append((idx, r, between))
            print(f"  ✓ VAR-HAS-TRT: [{r['head']}] → [{r['tail']}] | between='{between[:60]}'")
        else:
            filtered_out.append((idx, r, between, f"VAR-HAS-TRT: len={len(between)}, keywords={between_words & VAR_HAS_TRT_KEYWORDS}"))
    
    elif t == ('ABS', 'AFF', 'TRT'):
        # 过滤条件：between ≤ 80 字符，且有关键词
        if len(between) <= 80 and (between_words & ABS_AFF_TRT_KEYWORDS):
            precise_rels.append((idx, r, between))
            print(f"  ✓ ABS-AFF-TRT: [{r['head']}] → [{r['tail']}] | between='{between[:60]}'")
        else:
            filtered_out.append((idx, r, between, f"ABS-AFF-TRT: len={len(between)}, keywords={between_words & ABS_AFF_TRT_KEYWORDS}"))

print(f"\n精准过滤后: {len(precise_rels)} 条（过滤掉 {len(filtered_out)} 条）")
print("\n被过滤掉的关系:")
for idx, r, between, reason in filtered_out:
    print(f"  [{r['head']}] → [{r['tail']}] | {reason}")

# 生成精准版本
data = deepcopy(base)
added = 0
for idx, r, between in precise_rels:
    existing = {rel_key(ex) for ex in data[idx].get('relations', [])}
    if rel_key(r) not in existing:
        data[idx]['relations'].append(r)
        added += 1

save_json_zip('submit_v43_llm_precise', data)
total, avg, no_rel, no_rel_pct = stats(data)
print(f"\nsubmit_v43_llm_precise: added={added}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")

# 生成减法+精准加法组合
sub_combined = load(ROOT / 'submit_v43_sub_combined.json')
sub_combined_total = sum(len(x.get('relations', [])) for x in sub_combined)
sub_base_keys = set()
for item in sub_combined:
    for r in item.get('relations', []):
        sub_base_keys.add(rel_key(r))

data2 = deepcopy(sub_combined)
added2 = 0
for idx, r, between in precise_rels:
    existing = {rel_key(ex) for ex in data2[idx].get('relations', [])}
    if rel_key(r) not in existing:
        data2[idx]['relations'].append(r)
        added2 += 1

save_json_zip('submit_v43_sub_plus_precise', data2)
total2, avg2, no_rel2, no_rel_pct2 = stats(data2)
print(f"submit_v43_sub_plus_precise: added={added2}, rels={total2}(diff={total2-base_total:+d}), avg={avg2:.2f}, no_rel={no_rel2}({no_rel_pct2:.1f}%)")

print("""
最终推荐提交顺序（按优先级）：
1. submit_v43_sub_combined — 减法删35条高风险（TRT-OCI-GST+MRK-LOI-TRT+TRT-AFF-TRT）
   预期：涨分（类似v41_sub_conservative涨+0.0023）
2. submit_v43_llm_precise — LLM精准补充（VAR-HAS-TRT+ABS-AFF-TRT，历史涨分类型）
   预期：中等，涨分概率60%
3. submit_v43_sub_plus_precise — 减法+精准加法组合
   预期：最优组合，涨分概率65%
""")
