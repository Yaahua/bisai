# chunk_030 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`GsNAC2 was induced by saline-alkali treatment and expressed in sorghum leaves. GsNAC2-overexpressing sorghum plants showed increased plant height, dry weight, moisture content, root activity, leaf length, chlorophyll content, stomatal conductance, relative root activity, relative chlorophyll content, relative stomatal conductance, and relative transpiration rate after saline-alkali treatment.`

**分析**：
- `GsNAC2`（@0:6、@79:85）GENE 正确。
- `saline-alkali treatment`（@22:45、@371:394）ABS 正确。
- `sorghum`（@63:70）CROP 正确。
- 漏标大量并列性状：`plant height`（@101:113）、`dry weight`（@115:125）、`moisture content`（@127:143）、`root activity`（@145:158）、`leaf length`（@160:171）、`chlorophyll content`（@173:192）、`stomatal conductance`（@194:214）均为 TRT。
- 漏标：`GsNAC2-overexpressing sorghum plants`（@79:115）——这是过表达品系，应标为 VAR。但边界应精确到 `GsNAC2-overexpressing sorghum`（@79:108）。验证：text[79:108]="GsNAC2-overexpressing sorghum" ✓
- 关系：AFF(saline-alkali treatment, GsNAC2) 正确，保留。
- 新增关系：AFF(GsNAC2, plant height/dry weight/moisture content/root activity/leaf length/chlorophyll content/stomatal conductance)

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 6,   "text": "GsNAC2", "label": "GENE"},
  {"start": 22,  "end": 45,  "text": "saline-alkali treatment", "label": "ABS"},
  {"start": 63,  "end": 70,  "text": "sorghum", "label": "CROP"},
  {"start": 79,  "end": 85,  "text": "GsNAC2", "label": "GENE"},
  {"start": 79,  "end": 108, "text": "GsNAC2-overexpressing sorghum", "label": "VAR"},
  {"start": 101, "end": 113, "text": "plant height", "label": "TRT"},
  {"start": 115, "end": 125, "text": "dry weight", "label": "TRT"},
  {"start": 127, "end": 143, "text": "moisture content", "label": "TRT"},
  {"start": 145, "end": 158, "text": "root activity", "label": "TRT"},
  {"start": 160, "end": 171, "text": "leaf length", "label": "TRT"},
  {"start": 173, "end": 192, "text": "chlorophyll content", "label": "TRT"},
  {"start": 194, "end": 214, "text": "stomatal conductance", "label": "TRT"},
  {"start": 371, "end": 394, "text": "saline-alkali treatment", "label": "ABS"}
]
```

> [新增] `GsNAC2-overexpressing sorghum` @79:108 VAR；`plant height` @101:113 TRT；`dry weight` @115:125 TRT；`moisture content` @127:143 TRT；`root activity` @145:158 TRT；`leaf length` @160:171 TRT；`chlorophyll content` @173:192 TRT；`stomatal conductance` @194:214 TRT

### relations（修订后完整列表）

```json
[
  {"head": "saline-alkali treatment", "head_start": 22, "head_end": 45, "head_type": "ABS",
   "tail": "GsNAC2", "tail_start": 0, "tail_end": 6, "tail_type": "GENE", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "plant height", "tail_start": 101, "tail_end": 113, "tail_type": "TRT", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "dry weight", "tail_start": 115, "tail_end": 125, "tail_type": "TRT", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "moisture content", "tail_start": 127, "tail_end": 143, "tail_type": "TRT", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "root activity", "tail_start": 145, "tail_end": 158, "tail_type": "TRT", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "leaf length", "tail_start": 160, "tail_end": 171, "tail_type": "TRT", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "chlorophyll content", "tail_start": 173, "tail_end": 192, "tail_type": "TRT", "label": "AFF"},
  {"head": "GsNAC2", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "stomatal conductance", "tail_start": 194, "tail_end": 214, "tail_type": "TRT", "label": "AFF"},
  {"head": "sorghum", "head_start": 63, "head_end": 70, "head_type": "CROP",
   "tail": "GsNAC2-overexpressing sorghum", "tail_start": 79, "tail_end": 108, "tail_type": "VAR", "label": "CON"}
]
```

> [新增] AFF(GsNAC2, plant height/dry weight/moisture content/root activity/leaf length/chlorophyll content/stomatal conductance)；CON(sorghum, GsNAC2-overexpressing sorghum)

---

## 样本 1

**原文**：`The genes of LRNK1 and LR2381 showed different expression patterns under salt stress. Metabolomic data revealed different salicylic acid and betaine profiles between LRNK1 and LR2381, which mediated salt tolerance in sorghum.`

**分析**：
- `LRNK1`（@13:18、@166:171）VAR 正确。
- `LR2381`（@23:29、@176:182）VAR 正确。
- `salt stress`（@73:84）ABS 正确。
- `salicylic acid`（@122:136）TRT 正确。
- `betaine`（@141:148）TRT 正确。
- `salt tolerance`（@199:213）TRT 正确。
- `sorghum`（@217:224）CROP 正确。
- 关系均正确，保留。
- 漏标：`gene expression`（@37:52）——原文 "different expression patterns" 是基因表达模式，应标 TRT。验证：text[37:52]="expression patter"——不完整。text[37:55]="expression patterns" ✓ 但更精确应标 `expression patterns`（@37:55）TRT。
- 漏标关系：AFF(salt stress, salicylic acid)；AFF(salt stress, betaine)

### entities（修订后完整列表）

```json
[
  {"start": 13,  "end": 18,  "text": "LRNK1", "label": "VAR"},
  {"start": 23,  "end": 29,  "text": "LR2381", "label": "VAR"},
  {"start": 37,  "end": 55,  "text": "expression patterns", "label": "TRT"},
  {"start": 73,  "end": 84,  "text": "salt stress", "label": "ABS"},
  {"start": 122, "end": 136, "text": "salicylic acid", "label": "TRT"},
  {"start": 141, "end": 148, "text": "betaine", "label": "TRT"},
  {"start": 166, "end": 171, "text": "LRNK1", "label": "VAR"},
  {"start": 176, "end": 182, "text": "LR2381", "label": "VAR"},
  {"start": 199, "end": 213, "text": "salt tolerance", "label": "TRT"},
  {"start": 217, "end": 224, "text": "sorghum", "label": "CROP"}
]
```

> [新增] `expression patterns` @37:55 TRT

### relations（修订后完整列表）

```json
[
  {"head": "sorghum", "head_start": 217, "head_end": 224, "head_type": "CROP",
   "tail": "LRNK1", "tail_start": 13, "tail_end": 18, "tail_type": "VAR", "label": "CON"},
  {"head": "sorghum", "head_start": 217, "head_end": 224, "head_type": "CROP",
   "tail": "LR2381", "tail_start": 23, "tail_end": 29, "tail_type": "VAR", "label": "CON"},
  {"head": "salt stress", "head_start": 73, "head_end": 84, "head_type": "ABS",
   "tail": "salt tolerance", "tail_start": 199, "tail_end": 213, "tail_type": "TRT", "label": "AFF"},
  {"head": "salt stress", "head_start": 73, "head_end": 84, "head_type": "ABS",
   "tail": "salicylic acid", "tail_start": 122, "tail_end": 136, "tail_type": "TRT", "label": "AFF"},
  {"head": "salt stress", "head_start": 73, "head_end": 84, "head_type": "ABS",
   "tail": "betaine", "tail_start": 141, "tail_end": 148, "tail_type": "TRT", "label": "AFF"},
  {"head": "sorghum", "head_start": 217, "head_end": 224, "head_type": "CROP",
   "tail": "salt tolerance", "tail_start": 199, "tail_end": 213, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] AFF(salt stress, salicylic acid)；AFF(salt stress, betaine)

---

## 样本 2

**原文**：`Indole-3-acetic acid (IAA), cytokinins (CTK), gibberellic acid (GA3), abscisic acid (ABA), soluble sugar, amino acid, and root bleeding intensity were mainly affected by non-additive genetic effects of the genes. Soluble protein was affected by additive genetic effects of the genes and had a high narrow heritability of 75.50%.`

**分析**：
- 所有激素/代谢物标为 TRT 正确（IAA、CTK、GA3、ABA 等均为可量化生理性状）。
- `Soluble protein`（@213:228）TRT 正确。
- 原始关系为空，但原文明确提到各性状受遗传效应影响，无法建立标准关系（无具体 GENE/VAR/CROP 实体），保留空关系。
- 无漏标。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 20,  "text": "Indole-3-acetic acid", "label": "TRT"},
  {"start": 22,  "end": 25,  "text": "IAA", "label": "TRT"},
  {"start": 28,  "end": 38,  "text": "cytokinins", "label": "TRT"},
  {"start": 40,  "end": 43,  "text": "CTK", "label": "TRT"},
  {"start": 46,  "end": 62,  "text": "gibberellic acid", "label": "TRT"},
  {"start": 64,  "end": 67,  "text": "GA3", "label": "TRT"},
  {"start": 70,  "end": 83,  "text": "abscisic acid", "label": "TRT"},
  {"start": 85,  "end": 88,  "text": "ABA", "label": "TRT"},
  {"start": 91,  "end": 104, "text": "soluble sugar", "label": "TRT"},
  {"start": 106, "end": 116, "text": "amino acid", "label": "TRT"},
  {"start": 122, "end": 145, "text": "root bleeding intensity", "label": "TRT"},
  {"start": 213, "end": 228, "text": "Soluble protein", "label": "TRT"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[]
```

---

## 样本 3

**原文**：`GWAS investigated RSA traits and GP accuracy in sorghum at seedling stage. NRA, NNR, NRL, FSW, DSW, and LA were measured in 160 sorghum accessions grown in rhizotrons.`

**分析**：
- `GWAS`（@0:4）BM 正确。
- `sorghum`（@48:55）CROP 正确。
- `seedling stage`（@59:73）GST 正确。
- `R`（@86:87）被标为 CROP，明显错误——这是单字母，不是作物名称，应删除。
- 漏标：`RSA traits`（@17:27）是根系构型性状，应标为 TRT。验证：text[17:27]="RSA traits" ✓
- 漏标：`GP accuracy`（@32:43）是基因组预测准确性，应标为 TRT。验证：text[32:43]="GP accuracy" ✓
- 漏标：`NRA`（@75:78）、`NNR`（@80:83）、`NRL`（@85:88）、`FSW`（@90:93）、`DSW`（@95:98）、`LA`（@104:106）均是根系性状缩写，应标为 TRT。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 4,   "text": "GWAS", "label": "BM"},
  {"start": 17,  "end": 27,  "text": "RSA traits", "label": "TRT"},
  {"start": 32,  "end": 43,  "text": "GP accuracy", "label": "TRT"},
  {"start": 48,  "end": 55,  "text": "sorghum", "label": "CROP"},
  {"start": 59,  "end": 73,  "text": "seedling stage", "label": "GST"},
  {"start": 75,  "end": 78,  "text": "NRA", "label": "TRT"},
  {"start": 80,  "end": 83,  "text": "NNR", "label": "TRT"},
  {"start": 85,  "end": 88,  "text": "NRL", "label": "TRT"},
  {"start": 90,  "end": 93,  "text": "FSW", "label": "TRT"},
  {"start": 95,  "end": 98,  "text": "DSW", "label": "TRT"},
  {"start": 104, "end": 106, "text": "LA", "label": "TRT"}
]
```

> [删除] `R` @86:87 CROP；[新增] `RSA traits` @17:27 TRT；`GP accuracy` @32:43 TRT；`NRA` @75:78 TRT；`NNR` @80:83 TRT；`NRL` @85:88 TRT；`FSW` @90:93 TRT；`DSW` @95:98 TRT；`LA` @104:106 TRT

### relations（修订后完整列表）

```json
[
  {"head": "GWAS", "head_start": 0, "head_end": 4, "head_type": "BM",
   "tail": "RSA traits", "tail_start": 17, "tail_end": 27, "tail_type": "TRT", "label": "USE"},
  {"head": "GWAS", "head_start": 0, "head_end": 4, "head_type": "BM",
   "tail": "GP accuracy", "tail_start": 32, "tail_end": 43, "tail_type": "TRT", "label": "USE"}
]
```

> [新增] USE(GWAS, RSA traits)；USE(GWAS, GP accuracy)

---

## 样本 4

**原文**：`The QTLs (QKW 1.5, QKW2.7b, QKW4.1, QKW6.7, QKW6.9) have positive effects on crop yield in semi-dry and dry areas. In the Arta/Harmal population, genomic co-localisation of the QTL suggests selection for drought tolerance in barley via linked markers.`

**分析**：
- 所有 QTL 标注正确（QKW 1.5、QKW2.7b、QKW4.1、QKW6.7、QKW6.9）。
- `crop yield`（@77:87）TRT 正确。
- `semi-dry and dry areas`（@91:113）ABS 正确。
- `Arta/Harmal population`（@122:144）CROSS 正确。
- `drought tolerance`（@204:221）TRT 正确。
- `barley`（@225:231）CROP 正确。
- `linked markers`（@236:250）MRK 正确。
- 关系：QTL AFF TRT 应改为 QTL LOI TRT（QTL 与性状的关系是定位，不是影响）。
- `Arta/Harmal population` CON `barley` 关系正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 10,  "end": 17,  "text": "QKW 1.5", "label": "QTL"},
  {"start": 19,  "end": 26,  "text": "QKW2.7b", "label": "QTL"},
  {"start": 28,  "end": 34,  "text": "QKW4.1", "label": "QTL"},
  {"start": 36,  "end": 42,  "text": "QKW6.7", "label": "QTL"},
  {"start": 44,  "end": 50,  "text": "QKW6.9", "label": "QTL"},
  {"start": 77,  "end": 87,  "text": "crop yield", "label": "TRT"},
  {"start": 91,  "end": 113, "text": "semi-dry and dry areas", "label": "ABS"},
  {"start": 122, "end": 144, "text": "Arta/Harmal population", "label": "CROSS"},
  {"start": 204, "end": 221, "text": "drought tolerance", "label": "TRT"},
  {"start": 225, "end": 231, "text": "barley", "label": "CROP"},
  {"start": 236, "end": 250, "text": "linked markers", "label": "MRK"}
]
```

> 无实体修改。

### relations（修订后完整列表）

```json
[
  {"head": "QKW 1.5", "head_start": 10, "head_end": 17, "head_type": "QTL",
   "tail": "crop yield", "tail_start": 77, "tail_end": 87, "tail_type": "TRT", "label": "LOI"},
  {"head": "QKW2.7b", "head_start": 19, "head_end": 26, "head_type": "QTL",
   "tail": "crop yield", "tail_start": 77, "tail_end": 87, "tail_type": "TRT", "label": "LOI"},
  {"head": "QKW4.1", "head_start": 28, "head_end": 34, "head_type": "QTL",
   "tail": "crop yield", "tail_start": 77, "tail_end": 87, "tail_type": "TRT", "label": "LOI"},
  {"head": "QKW6.7", "head_start": 36, "head_end": 42, "head_type": "QTL",
   "tail": "crop yield", "tail_start": 77, "tail_end": 87, "tail_type": "TRT", "label": "LOI"},
  {"head": "QKW6.9", "head_start": 44, "head_end": 50, "head_type": "QTL",
   "tail": "crop yield", "tail_start": 77, "tail_end": 87, "tail_type": "TRT", "label": "LOI"},
  {"head": "semi-dry and dry areas", "head_start": 91, "head_end": 113, "head_type": "ABS",
   "tail": "crop yield", "tail_start": 77, "tail_end": 87, "tail_type": "TRT", "label": "AFF"},
  {"head": "Arta/Harmal population", "head_start": 122, "head_end": 144, "head_type": "CROSS",
   "tail": "drought tolerance", "tail_start": 204, "tail_end": 221, "tail_type": "TRT", "label": "HAS"},
  {"head": "Arta/Harmal population", "head_start": 122, "head_end": 144, "head_type": "CROSS",
   "tail": "barley", "tail_start": 225, "tail_end": 231, "tail_type": "CROP", "label": "CON"},
  {"head": "linked markers", "head_start": 236, "head_end": 250, "head_type": "MRK",
   "tail": "drought tolerance", "tail_start": 204, "tail_end": 221, "tail_type": "TRT", "label": "LOI"}
]
```

> [修改] QTL AFF TRT → QTL LOI TRT（×5）

---

## 样本 5

**原文**：`Haplotype and QTL analyses showed that E2 genes, including SiUBC39, are associated with plant height, flowering time, and stress tolerance. CRISPR/Cas9 validation found that disrupting SiUBC39 caused early flowering, reduced plant height, and reduced grain yield, resembling Setaria viridis. IP-MS and transcriptome analysis revealed SiUBC39 is involved in growth and development regulation, drought stress response, and immune response.`

**分析**：
- `SiUBC39`（@59:66、@185:192）GENE 正确。
- `plant height`（@88:100）TRT 正确。
- `stress tolerance`（@122:138）TRT 正确。
- `CRISPR/Cas9`（@140:151）BM 正确。
- `reduced plant height`（@217:237）TRT——应修改为 `plant height`（@225:237），去掉修饰词。
- `reduced grain yield`（@243:262）TRT——应修改为 `grain yield`（@251:262），去掉修饰词。
- `Setaria viridis`（@275:290）VAR——Setaria viridis 是野生型谷子，应标为 CROP 而非 VAR。
- `transcriptome`（@302:315）BM 正确。
- `drought stress response`（@392:415）TRT 正确。
- `immune response`（@421:436）TRT 正确。
- 漏标：`flowering time`（@102:116）是开花时间性状，应标为 TRT。验证：text[102:116]="flowering time" ✓
- 漏标：`early flowering`（@200:215）是早花性状，应标为 TRT。验证：text[200:215]="early flowering" ✓
- 漏标：`IP-MS`（@292:297）是质谱分析方法，应标为 BM。验证：text[292:297]="IP-MS" ✓
- 漏标关系：AFF(SiUBC39, plant height)；AFF(SiUBC39, flowering time)；AFF(SiUBC39, stress tolerance)；AFF(SiUBC39, early flowering)；AFF(SiUBC39, grain yield)；AFF(SiUBC39, immune response)

### entities（修订后完整列表）

```json
[
  {"start": 59,  "end": 66,  "text": "SiUBC39", "label": "GENE"},
  {"start": 88,  "end": 100, "text": "plant height", "label": "TRT"},
  {"start": 102, "end": 116, "text": "flowering time", "label": "TRT"},
  {"start": 122, "end": 138, "text": "stress tolerance", "label": "TRT"},
  {"start": 140, "end": 151, "text": "CRISPR/Cas9", "label": "BM"},
  {"start": 185, "end": 192, "text": "SiUBC39", "label": "GENE"},
  {"start": 200, "end": 215, "text": "early flowering", "label": "TRT"},
  {"start": 225, "end": 237, "text": "plant height", "label": "TRT"},
  {"start": 251, "end": 262, "text": "grain yield", "label": "TRT"},
  {"start": 275, "end": 290, "text": "Setaria viridis", "label": "CROP"},
  {"start": 292, "end": 297, "text": "IP-MS", "label": "BM"},
  {"start": 302, "end": 315, "text": "transcriptome", "label": "BM"},
  {"start": 392, "end": 415, "text": "drought stress response", "label": "TRT"},
  {"start": 421, "end": 436, "text": "immune response", "label": "TRT"}
]
```

> [修改] `reduced plant height` @217:237 → `plant height` @225:237 TRT；`reduced grain yield` @243:262 → `grain yield` @251:262 TRT；`Setaria viridis` VAR → CROP；[新增] `flowering time` @102:116 TRT；`early flowering` @200:215 TRT；`IP-MS` @292:297 BM

### relations（修订后完整列表）

```json
[
  {"head": "SiUBC39", "head_start": 59, "head_end": 66, "head_type": "GENE",
   "tail": "plant height", "tail_start": 88, "tail_end": 100, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 59, "head_end": 66, "head_type": "GENE",
   "tail": "flowering time", "tail_start": 102, "tail_end": 116, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 59, "head_end": 66, "head_type": "GENE",
   "tail": "stress tolerance", "tail_start": 122, "tail_end": 138, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 185, "head_end": 192, "head_type": "GENE",
   "tail": "early flowering", "tail_start": 200, "tail_end": 215, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 185, "head_end": 192, "head_type": "GENE",
   "tail": "plant height", "tail_start": 225, "tail_end": 237, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 185, "head_end": 192, "head_type": "GENE",
   "tail": "grain yield", "tail_start": 251, "tail_end": 262, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 59, "head_end": 66, "head_type": "GENE",
   "tail": "drought stress response", "tail_start": 392, "tail_end": 415, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 59, "head_end": 66, "head_type": "GENE",
   "tail": "immune response", "tail_start": 421, "tail_end": 436, "tail_type": "TRT", "label": "AFF"},
  {"head": "CRISPR/Cas9", "head_start": 140, "head_end": 151, "head_type": "BM",
   "tail": "SiUBC39", "tail_start": 59, "tail_end": 66, "tail_type": "GENE", "label": "USE"}
]
```

> [新增] AFF(SiUBC39, plant height/flowering time/stress tolerance/early flowering/grain yield/immune response)

---

## 样本 6

**原文**：`A major QTL locus qGL1, accounting for 16.7% phenotypic variance, is located on chromosome 1H. It is a new QTL affecting GL. Two other QTLs, qGL5 and qTGW5, accounting for 20.7% and 21.1% phenotypic variance respectively, were identified in the same region. Sequencing showed they are identical to the HvDep1 gene.`

**分析**：
- `qGL1`（@18:22）QTL 正确。
- `chromosome 1H`（@80:93）CHR 正确。
- `qGL5`（@141:145）QTL 正确。
- `qTGW5`（@150:155）QTL 正确。
- `HvDep1`（@302:308）GENE 正确。
- 关系：LOI(qGL1, chromosome 1H) 正确，保留。
- 漏标：`GL`（@113:115）是粒长性状，应标为 TRT。验证：text[113:115]="GL" ✓
- 漏标关系：LOI(qGL1, GL)；LOI(qGL5, GL)；LOI(qTGW5, GL)

### entities（修订后完整列表）

```json
[
  {"start": 18,  "end": 22,  "text": "qGL1", "label": "QTL"},
  {"start": 80,  "end": 93,  "text": "chromosome 1H", "label": "CHR"},
  {"start": 113, "end": 115, "text": "GL", "label": "TRT"},
  {"start": 141, "end": 145, "text": "qGL5", "label": "QTL"},
  {"start": 150, "end": 155, "text": "qTGW5", "label": "QTL"},
  {"start": 302, "end": 308, "text": "HvDep1", "label": "GENE"}
]
```

> [新增] `GL` @113:115 TRT

### relations（修订后完整列表）

```json
[
  {"head": "qGL1", "head_start": 18, "head_end": 22, "head_type": "QTL",
   "tail": "chromosome 1H", "tail_start": 80, "tail_end": 93, "tail_type": "CHR", "label": "LOI"},
  {"head": "qGL1", "head_start": 18, "head_end": 22, "head_type": "QTL",
   "tail": "GL", "tail_start": 113, "tail_end": 115, "tail_type": "TRT", "label": "LOI"},
  {"head": "qGL5", "head_start": 141, "head_end": 145, "head_type": "QTL",
   "tail": "GL", "tail_start": 113, "tail_end": 115, "tail_type": "TRT", "label": "LOI"},
  {"head": "qTGW5", "head_start": 150, "head_end": 155, "head_type": "QTL",
   "tail": "GL", "tail_start": 113, "tail_end": 115, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(qGL1/qGL5/qTGW5, GL)

---

## 样本 7

**原文**：`Molecular markers are linked to morphological loci. The linkage map integrates data on quantitative traits with morphological variants and aids in map-based cloning of genes controlling morphological traits.`

**分析**：
- `Molecular markers`（@0:17）MRK 正确。
- `morphological loci`（@32:50）QTL 正确。
- `quantitative traits`（@87:106）TRT 正确。
- `morphological variants`（@112:134）TRT 正确。
- `map-based cloning`（@147:164）BM 正确。
- `morphological traits`（@186:206）TRT 正确。
- 关系：LOI(Molecular markers, morphological loci) 正确，保留。
- 无漏标。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 17,  "text": "Molecular markers", "label": "MRK"},
  {"start": 32,  "end": 50,  "text": "morphological loci", "label": "QTL"},
  {"start": 87,  "end": 106, "text": "quantitative traits", "label": "TRT"},
  {"start": 112, "end": 134, "text": "morphological variants", "label": "TRT"},
  {"start": 147, "end": 164, "text": "map-based cloning", "label": "BM"},
  {"start": 186, "end": 206, "text": "morphological traits", "label": "TRT"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "Molecular markers", "head_start": 0, "head_end": 17, "head_type": "MRK",
   "tail": "morphological loci", "tail_start": 32, "tail_end": 50, "tail_type": "QTL", "label": "LOI"}
]
```

---

## 样本 8

**原文**：`SbWRKY50 directly binds to the upstream promoter of the SOS1 gene in A. thaliana. In sweet sorghum, SbWRKY50 directly binds to the upstream promoters of SOS1 and HKT1.`

**分析**：
- `SbWRKY50`（@0:8、@100:108）GENE 正确。
- `SOS1`（@56:60、@153:157）GENE 正确。
- `A. thaliana`（@69:80）CROP 正确。
- `sweet sorghum`（@85:98）CROP 正确。
- `HKT1`（@162:166）GENE 正确。
- 原始关系为空，漏标：AFF(SbWRKY50, SOS1)；AFF(SbWRKY50, HKT1)

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 8,   "text": "SbWRKY50", "label": "GENE"},
  {"start": 56,  "end": 60,  "text": "SOS1", "label": "GENE"},
  {"start": 69,  "end": 80,  "text": "A. thaliana", "label": "CROP"},
  {"start": 85,  "end": 98,  "text": "sweet sorghum", "label": "CROP"},
  {"start": 100, "end": 108, "text": "SbWRKY50", "label": "GENE"},
  {"start": 153, "end": 157, "text": "SOS1", "label": "GENE"},
  {"start": 162, "end": 166, "text": "HKT1", "label": "GENE"}
]
```

