#!/usr/bin/env python3
"""
双重验证脚本：检查修订后 JSON 中是否有残留非法关系类型。
依据 K8 分类体系的关系类型约束进行验证。
"""

import json
import os

RESULT_DIR = "/home/ubuntu/bisai_clone/数据/训练集/修订结果"

# K8 关系类型合法约束（head_type -> tail_type -> label）
# 格式：label -> [(合法 head_type 集合, 合法 tail_type 集合)]
LEGAL_RELATION_TYPES = {
    "AFF": [
        ({"GENE", "ABS", "BIS", "TRT"}, {"TRT"}),  # TRT->TRT 有先例，保留
    ],
    "HAS": [
        ({"VAR", "CROP", "CROSS", "GENE"}, {"TRT"}),
    ],
    "CON": [
        ({"CROP"}, {"VAR"}),
        ({"GENE"}, {"GENE"}),  # GENE全称 -> GENE缩写
        ({"VAR"}, {"GENE"}),   # VAR -> GENE (包含关系)
        ({"CROSS"}, {"VAR"}),  # 特殊情况：CROSS 包含 VAR（已在 audit 中删除，此处仅作记录）
    ],
    "LOI": [
        ({"QTL", "GENE"}, {"TRT", "CHR"}),
    ],
    "USE": [
        ({"VAR"}, {"BM"}),
    ],
    "LOC": [
        ({"GENE"}, {"CHR"}),
    ],
}

# 已知合法的特殊情况（不报错）
KNOWN_EXCEPTIONS = [
    # BIS -> CROP AFF（病原体侵染作物，K6 有先例）
    ("AFF", "BIS", "CROP"),
    # TRT -> TRT AFF（性状间相关性，K6 有先例）
    ("AFF", "TRT", "TRT"),
    # ABS -> TRT AFF（胁迫影响性状，合法）
    ("AFF", "ABS", "TRT"),
    # GENE -> TRT AFF（基因影响性状，合法）
    ("AFF", "GENE", "TRT"),
    # QTL -> TRT LOI（QTL 定位性状，合法）
    ("LOI", "QTL", "TRT"),
    # QTL -> CHR LOI（QTL 定位染色体，合法）
    ("LOI", "QTL", "CHR"),
    # GENE -> CHR LOI（基因定位染色体，合法）
    ("LOI", "GENE", "CHR"),
    # GENE -> TRT LOI（基因定位性状，合法）
    ("LOI", "GENE", "TRT"),
    # CROP -> VAR CON（作物包含品种，合法）
    ("CON", "CROP", "VAR"),
    # GENE -> GENE CON（基因全称缩写，合法）
    ("CON", "GENE", "GENE"),
    # VAR -> BM USE（品种使用方法，合法）
    ("USE", "VAR", "BM"),
    # GENE -> TRT HAS（基因拥有性状，合法）
    ("HAS", "GENE", "TRT"),
    # VAR -> TRT HAS（品种拥有性状，合法）
    ("HAS", "VAR", "TRT"),
    # CROP -> TRT HAS（作物拥有性状，合法）
    ("HAS", "CROP", "TRT"),
    # CROSS -> TRT HAS（杂交组合拥有性状，合法）
    ("HAS", "CROSS", "TRT"),
    # CHR -> CHR LOI（染色体区域定位，合法）
    ("LOI", "CHR", "CHR"),
    # MRK -> CHR LOI（标记定位染色体，待确认）- 已在 audit 中标为建议修改
    # ABS -> VAR AFF（胁迫影响品种，待确认）- 已在 audit 中删除
]

KNOWN_EXCEPTION_SET = set(KNOWN_EXCEPTIONS)


def validate_chunk(chunk_id):
    path = os.path.join(RESULT_DIR, f"{chunk_id}_corrected.json")
    if not os.path.exists(path):
        print(f"  文件不存在: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    issues = []
    for i, sample in enumerate(data):
        for r in sample.get("relations", []):
            label = r.get("label", "")
            head_type = r.get("head_type", "")
            tail_type = r.get("tail_type", "")

            # 检查是否为已知合法情况
            if (label, head_type, tail_type) in KNOWN_EXCEPTION_SET:
                continue

            # 检查是否为非法类型
            is_illegal = False
            illegal_reason = ""

            if label == "AFF":
                if tail_type not in {"TRT"}:
                    if (label, head_type, tail_type) not in KNOWN_EXCEPTION_SET:
                        is_illegal = True
                        illegal_reason = f"AFF tail 应为 TRT，实际为 {tail_type}"
            elif label == "HAS":
                if tail_type not in {"TRT"}:
                    is_illegal = True
                    illegal_reason = f"HAS tail 应为 TRT，实际为 {tail_type}"
            elif label == "CON":
                legal_pairs = [("CROP", "VAR"), ("GENE", "GENE"), ("VAR", "GENE")]
                if (head_type, tail_type) not in legal_pairs:
                    is_illegal = True
                    illegal_reason = f"CON({head_type},{tail_type}) 不是合法类型"
            elif label == "LOI":
                if head_type not in {"QTL", "GENE", "CHR"}:
                    is_illegal = True
                    illegal_reason = f"LOI head 应为 QTL/GENE/CHR，实际为 {head_type}"
                elif tail_type not in {"TRT", "CHR"}:
                    is_illegal = True
                    illegal_reason = f"LOI tail 应为 TRT/CHR，实际为 {tail_type}"
            elif label == "USE":
                if head_type != "VAR" or tail_type != "BM":
                    is_illegal = True
                    illegal_reason = f"USE({head_type},{tail_type}) 不是合法类型"

            if is_illegal:
                issues.append({
                    "chunk_id": chunk_id,
                    "sample_idx": i,
                    "relation": r,
                    "reason": illegal_reason
                })

    return issues


def main():
    chunks = [f"chunk_0{i:02d}" for i in range(21, 31)]
    all_issues = []

    print("双重验证开始...\n")
    for chunk_id in chunks:
        issues = validate_chunk(chunk_id)
        if issues:
            print(f"[{chunk_id}] 发现 {len(issues)} 个残留问题:")
            for issue in issues:
                r = issue["relation"]
                print(f"  样本{issue['sample_idx']}: {r.get('label')}({r.get('head_type')},{r.get('tail_type')}) - {issue['reason']}")
                print(f"    head: {r.get('head')} @{r.get('head_start')}:{r.get('head_end')}")
                print(f"    tail: {r.get('tail')} @{r.get('tail_start')}:{r.get('tail_end')}")
            all_issues.extend(issues)
        else:
            print(f"[{chunk_id}] 验证通过 ✓")

    print(f"\n验证完成。共发现 {len(all_issues)} 个残留问题。")
    return all_issues


if __name__ == "__main__":
    main()
