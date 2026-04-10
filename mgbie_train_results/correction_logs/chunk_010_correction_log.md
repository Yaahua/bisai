# MGBIE 数据块 chunk_010.json 修正记录

## 1. 修正摘要

本次修正根据对抗性审查报告 `chunk_010_audit.md` 对初步分类的 `chunk_010.json` 文件进行了全面修订。总共采纳了 **5** 项审查建议，未拒绝任何建议。修正的核心是提升实体边界的精确性和分类的知识准确性，确保所有标注严格遵循项目定义的实体和关系模式。

- **采纳的建议数量**: 5
- **未采纳的建议数量**: 0

## 2. 采纳的修正详情

### 采纳建议 1：词块边界修正 (Sample ID: 1)

- **修正内容**: 将实体 `"chromosome 2H"` (CHR) 的边界从 `65-78` 修正为 `76-78`，实体文本相应修改为 `"2H"`。
- **修正前**: `{"start": 65, "end": 78, "text": "chromosome 2H", "label": "CHR"}`
- **修正后**: `{"start": 76, "end": 78, "text": "2H", "label": "CHR"}`
- **采纳理由**: 采纳审查建议。根据 [QTL-Nomen] 命名习惯，"chromosome" 是描述性词语，不应包含在染色体标识符实体中。核心标识符是 `2H`。

### 采纳建议 2：知识分类修正 (Sample ID: 2)

- **修正内容**: 删除了将 `"G protein gamma-subunit"` 错误分类为 `TRT` 的实体。同时，删除了所有与此实体相关的关系。
- **修正前**: 存在实体 `{"start": 123, "end": 146, "text": "G protein gamma-subunit", "label": "TRT"}` 及相关联的 `AFF` 关系。
- **修正后**: 该实体及相关关系被完全移除。
- **采纳理由**: 采纳审查建议。根据分子生物学知识，蛋白质是基因的产物，其本身不是一个性状（Trait）。将其保留会违反 [SUN-2019] 中关于基因、蛋白质和性状关系的基本原则。

### 采纳建议 3：知识分类修正 (Sample ID: 3)

- **修正内容**: 将实体 `"18 chromosomes"` 和 `"Eleven chromosomes"` 的标签从 `CHR` 修改为 `TRT`。
- **修正前**:
  - `{"start": 75, "end": 89, "text": "18 chromosomes", "label": "CHR"}`
  - `{"start": 108, "end": 126, "text": "Eleven chromosomes", "label": "CHR"}`
- **修正后**:
  - `{"start": 75, "end": 89, "text": "18 chromosomes", "label": "TRT"}`
  - `{"start": 108, "end": 126, "text": "Eleven chromosomes", "label": "TRT"}`
- **采纳理由**: 采纳审查建议。`CHR` 标签应用于具体的染色体编号，而对染色体数量的描述是物种的核型性状，应归类为 `TRT`，此依据参考了 [LU-Sorghum-2006] 的描述。

### 采纳建议 4：词块边界修正 (Sample ID: 5)

- **修正内容**: 将实体 `"2 morphological markers"` (MRK) 的边界从 `59-81` 修正为 `61-81`，实体文本相应修改为 `"morphological markers"`。
- **修正前**: `{"start": 59, "end": 81, "text": "2 morphological markers", "label": "MRK"}`
- **修正后**: `{"start": 61, "end": 81, "text": "morphological markers", "label": "MRK"}`
- **采纳理由**: 采纳审查建议。根据词块审查标准，数量词（如“2”）不应包含在实体边界内。标记的核心是 `morphological markers`。

### 采纳建议 5：关系语义修正 (Sample ID: 9)

- **修正内容**: 删除了一个不符合 `AFF` 关系定义的实例 `(ABS, GENE)`。
- **修正前**: 存在关系 `{"head": "flooding stress", "head_type": "ABS", "tail": "C2H2 gene", "tail_type": "GENE", "label": "AFF"}`。
- **修正后**: 该关系被删除。
- **采纳理由**: 采纳审查建议。项目定义 `AFF` 关系的结构为 `head(ABS/GENE/MRK/QTL) -> tail(TRT)`。原关系 `(ABS -> GENE)` 的 `tail` 类型错误，因此是无效关系，予以删除。

## 3. 未采纳的建议

本次修正采纳了审查文档中提出的所有建议，无未采纳项。
