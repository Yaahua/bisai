# chunk_027 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 24 处（新增实体 10 个、删除实体 2 个、新增关系 9 条、修改关系 4 条、删除关系 1 条）

---

## 一、整体说明

本块涉及小麦、高粱、谷子、绿豆等作物的抗病性、胁迫响应、QTL 定位和分子标记研究。原始标注存在以下系统性问题：
1. 关系类型错误（HAS 用于 GENE→TRT，应改为 AFF）
2. 信号通路被错误标注为 TRT（jasmonic acid signal transduction pathway）
3. 关系方向错误（品种性状关系混淆）
4. 分析方法漏标（Genetic analysis、QTL analysis）

---

## 二、逐条修改说明

### 样本 0

**修改 1**：新增 `resistance` @22:32，label=`TRT`；新增 HAS(LCR4, resistance)

**理由**：原文 "LCR4 exhibited robust resistance against stripe rust infection" 明确表明 LCR4 具有抗条锈病性状，resistance（抗性）是可量化的农艺性状，属于 TRT。应建立 HAS(LCR4, resistance) 关系。

> 依据：K8 §1.3 TRT；K8 §2.1 HAS（VAR→TRT）。

**修改 2**：新增 `Genetic analysis` @218:234，label=`BM`；修改 AFF(2RL chromosome segment, stripe rust infection) → AFF(2RL chromosome segment, resistance)

**理由**：Genetic analysis（遗传分析）是分析方法，属于 BM。2RL 染色体片段负责抗性，应建立 AFF(CHR, TRT) 关系，而非 AFF(CHR, BIS)。

> 依据：K8 §1.4 BM；K2 §1.2（CHR 可 AFF TRT）。

---

### 样本 2

**修改 1**：新增 `ROS scavenging system` @56:77，label=`TRT`；删除 `jasmonic acid (JA) signal transduction pathway` @249:295 TRT；新增 `jasmonic acid` @249:261 ABS

**理由**：ROS scavenging system（活性氧清除系统）是可量化的生理响应性状，属于 TRT。jasmonic acid signal transduction pathway（茉莉酸信号转导通路）是生物学过程，不是农艺性状，不应标为 TRT。jasmonic acid（茉莉酸）是植物胁迫信号分子，属于 ABS。

> 依据：K8 §1.3 TRT；K8 §1.8 ABS；K7 §2.6（信号通路不标为 TRT）。

---

### 样本 3

**修改**：HAS(AtOAT, abiotic tolerance) → AFF；HAS(AtOAT, proline biosynthesis) → AFF；新增 AFF(AtOAT, proline biosynthesis-associated genes)；AFF(AtOAT, proline catabolic gene)

**理由**：HAS 关系用于 CROP/VAR→TRT（作物/品种拥有某性状），GENE→TRT 应使用 AFF（基因影响性状）。AtOAT 是基因，不是作物或品种，应使用 AFF。原文明确说明 AtOAT 通过上调/下调基因来修饰脯氨酸合成，应建立 GENE→GENE 的 AFF 关系。

> 依据：K2 §1.1 AFF（GENE→TRT）；K8 §2.1 HAS（仅限 CROP/VAR→TRT）。

---

### 样本 4

**修改 1**：新增 `QTL analysis` @122:134，label=`BM`

**理由**：QTL analysis（QTL 分析）是遗传分析方法，属于 BM。

> 依据：K8 §1.4 BM。

**修改 2**：删除 HAS(Xinliang52, high juice yielding)

**理由**：原文明确说明 Xinliang52（XL52）是 "low juice yielding"（低汁液产量）品种，W455 是 "high juice yielding" 品种。原始标注错误地将 Xinliang52 与 high juice yielding 建立了 HAS 关系，语义错误，应删除。

> 依据：K2 §1.1 HAS（语义准确性）；原文语义分析。

---

### 样本 5

**修改**：新增 `genetic diversity` @4:20 TRT；`oat` @117:120 CROP；新增 HAS(hulless oat, genetic diversity)

**理由**：genetic diversity（遗传多样性）是可量化的种群遗传性状，属于 TRT。oat 是作物名称，漏标。

> 依据：K8 §1.3 TRT；K8 §1.5 CROP。

---

### 样本 7

**修改**：新增 `stalk juice sugar contents` @180:205 TRT；新增 HAS(maintainer lines/CMS, stalk juice sugar contents)

**理由**：stalk juice sugar contents（茎汁液糖含量）是可量化的农艺性状，属于 TRT，与 stalk juice 并列，漏标。

> 依据：K8 §1.3 TRT；error_patterns §3.6（并列实体补齐）。

---

### 样本 9

**修改**：新增 `genetic diversity` @93:109 TRT；新增 HAS(mung bean, genetic diversity)

**理由**：genetic diversity（遗传多样性）是可量化的性状，属于 TRT，漏标。

> 依据：K8 §1.3 TRT。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `resistance` @22:32 ✓；`Genetic analysis` @218:234 ✓
- `ROS scavenging system` @56:77 ✓；`jasmonic acid` @249:261 ✓
- `QTL analysis` @122:134 ✓
- `genetic diversity` @4:20 ✓；`oat` @117:120 ✓
- `stalk juice sugar contents` @180:205 ✓
- `genetic diversity` @93:109 ✓
