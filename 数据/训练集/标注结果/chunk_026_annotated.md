# chunk_026 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`A two-year experiment under acidic conditions measured 12 yield-related traits in the F2 and F3 populations of the cross E232 x Murasakimochi and its reciprocal cross. The phenotypic coefficient of variation was high.`

**分析**：
- `F2`（@86:88）CROSS 正确。
- `F3`（@93:95）CROSS 正确。
- `E232`（@121:125）VAR 正确。
- `E232 x Murasakimochi`（@121:141）CROSS 正确（与 E232 VAR 嵌套共存）。
- `Murasakimochi`（@128:141）VAR 正确（与 CROSS 嵌套共存）。
- 漏标：`acidic conditions`（@24:40）是酸性土壤胁迫，应标为 ABS。验证：text[24:40]="acidic conditions" ✓
- 漏标：`yield-related traits`（@55:74）是产量相关性状，应标为 TRT。验证：text[55:74]="yield-related traits" ✓
- 漏标关系：HAS(E232 x Murasakimochi, yield-related traits)。

### entities（修订后完整列表）

```json
[
  {"start": 24,  "end": 40,  "text": "acidic conditions", "label": "ABS"},
  {"start": 55,  "end": 74,  "text": "yield-related traits", "label": "TRT"},
  {"start": 86,  "end": 88,  "text": "F2", "label": "CROSS"},
  {"start": 93,  "end": 95,  "text": "F3", "label": "CROSS"},
  {"start": 121, "end": 125, "text": "E232", "label": "VAR"},
  {"start": 121, "end": 141, "text": "E232 x Murasakimochi", "label": "CROSS"},
  {"start": 128, "end": 141, "text": "Murasakimochi", "label": "VAR"}
]
```

> [新增] `acidic conditions` @24:40 ABS；[新增] `yield-related traits` @55:74 TRT

### relations（修订后完整列表）

```json
[
  {"head": "E232 x Murasakimochi", "head_start": 121, "head_end": 141, "head_type": "CROSS",
   "tail": "yield-related traits", "tail_start": 55, "tail_end": 74, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] HAS(E232 x Murasakimochi, yield-related traits)

---

## 样本 1

**原文**：`This study mapped QTLs for agronomic and yield traits using three connected mapping populations of different genetic backgrounds in Ethiopian sorghum germplasm. The three bi-parental populations, each with 207 F 2:3 lines, were evaluated under two moisture stress environments.`

**分析**：
- `QTLs`（@18:22）QTL 正确。
- `agronomic and yield traits`（@27:53）TRT 正确。
- `Ethiopian sorghum germplasm`（@132:159）标为 CROP，但这是种质资源库，不是具体作物名称，应改为 VAR（种质库标为 VAR）。
- `moisture stress`（@248:263）ABS 正确。
- 漏标：`sorghum`（@141:148）是作物名称，应单独标为 CROP。验证：text[141:148]="sorghum" ✓
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 18,  "end": 22,  "text": "QTLs", "label": "QTL"},
  {"start": 27,  "end": 53,  "text": "agronomic and yield traits", "label": "TRT"},
  {"start": 132, "end": 159, "text": "Ethiopian sorghum germplasm", "label": "VAR"},
  {"start": 141, "end": 148, "text": "sorghum", "label": "CROP"},
  {"start": 248, "end": 263, "text": "moisture stress", "label": "ABS"}
]
```

> [修改] `Ethiopian sorghum germplasm` CROP→VAR；[新增] `sorghum` @141:148 CROP

### relations（修订后完整列表）

