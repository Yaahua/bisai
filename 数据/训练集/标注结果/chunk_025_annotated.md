# chunk_025 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`13,920 were up-regulated and 12,808 down-regulated in faba bean drought-stressed leaves. 2130 transcription factors in abscisic acid-dependent and independent signaling pathways were identified.`

**分析**：
- `faba bean`（@54:63）CROP 正确。
- `drought-stressed`（@64:80）标为 ABS，但 "drought-stressed" 是形容词修饰词，不是独立的胁迫实体。应改为 `drought`（@64:71）ABS，或删除。依据 K1 §1.3，标注应为完整名词短语，`drought-stressed` 是形容词，删除，改为标注 `drought stress`（@64:80 中的 "drought-stressed leaves" 不含独立胁迫词）。
- 漏标：`abscisic acid`（@107:120）是植物激素，可标为 ABS（非生物胁迫信号分子）。验证：text[107:120]="abscisic acid" ✓

### entities（修订后完整列表）

```json
[
  {"start": 54,  "end": 63,  "text": "faba bean", "label": "CROP"},
  {"start": 107, "end": 120, "text": "abscisic acid", "label": "ABS"}
]
```

> [删除] `drought-stressed` @64:80 ABS（形容词，非独立胁迫实体）；[新增] `abscisic acid` @107:120 ABS

### relations（修订后完整列表）

```json
[]
```

---

## 样本 1

**原文**：`Linkage analysis identified 21 QTL for GPC and GFC across six environments, including six major stable QTL, 72 combined QTL, and 54 epistatic QTL pairs. Association analysis showed significant differences in GPC or GFC among RILs with different genotypes for the six major stable QTL.`

**分析**：
- 所有实体正确：QTL×4（QTL @31:34、six major stable QTL @86:106、72 combined QTL @108:123、54 epistatic QTL pairs @129:151）；TRT×2（GPC @39:42、GFC @47:50）。
- 漏标：`Linkage analysis`（@0:16）是遗传分析方法，应标为 BM。验证：text[0:16]="Linkage analysis" ✓
- 漏标：`Association analysis`（@158:178）是遗传分析方法，应标为 BM。验证：text[158:178]="Association analysis" ✓
- 漏标：`21 QTL`（@27:34）整体是 QTL 集合，但 "21 QTL" 与 "QTL"（@31:34）重叠，保留 "QTL"（@31:34）。
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 16,  "text": "Linkage analysis", "label": "BM"},
  {"start": 31,  "end": 34,  "text": "QTL", "label": "QTL"},
  {"start": 39,  "end": 42,  "text": "GPC", "label": "TRT"},
  {"start": 47,  "end": 50,  "text": "GFC", "label": "TRT"},
  {"start": 86,  "end": 106, "text": "six major stable QTL", "label": "QTL"},
  {"start": 108, "end": 123, "text": "72 combined QTL", "label": "QTL"},
  {"start": 129, "end": 151, "text": "54 epistatic QTL pairs", "label": "QTL"},
  {"start": 158, "end": 178, "text": "Association analysis", "label": "BM"}
]
```

> [新增] `Linkage analysis` @0:16 BM；[新增] `Association analysis` @158:178 BM

### relations（修订后完整列表）

```json
[
  {"head": "QTL", "head_start": 31, "head_end": 34, "head_type": "QTL",
   "tail": "GPC", "tail_start": 39, "tail_end": 42, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTL", "head_start": 31, "head_end": 34, "head_type": "QTL",
   "tail": "GFC", "tail_start": 47, "tail_end": 50, "tail_type": "TRT", "label": "LOI"},
  {"head": "six major stable QTL", "head_start": 86, "head_end": 106, "head_type": "QTL",
   "tail": "GPC", "tail_start": 39, "tail_end": 42, "tail_type": "TRT", "label": "LOI"},
  {"head": "six major stable QTL", "head_start": 86, "head_end": 106, "head_type": "QTL",
   "tail": "GFC", "tail_start": 47, "tail_end": 50, "tail_type": "TRT", "label": "LOI"},
  {"head": "72 combined QTL", "head_start": 108, "head_end": 123, "head_type": "QTL",
   "tail": "GPC", "tail_start": 39, "tail_end": 42, "tail_type": "TRT", "label": "LOI"},
  {"head": "72 combined QTL", "head_start": 108, "head_end": 123, "head_type": "QTL",
   "tail": "GFC", "tail_start": 47, "tail_end": 50, "tail_type": "TRT", "label": "LOI"},
  {"head": "54 epistatic QTL pairs", "head_start": 129, "head_end": 151, "head_type": "QTL",
   "tail": "GPC", "tail_start": 39, "tail_end": 42, "tail_type": "TRT", "label": "LOI"},
  {"head": "54 epistatic QTL pairs", "head_start": 129, "head_end": 151, "head_type": "QTL",
   "tail": "GFC", "tail_start": 47, "tail_end": 50, "tail_type": "TRT", "label": "LOI"}
]
```

---

## 样本 2

**原文**：`Compared to WT, transgenic Arabidopsis overexpressing FtMYB13 had lower ABA sensitivity and improved drought/salt tolerance. This was attributed to higher proline content, greater photosynthetic efficiency, higher transcript abundance of stress-related genes, and smaller amounts of ROS and MDA in transgenic lines. FtMYB13 is involved in mediating plant responses to ABA, salt, and drought.`

**分析**：
- 所有实体正确：CROP（Arabidopsis）、GENE（FtMYB13）、TRT×7（ABA sensitivity、drought/salt tolerance、proline content、photosynthetic efficiency、transcript abundance of stress-related genes、ROS、MDA）、ABS×2（salt @373:377、drought @383:390）。
- 漏标：`ABA`（@363:366）是脱落酸，应标为 ABS。验证：text[363:366]="ABA" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 27,  "end": 38,  "text": "Arabidopsis", "label": "CROP"},
  {"start": 54,  "end": 61,  "text": "FtMYB13", "label": "GENE"},
  {"start": 72,  "end": 87,  "text": "ABA sensitivity", "label": "TRT"},
  {"start": 101, "end": 123, "text": "drought/salt tolerance", "label": "TRT"},
  {"start": 155, "end": 170, "text": "proline content", "label": "TRT"},
  {"start": 180, "end": 205, "text": "photosynthetic efficiency", "label": "TRT"},
  {"start": 214, "end": 258, "text": "transcript abundance of stress-related genes", "label": "TRT"},
  {"start": 283, "end": 286, "text": "ROS", "label": "TRT"},
  {"start": 291, "end": 294, "text": "MDA", "label": "TRT"},
  {"start": 363, "end": 366, "text": "ABA", "label": "ABS"},
  {"start": 373, "end": 377, "text": "salt", "label": "ABS"},
  {"start": 383, "end": 390, "text": "drought", "label": "ABS"}
]
```

