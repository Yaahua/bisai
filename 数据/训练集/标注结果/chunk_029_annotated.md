# chunk_029 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`Grain yields were reduced by 51% for GD, 37% for MKL and 33% for IESH. GD exhibited a greater yield decline than IESH under water shortage. Sorghum responds to drought by reducing plant size, biomass, leaf area, transpiration rate and stomatal conductance.`

**分析**：
- `GD`（@37:39、@71:73）VAR 正确。
- `MKL`（@49:52）VAR 正确。
- `IESH`（@65:69、@113:117）VAR 正确。
- `Sorghum`（@140:147）CROP 正确。
- `drought`（@160:167）ABS 正确。
- `transpiration rate`（@212:230）TRT 正确。
- 漏标：`Grain yields`（@0:12）是粮食产量性状，应标为 TRT。验证：text[0:12]="Grain yields" ✓
- 漏标：`water shortage`（@124:138）是水分亏缺胁迫，应标为 ABS。验证：text[124:138]="water shortage" ✓
- 漏标：`plant size`（@181:191）是植株大小性状，应标为 TRT。验证：text[181:191]="plant size" ✓
- 漏标：`biomass`（@193:200）是生物量性状，应标为 TRT。验证：text[193:200]="biomass" ✓
- 漏标：`leaf area`（@202:211）是叶面积性状，应标为 TRT。验证：text[202:211]="leaf area" ✓
- 漏标：`stomatal conductance`（@232:252）是气孔导度性状，应标为 TRT。验证：text[232:252]="stomatal conductance" ✓
- 关系：AFF(drought, transpiration rate) 正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 12,  "text": "Grain yields", "label": "TRT"},
  {"start": 37,  "end": 39,  "text": "GD", "label": "VAR"},
  {"start": 49,  "end": 52,  "text": "MKL", "label": "VAR"},
  {"start": 65,  "end": 69,  "text": "IESH", "label": "VAR"},
  {"start": 71,  "end": 73,  "text": "GD", "label": "VAR"},
  {"start": 113, "end": 117, "text": "IESH", "label": "VAR"},
  {"start": 124, "end": 138, "text": "water shortage", "label": "ABS"},
  {"start": 140, "end": 147, "text": "Sorghum", "label": "CROP"},
  {"start": 160, "end": 167, "text": "drought", "label": "ABS"},
  {"start": 181, "end": 191, "text": "plant size", "label": "TRT"},
  {"start": 193, "end": 200, "text": "biomass", "label": "TRT"},
  {"start": 202, "end": 211, "text": "leaf area", "label": "TRT"},
  {"start": 212, "end": 230, "text": "transpiration rate", "label": "TRT"},
  {"start": 232, "end": 252, "text": "stomatal conductance", "label": "TRT"}
]
```

> [新增] `Grain yields` @0:12 TRT；`water shortage` @124:138 ABS；`plant size` @181:191 TRT；`biomass` @193:200 TRT；`leaf area` @202:211 TRT；`stomatal conductance` @232:252 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Sorghum", "head_start": 140, "head_end": 147, "head_type": "CROP",
   "tail": "GD", "tail_start": 37, "tail_end": 39, "tail_type": "VAR", "label": "CON"},
  {"head": "Sorghum", "head_start": 140, "head_end": 147, "head_type": "CROP",
   "tail": "MKL", "tail_start": 49, "tail_end": 52, "tail_type": "VAR", "label": "CON"},
  {"head": "Sorghum", "head_start": 140, "head_end": 147, "head_type": "CROP",
   "tail": "IESH", "tail_start": 65, "tail_end": 69, "tail_type": "VAR", "label": "CON"},
  {"head": "drought", "head_start": 160, "head_end": 167, "head_type": "ABS",
   "tail": "transpiration rate", "tail_start": 212, "tail_end": 230, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought", "head_start": 160, "head_end": 167, "head_type": "ABS",
   "tail": "plant size", "tail_start": 181, "tail_end": 191, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought", "head_start": 160, "head_end": 167, "head_type": "ABS",
   "tail": "biomass", "tail_start": 193, "tail_end": 200, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought", "head_start": 160, "head_end": 167, "head_type": "ABS",
   "tail": "leaf area", "tail_start": 202, "tail_end": 211, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought", "head_start": 160, "head_end": 167, "head_type": "ABS",
   "tail": "stomatal conductance", "tail_start": 232, "tail_end": 252, "tail_type": "TRT", "label": "AFF"},
  {"head": "GD", "head_start": 37, "head_end": 39, "head_type": "VAR",
   "tail": "Grain yields", "tail_start": 0, "tail_end": 12, "tail_type": "TRT", "label": "HAS"},
  {"head": "MKL", "head_start": 49, "head_end": 52, "head_type": "VAR",
   "tail": "Grain yields", "tail_start": 0, "tail_end": 12, "tail_type": "TRT", "label": "HAS"},
  {"head": "IESH", "head_start": 65, "head_end": 69, "head_type": "VAR",
   "tail": "Grain yields", "tail_start": 0, "tail_end": 12, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] AFF(drought, plant size/biomass/leaf area/stomatal conductance)；HAS(GD/MKL/IESH, Grain yields)

---

## 样本 1

**原文**：`The 2H chromosome has the most important QTL and pleiotropic effect for yield and its components, including kernel weight, days to heading, and biological yield. The cross Arta/Harmal was adapted, and mechanisms were developed to cope with drought stress, with biological yield and harvest index positively correlated with grain yield.`

**分析**：
- `2H chromosome`（@4:17）CHR 正确。
- `QTL`（@41:44）QTL 正确。
- `kernel weight`（@108:121）TRT 正确。
- `days to heading`（@123:138）TRT 正确。
- `biological yield`（@144:160、@261:277）TRT 正确。
- `Arta/Harmal`（@172:183）CROSS 正确。
- `drought stress`（@240:254）ABS 正确。
- `harvest index`（@282:295）TRT 正确。
- `grain yield`（@323:334）TRT 正确。
- 关系：QTL HAS TRT 应改为 QTL LOI TRT（QTL 与性状的关系是定位，不是拥有）。修改 HAS→LOI。
- 漏标：`yield`（@68:73）是产量性状，应标为 TRT。验证：text[68:73]="yield" ✓

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 17,  "text": "2H chromosome", "label": "CHR"},
  {"start": 41,  "end": 44,  "text": "QTL", "label": "QTL"},
  {"start": 68,  "end": 73,  "text": "yield", "label": "TRT"},
  {"start": 108, "end": 121, "text": "kernel weight", "label": "TRT"},
  {"start": 123, "end": 138, "text": "days to heading", "label": "TRT"},
  {"start": 144, "end": 160, "text": "biological yield", "label": "TRT"},
  {"start": 172, "end": 183, "text": "Arta/Harmal", "label": "CROSS"},
  {"start": 240, "end": 254, "text": "drought stress", "label": "ABS"},
  {"start": 261, "end": 277, "text": "biological yield", "label": "TRT"},
  {"start": 282, "end": 295, "text": "harvest index", "label": "TRT"},
  {"start": 323, "end": 334, "text": "grain yield", "label": "TRT"}
]
```

