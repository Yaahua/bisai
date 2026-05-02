#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 v47 单候选：只在样本 249 新增一条 QTL-LOI-TRT 关系。"""
from __future__ import annotations

import copy
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path('/home/ubuntu/bisai')
BASE = ROOT / '当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.json'
OUT_DIR = ROOT / '当前工作区/候选/v47_single_add_qtl_loi_trt_249_grain_his'
OUT_JSON = OUT_DIR / 'submit_v47_single_add_qtl_loi_trt_249_grain_his.json'
OUT_ZIP = OUT_DIR / 'submit_v47_single_add_qtl_loi_trt_249_grain_his.zip'
OUT_DIFF = OUT_DIR / 'diff_report.md'

NEW_REL = {
    'head': 'QTLs',
    'head_start': 388,
    'head_end': 392,
    'head_type': 'QTL',
    'tail': 'grain HIS content',
    'tail_start': 4,
    'tail_end': 21,
    'tail_type': 'TRT',
    'label': 'LOI',
}
IDX = 249


def rel_key(rel: dict) -> tuple:
    return (
        rel.get('head'), rel.get('head_start'), rel.get('head_end'), rel.get('head_type'),
        rel.get('tail'), rel.get('tail_start'), rel.get('tail_end'), rel.get('tail_type'), rel.get('label')
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = json.loads(BASE.read_text(encoding='utf-8'))
    cand = copy.deepcopy(base)
    text = cand[IDX]['text']
    assert text[NEW_REL['head_start']:NEW_REL['head_end']] == NEW_REL['head'], 'head span mismatch'
    assert text[NEW_REL['tail_start']:NEW_REL['tail_end']] == NEW_REL['tail'], 'tail span mismatch'
    before = list(cand[IDX].get('relations', []))
    before_keys = {rel_key(r) for r in before}
    assert rel_key(NEW_REL) not in before_keys, 'relation already exists in baseline'
    cand[IDX].setdefault('relations', []).append(copy.deepcopy(NEW_REL))
    after = cand[IDX]['relations']
    assert len(after) == len(before) + 1, 'unexpected relation count delta'
    OUT_JSON.write_text(json.dumps(cand, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with zipfile.ZipFile(OUT_ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(OUT_JSON, arcname='submit.json')

    base_rel_count = sum(len(x.get('relations', [])) for x in base)
    cand_rel_count = sum(len(x.get('relations', [])) for x in cand)
    lines = [
        '# v47 单候选 diff 报告',
        '',
        '| 字段 | 值 |',
        '|---|---|',
        f'| 底座文件 | `{BASE.relative_to(ROOT)}` |',
        f'| 候选 JSON | `{OUT_JSON.relative_to(ROOT)}` |',
        f'| 候选 ZIP | `{OUT_ZIP.relative_to(ROOT)}` |',
        f'| 底座关系数 | {base_rel_count} |',
        f'| 候选关系数 | {cand_rel_count} |',
        f'| 净变化 | +{cand_rel_count - base_rel_count} |',
        f'| 修改样本 | {IDX} |',
        f'| JSON SHA256 | `{sha256(OUT_JSON)}` |',
        f'| ZIP SHA256 | `{sha256(OUT_ZIP)}` |',
        '',
        '## 新增关系',
        '',
        '| 样本 | head | label | tail | 类型 | span |',
        '|---:|---|---|---|---|---|',
        f"| {IDX} | `{NEW_REL['head']}` | `{NEW_REL['label']}` | `{NEW_REL['tail']}` | `{NEW_REL['head_type']}-{NEW_REL['label']}-{NEW_REL['tail_type']}` | `{NEW_REL['head_start']}-{NEW_REL['head_end']} / {NEW_REL['tail_start']}-{NEW_REL['tail_end']}` |",
        '',
        '## 样本文本',
        '',
        '> ' + text,
    ]
    OUT_DIFF.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(OUT_JSON)
    print(OUT_ZIP)
    print(OUT_DIFF)


if __name__ == '__main__':
    main()
