#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""还原历史涨分链：v36 0.4487 -> v41 0.4510 -> v44 0.4514。"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path('/home/ubuntu/bisai')
DATA = ROOT / '数据/A榜'
TRAIN = ROOT / '数据/官方原始数据/train.json'
OUT_MD = ROOT / '当前工作区/记录/历史涨分链审计_20260502.md'
OUT_JSON = ROOT / '当前工作区/记录/历史涨分链审计_20260502.json'

VERSIONS = [
    ('v36_gene_abs', DATA / 'submit_v36_gene_abs.json', 0.4487, 'ABS-AFF-GENE 加法后底座'),
    ('v41_sub_conservative', DATA / 'submit_v41_sub_conservative.json', 0.4510, '保守减法，删 25 条可疑关系'),
    ('v44_del_var_con_cross', DATA / 'submit_v44_del_var_con_cross.json', 0.4514, '删除 4 条 VAR-CON-CROSS'),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


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


def type_key(rel: dict[str, Any]) -> str:
    return f"{rel.get('head_type')}-{rel.get('label')}-{rel.get('tail_type')}"


def rel_table(sub: list[dict[str, Any]]) -> dict[tuple, dict[str, Any]]:
    out = {}
    for i, item in enumerate(sub):
        for rel in item.get('relations', []):
            out[rel_key(i, rel)] = {'idx': i, 'text': item.get('text', ''), 'rel': rel, 'type': type_key(rel)}
    return out


def stats(sub: list[dict[str, Any]]) -> dict[str, Any]:
    counts = [len(x.get('relations', [])) for x in sub]
    types = Counter(type_key(r) for item in sub for r in item.get('relations', []))
    return {
        'samples': len(sub),
        'non_empty': sum(c > 0 for c in counts),
        'relations': sum(counts),
        'avg_rel': round(sum(counts) / len(counts), 4),
        'type_counts': dict(types),
    }


def train_type_freq() -> Counter:
    train = load_json(TRAIN)
    return Counter(type_key(r) for item in train for r in item.get('relations', []))


def short_text(text: str, head_start: int, tail_start: int) -> str:
    pos = max(0, min([p for p in [head_start, tail_start] if p >= 0] or [0]) - 60)
    return text[pos:pos+180].replace('\n', ' ')


def diff_versions(a_name: str, a: list[dict[str, Any]], b_name: str, b: list[dict[str, Any]]) -> dict[str, Any]:
    ta, tb = rel_table(a), rel_table(b)
    removed_keys = sorted(set(ta) - set(tb))
    added_keys = sorted(set(tb) - set(ta))
    removed = [ta[k] for k in removed_keys]
    added = [tb[k] for k in added_keys]
    return {
        'from': a_name,
        'to': b_name,
        'removed_count': len(removed),
        'added_count': len(added),
        'removed_type_counts': dict(Counter(x['type'] for x in removed)),
        'added_type_counts': dict(Counter(x['type'] for x in added)),
        'removed_examples': removed,
        'added_examples': added,
    }


def main() -> None:
    loaded = [(name, load_json(path), score, note, path) for name, path, score, note in VERSIONS]
    train_freq = train_type_freq()
    version_stats = []
    for name, sub, score, note, path in loaded:
        s = stats(sub)
        s.update({'name': name, 'score': score, 'note': note, 'path': str(path.relative_to(ROOT))})
        version_stats.append(s)
    diffs = []
    for (a_name, a_sub, *_), (b_name, b_sub, *__) in zip(loaded, loaded[1:]):
        diffs.append(diff_versions(a_name, a_sub, b_name, b_sub))

    result = {'versions': version_stats, 'diffs': []}
    for d in diffs:
        slim = {k: v for k, v in d.items() if not k.endswith('_examples')}
        result['diffs'].append(slim)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = ['# 历史涨分链审计 2026-05-02', '']
    lines.append('## 结论')
    lines.append('本次审计确认，当前可信涨分链只有两段可直接归因：`v36_gene_abs` 到 `v41_sub_conservative` 的 25 条保守删除带来约 **+0.0023**，`v41_sub_conservative` 到 `v44_del_var_con_cross` 的 4 条 `VAR-CON-CROSS` 删除带来约 **+0.0004**。由于 v46/v46b 已经证明后续删除与旧体系加法会跌至 0.416x，新的 v47 不应复用删除逻辑，而应只把这两段作为历史证据，不把它们外推成“继续删低频”。')
    lines.append('')
    lines.append('| 版本 | 已知分数 | 样本数 | 含关系样本 | 关系数 | 均值 | 说明 |')
    lines.append('|---|---:|---:|---:|---:|---:|---|')
    for s in version_stats:
        lines.append(f"| `{s['name']}` | {s['score']:.4f} | {s['samples']} | {s['non_empty']} | {s['relations']} | {s['avg_rel']:.4f} | {s['note']} |")
    lines.append('')
    lines.append('## 可归因差异')
    lines.append('| 迁移 | 分数变化 | 删除数 | 新增数 | 删除类型摘要 | 新增类型摘要 |')
    lines.append('|---|---:|---:|---:|---|---|')
    for i, d in enumerate(diffs):
        score_delta = loaded[i+1][2] - loaded[i][2]
        rem = ', '.join(f'{k}:{v}' for k, v in Counter(d['removed_type_counts']).items()) or '无'
        add = ', '.join(f'{k}:{v}' for k, v in Counter(d['added_type_counts']).items()) or '无'
        lines.append(f"| `{d['from']}` → `{d['to']}` | {score_delta:+.4f} | {d['removed_count']} | {d['added_count']} | {rem} | {add} |")
    lines.append('')
    for d in diffs:
        lines.append(f"## `{d['from']}` → `{d['to']}` 关系级明细")
        lines.append('')
        lines.append('### 删除关系')
        lines.append('| 样本 | 类型 | 训练集频次 | head | label | tail | 文本片段 |')
        lines.append('|---:|---|---:|---|---|---|---|')
        for x in d['removed_examples']:
            r = x['rel']
            snippet = short_text(x['text'], int(r.get('head_start', -1)), int(r.get('tail_start', -1))).replace('|', ' ')
            lines.append(f"| {x['idx']} | `{x['type']}` | {train_freq[x['type']]} | `{r.get('head')}` | `{r.get('label')}` | `{r.get('tail')}` | {snippet} |")
        if not d['removed_examples']:
            lines.append('| - | - | - | - | - | - | - |')
        lines.append('')
        lines.append('### 新增关系')
        lines.append('| 样本 | 类型 | 训练集频次 | head | label | tail | 文本片段 |')
        lines.append('|---:|---|---:|---|---|---|---|')
        for x in d['added_examples']:
            r = x['rel']
            snippet = short_text(x['text'], int(r.get('head_start', -1)), int(r.get('tail_start', -1))).replace('|', ' ')
            lines.append(f"| {x['idx']} | `{x['type']}` | {train_freq[x['type']]} | `{r.get('head')}` | `{r.get('label')}` | `{r.get('tail')}` | {snippet} |")
        if not d['added_examples']:
            lines.append('| - | - | - | - | - | - | - |')
        lines.append('')
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(OUT_MD)


if __name__ == '__main__':
    main()
