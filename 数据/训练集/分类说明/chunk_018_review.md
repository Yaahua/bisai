**数据块编号**: chunk_018
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

本块共 10 条，已按“当前只处理一个 chunk”的要求完成初步标注与结构校验。与前几个数据块相比，本块的主要难点不在于单一命名实体识别，而在于如何处理大量**概括性材料表述**、**离子/生理指标短词**、**处理条件对基因表达的影响句式**以及**技术流程句**。因此，我延续了此前已经固定的策略：凡是可以稳定落入任务标签体系的对象均予以保留；凡是可能导致过度推断、关系方向不稳或实体边界人为扩张的内容，则尽量保守处理。

| 指标 | 数值 |
|------|------|
| 总条数 | 10 |
| 已完成初标条数 | 10 |
| 重点保守处理条数 | 6 |

## 2. 关键分类理由与依据

### 2.1 材料—性状型句子继续沿用 `VAR -> TRT (HAS)`

第一条样本中，`Genotype A. Sacaca` 是明确材料名称，因此归为 **VAR**。`saponins content` 以及元素型表述 `K`、`Ca`、`P`、`Fe` 在原句中都表示该材料具有较高的测定指标，因此统一归为 **TRT**，并由材料指向这些指标建立 **HAS**。原始标注遗漏了 `P` 的关系，本块已经补齐。这样处理与技能中对“材料表现出更高含量/更高水平”的习惯性标注方式一致。

### 2.2 保留显式性状，弱化跨物种保守性推断关系

第二条样本的核心信息其实分成两部分：前半句是 `markers` 被定位到燕麦共识图谱，后半句是 `heading date` 与 `plant height` 相关基因组区域在 `oat`、`Oryza sativa` 和 `Brachypodium distachyon` 间具有保守性。由于现有关系标签并不直接覆盖“共线性/保守性”这一语义，本块没有强行制造跨物种伪关系，而是补入 `heading date`，保留两个 `oat` 实体和两个参照物种实体，并仅在第二处 `oat` 上保留 `oat -> heading date` 与 `oat -> plant height` 的 **HAS**。这样既不丢失核心对象，也避免把“保守性”误转成确定的育种关系。

### 2.3 技术支持句中，优先保留最稳定的作物—方法关系

第三条样本的原文强调 `SNP marker technologies` 与 `haplotype-based GWAS` 支持 `molecular breeding in barley`。因此本块补入 `molecular breeding` 作为 **BM**，保留 `molecular markers` 与 `SNP` 为 **MRK**，`GWAS` 为 **BM**，并只保留一条最稳定的 `barley -> molecular breeding (USE)`。之所以没有进一步扩展成 `molecular breeding -> SNP` 或 `molecular breeding -> GWAS` 的多条链式关系，是因为在现有训练集中，这类“方法支撑方法”的表达容易产生方向不一致问题，后续统一审查时再决定是否需要增强。

### 2.4 复杂耐盐机制句中，优先修正明显错误，再保留训练集习惯模式

第四条样本是本块最复杂的一条。处理思路分成三层。

第一，保留 `Salt-tolerant cultivars`、`salt-sensitive cultivars` 两个材料类别，并把 `growth rate`、`leaf cell membrane integrity`、`osmotic adjustment capability`、`antioxidant enzyme activities`、`osmotic regulators` 等可测性状统一归为 **TRT**，`saline condition` 归为 **ABS**。这是因为原文明确描述的是盐胁迫下耐盐材料维持更优的生理表现。

第二，原始标注把 `AsHKT2;1` 截断成了 `AsHKT2`，本块已改正为完整基因名 `AsHKT2;1`。这类边界修正属于技能中最强调的基础质量项：命名基因一旦边界错误，后续关系全部失真。

第三，原始关系里存在明显不当的一条：`salt-sensitive cultivars -> root Na+ uptake (HAS)`。原文并不是说盐敏材料具有该优势，而是说与盐敏材料相比，耐盐材料降低了 `root Na+ uptake`。因此本块删除了这条明显错误关系，仅保留 `salt-tolerant cultivars` 与相关离子/转运指标的 **HAS**，并保留 `AsAKT1`、`AsHKT2;1`、`AsSOS1`、`AsNHX1`、`AsVATP-P1`、`AsKUP1` 对对应离子性状的 **AFF**。这里继续沿用了训练集中“基因影响离子或生理指标”这一习惯模式。

### 2.5 `ASM` 应明确吸收为 QTL，本体应用场景单独标注

