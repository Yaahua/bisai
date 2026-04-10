**数据块编号**: chunk_014
**处理阶段**: 初步标注完成，待统一审查

## 1. 整体说明

本块共含 10 条样本，已按单块顺序完成初步修订。处理原则继续保持保守标注：凡是能够稳定落入比赛标签体系的实体予以保留，凡是仅表示实验背景、分析技术、泛化统计短语、同义说明或难以稳定归类的表达，则不强行入标。关系构建方面，优先保留文本中具有直接触发词支撑的 **AFF、HAS、USE、CON、LOI** 关系，避免由推断性语义引出的过度连接。

## 2. 关键修订理由

### 2.1 生理指标与复合材料的处理

在首条关于 `T2 transgenic 35S:VrNHX1 lines` 的样本中，`K+/Na+ ratio`、`[Na+]`、`lipid peroxidation`、`hydrogen peroxide`、`oxygen radical production`、`relative water content`、`proline`、`ascorbate` 与 `chlorophyll contents` 均作为处理后可观测的生理或表型指标，统一保留为 **TRT**。其中 `salt stress` 明确充当胁迫背景，故保留为 **ABS**。这里没有额外把 `VrNHX1` 从材料名中强拆为独立基因并大规模重建基因关系，原因是该句的直接叙述中心是转基因材料的表型表现，而不是单独讨论基因位点本体。

### 2.2 去除不稳定的亚细胞定位误标

第二条样本原先把 `nucleus` 标为 **TRT**，并构造了基因到 `nucleus` 的 **LOI** 关系。按照本任务标签体系，`nucleus` 不属于稳定的目标实体类别；它既不是染色体区段，也不是育种性状，因此该部分被删除。保留项集中于 `SbMYBAS1`、`SbMYB119` 两个基因、两处 `salt stress`、转基因材料以及各项表型指标。这样既保留了“盐胁迫影响基因表达”和“材料表现出多项性状变化”的核心信息，也避免了类别外扩。

### 2.3 删除套叠统计短语，保留核心性状

第三条样本中的 `genetic gains in grain yield` 与 `genetic gain in yield potential` 属于统计性修饰后的长短语，若与 `grain yield`、`yield potential` 同时保留，会形成冗余套叠并提高后续审查成本。因此本块仅保留 `grain yield` 和 `yield potential` 两个核心性状，并通过 `foxtail millet` 与性状之间的 **HAS** 关系表达语义主干。

### 2.4 对缩略语和隐含性状采取保守策略

第四条关于 `QTL for TKW` 的样本中，`TKW` 可稳定视为性状缩略语，因此保留 `QTL for TKW` 与 `TKW` 之间的 **LOI** 关系。句中 `DH`、`DM` 虽然在作物遗传研究中常可解释为发育或成熟相关性状，但该句未给出展开形式。按照“无充分证据不强标”的原则，本块未将其直接入标。`early maturity`、`post-anthesis grain growth`、`grain size` 与 `yield` 被保留为候选性状实体，以便后续统一审查时进一步确认是否需要补充关系。

### 2.5 修正染色体与标记的边界

第五条样本中，原标注把 `chromosomes 3, 5, and 6` 整体视为一个 **CHR** 实体。为降低边界歧义，本块改为将 `3`、`5`、`6` 分别作为独立的染色体编号实体保留，并删除了泛称 `QTLs` 与 `high-density genetic map` 的不稳定标注。与此同时，`Bin markers` 作为明确的标记对象保留为 **MRK**，`qFLW5-2` 保留为 **QTL**，并与 `FLW` 建立 **LOI** 关系。

### 2.6 区分真正的育种方法与分析技术

第六条样本中，`EMS` 与 `TILLING` 属于可稳定识别的育种/诱变方法，因此保留为 **BM**。相反，`CEL I enzyme` 与 `polyacrylamide electrophoresis` 更接近实验检测手段或实验材料，不宜继续作为 **BM**。因此本块删除了这两项误标，仅保留 `EMS-mutagenized population`、`TILLING population`、`barley` 与 `TX9425` 等核心对象，并通过 **USE** 与 **CON** 关系串联其来源结构。

### 2.7 修正群体类型与材料类型

第七条样本中的 `near isogenic lines (NILs)` 更接近育种群体或近等基因系材料，不宜简单视作普通品种实体，因此改标为 **CROSS**。`QSc/Sl.cib-7H` 作为明确命名 QTL 保留，并与 `spike length (SL)`、`spike compactness (SC)` 建立 **AFF** 关系。

### 2.8 提取稳定性状，压缩泛称列表

第八条样本原先几乎只保留了胁迫与作物名。本次补充了 `salt tolerance level` 作为核心性状实体，并以 `Avena sativa` 与 `Avena nuda` 对其建立 **HAS** 关系，以表达文本所说“参数反映耐盐性水平”的主旨。同时保留后文第二处 `salt concentration` 作为独立 **ABS**，并建立其对 `salt tolerance level` 的 **AFF** 关系。至于 `agronomic traits`、`photosynthetic characteristics` 等泛称列表，由于边界过宽且语义泛化，本块未纳入。

### 2.9 删除构式性假实体

第九条样本原先把 `High salinity inhibited germination` 整体当作 **TRT**，这实际上是一个完整事件描述，不属于稳定实体边界。因此本次只保留 `High salinity`、`Alkali stress` 两个胁迫实体，以及 `germination` 这一生育阶段实体，暂不构建关系，留待统一审查时再决定是否有必要补充最小充分关系。

### 2.10 细化基因列举，避免把关联概念强行入类

第十条样本中，`MTAs` 不在当前实体体系内，因此不标。`100-seed weight` 保留为 **TRT**，`SNPs` 保留为 **MRK**。对括号内列举项，仅保留可稳定视作基因名的 `ERECTA`、`ASR`、`DREB` 与 `AMDH`。`CAP2 promoter` 由于明确带有 `promoter`，其层级并不等同于标准基因实体，因此暂不纳入。

## 3. 后续统一审查关注点

本块进入统一审查时，建议重点复核三个问题。其一，第四条样本中 `early maturity`、`post-anthesis grain growth`、`grain size` 与 `yield` 是否需要在保持保守原则下补充关系。其二，第五条样本中染色体数字拆分是否完全符合既有训练集的边界风格。其三，第九条样本的 `germination` 是否需要与胁迫建立最小关系，还是维持仅保留实体的保守方案更稳妥。
