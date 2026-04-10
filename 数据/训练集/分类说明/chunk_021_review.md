# chunk_021 分类说明（review.md）

**处理时间**：2026-04-10  
**样本范围**：chunk_021（10条）  
**对应完整标注文件**：`标注结果/chunk_021_annotated.md`

---

## 一、整体处理情况

| 项目 | 数值 |
|------|------|
| 样本总数 | 10 |
| 无需修改样本数 | 2（样本1、样本8） |
| 有修改样本数 | 8 |
| 新增实体数 | 12 |
| 修改标签/边界数 | 2 |
| 删除实体数 | 1 |
| 新增关系数 | 12 |

---

## 二、逐条修改说明

### 样本 0

**修改**：新增 `WGCNA` @120:125，label=`BM`

**理由**：WGCNA（Weighted Gene Co-expression Network Analysis，加权基因共表达网络分析）是遗传分析的技术路线，属于 K8 §1.4 BM（"育种、选择或遗传分析的技术路线与方法"）。原始数据未标注，属于漏标。

> 依据：K8 §1.4 BM 定义；K6 文献语料库中 "RNA-seq"、"GWAS" 均标为 BM，WGCNA 同类。

**保留说明**：`DEGs`（差异表达基因集合）不标为 GENE，依据 error_patterns §2.1（DEGs 是基因集合，非具体基因）。

---

### 样本 1

**无修改**。原始标注正确：`Mqtl5-2`、`Mqtl2-5`、`Mqtl1-2` 均为 QTL，各 TRT 正确，LOI 关系方向正确（K2 §2.2）。

---

### 样本 2

**无修改**。原始标注正确：QTL、TRT、GST 均正确；OCI 关系（性状发生于生育时期）方向正确（K8 §2.4）。

---

### 样本 3

**修改 1**：新增 `Tol` @0:3，label=`VAR`；新增 `Tol` @253:256，label=`VAR`

**理由**：原文 "Tol" 是品种名（耐热品种 Tol），与后文 "Sen"（敏感品种）对比出现，应标为 VAR。原始数据未标注，属于漏标。

> 依据：K8 §1.1 VAR；K6 文献语料库中品种名均标为 VAR。

**修改 2**：新增 `elevated temperatures` @290:311，label=`ABS`

**理由**：高温是非生物胁迫因子，属于 K8 §1.3 ABS（"由非生命环境因素引起的胁迫条件"）。原始数据未标注，属于漏标。

> 依据：K8 §1.3 ABS；K7 §2.6（"heat"、"cold" 等极端温度均为 ABS）。

**修改 3**：删除 `GENE` @419:423，label=`VAR`

**理由**：原文 "SnRK1 (GENE)" 中括号内的 "GENE" 是原文中的字面标注说明字符串，并非真实实体。将其标为 VAR 是错误的。应删除该实体。

> 依据：K1 §1.1（实体必须对应原文中真实的生物学概念）。

**修改 4**：新增关系 `AFF(heat shock@58:68, SnRK1@412:417)`

**理由**：原文 "suppression of SnRK1 via transcripts and metabolites" 在热胁迫语境下，热胁迫（heat shock）通过代谢物抑制 SnRK1 表达，属于 ABS→GENE 的 AFF 关系。该模式在训练集中存在（error_patterns §1.1，AFF: ABS→GENE 18次），保留。

> 依据：K8 §2.3 AFF；error_patterns §1.1。

---

### 样本 4

**修改**：新增 `ABA` @107:110，label=`ABS`；新增 `ABA` @213:216，label=`ABS`

**理由**：ABA（脱落酸，Abscisic acid）是植物激素，在胁迫响应语境中作为非生物胁迫信号分子，属于 K8 §1.3 ABS。原文 "hypersensitivities to ABA" 和 "ABA dependent signaling pathway" 中 ABA 均作为胁迫因子出现，应标为 ABS。

> 依据：K8 §1.3 ABS；K7 §2.6（化学胁迫因子如 NaCl、d-Mannitol 均标为 ABS，ABA 同理）。

---

### 样本 5

**修改**：`cultivated barley` @271:288，label 由 `VAR` 改为 `CROP`

**理由**："cultivated barley" 是大麦的栽培类型（物种/亚种名称），而非具体品种名，应标为 CROP。与 "Tibetan wild barley" 同为大麦类型对比，后者在原始数据中标为 VAR 存在争议，但 "cultivated barley" 更明显是物种类型描述。

> 依据：K8 §1.1 CROP（"杂粮作物的物种或类别名称"）；error_patterns §2.4（"sweet sorghum" 标为 CROP 同理）。

---

### 样本 6

**修改 1**：新增 `B. fusca` @40:48，label=`BIS`；新增 `C. partellus` @53:65，label=`BIS`

**理由**：*Busseola fusca*（非洲高粱茎螟）和 *Chilo partellus*（玉米螟）均为高粱的主要害虫，属于生物胁迫因子。原文 "QTLs for resistance to B. fusca and C. partellus" 明确指出这两种害虫是抗性研究对象，应标为 BIS。

