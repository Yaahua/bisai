# chunk_016 问题清单

## 1. 已确认问题

| 序号 | 位置 | 问题类型 | 具体问题 | 直接修复动作 |
| --- | --- | --- | --- | --- |
| 1 | Sample 2 | 泛称实体过宽 | `putative genes[73:87]` 是候选基因集合表达，不是命名基因个体，却被标为 `GENE`。 | 删除 `putative genes` 实体，仅保留 `QTNs`、`stay-green QTLs` 与 `drought tolerance`。 |
| 2 | Sample 10 | 总括关系漏标 | 句首 `QTLs were detected for kernel morphology traits and groat percentage` 已有 `QTL`、`kernel morphology traits`、`groat percentage` 实体，但未建对应关系。 | 补充 `(QTL[12:15], kernel morphology traits[35:59]) -> LOI` 与 `(QTL[12:15], groat percentage[64:80]) -> LOI`。 |

## 2. 潜在问题

| 序号 | 位置 | 潜在风险 | 复核结论 |
| --- | --- | --- | --- |
| P1 | Sample 2 | 删除泛称实体后若未核对关系层，后续脚本可能误补悬空关系。 | 当前该样本 `relations` 为空，删除实体即可，不需回收关系。 |
| P2 | Sample 10 | 句首总括 `QTL` 与后半句三个并列 `QTL` 同名，补关系时容易错绑到后半句两个 `QTL[129:132]`、`QTL[176:179]`。 | 新增关系必须锚定句首 `QTL[12:15]`。 |
| P3 | Sample 10 | 已存在 `kernel size -> groat percentage` 的 `AFF`，补总括 `LOI` 时若误删会丢失原有监督信号。 | 保留现有 4 条关系，仅新增 2 条句首总括关系。 |

## 3. 关联问题

本块修复体现两类不同风险：一类是**泛称集合误入实体层**，另一类是**同名 QTL 在总括句与细化句并存时导致前者关系被漏掉**。因此修复顺序应为：先删除不稳定的泛称基因实体，再对句首总括 `QTL` 精确补关系，并复核新增关系的锚点坐标，避免与后半句并列 `QTL` 混淆。
