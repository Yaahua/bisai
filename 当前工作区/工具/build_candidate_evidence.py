#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立 v47 单候选证据表：只找当前 0.4514 底座缺失的单条补召回候选。"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path('/home/ubuntu/bisai')
DATA = ROOT / '数据/A榜'
BASE = ROOT / '当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.json'
TRAIN = ROOT / '数据/官方原始数据/train.json'
OUT_CSV = ROOT / '当前工作区/记录/v47_candidate_evidence_table_20260502.csv'
OUT_MD = ROOT / '当前工作区/记录/v47候选证据表_20260502.md'
OUT_JSON = ROOT / '当前工作区/记录/v47_candidate_evidence_table_20260502.json'

EXCLUDE_PATTERNS = [
    'submit_v44_del_var_con_cross',  # baseline duplicate
    'submit_v45_',                   # post-v44 failed/frozen family
    'submit_v46', 'submit_v46b',      # frozen family if present
]

TRUSTED_SOURCES = {
    'submit_v36_gene_abs.json': 3.0,
    'submit_v39_posw_3of3_fixed.json': 2.4,
    'submit_v39_posw_3of3.json': 2.2,
    'submit_v39_posw_2of3_highfreq.json': 2.0,
    'submit_v41_precise_cv.json': 1.8,
    'submit_v41_precise_ultrasafe.json': 1.8,
    'submit_v43_llm_safe.json': 1.4,
    'submit_v43_llm_precise.json': 1.2,
}

FROZEN_TYPES = {
    'VAR-CON-CROSS',  # v44 已证明删除有效，v46b 加回也失败
}

LABEL_TRIGGERS = {
    'LOI': ['located', 'mapped', 'mapping', 'linkage', 'linked', 'chromosome', 'chr', 'region', 'locus', 'interval', 'flanking', 'near'],
    'AFF': ['associated', 'association', 'affect', 'affected', 'confers', 'confer', 'resistance', 'tolerance', 'controlled', 'increased', 'decreased'],
    'HAS': ['has', 'had', 'with', 'showed', 'exhibited', 'trait', 'phenotype'],
    'CON': ['contains', 'contained', 'consists', 'composed', 'population', 'cross', 'derived', 'including', 'include'],
    'USE': ['used', 'useful', 'using', 'marker-assisted', 'selection', 'genotyping', 'developed'],
    'OCI': ['involved', 'participate', 'during', 'response', 'expression', 'stage'],
}


def load(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding='utf-8'))


def type_key(rel: dict[str, Any]) -> str:
    return f"{rel.get('head_type')}-{rel.get('label')}-{rel.get('tail_type')}"


def rel_key(idx: int, rel: dict[str, Any]) -> tuple:
    return (
        idx,
        str(rel.get('head', '')),
        int(rel.get('head_start', -1)),
        int(rel.get('head_end', -1)),
        str(rel.get('head_type', '')),
        str(rel.get('tail', '')),
        int(rel.get('tail_start', -1)),
        int(rel.get('tail_end', -1)),
        str(rel.get('tail_type', '')),
        str(rel.get('label', '')),
    )


def rel_from_key(k: tuple) -> dict[str, Any]:
    return {
        'idx': k[0], 'head': k[1], 'head_start': k[2], 'head_end': k[3], 'head_type': k[4],
        'tail': k[5], 'tail_start': k[6], 'tail_end': k[7], 'tail_type': k[8], 'label': k[9],
    }


def all_keys(sub: list[dict[str, Any]]) -> set[tuple]:
    return {rel_key(i, r) for i, item in enumerate(sub) for r in item.get('relations', [])}


def train_freq() -> Counter:
    train = load(TRAIN)
    return Counter(type_key(r) for item in train for r in item.get('relations', []))


def deleted_keys_between(a: Path, b: Path) -> set[tuple]:
    return all_keys(load(a)) - all_keys(load(b))


def token_span_between(text: str, h0: int, h1: int, t0: int, t1: int) -> str:
    left = min(h1, t1)
    right = max(h0, t0)
    if left <= right:
        return text[left:right].lower()
    return text[max(0, min(h0, t0)-40): min(len(text), max(h1, t1)+40)].lower()


def context(text: str, h0: int, t0: int) -> str:
    s = max(0, min(h0, t0) - 90)
    e = min(len(text), max(h0, t0) + 190)
    return re.sub(r'\s+', ' ', text[s:e]).strip()


def trigger_score(label: str, text: str, between: str) -> tuple[int, str]:
    triggers = LABEL_TRIGGERS.get(label, [])
    hits = [w for w in triggers if w in between or w in text.lower()]
    return min(3, len(hits)), ','.join(hits[:6])


def valid_span(text: str, rel: dict[str, Any]) -> bool:
    try:
        return text[rel['head_start']:rel['head_end']] == rel['head'] and text[rel['tail_start']:rel['tail_end']] == rel['tail']
    except Exception:
        return False


