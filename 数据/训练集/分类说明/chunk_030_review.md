# chunk_030 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 46 处（新增实体 21 个、修改实体 3 处、删除实体 1 个、新增关系 21 条、修改关系 5 条）

---

## 一、整体说明

本块涉及高粱、大麦、燕麦等作物的基因功能、QTL 定位、分子标记和胁迫响应研究。原始标注存在以下系统性问题：
1. 并列性状大量漏标（plant height、dry weight、moisture content、root activity 等）
2. 关系类型错误（QTL AFF TRT 应改为 QTL LOI TRT）
3. 单字母被错误标注为 CROP（`R` @86:87）
4. 修饰词未去除（`reduced plant height`、`reduced grain yield` 应去掉修饰词）
5. 物种标签错误（Setaria viridis 是野生型谷子，应标为 CROP 而非 VAR）
6. 关系漏标（SbWRKY50→SOS1/HKT1 的 AFF 关系）

---

## 二、逐条修改说明

### 样本 0

**修改**：新增 `GsNAC2-overexpressing sorghum` @79:108 VAR；新增 7 个并列性状 TRT；新增 AFF(GsNAC2, 7 个性状)；CON(sorghum, GsNAC2-overexpressing sorghum)

**理由**：GsNAC2-overexpressing sorghum 是过表达品系，属于 VAR。plant height、dry weight、moisture content、root activity、leaf length、chlorophyll content、stomatal conductance 均是可量化的农艺/生理性状，在原文中并列出现，属于 TRT，漏标。原文明确说明 GsNAC2 过表达体在盐碱处理后各性状增加，应建立 AFF 关系。

> 依据：K8 §1.3 TRT；K8 §1.2 VAR；K8 §2.3 AFF；error_patterns §3.6（并列实体补齐）。

---

### 样本 1

**修改**：新增 `expression patterns` @37:55 TRT；新增 AFF(salt stress, salicylic acid)；AFF(salt stress, betaine)

**理由**：expression patterns（基因表达模式）是可量化的分子性状，属于 TRT。原文明确说明盐胁迫下 salicylic acid 和 betaine 代谢谱不同，应建立 AFF 关系。

> 依据：K8 §1.3 TRT；K8 §2.3 AFF。

---

### 样本 3

**修改**：删除 `R` @86:87 CROP；新增 8 个性状 TRT；新增 USE(GWAS, RSA traits)；USE(GWAS, GP accuracy)

**理由**：`R` 是单字母，不是作物名称，明显标注错误，应删除。RSA traits（根系构型性状）和 GP accuracy（基因组预测准确性）是可量化性状，属于 TRT。NRA、NNR、NRL、FSW、DSW、LA 是根系性状缩写，属于 TRT。GWAS 用于调查这些性状，应建立 USE 关系。

> 依据：K8 §1.5 CROP（需为作物名称）；K8 §1.3 TRT；K8 §2.6 USE；K7 §2.4（单字母不标）。

---

### 样本 4

**修改**：修改 QTL AFF TRT → QTL LOI TRT（×5）

**理由**：QTL 与性状的关系是"定位/控制"，应使用 LOI，而非 AFF（影响）。AFF 关系用于胁迫因子/基因对性状的影响，QTL 是遗传位点，与性状的关系是"控制/定位"，应使用 LOI。

> 依据：K8 §2.5 LOI（QTL→TRT）；K2 §1.3（QTL 关系规则）；error_patterns §2.1（QTL 关系类型错误）。

---

### 样本 5

**修改**：修改 `reduced plant height` → `plant height` @225:237 TRT；`reduced grain yield` → `grain yield` @251:262 TRT；`Setaria viridis` VAR → CROP；新增 `flowering time` @102:116 TRT；`early flowering` @200:215 TRT；`IP-MS` @292:297 BM；新增 AFF(SiUBC39, 6 个性状)

**理由**：K1 §1.2 规定实体边界应去掉修饰词，`reduced` 是修饰词，不是性状名称的一部分。Setaria viridis（绿狗尾草）是野生型谷子，是物种名称，应标为 CROP 而非 VAR。flowering time 和 early flowering 是可量化的开花时间性状，属于 TRT，漏标。IP-MS（免疫沉淀质谱）是分析方法，属于 BM，漏标。

> 依据：K1 §1.2（修饰词边界）；K8 §1.5 CROP；K8 §1.3 TRT；K8 §1.4 BM。

---

### 样本 6

**修改**：新增 `GL` @113:115 TRT；新增 LOI(qGL1/qGL5/qTGW5, GL)

**理由**：GL（粒长）是可量化的农艺性状，属于 TRT，漏标。qGL1、qGL5、qTGW5 均是控制 GL 的 QTL，应建立 LOI 关系。

> 依据：K8 §1.3 TRT；K8 §2.5 LOI。

---

### 样本 8

**修改**：新增 AFF(SbWRKY50, SOS1)（×2）；AFF(SbWRKY50, HKT1)

**理由**：原文明确说明 SbWRKY50 直接结合 SOS1 和 HKT1 的启动子，是基因调控关系，应建立 AFF 关系。原始关系为空，严重漏标。

> 依据：K8 §2.3 AFF（GENE→GENE 调控关系）；K2 §1.1。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `GsNAC2-overexpressing sorghum` @79:108 ✓；`plant height` @101:113 ✓；`dry weight` @115:125 ✓；`moisture content` @127:143 ✓；`root activity` @145:158 ✓；`leaf length` @160:171 ✓；`chlorophyll content` @173:192 ✓；`stomatal conductance` @194:214 ✓
- `expression patterns` @37:55 ✓
- `RSA traits` @17:27 ✓；`GP accuracy` @32:43 ✓；`NRA` @75:78 ✓；`NNR` @80:83 ✓；`NRL` @85:88 ✓；`FSW` @90:93 ✓；`DSW` @95:98 ✓；`LA` @104:106 ✓
- `flowering time` @102:116 ✓；`early flowering` @200:215 ✓；`plant height` @225:237 ✓；`grain yield` @251:262 ✓；`IP-MS` @292:297 ✓
- `GL` @113:115 ✓