> [新增] `ABA` @363:366 ABS

### relations（修订后完整列表）

```json
[
  {"head": "Arabidopsis", "head_start": 27, "head_end": 38, "head_type": "CROP",
   "tail": "FtMYB13", "tail_start": 54, "tail_end": 61, "tail_type": "GENE", "label": "CON"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "ABA sensitivity", "tail_start": 72, "tail_end": 87, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "drought/salt tolerance", "tail_start": 101, "tail_end": 123, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "proline content", "tail_start": 155, "tail_end": 170, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "photosynthetic efficiency", "tail_start": 180, "tail_end": 205, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "transcript abundance of stress-related genes", "tail_start": 214, "tail_end": 258, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "ROS", "tail_start": 283, "tail_end": 286, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtMYB13", "head_start": 54, "head_end": 61, "head_type": "GENE",
   "tail": "MDA", "tail_start": 291, "tail_end": 294, "tail_type": "TRT", "label": "AFF"},
  {"head": "salt", "head_start": 373, "head_end": 377, "head_type": "ABS",
   "tail": "drought/salt tolerance", "tail_start": 101, "tail_end": 123, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought", "head_start": 383, "head_end": 390, "head_type": "ABS",
   "tail": "drought/salt tolerance", "tail_start": 101, "tail_end": 123, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 3

**原文**：`A QTL-seq analysis was conducted to identify genomic regions regulating days to heading (DTH). The analysis used an F2 population derived from crosses between the middle-heading cultivar Shinanotsubuhime and the early heading cultivar Yuikogane. Under field conditions, transgressive segregation of DTH toward late heading was observed in the F2 population.`

**分析**：
- `QTL-seq analysis`（@2:18）BM 正确。
- `days to heading`（@72:87）TRT 正确。
- `DTH`（@89:92）TRT 正确（与 days to heading 同义缩写）。
- `F2 population`（@116:129、@343:356）CROSS 正确。
- `crosses between the middle-heading cultivar Shinanotsubuhime and the early heading cultivar Yuikogane`（@143:244）CROSS 正确。
- `middle-heading cultivar Shinanotsubuhime`（@163:203）VAR 正确，但边界包含 "middle-heading cultivar" 描述词，应缩减为 `Shinanotsubuhime`（@187:203）。验证：text[187:203]="Shinanotsubuhime" ✓
- `early heading cultivar Yuikogane`（@212:244）VAR 正确，但边界包含 "early heading cultivar" 描述词，应缩减为 `Yuikogane`（@235:244）。验证：text[235:244]="Yuikogane" ✓
- `field conditions`（@252:268）标为 ABS，但 "field conditions" 是试验环境，不是具体胁迫因子，应删除。
- `transgressive segregation of DTH toward late heading`（@270:322）TRT 正确（超亲分离是性状表现）。
- `late heading`（@310:322）标为 GST，但 "late heading" 是生育阶段/性状，应标为 TRT（与 days to heading 相关）。
- 关系：USE(QTL-seq analysis, F2 population) 正确；CON 关系正确；OCI(transgressive segregation, late heading) 正确；AFF(field conditions, transgressive segregation) 因 field conditions 删除，需删除。

### entities（修订后完整列表）

```json
[
  {"start": 2,   "end": 18,  "text": "QTL-seq analysis", "label": "BM"},
  {"start": 72,  "end": 87,  "text": "days to heading", "label": "TRT"},
  {"start": 89,  "end": 92,  "text": "DTH", "label": "TRT"},
  {"start": 116, "end": 129, "text": "F2 population", "label": "CROSS"},
  {"start": 143, "end": 244, "text": "crosses between the middle-heading cultivar Shinanotsubuhime and the early heading cultivar Yuikogane", "label": "CROSS"},
  {"start": 187, "end": 203, "text": "Shinanotsubuhime", "label": "VAR"},
  {"start": 235, "end": 244, "text": "Yuikogane", "label": "VAR"},
  {"start": 270, "end": 322, "text": "transgressive segregation of DTH toward late heading", "label": "TRT"},
  {"start": 310, "end": 322, "text": "late heading", "label": "TRT"},
  {"start": 343, "end": 356, "text": "F2 population", "label": "CROSS"}
]
```

> [修改] `middle-heading cultivar Shinanotsubuhime` @163:203 → `Shinanotsubuhime` @187:203；[修改] `early heading cultivar Yuikogane` @212:244 → `Yuikogane` @235:244；[删除] `field conditions` @252:268 ABS；[修改] `late heading` GST→TRT

### relations（修订后完整列表）

```json
[
  {"head": "QTL-seq analysis", "head_start": 2, "head_end": 18, "head_type": "BM",
   "tail": "F2 population", "tail_start": 116, "tail_end": 129, "tail_type": "CROSS", "label": "USE"},
  {"head": "F2 population", "head_start": 116, "head_end": 129, "head_type": "CROSS",
   "tail": "crosses between the middle-heading cultivar Shinanotsubuhime and the early heading cultivar Yuikogane", "tail_start": 143, "tail_end": 244, "tail_type": "CROSS", "label": "CON"},
  {"head": "crosses between the middle-heading cultivar Shinanotsubuhime and the early heading cultivar Yuikogane", "head_start": 143, "head_end": 244, "head_type": "CROSS",
   "tail": "Shinanotsubuhime", "tail_start": 187, "tail_end": 203, "tail_type": "VAR", "label": "CON"},
  {"head": "crosses between the middle-heading cultivar Shinanotsubuhime and the early heading cultivar Yuikogane", "head_start": 143, "head_end": 244, "head_type": "CROSS",
   "tail": "Yuikogane", "tail_start": 235, "tail_end": 244, "tail_type": "VAR", "label": "CON"},
  {"head": "transgressive segregation of DTH toward late heading", "head_start": 270, "head_end": 322, "head_type": "TRT",
   "tail": "late heading", "tail_start": 310, "tail_end": 322, "tail_type": "TRT", "label": "OCI"}
]
```

> [删除] AFF(field conditions, transgressive segregation)（因 field conditions 实体删除）

---

## 样本 4

**原文**：`Genome-wide association analysis detected four markers highly associated with hullessness. Three were mapped on linkage group Mrg21 between 195.7 and 212.1 cM, indicating the dominantN1 locus on Mrg21 is the major factor controlling this trait.`

**分析**：
- `markers`（@47:54）MRK 正确。
- `hullessness`（@78:89）TRT 正确。
- `linkage group Mrg21`（@112:131）CHR 正确。
- `dominantN1`（@175:185）QTL 正确。
- `Mrg21`（@195:200）CHR 正确。
- 漏标：`Genome-wide association analysis`（@0:32）是遗传分析方法，应标为 BM。验证：text[0:32]="Genome-wide association analysis" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 32,  "text": "Genome-wide association analysis", "label": "BM"},
  {"start": 47,  "end": 54,  "text": "markers", "label": "MRK"},
  {"start": 78,  "end": 89,  "text": "hullessness", "label": "TRT"},
  {"start": 112, "end": 131, "text": "linkage group Mrg21", "label": "CHR"},
  {"start": 175, "end": 185, "text": "dominantN1", "label": "QTL"},
  {"start": 195, "end": 200, "text": "Mrg21", "label": "CHR"}
]
```

