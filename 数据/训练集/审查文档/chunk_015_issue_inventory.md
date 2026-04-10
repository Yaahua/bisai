# chunk_015 问题清单

## 1. 已确认问题

| 序号 | 位置 | 问题类型 | 具体问题 | 直接修复动作 |
| --- | --- | --- | --- | --- |
| 1 | Sample 8 | 关系漏标 | 文本明确写有 `SNPs associated with drought tolerance`，已保留 `SNPs` 与 `drought tolerance` 实体，但 `relations` 为空。 | 补充 `(SNPs[4:8], drought tolerance[25:42]) -> AFF`。 |
| 2 | Sample 7 | 泛称实体保留过宽 | `candidate genes[128:143]` 是类别性泛称，不是命名基因个体，却被标为 `GENE`。 | 删除 `candidate genes` 实体。 |
| 3 | Sample 7 | 关联关系过宽 | 在删除泛称实体后，`(loci, candidate genes) -> CON` 将成为不成立关系。 | 同步删除该 `CON` 关系，仅保留 `loci -> 染色体` 的 `LOI` 关系。 |

## 2. 潜在问题

| 序号 | 位置 | 潜在风险 | 复核结论 |
| --- | --- | --- | --- |
| P1 | Sample 7 | 删除泛称实体后，关系层若未同步回收，会形成悬空 `GENE` 关系。 | 必须同步删除唯一对应的 `CON` 关系。 |
| P2 | Sample 8 | 补 `AFF` 时若锚点误连到 `candidate loci` 或 `drought stress`，会破坏“显式最小充分关系”原则。 | 仅补 `SNPs -> drought tolerance`，不扩展到其他泛称对象。 |
| P3 | Sample 8 | 句中后半段还有 `candidate loci`、`drought stress`，容易诱发过度扩展。 | 当前审查仅确认首句显式 `associated with` 关系，应避免额外臆造关系。 |

## 3. 关联问题

本块修复需要同时控制两类偏差：第一类是**显式关联却漏关系**，第二类是**泛称对象被错误实体化并继续入关系层**。因此修复时要遵守一个顺序：先删除不稳定泛称实体及其关系，再补充文本中最明确、最稳定的 `marker-trait` 关系，避免顾此失彼。
