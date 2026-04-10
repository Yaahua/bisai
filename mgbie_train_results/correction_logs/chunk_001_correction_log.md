# MGBIE 数据块 001 修正记录

## 1. 修正概述

本文件记录了对 `chunk_001.json` 的修正过程。修正主要依据 `chunk_001_audit.md` 中提供的审查建议。本次修正共采纳了 **7** 条建议，未拒绝任何建议。

| 修正类别 | 数量 |
| :--- | :--- |
| 采纳的建议 | 7 |
| 拒绝的建议 | 0 |

## 2. 修正详情

### Sample 3

*   **采纳建议 1 (拆分审查)**
    *   **内容**: 将实体 `powdery mildew resistance genes` 拆分为 `powdery mildew resistance` (TRT) 和 `genes` (GENE)。
    *   **理由**: 采纳审查意见。复合概念应被拆分以保留性状和遗传实体的独立信息。
    *   **修正前**:
        ```json
        {
            "text": "powdery mildew resistance genes",
            "label": "GENE",
            "start": 54,
            "end": 85
        }
        ```
    *   **修正后**:
        ```json
        {
            "text": "powdery mildew resistance",
            "label": "TRT",
            "start": 54,
            "end": 79
        },
        {
            "text": "genes",
            "label": "GENE",
            "start": 80,
            "end": 85
        }
        ```

*   **采纳建议 2 (语义审查)**
    *   **内容**: 调整关系 `AFF(E. graminis, powdery mildew resistance)` 的方向为 `AFF(powdery mildew resistance, E. graminis)`。
    *   **理由**: 采纳审查意见。在育种领域，将性状作为主体更能精确表示其与胁迫的相互作用。
    *   **修正前**:
        ```json
        {
            "head": "E. graminis", "head_type": "BIS",
            "tail": "powdery mildew resistance", "tail_type": "TRT",
            "label": "AFF"
        }
        ```
    *   **修正后**:
        ```json
        {
            "head": "powdery mildew resistance", "head_type": "TRT",
            "tail": "E. graminis", "tail_type": "BIS",
            "label": "AFF"
        }
        ```

### Sample 4

*   **采纳建议 3 (知识审查)**
    *   **内容**: 将实体 `sweet sorghum` 的标签从 `VAR` 修改为 `CROP`。
    *   **理由**: 采纳审查意见。在没有明确品种信息时，“甜高粱”应被视为作物亚种（CROP）。
    *   **修正前**: `{"text": "sweet sorghum", "label": "VAR"}`
    *   **修正后**: `{"text": "sweet sorghum", "label": "CROP"}`

### Sample 7

*   **采纳建议 4 (知识审查)**
    *   **内容**: 实体 `ribosome` 的标签从 `GENE` 修正。审查建议为 `GST`，但该标签不存在于当前分类体系。根据审查依据，核糖体是细胞结构而非基因，因此决定删除此实体。
    *   **理由**: 采纳审查的核心逻辑。由于 `GST` 标签不可用，最合理的处理是移除该错误分类的实体。
    *   **修正前**: `{"text": "ribosome", "label": "GENE"}`
    *   **修正后**: (实体被删除)

*   **采纳建议 5 (知识审查)**
    *   **内容**: 将实体 `thermogenesis` 的标签从 `TRT` 修改为 `BIS`。
    *   **理由**: 采纳审查意见。“产热”是生物过程，用 `BIS` 描述更准确。
    *   **修正前**: `{"text": "thermogenesis", "label": "TRT"}`
    *   **修正后**: `{"text": "thermogenesis", "label": "BIS"}`

### Sample 8

*   **采纳建议 6 (词块审查)**
    *   **内容**: 将实体 `QTLs` 的边界从 `(9, 13)` 修正为 `(9, 12)`，文本为 `QTL`。
    *   **理由**: 采纳审查意见。实体应为核心术语，不包含复数形式。
    *   **修正前**: `{"text": "QTLs", "start": 9, "end": 13}`
    *   **修正后**: `{"text": "QTL", "start": 9, "end": 12}`

*   **采纳建议 7 (词块审查)**
    *   **内容**: 将实体 `drought tolerance traits` 的边界从 `(31, 54)` 修正为 `(31, 48)`，文本为 `drought tolerance`。
    *   **理由**: 采纳审查意见。去除冗余的描述性后缀“traits”。
    *   **修正前**: `{"text": "drought tolerance traits", "start": 31, "end": 54}`
    *   **修正后**: `{"text": "drought tolerance", "start": 31, "end": 48}`

## 3. 总结

所有审查建议均被采纳并实施。修正后的 `chunk_001_corrected.json` 文件反映了上述更改，提升了数据标注的准确性和一致性。
