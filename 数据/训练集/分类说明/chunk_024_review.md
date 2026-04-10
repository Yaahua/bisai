# chunk_024 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 25 处（新增实体 10 个、修改边界 3 处、修改标签 3 处、删除实体 4 个、新增关系 5 条、修改关系 3 条）

---

## 一、整体说明

本块涉及谷子、高粱、豇豆、藜麦、稷子、羊草等作物的 GWAS 分析、QTL 定位、基因功能和胁迫耐受性研究。原始标注存在以下系统性问题：
1. 实体边界不完整（括号缺失、描述词过多或过少）
2. 标签错误（细胞学现象标为 TRT；蛋白质复合体标为 TRT）
3. 关系方向错误（AFF tail 为 CROP 而非 TRT）
4. 性状漏标（water stress tolerance、flowering time 等）

---

## 二、逐条修改说明

### 样本 0

**修改 1**：`genome-wide association study (GWAS` @2:37 → @2:38（补全右括号）

**理由**：原始标注边界缺少右括号，导致实体文本不完整。正确边界应为 @2:38，text[2:38]="genome-wide association study (GWAS)"。

> 依据：K1 §1.2 括号完整性原则。

**修改 2**：新增 `10 K SNPs` @115:124，label=`MRK`

**理由**：原文 "using 10 K SNPs"，10 K SNPs 是用于 GWAS 的分子标记集合，应标为 MRK。原始数据漏标。

> 依据：K8 §1.6 MRK。

---

### 样本 1

**修改**：删除 `Quadrivalents` @89:102 TRT；`anaphase I and II laggards` @104:130 TRT；`autotetraploids` @179:194 CROSS

**理由**：
- Quadrivalents（四价体）和 anaphase I and II laggards（后期 I/II 落后染色体）是细胞学现象描述，不是可量化的农艺性状，不符合 TRT 定义（K8 §1.3 TRT：农艺性状、品质性状、抗性性状等可量化表型）。
- autotetraploids（同源四倍体）是倍性类型描述，不是具体杂交组合，不符合 CROSS 定义（K8 §1.7 CROSS：具体杂交组合或后代群体）。

> 依据：K8 §1.3 TRT；K8 §1.7 CROSS；K7 §2.4（细胞学现象不标为 TRT）。

---

### 样本 2

**修改 1**：新增 `alkalinity` @68:78，label=`ABS`

**理由**：原文 "including cold, salinity, alkalinity and drought"，alkalinity（碱胁迫）与 cold、salinity、drought 并列，均是非生物胁迫，应标为 ABS。原始数据漏标 alkalinity。

> 依据：K8 §1.8 ABS；error_patterns §3.6（并列实体补齐）。

**修改 2**：新增 `sheepgrass` @174:184，label=`CROP`

**理由**：sheepgrass 第二次出现，应标为 CROP。原始数据仅标注了第一次出现（@0:10）。

> 依据：K1 §2.1（同一实体多次出现均需标注）。

**修改 3**：新增 `water stress tolerance` @183:205，label=`TRT`

**理由**：原文 "sheepgrass water stress tolerance at the molecular level"，water stress tolerance（水分胁迫耐受性）是可量化的耐逆性状，应标为 TRT。

> 依据：K8 §1.3 TRT；K7 §2.1（"drought tolerance" 类性状标为 TRT）。

**修改 4**：新增 HAS(Sheepgrass, water stress tolerance)

**理由**：羊草具有耐水分胁迫的性状，应建立 HAS 关系。

> 依据：K8 §2.1 HAS。

---

### 样本 3

**修改 1**：新增 `MAPK signaling` @107:121，label=`GENE`

**理由**：MAPK signaling（MAPK 信号通路）是基因调控网络，属于 GENE 类别（信号通路相关基因集合）。

> 依据：K8 §1.1 GENE；K7 §2.2（信号通路标为 GENE）。

**修改 2**：新增 LOI(QTLs, plant height)

**理由**：原文 "Three QTLs...for plant height were obtained"，QTL 定位于株高性状，应建立 LOI 关系。原始关系中只有 LOI(QTLs, chromosomes I and IX)，缺少 LOI(QTLs, plant height)。

> 依据：K8 §2.2 LOI；K2 §2.2（QTL→TRT 的 LOI 关系）。

---

### 样本 4

**修改**：新增 `Cluster analysis` @0:16，label=`BM`