```json
[
  {"head": "QTLs", "head_start": 18, "head_end": 22, "head_type": "QTL",
   "tail": "agronomic and yield traits", "tail_start": 27, "tail_end": 53, "tail_type": "TRT", "label": "LOI"},
  {"head": "moisture stress", "head_start": 248, "head_end": 263, "head_type": "ABS",
   "tail": "agronomic and yield traits", "tail_start": 27, "tail_end": 53, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 2

**原文**：`Transcriptomic analysis revealed enriched metabolic pathways in L4 seeds: flavonoid biosynthesis, TCA cycle, and terpenoid backbone biosynthesis. L1 seeds showed enriched carbon metabolism. Key genes involved include CHS, CHI, AACT, ENO1, IDH, NADP-ME, and HAO2L. Aging may adversely affect flavonoids and terpenoids, contributing to vigor loss in storage-sensitive seeds. Storage-tolerant seeds maintain carbon metabolism and energy supply.`

**分析**：
- `L4 seeds`（@64:72）标为 VAR，但 L4 seeds 是种子批次/类型，不是品种，应标为 VAR（种质材料）。保留。
- `L1 seeds`（@146:154）VAR 正确。
- `CHS`（@217:220）GENE 正确。
- `ENO1`（@233:237）GENE 正确。
- `HAO2L`（@257:262）GENE 正确。
- 漏标：`Transcriptomic analysis`（@0:21）是分析方法，应标为 BM。验证：text[0:21]="Transcriptomic analysis" ✓
- 漏标：`CHI`（@222:225）是基因，应标为 GENE。验证：text[222:225]="CHI" ✓
- 漏标：`AACT`（@227:231）是基因，应标为 GENE。验证：text[227:231]="AACT" ✓
- 漏标：`IDH`（@239:242）是基因，应标为 GENE。验证：text[239:242]="IDH" ✓
- 漏标：`NADP-ME`（@244:251）是基因，应标为 GENE。验证：text[244:251]="NADP-ME" ✓
- 漏标：`flavonoid biosynthesis`（@75:96）是代谢通路/性状，应标为 TRT。验证：text[75:96]="flavonoid biosynthesis" ✓
- 漏标：`vigor loss`（@332:342）是种子活力性状，应标为 TRT。验证：text[332:342]="vigor loss" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 21,  "text": "Transcriptomic analysis", "label": "BM"},
  {"start": 64,  "end": 72,  "text": "L4 seeds", "label": "VAR"},
  {"start": 75,  "end": 96,  "text": "flavonoid biosynthesis", "label": "TRT"},
  {"start": 146, "end": 154, "text": "L1 seeds", "label": "VAR"},
  {"start": 217, "end": 220, "text": "CHS", "label": "GENE"},
  {"start": 222, "end": 225, "text": "CHI", "label": "GENE"},
  {"start": 227, "end": 231, "text": "AACT", "label": "GENE"},
  {"start": 233, "end": 237, "text": "ENO1", "label": "GENE"},
  {"start": 239, "end": 242, "text": "IDH", "label": "GENE"},
  {"start": 244, "end": 251, "text": "NADP-ME", "label": "GENE"},
  {"start": 257, "end": 262, "text": "HAO2L", "label": "GENE"},
  {"start": 332, "end": 342, "text": "vigor loss", "label": "TRT"}
]
```

> [新增] `Transcriptomic analysis` @0:21 BM；`CHI` @222:225 GENE；`AACT` @227:231 GENE；`IDH` @239:242 GENE；`NADP-ME` @244:251 GENE；`flavonoid biosynthesis` @75:96 TRT；`vigor loss` @332:342 TRT

### relations（修订后完整列表）

```json
[
  {"head": "CHS", "head_start": 217, "head_end": 220, "head_type": "GENE",
   "tail": "flavonoid biosynthesis", "tail_start": 75, "tail_end": 96, "tail_type": "TRT", "label": "AFF"},
  {"head": "CHI", "head_start": 222, "head_end": 225, "head_type": "GENE",
   "tail": "flavonoid biosynthesis", "tail_start": 75, "tail_end": 96, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(CHS, flavonoid biosynthesis)；AFF(CHI, flavonoid biosynthesis)

---

## 样本 3

**原文**：`The best location for planting strip-tilled fertilized corn varies with soil and climatic conditions and the time between fertilizer application and planting. With fewer days, planting directly on the center of the fertilized strip-till decreased plant population and grain yield.`

**分析**：
- `corn`（@55:59）CROP 正确。
- `strip-till`（@226:236）BM 正确（条带耕作是农业管理方法）。
- `plant population`（@247:263）TRT 正确。
- `grain yield`（@268:279）TRT 正确。
- 关系：HAS(corn, plant population)、HAS(corn, grain yield) 正确，保留。
- 无其他漏标。

### entities（修订后完整列表）

```json
[
  {"start": 55,  "end": 59,  "text": "corn", "label": "CROP"},
  {"start": 226, "end": 236, "text": "strip-till", "label": "BM"},
  {"start": 247, "end": 263, "text": "plant population", "label": "TRT"},
  {"start": 268, "end": 279, "text": "grain yield", "label": "TRT"}
]
```

> 无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "corn", "head_start": 55, "head_end": 59, "head_type": "CROP",
   "tail": "plant population", "tail_start": 247, "tail_end": 263, "tail_type": "TRT", "label": "HAS"},
  {"head": "corn", "head_start": 55, "head_end": 59, "head_type": "CROP",
   "tail": "grain yield", "tail_start": 268, "tail_end": 279, "tail_type": "TRT", "label": "HAS"}
]
```

