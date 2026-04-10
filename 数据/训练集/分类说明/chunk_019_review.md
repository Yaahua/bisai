**数据块编号**: chunk_019
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

- **总条数**: 10
- **成功处理条数**: 10
- **包含留空/不确定分类的条数**: 0

## 2. 关键分类理由与权威依据

### 示例 1: 分子标记与育种方法的区分

- **文本片段**: "84,521 SNP markers were identified by Genotyping-by-Sequencing (GBS)..."
- **识别结果**:
  - 实体 1: "84,521 SNP markers" (MRK)
  - 实体 2: "Genotyping-by-Sequencing" / "GBS" (BM)
- **分类理由与权威依据**: 依据 **[SUN-2019]**，测序、分型、图谱构建、QTL mapping 等属于标准育种/遗传分析方法；依据 **[上下文推断]**，SNP marker 明确指向分子标记本体，因此标为 MRK，而 GBS 是识别标记所使用的方法，标为 BM。相应关系采用 `USE(BM, MRK)`，不再保留原先噪声性的 `CON(MRK, MRK)`。

### 示例 2: SSR 相关术语的归类

- **文本片段**: "SSR loci in the TB genome... SSR primers... primer pairs for polymorphic SSR loci..."
- **识别结果**:
  - 实体 1: "SSR loci" (MRK)
  - 实体 2: "SSR primers" (MRK)
  - 实体 3: "primer pairs" (MRK)
  - 实体 4: "core germplasm resources" (VAR)
- **分类理由与权威依据**: 依据 **[NY/T 2467-2025]**，SSR 属于标准分子标记体系，SSR loci、SSR primers 与 primer pairs 均应归入 MRK；依据 **[TaeC-2024]** 的最大共识原则，"core germplasm resources" 在该句中指被分型利用的资源群体，作为材料集合处理为 VAR 更符合阅读和标注一致性。因此保留 `USE(VAR, MRK)`，去除原先不稳定的 `USE(MRK, MRK)` 与 `LOI(MRK, VAR)`。

### 示例 3: 嵌套与重叠实体的消解

- **文本片段**: "plant biomass in 32 sorghum germplasm resources"
- **识别结果**:
  - 实体 1: "sorghum" (CROP)
  - 实体 2: "sorghum germplasm resources" (VAR)
- **分类理由与权威依据**: 依据 **[TaeC-2024]** 的最大共识原则，对于可整体理解的材料短语，优先保留完整表达，因此将 "sorghum germplasm resources" 整体标为 VAR，并删除与其重叠的第二个 "sorghum" 子串实体，避免同一位置发生不必要重叠。作物层级信息仍通过 `CON(CROP, VAR)` 保留。

### 示例 4: QTL、性状与染色体定位关系

- **文本片段**: "The QTLs for frost survival and plant emergence... located on chromosomes Sb02, Sb07, and Sb08."
- **识别结果**:
  - 实体 1: "QTLs" (QTL)
  - 实体 2: "frost survival" (TRT)
  - 实体 3: "plant emergence" (TRT)
  - 实体 4: "chromosomes Sb02, Sb07, and Sb08" (CHR)
- **分类理由与权威依据**: 依据 **[QTL-Nomen]**，QTL 是与目标性状相联系的遗传位点；依据 **[TaeC-2024]**，"frost survival" 与 "plant emergence" 均是完整性状表达，应整体标注为 TRT。因此本块同时保留 `LOI(QTL, TRT)` 与 `LOI(QTL, CHR)`，以分别体现 QTL 的性状对应关系和染色体定位信息。

### 示例 5: 基因与胁迫、性状的关系方向

- **文本片段**: "CqZF-HD14 promotes photosynthetic pigment accumulation under drought stress... enhances drought tolerance."
- **识别结果**:
  - 实体 1: "CqZF-HD14" (GENE)
  - 实体 2: "photosynthetic pigment accumulation" (TRT)
  - 实体 3: "drought stress" (ABS)
  - 实体 4: "antioxidant system" (TRT)
  - 实体 5: "drought tolerance" (TRT)
- **分类理由与权威依据**: 依据 **[CGSNL-2011]**，"CqZF-HD14" 符合基因命名习惯，应标注为 GENE；依据 **[TaeC-2024]**，"drought tolerance"、"photosynthetic pigment accumulation" 等为可整体理解的性状表达，应标注为 TRT。关系上，句子语义是基因促进相关性状，而不是基因影响胁迫本身，因此保留 `AFF(GENE, TRT)`，删除原先方向不当的 `AFF(GENE, ABS)`。

### 示例 6: 温度区间作为胁迫条件的处理

- **文本片段**: "Recovery percentage was highest at 400 mM salinity and 25 mM alkalinity under 10-20°C... lower under 25-35°C"
- **识别结果**:
  - 实体 1: "10-20°C" (ABS)
  - 实体 2: "25-35°C" (ABS)
  - 实体 3: "Recovery percentage" (TRT)
- **分类理由与权威依据**: 依据 **[上下文推断]**，这里的温度区间不是一般数值，而是明确的处理环境条件；结合 **[TaeC-2024]** 的最大共识原则，可将完整温度区间整体标注为环境胁迫/处理条件 ABS，并与 "Recovery percentage" 建立 `AFF(ABS, TRT)`，从而保留实验条件对恢复指标的影响信息。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

- **接收到的审查文档**: 待统一审查阶段补充
- **采纳的修改建议**:
  - 待统一审查阶段补充
- **未采纳的修改建议及理由**:
  - 待统一审查阶段补充

## 4. 其他备注

本块已完成初步标注与说明，当前仍处于“先全部初标、后统一审查”的阶段。后续若统一审查发现 QTL-TRT、CROP-GENE 或 VAR-MRK 方向存在更高一致性方案，将在阶段三统一回填本说明文档。
