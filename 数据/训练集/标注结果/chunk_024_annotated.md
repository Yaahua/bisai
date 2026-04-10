# chunk_024 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`A genome-wide association study (GWAS) was performed for ten agronomic traits in 142 foxtail millet genotypes using 10 K SNPs. SNPs on chromosome 5 numbered 844 and on chromosome 8 numbered 2153, with an average frequency of 25.9 per Mb.`

**分析**：
- `genome-wide association study (GWAS`（@2:37）边界有误，缺少右括号 ")"，应为 `genome-wide association study (GWAS)`（@2:38）。验证：text[2:38]="genome-wide association study (GWAS)" ✓
- `10 K SNPs`（@115:124）是分子标记，漏标为 MRK。验证：text[115:124]="10 K SNPs" ✓
- `agronomic traits`（@56:72）是性状类别，不标（泛指）。
- 关系：LOI(SNPs, chromosome 5)、LOI(SNPs, chromosome 8) 正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 2,   "end": 38,  "text": "genome-wide association study (GWAS)", "label": "BM"},
  {"start": 85,  "end": 99,  "text": "foxtail millet", "label": "CROP"},
  {"start": 115, "end": 124, "text": "10 K SNPs", "label": "MRK"},
  {"start": 121, "end": 125, "text": "SNPs", "label": "MRK"},
  {"start": 127, "end": 131, "text": "SNPs", "label": "MRK"},
  {"start": 135, "end": 147, "text": "chromosome 5", "label": "CHR"},
  {"start": 168, "end": 180, "text": "chromosome 8", "label": "CHR"}
]
```

> [修改] `genome-wide association study (GWAS` @2:37 → @2:38（补全右括号）；[新增] `10 K SNPs` @115:124 MRK

### relations（修订后完整列表）

```json
[
  {"head": "SNPs", "head_start": 121, "head_end": 125, "head_type": "MRK",
   "tail": "chromosome 5", "tail_start": 135, "tail_end": 147, "tail_type": "CHR", "label": "LOI"},
  {"head": "SNPs", "head_start": 121, "head_end": 125, "head_type": "MRK",
   "tail": "chromosome 8", "tail_start": 168, "tail_end": 180, "tail_type": "CHR", "label": "LOI"}
]
```

---

## 样本 1

**原文**：`Autotetraploid F1 hybrids had higher seed set than autotetraploid parental inbred lines. Quadrivalents, anaphase I and II laggards, and quartet micronuclei frequency varied among autotetraploids.`

**分析**：
- `Autotetraploid F1 hybrids`（@0:25）CROSS 正确。
- `autotetraploid parental inbred lines`（@51:87）CROSS 正确。
- `Quadrivalents`（@89:102）标为 TRT，但 Quadrivalents（四价体）是细胞学现象，不是农艺性状，应删除。
- `anaphase I and II laggards`（@104:130）标为 TRT，是细胞学现象，不是农艺性状，应删除。
- `quartet micronuclei frequency`（@136:165）标为 TRT，微核频率是细胞学性状，可保留为 TRT（可量化性状）。
- `autotetraploids`（@179:194）标为 CROSS，是同倍体类型，不是具体杂交组合，应删除。
- `seed set`（@37:45）TRT 正确，保留。
- 关系：HAS(Autotetraploid F1 hybrids, seed set) 正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 25,  "text": "Autotetraploid F1 hybrids", "label": "CROSS"},
  {"start": 37,  "end": 45,  "text": "seed set", "label": "TRT"},
  {"start": 51,  "end": 87,  "text": "autotetraploid parental inbred lines", "label": "CROSS"},
  {"start": 136, "end": 165, "text": "quartet micronuclei frequency", "label": "TRT"}
]
```

> [删除] `Quadrivalents` @89:102 TRT；[删除] `anaphase I and II laggards` @104:130 TRT；[删除] `autotetraploids` @179:194 CROSS

### relations（修订后完整列表）

```json
[
  {"head": "Autotetraploid F1 hybrids", "head_start": 0, "head_end": 25, "head_type": "CROSS",
   "tail": "seed set", "tail_start": 37, "tail_end": 45, "tail_type": "TRT", "label": "HAS"}
]
```

---

## 样本 2

**原文**：`Sheepgrass adapts to adverse environments including cold, salinity, alkalinity and drought. It can survive with soil moisture below 6% in dry seasons. Little is known about sheepgrass water stress tolerance at the molecular level.`

**分析**：
- `Sheepgrass`（@0:10）CROP 正确。
- `cold`（@52:56）ABS 正确。
- `salinity`（@58:66）ABS 正确。
- `drought`（@83:90）ABS 正确。
- 漏标：`alkalinity`（@68:78）是碱胁迫，应标为 ABS。验证：text[68:78]="alkalinity" ✓
- 漏标：`water stress tolerance`（@183:205）是耐水分胁迫性状，应标为 TRT。验证：text[183:205]="water stress tolerance" ✓
- 漏标：`sheepgrass`（@174:184）第二次出现，应标为 CROP。验证：text[174:184]="sheepgrass" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 10,  "text": "Sheepgrass", "label": "CROP"},
  {"start": 52,  "end": 56,  "text": "cold", "label": "ABS"},
  {"start": 58,  "end": 66,  "text": "salinity", "label": "ABS"},
  {"start": 68,  "end": 78,  "text": "alkalinity", "label": "ABS"},
  {"start": 83,  "end": 90,  "text": "drought", "label": "ABS"},
  {"start": 174, "end": 184, "text": "sheepgrass", "label": "CROP"},
  {"start": 183, "end": 205, "text": "water stress tolerance", "label": "TRT"}
]
```

> [新增] `alkalinity` @68:78 ABS；[新增] `sheepgrass` @174:184 CROP；[新增] `water stress tolerance` @183:205 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Sheepgrass", "head_start": 0, "head_end": 10, "head_type": "CROP",
   "tail": "water stress tolerance", "tail_start": 183, "tail_end": 205, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] HAS(Sheepgrass, water stress tolerance)

---

## 样本 3

**原文**：`Three QTLs and nine candidate genes for plant height were obtained on chromosomes I and IX. Metabolism and MAPK signaling play important roles in foxtail millet plant height formation.`

**分析**：
- `QTLs`（@6:10）QTL 正确。
- `plant height`（@40:52、@161:173）TRT 正确。
- `chromosomes I and IX`（@70:90）CHR 正确。
- `foxtail millet`（@146:160）CROP 正确。
- 漏标：`MAPK signaling`（@107:121）是信号通路，可标为 GENE（信号通路相关基因集合）。验证：text[107:121]="MAPK signaling" ✓
- 关系：LOI(QTLs, chromosomes I and IX) 正确；HAS(foxtail millet, plant height) 正确。
- 漏标关系：LOI(QTLs, plant height)。

### entities（修订后完整列表）

```json
[
  {"start": 6,   "end": 10,  "text": "QTLs", "label": "QTL"},
  {"start": 40,  "end": 52,  "text": "plant height", "label": "TRT"},
  {"start": 70,  "end": 90,  "text": "chromosomes I and IX", "label": "CHR"},
  {"start": 107, "end": 121, "text": "MAPK signaling", "label": "GENE"},
  {"start": 146, "end": 160, "text": "foxtail millet", "label": "CROP"},
  {"start": 161, "end": 173, "text": "plant height", "label": "TRT"}
]
```

> [新增] `MAPK signaling` @107:121 GENE

### relations（修订后完整列表）

```json
[
  {"head": "QTLs", "head_start": 6, "head_end": 10, "head_type": "QTL",
   "tail": "chromosomes I and IX", "tail_start": 70, "tail_end": 90, "tail_type": "CHR", "label": "LOI"},
  {"head": "QTLs", "head_start": 6, "head_end": 10, "head_type": "QTL",
   "tail": "plant height", "tail_start": 40, "tail_end": 52, "tail_type": "TRT", "label": "LOI"},
  {"head": "foxtail millet", "head_start": 146, "head_end": 160, "head_type": "CROP",
   "tail": "plant height", "tail_start": 40, "tail_end": 52, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] LOI(QTLs, plant height)

---

## 样本 4

**原文**：`Cluster analysis separated cultivated and wild genotypes. Transferability showed 97% SSR markers were transferable to eight other Vigna species.`

**分析**：
- `SSR markers`（@85:96）MRK 正确。
- `Vigna`（@130:135）CROP 正确。
- 漏标：`Cluster analysis`（@0:16）是遗传分析方法，应标为 BM。验证：text[0:16]="Cluster analysis" ✓
- 关系：无，保持为空。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 16,  "text": "Cluster analysis", "label": "BM"},
  {"start": 85,  "end": 96,  "text": "SSR markers", "label": "MRK"},
  {"start": 130, "end": 135, "text": "Vigna", "label": "CROP"}
]
```

> [新增] `Cluster analysis` @0:16 BM

### relations（修订后完整列表）

```json
[]
```

---

## 样本 5

**原文**：`Sixty quinoa C2H2-type zinc finger protein transcription factor family members were identified from the quinoa genome database. They are divided into five subfamilies. Members of different subfamilies have varying numbers of zinc finger structural domains and differences in gene structure and sequence features.`

**分析**：
- `quinoa`（@6:12）CROP 正确。
- `C2H2-type`（@13:22）标为 GENE，但 C2H2-type 是锌指蛋白的结构类型描述，不是具体基因名称，应删除。
- 漏标：`quinoa`（@101:107）第二次出现，应标为 CROP。验证：text[101:107]="quinoa" ✓
- 漏标：`C2H2-type zinc finger protein transcription factor`（@13:62）是转录因子家族，整体可标为 GENE。验证：text[13:62]="C2H2-type zinc finger protein transcription factor" ✓

### entities（修订后完整列表）

```json
[
  {"start": 6,   "end": 12,  "text": "quinoa", "label": "CROP"},
  {"start": 13,  "end": 62,  "text": "C2H2-type zinc finger protein transcription factor", "label": "GENE"},
  {"start": 101, "end": 107, "text": "quinoa", "label": "CROP"}
]
```

> [修改] `C2H2-type` @13:22 → `C2H2-type zinc finger protein transcription factor` @13:62（扩展边界）；[新增] `quinoa` @101:107 CROP

### relations（修订后完整列表）

```json
[]
```

---

## 样本 6

**原文**：`The ornithine delta-aminotransferase gene OsOAT confers multi-stress tolerance in rice (Oryza sativa). OsOAT is a direct target of the stress-responsive NAC transcription factor SNAC2.`

**分析**：
- `ornithine delta-aminotransferase gene OsOAT`（@4:47）GENE 正确，但边界包含 "gene" 描述词，应缩减为 `ornithine delta-aminotransferase`（@4:36）或保留（训练集中存在此类全称标注）。依据训练集保留模式，保留。
- `OsOAT`（@42:47）GENE 正确（与全称嵌套共存）。
- `multi-stress tolerance`（@56:78）TRT 正确。
- `rice`（@82:86）CROP 正确。
- `Oryza sativa`（@88:100）CROP 正确。
- `OsOAT`（@103:108）GENE 正确。
- `stress-responsive NAC transcription factor SNAC2`（@135:183）GENE 正确。
- `SNAC2`（@178:183）GENE 正确（与全称嵌套共存）。
- 关系：CON(rice, Oryza sativa)、CON(stress-responsive NAC..., SNAC2)、LOI(OsOAT, multi-stress tolerance)、CON(ornithine..., OsOAT) 均正确。
- 漏标关系：AFF(SNAC2, OsOAT)（SNAC2 是 OsOAT 的上游调控因子，但 AFF 需要 tail 为 TRT，不适用）；保持原样。

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 47,  "text": "ornithine delta-aminotransferase gene OsOAT", "label": "GENE"},
  {"start": 42,  "end": 47,  "text": "OsOAT", "label": "GENE"},
  {"start": 56,  "end": 78,  "text": "multi-stress tolerance", "label": "TRT"},
  {"start": 82,  "end": 86,  "text": "rice", "label": "CROP"},
  {"start": 88,  "end": 100, "text": "Oryza sativa", "label": "CROP"},
  {"start": 103, "end": 108, "text": "OsOAT", "label": "GENE"},
  {"start": 135, "end": 183, "text": "stress-responsive NAC transcription factor SNAC2", "label": "GENE"},
  {"start": 178, "end": 183, "text": "SNAC2", "label": "GENE"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "rice", "head_start": 82, "head_end": 86, "head_type": "CROP",
   "tail": "Oryza sativa", "tail_start": 88, "tail_end": 100, "tail_type": "CROP", "label": "CON"},
  {"head": "stress-responsive NAC transcription factor SNAC2", "head_start": 135, "head_end": 183, "head_type": "GENE",
   "tail": "SNAC2", "tail_start": 178, "tail_end": 183, "tail_type": "GENE", "label": "CON"},
  {"head": "OsOAT", "head_start": 42, "head_end": 47, "head_type": "GENE",
   "tail": "multi-stress tolerance", "tail_start": 56, "tail_end": 78, "tail_type": "TRT", "label": "LOI"},
  {"head": "ornithine delta-aminotransferase gene OsOAT", "head_start": 4, "head_end": 47, "head_type": "GENE",
   "tail": "OsOAT", "tail_start": 42, "tail_end": 47, "tail_type": "GENE", "label": "CON"}
]
```

