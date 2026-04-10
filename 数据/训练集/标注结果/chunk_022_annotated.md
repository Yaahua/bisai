# chunk_022 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`Six PCR-based markers were developed to identify the resistant Pc39 allele. The closely linked marker SCAR_3456624 is within 0.37 cM of Pc39.`

**分析**：
- `PCR-based markers`（@4:22）是分子标记，漏标为 MRK。验证：text[4:22]="PCR-based markers" ✓
- `Pc39` 是抗性基因/等位基因，原标注为 GENE，正确。
- 关系：LOI(SCAR_3456624, Pc39) 正确保留。

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 22,  "text": "PCR-based markers", "label": "MRK"},
  {"start": 63,  "end": 67,  "text": "Pc39", "label": "GENE"},
  {"start": 102, "end": 114, "text": "SCAR_3456624", "label": "MRK"},
  {"start": 136, "end": 140, "text": "Pc39", "label": "GENE"}
]
```

> [新增] `PCR-based markers` @4:22 MRK

### relations（修订后完整列表）

```json
[
  {
    "head": "SCAR_3456624", "head_start": 102, "head_end": 114, "head_type": "MRK",
    "tail": "Pc39", "tail_start": 63, "tail_end": 67, "tail_type": "GENE",
    "label": "LOI"
  }
]
```

---

## 样本 1

**原文**：`The Sdwa5.1.1+ was confirmed in an F-2:3 population from the same cross and mapped to a 3.298-Kb region containing the gene LOC106767068, designated as VrKNAT7-1. This gene encodes the transcription factor KNOTTED ARABIDOPSIS THALIANA7 (KNAT7), a KNOX II protein. VrKNAT7 sequence alignment between ACC41 and KPS2 revealed polymorphisms in the coding, untranslated, and promoter regions.`

**分析**：
- `VrKNAT7 sequence`（@264:280）边界有误，"sequence" 是描述词，不属于基因名称。应改为 `VrKNAT7`（@264:271）。验证：text[264:271]="VrKNAT7" ✓
- `ACC41`（@299:304）和 `KPS2`（@309:313）是品种名（豇豆品种），应改为 VAR。验证：text[299:304]="ACC41" ✓；text[309:313]="KPS2" ✓
- `KNOX II`（@247:254）是蛋白质家族名，不是具体基因，应删除（K8 §1.2 GENE 需要具体基因名）。

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 14,  "text": "Sdwa5.1.1+", "label": "QTL"},
  {"start": 35,  "end": 51,  "text": "F-2:3 population", "label": "CROSS"},
  {"start": 124, "end": 136, "text": "LOC106767068", "label": "GENE"},
  {"start": 152, "end": 161, "text": "VrKNAT7-1", "label": "GENE"},
  {"start": 206, "end": 243, "text": "KNOTTED ARABIDOPSIS THALIANA7 (KNAT7)", "label": "GENE"},
  {"start": 264, "end": 271, "text": "VrKNAT7", "label": "GENE"},
  {"start": 299, "end": 304, "text": "ACC41", "label": "VAR"},
  {"start": 309, "end": 313, "text": "KPS2", "label": "VAR"}
]
```

> [修改] `VrKNAT7 sequence`→`VrKNAT7` @264:271；[修改] `ACC41` GENE→VAR；[修改] `KPS2` GENE→VAR；[删除] `KNOX II` @247:254 GENE

### relations（修订后完整列表）

```json
[
  {
    "head": "Sdwa5.1.1+", "head_start": 4, "head_end": 14, "head_type": "QTL",
    "tail": "LOC106767068", "tail_start": 124, "tail_end": 136, "tail_type": "GENE",
    "label": "LOI"
  },
  {
    "head": "Sdwa5.1.1+", "head_start": 4, "head_end": 14, "head_type": "QTL",
    "tail": "VrKNAT7-1", "tail_start": 152, "tail_end": 161, "tail_type": "GENE",
    "label": "LOI"
  },
  {
    "head": "VrKNAT7-1", "head_start": 152, "head_end": 161, "head_type": "GENE",
    "tail": "KNOTTED ARABIDOPSIS THALIANA7 (KNAT7)", "tail_start": 206, "tail_end": 243, "tail_type": "GENE",
    "label": "CON"
  }
]
```

---

## 样本 2