**理由**：Cluster analysis（聚类分析）是遗传多样性分析方法，属于 BM。

> 依据：K8 §1.4 BM；K7 §2.2（遗传分析方法标为 BM）。

---

### 样本 5

**修改 1**：`C2H2-type` @13:22 → `C2H2-type zinc finger protein transcription factor` @13:62

**理由**：原始标注 `C2H2-type` 仅标注了结构类型描述词，边界过窄。完整的转录因子名称应为 `C2H2-type zinc finger protein transcription factor`，整体作为 GENE 标注。

> 依据：K1 §1.1 最大共识原则；K8 §1.1 GENE。

**修改 2**：新增 `quinoa` @101:107，label=`CROP`

**理由**：quinoa 第二次出现（"from the quinoa genome database"），应标为 CROP。原始数据仅标注了第一次出现（@6:12）。

> 依据：K1 §2.1（同一实体多次出现均需标注）。

---

### 样本 6

**无修改**。所有实体和关系均正确，保留原始标注。

---

### 样本 7

**修改 1**：新增 `Bioinformatics analysis` @0:22，label=`BM`；`proteome` @111:119，label=`BM`

**理由**：Bioinformatics analysis（生物信息学分析）和 proteome（蛋白质组学）均是分析方法，属于 BM。原始数据漏标。

> 依据：K8 §1.4 BM。

**修改 2**：`photosynthetic characteristics in maize leaves` @186:232 → `photosynthetic characteristics` @186:212

**理由**：原始边界包含 "in maize leaves" 定语，导致边界过宽。性状实体应仅包含性状名称本身，不包含定语修饰。

> 依据：K1 §1.3 边界精确性原则。

**修改 3**：`PS I` TRT→GENE；`PS II` TRT→GENE；`cytochrome b6f complex` TRT→GENE

**理由**：PS I（光系统 I）、PS II（光系统 II）和 cytochrome b6f complex（细胞色素 b6f 复合体）均是蛋白质复合体，属于 GENE 类别，而非可量化的农艺性状（TRT）。

> 依据：K8 §1.1 GENE；K7 §2.3（蛋白质复合体标为 GENE）。

---

### 样本 8

**修改 1**：新增 `flowering time` @226:240，label=`TRT`

**理由**：原文 "six genes involved in photoperiodic control of flowering time"，flowering time（开花时间）是重要农艺性状，应标为 TRT。

> 依据：K8 §1.3 TRT。

**修改 2**：新增 LOI(SNPs, flowering time)

**理由**：原文说明 SNPs 位于参与光周期控制开花时间的基因中，SNPs 与 flowering time 性状关联，应建立 LOI 关系。

> 依据：K8 §2.2 LOI。

---

### 样本 9

**修改 1**：新增 `tolerance to drought stress` @76:101，label=`TRT`

**理由**：原文 "nutritional qualities and tolerance to drought stress and soil infertility"，tolerance to drought stress（抗旱耐受性）是性状，应标为 TRT。

> 依据：K8 §1.3 TRT；K7 §2.1。

**修改 2**：删除 AFF(drought stress, Proso millet) 和 AFF(soil infertility, Proso millet)；新增 HAS(Proso millet, tolerance to drought stress)；AFF(drought stress, tolerance to drought stress)

**理由**：原始关系 AFF(ABS, CROP) 方向错误，AFF 的 tail 必须为 TRT（K2 §2.3）。正确关系应为：CROP HAS TRT（品种具有性状）；ABS AFF TRT（胁迫影响性状）。

> 依据：K2 §2.3 AFF 方向规则；K8 §2.1 HAS；K8 §2.3 AFF。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `genome-wide association study (GWAS)` @2:38 ✓
- `10 K SNPs` @115:124 ✓
- `alkalinity` @68:78 ✓
- `sheepgrass` @174:184 ✓
- `water stress tolerance` @183:205 ✓
- `MAPK signaling` @107:121 ✓
- `Cluster analysis` @0:16 ✓
- `C2H2-type zinc finger protein transcription factor` @13:62 ✓
- `quinoa` @101:107 ✓
- `Bioinformatics analysis` @0:22 ✓；`proteome` @111:119 ✓
- `photosynthetic characteristics` @186:212 ✓
- `flowering time` @226:240 ✓
- `tolerance to drought stress` @76:101 ✓
