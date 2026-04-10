# chunk_028 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 32 处（新增实体 15 个、修改实体 1 处、删除实体 2 个、新增关系 14 条）

---

## 一、整体说明

本块涉及谷子、燕麦、蚕豆、大麦等作物的基因功能、胁迫响应、转录组分析和分子标记研究。原始标注存在以下系统性问题：
1. 胁迫因子被错误标注为 TRT（abiotic stress、waterlogging 重叠实体问题）
2. 分析方法漏标（GO、KEGG、Path analysis、Transcriptomic analysis、co-expression network）
3. 并列实体漏标（LEA、DHNs、HSPs；carbon fixation、proline synthesis）
4. 关键性状漏标（seed vigor、Na+ efflux、drought adaptation、genetic diversity）
5. 非实体词被错误标注为 CROP（drought-stressed faba bean leaves）

---

## 二、逐条修改说明

### 样本 0

**修改 1**：新增 `salt stress` @88:99，label=`ABS`；新增 `Na+ efflux` @163:173，label=`TRT`

**理由**：salt stress（盐胁迫）是非生物胁迫因子，属于 ABS。Na+ efflux（Na+ 外排）是可量化的离子转运性状，属于 TRT。原文明确描述 SiCBL5 过表达体具有更强的 Na+ 外排能力，漏标。

> 依据：K8 §1.8 ABS；K8 §1.3 TRT；error_patterns §3.6（并列性状补齐）。

**修改 2**：新增关系 AFF(SiCBL5@101, Na+ accumulation)；AFF(SiCBL5@101, Na+ efflux)；AFF(salt stress, salt tolerance)

**理由**：原文明确说明 SiCBL5 过表达体在盐胁迫下 Na+ 积累更低、Na+ 外排更强，应建立 GENE→TRT 的 AFF 关系。

> 依据：K8 §2.3 AFF；K2 §1.1（GENE→TRT）。

---

### 样本 1

**修改 1**：`abiotic stress` @161:175，TRT→ABS；删除 `drought-stressed faba bean leaves` @372:405 CROP

**理由**：abiotic stress（非生物胁迫）是胁迫因子，属于 ABS，不是可量化的农艺性状（TRT）。"drought-stressed faba bean leaves" 是描述性短语（干旱胁迫下的蚕豆叶片），不是作物名称，不应标为 CROP。

> 依据：K8 §1.8 ABS；K8 §1.5 CROP（需为作物名称）；K7 §2.4（描述性短语不标为实体）。

**修改 2**：新增 `GO` @16:18 BM；`KEGG` @25:29 BM；`LEA` @302:305 GENE；`DHNs` @307:311 GENE；`HSPs` @316:320 GENE；`faba bean` @388:397 CROP；`drought adaptation` @432:449 TRT

**理由**：GO（基因本体论分析）和 KEGG（代谢通路分析）是分析方法，属于 BM。LEA、DHNs、HSPs 是蛋白质/基因名称，在原文中并列出现，漏标。faba bean（蚕豆）是作物名称，漏标。drought adaptation（干旱适应性）是可量化的农艺性状，属于 TRT。

> 依据：K8 §1.4 BM；K8 §1.1 GENE；K8 §1.5 CROP；K8 §1.3 TRT；error_patterns §3.6（并列实体补齐）。

---

### 样本 2

**修改**：新增 `seed vigor` @20:30 TRT；新增 AFF(AsA priming, seed vigor)；AFF(45 degrees C, seed vigor)

**理由**：seed vigor（种子活力）是可量化的种子质量性状，属于 TRT。原文明确说明 AsA 引发提高了种子活力，45°C 老化处理影响种子活力，应建立相应 AFF 关系。

> 依据：K8 §1.3 TRT；K8 §2.3 AFF。

---

### 样本 3

**修改**：新增 `Path analysis` @115:128 BM

**理由**：Path analysis（通径分析）是统计分析方法，属于 BM。

> 依据：K8 §1.4 BM。

---

### 样本 4

**修改 1**：删除 `domestication` @174:187 TRT

**理由**：domestication（驯化）是育种历史过程，不是可量化的农艺性状，不应标为 TRT。

> 依据：K8 §1.3 TRT（需为可量化农艺性状）；K7 §2.4（过程描述不标为 TRT）。

**修改 2**：新增 `gene expression` @113:128 TRT

**理由**：gene expression（基因表达）是可量化的分子性状，属于 TRT。

> 依据：K8 §1.3 TRT。

---

### 样本 5

**修改**：新增 `co-expression network` @4:26 BM；`carbon fixation` @148:162 TRT；`proline synthesis` @248:264 TRT；新增关系 AFF(millet, drought stress)；HAS(millet, carbon fixation)；HAS(millet, proline synthesis)

**理由**：co-expression network（共表达网络）是分析方法，属于 BM。carbon fixation（碳固定）和 proline synthesis（脯氨酸合成）是可量化的代谢性状，属于 TRT，在原文中并列出现，漏标。

> 依据：K8 §1.4 BM；K8 §1.3 TRT；error_patterns §3.6（并列实体补齐）。

---

### 样本 6

**修改**：新增 `Transcriptomic analysis` @0:25 BM

**理由**：Transcriptomic analysis（转录组分析）是分析方法，属于 BM。

> 依据：K8 §1.4 BM。

---

### 样本 8

**修改**：新增 `genetic diversity` @22:38 TRT

**理由**：genetic diversity（遗传多样性）是可量化的种群遗传性状，属于 TRT。

> 依据：K8 §1.3 TRT。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `salt stress` @88:99 ✓；`Na+ efflux` @163:173 ✓
- `GO` @16:18 ✓；`KEGG` @25:29 ✓；`LEA` @302:305 ✓；`DHNs` @307:311 ✓；`HSPs` @316:320 ✓；`faba bean` @388:397 ✓；`drought adaptation` @432:449 ✓
- `seed vigor` @20:30 ✓
- `Path analysis` @115:128 ✓
- `gene expression` @113:128 ✓
- `co-expression network` @4:26 ✓；`carbon fixation` @148:162 ✓；`proline synthesis` @248:264 ✓
- `Transcriptomic analysis` @0:25 ✓
- `genetic diversity` @22:38 ✓
