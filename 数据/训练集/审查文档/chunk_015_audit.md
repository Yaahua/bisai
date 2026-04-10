**数据块编号**: chunk_015
**审查时间**: 2026-04-10 17:42:00

## 1. 审查概况

| 指标 | 结果 |
| --- | --- |
| 总条数 | 10 |
| 发现错误/遗漏条数 | 2 |
| 主要错误类型分布 | 关系漏标 1 处；泛称实体/关系过宽 1 处 |

本块整体沿用了较为保守的初标策略，大部分处理符合技能要求，尤其是 `marker-assisted selection`、`molecular breeding`、`F1 hybrids`、`Recombinant inbreed lines` 等条目判断较稳。统一审查后，问题主要集中在两个位置：其一，存在一句对 `SNPs` 与 `drought tolerance` 的直接关联表述，但关系被完全留空；其二，存在把泛称 `candidate genes` 当作稳定基因实体并进一步建立 `loci -> candidate genes` 关系的情况，该做法在训练一致性上风险较高。

## 2. 详细审查意见与权威依据

### 问题 1: 关系漏标（显式 marker-trait 关联未落到关系层）

- **错误位置**: Sample 8
- **原分类结果**: 已标出 `SNPs` (MRK) 与 `drought tolerance` (TRT)，但 `relations` 为空。
- **修改建议**: 建议补充 `(SNPs, drought tolerance) -> AFF`。
- **权威依据**: 原句为 `146 SNPs associated with drought tolerance were detected.`，其中 `associated with` 是典型的显式关联触发结构。依据 `[TaeC-2024]` 与技能中的最小充分关系原则，当文本直接陈述“标记与性状相关”时，应保留 `MRK -> TRT` 的稳定关系；若完全留空，会损失该句最核心的监督信号。

### 问题 2: 知识审查与词块审查问题（泛称 candidate genes 不宜作为稳定 GENE 并建立宽泛关系）

- **错误位置**: Sample 7
- **原分类结果**: 将 `candidate genes` 标为 GENE，并建立 `(loci, candidate genes) -> CON`。
- **修改建议**: 建议删除 `candidate genes` 实体及其对应的 `CON` 关系，仅保留 `loci` 与各个染色体编号之间的 `LOI` 关系。
- **权威依据**: `candidate genes` 只是泛称类别，不是命名基因个体。根据技能“命名对象优先、泛称从严”的规则，以及 `[TaeC-2024]` 对实体稳定性的要求，只有在文本给出明确基因名时才更适合保留为 **GENE**。此外，`contained one to three candidate genes` 描述的是位点区间内候选基因数量概况，不是一个适合稳定学习的具体实体-关系对；若保留，会把类别性短语误塑为实体本体，增加后续修订噪声。

## 3. 审查总结与后续建议

本块初标方向总体正确，但暴露出两个典型风险。第一，遇到 `associated with`、`linked to`、`for tolerance` 等显式触发词时，若实体已被保留，应优先检查是否遗漏了最直接的关系。第二，对于 `candidate genes`、`major traits` 这类集合性、类别性表达，应优先判断其是否属于命名实体；若不是，通常不应继续向关系层扩展。

建议在后续全量修正与经验记录中补充两条规则：一是**显式关联触发词出现时，先补最小充分关系，再决定是否扩展其他关系**；二是**泛称类 gene/loci/trait 短语默认从严，不与具体位点或材料构造宽泛关系**。
