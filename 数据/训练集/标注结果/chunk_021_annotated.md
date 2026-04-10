# chunk_021 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`Transcriptome data before and after drought stress in foxtail millet hybrid Zhangza 19 and its parents identified 5597 DEGs. WGCNA screened 607 drought-tolerant genes. Heterotic genes were screened based on expression level.`

**分析**：
- `WGCNA`（@120:125）是加权基因共表达网络分析，属于遗传分析方法 BM，原始漏标。
- 验证：text[120:125] = "WGCNA" ✓
- `DEGs` 是差异表达基因集合，非具体基因，不标（error_patterns §2.1）。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 13,  "text": "Transcriptome", "label": "BM"},
  {"start": 36,  "end": 50,  "text": "drought stress", "label": "ABS"},
  {"start": 54,  "end": 68,  "text": "foxtail millet", "label": "CROP"},
  {"start": 76,  "end": 86,  "text": "Zhangza 19", "label": "VAR"},
  {"start": 120, "end": 125, "text": "WGCNA", "label": "BM"}
]
```

> [新增] `WGCNA` @120:125，BM

### relations（修订后完整列表）

```json
[
  {
    "head": "foxtail millet", "head_start": 54, "head_end": 68, "head_type": "CROP",
    "tail": "Zhangza 19", "tail_start": 76, "tail_end": 86, "tail_type": "VAR",
    "label": "CON"
  }
]
```

---

## 样本 1

**原文**：`Two multi-effect QTLs, Mqtl5-2 and Mqtl2-5, underlie panicle development and yield. One QTL, Mqtl1-2, is related to plant growth and development. Candidate genes for five major QTLs were discussed.`

**分析**：原始标注正确，无需修改。

### entities（修订后完整列表）

```json
[
  {"start": 23,  "end": 30,  "text": "Mqtl5-2", "label": "QTL"},
  {"start": 35,  "end": 42,  "text": "Mqtl2-5", "label": "QTL"},
  {"start": 53,  "end": 72,  "text": "panicle development", "label": "TRT"},
  {"start": 77,  "end": 82,  "text": "yield", "label": "TRT"},
  {"start": 93,  "end": 100, "text": "Mqtl1-2", "label": "QTL"},
  {"start": 116, "end": 144, "text": "plant growth and development", "label": "TRT"},
  {"start": 166, "end": 181, "text": "five major QTLs", "label": "QTL"}
]
```

### relations（修订后完整列表）

```json
[
  {"head": "Mqtl5-2", "head_start": 23, "head_end": 30, "head_type": "QTL",
   "tail": "panicle development", "tail_start": 53, "tail_end": 72, "tail_type": "TRT", "label": "LOI"},
  {"head": "Mqtl5-2", "head_start": 23, "head_end": 30, "head_type": "QTL",
   "tail": "yield", "tail_start": 77, "tail_end": 82, "tail_type": "TRT", "label": "LOI"},
  {"head": "Mqtl2-5", "head_start": 35, "head_end": 42, "head_type": "QTL",
   "tail": "panicle development", "tail_start": 53, "tail_end": 72, "tail_type": "TRT", "label": "LOI"},
  {"head": "Mqtl2-5", "head_start": 35, "head_end": 42, "head_type": "QTL",
   "tail": "yield", "tail_start": 77, "tail_end": 82, "tail_type": "TRT", "label": "LOI"},
  {"head": "Mqtl1-2", "head_start": 93, "head_end": 100, "head_type": "QTL",
   "tail": "plant growth and development", "tail_start": 116, "tail_end": 144, "tail_type": "TRT", "label": "LOI"}
]
```

---

## 样本 2

**原文**：`Two novel QTL clusters controlled NUE traits at seedling and maturity stages. Genes related to NUE traits were predicted in the major QTL intervals.`

**分析**：原始标注正确，无需修改。

### entities（修订后完整列表）

```json
[
  {"start": 10, "end": 13, "text": "QTL", "label": "QTL"},
  {"start": 34, "end": 44, "text": "NUE traits", "label": "TRT"},
  {"start": 48, "end": 56, "text": "seedling", "label": "GST"},
  {"start": 61, "end": 76, "text": "maturity stages", "label": "GST"},
  {"start": 95, "end": 105, "text": "NUE traits", "label": "TRT"}
]
```

### relations（修订后完整列表）

```json
[
  {"head": "NUE traits", "head_start": 34, "head_end": 44, "head_type": "TRT",
   "tail": "seedling", "tail_start": 48, "tail_end": 56, "tail_type": "GST", "label": "OCI"},
  {"head": "NUE traits", "head_start": 34, "head_end": 44, "head_type": "TRT",
   "tail": "maturity stages", "tail_start": 61, "tail_end": 76, "tail_type": "GST", "label": "OCI"},
  {"head": "QTL", "head_start": 10, "head_end": 13, "head_type": "QTL",
   "tail": "NUE traits", "tail_start": 34, "tail_end": 44, "tail_type": "TRT", "label": "LOI"}
]
```

---

## 样本 3

**原文**：`Tol showed important changes in metabolic pathways during heat shock (GST). These included up-regulation of raffinose family oligosaccharides and down-regulation of the gamma-aminobutyric acid catalytic pathway. Hexose sugar concentration became depleted. Tol tolerated elevated temperatures (ABS) due to up-regulation of osmoprotectants, chaperones, and reactive oxygen species scavengers and by suppression of SnRK1 (GENE) via transcripts and metabolites.`

**分析**：
- `Tol`（@0:3）是品种名，漏标为 VAR。验证：text[0:3]="Tol" ✓
- `Tol`（@253:256）同上。验证：text[253:256]="Tol" ✓
- `elevated temperatures`（@290:311）是非生物胁迫，漏标为 ABS。验证：text[290:311]="elevated temperatures" ✓
- `GENE`（@419:423）是原文括号内字面字符串，被错标为 VAR，应删除。
- `heat shock`（@58:68）已正确标为 ABS，`SnRK1`（@412:417）已正确标为 GENE。
- 新增关系：原文"suppression of SnRK1 (GENE) via transcripts and metabolites"在热胁迫语境下，AFF(heat shock, SnRK1) 符合训练集 AFF:ABS→GENE 模式（error_patterns §1.1）。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 3,   "text": "Tol", "label": "VAR"},
  {"start": 58,  "end": 68,  "text": "heat shock", "label": "ABS"},
  {"start": 253, "end": 256, "text": "Tol", "label": "VAR"},
  {"start": 290, "end": 311, "text": "elevated temperatures", "label": "ABS"},
  {"start": 412, "end": 417, "text": "SnRK1", "label": "GENE"}
]
```

