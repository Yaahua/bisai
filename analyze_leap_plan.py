#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze MGBIE Track-A submissions for leap-forward planning."""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path('/home/ubuntu/bisai')
A = ROOT / '数据' / 'A榜'
RAW = ROOT / '数据' / '官方原始数据'
OUT = ROOT / '分析报告' / 'leap_plan_data_20260430.md'

KNOWN_SCORES = {
    'submit_ensemble_v3': 0.4172,
    'submit_v16_rules': 0.4172,
    'submit_v30_safe': 0.4479,
    'submit_v32_plus_abs_var': 0.4479,
    'submit_v36_gene_abs': 0.4487,
    'submit_v41_sub_conservative': 0.4510,
    'submit_v43_sub_all_score3': 0.4454,
    'submit_v44_del_var_con_cross': 0.4514,
}

SUBMISSIONS = [
    'submit_v36_gene_abs',
    'submit_v41_sub_conservative',
    'submit_v44_del_var_con_cross',
    'submit_v45_del_gene_loi_mrk',
    'submit_v45_fix_gene_mrk_direction',
    'submit_v45_del_low_freq_types',
    'submit_v45_del_all_risks',
    'submit_v45_fix_cross_con_var',
    'submit_v45_fix_cross_del_gene_mrk',
    'submit_v45_fix_both_directions',
]


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def rel_key(r):
    return (r.get('head_type'), r.get('label'), r.get('tail_type'))


def rel_sig(idx, r):
    return (
        idx,
        r.get('head'), r.get('head_type'), r.get('head_start'), r.get('head_end'),
        r.get('label'),
        r.get('tail'), r.get('tail_type'), r.get('tail_start'), r.get('tail_end'),
    )


def stats(data):
    n = len(data)
    rels = []
    ent_count = []
    no_rel = 0
    type_counter = Counter()
    per_item = []
    for i, item in enumerate(data):
        rs = item.get('relations', []) or []
        es = item.get('entities', []) or []
        if not rs:
            no_rel += 1
        ent_count.append(len(es))
        per_item.append(len(rs))
        for r in rs:
            rels.append((i, r))
            type_counter['-'.join(rel_key(r))] += 1
    return {
        'n': n,
        'rel_total': len(rels),
        'rel_avg': len(rels) / n if n else 0,
        'ent_avg': sum(ent_count) / n if n else 0,
        'no_rel': no_rel,
        'no_rel_pct': no_rel / n * 100 if n else 0,
        'type_counter': type_counter,
        'per_item': per_item,
        'rels': rels,
    }


def load_submission(name):
    path = A / f'{name}.json'
    return load_json(path) if path.exists() else None


def training_type_counts():
    train_path = RAW / 'train.json'
    if not train_path.exists():
        return Counter(), Counter()
    train = load_json(train_path)
    c = Counter()
    pair_c = Counter()
    for item in train:
        for r in item.get('relations', []) or []:
            c['-'.join(rel_key(r))] += 1
            pair_c[(r.get('head_type'), r.get('tail_type'))] += 1
    return c, pair_c


def diff_names(base_name, cand_name):
    base = load_submission(base_name)
    cand = load_submission(cand_name)
    if base is None or cand is None:
        return None
    bset = set()
    cset = set()
    b_by = {}
    c_by = {}
    for i, item in enumerate(base):
        for r in item.get('relations', []) or []:
            s = rel_sig(i, r)
            bset.add(s); b_by[s] = r
    for i, item in enumerate(cand):
        for r in item.get('relations', []) or []:
            s = rel_sig(i, r)
            cset.add(s); c_by[s] = r
    removed = bset - cset
    added = cset - bset
    rem_types = Counter('-'.join(rel_key(b_by[s])) for s in removed)
    add_types = Counter('-'.join(rel_key(c_by[s])) for s in added)
    return removed, added, rem_types, add_types


