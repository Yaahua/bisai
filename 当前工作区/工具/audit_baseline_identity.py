#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""底座身份复核：确认 0.4514 底座 JSON 与 ZIP 内 submit.json 完全一致且格式稳定。"""
from __future__ import annotations

import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path('/home/ubuntu/bisai')
BASE_JSON = ROOT / '当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.json'
BASE_ZIP = ROOT / '当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.zip'
OUT_MD = ROOT / '当前工作区/记录/底座身份复核_20260502.md'
OUT_JSON = ROOT / '当前工作区/记录/底座身份复核_20260502.json'


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def load_json_bytes(path: Path) -> tuple[Any, bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode('utf-8')), raw


def rels_of(item: dict[str, Any]) -> list[Any]:
    return item.get('relation_of_mention') or item.get('relations') or []


def relation_label(rel: Any) -> str:
    if isinstance(rel, dict):
        return str(rel.get('relation') or rel.get('type') or rel.get('label') or rel.get('predicate') or 'UNKNOWN')
    if isinstance(rel, (list, tuple)) and len(rel) >= 3:
        return str(rel[2])
    return 'UNKNOWN'


def relation_key(rel: Any) -> str:
    if isinstance(rel, dict):
        h = rel.get('head') or rel.get('subject') or rel.get('entity1') or rel.get('arg1') or rel.get('h') or ''
        t = rel.get('tail') or rel.get('object') or rel.get('entity2') or rel.get('arg2') or rel.get('t') or ''
        r = relation_label(rel)
        return f'{h}\t{r}\t{t}\t{json.dumps(rel, ensure_ascii=False, sort_keys=True)}'
    return json.dumps(rel, ensure_ascii=False, sort_keys=True)


def main() -> None:
    obj_json, raw_json = load_json_bytes(BASE_JSON)
    with zipfile.ZipFile(BASE_ZIP) as zf:
        entries = [(i.filename, i.file_size, i.CRC) for i in zf.infolist()]
        zip_raw = zf.read('submit.json')
        obj_zip = json.loads(zip_raw.decode('utf-8'))

    same_canonical = canonical_bytes(obj_json) == canonical_bytes(obj_zip)
    sample_count = len(obj_json) if isinstance(obj_json, list) else None
    rel_total = 0
    non_empty = 0
    type_counter = Counter()
    rel_field_counter = Counter()
    item_field_counter = Counter()
    duplicate_relation_keys = []
    per_item_counts = []

    for idx, item in enumerate(obj_json):
        if isinstance(item, dict):
            item_field_counter.update(item.keys())
            rels = rels_of(item)
        else:
            rels = []
        if rels:
            non_empty += 1
        rel_total += len(rels)
        per_item_counts.append(len(rels))
        seen = set()
        for rel in rels:
            type_counter[relation_label(rel)] += 1
            if isinstance(rel, dict):
                rel_field_counter.update(rel.keys())
            key = relation_key(rel)
            if key in seen:
                duplicate_relation_keys.append((idx, key))
            seen.add(key)

    histogram = Counter(per_item_counts)
    result = {
        'base_json': str(BASE_JSON.relative_to(ROOT)),
        'base_zip': str(BASE_ZIP.relative_to(ROOT)),
        'json_raw_sha256': sha256_bytes(raw_json),
        'zip_submit_raw_sha256': sha256_bytes(zip_raw),
        'json_canonical_sha256': sha256_bytes(canonical_bytes(obj_json)),
        'zip_submit_canonical_sha256': sha256_bytes(canonical_bytes(obj_zip)),
        'same_canonical_content': same_canonical,
        'zip_entries': entries,
        'sample_count': sample_count,
        'non_empty_sample_count': non_empty,
        'relation_total': rel_total,
        'relation_type_counts': dict(type_counter),
        'item_field_counts': dict(item_field_counter),
        'relation_field_counts': dict(rel_field_counter),
        'relation_count_histogram': dict(sorted(histogram.items())),
        'duplicate_relation_count_within_same_sample': len(duplicate_relation_keys),
        'pass': bool(same_canonical and sample_count == 400 and rel_total == 1052 and entries == [('submit.json', len(zip_raw), entries[0][2])]),
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = []
    lines.append('# 底座身份复核 2026-05-02')
    lines.append('')
    lines.append('## 结论')
    verdict = '通过' if result['pass'] else '不通过'
    lines.append(f'底座身份复核结论：**{verdict}**。JSON 文件与 ZIP 内 `submit.json` 的规范化内容一致；当前可继续作为唯一候选派生源。' if result['pass'] else f'底座身份复核结论：**{verdict}**。必须先处理不一致项，不能生成候选。')
    lines.append('')
    lines.append('| 项目 | 值 |')
    lines.append('|---|---:|')
    lines.append(f'| 样本数 | {sample_count} |')
    lines.append(f'| 含关系样本数 | {non_empty} |')
    lines.append(f'| 关系总数 | {rel_total} |')
    lines.append(f'| JSON 与 ZIP 规范化内容一致 | {same_canonical} |')
    lines.append(f'| 样本内重复关系数 | {len(duplicate_relation_keys)} |')
    lines.append('')
    lines.append('## 哈希')
    lines.append('| 对象 | SHA256 |')
    lines.append('|---|---|')
    lines.append(f"| JSON 原始字节 | `{result['json_raw_sha256']}` |")
    lines.append(f"| ZIP 内 submit.json 原始字节 | `{result['zip_submit_raw_sha256']}` |")
    lines.append(f"| JSON 规范化 | `{result['json_canonical_sha256']}` |")
    lines.append(f"| ZIP 内 submit.json 规范化 | `{result['zip_submit_canonical_sha256']}` |")
    lines.append('')
    lines.append('## ZIP 结构')
    lines.append('| 文件 | 大小字节 | CRC |')
    lines.append('|---|---:|---:|')
    for name, size, crc in entries:
        lines.append(f'| `{name}` | {size} | {crc} |')
    lines.append('')
    lines.append('## 关系类型分布')
    lines.append('| 关系类型 | 数量 |')
    lines.append('|---|---:|')
    for k, v in type_counter.most_common():
        lines.append(f'| `{k}` | {v} |')
    lines.append('')
    lines.append('## 样本关系数分布')
    lines.append('| 每样本关系数 | 样本数 |')
    lines.append('|---:|---:|')
    for k, v in sorted(histogram.items()):
        lines.append(f'| {k} | {v} |')
    lines.append('')
    lines.append('## 字段概览')
    lines.append('| 顶层样本字段 | 出现次数 |')
    lines.append('|---|---:|')
    for k, v in item_field_counter.most_common():
        lines.append(f'| `{k}` | {v} |')
    lines.append('')
    lines.append('| 关系字段 | 出现次数 |')
    lines.append('|---|---:|')
    for k, v in rel_field_counter.most_common():
        lines.append(f'| `{k}` | {v} |')
    lines.append('')
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(OUT_MD)


if __name__ == '__main__':
    main()
