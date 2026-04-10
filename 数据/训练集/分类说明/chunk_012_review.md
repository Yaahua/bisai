**数据块编号**: chunk_012
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

- **总条数**: 10
- **成功处理条数**: 10
- **包含留空/不确定分类的条数**: 5

## 2. 关键分类理由与权威依据

### 示例 1: 基因—性状关系方向修正

- **文本片段**: `Pc98 is a seedling crown rust resistance gene from the wild oat Avena sterilis accession CAV 1979.`
- **识别结果**:
  - 实体 1: `Pc98` (GENE)
  - 实体 2: `seedling crown rust resistance` (TRT)
  - 实体 3: `Avena sterilis` (CROP)
  - 实体 4: `CAV 1979` (VAR)
  - 关系 1: `(Pc98, seedling crown rust resistance) -> AFF`
  - 关系 2: `(Avena sterilis, CAV 1979) -> CON`
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，`Pc98` 符合禾本科作物基因命名习惯，应归为 GENE；依据 **[TaeC-2024]** 的最大共识原则，`seedling crown rust resistance` 应整体视为抗病/抗性性状，不宜拆散。关系方向上遵循技能规则中“**AFF head 必须是影响发起方**”，因此采用 `Pc98 -> seedling crown rust resistance`，而不是反向标注。`Avena sterilis accession CAV 1979` 中，物种名归为 CROP，具体材料编号归为 VAR，此处理符合材料层级划分逻辑，可援引 **[GB 4404.1]** 对禾谷类作物材料对象的基本划分思路。

### 示例 2: 复合抗逆性状整体标注

- **文本片段**: `...enhancing drought/salt tolerance. FtMYB30 overexpression also reduced ABA sensitivity...`
- **识别结果**:
  - 实体 1: `FtMYB30` (GENE)
  - 实体 2: `drought` (ABS)
  - 实体 3: `salt stress` (ABS)
  - 实体 4: `proline content` (TRT)
  - 实体 5: `antioxidant enzyme activity` (TRT)
  - 实体 6: `RD29A` / `RD29B` / `Cu/ZnSOD` (GENE)
  - 实体 7: `drought/salt tolerance` (TRT)
  - 实体 8: `ABA sensitivity` (TRT)
  - 关系: 采用 `FtMYB30 -> TRT` 的 AFF 方向
- **分类理由与权威依据**: 依据 **[TaeC-2024]**，`drought/salt tolerance` 属于复合抗逆性状表达，应整体标为 TRT，而不是拆成多个零散片段。依据 **[CGSNL-2011]**，`FtMYB30`、`RD29A`、`RD29B`、`Cu/ZnSOD` 均表现为标准基因符号，应标为 GENE。句义上是 `FtMYB30 overexpression` 导致多个生理性状和耐逆结果变化，因此按技能关系规则使用基因作为 AFF 发起方。

### 示例 3: 基因家族名称保守留空

- **文本片段**: `The transcription factor families bHLH, WRKY, AP2/ERF, and MYB-MYC play critical roles...`
- **识别结果**:
  - 保留 `salt stress` (ABS)、`salt-sensitive` (TRT)、`salt-tolerant` (TRT)、`foxtail millet` (CROP)
  - 对 `bHLH`、`WRKY`、`AP2/ERF`、`MYB-MYC` 未继续保留为确定性实体
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，GENE 标注更适合具有明确基因命名特征的基因或基因符号。本句中的 `bHLH`、`WRKY`、`AP2/ERF`、`MYB-MYC` 更像转录因子家族类别，而非具体基因位点。依据 **[TaeC-2024]** 的准确性优先原则，以及技能要求“宁可留空也不错分”，此处采取保守策略，避免把家族名误标为具体基因实例。

### 示例 4: 染色体位置词块拆分

- **文本片段**: `QTL for DON were found on chromosomes 5C, 9D, 13A, 14D and unknown_3. A QTL for FHB was found on 11A.`
- **识别结果**:
  - 实体 1: `QTL for DON` (QTL)
  - 实体 2: `5C` / `9D` / `13A` / `14D` / `unknown_3` / `11A` (CHR)
  - 实体 3: `QTL for FHB` (QTL)
  - 关系: `QTL -> CHR` 采用 LOI
- **分类理由与权威依据**: 依据技能的词块审查标准，应去掉泛化前缀 `chromosomes`，仅保留真正的定位单元 `5C`、`9D`、`13A`、`14D`、`11A` 等作为 CHR。依据 **[QTL-Nomen]**，QTL 与染色体/连锁位置之间应优先体现定位关系，因此使用 `LOI`。`unknown_3` 虽非标准染色体命名，但在原句中承担位置承载功能，故暂按 CHR 保守处理，并在后续统一审查阶段再次核验。

### 示例 5: 杂交群体与实验技术区分

- **文本片段**: `They were examined in 128 recombinant inbred lines... added to the Fulghum x Norline linkage map.`
- **识别结果**:
  - 实体 1: `Fulghum` (VAR)
  - 实体 2: `Norline` (VAR)
  - 实体 3: `recombinant inbred lines` (CROSS)
  - 实体 4: `Fulghum x Norline` (CROSS)
  - 实体 5: `Sixty-five new SSR markers` / `SNP markers` / `CAPS marker` (MRK)
- **分类理由与权威依据**: 依据 **[SUN-2019]**，RIL 群体本质上属于育种群体/杂交后代材料，不应误标为一般方法或普通品种，因此将 `recombinant inbred lines` 归为 CROSS。`Fulghum x Norline` 明确表示杂交组合，也归为 CROSS；其亲本 `Fulghum`、`Norline` 则归为 VAR。对于“标记加入连锁图谱”的表述，当前阶段未强行建立 `MRK -> CROSS` 关系，以避免把图谱载体误当成定位对象。

### 示例 6: 实验技术不作为 BM

- **文本片段**: `The transcriptome profiles of two salt tolerance cultivars were compared under 0.8% NaCl treatment...`
- **识别结果**:
  - 实体 1: `0.8% NaCl treatment` (ABS)
  - `transcriptome` 未标为 BM
- **分类理由与权威依据**: 依据 **[SUN-2019]**，BM 主要对应杂交育种、诱变育种、回交转育、分子标记辅助选择等育种方法；`transcriptome` 属于组学检测/分析技术，不属于育种方法。结合技能中“实验技术不标注为 BM”的经验规则，此处仅保留明确胁迫处理 `0.8% NaCl treatment` 为 ABS。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

- **接收到的审查文档**: 暂无，本块当前处于阶段一初标完成状态。
- **采纳的修改建议**: 暂无。
- **未采纳的修改建议及理由**: 暂无。

## 4. 其他备注

本块已按单块顺序流程完成初步标注，并已进行实体与关系边界一致性验证。当前处理策略保持“准确性优先、宁可留空也不错分”，对基因家族名、图谱承载对象、实验技术等高风险场景采取了保守标注。`unknown_3` 的类型在后续统一审查阶段应再次复核。