def low_freq_inventory(data_name, train_counts, max_freq=5):
    data = load_submission(data_name)
    out = []
    if data is None:
        return out
    st = stats(data)
    for typ, cnt in st['type_counter'].most_common():
        tf = train_counts.get(typ, 0)
        if tf <= max_freq:
            out.append((typ, cnt, tf))
    return sorted(out, key=lambda x: (x[2], -x[1], x[0]))


def examples_for_types(data_name, types, limit_each=8):
    data = load_submission(data_name)
    out = defaultdict(list)
    wanted = set(types)
    for idx, item in enumerate(data):
        text = item.get('text') or item.get('sentence') or item.get('abstract') or ''
        for r in item.get('relations', []) or []:
            typ = '-'.join(rel_key(r))
            if typ in wanted and len(out[typ]) < limit_each:
                out[typ].append({
                    'idx': idx,
                    'head': r.get('head'),
                    'label': r.get('label'),
                    'tail': r.get('tail'),
                    'text': text[:220].replace('\n',' '),
                })
    return out


def main():
    train_counts, train_pair_counts = training_type_counts()
    lines = []
    lines.append('# 大跃进计划数据底稿（自动统计）')
    lines.append('')
    lines.append('## 1. 关键提交版本总体统计')
    lines.append('')
    lines.append('| 版本 | 已知分数 | 关系数 | 关系均值 | 无关系样本 | 实体均值 | Top关系类型 |')
    lines.append('| :--- | ---: | ---: | ---: | :--- | ---: | :--- |')
    for name in SUBMISSIONS:
        data = load_submission(name)
        if data is None:
            continue
        st = stats(data)
        top = ', '.join([f'{k}:{v}' for k, v in st['type_counter'].most_common(6)])
        score = KNOWN_SCORES.get(name)
        score_s = f'{score:.4f}' if score is not None else ''
        lines.append(f'| `{name}` | {score_s} | {st["rel_total"]} | {st["rel_avg"]:.2f} | {st["no_rel"]} ({st["no_rel_pct"]:.1f}%) | {st["ent_avg"]:.2f} | {top} |')

    lines.append('')
    lines.append('## 2. v44底座中的低频关系库存（训练集频次<=5）')
    lines.append('')
    lines.append('| 类型 | v44数量 | 训练集频次 |')
    lines.append('| :--- | ---: | ---: |')
    low = low_freq_inventory('submit_v44_del_var_con_cross', train_counts, 5)
    for typ, cnt, tf in low:
        lines.append(f'| {typ} | {cnt} | {tf} |')

    lines.append('')
    lines.append('## 3. v45候选相对v44底座的差异')
    lines.append('')
    lines.append('| 候选 | 删除数 | 新增数 | 删除类型Top | 新增类型Top |')
    lines.append('| :--- | ---: | ---: | :--- | :--- |')
    for cand in SUBMISSIONS[3:]:
        d = diff_names('submit_v44_del_var_con_cross', cand)
        if d is None:
            continue
        removed, added, rem_types, add_types = d
        rem = ', '.join([f'{k}:{v}' for k, v in rem_types.most_common(8)])
        add = ', '.join([f'{k}:{v}' for k, v in add_types.most_common(8)])
        lines.append(f'| `{cand}` | {len(removed)} | {len(added)} | {rem} | {add} |')

    lines.append('')
    lines.append('## 4. 方向与低频关系样例')
    lines.append('')
    key_types = ['GENE-LOI-MRK','GENE-CON-TRT','QTL-AFF-BIS','BM-USE-TRT','VAR-OCI-GST','BM-AFF-GENE','CROSS-USE-MRK','VAR-CON-GENE']
    ex = examples_for_types('submit_v44_del_var_con_cross', key_types, 5)
    for typ in key_types:
        lines.append(f'### {typ}')
        if not ex.get(typ):
            lines.append('无。')
        else:
            lines.append('| idx | head | label | tail | text片段 |')
            lines.append('| ---: | :--- | :--- | :--- | :--- |')
            for e in ex[typ]:
                lines.append(f'| {e["idx"]} | {e["head"]} | {e["label"]} | {e["tail"]} | {e["text"]} |')
        lines.append('')

    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT)

if __name__ == '__main__':
    main()
