**数据块编号**: chunk_015
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

- **总条数**: 10
- **成功处理条数**: 10
- **包含留空/不确定分类的条数**: 4

## 2. 关键分类理由与权威依据

### 示例 1: `MTAs` 与 `marker-assisted selection` 的区分

- **文本片段**: `Identified MTAs have a pyramiding effect important for breeding. Desirable alleles and superior genotypes are valuable for foxtail millet improvement through marker-assisted selection.`
- **识别结果**:
  - 实体 1: `foxtail millet` (CROP)
  - 实体 2: `marker-assisted selection` (BM)
  - 关系 1: (`foxtail millet`, `marker-assisted selection`) -> USE
- **分类理由与权威依据**: `marker-assisted selection` 指向明确的育种方法，可稳定归入 **BM**。而 `MTAs` 在句中仅表示 marker-trait associations 的研究结果概念，并非稳定的 QTL、MRK 或 GENE 个体，因此不强行入标。该处理符合技能中“准确性优先、宁可留空也不错分”的原则，也符合 `authoritative_references.md` 中关于育种方法与研究分析结果应区分处理的要求。

### 示例 2: 多个命名 QTL 与对应连锁群的逐一映射

- **文本片段**: `Four QTLs, BYDq1, BYDq2, BYDq3 and BYDq4, for BYD tolerance were identified on linkage groups OM1, 5, 7 and 24, respectively.`
- **识别结果**:
  - 实体 1: `BYDq1` (QTL)
  - 实体 2: `BYDq2` (QTL)
  - 实体 3: `BYDq3` (QTL)
  - 实体 4: `BYDq4` (QTL)
  - 实体 5: `BYD tolerance` (TRT)
  - 实体 6: `OM1` (CHR)
  - 实体 7: `5` (CHR)
  - 实体 8: `7` (CHR)
  - 实体 9: `24` (CHR)
  - 关系: 分别建立 QTL→TRT 的 **AFF**，以及 QTL→CHR 的 **LOI**
- **分类理由与权威依据**: 这里存在明确的 `respectively` 对齐结构，故可逐一建立一对一对应关系。根据技能规则，**AFF** 的方向应为影响发起方到受影响性状，即 `(QTL, AFF, TRT)`；而定位关系使用 `(QTL, LOI, CHR)`。该方向性处理与技能文件“关系分类要点”完全一致，同时也符合审查知识库中关于“命名 QTL 可直接与染色体位置及目标性状建立关系”的做法。

### 示例 3: `molecular breeding` 可标，而宽泛的 `genetic materials` 不标

- **文本片段**: `This study provided novel genetic materials for molecular breeding of broomcorn millet varieties with improved agronomic traits.`
- **识别结果**:
  - 实体 1: `molecular breeding` (BM)
  - 实体 2: `broomcorn millet` (CROP)
  - 实体 3: `agronomic traits` (TRT)
  - 关系 1: (`broomcorn millet`, `molecular breeding`) -> USE
  - 关系 2: (`broomcorn millet`, `agronomic traits`) -> HAS
- **分类理由与权威依据**: `molecular breeding` 为明确的育种方式，可入 **BM**。相对地，`genetic materials` 过于泛化，既不指向具体品种、群体，也不指向具体标记或基因，因此留空更稳妥。`HAS(CROP, TRT)` 虽不完全标准化，但技能文件已明确指出这是原始训练数据中的高频非标准模式，应予尊重保留。[authoritative_references.md] 中关于作物育种语义抽取的条目也支持将“作物—目标性状”的拥有关系作为可接受表达。

### 示例 4: 胁迫与作物之间不强行建立关系

- **文本片段**: `MAPK signaling and oxidative metabolism were key pathways in quinoa under cold stress.`
- **识别结果**:
  - 实体 1: `quinoa` (CROP)
  - 实体 2: `cold stress` (ABS)
  - 实体 3: `lipid peroxidation` (TRT)
  - 实体 4: `oxidative damage` (TRT)
  - 关系 1: (`cold stress`, `lipid peroxidation`) -> AFF
  - 关系 2: (`cold stress`, `oxidative damage`) -> AFF
- **分类理由与权威依据**: 原始标注曾尝试建立 `cold stress -> quinoa` 的关系，但这类“胁迫作用于作物”在本任务既有标签集中不如“胁迫影响性状/表现”稳定，因此本块改为只保留 `ABS -> TRT` 的最小充分关系。这与技能中强调的“准确性优先”一致，也符合 `breeding_knowledge_base.md` 对环境胁迫语义的常识性描述：胁迫更稳定地作用于可测性状或损伤结果，而非直接构成作物实体关系。

### 示例 5: `F1 hybrids` 判为 CROSS 而非 VAR