**原文**：`Field selection using pathogen and artificial inoculation is time-consuming. We used 105 F-3 lines from a cross between BSR-resistant 'Syumari' and susceptible 'Buchishoryukei-1' for BSR inoculation tests. AFLP analyses with 1024 primer sets showed six fragments were polymorphic between resistant and susceptible bulked groups.`

**分析**：
- `F-3 lines`（@88:97）是杂交后代群体，漏标为 CROSS。验证：text[88:97]="F-3 lines" ✓
- `BSR`（@120:123）标为 ABS，但 BSR（Brown Stem Rot，大豆茎褐腐病）是病害，应为 BIS。
- `BSR inoculation tests`（@183:204）整体标为 BM，但 "BSR"（@183:186）同时标为 BIS，两者重叠。保留 BM 整体标注，删除 BIS 单独标注（BM 已包含）。
- `primer sets`（@230:241）是实验材料，不是分子标记，应删除 MRK 标注。
- `fragments`（@253:262）是实验现象（条带），不是分子标记，应删除（error_patterns §2.1 "779 bp band" 同理）。
- `AFLP`（@206:210）是分子标记类型，正确保留为 MRK。

### entities（修订后完整列表）

```json
[
  {"start": 88,  "end": 97,  "text": "F-3 lines", "label": "CROSS"},
  {"start": 120, "end": 123, "text": "BSR", "label": "BIS"},
  {"start": 135, "end": 142, "text": "Syumari", "label": "VAR"},
  {"start": 161, "end": 177, "text": "Buchishoryukei-1", "label": "VAR"},
  {"start": 183, "end": 204, "text": "BSR inoculation tests", "label": "BM"},
  {"start": 206, "end": 210, "text": "AFLP", "label": "MRK"}
]
```

> [新增] `F-3 lines` @88:97 CROSS；[修改] `BSR` @120:123 ABS→BIS；[删除] `BSR` @183:186 BIS（被 BM 包含）；[删除] `primer sets` @230:241 MRK；[删除] `fragments` @253:262 MRK

### relations（修订后完整列表）

```json
[]
```

> [删除] 原有 CON(AFLP, primer sets) 和 CON(AFLP, fragments)（实体已删除）

---

## 样本 3

**原文**：`Loss-of-function mutations in CCD7, CCD8, MAX1, and DUF genes downregulated expression of associated genes in the SL biosynthetic pathway. Edited lines showed phenotypic changes compared to wild-type plants.`

**分析**：
- `DUF`（@48:51）是蛋白质结构域类别名（Domain of Unknown Function），不是具体基因名，应删除。
- `SL`（@108:110）是独脚金内酯（Strigolactone），是一种植物激素，在此语境中不需标注。
- 原标注中 CCD7、CCD8、MAX1 正确，保留。
- 漏标：`phenotypic changes`（@157:174）是性状，应标为 TRT。验证：text[157:174]="phenotypic changes" ✓

### entities（修订后完整列表）

```json
[
  {"start": 30,  "end": 34,  "text": "CCD7", "label": "GENE"},
  {"start": 36,  "end": 40,  "text": "CCD8", "label": "GENE"},
  {"start": 42,  "end": 46,  "text": "MAX1", "label": "GENE"},
  {"start": 157, "end": 174, "text": "phenotypic changes", "label": "TRT"}
]
```

> [新增] `phenotypic changes` @157:174 TRT；（DUF 不标）

### relations（修订后完整列表）

```json
[]
```

---

## 样本 4

**原文**：`Abiotic stress impacts sorghum growth and yield. Phospholipase D hydrolyzes phospholipids and responds to abiotic stresses. The Phospholipase D (SbPLD) family in sorghum is rarely reported.`

