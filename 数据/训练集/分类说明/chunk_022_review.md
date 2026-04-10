# chunk_022 分类说明 (review.md)

**处理时间**：2026-04-10
**样本数**：10 条
**修改总数**：共 22 处（新增实体 16 个、修改标签/边界 5 处、删除实体 4 个、新增关系 18 条、删除关系 2 条）

---

## 一、整体说明

本块涉及燕麦、大豆、高粱等作物的 QTL 定位、基因功能、胁迫响应和育种材料描述。原始标注存在以下系统性问题：
1. 实体边界包含描述词（VrKNAT7 sequence）
2. 品种名误标为基因（ACC41、KPS2）
3. 实验现象/材料误标为分子标记（primer sets、fragments）
4. 并列性状漏标（flowering、leaf area、yields）
5. 关系漏标（QTL→TRT 的 LOI 关系、AFF/HAS 关系）

---

## 二、逐条修改说明

### 样本 0

**修改**：新增 `PCR-based markers` @4:22，label=`MRK`

**理由**：原文 "Six PCR-based markers were developed"，PCR-based markers 是基于 PCR 的分子标记，属于 K8 §1.6 MRK（"用于定位或选择的 DNA 序列多态性标记"）。原始数据未标注，属于漏标。

> 依据：K8 §1.6 MRK；K1 §2.3 分子标记边界规则。

---

### 样本 1

**修改 1**：`VrKNAT7 sequence` @264:280 → `VrKNAT7` @264:271，边界缩减

**理由**："sequence" 是描述词，不属于基因名称本身。依据 K1 §1.1 最大共识原则，"sequence" 不是基因名称的必要组成部分，应从实体边界中排除。

> 依据：K1 §1.1；error_patterns §2.2（描述词不包含在实体内）。

**修改 2**：`ACC41` @299:304 GENE→VAR；`KPS2` @309:313 GENE→VAR

**理由**：ACC41 和 KPS2 是豇豆品种名称（Accession 编号），不是基因名称。原文 "VrKNAT7 sequence alignment between ACC41 and KPS2" 中两者是被比较的材料/品种，应标为 VAR。

> 依据：K8 §1.1 VAR；K4 命名规范（品种代号标为 VAR）。

**修改 3**：删除 `KNOX II` @247:254 GENE

**理由**：KNOX II 是蛋白质结构域家族名称（KNOTTED-like homeobox protein family II），不是具体基因名称，不应标为 GENE。依据 K8 §1.2 GENE（"必须包含完整的字母和数字编号"），KNOX II 是蛋白质家族类别名，不符合 GENE 定义。

> 依据：K8 §1.2 GENE；error_patterns §2.3。

---

### 样本 2

**修改 1**：新增 `F-3 lines` @88:97，label=`CROSS`

**理由**：F-3 lines 是第三代自交系，属于杂交后代群体，应标为 CROSS。依据 K8 §1.1 CROSS（"用于构建作图群体或育种的父本/母本材料，及其杂交组合或衍生群体"）。

> 依据：K8 §1.1 CROSS；K7 §2.3（F-3 lines 同 F-2 population，标为 CROSS）。

**修改 2**：`BSR` @120:123 ABS→BIS

**理由**：BSR（Brown Stem Rot，大豆茎褐腐病）是由真菌引起的病害，属于生物胁迫，应标为 BIS，不是非生物胁迫 ABS。

> 依据：K8 §1.3 BIS；K7 §2.1（病害标为 BIS）。

**修改 3**：删除 `BSR` @183:186 BIS（被 BM 包含）

**理由**：`BSR inoculation tests`（@183:204）已整体标为 BM，其中包含 BSR。重复标注同一文本位置会造成重叠实体冲突。保留 BM 整体标注，删除内部的 BIS 单独标注。

> 依据：K1 §3.1 嵌套实体处理原则。

**修改 4**：删除 `primer sets` @230:241 MRK；删除 `fragments` @253:262 MRK

**理由**：`primer sets` 是实验材料（引物组），不是分子标记本身；`fragments` 是电泳条带（实验现象），不是分子标记。依据 error_patterns §2.1（"779 bp band" 不标为 MRK，实验现象不是分子标记）。

> 依据：error_patterns §2.1；K8 §1.6 MRK（必须是 DNA 序列多态性标记，不是实验材料或现象）。

---

### 样本 3

**修改**：新增 `phenotypic changes` @157:174，label=`TRT`

**理由**：原文 "Edited lines showed phenotypic changes compared to wild-type plants"，"phenotypic changes" 是表型变化，属于性状描述，应标为 TRT。

> 依据：K8 §1.3 TRT。

---

### 样本 4

**修改 1**：新增 `Abiotic stress` @0:13 ABS；新增 `abiotic stresses` @100:116 ABS

**理由**：原文 "Abiotic stress impacts sorghum growth and yield" 和 "responds to abiotic stresses"，均是非生物胁迫的泛指，属于 ABS。原始数据漏标。

> 依据：K8 §1.3 ABS。

**修改 2**：新增 `growth` @31:37 TRT；新增 `yield` @42:47 TRT

**理由**：原文 "Abiotic stress impacts sorghum growth and yield"，growth 和 yield 是高粱的农艺性状，应标为 TRT。原始数据漏标。

> 依据：K8 §1.3 TRT。

**修改 3**：新增 `SbPLD` @133:138 GENE；新增 `sorghum` @153:160 CROP

