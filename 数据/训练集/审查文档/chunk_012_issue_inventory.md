## 1. 已确认问题

| 序号 | 位置 | 问题类型 | 具体问题 | 直接修复动作 |
| --- | --- | --- | --- | --- |
| 1 | Sample 5 | 语义层级提升过度 | 将 `salt-sensitive` 与 `salt-tolerant` 直接上挂到 `foxtail millet`，建立了两条不稳健的 `CROP -> TRT` `HAS` 关系，但原文真正修饰的是 `accessions`。 | 删除 `(foxtail millet, salt-sensitive) -> HAS` 与 `(foxtail millet, salt-tolerant) -> HAS` 两条关系，仅保留 `salt stress -> salt-sensitive` 与 `salt stress -> salt-tolerant` 的 `AFF` 关系。 |
| 2 | Sample 6 | 实体漏标 | 句中并列出现的 `superoxide dismutase`、`peroxidase`、`catalase activities` 未被标为 `TRT`。 | 为上述三个词块补充 `TRT` 实体，并逐一核对边界与原文字面一致。 |
| 3 | Sample 6 | 关系漏标 | 由于酶活性实体缺失，连带遗漏了 `FtNAC31 -> TRT` 的三条 `AFF` 关系。 | 补充 `FtNAC31 -> superoxide dismutase`、`FtNAC31 -> peroxidase`、`FtNAC31 -> catalase activities` 三条 `AFF` 关系，并同步填写完整锚点字段。 |

## 2. 潜在问题

| 序号 | 位置 | 潜在风险 | 复核结论 |
| --- | --- | --- | --- |
| P1 | Sample 5 | “sensitive/tolerant/resistant accessions” 一类短语很容易被误提升为作物整体固有性状。 | 本样本中 `salt-sensitive`、`salt-tolerant` 仅表示材料分组，应保留为 `TRT` 但不再与 `foxtail millet` 建立 `HAS`。 |
| P2 | Sample 6 | 并列性状结构最容易出现“补了实体、忘了补关系”或只补一部分的问题。 | 需确认三个酶活性词块全部补齐，并与 `FtNAC31` 一一建立 `AFF`。 |
| P3 | Sample 6 | 酶活性类词块可能存在共享后缀，若边界取值不一致，会引起并列结构不整齐。 | 修复后再次核对三个 `TRT` 的 `start/end` 与原文一致，必要时按完整可读词块统一。 |

## 3. 关联问题

本块修复时，必须把**对象层级判断**与**并列性状补全**分开处理。Sample 5 的关键是删除被过度提升的 `CROP -> TRT` 关系，而不是误删已有的 `TRT` 实体或 `salt stress -> TRT` 关系。Sample 6 的关键是成组补齐实体与关系，不能只加 `TRT` 不加 `AFF`，也不能只修其中一项。回写后应重点复核两点：其一，`foxtail millet` 是否已不再承担材料分组词的 `HAS` 关系；其二，三个新补 `TRT` 是否都已与 `FtNAC31` 正确对齐。
