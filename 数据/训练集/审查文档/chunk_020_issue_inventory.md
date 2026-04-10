# Chunk 020 问题清单

## 1. 已确认问题

| 样本 | 问题类型 | 当前问题 | 直接修复动作 |
| --- | --- | --- | --- |
| Sample 1 | 泛化基因集合误标 | `drought-inducible transcription factors`、`drought responsive DEGs` 为功能性/集合性表达，却被保留为 **GENE** | 删除两处 GENE 实体及其 `common buckwheat -> GENE (CON)` 关系，仅保留稳定对象 |
| Sample 9 | 概括性候选基因短语误标 | `barley genes or orthologs` 为集合性说明短语，却被保留为 **GENE** | 删除该 GENE 实体及其 `barley -> GENE (CON)` 关系 |
| Sample 10 | 泛化基因与非方法实体误标 | `Genes determining flowering` 为功能性概括，不是稳定命名基因；`multiple cropping` 不是育种/分析方法，却被标为 **BM** | 删除该 GENE 实体、其 `AFF` 关系，以及 `multiple cropping` 实体 |

## 2. 潜在关联问题

| 样本 | 潜在影响 | 复核要点 |
| --- | --- | --- |
| Sample 1 | 删除两个 GENE 后，样本可能只剩 `CROP + TRT`，需防止残留孤立关系或错误补链 | 不新增臆测关系；仅清理泛化 GENE 与残留 `CON` |
| Sample 9 | 删除概括性基因短语后，`barley grain size and weight` 与 `QTL hotspot regions` 的 LOI/HAS 结构必须保持完整 | 检查 `barley`、`QTL hotspot regions`、染色体位置和性状链条不受影响 |
| Sample 10 | 删除泛化 GENE 与 BM 后，剩余应为 `TRT-ABS-TRT` 语义链，不能误删 `flowering time -> crop maturity/yield` | 保留稳定的性状因果链，不因上游删除而断裂 |

## 3. 关联修复原则

1. 仅保留**稳定命名实体**，删除 `genes / orthologs / DEGs / transcription factors / genes determining...` 等集合或功能泛称。
2. `multiple cropping` 属于种植制度/农艺安排，不按 **BM** 入最终标注。
3. 修复时同步检查：实体重叠、关系残留、方向一致性、span 精确匹配与 occurrence 锚点。

## 4. 本块修订目标

本块全量修正聚焦 Sample 1、9、10 三处问题，但执行时同步保证：

- 删除泛化实体后不残留旧 relation；
- 其余样本的稳定 BM、MRK、CROSS、ABS、TRT 结构不被连带破坏；
- 最终 JSON 仍满足实体边界与关系边界校验要求。
