# chunk_026 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 37 处（新增实体 17 个、修改标签 3 处、删除实体 6 个、新增关系 10 条、修改关系 1 条）

---

## 一、整体说明

本块涉及大麦、高粱、蚕豆、玉米等作物的 QTL 定位、基因功能、转录组分析和育种方法研究。原始标注存在以下系统性问题：
1. 生物学过程描述词被错误标注为 TRT（light response、plant hormone、abiotic stress response 等）
2. 形容词前缀被错误标注为 ABS（heat-）
3. 关系方向错误（AFF 的 tail 为 ABS 而非 TRT）
4. 分析方法漏标（Transcriptomic analysis、Phylogenetic analysis、IP-MS）
5. 并列基因漏标（CHI、AACT、IDH、NADP-ME）

---

## 二、逐条修改说明

### 样本 0

**修改 1**：新增 `acidic conditions` @24:40，label=`ABS`

**理由**：acidic conditions（酸性条件）是土壤酸性胁迫，属于 ABS（非生物胁迫）。原文 "under acidic conditions" 明确表明试验在酸性胁迫环境下进行。

> 依据：K8 §1.8 ABS；K7 §2.6（土壤酸性胁迫标为 ABS）。

**修改 2**：新增 `yield-related traits` @55:74，label=`TRT`

**理由**：yield-related traits（产量相关性状）是可量化的农艺性状集合，属于 TRT。

> 依据：K8 §1.3 TRT。

---

### 样本 1

**修改 1**：`Ethiopian sorghum germplasm` @132:159，CROP→VAR

**理由**：Ethiopian sorghum germplasm 是埃塞俄比亚高粱种质资源库，是种质材料集合，不是具体作物名称，应标为 VAR（种质材料）。

> 依据：K8 §1.5 VAR；K7 §2.1（种质资源库标为 VAR）。

**修改 2**：新增 `sorghum` @141:148，label=`CROP`

**理由**：sorghum 是作物名称，在 "Ethiopian sorghum germplasm" 中嵌套出现，应单独标注为 CROP。

> 依据：K8 §1.5 CROP；K1 §2.1（嵌套实体均需标注）。

---

### 样本 2

**修改 1**：新增 `Transcriptomic analysis` @0:21，label=`BM`

**理由**：Transcriptomic analysis（转录组分析）是遗传分析方法，属于 BM。

> 依据：K8 §1.4 BM。

**修改 2**：新增 `CHI` @222:225、`AACT` @227:231、`IDH` @239:242、`NADP-ME` @244:251，label=`GENE`

**理由**：原文 "Key genes involved include CHS, CHI, AACT, ENO1, IDH, NADP-ME, and HAO2L" 中，CHI、AACT、IDH、NADP-ME 均是基因名称，原始标注只标了 CHS、ENO1、HAO2L，漏标了其余 4 个。

> 依据：K8 §1.1 GENE；error_patterns §3.6（并列实体补齐）。

**修改 3**：新增 `flavonoid biosynthesis` @75:96，label=`TRT`；`vigor loss` @332:342，label=`TRT`

**理由**：flavonoid biosynthesis（类黄酮生物合成）是代谢通路，vigor loss（活力损失）是种子活力性状，均属于 TRT。

> 依据：K8 §1.3 TRT。

---

### 样本 4

**修改 1**：删除 `light response` @219:233、`plant hormone` @235:248、`abiotic stress response` @250:273、`plant growth and development` @279:307，label=`TRT`

**理由**：这四个词组均是基因顺式元件（cis-elements）相关的生物学功能描述，不是可量化的农艺性状（TRT）。TRT 应为具体可测量的表型性状，如产量、株高等，而非基因功能类别。

> 依据：K8 §1.3 TRT（需为可量化农艺性状）；K7 §2.4（基因功能描述不标为 TRT）。

**修改 2**：新增 `Phylogenetic analysis` @84:104，label=`BM`；`VfAP2/ERF` @169:178，label=`GENE`

**理由**：Phylogenetic analysis（系统发育分析）是分析方法；VfAP2/ERF 第二次出现（"VfAP2/ERF promoters"）漏标。

> 依据：K8 §1.4 BM；K1 §2.1（同一实体多次出现均需标注）。

---

### 样本 5

**修改 1**：删除 `heat-` @203:208，label=`ABS`

**理由**：`heat-` 是形容词前缀（"heat- and water-stressed conditions"），不是独立的胁迫实体名词。

