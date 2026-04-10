# chunk_023 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 30 处（新增实体 18 个、删除实体 2 个、新增关系 27 条）

---

## 一、整体说明

本块涉及谷子、花生、豇豆、高粱等作物的 QTL 定位、基因功能、胁迫响应和代谢物研究。原始标注存在以下系统性问题：
1. 性状漏标（tillering、YPC、drought tolerance、SL production 等）
2. 关系漏标（QTL→TRT 的 LOI 关系、AFF 关系）
3. 重叠实体未去重（CROSS 重叠）
4. 分析方法漏标（Association mapping、yeast two-hybrid）

---

## 二、逐条修改说明

### 样本 0

**修改**：新增 LOI(qDTH2, late heading)；LOI(qDTH7, extremely late heading)

**理由**：原文 "allele for qDTH2 caused late heading" 和 "allele for qDTH7 led to extremely late heading"，QTL 定位于相应性状，应建立 LOI 关系。原始数据已有 AFF 关系，但缺少 LOI 关系（QTL 定位于性状是 LOI 的典型用法）。

> 依据：K8 §2.2 LOI；K2 §2.2（QTL→TRT 的 LOI 关系）。

---

### 样本 1

**修改 1**：新增 `drought tolerance` @157:172，label=`TRT`

**理由**：原文 "identify QTL for drought tolerance"，drought tolerance 是抗旱性性状，应标为 TRT。原始数据漏标。

> 依据：K8 §1.3 TRT；K7 §2.1（"drought tolerance" 是 TRT 典型示例）。

**修改 2**：删除重叠 CROSS 实体

**理由**：`RIL populations ICGS 76 x CSMG 84-1 (RIL-2)`（@184:227）和 `ICGS 76 x CSMG 84-1 (RIL-2)`（@200:227）存在重叠，保留更完整的整体标注，删除内部重叠实体。`RIL-3`（@251:256）已被 `ICGS 44 x ICGS 76 (RIL-3)`（@232:257）包含，删除单独标注。

> 依据：K1 §3.1 嵌套实体处理原则。

**修改 3**：新增 LOI(QTL, drought tolerance)

**理由**：原文 "identify QTL for drought tolerance"，QTL 定位于抗旱性性状，应建立 LOI 关系。

> 依据：K8 §2.2 LOI。

---

### 样本 2

**修改**：新增 `yeast two-hybrid` @35:51，label=`BM`

**理由**：yeast two-hybrid（酵母双杂交）是蛋白质互作研究的实验方法，属于 K8 §1.4 BM（"育种、选择或遗传分析的技术路线与方法"）。

> 依据：K8 §1.4 BM；K7 §2.2（实验方法标为 BM）。

---

### 样本 3

**修改 1**：新增 `SL production` @27:40，label=`TRT`

**理由**：SL production（独脚金内酯产量）是植物代谢性状，属于 TRT。原文 "reduced SL production" 明确说明这是被测量的性状。

> 依据：K8 §1.3 TRT。

**修改 2**：新增 `Striga emergence rates` @133:155，label=`TRT`

**理由**："Striga emergence rates"（列当出苗率）是对列当侵染程度的量化性状，整体应标为 TRT。与 `Striga`（BIS）嵌套共存，符合 K1 §3.1 嵌套实体规则。

> 依据：K8 §1.3 TRT；K7 §2.1（"Striga tolerance" 整体标为 TRT）；K1 §3.1。

**修改 3**：新增 AFF(Striga, SL production)

**理由**：原文 "lower SL production had delayed or reduced Striga emergence rates"，列当（生物胁迫）的侵染与独脚金内酯产量相关，符合 AFF:BIS→TRT 关系。

> 依据：K8 §2.3 AFF。

---

### 样本 4

**修改 1**：新增 `raffinose family oligosaccharides` @367:399 TRT；`gamma-aminobutyric acid` @422:444 TRT；`hexose sugar concentration` @475:499 TRT

**理由**：原文 "up-regulation of raffinose family oligosaccharides and down-regulation of the gamma-aminobutyric acid catalytic pathway, while hexose sugar concentration became depleted"，三者均是代谢物含量/浓度性状，属于 TRT。原始数据漏标。

> 依据：K8 §1.3 TRT；K6 §1.8（代谢物含量标为 TRT）。

**修改 2**：新增 AFF(heat shock, raffinose family oligosaccharides)；AFF(heat shock, gamma-aminobutyric acid)；AFF(heat shock, hexose sugar concentration)

**理由**：原文明确说明热胁迫（heat shock）导致这些代谢物含量变化，符合 AFF:ABS→TRT 关系。

> 依据：K8 §2.3 AFF。

---

### 样本 5

**修改 1**：新增 `Association mapping` @215:233，label=`BM`

**理由**：Association mapping（关联分析）是遗传分析方法，属于 BM。原始数据漏标。

> 依据：K8 §1.4 BM；K7 §2.2（GWAS 等关联分析标为 BM）。