**理由**：SbPLD 是高粱磷脂酶 D 基因家族名称，应标为 GENE；第二次出现的 sorghum 漏标为 CROP。

> 依据：K8 §1.2 GENE；K8 §1.1 CROP。

**修改 4**：新增关系 AFF(Abiotic stress, growth)；AFF(Abiotic stress, yield)；HAS(sorghum, growth)；HAS(sorghum, yield)

**理由**：原文明确说明非生物胁迫影响高粱的生长和产量，符合 AFF:ABS→TRT 关系；高粱具有这些性状，符合 HAS:CROP→TRT 关系。

> 依据：K8 §2.3 AFF；K8 §2.1 HAS。

---

### 样本 5

**修改 1**：新增 `yields` @16:22，label=`TRT`

**理由**：原文 "Qing1 and Long4 yields were 27.25% and 21.42% higher"，yields 是产量性状，应标为 TRT。原始数据漏标。

> 依据：K8 §1.3 TRT。

**修改 2**：新增 HAS(Qing1, yields)；HAS(Long4, yields)；HAS(Long4, CAT)

**理由**：原始关系中 Long4 缺少 HAS(Long4, CAT)，且两个品种均具有 yields 性状，需补充。依据 error_patterns §3.6，并列实体补齐时必须同步补齐成组关系。

> 依据：K8 §2.1 HAS；error_patterns §3.6。

---

### 样本 6

**修改 1**：新增 `flowering` @75:84 TRT；新增 `leaf area` @95:104 TRT

**理由**：原文 "38 QTLs controlling variation in height, flowering, biomass, leaf area, greenness and stomatal density"，flowering 和 leaf area 是农艺性状，与 height、biomass 并列，原始数据漏标。

> 依据：K8 §1.3 TRT；error_patterns §3.6 并列实体补齐。

**修改 2**：拆分 `greenness and stomatal density` → `greenness` @106:115 + `stomatal density` @120:136

**理由**：greenness（叶片绿度）和 stomatal density（气孔密度）是两个独立的性状，不应合并为一个实体。依据 K1 §3.2 并列实体处理原则，并列结构必须拆分为独立实体。

> 依据：K1 §3.2；K8 §1.3 TRT。

**修改 3**：新增 LOI(QTLs, 各TRT) ×6；新增 USE(sorghum, marker assisted selection)

**理由**：原文明确说明 38 QTLs 控制各性状变异，应建立 LOI 关系；高粱育种采用标记辅助选择，应建立 USE 关系。

> 依据：K8 §2.2 LOI；K8 §2.4 USE。

---

### 样本 7

**修改**：新增 `seed germination` @107:122，label=`GST`；新增 OCI(24-h germination rate, seed germination)

**理由**："seed germination" 是种子萌发阶段，属于生育时期 GST。24-h germination rate 是在萌发阶段测定的性状，应建立 OCI 关系。

> 依据：K8 §1.3 GST；K8 §2.4 OCI。

---

### 样本 8

**修改**：新增 `phenotypic diversity` @120:139 TRT；新增 HAS(Sorghum, phenotypic diversity)

**理由**：phenotypic diversity 是高粱的表型多样性，属于 TRT；高粱具有该性状，应建立 HAS 关系。

> 依据：K8 §1.3 TRT；K8 §2.1 HAS。

---

### 样本 9

**修改 1**：新增 `Bulked segregant analysis` @265:290 BM；新增 `RNA sequencing` @295:309 BM

**理由**：Bulked segregant analysis（混合分组分析）是遗传分析方法；RNA sequencing（RNA 测序）是遗传分析技术路线，均属于 BM。

> 依据：K8 §1.4 BM；K7 §2.2（RNA-seq 标为 BM）。

**修改 2**：新增 `SNPs` @321:325 MRK

**理由**：原文 "identified common SNPs in the genomic region of QLB-czas8"，SNPs 是分子标记，漏标。

> 依据：K8 §1.6 MRK。

**修改 3**：新增 LOI(QLB-czas1/2/8, CHR) ×3；新增 LOI(SNPs, QLB-czas8)

**理由**：原文明确说明三个 QTL 定位于染色体 1、2、8，应建立 LOI 关系；SNPs 定位于 QLB-czas8 的基因组区域，应建立 LOI 关系。

> 依据：K8 §2.2 LOI；K2 §2.2。

---

## 三、边界验证记录

所有新增/修改实体均已通过 text[start:end] == entity['text'] 验证：
- `PCR-based markers` @4:22 ✓
- `VrKNAT7` @264:271 ✓；`ACC41` @299:304 ✓；`KPS2` @309:313 ✓
- `F-3 lines` @88:97 ✓；`BSR` @120:123 ✓
- `phenotypic changes` @157:174 ✓
- `Abiotic stress` @0:13 ✓；`growth` @31:37 ✓；`yield` @42:47 ✓；`abiotic stresses` @100:116 ✓；`SbPLD` @133:138 ✓；`sorghum` @153:160 ✓
- `yields` @16:22 ✓
- `flowering` @75:84 ✓；`leaf area` @95:104 ✓；`greenness` @106:115 ✓；`stomatal density` @120:136 ✓
- `seed germination` @107:122 ✓
- `phenotypic diversity` @120:139 ✓
- `Bulked segregant analysis` @265:290 ✓；`RNA sequencing` @295:309 ✓；`SNPs` @321:325 ✓
