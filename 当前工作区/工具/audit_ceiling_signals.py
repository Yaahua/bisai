#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只读审计：汇总当前可信底座、zip 结构、关系数量和已知提交分数信号。"""
from __future__ import annotations

import json
import re
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path('/home/ubuntu/bisai')
BASE_JSON = ROOT / '当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.json'
BASE_ZIP = ROOT / '当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.zip'
REPORTS = [
    ROOT / '当前工作区/统一计划_精简版_20260501.md',
    ROOT / '当前工作区/记录/失败禁忌_v46_v46b三连0416记录.md',
    ROOT / '分析报告/36_失败后极简重启计划_20260501.md',
    ROOT / '分析报告/35_广域学术API修订版大跃进计划_20260430.md',
    ROOT / 'README.md',
]
OUT = ROOT / '当前工作区/记录/技术天花板审计_20260501.md'


def load_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def iter_relations(data):
    if isinstance(data, list):
        for i, item in enumerate(data):
            rels = item.get('relation_of_mention') or item.get('relations') or []
            yield i, item, rels
    elif isinstance(data, dict):
        items = data.get('result') or data.get('data') or data.get('submit') or []
        for i, item in enumerate(items):
            rels = item.get('relation_of_mention') or item.get('relations') or []
            yield i, item, rels


def relation_label(rel):
    if isinstance(rel, dict):
        return rel.get('relation') or rel.get('type') or rel.get('label') or rel.get('predicate') or 'UNKNOWN'
    if isinstance(rel, (list, tuple)) and len(rel) >= 3:
        return str(rel[2])
    return 'UNKNOWN'


def main():
    data = load_json(BASE_JSON)
    rows = list(iter_relations(data))
    rel_counter = Counter()
    non_empty = 0
    total_rel = 0
    for _, _, rels in rows:
        if rels:
            non_empty += 1
        total_rel += len(rels)
        for rel in rels:
            rel_counter[relation_label(rel)] += 1

    scores = []
    for rp in REPORTS:
        if not rp.exists():
            continue
        txt = rp.read_text(encoding='utf-8', errors='ignore')
        for m in re.finditer(r'(0\.45\d{2}|0\.416\d|0\.4560)', txt):
            start = max(0, m.start()-70)
            end = min(len(txt), m.end()+70)
            scores.append((rp.name, m.group(1), txt[start:end].replace('\n', ' ')))

    with zipfile.ZipFile(BASE_ZIP) as zf:
        zip_entries = [(info.filename, info.file_size) for info in zf.infolist()]

    lines = []
    lines.append('# 技术天花板审计摘要 2026-05-01')
    lines.append('')
    lines.append('## 底座身份')
    lines.append(f'- JSON 文件：`{BASE_JSON.relative_to(ROOT)}`')
    lines.append(f'- ZIP 文件：`{BASE_ZIP.relative_to(ROOT)}`')
    lines.append(f'- JSON 顶层类型：`{type(data).__name__}`')
    lines.append(f'- 样本数：`{len(rows)}`')
    lines.append(f'- 含关系样本数：`{non_empty}`')
    lines.append(f'- 关系总数：`{total_rel}`')
    lines.append('')
    lines.append('## ZIP 内部结构')
    lines.append('| 文件 | 大小字节 |')
    lines.append('|---|---:|')
    for name, size in zip_entries:
        lines.append(f'| `{name}` | {size} |')
    lines.append('')
    lines.append('## 底座关系类型 Top 20')
    lines.append('| 关系类型 | 数量 |')
    lines.append('|---|---:|')
    for k, v in rel_counter.most_common(20):
        lines.append(f'| `{k}` | {v} |')
    lines.append('')
    lines.append('## 报告中出现的关键分数信号')
    lines.append('| 来源文件 | 分数 | 上下文摘录 |')
    lines.append('|---|---:|---|')
    seen = set()
    for name, score, ctx in scores:
        key = (name, score, ctx[:60])
        if key in seen:
            continue
        seen.add(key)
        lines.append(f'| `{name}` | {score} | {ctx} |')
    lines.append('')
    lines.append('## 审计解释')
    lines.append('当前底座是唯一可继续派生的可信对象；三次 0.416x 结果与 0.4514 底座相差约 0.035，说明错误候选并非小幅波动，而是会破坏公开榜关键命中单元。')
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT)


if __name__ == '__main__':
    main()
