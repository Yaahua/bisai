# chunk_017 问题清单

## 1. 已确认问题

| 序号 | 位置 | 问题类型 | 具体问题 | 直接修复动作 |
| --- | --- | --- | --- | --- |
| 1 | Sample 2 | 泛称实体过宽 | `PgB3[5:9]` 是基因家族/集合层表达，不是稳定命名基因个体，却被标为 `GENE`，并承接了两条胁迫关系。 | 删除 `PgB3` 实体，并同步删除 `(drought, PgB3) -> AFF` 与 `(high-temperature stresses, PgB3) -> AFF`。保留 `PgRAV-04`。 |
| 2 | Sample 3 | 泛称实体过宽 | `drought-responsive genes[145:169]` 是功能性集合表达，被误写为 `GENE`。 | 删除 `drought-responsive genes` 实体。 |
| 3 | Sample 3 | 关系过度外推 | `sorghum -> drought tolerance` 被写为 `HAS`，但原句更接近“资源有助于耐旱改良”，并非作物固有性状陈述。 | 删除 `(sorghum, drought tolerance) -> HAS`，保留实体层主题对象。 |
| 4 | Sample 10 | 泛称实体过宽 | `FT genes[394:402]` 是 gene cluster / 集合表达，缺少稳定命名成员，不宜保留为 `GENE`。 | 删除 `FT genes` 实体，保留 `major QTL`、`DTF3A`、`flowering time`、`short-day conditions`、`chromosome three`。 |

## 2. 潜在问题

| 序号 | 位置 | 潜在风险 | 复核结论 |
| --- | --- | --- | --- |
| P1 | Sample 2 | 删除 `PgB3` 后若未同步处理关系，会产生悬空关系。 | 必须同步删去两条 `ABS -> GENE` 的 `AFF`。 |
| P2 | Sample 3 | 删除 `HAS` 后可能误删 `drought tolerance` 或 `sorghum` 实体，导致主题对象丢失。 | 两实体仍保留，不回收实体层。 |
| P3 | Sample 10 | 删除 `FT genes` 时若误触及 `DTF3A -> chromosome three` 或 `major QTL -> flowering time`，会破坏核心骨架。 | 仅删除 `FT genes` 实体，不动现有 3 条核心关系。 |

## 3. 关联问题

本块的问题具有一致模式：**家族名、响应性基因集合、基因簇等集合表述被误当作单一稳定基因实体**。同时，Sample 3 还伴随“研究改良目标被外推为作物固有性状”的关系层偏移。因此修复顺序应为：先处理实体层过宽问题，再清理由这些过宽实体衍生的关系；最后复核剩余核心关系是否仍保持最小充分骨架。