---

## 样本 4

**原文**：`145 VfAP2/ERFs were identified and are unevenly distributed across six chromosomes. Phylogenetic analysis classified them into five subgroups. Cis-elements analysis found VfAP2/ERF promoters contain elements related to light response, plant hormone, abiotic stress response, and plant growth and development.`

**分析**：
- `VfAP2/ERFs`（@4:14）GENE 正确。
- `six chromosomes`（@67:82）CHR 正确。
- `light response`（@219:233）标为 TRT，但 light response 是光响应，是基因表达调控的生物学过程，不是农艺性状，应删除。
- `plant hormone`（@235:248）标为 TRT，但 plant hormone 是植物激素类别，不是具体性状，应删除。
- `abiotic stress response`（@250:273）标为 TRT，但这是基因功能描述，不是农艺性状，应删除。
- `plant growth and development`（@279:307）标为 TRT，但这是生物学过程描述，不是具体可量化性状，应删除。
- 漏标：`Phylogenetic analysis`（@84:104）是分析方法，应标为 BM。验证：text[84:104]="Phylogenetic analysis" ✓
- 漏标：`VfAP2/ERF`（@169:178）第二次出现（"VfAP2/ERF promoters"），应标为 GENE。验证：text[169:178]="VfAP2/ERF" ✓

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 14,  "text": "VfAP2/ERFs", "label": "GENE"},
  {"start": 67,  "end": 82,  "text": "six chromosomes", "label": "CHR"},
  {"start": 84,  "end": 104, "text": "Phylogenetic analysis", "label": "BM"},
  {"start": 169, "end": 178, "text": "VfAP2/ERF", "label": "GENE"}
]
```

> [删除] `light response` @219:233 TRT；[删除] `plant hormone` @235:248 TRT；[删除] `abiotic stress response` @250:273 TRT；[删除] `plant growth and development` @279:307 TRT；[新增] `Phylogenetic analysis` @84:104 BM；[新增] `VfAP2/ERF` @169:178 GENE

### relations（修订后完整列表）

```json
[
  {"head": "VfAP2/ERFs", "head_start": 4, "head_end": 14, "head_type": "GENE",
   "tail": "six chromosomes", "tail_start": 67, "tail_end": 82, "tail_type": "CHR", "label": "LOI"}
]
```

---

## 样本 5

**原文**：`SG QTL were mapped near previously reported chromosomal regions. Two heat-stress QTL were mapped to bPb-5529 on 5H, adjacent to QTL for root length and root-shoot ratio. SG QTL detection in barley under heat- and water-stressed conditions enables high throughput screening for these traits.`

**分析**：
- `SG QTL`（@0:6）QTL 正确。
- `heat-stress QTL`（@69:84）QTL 正确。
- `5H`（@112:114）CHR 正确。
- `root length`（@136:147）TRT 正确。
- `root-shoot ratio`（@152:168）TRT 正确。
- `barley`（@190:196）CROP 正确。
- `heat-`（@203:208）标为 ABS，但 "heat-" 是形容词前缀，不是独立的胁迫实体，应删除。
- 漏标：`bPb-5529`（@101:109）是分子标记，应标为 MRK。验证：text[101:109]="bPb-5529" ✓
- 漏标：`SG QTL`（@170:176）第二次出现，应标为 QTL。验证：text[170:176]="SG QTL" ✓
- 漏标关系：LOI(SG QTL, 5H)；LOI(heat-stress QTL, root length)；LOI(heat-stress QTL, root-shoot ratio)。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 6,   "text": "SG QTL", "label": "QTL"},
  {"start": 69,  "end": 84,  "text": "heat-stress QTL", "label": "QTL"},
  {"start": 101, "end": 109, "text": "bPb-5529", "label": "MRK"},
  {"start": 112, "end": 114, "text": "5H", "label": "CHR"},
  {"start": 136, "end": 147, "text": "root length", "label": "TRT"},
  {"start": 152, "end": 168, "text": "root-shoot ratio", "label": "TRT"},
  {"start": 170, "end": 176, "text": "SG QTL", "label": "QTL"},
  {"start": 190, "end": 196, "text": "barley", "label": "CROP"}
]
```