> 依据：K1 §1.3；error_patterns §2.1（形容词不标为实体）。

**修改 2**：新增 `bPb-5529` @101:109，label=`MRK`；`SG QTL` @170:176，label=`QTL`

**理由**：bPb-5529 是分子标记；SG QTL 第二次出现漏标。

> 依据：K8 §1.6 MRK；K1 §2.1。

**修改 3**：新增 LOI 关系 ×5

**理由**：heat-stress QTL 与 bPb-5529、5H、root length、root-shoot ratio 均有定位关系；SG QTL 与 5H 有定位关系，均漏标。

> 依据：K8 §2.5 LOI；K2 §1.2（QTL→位置/性状）。

---

### 样本 6

**修改 1**：新增 `IP-MS` @0:5，label=`BM`

**理由**：IP-MS（免疫共沉淀质谱）是蛋白质互作分析方法，属于 BM。

> 依据：K8 §1.4 BM。

**修改 2**：`immune response` @134:149，BIS→TRT

**理由**：immune response（免疫响应）是植物对病原体的抵抗反应，是可量化的性状表现（如免疫响应强度），属于 TRT，而非具体病害（BIS）。

> 依据：K8 §1.3 TRT vs §1.10 BIS；K7 §2.7（免疫响应性状标为 TRT）。

**修改 3**：新增 `drought stress response` @105:128，label=`TRT`；修改 AFF(SiUBC39, drought stress) → AFF(SiUBC39, drought stress response)

**理由**：原关系 AFF(SiUBC39, drought stress) 方向错误，AFF 的 tail 应为 TRT（性状），不能为 ABS（胁迫因子）。应补标 "drought stress response"（TRT），并修正关系方向。

> 依据：K2 §1.1 AFF（head: GENE, tail: TRT）；K8 §2.3 AFF。

---

### 样本 7

**修改 1**：删除 `exogenous phytohormones` @214:237，label=`ABS`

**理由**：exogenous phytohormones（外源植物激素）是处理类别描述，不是具体胁迫因子，不符合 ABS 定义。

> 依据：K8 §1.8 ABS；K7 §2.6（激素类别描述不标为 ABS）。

**修改 2**：新增 `Phylogenetic analysis` @0:20，label=`BM`；`abscisic acid` @239:252，label=`ABS`；`salicylic acid` @272:285，label=`ABS`

**理由**：Phylogenetic analysis 是分析方法；abscisic acid（脱落酸）和 salicylic acid（水杨酸）是植物胁迫信号分子，属于 ABS，与 methyl jasmonate 并列，漏标。

> 依据：K8 §1.4 BM；K8 §1.8 ABS；error_patterns §3.6（并列实体补齐）。

---

### 样本 8

**修改**：新增 `enzyme thermostability` @30:50，label=`TRT`；新增 AFF(Sd3, enzyme thermostability)

**理由**：enzyme thermostability（酶热稳定性）是可量化的生化性状，属于 TRT。原文 "Sd3 allele increased enzyme thermostability" 明确表明 Sd3 影响酶热稳定性，应建立 AFF 关系。

> 依据：K8 §1.3 TRT；K8 §2.3 AFF。

---

### 样本 9

**修改**：新增 `stem diameter` @79:92，label=`TRT`

**理由**：stem diameter 在 "SXAU8006 for stem diameter" 中第一次出现，漏标。

> 依据：K1 §2.1（同一实体多次出现均需标注）。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `acidic conditions` @24:40 ✓；`yield-related traits` @55:74 ✓
- `sorghum` @141:148 ✓
- `Transcriptomic analysis` @0:21 ✓；`CHI` @222:225 ✓；`AACT` @227:231 ✓；`IDH` @239:242 ✓；`NADP-ME` @244:251 ✓；`flavonoid biosynthesis` @75:96 ✓；`vigor loss` @332:342 ✓
- `Phylogenetic analysis` @84:104 ✓；`VfAP2/ERF` @169:178 ✓
- `bPb-5529` @101:109 ✓；`SG QTL` @170:176 ✓
- `IP-MS` @0:5 ✓；`drought stress response` @105:128 ✓；`blast resistance` @238:253 ✓
- `Phylogenetic analysis` @0:20 ✓；`abscisic acid` @239:252 ✓；`salicylic acid` @272:285 ✓
- `enzyme thermostability` @30:50 ✓
- `stem diameter` @79:92 ✓