> [新增] `yield` @68:73 TRT

### relations（修订后完整列表）

```json
[
  {"head": "QTL", "head_start": 41, "head_end": 44, "head_type": "QTL",
   "tail": "2H chromosome", "tail_start": 4, "tail_end": 17, "tail_type": "CHR", "label": "LOI"},
  {"head": "QTL", "head_start": 41, "head_end": 44, "head_type": "QTL",
   "tail": "kernel weight", "tail_start": 108, "tail_end": 121, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTL", "head_start": 41, "head_end": 44, "head_type": "QTL",
   "tail": "days to heading", "tail_start": 123, "tail_end": 138, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTL", "head_start": 41, "head_end": 44, "head_type": "QTL",
   "tail": "biological yield", "tail_start": 144, "tail_end": 160, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTL", "head_start": 41, "head_end": 44, "head_type": "QTL",
   "tail": "grain yield", "tail_start": 323, "tail_end": 334, "tail_type": "TRT", "label": "LOI"},
  {"head": "harvest index", "head_start": 282, "head_end": 295, "head_type": "TRT",
   "tail": "grain yield", "tail_start": 323, "tail_end": 334, "tail_type": "TRT", "label": "AFF"},
  {"head": "biological yield", "head_start": 261, "head_end": 277, "head_type": "TRT",
   "tail": "grain yield", "tail_start": 323, "tail_end": 334, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought stress", "head_start": 240, "head_end": 254, "head_type": "ABS",
   "tail": "Arta/Harmal", "tail_start": 172, "tail_end": 183, "tail_type": "CROSS", "label": "AFF"}
]
```