> [删除] `heat-` @203:208 ABS；[新增] `bPb-5529` @101:109 MRK；[新增] `SG QTL` @170:176 QTL

### relations（修订后完整列表）

```json
[
  {"head": "SG QTL", "head_start": 0, "head_end": 6, "head_type": "QTL",
   "tail": "5H", "tail_start": 112, "tail_end": 114, "tail_type": "CHR", "label": "LOI"},
  {"head": "heat-stress QTL", "head_start": 69, "head_end": 84, "head_type": "QTL",
   "tail": "bPb-5529", "tail_start": 101, "tail_end": 109, "tail_type": "MRK", "label": "LOI"},
  {"head": "heat-stress QTL", "head_start": 69, "head_end": 84, "head_type": "QTL",
   "tail": "5H", "tail_start": 112, "tail_end": 114, "tail_type": "CHR", "label": "LOI"},
  {"head": "heat-stress QTL", "head_start": 69, "head_end": 84, "head_type": "QTL",
   "tail": "root length", "tail_start": 136, "tail_end": 147, "tail_type": "TRT", "label": "LOI"},
  {"head": "heat-stress QTL", "head_start": 69, "head_end": 84, "head_type": "QTL",
   "tail": "root-shoot ratio", "tail_start": 152, "tail_end": 168, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(SG QTL, 5H)；LOI(heat-stress QTL, bPb-5529)；LOI(heat-stress QTL, 5H)；LOI(heat-stress QTL, root length)；LOI(heat-stress QTL, root-shoot ratio)

---

## 样本 6

**原文**：`IP-MS and transcriptome analysis revealed that SiUBC39 is involved in growth and development regulation, drought stress response, and immune response. SiPIP2;1 and SiEhd2 were identified as interactors of SiUBC39, explaining its roles in blast resistance and flowering time control. Domestication analysis identified an A/G mutation in the SiUBC39 promoter TATA box, distinguishing domesticated and wild haplotypes and highlighting its role in domestication selection.`

**分析**：
- `transcriptome`（@10:23）BM 正确。
- `SiUBC39`（@47:54、@205:212、@340:347）GENE 正确。
- `drought stress`（@105:119）ABS 正确。
- `immune response`（@134:149）标为 BIS，但 immune response 是免疫响应，是生物学过程，不是具体病害，应改为 TRT（免疫响应是可量化的性状表现）。
- `SiPIP2;1`（@151:159）GENE 正确。
- `SiEhd2`（@164:170）GENE 正确。
- `blast`（@238:243）BIS 正确（稻瘟病）。
- `flowering time`（@259:273）TRT 正确。
- 漏标：`IP-MS`（@0:5）是蛋白质互作分析方法，应标为 BM。验证：text[0:5]="IP-MS" ✓
- 漏标：`blast resistance`（@238:253）整体是抗稻瘟病性状，应标为 TRT（与 blast BIS 嵌套共存）。验证：text[238:253]="blast resistance" ✓
- 关系：AFF(SiUBC39, drought stress) 方向有误，AFF 的 tail 应为 TRT，不能为 ABS。应改为 AFF(drought stress, drought stress response)，但 "drought stress response" 未标注。应补标 `drought stress response`（@105:128）TRT。验证：text[105:128]="drought stress response" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 5,   "text": "IP-MS", "label": "BM"},
  {"start": 10,  "end": 23,  "text": "transcriptome", "label": "BM"},
  {"start": 47,  "end": 54,  "text": "SiUBC39", "label": "GENE"},
  {"start": 105, "end": 119, "text": "drought stress", "label": "ABS"},
  {"start": 105, "end": 128, "text": "drought stress response", "label": "TRT"},
  {"start": 134, "end": 149, "text": "immune response", "label": "TRT"},
  {"start": 151, "end": 159, "text": "SiPIP2;1", "label": "GENE"},
  {"start": 164, "end": 170, "text": "SiEhd2", "label": "GENE"},
  {"start": 205, "end": 212, "text": "SiUBC39", "label": "GENE"},
  {"start": 238, "end": 243, "text": "blast", "label": "BIS"},
  {"start": 238, "end": 253, "text": "blast resistance", "label": "TRT"},
  {"start": 259, "end": 273, "text": "flowering time", "label": "TRT"},
  {"start": 340, "end": 347, "text": "SiUBC39", "label": "GENE"}
]
```