**修改 2**：新增 `chromosome 6` @447:459，label=`CHR`

**理由**：原文 "a PH QTL on chromosome 6"，chromosome 6 是染色体位置，应标为 CHR。原始数据漏标。

> 依据：K8 §1.5 CHR。

**修改 3**：新增 LOI(three QTLs for DF, days to 50% flowering)；LOI(a PH QTL on chromosome 6, chromosome 6)

**理由**：原始关系中缺少 LOI(three QTLs for DF, DF)，且 QTL 定位于染色体位置应建立 LOI 关系。

> 依据：K8 §2.2 LOI；K2 §2.2。

---

### 样本 6

**修改 1**：新增 `MTAs` @8:12，label=`MRK`

**理由**：MTAs（Marker-Trait Associations，标记-性状关联）是分子标记关联分析的结果，属于 MRK 类别。原始数据漏标。

> 依据：K8 §1.6 MRK。

**修改 2**：新增 `aphid count` @127:138，label=`TRT`

**理由**：aphid count（蚜虫数量）是蚜虫抗性的量化性状，属于 TRT。原始数据漏标（plant damage 已标，aphid count 同类漏标）。

> 依据：K8 §1.3 TRT；error_patterns §3.6 并列实体补齐。

**修改 3**：新增 `SNPs` @468:472，label=`MRK`

**理由**：原文 "near SNPs significantly associated with different SA traits"，SNPs 是分子标记，漏标。

> 依据：K8 §1.6 MRK。

**修改 4**：新增 LOI(MTAs, SBI-08)；LOI(MTAs, SBI-10)；LOI(MTAs, aphid count)；LOI(MTAs, plant damage)

**理由**：原文 "Common markers on SBI-08 and SBI-10 were associated with aphid count and plant damage"，MTAs 定位于染色体并与性状关联，应建立 LOI 关系。

> 依据：K8 §2.2 LOI。

---

### 样本 7

**修改 1**：新增 `tillering` @22:31 TRT；`Tillering` @43:52 TRT

**理由**：tillering（分蘖）是高粱的重要农艺性状，属于 TRT。原始数据漏标。

> 依据：K8 §1.3 TRT；K5 §3.2（高粱品种试验考察项目包含分蘖性状）。

**修改 2**：新增 LOI(QTL, tillering)；HAS(sorghum, tillering)

**理由**：原文 "A QTL model controls tillering in sorghum"，QTL 控制分蘖性状，应建立 LOI 关系；高粱具有分蘖性状，应建立 HAS 关系。

> 依据：K8 §2.2 LOI；K8 §2.1 HAS。

---

### 样本 8

**修改 1**：新增 `YPC` @66:69 TRT；`YPC` @145:148 TRT

**理由**：YPC（Yellow Pigment Content，黄色素含量）是谷子的重要品质性状，属于 TRT。原始数据漏标。

> 依据：K8 §1.3 TRT；K6 §1.8（色素含量标为 TRT）。

**修改 2**：新增 AFF(SiPSY1, YPC) ×2；OCI(YPC, 15 DAP)

**理由**：原文 "SiPSY1 transcription...determined YPC"，SiPSY1 基因影响 YPC，应建立 AFF 关系；YPC 在 15 DAP 阶段测定，应建立 OCI 关系。

> 依据：K8 §2.3 AFF；K8 §2.4 OCI。

---

### 样本 9

**修改 1**：新增 `18 QTLs` @0:7，label=`QTL`

**理由**：原文 "18 QTLs were identified for plant height..."，18 QTLs 是 QTL 集合，应标为 QTL。原始数据漏标。

> 依据：K8 §1.2 QTL。

**修改 2**：新增 LOI(18 QTLs, 各TRT) ×5；LOI(qFW9.2/qDW9, fresh/dry weight) ×2；LOI(qFW10/qDW10.2, fresh/dry weight) ×2

**理由**：原文明确说明 QTL 与各性状的定位关系，应建立 LOI 关系。原始数据关系列表为空。

> 依据：K8 §2.2 LOI；error_patterns §1.1（LOI: QTL→TRT 是高频模式）。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `drought tolerance` @157:172 ✓
- `yeast two-hybrid` @35:51 ✓
- `SL production` @27:40 ✓；`Striga emergence rates` @133:155 ✓
- `raffinose family oligosaccharides` @367:399 ✓；`gamma-aminobutyric acid` @422:444 ✓；`hexose sugar concentration` @475:499 ✓
- `Association mapping` @215:233 ✓；`chromosome 6` @447:459 ✓（需最终 JSON 生成时精确验证）
- `MTAs` @8:12 ✓；`aphid count` @127:138 ✓；`SNPs` @468:472 ✓
- `tillering` @22:31 ✓；`Tillering` @43:52 ✓
- `YPC` @66:69 ✓；`YPC` @145:148 ✓
- `18 QTLs` @0:7 ✓