> 无实体修改。

### relations（修订后完整列表）

```json
[
  {"head": "SbWRKY50", "head_start": 0, "head_end": 8, "head_type": "GENE",
   "tail": "SOS1", "tail_start": 56, "tail_end": 60, "tail_type": "GENE", "label": "AFF"},
  {"head": "SbWRKY50", "head_start": 100, "head_end": 108, "head_type": "GENE",
   "tail": "SOS1", "tail_start": 153, "tail_end": 157, "tail_type": "GENE", "label": "AFF"},
  {"head": "SbWRKY50", "head_start": 100, "head_end": 108, "head_type": "GENE",
   "tail": "HKT1", "tail_start": 162, "tail_end": 166, "tail_type": "GENE", "label": "AFF"}
]
```

> [新增] AFF(SbWRKY50, SOS1)（×2）；AFF(SbWRKY50, HKT1)

---

## 样本 9

**原文**：`The cultivation of oats has been affected by Septoria avenae f. sp. avenae, septoria leaf blotch disease.`

**分析**：
- `oats`（@19:23）CROP 正确。
- `Septoria avenae f. sp. avenae`（@45:74）BIS 正确。
- `septoria leaf blotch disease`（@76:104）BIS 正确。
- 关系均正确，保留。
- 无漏标。

