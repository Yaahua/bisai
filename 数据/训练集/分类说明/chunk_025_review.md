# chunk_025 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 28 处（新增实体 13 个、修改边界 2 处、修改标签 5 处、删除实体 4 个、新增关系 3 条、删除关系 2 条）

---

## 一、整体说明

本块涉及蚕豆、谷子、高粱、水稻等作物的 QTL 定位、基因功能、胁迫响应和光合特性研究。原始标注存在以下系统性问题：
1. 形容词被错误标注为实体（drought-stressed、abiotic）
2. 光系统蛋白质复合体（PSI、PSII）被错误标注为 TRT，应为 GENE
3. VAR 实体边界过宽（包含描述词）
4. 分析方法漏标（Linkage analysis、Genome-wide association analysis）

---

## 二、逐条修改说明

### 样本 0

**修改 1**：删除 `drought-stressed` @64:80，label=`ABS`

**理由**：`drought-stressed` 是形容词修饰词（"drought-stressed leaves"），不是独立的胁迫实体名词。依据 K1 §1.3，标注应为完整名词短语，形容词不单独标注。

> 依据：K1 §1.3 边界精确性原则；error_patterns §2.1（形容词不标为实体）。

**修改 2**：新增 `abscisic acid` @107:120，label=`ABS`

**理由**：abscisic acid（脱落酸，ABA）是植物应对胁迫的重要信号分子，属于 ABS（非生物胁迫相关物质）。原文 "abscisic acid-dependent and independent signaling pathways" 明确提及 ABA 信号通路。

> 依据：K8 §1.8 ABS；K7 §2.6（植物激素可标为 ABS）。

---

### 样本 1

**修改**：新增 `Linkage analysis` @0:16 BM；`Association analysis` @158:178 BM

**理由**：Linkage analysis（连锁分析）和 Association analysis（关联分析）均是遗传分析方法，属于 BM。原始数据漏标。

> 依据：K8 §1.4 BM；K7 §2.2（遗传分析方法标为 BM）。

---

### 样本 2

**修改**：新增 `ABA` @363:366，label=`ABS`

**理由**：ABA（脱落酸）在原文第三句 "mediating plant responses to ABA, salt, and drought" 中出现，与 salt、drought 并列，均是胁迫信号，应标为 ABS。

> 依据：K8 §1.8 ABS；error_patterns §3.6（并列实体补齐）。

---

### 样本 3

**修改 1**：`middle-heading cultivar Shinanotsubuhime` @163:203 → `Shinanotsubuhime` @187:203

**理由**：原始边界包含 "middle-heading cultivar" 描述词，VAR 实体应仅包含品种名称本身。

> 依据：K1 §1.3 边界精确性原则；K8 §1.5 VAR（品种名称不含描述词）。

**修改 2**：`early heading cultivar Yuikogane` @212:244 → `Yuikogane` @235:244

**理由**：同上，应缩减为品种名称本身。

> 依据：K1 §1.3；K8 §1.5 VAR。

**修改 3**：删除 `field conditions` @252:268，label=`ABS`

**理由**：field conditions（田间条件）是试验环境描述，不是具体的非生物胁迫因子，不符合 ABS 定义（K8 §1.8 ABS：干旱、盐碱、高温等具体胁迫）。

> 依据：K8 §1.8 ABS；K7 §2.6（试验环境不标为 ABS）。

**修改 4**：`late heading` @310:322，label=`GST` → `TRT`

**理由**：late heading（晚抽穗）是抽穗期性状，属于 TRT（可量化农艺性状），而非 GST（生育阶段）。GST 应用于"灌浆期"、"开花期"等具体生育阶段描述，而非性状表现。

> 依据：K8 §1.3 TRT vs §1.9 GST；K7 §2.5（抽穗期性状标为 TRT）。

---

### 样本 4

**修改**：新增 `Genome-wide association analysis` @0:32，label=`BM`

**理由**：Genome-wide association analysis（全基因组关联分析）是遗传分析方法，属于 BM。原始数据漏标。

> 依据：K8 §1.4 BM。

---

### 样本 5

**修改 1**：新增 `Chr1_61095994` @23:36，label=`MRK`

**理由**：Chr1_61095994 是染色体位置特定的分子标记，应标为 MRK。

> 依据：K8 §1.6 MRK。

**修改 2**：新增 `glutathione S-transferase` @177:201，label=`GENE`；`MYB-bHLH-WD40 complex` @305:327，label=`GENE`

**理由**：glutathione S-transferase（谷胱甘肽 S-转移酶）是基因家族；MYB-bHLH-WD40 complex（转录因子复合体）是基因调控复合体，均属于 GENE。

> 依据：K8 §1.1 GENE；K7 §2.3（蛋白质复合体和基因家族标为 GENE）。

---

### 样本 6

**修改**：新增 `Chalk5` @23:29，label=`GENE`；新增 AFF(Chalk5 @23:29, endosperm chalkiness)

**理由**：Chalk5 第一次出现（"Elevated expression of Chalk5"）漏标。原文明确说明 Chalk5 表达升高导致胚乳垩白增加，应建立 AFF 关系。

> 依据：K1 §2.1（同一实体多次出现均需标注）；K8 §2.3 AFF。

---

### 样本 7

**修改**：删除 `abiotic` @125:132，label=`ABS`；删除 AFF(abiotic, ROS homeostasis)

**理由**：`abiotic` 是形容词（"abiotic and biotic stresses"），不是独立的胁迫实体名词。应标注的是 "abiotic stresses" 整体，但 "abiotic" 单独标注不符合 K1 §1.3 边界精确性原则。

> 依据：K1 §1.3；error_patterns §2.1（形容词不标为实体）。

---

### 样本 8

**修改**：新增 `sorghum` @14:21 CROP；`genetic diversity` @45:61 TRT；`sorghum` @189:196 CROP；HAS(sorghum, genetic diversity)

**理由**：原始数据完全空白。sorghum 是作物，genetic diversity（遗传多样性）是可量化的性状，应标注。

> 依据：K8 §1.3 TRT；K8 §1.5 CROP；K8 §2.1 HAS。

---

### 样本 9

**修改 1**：`PSII` @62:66 TRT→GENE；`PSI` @219:222 TRT→GENE；`PSII` @265:269 TRT→GENE

**理由**：PSI（光系统 I）和 PSII（光系统 II）是光合作用蛋白质复合体，属于 GENE 类别，而非可量化的农艺性状（TRT）。

> 依据：K8 §1.1 GENE；K7 §2.3（蛋白质复合体标为 GENE）；与 chunk_024 样本 7 的 PS I/PS II 标注保持一致。

**修改 2**：新增 `Roma` @143:147，label=`VAR`

**理由**：Roma 是高粱品种名，在原文 "decreased more in Roma than in M-81E" 中与 M-81E（已标注为 VAR）并列，漏标。

> 依据：K8 §1.5 VAR；error_patterns §3.6（并列实体补齐）。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `abscisic acid` @107:120 ✓
- `Linkage analysis` @0:16 ✓；`Association analysis` @158:178 ✓
- `ABA` @363:366 ✓
- `Shinanotsubuhime` @187:203 ✓；`Yuikogane` @235:244 ✓
- `Genome-wide association analysis` @0:32 ✓
- `Chr1_61095994` @23:36 ✓；`glutathione S-transferase` @177:201 ✓；`MYB-bHLH-WD40 complex` @305:327 ✓
- `Chalk5` @23:29 ✓
- `sorghum` @14:21 ✓；`genetic diversity` @45:61 ✓；`sorghum` @189:196 ✓
- `Roma` @143:147 ✓