> [新增] `Genome-wide association analysis` @0:32 BM

### relations（修订后完整列表）

```json
[
  {"head": "markers", "head_start": 47, "head_end": 54, "head_type": "MRK",
   "tail": "hullessness", "tail_start": 78, "tail_end": 89, "tail_type": "TRT", "label": "LOI"},
  {"head": "markers", "head_start": 47, "head_end": 54, "head_type": "MRK",
   "tail": "linkage group Mrg21", "tail_start": 112, "tail_end": 131, "tail_type": "CHR", "label": "LOI"},
  {"head": "dominantN1", "head_start": 175, "head_end": 185, "head_type": "QTL",
   "tail": "hullessness", "tail_start": 78, "tail_end": 89, "tail_type": "TRT", "label": "LOI"},
  {"head": "dominantN1", "head_start": 175, "head_end": 185, "head_type": "QTL",
   "tail": "Mrg21", "tail_start": 195, "tail_end": 200, "tail_type": "CHR", "label": "LOI"}
]
```

---

## 样本 5

**原文**：`A major effect marker (Chr1_61095994) explained the highest variance proportion (R-2 = 27-31%) in most evaluated traits. It was in linkage disequilibrium with a hotspot of 19 putative glutathione S-transferase genes. On chromosome four, a hotspot region involved major effect markers linked with putative MYB-bHLH-WD40 complex genes.`