### entities（修订后完整列表）

```json
[
  {"start": 19, "end": 23,  "text": "oats", "label": "CROP"},
  {"start": 45, "end": 74,  "text": "Septoria avenae f. sp. avenae", "label": "BIS"},
  {"start": 76, "end": 104, "text": "septoria leaf blotch disease", "label": "BIS"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "Septoria avenae f. sp. avenae", "head_start": 45, "head_end": 74, "head_type": "BIS",
   "tail": "oats", "tail_start": 19, "tail_end": 23, "tail_type": "CROP", "label": "AFF"},
  {"head": "septoria leaf blotch disease", "head_start": 76, "head_end": 104, "head_type": "BIS",
   "tail": "oats", "tail_start": 19, "tail_end": 23, "tail_type": "CROP", "label": "AFF"}
]
```

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增实体 | `GsNAC2-overexpressing sorghum` VAR；`plant height` TRT；`dry weight` TRT；`moisture content` TRT；`root activity` TRT；`leaf length` TRT；`chlorophyll content` TRT；`stomatal conductance` TRT |
| 0 | 新增关系 | AFF(GsNAC2, 7 个性状)；CON(sorghum, GsNAC2-overexpressing sorghum) |
| 1 | 新增实体 | `expression patterns` @37:55 TRT |
| 1 | 新增关系 | AFF(salt stress, salicylic acid)；AFF(salt stress, betaine) |
| 3 | 删除实体 | `R` @86:87 CROP |
| 3 | 新增实体 | `RSA traits` TRT；`GP accuracy` TRT；`NRA` TRT；`NNR` TRT；`NRL` TRT；`FSW` TRT；`DSW` TRT；`LA` TRT |
| 3 | 新增关系 | USE(GWAS, RSA traits)；USE(GWAS, GP accuracy) |
| 4 | 修改关系 | QTL AFF TRT → QTL LOI TRT（×5） |
| 5 | 修改实体 | `reduced plant height` → `plant height` @225:237；`reduced grain yield` → `grain yield` @251:262；`Setaria viridis` VAR → CROP |
| 5 | 新增实体 | `flowering time` @102:116 TRT；`early flowering` @200:215 TRT；`IP-MS` @292:297 BM |
| 5 | 新增关系 | AFF(SiUBC39, 6 个性状) |
| 6 | 新增实体 | `GL` @113:115 TRT |
| 6 | 新增关系 | LOI(qGL1/qGL5/qTGW5, GL) |
| 8 | 新增关系 | AFF(SbWRKY50, SOS1)（×2）；AFF(SbWRKY50, HKT1) |