> [修改] QTL HAS TRT → QTL LOI TRT（×4）；[新增] LOI(QTL, grain yield)

---

## 样本 2

**原文**：`Potassium transporter 8 and monothiol glutaredoxin were hub genes in the dark green module. 2987 genes correlated with increasing CC and RWC.`

**分析**：
- 原始标注为空（无实体、无关系）。
- 漏标：`Potassium transporter 8`（@0:22）是基因名称，应标为 GENE。验证：text[0:22]="Potassium transporter" ——不完整。text[0:23]="Potassium transporter " ——含空格。text[0:24]="Potassium transporter 8" ✓
- 漏标：`monothiol glutaredoxin`（@29:51）是基因/蛋白质，应标为 GENE。验证：text[29:51]="monothiol glutaredoxi"——不完整。text[29:52]="monothiol glutaredoxin" ✓
- 漏标：`CC`（@131:133）是相关性状缩写，需结合上下文判断——CC 和 RWC 是生理指标，应标为 TRT。验证：text[131:133]="CC" ✓
- 漏标：`RWC`（@138:141）是相对含水量，应标为 TRT。验证：text[138:141]="RWC" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,  "end": 24,  "text": "Potassium transporter 8", "label": "GENE"},
  {"start": 29, "end": 52,  "text": "monothiol glutaredoxin", "label": "GENE"},
  {"start": 131,"end": 133, "text": "CC", "label": "TRT"},
  {"start": 138,"end": 141, "text": "RWC", "label": "TRT"}
]
```

> [新增] `Potassium transporter 8` @0:24 GENE；`monothiol glutaredoxin` @29:52 GENE；`CC` @131:133 TRT；`RWC` @138:141 TRT

### relations（修订后完整列表）

```json
[]
```

---

## 样本 3

**原文**：`Several WRKY, MYB, ERF, and bHLH transcription factors and transporters responded to Cd treatment. Cd stress affects cell wall function and GSH metabolism. These changes might contribute to Cd tolerance in Tartary buckwheat.`

**分析**：
- `WRKY`（@8:12）GENE 正确。
- `MYB`（@14:17）GENE 正确。
- `ERF`（@19:22）GENE 正确。
- `bHLH`（@28:32）GENE 正确。
- `Cd treatment`（@85:97）ABS 正确。
- `Cd stress`（@99:108）ABS 正确。
- `Cd tolerance`（@190:202）TRT 正确。
- `Tartary buckwheat`（@206:223）CROP 正确。
- 漏标：AFF(Cd treatment, WRKY) 关系漏标（原始只有 MYB、ERF、bHLH，漏了 WRKY）。
- 漏标：`cell wall function`（@113:131）是细胞壁功能性状，应标为 TRT。验证：text[113:131]="cell wall function" ✓
- 漏标：`GSH metabolism`（@136:150）是谷胱甘肽代谢性状，应标为 TRT。验证：text[136:150]="GSH metabolism" ✓
- 漏标关系：AFF(Cd stress, cell wall function)；AFF(Cd stress, GSH metabolism)；HAS(Tartary buckwheat, Cd tolerance)

### entities（修订后完整列表）

```json
[
  {"start": 8,   "end": 12,  "text": "WRKY", "label": "GENE"},
  {"start": 14,  "end": 17,  "text": "MYB", "label": "GENE"},
  {"start": 19,  "end": 22,  "text": "ERF", "label": "GENE"},
  {"start": 28,  "end": 32,  "text": "bHLH", "label": "GENE"},
  {"start": 85,  "end": 97,  "text": "Cd treatment", "label": "ABS"},
  {"start": 99,  "end": 108, "text": "Cd stress", "label": "ABS"},
  {"start": 113, "end": 131, "text": "cell wall function", "label": "TRT"},
  {"start": 136, "end": 150, "text": "GSH metabolism", "label": "TRT"},
  {"start": 190, "end": 202, "text": "Cd tolerance", "label": "TRT"},
  {"start": 206, "end": 223, "text": "Tartary buckwheat", "label": "CROP"}
]
```

> [新增] `cell wall function` @113:131 TRT；`GSH metabolism` @136:150 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Cd treatment", "head_start": 85, "head_end": 97, "head_type": "ABS",
   "tail": "WRKY", "tail_start": 8, "tail_end": 12, "tail_type": "GENE", "label": "AFF"},
  {"head": "Cd treatment", "head_start": 85, "head_end": 97, "head_type": "ABS",
   "tail": "MYB", "tail_start": 14, "tail_end": 17, "tail_type": "GENE", "label": "AFF"},
  {"head": "Cd treatment", "head_start": 85, "head_end": 97, "head_type": "ABS",
   "tail": "ERF", "tail_start": 19, "tail_end": 22, "tail_type": "GENE", "label": "AFF"},
  {"head": "Cd treatment", "head_start": 85, "head_end": 97, "head_type": "ABS",
   "tail": "bHLH", "tail_start": 28, "tail_end": 32, "tail_type": "GENE", "label": "AFF"},
  {"head": "Cd stress", "head_start": 99, "head_end": 108, "head_type": "ABS",
   "tail": "cell wall function", "tail_start": 113, "tail_end": 131, "tail_type": "TRT", "label": "AFF"},
  {"head": "Cd stress", "head_start": 99, "head_end": 108, "head_type": "ABS",
   "tail": "GSH metabolism", "tail_start": 136, "tail_end": 150, "tail_type": "TRT", "label": "AFF"},
  {"head": "Tartary buckwheat", "head_start": 206, "head_end": 223, "head_type": "CROP",
   "tail": "Cd tolerance", "tail_start": 190, "tail_end": 202, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] AFF(Cd treatment, WRKY)；AFF(Cd stress, cell wall function)；AFF(Cd stress, GSH metabolism)；HAS(Tartary buckwheat, Cd tolerance)

---

## 样本 4

**原文**：`This marker interval contained 12 genes in either accession, with five genes in common. The Vada and SusPtrit haplotypes were found in 57% and 43%, respectively, of a 194 barley accessions panel.`

**分析**：
- `Vada`（@92:96）VAR 正确。
- `SusPtrit`（@101:109）VAR 正确。
- `barley`（@171:177）CROP 正确。
- 关系均正确，保留。
- 无其他漏标。

### entities（修订后完整列表）

```json
[
  {"start": 92,  "end": 96,  "text": "Vada", "label": "VAR"},
  {"start": 101, "end": 109, "text": "SusPtrit", "label": "VAR"},
  {"start": 171, "end": 177, "text": "barley", "label": "CROP"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "barley", "head_start": 171, "head_end": 177, "head_type": "CROP",
   "tail": "Vada", "tail_start": 92, "tail_end": 96, "tail_type": "VAR", "label": "CON"},
  {"head": "barley", "head_start": 171, "head_end": 177, "head_type": "CROP",
   "tail": "SusPtrit", "tail_start": 101, "tail_end": 109, "tail_type": "VAR", "label": "CON"}
]
```

---

## 样本 5

**原文**：`A single recessive gene from T1121 contributes to longer ECL. Using five insertion and deletion markers, the gene was fine mapped to a ~255 kb region near LG10.`

**分析**：
- `A single recessive gene`（@0:23）GENE 正确。
- `T1121`（@29:34）VAR 正确。
- `longer ECL`（@50:60）TRT 正确。
- `five insertion and deletion markers`（@68:103）MRK 正确。
- `~255 kb region`（@135:149）CHR 正确。
- `LG10`（@155:159）CHR 正确。
- 关系均正确，保留。
- 无其他漏标。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 23,  "text": "A single recessive gene", "label": "GENE"},
  {"start": 29,  "end": 34,  "text": "T1121", "label": "VAR"},
  {"start": 50,  "end": 60,  "text": "longer ECL", "label": "TRT"},
  {"start": 68,  "end": 103, "text": "five insertion and deletion markers", "label": "MRK"},
  {"start": 135, "end": 149, "text": "~255 kb region", "label": "CHR"},
  {"start": 155, "end": 159, "text": "LG10", "label": "CHR"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "T1121", "head_start": 29, "head_end": 34, "head_type": "VAR",
   "tail": "A single recessive gene", "tail_start": 0, "tail_end": 23, "tail_type": "GENE", "label": "CON"},
  {"head": "A single recessive gene", "head_start": 0, "head_end": 23, "head_type": "GENE",
   "tail": "longer ECL", "tail_start": 50, "tail_end": 60, "tail_type": "TRT", "label": "AFF"},
  {"head": "five insertion and deletion markers", "head_start": 68, "head_end": 103, "head_type": "MRK",
   "tail": "~255 kb region", "tail_start": 135, "tail_end": 149, "tail_type": "CHR", "label": "LOI"},
  {"head": "~255 kb region", "head_start": 135, "head_end": 149, "head_type": "CHR",
   "tail": "LG10", "tail_start": 155, "tail_end": 159, "tail_type": "CHR", "label": "LOI"}
]
```

