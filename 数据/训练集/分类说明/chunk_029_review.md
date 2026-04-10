# chunk_029 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 41 处（新增实体 22 个、删除实体 1 个、新增关系 17 条、修改关系 4 条）

---

## 一、整体说明

本块涉及高粱、大麦、荞麦、谷子等作物的产量性状、胁迫响应、QTL 定位和基因功能研究。原始标注存在以下系统性问题：
1. 并列性状大量漏标（plant size、biomass、leaf area、stomatal conductance 等）
2. 关系类型错误（QTL HAS TRT 应改为 QTL LOI TRT）
3. 分析方法漏标（Electrophoretic mobility shift assays、yeast one-hybrids、Bioinformatics analysis）
4. 描述性短语被错误标注为 CROP（salt-responsive Tartary buckwheat）
5. 关键基因漏标（SiARDP、SiLTP、Potassium transporter 8、monothiol glutaredoxin）

---

## 二、逐条修改说明

### 样本 0

**修改**：新增 `Grain yields` @0:12 TRT；`water shortage` @124:138 ABS；`plant size` @181:191 TRT；`biomass` @193:200 TRT；`leaf area` @202:211 TRT；`stomatal conductance` @232:252 TRT

**理由**：Grain yields（粮食产量）是核心农艺性状，属于 TRT。water shortage（水分亏缺）是干旱胁迫的具体表现形式，属于 ABS。plant size、biomass、leaf area、stomatal conductance 均是可量化的农艺/生理性状，属于 TRT，在原文中并列出现，漏标。

> 依据：K8 §1.3 TRT；K8 §1.8 ABS；error_patterns §3.6（并列实体补齐）。

---

### 样本 1

**修改**：新增 `yield` @68:73 TRT；修改 QTL HAS TRT → QTL LOI TRT（×4）

**理由**：yield（产量）是农艺性状，漏标。QTL 与性状的关系应使用 LOI（定位），而非 HAS（拥有）。HAS 关系用于 CROP/VAR 拥有某性状，QTL 是遗传位点，与性状的关系是"控制/定位"，应使用 LOI。

> 依据：K8 §2.5 LOI（QTL→TRT）；K8 §2.1 HAS（仅限 CROP/VAR→TRT）；K2 §1.3（QTL 关系规则）。

---

### 样本 2

**修改**：新增 `Potassium transporter 8` @0:24 GENE；`monothiol glutaredoxin` @29:52 GENE；`CC` @131:133 TRT；`RWC` @138:141 TRT

**理由**：Potassium transporter 8（钾转运体 8）和 monothiol glutaredoxin（单硫醇谷氧还蛋白）是基因/蛋白质名称，属于 GENE。CC（叶绿素含量）和 RWC（相对含水量）是可量化的生理性状，属于 TRT。原始标注完全为空，严重漏标。

> 依据：K8 §1.1 GENE；K8 §1.3 TRT。

---

### 样本 3

**修改**：新增 `cell wall function` @113:131 TRT；`GSH metabolism` @136:150 TRT；新增 AFF(Cd treatment, WRKY)；AFF(Cd stress, cell wall function/GSH metabolism)；HAS(Tartary buckwheat, Cd tolerance)

**理由**：cell wall function（细胞壁功能）和 GSH metabolism（谷胱甘肽代谢）是可量化的生理/生化性状，属于 TRT。原始关系漏标了 AFF(Cd treatment, WRKY)（与 MYB、ERF、bHLH 并列）。Tartary buckwheat 具有 Cd tolerance 性状，应建立 HAS 关系。

> 依据：K8 §1.3 TRT；K8 §2.3 AFF；K8 §2.1 HAS；error_patterns §3.6（并列关系补齐）。

---

### 样本 6

**修改**：新增 `Electrophoretic mobility shift assays` @0:39 BM；`yeast one-hybrids` @44:61 BM；`SiARDP` @96:102 GENE；`SiLTP` @116:121 GENE；新增 AFF(SiARDP, SiLTP)

**理由**：Electrophoretic mobility shift assays（电泳迁移率变动实验）和 yeast one-hybrids（酵母单杂交）是蛋白质-DNA 互作分析方法，属于 BM。SiARDP 是转录因子，SiLTP 是其靶基因，均属于 GENE，漏标。原文明确说明 SiARDP 结合 SiLTP 启动子，应建立 AFF 关系。

> 依据：K8 §1.4 BM；K8 §1.1 GENE；K8 §2.3 AFF。

---

### 样本 7

**修改**：新增 `genetic diversity` @13:29 TRT；`lipid peroxidation` @94:111 TRT；新增 HAS(foxtail millet, genetic diversity)

**理由**：genetic diversity（遗传多样性）是可量化的种群遗传性状，属于 TRT。lipid peroxidation（脂质过氧化）是可量化的生化性状，属于 TRT。

> 依据：K8 §1.3 TRT。

---

### 样本 8

**修改**：删除 `salt-responsive Tartary buckwheat` @41:74 CROP；新增 `Tartary buckwheat` @57:74 CROP；`Bioinformatics analysis` @148:171 BM；新增 AFF(FtIST1, salt tolerance)

**理由**："salt-responsive Tartary buckwheat" 是描述性短语，不是作物名称，不应标为 CROP。应提取其中的 "Tartary buckwheat"（荞麦）单独标注为 CROP。Bioinformatics analysis（生物信息学分析）是分析方法，属于 BM。FtIST1 与 salt tolerance 有功能关系，应建立 AFF。

> 依据：K8 §1.5 CROP；K8 §1.4 BM；K1 §1.3（描述性短语边界）；K7 §2.4。

---

### 样本 9

**修改**：新增 `yield` @286:291 TRT；新增 LOI(qSRN2-1, SRN)；LOI(qSL5-1, SL)

**理由**：yield（产量）是农艺性状，漏标。qSRN2-1 和 qSL5-1 分别是 SRN 和 SL 性状的 QTL，应建立 LOI 关系。

> 依据：K8 §1.3 TRT；K8 §2.5 LOI。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `Grain yields` @0:12 ✓；`water shortage` @124:138 ✓；`plant size` @181:191 ✓；`biomass` @193:200 ✓；`leaf area` @202:211 ✓；`stomatal conductance` @232:252 ✓
- `yield` @68:73 ✓
- `Potassium transporter 8` @0:24 ✓；`monothiol glutaredoxin` @29:52 ✓；`CC` @131:133 ✓；`RWC` @138:141 ✓
- `cell wall function` @113:131 ✓；`GSH metabolism` @136:150 ✓
- `Electrophoretic mobility shift assays` @0:39 ✓；`yeast one-hybrids` @44:61 ✓；`SiARDP` @96:102 ✓；`SiLTP` @116:121 ✓
- `genetic diversity` @13:29 ✓；`lipid peroxidation` @94:111 ✓
- `Tartary buckwheat` @57:74 ✓；`Bioinformatics analysis` @148:171 ✓
- `yield` @286:291 ✓