- **文本片段**: `The agronomic performance and chromosome behavior of autotetraploid sorghum inbreds and F1 hybrids were investigated.`
- **识别结果**:
  - 实体 1: `autotetraploid sorghum inbreds` (VAR)
  - 实体 2: `sorghum` (CROP)
  - 实体 3: `F1 hybrids` (CROSS)
- **分类理由与权威依据**: 技能文件“关键分类规则”明确指出，杂交后代群体如 `RILs` 应优先标为 **CROSS**，而非 **VAR**。同理，`F1 hybrids` 体现的是杂交群体属性，应归入 **CROSS**。这一处理与 `authoritative_references.md` 中引用的群体遗传与作物育种文献口径一致。

### 示例 6: `QTNs` 保留，泛称数量统计不拆成伪实体

- **文本片段**: `117 candidate genes were mapped to these QTNs. They are associated with six major traits: 20 for flowering time, 16 for maturity...`
- **识别结果**:
  - 实体: `QTNs` (QTL), `flowering time` (TRT), `maturity` (TRT), `plant height` (TRT), `seed number per plant` (TRT), `seed yield` (TRT), `seed weight` (TRT), `Sobic.001G196700` (GENE), `Sobic.005G176100` (GENE), `stress responses` (TRT), `SbMADS1` (GENE), `SbFT` (GENE)
  - 关系: `Sobic.001G196700 -> flowering time` 使用 **AFF**；`Sobic.005G176100 -> stress responses` 使用 **AFF**
- **分类理由与权威依据**: `QTNs` 在语义上属于位点层级，可按 **QTL** 近似吸收。数字统计短语如 `20 for flowering time` 中的前置数字只是频数信息，不应拆成实体。对 `SbMADS1` 与 `SbFT`，虽然句中说明其参与开花调控，但未给出与标准性状短语的稳定对齐文本，因此先保留基因实体而不强建关系，以减少过推断。

### 示例 7: 染色体数字拆分而非整串合并

- **文本片段**: `one each on chromosomes 1, 2, 4, and 6, and two on chromosomes 5 and 9`
- **识别结果**:
  - 实体 1: `loci` (QTL)
  - 实体 2–7: `1`、`2`、`4`、`6`、`5`、`9` (CHR)
  - 实体 8: `candidate genes` (GENE)
- **分类理由与权威依据**: 为降低实体边界歧义，本块未保留长串 `chromosomes 1, 2, 4, and 6` 作为单个实体，而是将每个编号拆为独立 **CHR**。这种处理更利于后续精确关系校验，也符合词块审查中“避免把并列列表合并为单一实体”的做法。

### 示例 8: 泛称基因列表采取压缩保留策略

- **文本片段**: `215 candidate genes were identified at these loci, including eleven transcription factor genes, seven protein kinase genes...`
- **识别结果**:
  - 实体 1: `SNPs` (MRK)
  - 实体 2: `drought tolerance` (TRT)
  - 实体 3: `candidate loci` (QTL)
  - 实体 4: `drought stress` (ABS)
- **分类理由与权威依据**: `candidate genes`、`transcription factor genes`、`protein kinase genes` 均为类别性泛称，不是稳定命名基因；若全部保留，容易在后续全量修订时引发“泛称—泛称”伪关系。因此本块采取压缩策略，只保留最稳定的标记、性状、位点与胁迫实体。该做法符合技能中“宁可留空也不错分”的原则。

### 示例 9: `Recombinant inbreed lines` 归入 CROSS

- **文本片段**: `164 Recombinant inbreed lines were created from a cross between Longgu7 and Yugu1.`
- **识别结果**:
  - 实体 1: `Recombinant inbreed lines` (CROSS)
  - 实体 2: `Longgu7` (VAR)
  - 实体 3: `Yugu1` (VAR)
  - 关系 1: (`Longgu7`, `Recombinant inbreed lines`) -> CON
  - 关系 2: (`Yugu1`, `Recombinant inbreed lines`) -> CON
- **分类理由与权威依据**: 虽然原文拼写为 `inbreed`，但其语义显然对应重组自交系群体。根据技能规则，群体应优先归为 **CROSS**。父本品种与群体之间使用 **CON** 表示构成来源，较为贴合语义主干。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

- **接收到的审查文档**: 待统一审查后补充
- **采纳的修改建议**:
  - 待阶段三填写
- **未采纳的修改建议及理由**:
  - 待阶段三填写

## 4. 其他备注

本块中有若干“泛称实体”与“并列定位列表”场景，已统一采取保守处理：命名对象优先、类别性泛称从严、关系只保留有明确触发词支撑的最小充分集。统一审查阶段建议重点复核 Sample 7 与 Sample 8，判断是否需要在尊重训练集风格的前提下补回部分泛称级关系。