> [新增] `Tol` @0:3 VAR；[新增] `Tol` @253:256 VAR；[新增] `elevated temperatures` @290:311 ABS；[删除] `GENE` @419:423 VAR（字面字符串）

### relations（修订后完整列表）

```json
[
  {
    "head": "heat shock", "head_start": 58, "head_end": 68, "head_type": "ABS",
    "tail": "SnRK1", "tail_start": 412, "tail_end": 417, "tail_type": "GENE",
    "label": "AFF"
  }
]
```

> [新增] AFF(heat shock, SnRK1)

---

## 样本 4

**原文**：`In the germination stage, SbNAC56 overexpression transgenic lines exhibited enhanced hypersensitivities to ABA, NaCl and d-Mannitol. This indicates SbNAC56 plays roles in plant response to abiotic stresses in an ABA dependent signaling pathway.`

**分析**：
- `ABA`（@107:110）是脱落酸，在胁迫响应语境中作为非生物胁迫信号分子，漏标为 ABS。验证：text[107:110]="ABA" ✓
- `ABA`（@213:216）同上。验证：text[213:216]="ABA" ✓
- 原有关系 AFF(SbNAC56@26:33, abiotic stresses@189:205) 保留（训练集 AFF:GENE→ABS 模式）。

### entities（修订后完整列表）