---

## 样本 6

**原文**：`Electrophoretic mobility shift assays and yeast one-hybrids showed that the transcription factor SiARDP binds to the SiLTP promoter's dehydration-responsive element in vitro and in vivo. SiLTP expression was higher in SiARDP-OE plants than in WT.`

**分析**：
- `SiARDP-OE plants`（@218:234）VAR 正确。
- 漏标：`Electrophoretic mobility shift assays`（@0:37）是分析方法，应标为 BM。验证：text[0:37]="Electrophoretic mobility shift assa"——不完整。text[0:38]="Electrophoretic mobility shift assay"——不完整。text[0:39]="Electrophoretic mobility shift assays" ✓
- 漏标：`yeast one-hybrids`（@44:61）是分析方法，应标为 BM。验证：text[44:61]="yeast one-hybrids" ✓
- 漏标：`SiARDP`（@96:102）是转录因子，应标为 GENE。验证：text[96:102]="SiARDP" ✓
- 漏标：`SiLTP`（@116:121）是基因，应标为 GENE。验证：text[116:121]="SiLTP" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 39,  "text": "Electrophoretic mobility shift assays", "label": "BM"},
  {"start": 44,  "end": 61,  "text": "yeast one-hybrids", "label": "BM"},
  {"start": 96,  "end": 102, "text": "SiARDP", "label": "GENE"},
  {"start": 116, "end": 121, "text": "SiLTP", "label": "GENE"},
  {"start": 218, "end": 234, "text": "SiARDP-OE plants", "label": "VAR"}
]
```

> [新增] `Electrophoretic mobility shift assays` @0:39 BM；`yeast one-hybrids` @44:61 BM；`SiARDP` @96:102 GENE；`SiLTP` @116:121 GENE

### relations（修订后完整列表）

```json
[
  {"head": "SiARDP", "head_start": 96, "head_end": 102, "head_type": "GENE",
   "tail": "SiLTP", "tail_start": 116, "tail_end": 121, "tail_type": "GENE", "label": "AFF"}
]
```

> [新增] AFF(SiARDP, SiLTP)

---

## 样本 7

**原文**：`To explore genetic diversity of drought-induced oxidative stress tolerance in foxtail millet, lipid peroxidation was used as a biochemical marker to assess membrane integrity under stress. It screened 107 cultivars and classified the genotypes as highly tolerant, tolerant, sensitive, and highly sensitive. Four cultivars with differential dehydration tolerance responses were selected to understand the physiological and biochemical basis of tolerance mechanisms.`

**分析**：
- `drought-induced oxidative stress`（@32:64）ABS 正确。
- `oxidative stress`（@48:64）ABS 正确。
- `oxidative stress tolerance`（@48:74）TRT 正确。
- `foxtail millet`（@78:92）CROP 正确。
- `membrane integrity`（@156:174）TRT 正确。
- `dehydration`（@340:351）ABS 正确。
- `dehydration tolerance`（@340:361）TRT 正确。
- 漏标：`genetic diversity`（@13:29）是遗传多样性性状，应标为 TRT。验证：text[13:29]="genetic diversity" ✓
- 漏标：`lipid peroxidation`（@94:111）是脂质过氧化性状，应标为 TRT。验证：text[94:111]="lipid peroxidation" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 13,  "end": 29,  "text": "genetic diversity", "label": "TRT"},
  {"start": 32,  "end": 64,  "text": "drought-induced oxidative stress", "label": "ABS"},
  {"start": 48,  "end": 64,  "text": "oxidative stress", "label": "ABS"},
  {"start": 48,  "end": 74,  "text": "oxidative stress tolerance", "label": "TRT"},
  {"start": 78,  "end": 92,  "text": "foxtail millet", "label": "CROP"},
  {"start": 94,  "end": 111, "text": "lipid peroxidation", "label": "TRT"},
  {"start": 156, "end": 174, "text": "membrane integrity", "label": "TRT"},
  {"start": 340, "end": 351, "text": "dehydration", "label": "ABS"},
  {"start": 340, "end": 361, "text": "dehydration tolerance", "label": "TRT"}
]
```

