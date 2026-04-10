**数据块编号**: chunk_011
**处理时间**: 2026-04-10 16:30:00

## 1. 整体处理情况

- **总条数**: 10
- **成功处理条数**: 10
- **包含留空/不确定分类的条数**: 0

## 2. 关键分类理由与权威依据

### 示例 1: 作物与性状关系的保留

- **文本片段**: "The transgenic Arabidopsis seedlings had greater root length and mature plants had higher survival rates under drought conditions."
- **识别结果**:
  - 实体 1: "Arabidopsis" (CROP)
  - 实体 2: "root length" (TRT)
  - 实体 3: "survival rates" (TRT)
  - 实体 4: "drought conditions" (ABS)
  - 关系: (Arabidopsis, root length) -> HAS; (Arabidopsis, survival rates) -> HAS
- **分类理由与权威依据**: 依据 `[LU-2006]` 与 `[LU-Sorghum-2006]` 中对作物农艺性状、抗性相关表型的描述方式，"root length" 与 "survival rates" 均属于可观测性状，应标注为 TRT。结合原始训练集中已存在的 `HAS: (CROP, TRT)` 扩展模式，保留由作物指向性状的 HAS 关系，以利模型学习原始语料中的真实标注分布。

### 示例 2: 品种与作物的从属关系

- **文本片段**: "The quinoa cultivar Shelly seeds and seedlings were treated with NaCl solution."
- **识别结果**:
  - 实体 1: "quinoa" (CROP)
  - 实体 2: "Shelly" (VAR)
  - 实体 3: "NaCl solution" (ABS)
  - 关系: (quinoa, Shelly) -> CON
- **分类理由与权威依据**: 依据 `[SUN-2019]` 关于作物与品种层级的基本界定，以及知识库中对 CROP 与 VAR 的区分，"quinoa" 属于作物类型，"Shelly" 属于具体品种，二者可建立从属关系。"NaCl solution" 在处理语境中表示盐胁迫来源，依据 `[通用生物学常识]` 归为 ABS。

### 示例 3: 基因与性状影响关系

- **文本片段**: "Notable candidate genes include FPA for flowering time (VRADI10G01470 ... )"
- **识别结果**:
  - 实体 1: "FPA" (GENE)
  - 实体 2: "flowering time" (TRT)
  - 实体 3: "VRADI10G01470" (GENE)
  - 关系: (FPA, flowering time) -> AFF
- **分类理由与权威依据**: 依据 `[CGSNL-2011]`，"FPA" 与 "VRADI10G01470" 均符合基因命名习惯，应标注为 GENE。"flowering time" 是标准生育期相关性状，依据 `[TaeC-2024]` 的最大共识原则整体标为 TRT。句中语义明确表示候选基因与开花时间相关，因此保留 `AFF: (GENE, TRT)`。

### 示例 4: 非生物胁迫与离子相关性状

- **文本片段**: "Salt or alkali treatment for 3 days ... increased Na+ levels ... Under alkali stress, K+ levels decreased ..."
- **识别结果**:
  - 实体 1: "Salt" (ABS)
  - 实体 2: "alkali treatment" (ABS)
  - 实体 3: "Na+ levels" (TRT)
  - 实体 4: "alkali stress" (ABS)
  - 实体 5: "K+ levels" (TRT)
  - 关系: (Salt, Na+ levels) -> AFF; (alkali treatment, Na+ levels) -> AFF; (alkali stress, K+ levels) -> AFF
- **分类理由与权威依据**: 依据知识库中 ABS 与 TRT 的区分，盐与碱胁迫属于环境胁迫，应标注为 ABS；离子含量属于生理性状，应标注为 TRT。胁迫改变离子积累或含量的方向符合 `AFF: (ABS, TRT)` 的常见逻辑，故保留相关影响关系。

### 示例 5: 固定搭配性状整体保留

- **文本片段**: "... resulted in longer roots and increased salt tolerance."
- **识别结果**:
  - 实体 1: "SbMYBHv33" (GENE)
  - 实体 2: "longer roots" (TRT)
  - 实体 3: "salt tolerance" (TRT)
  - 关系: (SbMYBHv33, longer roots) -> AFF; (SbMYBHv33, salt tolerance) -> AFF
- **分类理由与权威依据**: 依据 `[TaeC-2024]` 的最大共识原则，"salt tolerance" 属于育种文本中的固定性状表达，不应拆分为 "salt" 与 "tolerance" 两个实体，应整体标注为 TRT。基因导致根系和耐盐性变化，语义上符合 `AFF: (GENE, TRT)`。

### 示例 6: 宽泛 QTL 提及与缩写性状

- **文本片段**: "19 QTLs were detected for five traits: one QTL for CP, five for NDF, three for ADF, two for ADL, and eight for HC."
- **识别结果**:
  - 实体 1: "QTL" (QTL)
  - 实体 2: "QTLs" (QTL)
  - 实体 3: "CP" (TRT)
  - 实体 4: "NDF" (TRT)
  - 实体 5: "ADF" (TRT)
  - 实体 6: "ADL" (TRT)
  - 实体 7: "HC" (TRT)
- **分类理由与权威依据**: 依据 `[QTL-Nomen]`，文本中对 QTL 的直接指称可作为 QTL 类实体保留。各缩写项在上下文中明确作为 five traits 的组成，应归入 TRT。由于句中未把具体某个 QTL 名称与某个具体 trait 逐一锚定到稳定边界，初标阶段未强行补充关系，保留为后续统一审查时再核定。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

- **接收到的审查文档**: 待统一审查阶段生成 `chunk_011_audit.md`
- **采纳的修改建议**:
  - 待填写
- **未采纳的修改建议及理由**:
  - 待填写

## 4. 其他备注

本块初标遵循“先保证实体边界与关系方向的可验证性，再在统一审查阶段集中处理挑剔性修正”的原则。对原始训练集中已出现的扩展关系模式，本块初标阶段尽量予以保留，避免过度标准化。