> [新增] `IP-MS` @0:5 BM；[新增] `drought stress response` @105:128 TRT；[修改] `immune response` BIS→TRT；[新增] `blast resistance` @238:253 TRT

### relations（修订后完整列表）

```json
[
  {"head": "SiUBC39", "head_start": 47, "head_end": 54, "head_type": "GENE",
   "tail": "drought stress response", "tail_start": 105, "tail_end": 128, "tail_type": "TRT", "label": "AFF"},
  {"head": "drought stress", "head_start": 105, "head_end": 119, "head_type": "ABS",
   "tail": "drought stress response", "tail_start": 105, "tail_end": 128, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 47, "head_end": 54, "head_type": "GENE",
   "tail": "immune response", "tail_start": 134, "tail_end": 149, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 47, "head_end": 54, "head_type": "GENE",
   "tail": "flowering time", "tail_start": 259, "tail_end": 273, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiUBC39", "head_start": 47, "head_end": 54, "head_type": "GENE",
   "tail": "blast resistance", "tail_start": 238, "tail_end": 253, "tail_type": "TRT", "label": "AFF"}
]
```

> [修改] AFF(SiUBC39, drought stress) → AFF(SiUBC39, drought stress response)；[新增] AFF(drought stress, drought stress response)；[新增] AFF(SiUBC39, blast resistance)

---

## 样本 7

**原文**：`Phylogenetic analysis assigned eight FtNAC TFs to three abiotic stress-related subgroups. The relative expression levels of FtNAC genes were analyzed under abiotic stresses (salt, drought, cold, ultraviolet B) and exogenous phytohormones (abscisic acid, methyl jasmonate, salicylic acid).`

**分析**：
- `FtNAC TFs`（@37:46）GENE 正确。
- `FtNAC`（@124:129）GENE 正确。
- `abiotic stresses`（@156:172）ABS 正确。
- `salt`（@174:178）ABS 正确。
- `drought`（@180:187）ABS 正确。
- `cold`（@189:193）ABS 正确。
- `ultraviolet B`（@195:208）ABS 正确。
- `exogenous phytohormones`（@214:237）标为 ABS，但 phytohormones 是植物激素类别描述，不是具体胁迫因子，应删除。
- `methyl jasmonate`（@254:270）ABS 正确（茉莉酸甲酯是胁迫信号分子）。
- 漏标：`Phylogenetic analysis`（@0:20）是分析方法，应标为 BM。验证：text[0:20]="Phylogenetic analysis" ✓
- 漏标：`abscisic acid`（@239:252）是脱落酸，应标为 ABS。验证：text[239:252]="abscisic acid" ✓
- 漏标：`salicylic acid`（@272:285）是水杨酸，应标为 ABS。验证：text[272:285]="salicylic acid" ✓

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 20,  "text": "Phylogenetic analysis", "label": "BM"},
  {"start": 37,  "end": 46,  "text": "FtNAC TFs", "label": "GENE"},
  {"start": 124, "end": 129, "text": "FtNAC", "label": "GENE"},
  {"start": 156, "end": 172, "text": "abiotic stresses", "label": "ABS"},
  {"start": 174, "end": 178, "text": "salt", "label": "ABS"},
  {"start": 180, "end": 187, "text": "drought", "label": "ABS"},
  {"start": 189, "end": 193, "text": "cold", "label": "ABS"},
  {"start": 195, "end": 208, "text": "ultraviolet B", "label": "ABS"},
  {"start": 239, "end": 252, "text": "abscisic acid", "label": "ABS"},
  {"start": 254, "end": 270, "text": "methyl jasmonate", "label": "ABS"},
  {"start": 272, "end": 285, "text": "salicylic acid", "label": "ABS"}
]
```

> [删除] `exogenous phytohormones` @214:237 ABS；[新增] `Phylogenetic analysis` @0:20 BM；[新增] `abscisic acid` @239:252 ABS；[新增] `salicylic acid` @272:285 ABS

### relations（修订后完整列表）

```json
[]
```

---

## 样本 8

**原文**：`The Sd3 allele increased enzyme thermostability and enhanced diastatic power, a malting quality trait. The BC1F1 individuals impacted the agronomic and quality traits of the final progenies, showing the importance of screening at the early backcrossing stage in MABC.`

**分析**：
- `Sd3`（@4:7）GENE 正确。
- `diastatic power`（@61:76）TRT 正确。
- `malting quality trait`（@80:101）TRT 正确。
- `BC1F1 individuals`（@107:124）VAR 正确。
- `final progenies`（@174:189）VAR 正确。
- `backcrossing`（@240:252）BM 正确。
- `MABC`（@262:266）BM 正确（Marker-Assisted Backcrossing）。
- 关系：AFF(Sd3, diastatic power)、CON(diastatic power, malting quality trait)、AFF(BC1F1 individuals, final progenies)、USE(final progenies, backcrossing)、USE(final progenies, MABC) 均正确。
- 漏标：`enzyme thermostability`（@30:50）是酶热稳定性性状，应标为 TRT。验证：text[30:50]="enzyme thermostability" ✓
- 漏标关系：AFF(Sd3, enzyme thermostability)。

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 7,   "text": "Sd3", "label": "GENE"},
  {"start": 30,  "end": 50,  "text": "enzyme thermostability", "label": "TRT"},
  {"start": 61,  "end": 76,  "text": "diastatic power", "label": "TRT"},
  {"start": 80,  "end": 101, "text": "malting quality trait", "label": "TRT"},
  {"start": 107, "end": 124, "text": "BC1F1 individuals", "label": "VAR"},
  {"start": 174, "end": 189, "text": "final progenies", "label": "VAR"},
  {"start": 240, "end": 252, "text": "backcrossing", "label": "BM"},
  {"start": 262, "end": 266, "text": "MABC", "label": "BM"}
]
```