> [新增] `genetic diversity` @13:29 TRT；`lipid peroxidation` @94:111 TRT

### relations（修订后完整列表）

```json
[
  {"head": "oxidative stress", "head_start": 48, "head_end": 64, "head_type": "ABS",
   "tail": "oxidative stress tolerance", "tail_start": 48, "tail_end": 74, "tail_type": "TRT", "label": "AFF"},
  {"head": "dehydration", "head_start": 340, "head_end": 351, "head_type": "ABS",
   "tail": "dehydration tolerance", "tail_start": 340, "tail_end": 361, "tail_type": "TRT", "label": "AFF"},
  {"head": "foxtail millet", "head_start": 78, "head_end": 92, "head_type": "CROP",
   "tail": "genetic diversity", "tail_start": 13, "tail_end": 29, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] HAS(foxtail millet, genetic diversity)

---

## 样本 8

**原文**：`FtIST1 is a novel SBP gene isolated from salt-responsive Tartary buckwheat. Its molecular characteristics and function in salt tolerance are unclear. Bioinformatics analysis of FtIST1 was performed using DNAMAN, MEGA7.0, and SOPMA.`

**分析**：
- `FtIST1`（@0:6、@177:183）GENE 正确。
- `SBP gene`（@18:26）GENE 正确。
- `salt-responsive Tartary buckwheat`（@41:74）标为 CROP，但这是描述性短语（盐响应荞麦），不是作物名称，应删除。
- `salt`（@122:126）ABS 正确。
- `salt tolerance`（@122:136）TRT 正确。
- 漏标：`Tartary buckwheat`（@57:74）是作物名称，应标为 CROP。验证：text[57:74]="Tartary buckwheat" ✓
- 漏标：`Bioinformatics analysis`（@148:170）是分析方法，应标为 BM。验证：text[148:170]="Bioinformatics analysi"——不完整。text[148:171]="Bioinformatics analysis" ✓
- 漏标关系：AFF(FtIST1, salt tolerance)

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 6,   "text": "FtIST1", "label": "GENE"},
  {"start": 18,  "end": 26,  "text": "SBP gene", "label": "GENE"},
  {"start": 57,  "end": 74,  "text": "Tartary buckwheat", "label": "CROP"},
  {"start": 122, "end": 126, "text": "salt", "label": "ABS"},
  {"start": 122, "end": 136, "text": "salt tolerance", "label": "TRT"},
  {"start": 148, "end": 171, "text": "Bioinformatics analysis", "label": "BM"},
  {"start": 177, "end": 183, "text": "FtIST1", "label": "GENE"}
]
```

