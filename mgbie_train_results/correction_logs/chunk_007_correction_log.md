# MGBIE 数据块 chunk_007 全量修正记录

本文档记录了对 `chunk_007.json` 初步分类结果的修正过程。修正主要依据 `chunk_007_audit.md` 中提出的对抗性审查建议。

## 1. 修正摘要

- **采纳的建议**: 4
- **未采纳的建议**: 0
- **修正总结**: 本次修正采纳了全部4条对抗性审查建议，涉及实体拆分、关系方向调整、实体边界优化和实体类型修正。所有修改均有权威依据支持，显著提升了数据标注的准确性和规范性。

## 2. 采纳的修改建议

### 2.1. 建议1：【拆分审查】复合基因实体未拆分

- **位置**: Sample 10 (Index 9)
- **审查建议**: 将复合实体 `SbWRKY50 gene (Sb09g005700)` 拆分为两个独立的 `GENE` 实体 `SbWRKY50` 和 `Sb09g005700`，并移除描述性词语 “gene”。
- **采纳理由**: 该建议符合 [TaeC-2024] 的最大共识原则，即当一个概念有多种指代方式时，应分别标注以保留最多信息。同时，去除通用描述词能确保实体词块的简洁性。
- **修正前**: 
  - Entity: `{"start": 18, "end": 44, "text": "SbWRKY50 gene (Sb09g005700)", "label": "GENE"}`
  - Relations: `("SbWRKY50 gene (Sb09g005700)", AFF, "transcriptional activation activity")`, `("salt stress", AFF, "SbWRKY50 gene (Sb09g005700)")`
- **修正后**:
  - Entities: 
    - `{"start": 18, "end": 26, "text": "SbWRKY50", "label": "GENE"}`
    - `{"start": 33, "end": 43, "text": "Sb09g005700", "label": "GENE"}`
  - Relations:
    - `("SbWRKY50", AFF, "transcriptional activation activity")`
    - `("Sb09g005700", AFF, "transcriptional activation activity")`
    - `("salt stress", AFF, "SbWRKY50")`

### 2.2. 建议2：【语义审查】AFF关系方向颠倒

- **位置**: Sample 6 (Index 5)
- **审查建议**: 将关系 `("Flowering time", AFF, "QTL")` 的方向颠倒为 `("QTL", AFF, "Flowering time")`。
- **采纳理由**: 依据 MGBIE 任务定义，`AFF` 关系中头部必须是影响发起方 (`ABS/GENE/MRK/QTL`)，尾部是被影响的性状 (`TRT`)。原标注 `(TRT, AFF, QTL)` 违反了此定义。
- **修正前**: `{"head": "Flowering time", ..., "tail": "QTL", ..., "label": "AFF"}`
- **修正后**: `{"head": "QTL", ..., "tail": "Flowering time", ..., "label": "AFF"}`

### 2.3. 建议3：【词块审查】实体包含不必要的描述词

- **位置**: Sample 5 (Index 4)
- **审查建议**: 将实体 `marker OPA 12(383)` 的边界修正为 `OPA 12(383)`。
- **采纳理由**: 依据 MGBIE 词块审查标准，实体应保持简洁，去除通用的描述性词语（如 “marker”）。
- **修正前**: `{"start": 4, "end": 22, "text": "marker OPA 12(383)", "label": "MRK"}`
- **修正后**: `{"start": 11, "end": 22, "text": "OPA 12(383)", "label": "MRK"}`
- **关联修正**: 相关的 `LOI` 关系也已同步更新。

### 2.4. 建议4：【知识审查】实体类型判断错误

- **位置**: Sample 3 (Index 2)
- **审查建议**: 删除被错误分类为 `BM` (育种方法) 的实体 `ddRAD-seq`。
- **采纳理由**: 依据 [NY/T 2467-2025] 对分子标记法的定义，`ddRAD-seq` 是一种用于开发分子标记的技术手段，而非育种流程中的宏观步骤。将其归类为 `BM` 是对育种流程的误解。正确的操作是不对该实体进行标注。
- **修正前**: `{"start": 174, "end": 183, "text": "ddRAD-seq", "label": "BM"}`
- **修正后**: 该实体及相关关系已被删除。

## 3. 未采纳的修改建议

本次修正采纳了对抗性审查报告中提出的所有建议，无未采纳项。
