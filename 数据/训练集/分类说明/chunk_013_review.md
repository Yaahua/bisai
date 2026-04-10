**数据块编号**: chunk_013
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

- **总条数**: 10
- **成功处理条数**: 10
- **包含留空/不确定分类的条数**: 6

## 2. 关键分类理由与权威依据

### 示例 1: 泛称材料类型不强行标为 CROSS

- **文本片段**: `...genetic diversity of 142 sweet sorghum parent lines.`
- **识别结果**:
  - 实体 1: `SSR markers` (MRK)
  - 实体 2: `agronomical traits` (TRT)
  - 实体 3: `sweet sorghum` (CROP)
  - 实体 4: `morphological traits` (TRT)
- **分类理由与权威依据**: 依据 **[GB 4404.1]**，`sweet sorghum` 更适合作为作物层级对象处理，应标为 CROP，而 `parent lines` 在该句中只是泛称材料集合，既不是明确的杂交组合，也不是具体后代群体。结合 **[SUN-2019]** 对育种群体与亲本材料的区分，以及技能中“准确性优先、宁可留空也不错分”的原则，本块删除了把 `parent lines` 机械标为 CROSS 的做法，也删除了由此引出的不稳定关系。

### 示例 2: 复合抗性表达整体视为性状

- **文本片段**: `SiNF-YC2 promotes flowering and improves resistance to salt stress.`
- **识别结果**:
  - 实体 1: `SiNF-YC2` (GENE)
  - 实体 2: `SiCO` (GENE)
  - 实体 3: `flowering` (TRT)
  - 实体 4: `resistance to salt stress` (TRT)
  - 关系 1: `(SiNF-YC2, flowering) -> AFF`
  - 关系 2: `(SiNF-YC2, resistance to salt stress) -> AFF`
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，`SiNF-YC2` 与 `SiCO` 具有明确的基因命名特征，应归为 GENE。依据 **[TaeC-2024]** 的最大共识原则，`resistance to salt stress` 表达的是完整抗逆性状，应整体标注为 TRT，而不是仅抽取 `salt stress` 为 ABS。关系方向按照技能规则保持为“基因影响性状”，即 GENE 作为 AFF 发起方。

### 示例 3: 病害名称与抗病性状区分

- **文本片段**: `Pc39 is a major race-specific crown rust resistance gene...`
- **识别结果**:
  - 实体 1: `Pc39` (GENE)
  - 实体 2: `race-specific crown rust resistance` (TRT)
  - 实体 3: `Israeli accession` (VAR)
  - 实体 4: `Avena sterilis` (CROP)
  - 关系 1: `(Pc39, race-specific crown rust resistance) -> AFF`
  - 关系 2: `(Avena sterilis, Israeli accession) -> CON`
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，`Pc39` 应归为 GENE。这里核心语义是“抗冠锈病性”，不是单独描述病原或病害对象；因此依据 **[TaeC-2024]** 的整体现象优先原则，将 `race-specific crown rust resistance` 整体视为性状 TRT，而不再把 `crown rust` 单独拆成 BIS。`Avena sterilis` 为物种层级作物对象，`Israeli accession` 为具体材料来源，符合 CROP—VAR 的层级关系。

### 示例 4: 生化物质与外观性状分离

- **文本片段**: `Many cultivated soybeans with yellow seed coats lack PAs or anthocyanins...`
- **识别结果**:
  - 实体 1: `soybeans` / `soybean` (CROP)
  - 实体 2: `yellow seed coats` (TRT)
  - 实体 3: `coloured seed coats` (TRT)
  - 关系: `(CROP, TRT) -> HAS`
- **分类理由与权威依据**: 依据 **[TaeC-2024]**，`yellow seed coats` 与 `coloured seed coats` 都是直接可观测的表型表达，宜整体标为 TRT。相对而言，`PAs`、`anthocyanins` 更偏向化学成分或代谢物，不属于本任务中最稳定的实体类别，因此不强行纳入。原有嵌套片段 `seed coats` 与长短重叠表达会造成边界冗余，本块予以删除，保留更完整的性状短语。

### 示例 5: 基因家族名与具体基因实例分开处理

- **文本片段**: `...quinoa trihelix family and families associated with salt stress... Expression analysis identified Cqtrihelix23...`
- **识别结果**:
  - 实体 1: `quinoa` (CROP)
  - 实体 2: `salt stress` (ABS)
  - 实体 3: `Cqtrihelix23` (GENE)
  - 实体 4: `tolerance to salt stress` (TRT)
  - 实体 5: `root development` / `antioxidant system` / `Na+/K+ ratio` (TRT)
  - 关系: `Cqtrihelix23 -> TRT` 采用 AFF
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，`Cqtrihelix23` 具备明确基因命名形式，可稳定标为 GENE；而 `trihelix family`、`NHX`、`CBL` 在此处更偏向家族/类别层面，不一定指向唯一具体基因实例。依据 **[TaeC-2024]** 与技能的保守标注原则，本块保留确定性强的 `Cqtrihelix23`，删除高歧义家族词。对 `tolerance to salt stress` 采用整体 TRT 标注，避免把复合性状拆碎。

### 示例 6: 同义名不建立 CON，分析技术不标为 BM

- **文本片段**: `Foxtail millet (Setaria italica) is a nutritional crop.` 以及 `QTL mapping was conducted with the MULTIQTL package.`
- **识别结果**:
  - `Foxtail millet` 与 `Setaria italica` 均保留为 CROP，但不建立关系
  - `QTL mapping` 未标为 BM
- **分类理由与权威依据**: 按技能规则，同义名或拉丁学名对应关系**不建立 CON**，因此 `Foxtail millet` 与 `Setaria italica` 虽可同时保留为 CROP，但不建立连接。另一方面，依据 **[SUN-2019]**，BM 主要对应具体育种方法；`QTL mapping` 属于分析/定位技术，不宜机械归为育种方法，因此删除了原有 BM 标注。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

- **接收到的审查文档**: 暂无，本块当前处于阶段一初标完成状态。
- **采纳的修改建议**: 暂无。
- **未采纳的修改建议及理由**: 暂无。

## 4. 其他备注

本块已完成单块初标与边界一致性验证。处理时重点压缩了三类高风险误标：一是把泛称材料机械归入 CROSS，二是把复合抗性状拆成单个胁迫词，三是把基因家族、拉丁学名同义关系与分析技术误标成目标类别。后续统一审查时，应继续复核 `Integrative breeding` 是否需要保留为 BM，以及 `durable QTL` 的边界是否还有更优切分方案。
