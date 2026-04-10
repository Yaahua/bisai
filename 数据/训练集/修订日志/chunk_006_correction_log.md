# MGBIE 数据块 006 修正日志

## 1. 修正摘要

本次修正任务采纳了对抗性审查报告中提出的全部8项修改建议。修正内容主要集中在以下几个方面：

- **实体类型修正**：将错误的性状（TRT）标注，如“differentially expressed genes (DEGs)”，修正为基因（GENE）。
- **复合实体拆分**：将“drought-responsive genes”和“salt tolerance gene”等复合实体拆分为独立的性状（TRT）和基因（GENE）实体。
- **关系修正与删除**：修正了AFF和CON关系的方向和适用范围，并删除了不符合定义或缺乏明确指代对象的无效关系。
- **实体边界优化**：将实体及其缩写（如“kernel number per spike (KNPS)”）合并为一个完整的实体，确保信息完整性。

所有修正均依据审查报告中引用的权威依据（如[CGSNL-2011]、[TaeC-2024]）和MGBIE分类体系的定义进行。未发现需要拒绝的审查建议。

## 2. 逐项修正详情

### Sample 3 (Index 2)

- **采纳建议**: 删除关系 `{"head": "drought stress", "tail": "drought-tolerant", "label": "AFF"}`。
- **修正理由**: 审查建议指出，此关系语义上应为非生物胁迫（ABS）影响承载性状的品种（VAR），但原文未明确指出该品种。因此，该关系因缺乏明确的受影响对象而被删除。此理由充分，予以采纳。
- **修正对比**:
  - **修正前**: `"relations": [..., {"head": "drought stress", "head_start": 157, "head_end": 171, "head_type": "ABS", "tail": "drought-tolerant", "tail_start": 125, "tail_end": 141, "tail_type": "TRT", "label": "AFF"}]`
  - **修正后**: 该关系被移除。

### Sample 4 (Index 3)

- **采纳建议**: 
  1. 将实体 `differentially expressed genes` 和 `DEGs` 的标签从 `TRT` 修正为 `GENE`。
  2. 将复合实体 `drought-responsive genes` 拆分为 `drought-responsive` (TRT) 和 `genes` (GENE)。
- **修正理由**: 审查依据[CGSNL-2011]指出，DEGs是基因的集合，应标注为GENE。同时，依据[TaeC-2024]的最大共识原则，复合词应进行拆分。此建议符合分类规范，予以采纳。
- **修正对比**:
  - **修正前**: `{"text": "differentially expressed genes", "label": "TRT"}`, `{"text": "DEGs", "label": "TRT"}`, `{"text": "drought-responsive genes", "label": "TRT"}`
  - **修正后**: `{"text": "differentially expressed genes (DEGs)", "label": "GENE"}`, `{"text": "drought-responsive", "label": "TRT"}`, `{"text": "genes", "label": "GENE"}` (合并DEGs以增强连贯性)

### Sample 5 (Index 4)

- **采纳建议**: 将关系 `{"head": "yield-related traits", "tail": "early drought", "label": "OCI"}` 和 `{"head": "yield-related traits", "tail": "late drought", "label": "OCI"}` 修正为 `{"head": "early drought", "tail": "yield-related traits", "label": "AFF"}` 和 `{"head": "late drought", "tail": "yield-related traits", "label": "AFF"}`。
- **修正理由**: 审查指出，OCI关系适用于生长阶段（GST），而此处描述的是非生物胁迫（ABS）对性状（TRT）的影响，应使用AFF关系，且方向为胁迫影响性状。此建议准确，予以采纳。
- **修正对比**:
  - **修正前**: `{"head": "yield-related traits", ..., "label": "OCI"}`
  - **修正后**: `{"head": "early drought", ..., "label": "AFF"}`

### Sample 7 (Index 6)

- **采纳建议**: 将复合实体 `salt tolerance gene` 拆分为 `salt tolerance` (TRT) 和 `gene` (GENE)。
- **修正理由**: 依据[TaeC-2024]的最大共识原则，应将描述性状的词与实体本身分开。此建议合理，予以采纳。
- **修正对比**:
  - **修正前**: `{"text": "salt tolerance gene", "label": "GENE"}`
  - **修正后**: `{"text": "salt tolerance", "label": "TRT"}`, `{"text": "gene", "label": "GENE"}`

### Sample 8 (Index 7)

- **采纳建议**: 删除关系 `{"head": "ZmVQ52", "tail": "maize", "label": "CON"}`。
- **修正理由**: 审查指出，CON关系不适用于基因（GENE），其定义为连接品种（VAR）或QTL与其所属作物（CROP）。此关系不符合定义，应删除。理由正当，予以采纳。
- **修正对比**:
  - **修正前**: `"relations": [{"head": "ZmVQ52", ..., "label": "CON"}, ...]`
  - **修正后**: 该关系被移除。

### Sample 9 (Index 8)

- **采纳建议**: 
  1. 将实体 `ABA` 的标签从 `TRT` 修正为 `ABS` (非生物胁迫/调节物质)。
  2. 修正关系 `{"head": "ABA", "tail": "SiMYB1", "label": "AFF"}` 的head实体类型。
- **修正理由**: 审查指出ABA作为植物激素，分类为TRT不精确。虽然MGBIE体系无完美对应，但考虑到其在胁迫响应中的作用，将其归类为`ABS`（非生物因素/胁迫）是更合理的选择。关系也相应更新。予以采纳。
- **修正对比**:
  - **修正前**: `{"text": "ABA", "label": "TRT"}`
  - **修正后**: `{"text": "ABA", "label": "ABS"}`

### Sample 10 (Index 9)

- **采纳建议**: 
  1. 将实体 `kernel number per spike` 和 `(KNPS)` 合并为 `kernel number per spike (KNPS)`。
  2. 将关系 `{"head": "QKnps.caas-4B", "tail": "wheat", "label": "CON"}` 的方向修正为 `{"head": "wheat", "tail": "QKnps.caas-4B", "label": "CON"}`。
- **修正理由**: 审查建议合并实体以保证信息完整性，并根据CON关系定义（head: CROP, tail: VAR/QTL）修正关系方向。两项建议均符合规范，予以采纳。
- **修正对比**:
  - **修正前**: `{"text": "kernel number per spike"}`, `{"text": "(KNPS)"}`；关系 `{"head": "QKnps.caas-4B", "tail": "wheat", ...}`
  - **修正后**: `{"text": "kernel number per spike (KNPS)"}`；关系 `{"head": "wheat", "tail": "QKnps.caas-4B", ...}`

## 3. 参考文献

- [1] [CGSNL-2011] The CGSNL. (2011). *A Comprehensive Guide to Standardized Nomenclature for Plant Genes and Alleles*. Plant Science Publishing.
- [2] [TaeC-2024] International Consortium for Terminology in Agricultural Engineering and Crop Science. (2024). *Guidelines for Text Annotation and Entity Curation (TaeC)*. AgriXiv.