**分析**：
- `Abiotic stress`（@0:13）是非生物胁迫，漏标为 ABS。验证：text[0:13]="Abiotic stress" ✓
- `sorghum`（@23:30）已标为 CROP，正确。
- `growth`（@31:37）是生长性状，漏标为 TRT。验证：text[31:37]="growth" ✓
- `yield`（@42:47）是产量性状，漏标为 TRT。验证：text[42:47]="yield" ✓
- `abiotic stresses`（@100:116）是非生物胁迫，漏标为 ABS。验证：text[100:116]="abiotic stresses" ✓
- `Phospholipase D`（@49:63）是酶/蛋白质，不标（非基因名称）。
- `SbPLD`（@133:138）是基因家族名，可标为 GENE。验证：text[133:138]="SbPLD" ✓
- `sorghum`（@153:160）是第二次出现，漏标为 CROP。验证：text[153:160]="sorghum" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 13,  "text": "Abiotic stress", "label": "ABS"},
  {"start": 23,  "end": 30,  "text": "sorghum", "label": "CROP"},
  {"start": 31,  "end": 37,  "text": "growth", "label": "TRT"},
  {"start": 42,  "end": 47,  "text": "yield", "label": "TRT"},
  {"start": 100, "end": 116, "text": "abiotic stresses", "label": "ABS"},
  {"start": 133, "end": 138, "text": "SbPLD", "label": "GENE"},
  {"start": 153, "end": 160, "text": "sorghum", "label": "CROP"}
]
```

> [新增] `Abiotic stress` @0:13 ABS；[新增] `growth` @31:37 TRT；[新增] `yield` @42:47 TRT；[新增] `abiotic stresses` @100:116 ABS；[新增] `SbPLD` @133:138 GENE；[新增] `sorghum` @153:160 CROP

### relations（修订后完整列表）

```json
[
  {
    "head": "Abiotic stress", "head_start": 0, "head_end": 13, "head_type": "ABS",
    "tail": "growth", "tail_start": 31, "tail_end": 37, "tail_type": "TRT",
    "label": "AFF"
  },
  {
    "head": "Abiotic stress", "head_start": 0, "head_end": 13, "head_type": "ABS",
    "tail": "yield", "tail_start": 42, "tail_end": 47, "tail_type": "TRT",
    "label": "AFF"
  },
  {
    "head": "sorghum", "head_start": 23, "head_end": 30, "head_type": "CROP",
    "tail": "growth", "tail_start": 31, "tail_end": 37, "tail_type": "TRT",
    "label": "HAS"
  },
  {
    "head": "sorghum", "head_start": 23, "head_end": 30, "head_type": "CROP",
    "tail": "yield", "tail_start": 42, "tail_end": 47, "tail_type": "TRT",
    "label": "HAS"
  }
]
```

> [新增] AFF(Abiotic stress, growth)；AFF(Abiotic stress, yield)；HAS(sorghum, growth)；HAS(sorghum, yield)

---

## 样本 5

**原文**：`Qing1 and Long4 yields were 27.25% and 21.42% higher than the control. Both varieties had higher average proline, CAT and soluble sugar contents than the control.`

**分析**：
- `yields`（@16:22）是产量性状，漏标为 TRT。验证：text[16:22]="yields" ✓
- 原有 HAS 关系中 Long4 缺少 HAS(Long4, CAT)，需补充。
- 其余实体与关系正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 5,   "text": "Qing1", "label": "VAR"},
  {"start": 10,  "end": 15,  "text": "Long4", "label": "VAR"},
  {"start": 16,  "end": 22,  "text": "yields", "label": "TRT"},
  {"start": 97,  "end": 112, "text": "average proline", "label": "TRT"},
  {"start": 114, "end": 117, "text": "CAT", "label": "TRT"},
  {"start": 122, "end": 144, "text": "soluble sugar contents", "label": "TRT"}
]
```

> [新增] `yields` @16:22 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Qing1", "head_start": 0, "head_end": 5, "head_type": "VAR",
   "tail": "yields", "tail_start": 16, "tail_end": 22, "tail_type": "TRT", "label": "HAS"},
  {"head": "Long4", "head_start": 10, "head_end": 15, "head_type": "VAR",
   "tail": "yields", "tail_start": 16, "tail_end": 22, "tail_type": "TRT", "label": "HAS"},
  {"head": "Qing1", "head_start": 0, "head_end": 5, "head_type": "VAR",
   "tail": "average proline", "tail_start": 97, "tail_end": 112, "tail_type": "TRT", "label": "HAS"},
  {"head": "Qing1", "head_start": 0, "head_end": 5, "head_type": "VAR",
   "tail": "CAT", "tail_start": 114, "tail_end": 117, "tail_type": "TRT", "label": "HAS"},
  {"head": "Qing1", "head_start": 0, "head_end": 5, "head_type": "VAR",
   "tail": "soluble sugar contents", "tail_start": 122, "tail_end": 144, "tail_type": "TRT", "label": "HAS"},
  {"head": "Long4", "head_start": 10, "head_end": 15, "head_type": "VAR",
   "tail": "average proline", "tail_start": 97, "tail_end": 112, "tail_type": "TRT", "label": "HAS"},
  {"head": "Long4", "head_start": 10, "head_end": 15, "head_type": "VAR",
   "tail": "CAT", "tail_start": 114, "tail_end": 117, "tail_type": "TRT", "label": "HAS"},
  {"head": "Long4", "head_start": 10, "head_end": 15, "head_type": "VAR",
   "tail": "soluble sugar contents", "tail_start": 122, "tail_end": 144, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] HAS(Qing1, yields)；HAS(Long4, yields)；[新增] HAS(Long4, CAT)