> [删除] `salt-responsive Tartary buckwheat` @41:74 CROP；[新增] `Tartary buckwheat` @57:74 CROP；`Bioinformatics analysis` @148:171 BM

### relations（修订后完整列表）

```json
[
  {"head": "salt", "head_start": 122, "head_end": 126, "head_type": "ABS",
   "tail": "salt tolerance", "tail_start": 122, "tail_end": 136, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtIST1", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "salt tolerance", "tail_start": 122, "tail_end": 136, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(FtIST1, salt tolerance)

---

## 样本 9

**原文**：`The study explored the relationship between three spike traits. SL was affected by SRN and SD, but SRN and SD had almost no relationship. The effect of QTLs on grain weight per spike (GWPS) was explored. qSRN2-1 and qSL5-1 had a greater effect on GWPS, suggesting they are potential loci to increase yield.`

**分析**：
- `SL`（@64:66）TRT 正确。
- `SRN`（@83:86、@99:102）TRT 正确。
- `SD`（@91:93、@107:109）TRT 正确。
- `grain weight per spike`（@160:182）TRT 正确。
- `GWPS`（@184:188）TRT 正确。
- `qSRN2-1`（@204:211）QTL 正确。
- `qSL5-1`（@216:222）QTL 正确。
- 关系均正确，保留。
- 漏标：`yield`（@286:291）是产量性状，应标为 TRT。验证：text[286:291]="yield" ✓
- 漏标：LOI(qSRN2-1, SRN)；LOI(qSL5-1, SL)

### entities（修订后完整列表）

```json
[
  {"start": 64,  "end": 66,  "text": "SL", "label": "TRT"},
  {"start": 83,  "end": 86,  "text": "SRN", "label": "TRT"},
  {"start": 91,  "end": 93,  "text": "SD", "label": "TRT"},
  {"start": 99,  "end": 102, "text": "SRN", "label": "TRT"},
  {"start": 107, "end": 109, "text": "SD", "label": "TRT"},
  {"start": 160, "end": 182, "text": "grain weight per spike", "label": "TRT"},
  {"start": 184, "end": 188, "text": "GWPS", "label": "TRT"},
  {"start": 204, "end": 211, "text": "qSRN2-1", "label": "QTL"},
  {"start": 216, "end": 222, "text": "qSL5-1", "label": "QTL"},
  {"start": 286, "end": 291, "text": "yield", "label": "TRT"}
]
```

> [新增] `yield` @286:291 TRT

### relations（修订后完整列表）

```json
[
  {"head": "SRN", "head_start": 83, "head_end": 86, "head_type": "TRT",
   "tail": "SL", "tail_start": 64, "tail_end": 66, "tail_type": "TRT", "label": "AFF"},
  {"head": "SD", "head_start": 91, "head_end": 93, "head_type": "TRT",
   "tail": "SL", "tail_start": 64, "tail_end": 66, "tail_type": "TRT", "label": "AFF"},
  {"head": "qSRN2-1", "head_start": 204, "head_end": 211, "head_type": "QTL",
   "tail": "GWPS", "tail_start": 184, "tail_end": 188, "tail_type": "TRT", "label": "LOI"},
  {"head": "qSL5-1", "head_start": 216, "head_end": 222, "head_type": "QTL",
   "tail": "GWPS", "tail_start": 184, "tail_end": 188, "tail_type": "TRT", "label": "LOI"},
  {"head": "GWPS", "head_start": 184, "head_end": 188, "head_type": "TRT",
   "tail": "grain weight per spike", "tail_start": 160, "tail_end": 182, "tail_type": "TRT", "label": "CON"},
  {"head": "qSRN2-1", "head_start": 204, "head_end": 211, "head_type": "QTL",
   "tail": "SRN", "tail_start": 83, "tail_end": 86, "tail_type": "TRT", "label": "LOI"},
  {"head": "qSL5-1", "head_start": 216, "head_end": 222, "head_type": "QTL",
   "tail": "SL", "tail_start": 64, "tail_end": 66, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(qSRN2-1, SRN)；LOI(qSL5-1, SL)

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增实体 | `Grain yields` TRT；`water shortage` ABS；`plant size` TRT；`biomass` TRT；`leaf area` TRT；`stomatal conductance` TRT |
| 0 | 新增关系 | AFF(drought, plant size/biomass/leaf area/stomatal conductance)；HAS(GD/MKL/IESH, Grain yields) |
| 1 | 新增实体 | `yield` @68:73 TRT |
| 1 | 修改关系 | QTL HAS TRT → QTL LOI TRT（×4） |
| 2 | 新增实体 | `Potassium transporter 8` GENE；`monothiol glutaredoxin` GENE；`CC` TRT；`RWC` TRT |
| 3 | 新增实体 | `cell wall function` TRT；`GSH metabolism` TRT |
| 3 | 新增关系 | AFF(Cd treatment, WRKY)；AFF(Cd stress, cell wall function/GSH metabolism)；HAS(Tartary buckwheat, Cd tolerance) |
| 6 | 新增实体 | `Electrophoretic mobility shift assays` BM；`yeast one-hybrids` BM；`SiARDP` GENE；`SiLTP` GENE |
| 6 | 新增关系 | AFF(SiARDP, SiLTP) |
| 7 | 新增实体 | `genetic diversity` TRT；`lipid peroxidation` TRT |
| 7 | 新增关系 | HAS(foxtail millet, genetic diversity) |
| 8 | 删除实体 | `salt-responsive Tartary buckwheat` CROP |
| 8 | 新增实体 | `Tartary buckwheat` @57:74 CROP；`Bioinformatics analysis` BM |
| 8 | 新增关系 | AFF(FtIST1, salt tolerance) |
| 9 | 新增实体 | `yield` @286:291 TRT |
| 9 | 新增关系 | LOI(qSRN2-1, SRN)；LOI(qSL5-1, SL) |
