**数据块编号**: chunk_012
**审查时间**: 2026-04-10 17:00:00

## 1. 审查概况

| 指标 | 结果 |
| --- | --- |
| 总条数 | 10 |
| 发现错误/遗漏条数 | 2 |
| 主要错误类型分布 | 语义关系错误 1 处；实体漏标与关系漏标 1 处 |

本块初标整体保持了较好的保守性，尤其在 `Pc98`、`FtMYB30`、QTL 与染色体位置、杂交材料与标记类型的处理上，基本符合技能要求。但是统一审查后仍发现两类应在全量修正阶段处理的问题：一是把材料分组词误提升为作物层面的稳定性状，并进一步建立了不够稳健的 `CROP -> TRT` 关系；二是对酶活性类标准表型存在明显漏标，从而连带遗漏了对应的 `GENE -> TRT` 影响关系。

## 2. 详细审查意见与权威依据

### 问题 1: 语义审查错误（材料分组词不宜直接提升为作物层面的 HAS 性状）

- **错误位置**: Sample 5, Relation 3–4
- **原分类结果**: `(foxtail millet, salt-sensitive) -> HAS` 与 `(foxtail millet, salt-tolerant) -> HAS`。
- **修改建议**: 建议删除这两条 `HAS` 关系，仅保留 `salt stress -> salt-sensitive` 与 `salt stress -> salt-tolerant` 的影响关系；同时保留 `foxtail millet` 作为语境作物实体即可，不再把 `salt-sensitive`、`salt-tolerant` 直接作为作物层面稳定拥有的性状锚定到 `foxtail millet`。
- **权威依据**: 依据 `[TaeC-2024]`，标注应贴近原句最自然的语义单位。此处原文为 “salt-sensitive and salt-tolerant accessions”，真正被修饰的是 `accessions`，而非整个 `foxtail millet` 物种层级。依据 `[LU-2006]` 与 `[LU-Sorghum-2006]` 的描述规范思路，性状通常应落在具体材料、群体或品种对象上；若文本并未显式给出这些对象的独立实体，则不宜机械上升为作物整体 `HAS` 某种性状。

### 问题 2: 实体与关系漏标（酶活性类表型缺失）

- **错误位置**: Sample 6
- **原分类结果**: 仅标注了 `FtNAC31`、`RD29A`、`RD29B`、`RD22`、`DREB2B`、`NCED3`、`POD1`，未标注 `superoxide dismutase`、`peroxidase`、`catalase activities`，也未建立相应 AFF 关系。
- **修改建议**: 建议补充以下 TRT 实体，并建立 `FtNAC31 -> TRT` 的 AFF 关系：`superoxide dismutase`、`peroxidase`、`catalase activities`。若边界复核后发现更自然的词块是带有共同后缀的并列结构，也可按 `[TaeC-2024]` 的最大共识原则调整为更完整、可读的性状词块，但必须保证与原文字面一致。
- **权威依据**: 依据 `[TaeC-2024]`，酶活性在育种与胁迫生理文本中属于稳定可观测的生理性状表达，应整体归入 TRT。句中 “FtNAC31 overexpression lines had sharply increased ... activities” 明确表达了基因操作对这些性状的影响，因此符合 `AFF: (GENE, TRT)`。这种处理也与前文 `FtMYB30 -> proline content / antioxidant enzyme activity` 的一致性要求相符。

## 3. 审查总结与后续建议

本块的主要问题不是大面积错分，而是**对象层级提升过度**与**并列性状漏标**。进入全量修正阶段时，应优先检查两类高风险场景。第一，凡遇到 “sensitive/tolerant/resistant accessions” 之类表达，必须先判断被修饰对象是否真已作为实体出现，不能默认把它们上挂到作物实体。第二，凡句子存在 “A, B, and C activities” 这一类并列生理指标时，必须逐一核对是否已完整落为 TRT，并同步补齐上游基因或胁迫的影响关系。

建议把本块经验加入批次错误记录：**材料分组词不等于作物固有性状**，以及**并列酶活性常被漏标，需要逐项复核**。