**分析**：
- `chromosome four`（@220:235）CHR 正确。
- 漏标：`Chr1_61095994`（@23:36）是分子标记，应标为 MRK。验证：text[23:36]="Chr1_61095994" ✓
- 漏标：`glutathione S-transferase`（@177:201）是基因家族，应标为 GENE。验证：text[177:201]="glutathione S-transferase" ✓
- 漏标：`MYB-bHLH-WD40 complex`（@305:327）是转录因子复合体，应标为 GENE。验证：text[305:327]="MYB-bHLH-WD40 complex" ✓

### entities（修订后完整列表）

```json
[
  {"start": 23,  "end": 36,  "text": "Chr1_61095994", "label": "MRK"},
  {"start": 177, "end": 201, "text": "glutathione S-transferase", "label": "GENE"},
  {"start": 220, "end": 235, "text": "chromosome four", "label": "CHR"},
  {"start": 305, "end": 327, "text": "MYB-bHLH-WD40 complex", "label": "GENE"}
]
```

> [新增] `Chr1_61095994` @23:36 MRK；[新增] `glutathione S-transferase` @177:201 GENE；[新增] `MYB-bHLH-WD40 complex` @305:327 GENE

### relations（修订后完整列表）

```json
[
  {"head": "Chr1_61095994", "head_start": 23, "head_end": 36, "head_type": "MRK",
   "tail": "chromosome four", "tail_start": 220, "tail_end": 235, "tail_type": "CHR", "label": "LOI"}
]
```

> [新增] LOI(Chr1_61095994, chromosome four)

---

## 样本 6

**原文**：`Elevated expression of Chalk5 increases endosperm chalkiness. Two consensus nucleotide polymorphisms in the Chalk5 promoter in rice varieties might partly account for differences in Chalk5 mRNA levels that contribute to natural variation in grain chalkiness.`