def main() -> None:
    base = load(BASE)
    base_keys = all_keys(base)
    train_type = train_freq()
    historical_deleted = set()
    historical_deleted |= deleted_keys_between(DATA / 'submit_v36_gene_abs.json', DATA / 'submit_v41_sub_conservative.json')
    historical_deleted |= deleted_keys_between(DATA / 'submit_v41_sub_conservative.json', DATA / 'submit_v44_del_var_con_cross.json')

    sources = []
    for p in sorted(DATA.glob('submit_*.json')):
        name = p.name
        if any(x in name for x in EXCLUDE_PATTERNS):
            continue
        sources.append(p)

    support = defaultdict(list)
    exemplar = {}
    for p in sources:
        try:
            sub = load(p)
        except Exception:
            continue
        for i, item in enumerate(sub):
            for r in item.get('relations', []):
                k = rel_key(i, r)
                if k in base_keys or k in historical_deleted:
                    continue
                rel = rel_from_key(k)
                typ = f"{rel['head_type']}-{rel['label']}-{rel['tail_type']}"
                if typ in FROZEN_TYPES:
                    continue
                support[k].append(p.name)
                exemplar.setdefault(k, {'text': item.get('text', ''), 'rel': rel})

    rows = []
    for k, srcs in support.items():
        ex = exemplar[k]
        text = ex['text']
        rel = ex['rel']
        typ = f"{rel['head_type']}-{rel['label']}-{rel['tail_type']}"
        weighted = sum(TRUSTED_SOURCES.get(s, 0.25) for s in set(srcs))
        unique_sources = len(set(srcs))
        tf = train_type[typ]
        between = token_span_between(text, rel['head_start'], rel['head_end'], rel['tail_start'], rel['tail_end'])
        trig_score, trig_hits = trigger_score(rel['label'], context(text, rel['head_start'], rel['tail_start']), between)
        span_ok = valid_span(text, rel)
        same_sample_rel_count = len(base[rel['idx']].get('relations', []))
        # 高分不是自动可提交，仍需闸门。分数只用于排序。
        score = weighted + min(4, unique_sources / 2) + min(3, tf / 80) + trig_score + (1.0 if span_ok else -5.0)
        gate = 'pass' if span_ok and unique_sources >= 2 and weighted >= 2.0 and tf >= 3 and trig_score >= 1 and typ not in FROZEN_TYPES else 'review'
        rows.append({
            'score': round(score, 4),
            'gate': gate,
            'idx': rel['idx'],
            'type': typ,
            'label': rel['label'],
            'head': rel['head'],
            'head_type': rel['head_type'],
            'tail': rel['tail'],
            'tail_type': rel['tail_type'],
            'head_start': rel['head_start'],
            'head_end': rel['head_end'],
            'tail_start': rel['tail_start'],
            'tail_end': rel['tail_end'],
            'train_type_freq': tf,
            'unique_source_count': unique_sources,
            'weighted_support': round(weighted, 3),
            'trigger_score': trig_score,
            'trigger_hits': trig_hits,
            'base_sample_rel_count': same_sample_rel_count,
            'sources': ';'.join(sorted(set(srcs))),
            'context': context(text, rel['head_start'], rel['tail_start']).replace('|', ' '),
        })
    rows.sort(key=lambda x: (x['gate'] == 'pass', x['score'], x['weighted_support'], x['train_type_freq']), reverse=True)

    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with OUT_CSV.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader(); writer.writerows(rows)

    lines = ['# v47 候选证据表 2026-05-02', '']
    pass_rows = [r for r in rows if r['gate'] == 'pass']
    lines.append('## 筛选结论')
    if pass_rows:
        best = pass_rows[0]
        lines.append(f"本轮从历史提交中发现 {len(rows)} 条当前底座缺失的关系候选，其中 {len(pass_rows)} 条通过自动闸门。排序第一的候选为样本 **{best['idx']}** 的 `{best['type']}`：`{best['head']}` — `{best['label']}` — `{best['tail']}`。该候选仍需在生成前写入单候选假设卡，并且只允许生成这一个 `v47_single_*` 文件。")
    else:
        lines.append(f'本轮发现 {len(rows)} 条当前底座缺失候选，但没有候选通过自动闸门；不应生成 v47 提交文件。')
    lines.append('')
    lines.append('| 排名 | 闸门 | 得分 | 样本 | 类型 | head | label | tail | 训练频次 | 支持源数 | 加权支持 | 触发词 | 来源 |')
    lines.append('|---:|---|---:|---:|---|---|---|---|---:|---:|---:|---|---|')
    for rank, r in enumerate(rows[:30], 1):
        src_preview = ', '.join(r['sources'].split(';')[:5])
        lines.append(f"| {rank} | {r['gate']} | {r['score']:.4f} | {r['idx']} | `{r['type']}` | `{r['head']}` | `{r['label']}` | `{r['tail']}` | {r['train_type_freq']} | {r['unique_source_count']} | {r['weighted_support']:.3f} | {r['trigger_hits'] or '-'} | {src_preview} |")
    lines.append('')
    if rows:
        lines.append('## 第一候选文本证据')
        r = rows[0]
        lines.append('| 字段 | 内容 |')
        lines.append('|---|---|')
        for k in ['gate','score','idx','type','head','label','tail','train_type_freq','unique_source_count','weighted_support','trigger_hits','sources','context']:
            lines.append(f"| {k} | {str(r[k]).replace('|', ' ')} |")
        lines.append('')
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(OUT_MD)
    if rows:
        print(json.dumps(rows[0], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