第五条样本中，`ASM` 在句首被直接定义为“a major QTL for dehydration tolerance”，因此本块将两次 `ASM` 都归为 **QTL**，同时保留 `major QTL` 这个概括性 QTL 实体。关系层面，保留 `ASM -> dehydration tolerance (LOI)` 作为最核心的定位信息；后半句中的 `marker-aided breeding` 与 `allele-mining` 都是明确育种方法，因此标为 **BM**，并与 `foxtail millet` 建立 **USE**。这比仅保留 `foxtail millet -> dehydration tolerance` 更完整地反映了句子的应用导向。

### 2.6 “except for” 结构下，不把例外项误标为优势性状

第六条样本是典型比较句：`DA92-2F6` 在 `15% PEG-6000 drought stress` 下，其 `antioxidant enzyme`、`osmotic adjustment substance` 与 `photosynthetic efficiency` 都显著高于 `Longyan 3`，但 `cell membrane permeability` 例外。基于这一句法结构，本块新增了前三个性状实体，并由第二处 `DA92-2F6` 分别指向这些性状建立 **HAS**，同时保留胁迫条件对这些性状的 **AFF**。相反，虽然 `cell membrane permeability` 被补入为实体，但没有给 `DA92-2F6` 增加对应 **HAS**，因为原文明确将其作为例外项，这一点不能被误读。

### 2.7 MeJA 作为处理因素，按训练集习惯可作用于基因表达

第七条样本中，`MeJA up-regulated the expression of key genes ...` 这一表述非常适合沿用训练集中常见的 `ABS -> GENE (AFF)` 模式。因此本块把两处 `MeJA` 统一吸收为 **ABS**，并将列举的 11 个基因全部标为 **GENE**，同时由第一处 `MeJA` 指向这些基因建立 **AFF**。后半句中的 `ester biosynthesis`、`aroma`、`quality` 都是品质相关性状，因此归为 **TRT**，`'Nanguo' pears` 作为具体品种/材料归为 **VAR**，并保留 `VAR -> TRT (HAS)`。这样处理既保留了处理因素对表达的影响，也保留了品种层面的品质属性。

### 2.8 泛化材料短语不直接当作 CROP 名称使用

第八条样本原始标注把 `oat cultivars` 整体当作 **CROP**。考虑到真正稳定的作物名是 `oat`，而 `cultivars` 只是说明材料类别，因此本块收缩为 `oat`。同时保留 `Baiyan7` 与 `Yizhangyan4` 两个 **VAR**，并用 `oat -> VAR (CON)` 表示材料归属。`better adaptability to saline-alkali` 的原边界过长且夹带处理信息，因此改收缩为 `adaptability`，再保留 `Baiyan7 -> adaptability (HAS)` 与 `saline-alkali stress -> adaptability (AFF)`。这更符合词块审查所要求的“最小充分边界”。

### 2.9 非具体材料集合不强行制造 VAR

第九条样本的原始标注创造了一个很长的伪材料 `germinated saline-alkali-tolerant oat` 并归为 **VAR**。这类对象并非真实命名品种，而是描述性集合，不宜直接当作稳定品种实体。因此本块删除该 **VAR**，仅保留 `oat`、`saline-alkali tolerance` 和 `germination stage` 三个稳定对象，并保留 `oat -> saline-alkali tolerance (HAS)` 与 `saline-alkali tolerance -> germination stage (OCI)`。这种简化能够显著降低后续审查中的伪实体风险。

### 2.10 技术流程句不必扩张过多方法链

第十条样本把 `QTL mapping`、`DNA extraction`、`genotyping` 和 `genome-wide markers` 等流程信息串联在一起。就训练目标而言，最关键的信息仍是 `QTL` 与 `main stem length` 的关联，因此本块保留 `QTL -> main stem length (LOI)`。同时保留 `buckwheat` 与第二处 `genotyping` 的 **USE** 关系，表示该作物被用于基因分型流程。相比大量追加方法之间的链式连接，这种处理更稳妥，也更符合“优先保留核心育种信息”的原则。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

当前尚未进入统一审查阶段，本节待后续四维审查完成后回填。

## 4. 其他备注

本块后续统一审查时应重点复核三类对象：其一是第二条中跨物种“保守性”是否还需要更强表达；其二是第四条耐盐机制句中 `Na+` 与 `root Na+` 的拆分是否最优；其三是第七条 `MeJA -> GENE` 的批量 **AFF** 是否需要进一步收缩。当前初标遵循的是“先保证不明显错，再在统一审查阶段做第二轮精修”的原则。