**分析**：
- `endosperm chalkiness`（@40:60）TRT 正确。
- `Chalk5`（@108:114）GENE 正确。
- `rice`（@127:131）CROP 正确。
- `Chalk5 mRNA levels`（@182:200）TRT 正确。
- `grain chalkiness`（@241:257）TRT 正确。
- 漏标：`Chalk5`（@23:29）第一次出现，应标为 GENE。验证：text[23:29]="Chalk5" ✓
- 漏标：`Chalk5`（@182:188）在 "Chalk5 mRNA levels" 中，已被整体标注包含，不单独标。
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 23,  "end": 29,  "text": "Chalk5", "label": "GENE"},
  {"start": 40,  "end": 60,  "text": "endosperm chalkiness", "label": "TRT"},
  {"start": 108, "end": 114, "text": "Chalk5", "label": "GENE"},
  {"start": 127, "end": 131, "text": "rice", "label": "CROP"},
  {"start": 182, "end": 200, "text": "Chalk5 mRNA levels", "label": "TRT"},
  {"start": 241, "end": 257, "text": "grain chalkiness", "label": "TRT"}
]
```

> [新增] `Chalk5` @23:29 GENE

### relations（修订后完整列表）

```json
[
  {"head": "rice", "head_start": 127, "head_end": 131, "head_type": "CROP",
   "tail": "grain chalkiness", "tail_start": 241, "tail_end": 257, "tail_type": "TRT", "label": "HAS"},
  {"head": "Chalk5", "head_start": 108, "head_end": 114, "head_type": "GENE",
   "tail": "Chalk5 mRNA levels", "tail_start": 182, "tail_end": 200, "tail_type": "TRT", "label": "AFF"},
  {"head": "Chalk5", "head_start": 108, "head_end": 114, "head_type": "GENE",
   "tail": "endosperm chalkiness", "tail_start": 40, "tail_end": 60, "tail_type": "TRT", "label": "AFF"},
  {"head": "Chalk5 mRNA levels", "head_start": 182, "head_end": 200, "head_type": "TRT",
   "tail": "grain chalkiness", "tail_start": 241, "tail_end": 257, "tail_type": "TRT", "label": "AFF"},
  {"head": "Chalk5", "head_start": 23, "head_end": 29, "head_type": "GENE",
   "tail": "endosperm chalkiness", "tail_start": 40, "tail_end": 60, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(Chalk5 @23:29, endosperm chalkiness)

---

## 样本 7

**原文**：`VfAP2-1 and VfERF-99 enhance pathogen resistance. They positively influence ROS homeostasis, accumulating H2O2 and O2- under abiotic and biotic stresses, inhibiting pathogen colonization.`

**分析**：
- `VfAP2-1`（@0:7）GENE 正确。
- `VfERF-99`（@12:20）GENE 正确。
- `pathogen resistance`（@29:48）TRT 正确。
- `ROS homeostasis`（@76:91）TRT 正确。
- `H2O2`（@106:110）TRT 正确（活性氧含量是可量化性状）。
- `O2-`（@115:118）TRT 正确。
- `abiotic`（@125:132）标为 ABS，但 "abiotic" 是形容词，不是独立胁迫实体，应删除。
- `biotic stresses`（@137:152）BIS 正确。
- `pathogen colonization`（@165:186）BIS 正确。
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 7,   "text": "VfAP2-1", "label": "GENE"},
  {"start": 12,  "end": 20,  "text": "VfERF-99", "label": "GENE"},
  {"start": 29,  "end": 48,  "text": "pathogen resistance", "label": "TRT"},
  {"start": 76,  "end": 91,  "text": "ROS homeostasis", "label": "TRT"},
  {"start": 106, "end": 110, "text": "H2O2", "label": "TRT"},
  {"start": 115, "end": 118, "text": "O2-", "label": "TRT"},
  {"start": 137, "end": 152, "text": "biotic stresses", "label": "BIS"},
  {"start": 165, "end": 186, "text": "pathogen colonization", "label": "BIS"}
]
```

> [删除] `abiotic` @125:132 ABS（形容词，非独立胁迫实体）

### relations（修订后完整列表）

```json
[
  {"head": "VfAP2-1", "head_start": 0, "head_end": 7, "head_type": "GENE",
   "tail": "pathogen resistance", "tail_start": 29, "tail_end": 48, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfAP2-1", "head_start": 0, "head_end": 7, "head_type": "GENE",
   "tail": "ROS homeostasis", "tail_start": 76, "tail_end": 91, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfERF-99", "head_start": 12, "head_end": 20, "head_type": "GENE",
   "tail": "pathogen resistance", "tail_start": 29, "tail_end": 48, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfERF-99", "head_start": 12, "head_end": 20, "head_type": "GENE",
   "tail": "ROS homeostasis", "tail_start": 76, "tail_end": 91, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfAP2-1", "head_start": 0, "head_end": 7, "head_type": "GENE",
   "tail": "H2O2", "tail_start": 106, "tail_end": 110, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfAP2-1", "head_start": 0, "head_end": 7, "head_type": "GENE",
   "tail": "O2-", "tail_start": 115, "tail_end": 118, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfERF-99", "head_start": 12, "head_end": 20, "head_type": "GENE",
   "tail": "H2O2", "tail_start": 106, "tail_end": 110, "tail_type": "TRT", "label": "AFF"},
  {"head": "VfERF-99", "head_start": 12, "head_end": 20, "head_type": "GENE",
   "tail": "O2-", "tail_start": 115, "tail_end": 118, "tail_type": "TRT", "label": "AFF"},
  {"head": "biotic stresses", "head_start": 137, "head_end": 152, "head_type": "BIS",
   "tail": "ROS homeostasis", "tail_start": 76, "tail_end": 91, "tail_type": "TRT", "label": "AFF"},
  {"head": "pathogen colonization", "head_start": 165, "head_end": 186, "head_type": "BIS",
   "tail": "ROS homeostasis", "tail_start": 76, "tail_end": 91, "tail_type": "TRT", "label": "AFF"}
]
```

> [删除] AFF(abiotic, ROS homeostasis)（因 abiotic 实体删除）

---

## 样本 8

**原文**：`The Ethiopian sorghum germplasm has extensive genetic diversity across traits. The genetic basis of seedling traits is unexplored. Understanding this is vital for developing drought-resistant sorghum cultivars.`

**分析**：
- 原始数据无任何实体和关系。
- 漏标：`sorghum`（@14:21）CROP。验证：text[14:21]="sorghum" ✓
- 漏标：`genetic diversity`（@45:61）是遗传多样性性状，应标为 TRT。验证：text[45:61]="genetic diversity" ✓
- 漏标：`sorghum`（@189:196）第二次出现，应标为 CROP。验证：text[189:196]="sorghum" ✓

### entities（修订后完整列表）

```json
[
  {"start": 14,  "end": 21,  "text": "sorghum", "label": "CROP"},
  {"start": 45,  "end": 61,  "text": "genetic diversity", "label": "TRT"},
  {"start": 189, "end": 196, "text": "sorghum", "label": "CROP"}
]
```

> [新增] `sorghum` @14:21 CROP；[新增] `genetic diversity` @45:61 TRT；[新增] `sorghum` @189:196 CROP

### relations（修订后完整列表）

```json
[
  {"head": "sorghum", "head_start": 14, "head_end": 21, "head_type": "CROP",
   "tail": "genetic diversity", "tail_start": 45, "tail_end": 61, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] HAS(sorghum, genetic diversity)

---

## 样本 9

**原文**：`Under drought stress, the maximal photochemical efficiency of PSII (F-v/F-m) and oxidoreductive activity (Delta I/I-0) decreased more in Roma than in M-81E. The Delta I/I0 decreased more markedly than Fv/Fm, indicating PSI was more sensitive to drought stress than PSII.`

**分析**：
- `drought stress`（@6:20、@245:259）ABS 正确。
- `maximal photochemical efficiency of PSII (F-v/F-m)`（@26:76）TRT 正确。
- `PSII`（@62:66）标为 TRT，但 PSII（光系统 II）是蛋白质复合体，应标为 GENE。
- `F-v/F-m`（@68:75）TRT 正确（光合参数）。
- `oxidoreductive activity (Delta I/I-0)`（@81:118）TRT 正确。
- `Delta I/I-0`（@106:117）TRT 正确（与整体标注嵌套共存）。
- `M-81E`（@150:155）VAR 正确。
- `Delta I/I0`（@161:171）TRT 正确。
- `Fv/Fm`（@201:206）TRT 正确。
- `PSI`（@219:222）标为 TRT，但 PSI（光系统 I）是蛋白质复合体，应标为 GENE。
- `PSII`（@265:269）标为 TRT，应标为 GENE。
- 漏标：`Roma`（@143:147）是品种名，应标为 VAR。验证：text[143:147]="Roma" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 6,   "end": 20,  "text": "drought stress", "label": "ABS"},
  {"start": 26,  "end": 76,  "text": "maximal photochemical efficiency of PSII (F-v/F-m)", "label": "TRT"},
  {"start": 62,  "end": 66,  "text": "PSII", "label": "GENE"},
  {"start": 68,  "end": 75,  "text": "F-v/F-m", "label": "TRT"},
  {"start": 81,  "end": 118, "text": "oxidoreductive activity (Delta I/I-0)", "label": "TRT"},
  {"start": 106, "end": 117, "text": "Delta I/I-0", "label": "TRT"},
  {"start": 143, "end": 147, "text": "Roma", "label": "VAR"},
  {"start": 150, "end": 155, "text": "M-81E", "label": "VAR"},
  {"start": 161, "end": 171, "text": "Delta I/I0", "label": "TRT"},
  {"start": 201, "end": 206, "text": "Fv/Fm", "label": "TRT"},
  {"start": 219, "end": 222, "text": "PSI", "label": "GENE"},
  {"start": 245, "end": 259, "text": "drought stress", "label": "ABS"},
  {"start": 265, "end": 269, "text": "PSII", "label": "GENE"}
]
```

> [修改] `PSII` @62:66 TRT→GENE；[修改] `PSI` @219:222 TRT→GENE；[修改] `PSII` @265:269 TRT→GENE；[新增] `Roma` @143:147 VAR

### relations（修订后完整列表）

```json
[
  {"head": "drought stress", "head_start": 6, "head_end": 20, "head_type": "ABS",
   "tail": "maximal photochemical efficiency of PSII (F-v/F-m)", "tail_start": 26, "tail_end": 76, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought stress", "head_start": 6, "head_end": 20, "head_type": "ABS",
   "tail": "F-v/F-m", "tail_start": 68, "tail_end": 75, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought stress", "head_start": 6, "head_end": 20, "head_type": "ABS",
   "tail": "oxidoreductive activity (Delta I/I-0)", "tail_start": 81, "tail_end": 118, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought stress", "head_start": 6, "head_end": 20, "head_type": "ABS",
   "tail": "Delta I/I-0", "tail_start": 106, "tail_end": 117, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 删除实体 | `drought-stressed` @64:80 ABS |
| 0 | 新增实体 | `abscisic acid` @107:120 ABS |
| 1 | 新增实体 | `Linkage analysis` BM；`Association analysis` BM |
| 2 | 新增实体 | `ABA` @363:366 ABS |
| 3 | 修改边界 | `middle-heading cultivar Shinanotsubuhime` → `Shinanotsubuhime` @187:203 |
| 3 | 修改边界 | `early heading cultivar Yuikogane` → `Yuikogane` @235:244 |
| 3 | 删除实体 | `field conditions` @252:268 ABS |
| 3 | 修改标签 | `late heading` GST→TRT |
| 3 | 删除关系 | AFF(field conditions, transgressive segregation) |
| 4 | 新增实体 | `Genome-wide association analysis` @0:32 BM |
| 5 | 新增实体 | `Chr1_61095994` MRK；`glutathione S-transferase` GENE；`MYB-bHLH-WD40 complex` GENE |
| 5 | 新增关系 | LOI(Chr1_61095994, chromosome four) |
| 6 | 新增实体 | `Chalk5` @23:29 GENE |
| 6 | 新增关系 | AFF(Chalk5 @23:29, endosperm chalkiness) |
| 7 | 删除实体 | `abiotic` @125:132 ABS |
| 7 | 删除关系 | AFF(abiotic, ROS homeostasis) |
| 8 | 新增实体 | `sorghum` CROP ×2；`genetic diversity` TRT |
| 8 | 新增关系 | HAS(sorghum, genetic diversity) |
| 9 | 修改标签 | `PSII` @62:66 TRT→GENE；`PSI` @219:222 TRT→GENE；`PSII` @265:269 TRT→GENE |
| 9 | 新增实体 | `Roma` @143:147 VAR |