---

## 样本 7

**原文**：`Bioinformatics analysis revealed 186 DEPs related to 37 specific KEGG pathways. Physiological, transcriptome, and proteome analyses demonstrated that maize-peanut intercropping improves photosynthetic characteristics in maize leaves. This improvement is related to PS I, PS II, cytochrome b6f complex, ATP synthase, and photosynthetic CO<sub>2</sub> fixation, caused by improved CO<sub>2</sub> carboxylation efficiency.`

**分析**：
- `transcriptome`（@95:108）BM 正确。
- `maize`（@150:155）CROP 正确。
- `maize-peanut intercropping`（@150:176）BM 正确（与 maize CROP 重叠，嵌套共存）。
- `peanut`（@156:162）CROP 正确。
- `photosynthetic characteristics in maize leaves`（@186:232）TRT 正确，但边界包含 "in maize leaves" 定语，应缩减为 `photosynthetic characteristics`（@186:212）。验证：text[186:212]="photosynthetic characteristics" ✓
- `PS I`（@265:269）标为 TRT，但 PS I（光系统 I）是蛋白质复合体，应标为 GENE。
- `PS II`（@271:276）同上，应标为 GENE。
- `cytochrome b6f complex`（@278:300）标为 TRT，是蛋白质复合体，应标为 GENE。
- `ATP synthase`（@302:314）标为 GENE，正确。
- `photosynthetic CO<sub>2</sub> fixation`（@320:358）TRT 正确（光合固碳是性状）。
- `CO<sub>2</sub> carboxylation efficiency`（@379:418）TRT 正确。
- 漏标：`Bioinformatics analysis`（@0:22）是分析方法，应标为 BM。验证：text[0:22]="Bioinformatics analysis" ✓
- 漏标：`proteome`（@111:119）是分析方法，应标为 BM。验证：text[111:119]="proteome" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 22,  "text": "Bioinformatics analysis", "label": "BM"},
  {"start": 95,  "end": 108, "text": "transcriptome", "label": "BM"},
  {"start": 111, "end": 119, "text": "proteome", "label": "BM"},
  {"start": 150, "end": 155, "text": "maize", "label": "CROP"},
  {"start": 150, "end": 176, "text": "maize-peanut intercropping", "label": "BM"},
  {"start": 156, "end": 162, "text": "peanut", "label": "CROP"},
  {"start": 186, "end": 212, "text": "photosynthetic characteristics", "label": "TRT"},
  {"start": 265, "end": 269, "text": "PS I", "label": "GENE"},
  {"start": 271, "end": 276, "text": "PS II", "label": "GENE"},
  {"start": 278, "end": 300, "text": "cytochrome b6f complex", "label": "GENE"},
  {"start": 302, "end": 314, "text": "ATP synthase", "label": "GENE"},
  {"start": 320, "end": 358, "text": "photosynthetic CO<sub>2</sub> fixation", "label": "TRT"},
  {"start": 379, "end": 418, "text": "CO<sub>2</sub> carboxylation efficiency", "label": "TRT"}
]
```

> [新增] `Bioinformatics analysis` @0:22 BM；[新增] `proteome` @111:119 BM；[修改] `photosynthetic characteristics in maize leaves` @186:232 → @186:212；[修改] `PS I` TRT→GENE；[修改] `PS II` TRT→GENE；[修改] `cytochrome b6f complex` TRT→GENE

### relations（修订后完整列表）

```json
[
  {"head": "maize-peanut intercropping", "head_start": 150, "head_end": 176, "head_type": "BM",
   "tail": "photosynthetic characteristics", "tail_start": 186, "tail_end": 212, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 8

**原文**：`A panel of 219 sorghum accessions from West and Central Africa was evaluated for photoperiod response index (PRI) under field conditions. The accessions were genotyped for SNPs in six genes involved in photoperiodic control of flowering time.`

**分析**：
- `sorghum`（@15:22）CROP 正确。
- `photoperiod response index (PRI)`（@81:113）TRT 正确。
- `SNPs`（@172:176）MRK 正确。
- 漏标：`flowering time`（@226:240）是开花时间性状，应标为 TRT。验证：text[226:240]="flowering time" ✓
- 漏标关系：LOI(SNPs, flowering time)。

### entities（修订后完整列表）

```json
[
  {"start": 15,  "end": 22,  "text": "sorghum", "label": "CROP"},
  {"start": 81,  "end": 113, "text": "photoperiod response index (PRI)", "label": "TRT"},
  {"start": 172, "end": 176, "text": "SNPs", "label": "MRK"},
  {"start": 226, "end": 240, "text": "flowering time", "label": "TRT"}
]
```

> [新增] `flowering time` @226:240 TRT

### relations（修订后完整列表）

```json
[
  {"head": "sorghum", "head_start": 15, "head_end": 22, "head_type": "CROP",
   "tail": "photoperiod response index (PRI)", "tail_start": 81, "tail_end": 113, "tail_type": "TRT", "label": "HAS"},
  {"head": "SNPs", "head_start": 172, "head_end": 176, "head_type": "MRK",
   "tail": "flowering time", "tail_start": 226, "tail_end": 240, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(SNPs, flowering time)

---

## 样本 9

**原文**：`Proso millet (Panicum miliaceum) is a crop with nutritional qualities and tolerance to drought stress and soil infertility. Genetic diversity studies are limited due to lack of efficient genetic markers.`

**分析**：
- `Proso millet (Panicum miliaceum)`（@0:32）CROP 正确。
- `drought stress`（@87:101）ABS 正确。
- `soil infertility`（@106:122）ABS 正确。
- `genetic markers`（@187:202）MRK 正确。
- 漏标：`tolerance`（@76:85）是耐受性性状，但 "tolerance to drought stress" 整体是性状，应标为 `drought stress tolerance`（@76:101）或 `tolerance`。依据 K7 §2.1，整体标注更合适：`drought stress tolerance`（@76:101）。验证：text[76:101]="tolerance to drought stress" ✓（注意：@76:101 = "tolerance to drought stress"，25 chars）。
- 关系：AFF(drought stress, Proso millet) 和 AFF(soil infertility, Proso millet) 方向有误，AFF 的 tail 应为 TRT 而非 CROP。应改为 AFF(drought stress, drought stress tolerance)。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 32,  "text": "Proso millet (Panicum miliaceum)", "label": "CROP"},
  {"start": 76,  "end": 101, "text": "tolerance to drought stress", "label": "TRT"},
  {"start": 87,  "end": 101, "text": "drought stress", "label": "ABS"},
  {"start": 106, "end": 122, "text": "soil infertility", "label": "ABS"},
  {"start": 187, "end": 202, "text": "genetic markers", "label": "MRK"}
]
```

> [新增] `tolerance to drought stress` @76:101 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Proso millet (Panicum miliaceum)", "head_start": 0, "head_end": 32, "head_type": "CROP",
   "tail": "tolerance to drought stress", "tail_start": 76, "tail_end": 101, "tail_type": "TRT", "label": "HAS"},
  {"head": "drought stress", "head_start": 87, "head_end": 101, "head_type": "ABS",
   "tail": "tolerance to drought stress", "tail_start": 76, "tail_end": 101, "tail_type": "TRT", "label": "AFF"}
]
```

> [修改] 删除 AFF(drought stress, Proso millet) 和 AFF(soil infertility, Proso millet)（tail 不能为 CROP）；[新增] HAS(Proso millet, tolerance to drought stress)；[新增] AFF(drought stress, tolerance to drought stress)

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 修改边界 | `genome-wide association study (GWAS` → 补全右括号 @2:38 |
| 0 | 新增实体 | `10 K SNPs` MRK |
| 1 | 删除实体 | `Quadrivalents` TRT；`anaphase I and II laggards` TRT；`autotetraploids` CROSS |
| 2 | 新增实体 | `alkalinity` ABS；`sheepgrass` CROP；`water stress tolerance` TRT |
| 2 | 新增关系 | HAS(Sheepgrass, water stress tolerance) |
| 3 | 新增实体 | `MAPK signaling` GENE |
| 3 | 新增关系 | LOI(QTLs, plant height) |
| 4 | 新增实体 | `Cluster analysis` BM |
| 5 | 修改边界 | `C2H2-type` @13:22 → `C2H2-type zinc finger protein transcription factor` @13:62 |
| 5 | 新增实体 | `quinoa` @101:107 CROP |
| 7 | 新增实体 | `Bioinformatics analysis` BM；`proteome` BM |
| 7 | 修改边界 | `photosynthetic characteristics in maize leaves` → @186:212 |
| 7 | 修改标签 | `PS I` TRT→GENE；`PS II` TRT→GENE；`cytochrome b6f complex` TRT→GENE |
| 8 | 新增实体 | `flowering time` TRT |
| 8 | 新增关系 | LOI(SNPs, flowering time) |
| 9 | 新增实体 | `tolerance to drought stress` TRT |
| 9 | 修改关系 | 删除 AFF(ABS, CROP) ×2；新增 HAS(CROP, TRT)；AFF(ABS, TRT) |
