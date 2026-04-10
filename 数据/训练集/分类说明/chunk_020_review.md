**数据块编号**: chunk_020
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

- **总条数**: 10
- **成功处理条数**: 10
- **包含留空/不确定分类的条数**: 0

## 2. 关键分类理由与权威依据

### 示例 1: 基因集合与胁迫响应表达的区分

- **文本片段**: "180 drought-inducible transcription factors were identified... drought responsive DEGs... regulating drought stress response."
- **识别结果**:
  - 实体 1: "drought-inducible transcription factors" (GENE)
  - 实体 2: "drought responsive DEGs" (GENE)
  - 实体 3: "drought stress response" (TRT)
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，转录因子、DEGs 在文献中通常指基因或基因集合，应归入 GENE；依据 **[TaeC-2024]** 的最大共识原则，"drought stress response" 在该句中表示完整响应性状/生理反应，整体标注比拆成局部成分更稳定，因此处理为 TRT，而不再将其中的局部字符串单独拆作 ABS。

### 示例 2: 表型分期标准与材料名称的处理

- **文本片段**: "The BBCH scale... describe morphological development stages in M. × giganteus, using observations of the 'Freedom' and 'Illinois' clones..."
- **识别结果**:
  - 实体 1: "BBCH scale" (BM)
  - 实体 2: "morphological development stages" (TRT)
  - 实体 3: "M. × giganteus" (CROP)
  - 实体 4: "'Freedom'"、"'Illinois'" (VAR)
- **分类理由与权威依据**: 依据 **[SUN-2019]**，BBCH scale 属于作物发育阶段描述与调查使用的方法/标准体系，归入 BM；依据 **[TaeC-2024]**，带引号的 clone 名称在该上下文中对应具体材料单元，应整体作为 VAR 保留。因此建立 `USE(BM, TRT)` 与 `CON(CROP, VAR)`，同时保留作物与发育阶段的 `HAS` 信息。

### 示例 3: 标记与位点的定位关系

- **文本片段**: "Five AFLP markers were linked to the sht1 locus... e54m58/610 and e55m46/320 cosegregated with the sht1 locus..."
- **识别结果**:
  - 实体 1: "AFLP markers" (MRK)
  - 实体 2: "e54m58/610"、"e55m46/320" (MRK)
  - 实体 3: "sht1 locus" (QTL)
- **分类理由与权威依据**: 依据 **[QTL-Nomen]** 与 **[通用生物学常识]**，文中 locus 表示与性状相关的遗传位点，可按 QTL 处理；具体 AFLP marker 与 locus 的语义是连锁/共分离定位关系，因此使用 `LOI(MRK, QTL)` 表达，而不是其他包含型关系。

### 示例 4: 杂交群体与亲本方向

- **文本片段**: "F2 population from the cross Hatiexi No. 1 x Zhe5819"
- **识别结果**:
  - 实体 1: "F2 population from the cross Hatiexi No. 1 x Zhe5819" (CROSS)
  - 实体 2: "Hatiexi No. 1" (VAR)
  - 实体 3: "Zhe5819" (VAR)
- **分类理由与权威依据**: 依据 **[SUN-2019]**，F2 population 明确属于杂交后代群体，归入 CROSS；依据 **[TaeC-2024]** 的可读性原则，完整交配表达整体保留。关系方向上，群体包含亲本来源信息，因此采用 `CON(CROSS, VAR)`，不再沿用方向相反的写法。

### 示例 5: 胁迫条件、标记与性状的组合判断

- **文本片段**: "SiDREB2 was significantly up-regulated by dehydration (polyethylene glycol) and salinity (NaCl). A synonymous SNP associated with dehydration tolerance... in a core set of 45 foxtail millet accessions."
- **识别结果**:
  - 实体 1: "dehydration"、"salinity" (ABS)
  - 实体 2: "SiDREB2" (GENE)
  - 实体 3: "SNP" (MRK)
  - 实体 4: "dehydration tolerance" (TRT)
  - 实体 5: "foxtail millet accessions" (VAR)
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，"SiDREB2" 为标准基因命名形式，应标注为 GENE；依据 **[TaeC-2024]**，"dehydration tolerance" 是完整性状短语，应整体标注为 TRT。语义上，dehydration 和 salinity 触发基因表达变化，故采用 `AFF(ABS, GENE)`；而 SNP 与耐脱水性之间为关联/影响关系，可使用 `AFF(MRK, TRT)` 表达。同时将材料集合整体标为 VAR，并用 `CON(CROP, VAR)` 保留作物归属。

### 示例 6: 泛化性描述中的方法与性状边界

- **文本片段**: "Early maturity is an important agronomic trait... Genes determining flowering affect flowering time, which directly affects crop maturity and yield."
- **识别结果**:
  - 实体 1: "Early maturity" (TRT)
  - 实体 2: "Genes determining flowering" (GENE)
  - 实体 3: "flowering time"、"crop maturity"、"yield" (TRT)
- **分类理由与权威依据**: 依据 **[LU-2006]** 与 **[LU-Sorghum-2006]**，成熟期、产量、开花期均属于育种研究中的标准农艺性状范畴，应归为 TRT；依据 **[TaeC-2024]**，这些名词短语应整体保留。关系上，仅保留文本中明示的影响链 `AFF(GENE, TRT)` 与 `AFF(TRT, TRT)`，删除不够稳定的“早熟→多熟制”类扩展推断。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

- **接收到的审查文档**: 待统一审查阶段补充
- **采纳的修改建议**:
  - 待统一审查阶段补充
- **未采纳的修改建议及理由**:
  - 待统一审查阶段补充

## 4. 其他备注

本块已完成初步标注与说明。至此，chunk_011 至 chunk_020 的初标阶段已完成，后续将按既定顺序进入统一审查阶段，并逐块形成审查报告后再进行全量修订。