> 依据：K8 §1.3 BIS（"由病原体、害虫或杂草等生物因素引起的胁迫类型"）；K7 §2.6（害虫标为 BIS）。

**修改 2**：`SNP` @150:153 → `SNP markers` @150:161，边界扩展

**理由**：原文 "4,955 SNP markers" 中 "SNP markers" 是完整的分子标记名称，"markers" 是标记类型描述词，与 "SNP" 共同构成完整实体。参考 K1 §2.3（"分子标记实体必须包含标记类型和具体的引物/位点编号"），应包含 "markers"。

> 依据：K1 §2.3；K8 §1.6 MRK。

**修改 3**：新增关系 `LOI(QTLs@17:21, B. fusca@40:48)` 和 `LOI(QTLs@17:21, C. partellus@53:65)`

**理由**：原文 "mapped QTLs for resistance to B. fusca and C. partellus" 明确表明 QTL 定位于对这两种害虫的抗性，属于 LOI 关系（K2 §2.2，QTL 定位于生物胁迫）。

> 依据：K2 §2.2；K8 §2.2 LOI。

---

### 样本 7

**修改 1**：新增 `Striga tolerance` @60:76，label=`TRT`

**理由**："Striga tolerance"（列当耐受性）是一个完整的抗性性状名称，整体应标为 TRT。原始数据仅标了 `Striga`（BIS），但 "Striga tolerance" 整体是性状，参考 K7 §2.1（"powdery mildew resistance" 整体标为 TRT）。两个实体（BIS 和 TRT）可以重叠共存，训练集中存在此类嵌套模式。

> 依据：K7 §2.1；K8 §1.3 TRT；K1 §3.1（嵌套实体）。

**修改 2**：新增 `leaves per plant` @159:175，label=`TRT`

**理由**："leaves per plant"（每株叶片数）是农艺性状，属于 TRT。原始数据未标注，属于漏标。

> 依据：K8 §1.3 TRT；K5 §3.2（高粱品种试验考察项目包含叶部性状）。

**修改 3**：新增 LOI 关系 8 条（SNPs 与各 TRT）

**理由**：原文 "Significant SNPs were found for plant height, panicle height, leaves per plant, foliar fresh grain weight, dry grain weight, and chlorophyll content" 明确表明这些 SNP 与各性状显著关联，应建立 LOI 关系（MRK→TRT，训练集高频非标准模式，error_patterns §1.1）。

> 依据：K8 §2.2 LOI；error_patterns §1.1。

---

### 样本 8

**无修改**。原始标注正确。

---

### 样本 9

**修改 1**：新增 `Rio` @122:125，label=`VAR`

**理由**：原文 "sweet sorghum cultivar 'Rio'" 中 "Rio" 是甜高粱品种名，应标为 VAR。原始数据未标注，属于漏标。

> 依据：K8 §1.1 VAR；K4 命名规范（品种名标为 VAR）。

**修改 2**：新增 `Brix` @174:178，label=`TRT`

**理由**：Brix（白利糖度）是衡量甜高粱糖分含量的性状指标，属于 TRT。原始数据未标注，属于漏标。

> 依据：K8 §1.3 TRT；K6 §1.8（"soluble solid content" 标为 TRT，Brix 同类）。

**修改 3**：新增 `flowering time` @202:216，label=`TRT`

**理由**："flowering time"（开花时间）是重要的农艺性状，属于 TRT。原始数据未标注，属于漏标。

> 依据：K8 §1.3 TRT；K6 §1.8（"flowering time" 是 TRT 典型示例）。

---

## 三、权威依据索引

| 依据 | 适用修改 |
|------|------|
| K8 §1.4 BM | 样本0 WGCNA |
| K8 §1.1 VAR | 样本3 Tol, 样本9 Rio |
| K8 §1.3 ABS | 样本3 elevated temperatures, 样本4 ABA |
| K8 §1.3 BIS | 样本6 B. fusca, C. partellus |
| K8 §1.3 TRT | 样本7 Striga tolerance, leaves per plant, 样本9 Brix, flowering time |
| K8 §1.1 CROP | 样本5 cultivated barley |
| K1 §2.3 MRK 边界 | 样本6 SNP markers |
| K1 §3.1 嵌套实体 | 样本7 Striga/Striga tolerance |
| K2 §2.2 LOI | 样本6 QTLs→BIS, 样本7 SNPs→TRT |
| K7 §2.1 TRT 整体标注 | 样本7 Striga tolerance |
| K7 §2.6 ABS/BIS 辨析 | 样本3 elevated temperatures, 样本4 ABA |
| error_patterns §1.1 AFF:ABS→GENE | 样本3 AFF(heat shock, SnRK1) |
| error_patterns §2.1 DEGs | 样本0 不标 DEGs |
| error_patterns §2.4 CROP/VAR | 样本5 cultivated barley |