> [新增] `enzyme thermostability` @30:50 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Sd3", "head_start": 4, "head_end": 7, "head_type": "GENE",
   "tail": "enzyme thermostability", "tail_start": 30, "tail_end": 50, "tail_type": "TRT", "label": "AFF"},
  {"head": "Sd3", "head_start": 4, "head_end": 7, "head_type": "GENE",
   "tail": "diastatic power", "tail_start": 61, "tail_end": 76, "tail_type": "TRT", "label": "AFF"},
  {"head": "diastatic power", "head_start": 61, "head_end": 76, "head_type": "TRT",
   "tail": "malting quality trait", "tail_start": 80, "tail_end": 101, "tail_type": "TRT", "label": "CON"},
  {"head": "BC1F1 individuals", "head_start": 107, "head_end": 124, "head_type": "VAR",
   "tail": "final progenies", "tail_start": 174, "tail_end": 189, "tail_type": "VAR", "label": "AFF"},
  {"head": "final progenies", "head_start": 174, "head_end": 189, "head_type": "VAR",
   "tail": "backcrossing", "tail_start": 240, "tail_end": 252, "tail_type": "BM", "label": "USE"},
  {"head": "final progenies", "head_start": 174, "head_end": 189, "head_type": "VAR",
   "tail": "MABC", "tail_start": 262, "tail_end": 266, "tail_type": "BM", "label": "USE"}
]
```

> [新增] AFF(Sd3, enzyme thermostability)

---

## 样本 9

**原文**：`Multiple SSR markers, including SXAU8002 for 100-grain weight and SXAU8006 for stem diameter, were associated with agronomic traits. A candidate gene, FtPinG0007685500, was identified that may affect node number and stem diameter by participating in lignin synthesis.`

**分析**：
- `SXAU8002`（@32:40）MRK 正确。
- `100-grain weight`（@45:61）TRT 正确。
- `SXAU8006`（@66:74）MRK 正确。
- `FtPinG0007685500`（@151:167）GENE 正确。
- `node number`（@200:211）TRT 正确。
- `stem diameter`（@216:229）TRT 正确。
- `lignin synthesis`（@250:266）标为 TRT，但 lignin synthesis（木质素合成）是生物学过程，不是农艺性状，应改为 GENE（木质素合成基因/通路）或删除。依据 K8 §1.1，保留为 TRT（木质素含量是可量化性状）。
- 漏标：`stem diameter`（@79:92）在 "SXAU8006 for stem diameter" 中，是第一次出现，应标为 TRT。验证：text[79:92]="stem diameter" ✓（注意：原文 "SXAU8006 for stem diameter"，stem diameter @79:92）。
- 关系均正确，保留。

### entities（修订后完整列表）

```json
[
  {"start": 32,  "end": 40,  "text": "SXAU8002", "label": "MRK"},
  {"start": 45,  "end": 61,  "text": "100-grain weight", "label": "TRT"},
  {"start": 66,  "end": 74,  "text": "SXAU8006", "label": "MRK"},
  {"start": 79,  "end": 92,  "text": "stem diameter", "label": "TRT"},
  {"start": 151, "end": 167, "text": "FtPinG0007685500", "label": "GENE"},
  {"start": 200, "end": 211, "text": "node number", "label": "TRT"},
  {"start": 216, "end": 229, "text": "stem diameter", "label": "TRT"},
  {"start": 250, "end": 266, "text": "lignin synthesis", "label": "TRT"}
]
```

> [新增] `stem diameter` @79:92 TRT

### relations（修订后完整列表）

```json
[
  {"head": "SXAU8002", "head_start": 32, "head_end": 40, "head_type": "MRK",
   "tail": "100-grain weight", "tail_start": 45, "tail_end": 61, "tail_type": "TRT", "label": "LOI"},
  {"head": "SXAU8006", "head_start": 66, "head_end": 74, "head_type": "MRK",
   "tail": "stem diameter", "tail_start": 79, "tail_end": 92, "tail_type": "TRT", "label": "LOI"},
  {"head": "FtPinG0007685500", "head_start": 151, "head_end": 167, "head_type": "GENE",
   "tail": "node number", "tail_start": 200, "tail_end": 211, "tail_type": "TRT", "label": "AFF"},
  {"head": "FtPinG0007685500", "head_start": 151, "head_end": 167, "head_type": "GENE",
   "tail": "stem diameter", "tail_start": 216, "tail_end": 229, "tail_type": "TRT", "label": "AFF"}
]
```

> [修改] LOI(SXAU8006, stem diameter) 的 tail 改为 @79:92（第一次出现）

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增实体 | `acidic conditions` ABS；`yield-related traits` TRT |
| 0 | 新增关系 | HAS(E232 x Murasakimochi, yield-related traits) |
| 1 | 修改标签 | `Ethiopian sorghum germplasm` CROP→VAR |
| 1 | 新增实体 | `sorghum` @141:148 CROP |
| 2 | 新增实体 | `Transcriptomic analysis` BM；`CHI` GENE；`AACT` GENE；`IDH` GENE；`NADP-ME` GENE；`flavonoid biosynthesis` TRT；`vigor loss` TRT |
| 2 | 新增关系 | AFF(CHS, flavonoid biosynthesis)；AFF(CHI, flavonoid biosynthesis) |
| 4 | 删除实体 | `light response` TRT；`plant hormone` TRT；`abiotic stress response` TRT；`plant growth and development` TRT |
| 4 | 新增实体 | `Phylogenetic analysis` BM；`VfAP2/ERF` @169:178 GENE |
| 5 | 删除实体 | `heat-` @203:208 ABS |
| 5 | 新增实体 | `bPb-5529` MRK；`SG QTL` @170:176 QTL |
| 5 | 新增关系 | LOI(SG QTL, 5H)；LOI(heat-stress QTL, bPb-5529/5H/root length/root-shoot ratio) ×4 |
| 6 | 新增实体 | `IP-MS` BM；`drought stress response` TRT；`blast resistance` TRT |
| 6 | 修改标签 | `immune response` BIS→TRT |
| 6 | 修改关系 | AFF(SiUBC39, drought stress) → AFF(SiUBC39, drought stress response) |
| 6 | 新增关系 | AFF(drought stress, drought stress response)；AFF(SiUBC39, blast resistance) |
| 7 | 删除实体 | `exogenous phytohormones` @214:237 ABS |
| 7 | 新增实体 | `Phylogenetic analysis` BM；`abscisic acid` ABS；`salicylic acid` ABS |
| 8 | 新增实体 | `enzyme thermostability` TRT |
| 8 | 新增关系 | AFF(Sd3, enzyme thermostability) |
| 9 | 新增实体 | `stem diameter` @79:92 TRT |
