
# MGBIE 数据块 chunk_008 审查报告

## 整体处理情况

- **总条数**: 10
- **问题条数**: 9
- **问题摘要**: 本次审查发现9条数据存在标注问题，主要涉及实体边界界定不准（如包含数量词）、实体类型错误（如将基因描述误标为基因）、关系类型错误或缺失、以及实体遗漏等。所有问题均已根据相关标准和规范进行修正。

---

## 问题详述

### Sample 1 (Index 0)

- **问题1**: 实体 `81,342 public genomic contigs` 和 `1,758 polymorphic primers` 等包含了数值，不符合核心名词标注原则。
- **修正1**: 移除数值，仅标注核心词汇 `polymorphic primers`。
- **问题2**: 实体 `eight sorghum lines` 被错误地标注为 `VAR`。这是一个对品系群体的描述，而非具体的品种名称。
- **修正2**: 移除该实体。
- **问题3**: 关系标注不当，例如 `(SSR markers, CON, primer pairs)` 使用了错误的 `CON` 关系类型。
- **修正3**: 移除了所有不正确的或无明确定义的关系。

### Sample 2 (Index 1)

- **问题1**: 遗漏实体 `grain traits`。
- **修正1**: 补充标注 `grain traits` 为 `TRT`。
- **问题2**: 遗漏关系 `(SNPs, AFF, grain traits)`。
- **修正2**: 补充 `AFF` 关系，表示 `SNPs` 对 `grain traits` 的影响。

### Sample 3 (Index 2)

- **问题1**: 实体 `male sterility gene rf4` 边界过大，应拆分为性状 `male sterility` (TRT) 和基因 `rf4` (GENE)。依据 [CGSNL-2011] 基因命名规范，`rf4` 是基因符号。
- **修正1**: 拆分实体并修正标签。
- **问题2**: 关系 `(LW7 marker, LOI, male sterility gene rf4)` 逻辑不正确。标记影响的是基因，而不是直接定位到基因。应为 `AFF` 关系。
- **修正2**: 将关系修正为 `(LW7 marker, AFF, rf4)`。
- **问题3**: 遗漏实体 `sterile male` (TRT)。
- **修正3**: 补充标注。

### Sample 4 (Index 3)

- **问题1**: 遗漏了多个性状实体，如 `drought-sensitive`、`drought-tolerant` 和 `photosynthesis-related pathways`。
- **修正1**: 补充标注这些实体为 `TRT`。
- **问题2**: 遗漏了胁迫对性状影响的关系。
- **修正2**: 补充 `(drought, AFF, drought-sensitive)` 等关系。

### Sample 5 (Index 4)

- **问题1**: 实体 `adaptation-related QTL` 边界不准，应拆分为 `adaptation` (TRT) 和 `related QTL` (QTL)。
- **修正1**: 拆分实体。
- **问题2**: 实体 `crown rust resistance` 边界过大，应拆分为 `crown rust` (BIS) 和 `resistance` (TRT)。
- **修正2**: 拆分实体。
- **问题3**: 关系逻辑错误。原文是基因与抗性关联，而不是QTL与基因定位。例如，`Pc48` 是一个抗性基因，它影响 `seedling resistance` 性状。
- **修正3**: 将关系修正为 `(Pc48, AFF, seedling resistance)` 等。

### Sample 6 (Index 5)

- **问题1**: 遗漏了性状实体 `drought-tolerant`。
- **修正1**: 补充标注为 `TRT`。
- **问题2**: 遗漏了品种具有性状的关系。
- **修正2**: 补充 `(V2, HAS, drought-tolerant)` 关系。

### Sample 7 (Index 6)

- **问题1**: 实体 `sorghum genotypes` 边界过大，应拆分为 `sorghum` (CROP) 和 `genotypes` (VAR)。
- **修正1**: 拆分实体。
- **问题2**: 实体 `control conditions` 错误地标注为 `TRT`，应为 `ABS`。
- **修正2**: 修正标签为 `ABS`。
- **问题3**: 关系 `(drought, OCI, grain filling)` 逻辑不正确。胁迫影响的是性状，而不是发生在某个时期。
- **修正3**: 修正为 `(drought, AFF, grain yield)` 等关系。

### Sample 8 (Index 7)

- **问题1**: 实体 `sorghum genotype` 边界过大，应拆分为 `sorghum` (CROP) 和 `genotype` (VAR)。
- **修正1**: 拆分实体。

### Sample 9 (Index 8)

- **问题1**: 实体 `Stay-green` 被错误地标注为 `GENE`，它是一种重要的耐旱性状。
- **修正1**: 修正标签为 `TRT`。
- **问题2**: 关系 `(Stay-green, AFF, sorghum)` 逻辑错误，性状不能影响作物。
- **修正2**: 修正为 `(Stay-green, AFF, drought tolerance)` 等关系。