```json
[
  {"start": 7,   "end": 24,  "text": "germination stage", "label": "GST"},
  {"start": 26,  "end": 33,  "text": "SbNAC56", "label": "GENE"},
  {"start": 107, "end": 110, "text": "ABA", "label": "ABS"},
  {"start": 112, "end": 116, "text": "NaCl", "label": "ABS"},
  {"start": 121, "end": 131, "text": "d-Mannitol", "label": "ABS"},
  {"start": 148, "end": 155, "text": "SbNAC56", "label": "GENE"},
  {"start": 189, "end": 205, "text": "abiotic stresses", "label": "ABS"},
  {"start": 213, "end": 216, "text": "ABA", "label": "ABS"}
]
```

> [新增] `ABA` @107:110 ABS；[新增] `ABA` @213:216 ABS

### relations（修订后完整列表）

```json
[
  {
    "head": "SbNAC56", "head_start": 26, "head_end": 33, "head_type": "GENE",
    "tail": "abiotic stresses", "tail_start": 189, "tail_end": 205, "tail_type": "ABS",
    "label": "AFF"
  }
]
```

---

## 样本 5

**原文**：`A genome-wide association study (GWAS) and a candidate gene-based association analysis were conducted on 59 cultivated and 99 Tibetan wild barley genotypes to identify molecular markers associated with grain protein content (GPC). Tibetan wild barley had higher GPC than cultivated barley. GPC was significantly correlated with diastatic power (DP) and malt extract, confirming its importance for malt quality.`

