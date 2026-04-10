# chunk_018 问题清单

## 1. 已确认问题

| 序号 | 位置 | 问题类型 | 具体问题 | 直接修复动作 |
| --- | --- | --- | --- | --- |
| 1 | Sample 5 | 冗余泛称实体 | `major QTL[13:22]` 只是对命名位点 `ASM` 的解释性同位表达，在已有稳定命名 QTL 的前提下构成冗余。 | 删除 `major QTL` 实体，仅保留两处 `ASM`。 |
| 2 | Sample 10 | 技术流程关系外推 | `buckwheat -> genotyping` 被写为 `USE`，但原句是流程能力/技术平台描述，不是稳定作物—方法关系。 | 删除 `buckwheat -> genotyping` 的 `USE` 关系；若 `genotyping` 不再承接核心关系，则同步回收 `genotyping` 实体。 |

## 2. 潜在问题

| 序号 | 位置 | 潜在风险 | 复核结论 |
| --- | --- | --- | --- |
| P1 | Sample 5 | 删除 `major QTL` 时若误触发 `ASM -> dehydration tolerance` 的 LOI，会破坏核心位点骨架。 | 仅删除同位泛称，不动两处 `ASM` 与既有核心关系。 |
| P2 | Sample 10 | 删除 `buckwheat -> genotyping (USE)` 后若仍保留无功能的 `genotyping`，会产生低价值残留实体。 | 关系删除后检查 `genotyping` 是否仍服务其他核心关系；若无，则一并删除。 |
| P3 | Sample 10 | 删除流程关系时可能误删 `QTL -> main stem length (LOI)` 或 `genome-wide markers` 等核心对象。 | 保留 `QTL`、`main stem length`、`genome-wide markers`、`buckwheat` 的核心信息。 |

## 3. 关联问题

本块的问题集中在两类风格一致性风险：**命名对象已足够明确时，解释性泛称不应再独立入库；句子主体若是实验流程或平台能力，也不应为了“保留更多信息”而外推出作物—方法关系。** 因此修复顺序应为：先删除冗余泛称，再清理流程型关系及其失去功能的尾随实体，最后复核核心育种信息骨架是否完整。
