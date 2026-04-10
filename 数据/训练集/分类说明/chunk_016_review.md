**数据块编号**: chunk_016
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

本块共 10 条，已按单块顺序完成初步标注与边界校验，当前全部样本均可进入后续统一审查阶段。整体上，本块以“保守吸收、避免伪关系、尊重训练集既有非标准模式”为处理原则：对于命名基因、明确 QTL、标准性状与明显胁迫信息予以保留；对于泛称位点、泛称基因家族、未给出稳定落点的研究结论，不强行建立关系。

| 指标 | 数值 |
|------|------|
| 总条数 | 10 |
| 成功处理条数 | 10 |
| 包含留空/不确定分类的条数 | 4 |

## 2. 关键分类理由与权威依据

### 2.1 基因与性状共现，但不把“单倍型优势”过度外推为关系

在首条样本中，`Seita.5G251300` 与 `Seita.8G036300` 均为稳定命名基因，`1000 grain weight`、`main panicle grain weight` 与 `grain weight per plant` 均为明确性状，因此保留这些实体。但句子真正的语义主语是 “drought-tolerant haplotypes”，并非直接断言“基因本体影响性状”。据此，本块没有把两个基因直接与三项性状建立 **AFF** 关系，以避免把单倍型层面的观察结论过度投射到基因层。此处理符合技能要求中的“准确性优先”，也与 `authoritative_references.md` 关于遗传位点、单倍型与性状关系应谨慎区分的原则一致。

### 2.2 `QTNs` 可保留，但与 `stay-green QTLs` 不强建伪定位关系

第二条样本写到 `Colocation analysis associated these QTNs with known stay-green QTLs`。这里的 `QTNs` 与 `stay-green QTLs` 都可稳定视为位点层级对象，因此保留为 **QTL**。但文本仅说明“共定位分析关联”，并未给出明确染色体位置、上下位包含关系或标准的 trait-target 关系，因此没有进一步建立 **LOI** 或 **CON**。`putative genes` 与 `drought tolerance` 也予以保留，但同样不扩展为推断性关系。该处理遵循了审查知识库中“研究关联不等于稳定结构关系”的原则。

### 2.3 基因家族列举仅保留可直接落点的命名成员

第三条样本中，`Tartary buckwheat` 可稳定归为 **CROP**，而 `FtRCAR1` 与 `FtRCAR12` 是明确命名的家族成员，故保留为 **GENE**。相较之下，`ABA receptors` 与 `FtRCARs` 更接近家族或功能类别泛称，如果与命名成员并列保留，容易在后续审查时造成“家族概念—成员实体”混杂。因此本块采用压缩策略，只保留最稳定的命名成员。这一做法符合技能文件中“蛋白质名称不应轻率归入 TRT，泛称实体从严”的规则。[SUN-2019] 亦支持将命名基因与泛称功能描述区分处理。

### 2.4 胁迫到性状的方向明确保留，作物到材料的构成关系最小表达

第四条样本 `Drought causes yield loss in sorghum` 中，`Drought` 作为 **ABS**，`yield loss` 作为 **TRT**，建立 `(ABS, AFF, TRT)` 是最稳定的语义表达。后句中的 `216 sorghum accessions` 为材料集合，更适合与 `sorghum` 建立 **CON**。这里没有对 `drought-tolerant sorghum lines` 继续拆分，是因为文本未给出命名材料，强标只会引入泛称实体。该处理既符合技能中对 **AFF** 方向的约束，也尊重训练集中作物—材料 **CON** 的常见表达方式。

### 2.5 同一诱变方法的全称与缩写可并存

第五条样本中，`ethyl methanesulfonate` 与 `EMS` 同时出现，语义上属于同一诱变方法的全称与缩写。鉴于两者都是原文独立出现的稳定文本片段，本块保留二者并分别与 `Longli-4` 建立 **USE** 关系，而不删去其中之一。这样做的原因在于训练集对“全称+缩写”并存通常具有较高容忍度，只要边界清晰、文本确实存在，就不属于幻觉实体。