**分析**：
- `cultivated barley`（@271:288）标为 VAR，但"cultivated barley"是大麦栽培类型名，应改为 CROP（K8 §1.1；error_patterns §2.4）。验证：text[271:288]="cultivated barley" ✓
- `barley`（整体作物）未出现独立标注，不补（原文中 barley 出现在复合词中）。
- 其余实体与关系正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 2,   "end": 38,  "text": "genome-wide association study (GWAS)", "label": "BM"},
  {"start": 43,  "end": 86,  "text": "a candidate gene-based association analysis", "label": "BM"},
  {"start": 126, "end": 145, "text": "Tibetan wild barley", "label": "VAR"},
  {"start": 202, "end": 229, "text": "grain protein content (GPC)", "label": "TRT"},
  {"start": 231, "end": 250, "text": "Tibetan wild barley", "label": "VAR"},
  {"start": 271, "end": 288, "text": "cultivated barley", "label": "CROP"},
  {"start": 290, "end": 293, "text": "GPC", "label": "TRT"},
  {"start": 328, "end": 348, "text": "diastatic power (DP)", "label": "TRT"},
  {"start": 353, "end": 365, "text": "malt extract", "label": "TRT"},
  {"start": 397, "end": 409, "text": "malt quality", "label": "TRT"}
]
```

> [修改] `cultivated barley` @271:288 VAR → CROP

### relations（修订后完整列表）

```json
[
  {"head": "Tibetan wild barley", "head_start": 126, "head_end": 145, "head_type": "VAR",
   "tail": "grain protein content (GPC)", "tail_start": 202, "tail_end": 229, "tail_type": "TRT", "label": "HAS"},
  {"head": "Tibetan wild barley", "head_start": 126, "head_end": 145, "head_type": "VAR",
   "tail": "GPC", "tail_start": 290, "tail_end": 293, "tail_type": "TRT", "label": "HAS"},
  {"head": "GPC", "head_start": 290, "head_end": 293, "head_type": "TRT",
   "tail": "diastatic power (DP)", "tail_start": 328, "tail_end": 348, "tail_type": "TRT", "label": "AFF"},
  {"head": "GPC", "head_start": 290, "head_end": 293, "head_type": "TRT",
   "tail": "malt extract", "tail_start": 353, "tail_end": 365, "tail_type": "TRT", "label": "AFF"},
  {"head": "GPC", "head_start": 290, "head_end": 293, "head_type": "TRT",
   "tail": "malt quality", "tail_start": 397, "tail_end": 409, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 6

**原文**：`The study mapped QTLs for resistance to B. fusca and C. partellus in sorghum. It used 243 F-9:10 sorghum RILs from ICSV 745 and PB 15520-1 with 4,955 SNP markers.`

**分析**：
- `B. fusca`（@40:48）是高粱茎螟，生物胁迫，漏标为 BIS。验证：text[40:48]="B. fusca" ✓
- `C. partellus`（@53:65）是玉米螟，生物胁迫，漏标为 BIS。验证：text[53:65]="C. partellus" ✓
- `SNP`（@150:153）边界偏短，应扩展为 `SNP markers`（@150:161）。验证：text[150:161]="SNP markers" ✓
- 新增关系：QTLs 定位于对 B. fusca 和 C. partellus 的抗性（LOI 关系）。

### entities（修订后完整列表）

```json
[
  {"start": 17,  "end": 21,  "text": "QTLs", "label": "QTL"},
  {"start": 40,  "end": 48,  "text": "B. fusca", "label": "BIS"},
  {"start": 53,  "end": 65,  "text": "C. partellus", "label": "BIS"},
  {"start": 69,  "end": 76,  "text": "sorghum", "label": "CROP"},
  {"start": 90,  "end": 109, "text": "F-9:10 sorghum RILs", "label": "CROSS"},
  {"start": 115, "end": 123, "text": "ICSV 745", "label": "VAR"},
  {"start": 128, "end": 138, "text": "PB 15520-1", "label": "VAR"},
  {"start": 150, "end": 161, "text": "SNP markers", "label": "MRK"}
]
```

> [新增] `B. fusca` @40:48 BIS；[新增] `C. partellus` @53:65 BIS；[修改] `SNP`→`SNP markers` @150:161

### relations（修订后完整列表）

```json
[
  {"head": "sorghum", "head_start": 69, "head_end": 76, "head_type": "CROP",
   "tail": "F-9:10 sorghum RILs", "tail_start": 90, "tail_end": 109, "tail_type": "CROSS", "label": "CON"},
  {"head": "sorghum", "head_start": 69, "head_end": 76, "head_type": "CROP",
   "tail": "ICSV 745", "tail_start": 115, "tail_end": 123, "tail_type": "VAR", "label": "CON"},
  {"head": "sorghum", "head_start": 69, "head_end": 76, "head_type": "CROP",
   "tail": "PB 15520-1", "tail_start": 128, "tail_end": 138, "tail_type": "VAR", "label": "CON"},
  {"head": "QTLs", "head_start": 17, "head_end": 21, "head_type": "QTL",
   "tail": "B. fusca", "tail_start": 40, "tail_end": 48, "tail_type": "BIS", "label": "LOI"},
  {"head": "QTLs", "head_start": 17, "head_end": 21, "head_type": "QTL",
   "tail": "C. partellus", "tail_start": 53, "tail_end": 65, "tail_type": "BIS", "label": "LOI"}
]
```

> [新增] LOI(QTLs, B. fusca)；[新增] LOI(QTLs, C. partellus)

---

## 样本 7

**原文**：`Chromosomes 1, 2, 3, 4, and 6 harbored SNPs significant for Striga tolerance in sorghum. Significant SNPs were found for plant height (4), panicle height (3), leaves per plant (2), foliar fresh grain weight (8), dry grain weight (2), and chlorophyll content (3).`

**分析**：
- `Striga tolerance`（@60:76）整体是抗性性状，应标为 TRT（K7 §2.1）。原始只标了 `Striga`（BIS），两者可并存（嵌套）。验证：text[60:76]="Striga tolerance" ✓
- `leaves per plant`（@159:175）是农艺性状，漏标为 TRT。验证：text[159:175]="leaves per plant" ✓
- 补充 SNPs 与各 TRT 的 LOI 关系（原始仅有 LOI(SNPs, CHR)，漏标了与各性状的关联）。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 29,  "text": "Chromosomes 1, 2, 3, 4, and 6", "label": "CHR"},
  {"start": 39,  "end": 43,  "text": "SNPs", "label": "MRK"},
  {"start": 60,  "end": 66,  "text": "Striga", "label": "BIS"},
  {"start": 60,  "end": 76,  "text": "Striga tolerance", "label": "TRT"},
  {"start": 80,  "end": 87,  "text": "sorghum", "label": "CROP"},
  {"start": 121, "end": 133, "text": "plant height", "label": "TRT"},
  {"start": 139, "end": 153, "text": "panicle height", "label": "TRT"},
  {"start": 159, "end": 175, "text": "leaves per plant", "label": "TRT"},
  {"start": 181, "end": 206, "text": "foliar fresh grain weight", "label": "TRT"},
  {"start": 212, "end": 228, "text": "dry grain weight", "label": "TRT"},
  {"start": 238, "end": 257, "text": "chlorophyll content", "label": "TRT"}
]
```

> [新增] `Striga tolerance` @60:76 TRT；[新增] `leaves per plant` @159:175 TRT

### relations（修订后完整列表）

```json
[
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "Chromosomes 1, 2, 3, 4, and 6", "tail_start": 0, "tail_end": 29, "tail_type": "CHR", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "Striga tolerance", "tail_start": 60, "tail_end": 76, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "plant height", "tail_start": 121, "tail_end": 133, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "panicle height", "tail_start": 139, "tail_end": 153, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "leaves per plant", "tail_start": 159, "tail_end": 175, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "foliar fresh grain weight", "tail_start": 181, "tail_end": 206, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "dry grain weight", "tail_start": 212, "tail_end": 228, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 39, "head_end": 43, "head_type": "MRK",
   "tail": "chlorophyll content", "tail_start": 238, "tail_end": 257, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(SNPs, Striga tolerance)；[新增] LOI(SNPs, leaves per plant)；[新增] LOI(SNPs, 各TRT) 共 6 条

---

## 样本 8

**原文**：`SNPs from auxin-related genes, including auxin efflux carrier protein (PIN3), p-glycoprotein, and nodulin MtN21/EamA-like transporter, were associated with yield and yield-related traits under drought. Four genetic regions contained SNPs associated with several different traits, indicating pleiotropic effects.`

**分析**：原始标注正确，无需修改。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 4,   "text": "SNPs", "label": "MRK"},
  {"start": 41,  "end": 76,  "text": "auxin efflux carrier protein (PIN3)", "label": "GENE"},
  {"start": 78,  "end": 92,  "text": "p-glycoprotein", "label": "GENE"},
  {"start": 98,  "end": 133, "text": "nodulin MtN21/EamA-like transporter", "label": "GENE"},
  {"start": 156, "end": 161, "text": "yield", "label": "TRT"},
  {"start": 166, "end": 186, "text": "yield-related traits", "label": "TRT"},
  {"start": 193, "end": 200, "text": "drought", "label": "ABS"},
  {"start": 207, "end": 222, "text": "genetic regions", "label": "QTL"},
  {"start": 233, "end": 237, "text": "SNPs", "label": "MRK"}
]
```

### relations（修订后完整列表）

```json
[
  {"head": "SNPs", "head_start": 0, "head_end": 4, "head_type": "MRK",
   "tail": "yield", "tail_start": 156, "tail_end": 161, "tail_type": "TRT", "label": "LOI"},
  {"head": "SNPs", "head_start": 0, "head_end": 4, "head_type": "MRK",
   "tail": "yield-related traits", "tail_start": 166, "tail_end": 186, "tail_type": "TRT", "label": "LOI"},
  {"head": "drought", "head_start": 193, "head_end": 200, "head_type": "ABS",
   "tail": "yield", "tail_start": 156, "tail_end": 161, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought", "head_start": 193, "head_end": 200, "head_type": "ABS",
   "tail": "yield-related traits", "tail_start": 166, "tail_end": 186, "tail_type": "TRT", "label": "AFF"},
  {"head": "genetic regions", "head_start": 207, "head_end": 222, "head_type": "QTL",
   "tail": "SNPs", "tail_start": 233, "tail_end": 237, "tail_type": "MRK", "label": "CON"}
]
```

---

## 样本 9

**原文**：`A recombinant inbred line (RIL) population of 189 individuals was derived from a cross between the sweet sorghum cultivar 'Rio' and the grain sorghum 'BTx623'. Plant height, Brix, 100-grain weight, and flowering time were evaluated over 3 years.`

**分析**：
- `Rio`（@122:125）是甜高粱品种，漏标为 VAR。验证：text[122:125]="Rio" ✓
- `Brix`（@174:178）是糖度性状，漏标为 TRT。验证：text[174:178]="Brix" ✓
- `flowering time`（@202:216）是开花时间性状，漏标为 TRT。验证：text[202:216]="flowering time" ✓
- 新增关系：sweet sorghum CON Rio；BTx623 HAS Brix；BTx623 HAS flowering time。

### entities（修订后完整列表）

```json
[
  {"start": 2,   "end": 42,  "text": "recombinant inbred line (RIL) population", "label": "CROSS"},
  {"start": 99,  "end": 112, "text": "sweet sorghum", "label": "CROP"},
  {"start": 122, "end": 125, "text": "Rio", "label": "VAR"},
  {"start": 136, "end": 149, "text": "grain sorghum", "label": "CROP"},
  {"start": 151, "end": 157, "text": "BTx623", "label": "VAR"},
  {"start": 160, "end": 172, "text": "Plant height", "label": "TRT"},
  {"start": 174, "end": 178, "text": "Brix", "label": "TRT"},
  {"start": 180, "end": 196, "text": "100-grain weight", "label": "TRT"},
  {"start": 202, "end": 216, "text": "flowering time", "label": "TRT"}
]
```

> [新增] `Rio` @122:125 VAR；[新增] `Brix` @174:178 TRT；[新增] `flowering time` @202:216 TRT

### relations（修订后完整列表）

```json
[
  {"head": "sweet sorghum", "head_start": 99, "head_end": 112, "head_type": "CROP",
   "tail": "Rio", "tail_start": 122, "tail_end": 125, "tail_type": "VAR", "label": "CON"},
  {"head": "grain sorghum", "head_start": 136, "head_end": 149, "head_type": "CROP",
   "tail": "BTx623", "tail_start": 151, "tail_end": 157, "tail_type": "VAR", "label": "CON"},
  {"head": "BTx623", "head_start": 151, "head_end": 157, "head_type": "VAR",
   "tail": "Plant height", "tail_start": 160, "tail_end": 172, "tail_type": "TRT", "label": "HAS"},
  {"head": "BTx623", "head_start": 151, "head_end": 157, "head_type": "VAR",
   "tail": "Brix", "tail_start": 174, "tail_end": 178, "tail_type": "TRT", "label": "HAS"},
  {"head": "BTx623", "head_start": 151, "head_end": 157, "head_type": "VAR",
   "tail": "100-grain weight", "tail_start": 180, "tail_end": 196, "tail_type": "TRT", "label": "HAS"},
  {"head": "BTx623", "head_start": 151, "head_end": 157, "head_type": "VAR",
   "tail": "flowering time", "tail_start": 202, "tail_end": 216, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] CON(sweet sorghum, Rio)；[新增] HAS(BTx623, Brix)；[新增] HAS(BTx623, flowering time)

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增实体 | `WGCNA` BM |
| 3 | 新增实体 | `Tol` VAR ×2；`elevated temperatures` ABS |
| 3 | 删除实体 | `GENE` VAR（字面字符串） |
| 3 | 新增关系 | AFF(heat shock, SnRK1) |
| 4 | 新增实体 | `ABA` ABS ×2 |
| 5 | 修改标签 | `cultivated barley` VAR→CROP |
| 6 | 新增实体 | `B. fusca` BIS；`C. partellus` BIS |
| 6 | 修改边界 | `SNP`→`SNP markers` |
| 6 | 新增关系 | LOI(QTLs, B. fusca)；LOI(QTLs, C. partellus) |
| 7 | 新增实体 | `Striga tolerance` TRT；`leaves per plant` TRT |
| 7 | 新增关系 | LOI(SNPs, 各TRT) ×8 |
| 9 | 新增实体 | `Rio` VAR；`Brix` TRT；`flowering time` TRT |
| 9 | 新增关系 | CON(sweet sorghum, Rio)；HAS(BTx623, Brix)；HAS(BTx623, flowering time) |