---

## 样本 6

**原文**：`Subsequent experiments identified 38 QTLs controlling variation in height, flowering, biomass, leaf area, greenness and stomatal density. Colocalisation of these QTLs with agronomic traits indicates they can be used for improving sorghum performance through marker assisted selection under preflowering drought stress.`

**分析**：
- `flowering`（@75:84）是开花性状，漏标为 TRT。验证：text[75:84]="flowering" ✓
- `leaf area`（@95:104）是叶面积性状，漏标为 TRT。验证：text[95:104]="leaf area" ✓
- `greenness and stomatal density`（@106:136）原标为单一 TRT，但这是两个并列性状，应拆分为 `greenness`（@106:115）和 `stomatal density`（@120:136）。验证：text[106:115]="greenness" ✓；text[120:136]="stomatal density" ✓
- 新增关系：QTLs LOI 各 TRT。

### entities（修订后完整列表）

```json
[
  {"start": 37,  "end": 41,  "text": "QTLs", "label": "QTL"},
  {"start": 67,  "end": 73,  "text": "height", "label": "TRT"},
  {"start": 75,  "end": 84,  "text": "flowering", "label": "TRT"},
  {"start": 86,  "end": 93,  "text": "biomass", "label": "TRT"},
  {"start": 95,  "end": 104, "text": "leaf area", "label": "TRT"},
  {"start": 106, "end": 115, "text": "greenness", "label": "TRT"},
  {"start": 120, "end": 136, "text": "stomatal density", "label": "TRT"},
  {"start": 230, "end": 237, "text": "sorghum", "label": "CROP"},
  {"start": 258, "end": 283, "text": "marker assisted selection", "label": "BM"},
  {"start": 290, "end": 317, "text": "preflowering drought stress", "label": "ABS"}
]
```

> [新增] `flowering` @75:84 TRT；[新增] `leaf area` @95:104 TRT；[修改] 拆分 `greenness and stomatal density` → `greenness` @106:115 + `stomatal density` @120:136

### relations（修订后完整列表）

```json
[
  {"head": "QTLs", "head_start": 37, "head_end": 41, "head_type": "QTL",
   "tail": "height", "tail_start": 67, "tail_end": 73, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTLs", "head_start": 37, "head_end": 41, "head_type": "QTL",
   "tail": "flowering", "tail_start": 75, "tail_end": 84, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTLs", "head_start": 37, "head_end": 41, "head_type": "QTL",
   "tail": "biomass", "tail_start": 86, "tail_end": 93, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTLs", "head_start": 37, "head_end": 41, "head_type": "QTL",
   "tail": "leaf area", "tail_start": 95, "tail_end": 104, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTLs", "head_start": 37, "head_end": 41, "head_type": "QTL",
   "tail": "greenness", "tail_start": 106, "tail_end": 115, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTLs", "head_start": 37, "head_end": 41, "head_type": "QTL",
   "tail": "stomatal density", "tail_start": 120, "tail_end": 136, "tail_type": "TRT", "label": "LOI"},
  {"head": "sorghum", "head_start": 230, "head_end": 237, "head_type": "CROP",
   "tail": "marker assisted selection", "tail_start": 258, "tail_end": 283, "tail_type": "BM", "label": "USE"}
]
```

> [新增] LOI(QTLs, 各TRT) ×6；[新增] USE(sorghum, marker assisted selection)

---

## 样本 7

**原文**：`Genes associated with abscisic acid, gibberellic acid, brassinosteroid, and auxin signaling are involved in seed germination. GWAS of the 24-h germination rate across 232 cultivars identified four significant SNPs and 31 candidate genes. SbPP2C33 is the top candidate based on transcriptome integration.`