### 2.6 染色体位点列表保留一般位点与命名位点双层结构

第六条样本既有前半句的泛称 `loci`，又有后半句的命名位点 `Pm 2-1` 与 `Pm 2-2`。本块保留这种双层结构：前者通过 **LOI** 与 `chromosome 1`、`chromosome 2`、`chromosome 6`、`chromosome 8`、`chromosome 10` 建立一般定位关系；后者再与第二处 `chromosome 2` 建立更具体的定位关系。这样可以最大程度保留原句信息层次，同时避免把所有信息都压缩进一个泛称 `loci` 中。根据技能文件，`LOI(QTL, CHR)` 是稳定合法模式，适用于此处。

### 2.7 `ABA` 作为处理因素时，按胁迫/处理源保留为 ABS

第七条样本描述 `ABA upregulated CHS, CHI, F3'H, F3H, and FLS... while downregulating 4CL and PAL`。本块将首个 `ABA` 视为处理因素，归入 **ABS**，并对七个基因建立 **AFF** 关系。这样做并不是把 ABA 当作环境逆境本身，而是沿用训练集中“处理因子/外源刺激 → 基因表达变化”常以 **ABS -> GENE** 表达的既有风格。技能文件也特别指出：`AFF: (ABS, GENE)` 在原始训练数据中是高频非标准模式，应避免过度纠正，因此此处予以保留。

### 2.8 `high-value parent ZGMLEL` 更适合作为材料而非群体

第八条样本原标注把 `ZGMLEL` 记为 **CROSS**。结合上下文 “It comes from the high-value parent ZGMLEL” 可知，`ZGMLEL` 指的是具体亲本材料，更适合归入 **VAR**。同时补充 `major QTL`、`minor QTL` 两个实体，并分别与 `chromosome 7H`、`chromosome 2H` 建立 **LOI**。标记 `GBM1303`、`GMS056`、`Scssr03381` 与 `Scssr07759` 也与对应染色体建立 **LOI**。相较于原始写法，这样更完整地保留了“QTL—染色体—标记”的结构骨架。

### 2.9 RIL 群体必须判为 CROSS

第九条样本中，`recombinant inbred line (RIL) population` 明确属于群体类型。根据技能文件“杂交后代群体应判为 CROSS”的规则，本块将其标为 **CROSS**，而非一般品种材料。其余 `foxtail millet`、`Quantitative trait loci (QTL)` 与多个 panicle/grain 相关性状均予保留。关系方面，一方面保留 `CROP -> TRT` 的 **HAS**，以贴合训练集既有风格；另一方面保留 `QTL -> TRT` 的 **LOI**，因为技能中已明确该非标准模式在原始训练集里应予尊重。

### 2.10 并列 QTL 不共用同一关系头

第十条样本原始关系把首个 `QTL` 同时连向 `kernel length`、`kernel width` 与 `groat percentage`，这会破坏句中三个并列 “a QTL for ...” 的一一对应结构。为修复此问题，本块分别保留三处 `QTL` 实体，并建立：第一处 `QTL -> kernel length`，第二处 `QTL -> kernel width`，第三处 `QTL -> groat percentage` 的 **LOI** 关系。同时，末句 `kernel size or shape influences groat percentage` 中，考虑到 `shape` 并未形成稳定边界短语，而 `kernel size` 可独立落点，因此仅补充 `kernel size -> groat percentage` 的 **AFF**。该处理兼顾了边界稳定性与句法对齐关系。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

当前阶段尚未进入统一审查，因此此节暂留空，待后续四维审查完成后回填采纳与未采纳理由。

## 4. 其他备注

本块最需要在后续统一审查中重点复核的，是第七条中将 `ABA` 吸收到 **ABS** 的一致性，以及第十条中 `kernel size -> groat percentage` 的 **AFF** 是否需要进一步收紧。如果后续审查发现与既有训练集风格存在明显偏差，再按技能要求逐块回修，不在当前初标阶段提前过度调整。
