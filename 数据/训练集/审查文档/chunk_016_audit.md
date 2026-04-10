**数据块编号**: chunk_016
**审查时间**: 2026-04-10 17:49:00

## 1. 审查概况

| 指标 | 结果 |
| --- | --- |
| 总条数 | 10 |
| 发现错误/遗漏条数 | 2 |
| 主要错误类型分布 | 泛称实体过宽 1 处；关系漏标 1 处 |

本块初标整体较稳，尤其是对 `RIL population` 判为 **CROSS**、对 `ABA -> GENE` 的非标准高频模式予以保留、以及对 `major/minor QTL` 与染色体关系的恢复，都符合技能强调的“尊重训练集原有风格、避免过度规范化”的原则。统一审查后，仍有两处需要在全量修正中处理：一处是将泛称 `putative genes` 直接作为 **GENE** 保留，另一处是句首关于 `QTLs` 与 `kernel morphology traits / groat percentage` 的显式对应关系未补齐。

## 2. 详细审查意见与权威依据

### 问题 1: 泛称 `putative genes` 不宜直接稳定化为 GENE

- **错误位置**: Sample 2
- **原分类结果**: 将 `putative genes` 标为 **GENE**，但未建立关系。
- **修改建议**: 建议删除 `putative genes` 实体，保留 `QTNs`、`stay-green QTLs` 与 `drought tolerance`。
- **权威依据**: 句中 `47 putative genes near these QTNs potentially influenced drought tolerance traits` 描述的是候选基因集合，而非命名基因个体。依据技能中的“命名对象优先、泛称从严”规则，以及 `[TaeC-2024]` 关于实体稳定性的要求，只有在给出明确基因名称时，才更适合保留为 **GENE**。若保留 `putative genes`，会把类别性、统计性概述误写成实体本体，降低训练信号一致性。

### 问题 2: 句首 QTL 与性状的显式关系存在漏标

- **错误位置**: Sample 10
- **原分类结果**: 保留了句首 `QTL`、`kernel morphology traits`、`groat percentage`，但未建立关系；仅在后半句为三处并列 `QTL` 建立了对应关系。
- **修改建议**: 建议补充句首 `(QTL, kernel morphology traits) -> LOI` 与 `(QTL, groat percentage) -> LOI`。
- **权威依据**: 原句 `One to five QTLs were detected for kernel morphology traits and groat percentage` 直接给出 QTL 与性状对象之间的对应范围。按照技能对原始训练集风格的继承策略，`QTL -> TRT` 在该数据中通常以 **LOI** 形式保留。后半句虽进一步展开了更细的三组 QTL-性状对应，但这并不抵消前半句的总括性关系；若完全留空，会漏掉一句原本已明确表达的监督信息。

## 3. 审查总结与后续建议

本块的主要经验是：对于 `putative genes`、`candidate genes`、`major traits` 一类泛称集合表达，若没有命名化落点，应优先收紧而不是勉强保留；而对于 `QTLs were detected for ...`、`markers associated with ...` 这类直陈型结构，只要实体已保留，就应优先检查是否存在最小充分关系漏标。

后续全量修正时，建议把本块沉淀为两条经验规则：其一，**泛称基因集合默认不入 GENE，除非文本给出稳定命名成员**；其二，**总括句中的 QTL/marker 与 trait 关系不能因为后文有细化结构就被省略**。