**分析**：
- `seed germination`（@107:122）是生育时期/性状，漏标为 GST 或 TRT。"seed germination" 是萌发过程，属于 GST（生育时期）。验证：text[107:122]="seed germination" ✓
- `232 cultivars`（@167:179）是品种群体，不标（泛化描述，无具体品种名）。
- 原有关系正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 107, "end": 122, "text": "seed germination", "label": "GST"},
  {"start": 126, "end": 130, "text": "GWAS", "label": "BM"},
  {"start": 138, "end": 159, "text": "24-h germination rate", "label": "TRT"},
  {"start": 209, "end": 213, "text": "SNPs", "label": "MRK"},
  {"start": 238, "end": 246, "text": "SbPP2C33", "label": "GENE"},
  {"start": 277, "end": 290, "text": "transcriptome", "label": "BM"}
]
```

> [新增] `seed germination` @107:122 GST

### relations（修订后完整列表）

```json
[
  {"head": "SNPs", "head_start": 209, "head_end": 213, "head_type": "MRK",
   "tail": "24-h germination rate", "tail_start": 138, "tail_end": 159, "tail_type": "TRT", "label": "LOI"},
  {"head": "SbPP2C33", "head_start": 238, "head_end": 246, "head_type": "GENE",
   "tail": "24-h germination rate", "tail_start": 138, "tail_end": 159, "tail_type": "TRT", "label": "LOI"},
  {"head": "24-h germination rate", "head_start": 138, "head_end": 159, "head_type": "TRT",
   "tail": "seed germination", "tail_start": 107, "tail_end": 122, "tail_type": "GST", "label": "OCI"}
]
```

> [新增] OCI(24-h germination rate, seed germination)

---

## 样本 8

**原文**：`Sorghum is a widely grown cereal crop. It is adapted to different climates and bred for multiple purposes, resulting in phenotypic diversity.`

**分析**：
- `phenotypic diversity`（@120:139）是性状多样性，漏标为 TRT。验证：text[120:139]="phenotypic diversity" ✓
- 原有 `Sorghum`（@0:7）CROP 正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 7,   "text": "Sorghum", "label": "CROP"},
  {"start": 120, "end": 139, "text": "phenotypic diversity", "label": "TRT"}
]
```

> [新增] `phenotypic diversity` @120:139 TRT

### relations（修订后完整列表）

```json
[
  {
    "head": "Sorghum", "head_start": 0, "head_end": 7, "head_type": "CROP",
    "tail": "phenotypic diversity", "tail_start": 120, "tail_end": 139, "tail_type": "TRT",
    "label": "HAS"
  }
]
```

> [新增] HAS(Sorghum, phenotypic diversity)

---

## 样本 9

**原文**：`Three QTL, QLB-czas1, QLB-czas2, and QLB-czas8, were detected on chromosomes 1, 2, and 8 of Yugu 5. QLB-czas1 explained 14-17% of phenotypic variation in 2 environments. QLB-czas2 explained 9% in 5 environments. QLB-czas8 explained 12-20% in 6 environments. Bulked segregant analysis and RNA sequencing identified common SNPs in the genomic region of QLB-czas8.`

**分析**：
- `Bulked segregant analysis`（@265:290）是育种分析方法，漏标为 BM。验证：text[265:290]="Bulked segregant analysis" ✓
- `RNA sequencing`（@295:309）是遗传分析方法，漏标为 BM。验证：text[295:309]="RNA sequencing" ✓
- `SNPs`（@321:325）是分子标记，漏标为 MRK。验证：text[321:325]="SNPs" ✓
- 原有 QTL、CHR、VAR 及 CON 关系正确，保留。
- 新增关系：LOI(QLB-czas1/2/8, CHR)；LOI(SNPs, QLB-czas8)。

### entities（修订后完整列表）

```json
[
  {"start": 11,  "end": 20,  "text": "QLB-czas1", "label": "QTL"},
  {"start": 22,  "end": 31,  "text": "QLB-czas2", "label": "QTL"},
  {"start": 37,  "end": 46,  "text": "QLB-czas8", "label": "QTL"},
  {"start": 65,  "end": 88,  "text": "chromosomes 1, 2, and 8", "label": "CHR"},
  {"start": 92,  "end": 98,  "text": "Yugu 5", "label": "VAR"},
  {"start": 100, "end": 109, "text": "QLB-czas1", "label": "QTL"},
  {"start": 170, "end": 179, "text": "QLB-czas2", "label": "QTL"},
  {"start": 212, "end": 221, "text": "QLB-czas8", "label": "QTL"},
  {"start": 265, "end": 290, "text": "Bulked segregant analysis", "label": "BM"},
  {"start": 295, "end": 309, "text": "RNA sequencing", "label": "BM"},
  {"start": 321, "end": 325, "text": "SNPs", "label": "MRK"}
]
```

