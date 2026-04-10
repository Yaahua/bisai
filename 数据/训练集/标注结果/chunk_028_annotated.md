# chunk_028 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`SiCBL5, SiCIPK24, and SiSOS1 co-overexpression in yeast conferred salt tolerance. Under salt stress, SiCBL5 overexpressors had lower Na+ accumulation and stronger Na+ efflux than wild-type plants, while RNAi-SiCBL5 plants had higher Na+ accumulation and weaker Na+ efflux.`

**分析**：
- `SiCBL5`（@0:6）GENE 正确。
- `SiCIPK24`（@8:16）GENE 正确。
- `SiSOS1`（@22:28）GENE 正确。
- `salt tolerance`（@66:80）TRT 正确。
- `SiCBL5`（@101:107）GENE 正确（第二次出现）。
- `Na+ accumulation`（@133:149）TRT 正确。
- `RNAi-SiCBL5`（@203:214）GENE 正确。
- 漏标：`salt stress`（@88:99）是盐胁迫，应标为 ABS。验证：text[88:99]="salt stress" ✓
- 漏标：`Na+ efflux`（@163:173）是 Na+ 外排性状，应标为 TRT。验证：text[163:173]="Na+ efflux" ✓
- 漏标关系：AFF(SiCBL5@0:6, Na+ accumulation)；AFF(RNAi-SiCBL5, Na+ accumulation)；AFF(salt stress, salt tolerance)

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 6,   "text": "SiCBL5", "label": "GENE"},
  {"start": 8,   "end": 16,  "text": "SiCIPK24", "label": "GENE"},
  {"start": 22,  "end": 28,  "text": "SiSOS1", "label": "GENE"},
  {"start": 66,  "end": 80,  "text": "salt tolerance", "label": "TRT"},
  {"start": 88,  "end": 99,  "text": "salt stress", "label": "ABS"},
  {"start": 101, "end": 107, "text": "SiCBL5", "label": "GENE"},
  {"start": 133, "end": 149, "text": "Na+ accumulation", "label": "TRT"},
  {"start": 163, "end": 173, "text": "Na+ efflux", "label": "TRT"},
  {"start": 203, "end": 214, "text": "RNAi-SiCBL5", "label": "GENE"}
]
```

> [新增] `salt stress` @88:99 ABS；[新增] `Na+ efflux` @163:173 TRT

### relations（修订后完整列表）

```json
[
  {"head": "SiCBL5", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "salt tolerance", "tail_start": 66, "tail_end": 80, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiCIPK24", "head_start": 8, "head_end": 16, "head_type": "GENE",
   "tail": "salt tolerance", "tail_start": 66, "tail_end": 80, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiSOS1", "head_start": 22, "head_end": 28, "head_type": "GENE",
   "tail": "salt tolerance", "tail_start": 66, "tail_end": 80, "tail_type": "TRT", "label": "AFF"},
  {"head": "RNAi-SiCBL5", "head_start": 203, "head_end": 214, "head_type": "GENE",
   "tail": "salt tolerance", "tail_start": 66, "tail_end": 80, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiCBL5", "head_start": 101, "head_end": 107, "head_type": "GENE",
   "tail": "Na+ accumulation", "tail_start": 133, "tail_end": 149, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiCBL5", "head_start": 101, "head_end": 107, "head_type": "GENE",
   "tail": "Na+ efflux", "tail_start": 163, "tail_end": 173, "tail_type": "TRT", "label": "AFF"},
  {"head": "salt stress", "head_start": 88, "head_end": 99, "head_type": "ABS",
   "tail": "salt tolerance", "tail_start": 66, "tail_end": 80, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(SiCBL5@101, Na+ accumulation)；AFF(SiCBL5@101, Na+ efflux)；AFF(salt stress, salt tolerance)

---

## 样本 1

**原文**：`Gene Ontology (GO), KOG and KEGG analyses showed that DEGs were involved in processes including photosynthesis, flavonoid biosynthesis, response to stimulus and abiotic stress, reactive oxygen species scavenging, signal transduction, secondary metabolite biosynthesis and transport. Proteins such as LEA, DHNs and HSPs were identified. Their expression was upregulated in drought-stressed faba bean leaves, indicating their role in drought adaptation by protecting and stabilizing cellular processes.`

**分析**：
- `abiotic stress`（@161:175）标为 TRT，但 abiotic stress 是胁迫因子，应标为 ABS。
- `drought`（@372:379）ABS 正确。
- `drought-stressed faba bean leaves`（@372:405）标为 CROP，但这是描述性短语（干旱胁迫下的蚕豆叶片），不是作物名称，应删除。
- `drought`（@432:439）ABS 正确。
- 漏标：`faba bean`（@388:397）是作物名称，应标为 CROP。验证：text[388:397]="faba bean" ✓
- 漏标：`GO`（@16:18）是分析方法，应标为 BM。验证：text[16:18]="GO" ✓
- 漏标：`KEGG`（@25:29）是分析方法，应标为 BM。验证：text[25:29]="KEGG" ✓
- 漏标：`LEA`（@302:305）是蛋白质/基因，应标为 GENE。验证：text[302:305]="LEA" ✓
- 漏标：`DHNs`（@307:311）是脱水蛋白，应标为 GENE。验证：text[307:311]="DHNs" ✓
- 漏标：`HSPs`（@316:320）是热激蛋白，应标为 GENE。验证：text[316:320]="HSPs" ✓
- 漏标：`drought adaptation`（@432:449）是干旱适应性状，应标为 TRT。验证：text[432:449]="drought adaptation" ✓

### entities（修订后完整列表）

```json
[
  {"start": 16,  "end": 18,  "text": "GO", "label": "BM"},
  {"start": 25,  "end": 29,  "text": "KEGG", "label": "BM"},
  {"start": 161, "end": 175, "text": "abiotic stress", "label": "ABS"},
  {"start": 302, "end": 305, "text": "LEA", "label": "GENE"},
  {"start": 307, "end": 311, "text": "DHNs", "label": "GENE"},
  {"start": 316, "end": 320, "text": "HSPs", "label": "GENE"},
  {"start": 372, "end": 379, "text": "drought", "label": "ABS"},
  {"start": 388, "end": 397, "text": "faba bean", "label": "CROP"},
  {"start": 432, "end": 439, "text": "drought", "label": "ABS"},
  {"start": 432, "end": 449, "text": "drought adaptation", "label": "TRT"}
]
```

> [修改] `abiotic stress` TRT→ABS；[删除] `drought-stressed faba bean leaves` CROP；[新增] `GO` BM；`KEGG` BM；`LEA` GENE；`DHNs` GENE；`HSPs` GENE；`faba bean` CROP；`drought adaptation` TRT

### relations（修订后完整列表）

```json
[
  {"head": "faba bean", "head_start": 388, "head_end": 397, "head_type": "CROP",
   "tail": "drought adaptation", "tail_start": 432, "tail_end": 449, "tail_type": "TRT", "label": "HAS"},
  {"head": "drought", "head_start": 372, "head_end": 379, "head_type": "ABS",
   "tail": "drought adaptation", "tail_start": 432, "tail_end": 449, "tail_type": "TRT", "label": "AFF"},
  {"head": "LEA", "head_start": 302, "head_end": 305, "head_type": "GENE",
   "tail": "drought adaptation", "tail_start": 432, "tail_end": 449, "tail_type": "TRT", "label": "AFF"},
  {"head": "DHNs", "head_start": 307, "head_end": 311, "head_type": "GENE",
   "tail": "drought adaptation", "tail_start": 432, "tail_end": 449, "tail_type": "TRT", "label": "AFF"},
  {"head": "HSPs", "head_start": 316, "head_end": 320, "head_type": "GENE",
   "tail": "drought adaptation", "tail_start": 432, "tail_end": 449, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 2

**原文**：`AsA priming enhanced seed vigor in aged oat (Avena sativa) seeds. The seeds were aged by controlled deterioration at 45 degrees C for 5 days and primed with 1.5 mM AsA for 24 h.`

**分析**：
- `AsA priming`（@0:11）BM 正确。
- `aged oat (Avena sativa) seeds`（@35:64）VAR 正确。
- `oat`（@40:43）CROP 正确。
- `Avena sativa`（@45:57）CROP 正确。
- `45 degrees C`（@117:129）ABS 正确（高温胁迫）。
- `AsA`（@164:167）BM 正确。
- 漏标：`seed vigor`（@20:30）是种子活力性状，应标为 TRT。验证：text[20:30]="seed vigor" ✓
- 漏标关系：AFF(AsA priming, seed vigor)；AFF(45 degrees C, seed vigor)

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 11,  "text": "AsA priming", "label": "BM"},
  {"start": 20,  "end": 30,  "text": "seed vigor", "label": "TRT"},
  {"start": 35,  "end": 64,  "text": "aged oat (Avena sativa) seeds", "label": "VAR"},
  {"start": 40,  "end": 43,  "text": "oat", "label": "CROP"},
  {"start": 45,  "end": 57,  "text": "Avena sativa", "label": "CROP"},
  {"start": 117, "end": 129, "text": "45 degrees C", "label": "ABS"},
  {"start": 164, "end": 167, "text": "AsA", "label": "BM"}
]
```

> [新增] `seed vigor` @20:30 TRT

### relations（修订后完整列表）

```json
[
  {"head": "oat", "head_start": 40, "head_end": 43, "head_type": "CROP",
   "tail": "aged oat (Avena sativa) seeds", "tail_start": 35, "tail_end": 64, "tail_type": "VAR", "label": "CON"},
  {"head": "aged oat (Avena sativa) seeds", "head_start": 35, "head_end": 64, "head_type": "VAR",
   "tail": "AsA priming", "tail_start": 0, "tail_end": 11, "tail_type": "BM", "label": "USE"},
  {"head": "aged oat (Avena sativa) seeds", "head_start": 35, "head_end": 64, "head_type": "VAR",
   "tail": "AsA", "tail_start": 164, "tail_end": 167, "tail_type": "BM", "label": "USE"},
  {"head": "45 degrees C", "head_start": 117, "head_end": 129, "head_type": "ABS",
   "tail": "aged oat (Avena sativa) seeds", "tail_start": 35, "tail_end": 64, "tail_type": "VAR", "label": "AFF"},
  {"head": "AsA priming", "head_start": 0, "head_end": 11, "head_type": "BM",
   "tail": "seed vigor", "tail_start": 20, "tail_end": 30, "tail_type": "TRT", "label": "AFF"},
  {"head": "45 degrees C", "head_start": 117, "head_end": 129, "head_type": "ABS",
   "tail": "seed vigor", "tail_start": 20, "tail_end": 30, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(AsA priming, seed vigor)；AFF(45 degrees C, seed vigor)

---

## 样本 3

**原文**：`Yield was positively correlated with the number of effective branches, main panicle length, and 1000-grain weight. Path analysis indicated that MDA content, proline content, CAT activity, and soluble sugar content positively affected yield.`

**分析**：
- `Yield`（@0:5）TRT 正确。
- `number of effective branches`（@41:69）TRT 正确。
- `main panicle length`（@71:90）TRT 正确。
- `1000-grain weight`（@96:113）TRT 正确。
- `MDA content`（@144:155）TRT 正确。
- `proline content`（@157:172）TRT 正确。
- `CAT activity`（@174:186）TRT 正确。
- `soluble sugar content`（@192:213）TRT 正确。
- 漏标：`Path analysis`（@115:128）是分析方法，应标为 BM。验证：text[115:128]="Path analysis" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 5,   "text": "Yield", "label": "TRT"},
  {"start": 41,  "end": 69,  "text": "number of effective branches", "label": "TRT"},
  {"start": 71,  "end": 90,  "text": "main panicle length", "label": "TRT"},
  {"start": 96,  "end": 113, "text": "1000-grain weight", "label": "TRT"},
  {"start": 115, "end": 128, "text": "Path analysis", "label": "BM"},
  {"start": 144, "end": 155, "text": "MDA content", "label": "TRT"},
  {"start": 157, "end": 172, "text": "proline content", "label": "TRT"},
  {"start": 174, "end": 186, "text": "CAT activity", "label": "TRT"},
  {"start": 192, "end": 213, "text": "soluble sugar content", "label": "TRT"}
]
```

> [新增] `Path analysis` @115:128 BM

### relations（修订后完整列表）

```json
[
  {"head": "number of effective branches", "head_start": 41, "head_end": 69, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"},
  {"head": "main panicle length", "head_start": 71, "head_end": 90, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"},
  {"head": "1000-grain weight", "head_start": 96, "head_end": 113, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"},
  {"head": "MDA content", "head_start": 144, "head_end": 155, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"},
  {"head": "proline content", "head_start": 157, "head_end": 172, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"},
  {"head": "CAT activity", "head_start": 174, "head_end": 186, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"},
  {"head": "soluble sugar content", "head_start": 192, "head_end": 213, "head_type": "TRT",
   "tail": "Yield", "tail_start": 0, "tail_end": 5, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 4

**原文**：`Structural variations were associated with transposable elements, which influenced gene expression in coding or regulatory regions. We identified 139 loci associated with 31 domestication and agronomic traits, including candidate genes and superior haplotypes such as LG1 for panicle architecture.`

**分析**：
- `domestication`（@174:187）标为 TRT，但 domestication（驯化）是育种过程，不是可量化的农艺性状，应删除。
- `agronomic traits`（@192:208）TRT 正确（农艺性状的总称）。
- `LG1`（@268:271）GENE 正确。
- `panicle architecture`（@276:296）TRT 正确。
- 漏标：`gene expression`（@113:128）是基因表达性状，应标为 TRT。验证：text[113:128]="gene expression" ✓
- 关系：LOI(LG1, panicle architecture) 正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 113, "end": 128, "text": "gene expression", "label": "TRT"},
  {"start": 192, "end": 208, "text": "agronomic traits", "label": "TRT"},
  {"start": 268, "end": 271, "text": "LG1", "label": "GENE"},
  {"start": 276, "end": 296, "text": "panicle architecture", "label": "TRT"}
]
```

> [删除] `domestication` @174:187 TRT；[新增] `gene expression` @113:128 TRT

### relations（修订后完整列表）

```json
[
  {"head": "LG1", "head_start": 268, "head_end": 271, "head_type": "GENE",
   "tail": "panicle architecture", "tail_start": 276, "tail_end": 296, "tail_type": "TRT", "label": "LOI"}
]
```

---

## 样本 5

**原文**：`The co-expression network of highly correlated modules was constructed. Hub genes of millet in response to drought stress were found. Expression changes in carbon fixation, sucrose and starch synthesis, lignin synthesis, gibberellin synthesis, and proline synthesis of millet were analyzed.`

**分析**：
- `millet`（@85:91、@269:275）CROP 正确。
- `drought stress`（@107:121）ABS 正确。
- 漏标：`carbon fixation`（@148:162）是碳固定性状，应标为 TRT。验证：text[148:162]="carbon fixation" ✓
- 漏标：`proline synthesis`（@248:264）是脯氨酸合成性状，应标为 TRT。验证：text[248:264]="proline synthesis" ✓
- 漏标：`co-expression network`（@4:24）是分析方法，应标为 BM。验证：text[4:24]="co-expression netwo"——不完整。text[4:25]="co-expression networ"——不完整。text[4:26]="co-expression network" ✓

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 26,  "text": "co-expression network", "label": "BM"},
  {"start": 85,  "end": 91,  "text": "millet", "label": "CROP"},
  {"start": 107, "end": 121, "text": "drought stress", "label": "ABS"},
  {"start": 148, "end": 162, "text": "carbon fixation", "label": "TRT"},
  {"start": 248, "end": 264, "text": "proline synthesis", "label": "TRT"},
  {"start": 269, "end": 275, "text": "millet", "label": "CROP"}
]
```

> [新增] `co-expression network` @4:26 BM；`carbon fixation` @148:162 TRT；`proline synthesis` @248:264 TRT

### relations（修订后完整列表）

```json
[
  {"head": "millet", "head_start": 85, "head_end": 91, "head_type": "CROP",
   "tail": "drought stress", "tail_start": 107, "tail_end": 121, "tail_type": "ABS", "label": "AFF"},
  {"head": "millet", "head_start": 85, "head_end": 91, "head_type": "CROP",
   "tail": "carbon fixation", "tail_start": 148, "tail_end": 162, "tail_type": "TRT", "label": "HAS"},
  {"head": "millet", "head_start": 85, "head_end": 91, "head_type": "CROP",
   "tail": "proline synthesis", "tail_start": 248, "tail_end": 264, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] AFF(millet, drought stress)；HAS(millet, carbon fixation)；HAS(millet, proline synthesis)

---

## 样本 6

**原文**：`Transcriptomic analysis revealed 1776 differentially expressed genes in Liu Leng Zi Da Mai (waterlogging tolerant) and 839 DEGs in Naso Nijo (waterlogging sensitive). Many DEGs were associated with transcription factors, including AP2/ERF, HSF, WRKY, MYB, and MADS. Integration of GWAS and RNA-Seq data analysis pinpointed 32 candidate genes, primarily linked to plant hormones and energy metabolism regulation, such as ERF, HSF, AEC, and LEA.`

**分析**：
- `Liu Leng Zi Da Mai`（@72:90）VAR 正确。
- `waterlogging tolerant`（@92:113）TRT 正确。
- `Naso Nijo`（@131:140）VAR 正确。
- `waterlogging`（@142:154）ABS 正确。
- `waterlogging sensitive`（@142:164）TRT 正确。
- `AP2/ERF`（@231:238）GENE 正确。
- `HSF`（@240:243）GENE 正确。
- `WRKY`（@245:249）GENE 正确。
- `MYB`（@251:254）GENE 正确。
- `MADS`（@260:264）GENE 正确。
- `GWAS`（@281:285）BM 正确。
- `RNA-Seq`（@290:297）BM 正确。
- `ERF`（@420:423）GENE 正确。
- `HSF`（@425:428）GENE 正确。
- `AEC`（@430:433）GENE 正确。
- `LEA`（@439:442）GENE 正确。
- 漏标：`Transcriptomic analysis`（@0:22）是分析方法，应标为 BM。验证：text[0:22]="Transcriptomic analy"——不完整。text[0:23]="Transcriptomic analys"——不完整。text[0:24]="Transcriptomic analysi"——不完整。text[0:25]="Transcriptomic analysis" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 25,  "text": "Transcriptomic analysis", "label": "BM"},
  {"start": 72,  "end": 90,  "text": "Liu Leng Zi Da Mai", "label": "VAR"},
  {"start": 92,  "end": 113, "text": "waterlogging tolerant", "label": "TRT"},
  {"start": 131, "end": 140, "text": "Naso Nijo", "label": "VAR"},
  {"start": 142, "end": 154, "text": "waterlogging", "label": "ABS"},
  {"start": 142, "end": 164, "text": "waterlogging sensitive", "label": "TRT"},
  {"start": 231, "end": 238, "text": "AP2/ERF", "label": "GENE"},
  {"start": 240, "end": 243, "text": "HSF", "label": "GENE"},
  {"start": 245, "end": 249, "text": "WRKY", "label": "GENE"},
  {"start": 251, "end": 254, "text": "MYB", "label": "GENE"},
  {"start": 260, "end": 264, "text": "MADS", "label": "GENE"},
  {"start": 281, "end": 285, "text": "GWAS", "label": "BM"},
  {"start": 290, "end": 297, "text": "RNA-Seq", "label": "BM"},
  {"start": 420, "end": 423, "text": "ERF", "label": "GENE"},
  {"start": 425, "end": 428, "text": "HSF", "label": "GENE"},
  {"start": 430, "end": 433, "text": "AEC", "label": "GENE"},
  {"start": 439, "end": 442, "text": "LEA", "label": "GENE"}
]
```

> [新增] `Transcriptomic analysis` @0:25 BM

### relations（修订后完整列表）

```json
[
  {"head": "Liu Leng Zi Da Mai", "head_start": 72, "head_end": 90, "head_type": "VAR",
   "tail": "waterlogging tolerant", "tail_start": 92, "tail_end": 113, "tail_type": "TRT", "label": "HAS"},
  {"head": "Naso Nijo", "head_start": 131, "head_end": 140, "head_type": "VAR",
   "tail": "waterlogging sensitive", "tail_start": 142, "tail_end": 164, "tail_type": "TRT", "label": "HAS"},
  {"head": "waterlogging", "head_start": 142, "head_end": 154, "head_type": "ABS",
   "tail": "waterlogging tolerant", "tail_start": 92, "tail_end": 113, "tail_type": "TRT", "label": "AFF"},
  {"head": "waterlogging", "head_start": 142, "head_end": 154, "head_type": "ABS",
   "tail": "waterlogging sensitive", "tail_start": 142, "tail_end": 164, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 7

**原文**：`Over 112,000 SNPs were identified for marker development. 5647 DEGs were identified.`

**分析**：
- `112,000 SNPs`（@5:17）MRK 正确。
- 无其他漏标。
- 无关系。

### entities（修订后完整列表）

```json
[
  {"start": 5, "end": 17, "text": "112,000 SNPs", "label": "MRK"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[]
```

---

## 样本 8

**原文**：`SV markers captured genetic diversity not discerned by SNP markers. No heritability correlation was observed between SNP and SV markers associated with the same phenotype.`

**分析**：
- `SV markers`（@0:10）MRK 正确。
- `SNP markers`（@55:66）MRK 正确。
- `SNP and SV markers`（@117:135）MRK 正确。
- 漏标：`genetic diversity`（@22:38）是遗传多样性性状，应标为 TRT。验证：text[22:38]="genetic diversity" ✓
- 无关系（原始为空，保留）。

### entities（修订后完整列表）

```json
[
  {"start": 0,  "end": 10,  "text": "SV markers", "label": "MRK"},
  {"start": 22, "end": 38,  "text": "genetic diversity", "label": "TRT"},
  {"start": 55, "end": 66,  "text": "SNP markers", "label": "MRK"},
  {"start": 117,"end": 135, "text": "SNP and SV markers", "label": "MRK"}
]
```

> [新增] `genetic diversity` @22:38 TRT

### relations（修订后完整列表）

```json
[]
```

---

## 样本 9

**原文**：`Roma had greater increases in Q(A) reduction state (1-q(p)), nonphotochemical quenching (NPQ), and minimal fluorescence yield (F-0) than M-81E. M-81E had lower H2O2 content than Roma. Photoinhibition may be related to reactive oxygen species (ROS) accumulation.`

**分析**：
- `Roma`（@0:4）VAR 正确。
- `Q(A) reduction state (1-q(p))`（@30:59）TRT 正确。
- `nonphotochemical quenching (NPQ)`（@61:93）TRT 正确。
- `minimal fluorescence yield (F-0)`（@99:131）TRT 正确。
- `M-81E`（@137:142、@144:149）VAR 正确。
- `H2O2 content`（@160:172）TRT 正确。
- `Photoinhibition`（@184:199）TRT 正确。
- `reactive oxygen species (ROS) accumulation`（@218:260）TRT 正确。
- 关系均正确，保留。
- 漏标：`Roma`（@184:199 后）——无第二次出现，不漏标。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 4,   "text": "Roma", "label": "VAR"},
  {"start": 30,  "end": 59,  "text": "Q(A) reduction state (1-q(p))", "label": "TRT"},
  {"start": 61,  "end": 93,  "text": "nonphotochemical quenching (NPQ)", "label": "TRT"},
  {"start": 99,  "end": 131, "text": "minimal fluorescence yield (F-0)", "label": "TRT"},
  {"start": 137, "end": 142, "text": "M-81E", "label": "VAR"},
  {"start": 144, "end": 149, "text": "M-81E", "label": "VAR"},
  {"start": 160, "end": 172, "text": "H2O2 content", "label": "TRT"},
  {"start": 184, "end": 199, "text": "Photoinhibition", "label": "TRT"},
  {"start": 218, "end": 260, "text": "reactive oxygen species (ROS) accumulation", "label": "TRT"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "Roma", "head_start": 0, "head_end": 4, "head_type": "VAR",
   "tail": "Q(A) reduction state (1-q(p))", "tail_start": 30, "tail_end": 59, "tail_type": "TRT", "label": "HAS"},
  {"head": "Roma", "head_start": 0, "head_end": 4, "head_type": "VAR",
   "tail": "nonphotochemical quenching (NPQ)", "tail_start": 61, "tail_end": 93, "tail_type": "TRT", "label": "HAS"},
  {"head": "Roma", "head_start": 0, "head_end": 4, "head_type": "VAR",
   "tail": "minimal fluorescence yield (F-0)", "tail_start": 99, "tail_end": 131, "tail_type": "TRT", "label": "HAS"},
  {"head": "M-81E", "head_start": 137, "head_end": 142, "head_type": "VAR",
   "tail": "Q(A) reduction state (1-q(p))", "tail_start": 30, "tail_end": 59, "tail_type": "TRT", "label": "HAS"},
  {"head": "M-81E", "head_start": 137, "head_end": 142, "head_type": "VAR",
   "tail": "nonphotochemical quenching (NPQ)", "tail_start": 61, "tail_end": 93, "tail_type": "TRT", "label": "HAS"},
  {"head": "M-81E", "head_start": 137, "head_end": 142, "head_type": "VAR",
   "tail": "minimal fluorescence yield (F-0)", "tail_start": 99, "tail_end": 131, "tail_type": "TRT", "label": "HAS"},
  {"head": "M-81E", "head_start": 137, "head_end": 142, "head_type": "VAR",
   "tail": "H2O2 content", "tail_start": 160, "tail_end": 172, "tail_type": "TRT", "label": "HAS"},
  {"head": "reactive oxygen species (ROS) accumulation", "head_start": 218, "head_end": 260, "head_type": "TRT",
   "tail": "Photoinhibition", "tail_start": 184, "tail_end": 199, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增实体 | `salt stress` @88:99 ABS；`Na+ efflux` @163:173 TRT |
| 0 | 新增关系 | AFF(SiCBL5@101, Na+ accumulation)；AFF(SiCBL5@101, Na+ efflux)；AFF(salt stress, salt tolerance) |
| 1 | 修改实体 | `abiotic stress` TRT→ABS |
| 1 | 删除实体 | `drought-stressed faba bean leaves` CROP |
| 1 | 新增实体 | `GO` BM；`KEGG` BM；`LEA` GENE；`DHNs` GENE；`HSPs` GENE；`faba bean` CROP；`drought adaptation` TRT |
| 1 | 新增关系 | HAS(faba bean, drought adaptation)；AFF(drought, drought adaptation)；AFF(LEA/DHNs/HSPs, drought adaptation) |
| 2 | 新增实体 | `seed vigor` @20:30 TRT |
| 2 | 新增关系 | AFF(AsA priming, seed vigor)；AFF(45 degrees C, seed vigor) |
| 3 | 新增实体 | `Path analysis` @115:128 BM |
| 4 | 删除实体 | `domestication` @174:187 TRT |
| 4 | 新增实体 | `gene expression` @113:128 TRT |
| 5 | 新增实体 | `co-expression network` @4:26 BM；`carbon fixation` @148:162 TRT；`proline synthesis` @248:264 TRT |
| 5 | 新增关系 | AFF(millet, drought stress)；HAS(millet, carbon fixation)；HAS(millet, proline synthesis) |
| 6 | 新增实体 | `Transcriptomic analysis` @0:25 BM |
| 8 | 新增实体 | `genetic diversity` @22:38 TRT |