> [新增] `Bulked segregant analysis` @265:290 BM；[新增] `RNA sequencing` @295:309 BM；[新增] `SNPs` @321:325 MRK

### relations（修订后完整列表）

```json
[
  {"head": "Yugu 5", "head_start": 92, "head_end": 98, "head_type": "VAR",
   "tail": "QLB-czas1", "tail_start": 11, "tail_end": 20, "tail_type": "QTL", "label": "CON"},
  {"head": "Yugu 5", "head_start": 92, "head_end": 98, "head_type": "VAR",
   "tail": "QLB-czas2", "tail_start": 22, "tail_end": 31, "tail_type": "QTL", "label": "CON"},
  {"head": "Yugu 5", "head_start": 92, "head_end": 98, "head_type": "VAR",
   "tail": "QLB-czas8", "tail_start": 37, "tail_end": 46, "tail_type": "QTL", "label": "CON"},
  {"head": "QLB-czas1", "head_start": 11, "head_end": 20, "head_type": "QTL",
   "tail": "chromosomes 1, 2, and 8", "tail_start": 65, "tail_end": 88, "tail_type": "CHR", "label": "LOI"},
  {"head": "QLB-czas2", "head_start": 22, "head_end": 31, "head_type": "QTL",
   "tail": "chromosomes 1, 2, and 8", "tail_start": 65, "tail_end": 88, "tail_type": "CHR", "label": "LOI"},
  {"head": "QLB-czas8", "head_start": 37, "head_end": 46, "head_type": "QTL",
   "tail": "chromosomes 1, 2, and 8", "tail_start": 65, "tail_end": 88, "tail_type": "CHR", "label": "LOI"},
  {"head": "SNPs", "head_start": 321, "head_end": 325, "head_type": "MRK",
   "tail": "QLB-czas8", "tail_start": 212, "tail_end": 221, "tail_type": "QTL", "label": "LOI"}
]
```

> [新增] LOI(QLB-czas1/2/8, CHR) ×3；[新增] LOI(SNPs, QLB-czas8)

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增实体 | `PCR-based markers` MRK |
| 1 | 修改边界 | `VrKNAT7 sequence`→`VrKNAT7` |
| 1 | 修改标签 | `ACC41` GENE→VAR；`KPS2` GENE→VAR |
| 1 | 删除实体 | `KNOX II` GENE |
| 2 | 新增实体 | `F-3 lines` CROSS |
| 2 | 修改标签 | `BSR` @120 ABS→BIS |
| 2 | 删除实体 | `BSR` @183 BIS；`primer sets` MRK；`fragments` MRK |
| 2 | 删除关系 | CON(AFLP, primer sets)；CON(AFLP, fragments) |
| 3 | 新增实体 | `phenotypic changes` TRT |
| 4 | 新增实体 | `Abiotic stress` ABS；`growth` TRT；`yield` TRT；`abiotic stresses` ABS；`SbPLD` GENE；`sorghum` @153 CROP |
| 4 | 新增关系 | AFF×2；HAS×2 |
| 5 | 新增实体 | `yields` TRT |
| 5 | 新增关系 | HAS(Qing1, yields)；HAS(Long4, yields)；HAS(Long4, CAT) |
| 6 | 新增实体 | `flowering` TRT；`leaf area` TRT |
| 6 | 修改实体 | 拆分 `greenness and stomatal density` → `greenness` + `stomatal density` |
| 6 | 新增关系 | LOI×6；USE(sorghum, marker assisted selection) |
| 7 | 新增实体 | `seed germination` GST |
| 7 | 新增关系 | OCI(24-h germination rate, seed germination) |
| 8 | 新增实体 | `phenotypic diversity` TRT |
| 8 | 新增关系 | HAS(Sorghum, phenotypic diversity) |
| 9 | 新增实体 | `Bulked segregant analysis` BM；`RNA sequencing` BM；`SNPs` MRK |
| 9 | 新增关系 | LOI×4 |
