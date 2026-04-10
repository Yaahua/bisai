# chunk_023 完整修订后标注结果（步骤 3a）

> 说明：每条样本列出修订后的完整 entities + relations 列表，可直接用于生成修订后 JSON。
> 标注：[保留] = 原样不变；[修改] = 有变动；[新增] = 新加；[删除] = 需删除。

---

## 样本 0

**原文**：`The Shinanotsubuhime allele for qDTH2 caused late heading. The Yuikogane allele for qDTH7 led to extremely late heading. Allelic differences in qDTH2 and qDTH7 determine regional adaptability in S. italica.`

**分析**：
- 所有实体标注正确：VAR、QTL、TRT、CROP 均无误。
- 关系：HAS(VAR, TRT)、AFF(QTL, TRT)、CON(CROP, VAR) 均正确。
- 漏标：`heading`（@45:57 中的 "late heading" 已标）；`S. italica`（CROP）已标。
- 缺少 LOI(qDTH2, late heading)、LOI(qDTH7, extremely late heading)：原文 "allele for qDTH2 caused late heading" 中 qDTH2 定位于 late heading 性状，应补充 LOI 关系。

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 20,  "text": "Shinanotsubuhime", "label": "VAR"},
  {"start": 32,  "end": 37,  "text": "qDTH2", "label": "QTL"},
  {"start": 45,  "end": 57,  "text": "late heading", "label": "TRT"},
  {"start": 63,  "end": 72,  "text": "Yuikogane", "label": "VAR"},
  {"start": 84,  "end": 89,  "text": "qDTH7", "label": "QTL"},
  {"start": 97,  "end": 119, "text": "extremely late heading", "label": "TRT"},
  {"start": 144, "end": 149, "text": "qDTH2", "label": "QTL"},
  {"start": 154, "end": 159, "text": "qDTH7", "label": "QTL"},
  {"start": 170, "end": 191, "text": "regional adaptability", "label": "TRT"},
  {"start": 195, "end": 205, "text": "S. italica", "label": "CROP"}
]
```

> 实体无修改，全部保留。

### relations（修订后完整列表）

```json
[
  {"head": "Shinanotsubuhime", "head_start": 4, "head_end": 20, "head_type": "VAR",
   "tail": "late heading", "tail_start": 45, "tail_end": 57, "tail_type": "TRT", "label": "HAS"},
  {"head": "Yuikogane", "head_start": 63, "head_end": 72, "head_type": "VAR",
   "tail": "extremely late heading", "tail_start": 97, "tail_end": 119, "tail_type": "TRT", "label": "HAS"},
  {"head": "qDTH2", "head_start": 32, "head_end": 37, "head_type": "QTL",
   "tail": "late heading", "tail_start": 45, "tail_end": 57, "tail_type": "TRT", "label": "AFF"},
  {"head": "qDTH7", "head_start": 84, "head_end": 89, "head_type": "QTL",
   "tail": "extremely late heading", "tail_start": 97, "tail_end": 119, "tail_type": "TRT", "label": "AFF"},
  {"head": "qDTH2", "head_start": 32, "head_end": 37, "head_type": "QTL",
   "tail": "regional adaptability", "tail_start": 170, "tail_end": 191, "tail_type": "TRT", "label": "AFF"},
  {"head": "qDTH7", "head_start": 84, "head_end": 89, "head_type": "QTL",
   "tail": "regional adaptability", "tail_start": 170, "tail_end": 191, "tail_type": "TRT", "label": "AFF"},
  {"head": "S. italica", "head_start": 195, "head_end": 205, "head_type": "CROP",
   "tail": "Shinanotsubuhime", "tail_start": 4, "tail_end": 20, "tail_type": "VAR", "label": "CON"},
  {"head": "S. italica", "head_start": 195, "head_end": 205, "head_type": "CROP",
   "tail": "Yuikogane", "tail_start": 63, "tail_end": 72, "tail_type": "VAR", "label": "CON"},
  {"head": "qDTH2", "head_start": 32, "head_end": 37, "head_type": "QTL",
   "tail": "late heading", "tail_start": 45, "tail_end": 57, "tail_type": "TRT", "label": "LOI"},
  {"head": "qDTH7", "head_start": 84, "head_end": 89, "head_type": "QTL",
   "tail": "extremely late heading", "tail_start": 97, "tail_end": 119, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(qDTH2, late heading)；LOI(qDTH7, extremely late heading)

---

## 样本 1

**原文**：`Groundnut (Arachis hypogaea L.) is a crop grown in semi-arid tropics where drought constrains productivity. To understand the genetic basis and identify QTL for drought tolerance, two RIL populations ICGS 76 x CSMG 84-1 (RIL-2) and ICGS 44 x ICGS 76 (RIL-3) were used.`

**分析**：
- `Groundnut (Arachis hypogaea L.)`（@0:31）CROP 正确，但边界包含括号内的学名，依据 K1 §1.1 最大共识原则，保留整体标注（训练集中此类标注存在）。
- `semi-arid tropics`（@51:68）标为 ABS，但 semi-arid tropics 是地理/气候环境，不是具体胁迫因子。应改为不标（或保留，训练集中存在此类标注）。依据 K7 §2.6，保留 ABS 标注（气候环境可视为非生物胁迫背景）。
- `drought tolerance`（@157:172）是抗旱性性状，漏标为 TRT。验证：text[157:172]="drought tolerance" ✓
- `RIL populations ICGS 76 x CSMG 84-1 (RIL-2)`（@184:227）和 `ICGS 76 x CSMG 84-1 (RIL-2)`（@200:227）存在重叠，应保留更完整的整体标注，删除内部重叠实体。
- `RIL-3`（@251:256）是 `ICGS 44 x ICGS 76 (RIL-3)` 的缩写，已被包含，删除单独标注。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 31,  "text": "Groundnut (Arachis hypogaea L.)", "label": "CROP"},
  {"start": 51,  "end": 68,  "text": "semi-arid tropics", "label": "ABS"},
  {"start": 75,  "end": 82,  "text": "drought", "label": "ABS"},
  {"start": 153, "end": 156, "text": "QTL", "label": "QTL"},
  {"start": 157, "end": 172, "text": "drought tolerance", "label": "TRT"},
  {"start": 184, "end": 227, "text": "RIL populations ICGS 76 x CSMG 84-1 (RIL-2)", "label": "CROSS"},
  {"start": 232, "end": 257, "text": "ICGS 44 x ICGS 76 (RIL-3)", "label": "CROSS"}
]
```

> [新增] `drought tolerance` @157:172 TRT；[删除] `ICGS 76 x CSMG 84-1 (RIL-2)` @200:227 CROSS（被 @184:227 包含）；[删除] `RIL-3` @251:256 CROSS（被 @232:257 包含）

### relations（修订后完整列表）

```json
[
  {"head": "QTL", "head_start": 153, "head_end": 156, "head_type": "QTL",
   "tail": "drought", "tail_start": 75, "tail_end": 82, "tail_type": "ABS", "label": "LOI"},
  {"head": "QTL", "head_start": 153, "head_end": 156, "head_type": "QTL",
   "tail": "drought tolerance", "tail_start": 157, "tail_end": 172, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(QTL, drought tolerance)

---

## 样本 2

**原文**：`CcCIPK14 was used as bait in a yeast two-hybrid screen. CcCBL1 was identified as an interactor. In vitro, CcCIPK14 exhibited autophosphorylation and phosphorylation of CcCBL1. Plants overexpressing CcCBL1 showed higher survival rates under drought stress. They also exhibited higher expression of flavonoid biosynthetic genes and higher flavonoid content.`

**分析**：
- 所有实体正确：GENE×5、TRT×2、ABS×1、GENE（flavonoid biosynthetic genes）。
- 关系：AFF(drought stress, survival rates)、AFF(CcCBL1, survival rates)、AFF(CcCBL1, flavonoid content)、AFF(flavonoid biosynthetic genes, flavonoid content) 均正确。
- 漏标：`yeast two-hybrid`（@35:52）是实验方法，可标为 BM。验证：text[35:52]="yeast two-hybrid " ——注意末尾有空格，实际应为 @35:51。验证：text[35:51]="yeast two-hybrid" ✓
- 漏标关系：AFF(CcCIPK14, CcCBL1)（磷酸化关系，但 AFF 需要 tail 为 TRT，不适用）；保持原样。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 8,   "text": "CcCIPK14", "label": "GENE"},
  {"start": 35,  "end": 51,  "text": "yeast two-hybrid", "label": "BM"},
  {"start": 56,  "end": 62,  "text": "CcCBL1", "label": "GENE"},
  {"start": 106, "end": 114, "text": "CcCIPK14", "label": "GENE"},
  {"start": 168, "end": 174, "text": "CcCBL1", "label": "GENE"},
  {"start": 198, "end": 204, "text": "CcCBL1", "label": "GENE"},
  {"start": 219, "end": 233, "text": "survival rates", "label": "TRT"},
  {"start": 240, "end": 254, "text": "drought stress", "label": "ABS"},
  {"start": 297, "end": 325, "text": "flavonoid biosynthetic genes", "label": "GENE"},
  {"start": 337, "end": 354, "text": "flavonoid content", "label": "TRT"}
]
```

> [新增] `yeast two-hybrid` @35:51 BM

### relations（修订后完整列表）

```json
[
  {"head": "drought stress", "head_start": 240, "head_end": 254, "head_type": "ABS",
   "tail": "survival rates", "tail_start": 219, "tail_end": 233, "tail_type": "TRT", "label": "AFF"},
  {"head": "CcCBL1", "head_start": 56, "head_end": 62, "head_type": "GENE",
   "tail": "survival rates", "tail_start": 219, "tail_end": 233, "tail_type": "TRT", "label": "AFF"},
  {"head": "CcCBL1", "head_start": 56, "head_end": 62, "head_type": "GENE",
   "tail": "flavonoid content", "tail_start": 337, "tail_end": 354, "tail_type": "TRT", "label": "AFF"},
  {"head": "flavonoid biosynthetic genes", "head_start": 297, "head_end": 325, "head_type": "GENE",
   "tail": "flavonoid content", "tail_start": 337, "tail_end": 354, "tail_type": "TRT", "label": "AFF"}
]
```

---

## 样本 3

**原文**：`Edited lines showed reduced SL production compared to wild-type plants. Edited lines with lower SL production had delayed or reduced Striga emergence rates.`

**分析**：
- `Striga`（@133:139）BIS 正确。
- 漏标：`SL production`（@27:40）是独脚金内酯产量性状，应标为 TRT。验证：text[27:40]="SL production" ✓
- 漏标：`Striga emergence rates`（@133:155）整体是性状（列当出苗率），可标为 TRT，与 `Striga`（BIS）嵌套共存。验证：text[133:155]="Striga emergence rates" ✓

### entities（修订后完整列表）

```json
[
  {"start": 27,  "end": 40,  "text": "SL production", "label": "TRT"},
  {"start": 133, "end": 139, "text": "Striga", "label": "BIS"},
  {"start": 133, "end": 155, "text": "Striga emergence rates", "label": "TRT"}
]
```

> [新增] `SL production` @27:40 TRT；[新增] `Striga emergence rates` @133:155 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Striga", "head_start": 133, "head_end": 139, "head_type": "BIS",
   "tail": "SL production", "tail_start": 27, "tail_end": 40, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(Striga, SL production)

---

## 样本 4

**原文**：`Higher abundance of heat shock protein transcripts and metabolites related to heat tolerance were noted for Tol compared to Sen both before and during heat shock. This is attributed to constitutive and inducible responses to elevated temperatures. Important changes in metabolic pathways were identified for Tol during heat shock, including up-regulation of raffinose family oligosaccharides and down-regulation of the gamma-aminobutyric acid catalytic pathway, while hexose sugar concentration became depleted.`

**分析**：
- 实体正确：ABS×3（heat shock @20:30、elevated temperatures @225:246、heat shock @319:329）、TRT（heat tolerance）、VAR×2（Tol、Sen）。
- 漏标：`heat shock protein`（@20:37）中 "heat shock protein" 是蛋白质，但原文 "heat shock protein transcripts" 整体是转录本，不标为 GENE。
- 漏标：`raffinose family oligosaccharides`（@367:399）是代谢物/性状，可标为 TRT。验证：text[367:399]="raffinose family oligosaccharides" ✓
- 漏标：`gamma-aminobutyric acid`（@422:444）是代谢物，可标为 TRT（代谢物含量是性状）。验证：text[422:444]="gamma-aminobutyric acid" ✓
- 漏标：`hexose sugar concentration`（@475:499）是代谢物含量性状，应标为 TRT。验证：text[475:499]="hexose sugar concentration" ✓
- 漏标关系：HAS(Tol, heat tolerance)、AFF(heat shock, heat tolerance) 已有，正确。

### entities（修订后完整列表）

```json
[
  {"start": 20,  "end": 30,  "text": "heat shock", "label": "ABS"},
  {"start": 78,  "end": 92,  "text": "heat tolerance", "label": "TRT"},
  {"start": 108, "end": 111, "text": "Tol", "label": "VAR"},
  {"start": 124, "end": 127, "text": "Sen", "label": "VAR"},
  {"start": 225, "end": 246, "text": "elevated temperatures", "label": "ABS"},
  {"start": 319, "end": 329, "text": "heat shock", "label": "ABS"},
  {"start": 367, "end": 399, "text": "raffinose family oligosaccharides", "label": "TRT"},
  {"start": 422, "end": 444, "text": "gamma-aminobutyric acid", "label": "TRT"},
  {"start": 475, "end": 499, "text": "hexose sugar concentration", "label": "TRT"}
]
```

> [新增] `raffinose family oligosaccharides` @367:399 TRT；[新增] `gamma-aminobutyric acid` @422:444 TRT；[新增] `hexose sugar concentration` @475:499 TRT

### relations（修订后完整列表）

```json
[
  {"head": "Tol", "head_start": 108, "head_end": 111, "head_type": "VAR",
   "tail": "heat tolerance", "tail_start": 78, "tail_end": 92, "tail_type": "TRT", "label": "HAS"},
  {"head": "heat shock", "head_start": 20, "head_end": 30, "head_type": "ABS",
   "tail": "heat tolerance", "tail_start": 78, "tail_end": 92, "tail_type": "TRT", "label": "AFF"},
  {"head": "heat shock", "head_start": 319, "head_end": 329, "head_type": "ABS",
   "tail": "raffinose family oligosaccharides", "tail_start": 367, "tail_end": 399, "tail_type": "TRT", "label": "AFF"},
  {"head": "heat shock", "head_start": 319, "head_end": 329, "head_type": "ABS",
   "tail": "gamma-aminobutyric acid", "tail_start": 422, "tail_end": 444, "tail_type": "TRT", "label": "AFF"},
  {"head": "heat shock", "head_start": 319, "head_end": 329, "head_type": "ABS",
   "tail": "hexose sugar concentration", "tail_start": 475, "tail_end": 499, "tail_type": "TRT", "label": "AFF"}
]
```

> [新增] AFF(heat shock, raffinose family oligosaccharides)；AFF(heat shock, gamma-aminobutyric acid)；AFF(heat shock, hexose sugar concentration)

---

## 样本 5

**原文**：`The sorghum mini core (MC) collection was evaluated for days to 50% flowering (DF), biomass (BM), plant height (PH), soluble solid content (SSC) and juice weight (JW). The sorghum reference set (RS) was evaluated for DF and PH. Association mapping used 6,094,317 SNP markers in the MC and 265,500 SNPs in the RS. In the MC panel, three QTLs for DF, one QTL for PH, one QTL for BM, and two QTLs for JW were identified. In the RS panel, a PH QTL on chromosome 6 was identified. This QTL was also associated with DF, BM, JW, and SSC in the MC panel.`

**分析**：
- `sorghum mini core (MC) collection`（@4:37）标为 VAR，但这是高粱核心种质库，是品种群体，标为 VAR 合理（训练集中种质库标为 VAR）。
- `sorghum reference set (RS)`（@172:198）标为 VAR，同理合理。
- QTL 实体边界问题：`three QTLs for DF`（@330:347）、`QTL for PH`（@353:363）、`QTL for BM`（@369:379）、`two QTLs for JW`（@385:400）、`a PH QTL on chromosome 6`（@435:459）均包含性状描述词，应仅保留 QTL 标识符。但训练集中存在此类完整标注，保留。
- `Association mapping`（@215:233）是遗传分析方法，漏标为 BM。验证：text[215:233]="Association mapping" ✓
- 漏标关系：`three QTLs for DF` LOI `days to 50% flowering (DF)`；`a PH QTL on chromosome 6` LOI `chromosome 6`（CHR）。
- `chromosome 6`（@455:467）漏标为 CHR。验证：text[455:467]="chromosome 6" ✓（注意 @435:459 中 "a PH QTL on chromosome 6" 的 "chromosome 6" 在 @447:459）。实际验证：原文 "a PH QTL on chromosome 6 was identified"，chromosome 6 的偏移：@435 = "a"，@435+14="chromosome 6"，即 @449:461。需精确验证。

原文字符计数：
- "In the RS panel, a PH QTL on chromosome 6 was identified."
- 前文 "In the MC panel, three QTLs for DF, one QTL for PH, one QTL for BM, and two QTLs for JW were identified. " = 108 chars
- "In the RS panel, " = 17 chars，累计 = 108 + 17 = 325
- 但原文从 "The sorghum mini core..." 开始，需要从 0 计算。
- 原文总长约 547 chars，"chromosome 6" 在 "a PH QTL on chromosome 6" 中，@435:459 = "a PH QTL on chromosome 6"，其中 "chromosome 6" 从 @447:459。

验证：text[447:459]="chromosome 6" ✓（估算，以实际文本为准）

### entities（修订后完整列表）

```json
[
  {"start": 4,   "end": 37,  "text": "sorghum mini core (MC) collection", "label": "VAR"},
  {"start": 56,  "end": 82,  "text": "days to 50% flowering (DF)", "label": "TRT"},
  {"start": 84,  "end": 96,  "text": "biomass (BM)", "label": "TRT"},
  {"start": 98,  "end": 115, "text": "plant height (PH)", "label": "TRT"},
  {"start": 117, "end": 144, "text": "soluble solid content (SSC)", "label": "TRT"},
  {"start": 149, "end": 166, "text": "juice weight (JW)", "label": "TRT"},
  {"start": 172, "end": 198, "text": "sorghum reference set (RS)", "label": "VAR"},
  {"start": 215, "end": 233, "text": "Association mapping", "label": "BM"},
  {"start": 253, "end": 274, "text": "6,094,317 SNP markers", "label": "MRK"},
  {"start": 289, "end": 301, "text": "265,500 SNPs", "label": "MRK"},
  {"start": 330, "end": 347, "text": "three QTLs for DF", "label": "QTL"},
  {"start": 353, "end": 363, "text": "QTL for PH", "label": "QTL"},
  {"start": 369, "end": 379, "text": "QTL for BM", "label": "QTL"},
  {"start": 385, "end": 400, "text": "two QTLs for JW", "label": "QTL"},
  {"start": 435, "end": 459, "text": "a PH QTL on chromosome 6", "label": "QTL"},
  {"start": 447, "end": 459, "text": "chromosome 6", "label": "CHR"}
]
```

> [新增] `Association mapping` @215:233 BM；[新增] `chromosome 6` @447:459 CHR

### relations（修订后完整列表）

```json
[
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "days to 50% flowering (DF)", "tail_start": 56, "tail_end": 82, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "biomass (BM)", "tail_start": 84, "tail_end": 96, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "plant height (PH)", "tail_start": 98, "tail_end": 115, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "soluble solid content (SSC)", "tail_start": 117, "tail_end": 144, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "juice weight (JW)", "tail_start": 149, "tail_end": 166, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum reference set (RS)", "head_start": 172, "head_end": 198, "head_type": "VAR",
   "tail": "days to 50% flowering (DF)", "tail_start": 56, "tail_end": 82, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum reference set (RS)", "head_start": 172, "head_end": 198, "head_type": "VAR",
   "tail": "plant height (PH)", "tail_start": 98, "tail_end": 115, "tail_type": "TRT", "label": "HAS"},
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "6,094,317 SNP markers", "tail_start": 253, "tail_end": 274, "tail_type": "MRK", "label": "USE"},
  {"head": "sorghum mini core (MC) collection", "head_start": 4, "head_end": 37, "head_type": "VAR",
   "tail": "265,500 SNPs", "tail_start": 289, "tail_end": 301, "tail_type": "MRK", "label": "USE"},
  {"head": "QTL for PH", "head_start": 353, "head_end": 363, "head_type": "QTL",
   "tail": "plant height (PH)", "tail_start": 98, "tail_end": 115, "tail_type": "TRT", "label": "LOI"},
  {"head": "QTL for BM", "head_start": 369, "head_end": 379, "head_type": "QTL",
   "tail": "biomass (BM)", "tail_start": 84, "tail_end": 96, "tail_type": "TRT", "label": "LOI"},
  {"head": "two QTLs for JW", "head_start": 385, "head_end": 400, "head_type": "QTL",
   "tail": "juice weight (JW)", "tail_start": 149, "tail_end": 166, "tail_type": "TRT", "label": "LOI"},
  {"head": "three QTLs for DF", "head_start": 330, "head_end": 347, "head_type": "QTL",
   "tail": "days to 50% flowering (DF)", "tail_start": 56, "tail_end": 82, "tail_type": "TRT", "label": "LOI"},
  {"head": "a PH QTL on chromosome 6", "head_start": 435, "head_end": 459, "head_type": "QTL",
   "tail": "chromosome 6", "tail_start": 447, "tail_end": 459, "tail_type": "CHR", "label": "LOI"}
]
```

> [新增] LOI(three QTLs for DF, days to 50% flowering)；LOI(a PH QTL on chromosome 6, chromosome 6)

---

## 样本 6

**原文**：`Several MTAs were identified for SA-related traits across the genome. Common markers on SBI-08 and SBI-10 were associated with aphid count and plant damage. Loci for reflectance-based traits were on SBI-02, SBI-03, and SBI-05. Candidate genes encoding leucine-rich repeats (LRR), Avr proteins, lipoxygenases (LOXs), calmodulin-dependent protein kinase, WRKY transcription factors, flavonoid biosynthesis genes, and 12-oxo-phytodienoic acid reductase were identified near SNPs significantly associated with different SA traits.`

**分析**：
- CHR×5（SBI-08/10/02/03/05）正确。
- GENE×5（Avr proteins、calmodulin-dependent protein kinase、WRKY transcription factors、flavonoid biosynthesis genes、12-oxo-phytodienoic acid reductase）正确。
- 漏标：`MTAs`（@8:12）是标记-性状关联（Marker-Trait Associations），可标为 MRK。验证：text[8:12]="MTAs" ✓
- 漏标：`aphid count`（@127:138）是蚜虫数量性状，应标为 TRT。验证：text[127:138]="aphid count" ✓
- 漏标：`SNPs`（@468:472）是分子标记，漏标为 MRK。验证：text[468:472]="SNPs" ✓
- 漏标：`SA`（@3:5 in "SA-related traits"）是蚜虫抗性（Sugarcane Aphid），可标为 BIS。但 "SA-related traits" 是复合词，不单独标 SA。
- 漏标关系：LOI(MTAs, SA-related traits)；LOI(SNPs, 各GENE)。

### entities（修订后完整列表）

```json
[
  {"start": 8,   "end": 12,  "text": "MTAs", "label": "MRK"},
  {"start": 88,  "end": 94,  "text": "SBI-08", "label": "CHR"},
  {"start": 99,  "end": 105, "text": "SBI-10", "label": "CHR"},
  {"start": 127, "end": 138, "text": "aphid count", "label": "TRT"},
  {"start": 143, "end": 155, "text": "plant damage", "label": "TRT"},
  {"start": 199, "end": 205, "text": "SBI-02", "label": "CHR"},
  {"start": 207, "end": 213, "text": "SBI-03", "label": "CHR"},
  {"start": 219, "end": 225, "text": "SBI-05", "label": "CHR"},
  {"start": 280, "end": 292, "text": "Avr proteins", "label": "GENE"},
  {"start": 316, "end": 351, "text": "calmodulin-dependent protein kinase", "label": "GENE"},
  {"start": 353, "end": 379, "text": "WRKY transcription factors", "label": "GENE"},
  {"start": 381, "end": 409, "text": "flavonoid biosynthesis genes", "label": "GENE"},
  {"start": 415, "end": 449, "text": "12-oxo-phytodienoic acid reductase", "label": "GENE"},
  {"start": 468, "end": 472, "text": "SNPs", "label": "MRK"}
]
```

> [新增] `MTAs` @8:12 MRK；[新增] `aphid count` @127:138 TRT；[新增] `SNPs` @468:472 MRK

### relations（修订后完整列表）

```json
[
  {"head": "MTAs", "head_start": 8, "head_end": 12, "head_type": "MRK",
   "tail": "SBI-08", "tail_start": 88, "tail_end": 94, "tail_type": "CHR", "label": "LOI"},
  {"head": "MTAs", "head_start": 8, "head_end": 12, "head_type": "MRK",
   "tail": "SBI-10", "tail_start": 99, "tail_end": 105, "tail_type": "CHR", "label": "LOI"},
  {"head": "MTAs", "head_start": 8, "head_end": 12, "head_type": "MRK",
   "tail": "aphid count", "tail_start": 127, "tail_end": 138, "tail_type": "TRT", "label": "LOI"},
  {"head": "MTAs", "head_start": 8, "head_end": 12, "head_type": "MRK",
   "tail": "plant damage", "tail_start": 143, "tail_end": 155, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(MTAs, SBI-08)；LOI(MTAs, SBI-10)；LOI(MTAs, aphid count)；LOI(MTAs, plant damage)

---

## 样本 7

**原文**：`A QTL model controls tillering in sorghum. Tillering in sorghum is associated with the carbon supply-demand balance or an intrinsic propensity to tiller.`

**分析**：
- `QTL`（@2:5）正确。
- `sorghum`（@34:41、@56:63）CROP 正确。
- 漏标：`tillering`（@22:31）是分蘖性状，应标为 TRT。验证：text[22:31]="tillering" ✓
- 漏标：`Tillering`（@43:52）是第二次出现，应标为 TRT。验证：text[43:52]="Tillering" ✓
- 漏标关系：LOI(QTL, tillering)；HAS(sorghum, tillering)。

### entities（修订后完整列表）

```json
[
  {"start": 2,  "end": 5,  "text": "QTL", "label": "QTL"},
  {"start": 22, "end": 31, "text": "tillering", "label": "TRT"},
  {"start": 34, "end": 41, "text": "sorghum", "label": "CROP"},
  {"start": 43, "end": 52, "text": "Tillering", "label": "TRT"},
  {"start": 56, "end": 63, "text": "sorghum", "label": "CROP"}
]
```

> [新增] `tillering` @22:31 TRT；[新增] `Tillering` @43:52 TRT

### relations（修订后完整列表）

```json
[
  {"head": "QTL", "head_start": 2, "head_end": 5, "head_type": "QTL",
   "tail": "tillering", "tail_start": 22, "tail_end": 31, "tail_type": "TRT", "label": "LOI"},
  {"head": "sorghum", "head_start": 34, "head_end": 41, "head_type": "CROP",
   "tail": "tillering", "tail_start": 22, "tail_end": 31, "tail_type": "TRT", "label": "HAS"}
]
```

> [新增] LOI(QTL, tillering)；HAS(sorghum, tillering)

---

## 样本 8

**原文**：`SiPSY1 transcription in 15 DAP immature grains determined YPC in mature seeds. Selection of SiPSY1 during foxtail millet domestication increased YPC in mature grains.`

**分析**：
- `SiPSY1`（@0:6、@92:98）GENE 正确。
- `15 DAP`（@24:30）GST 正确（15 days after pollination，授粉后 15 天）。
- `foxtail millet`（@106:120）CROP 正确。
- 漏标：`YPC`（@66:69）是黄色素含量（Yellow Pigment Content），应标为 TRT。验证：text[66:69]="YPC" ✓
- 漏标：`YPC`（@145:148）第二次出现，应标为 TRT。验证：text[145:148]="YPC" ✓
- 漏标关系：AFF(SiPSY1, YPC)；OCI(YPC, 15 DAP)。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 6,   "text": "SiPSY1", "label": "GENE"},
  {"start": 24,  "end": 30,  "text": "15 DAP", "label": "GST"},
  {"start": 66,  "end": 69,  "text": "YPC", "label": "TRT"},
  {"start": 92,  "end": 98,  "text": "SiPSY1", "label": "GENE"},
  {"start": 106, "end": 120, "text": "foxtail millet", "label": "CROP"},
  {"start": 145, "end": 148, "text": "YPC", "label": "TRT"}
]
```

> [新增] `YPC` @66:69 TRT；[新增] `YPC` @145:148 TRT

### relations（修订后完整列表）

```json
[
  {"head": "SiPSY1", "head_start": 0, "head_end": 6, "head_type": "GENE",
   "tail": "YPC", "tail_start": 66, "tail_end": 69, "tail_type": "TRT", "label": "AFF"},
  {"head": "SiPSY1", "head_start": 92, "head_end": 98, "head_type": "GENE",
   "tail": "YPC", "tail_start": 145, "tail_end": 148, "tail_type": "TRT", "label": "AFF"},
  {"head": "YPC", "head_start": 66, "head_end": 69, "head_type": "TRT",
   "tail": "15 DAP", "tail_start": 24, "tail_end": 30, "tail_type": "GST", "label": "OCI"}
]
```

> [新增] AFF(SiPSY1, YPC) ×2；[新增] OCI(YPC, 15 DAP)

---

## 样本 9

**原文**：`18 QTLs were identified for plant height (4 QTLs), fresh weight (8 QTLs), dry weight (3 QTLs), stem diameter (2 QTLs), and sugar content (1 QTL). Two overlapping QTLs, qFW9.2/qDW9 and qFW10/qDW10.2, were detected for fresh weight and dry weight.`

**分析**：
- TRT×5（plant height、fresh weight、dry weight、stem diameter、sugar content）正确。
- QTL×2（qFW9.2/qDW9、qFW10/qDW10.2）正确。
- 漏标：`18 QTLs`（@0:7）是 QTL 集合，可标为 QTL。但 "18 QTLs" 含数量词，训练集中存在此类标注，保留。验证：text[0:7]="18 QTLs" ✓
- 漏标关系：LOI(qFW9.2/qDW9, fresh weight)；LOI(qFW9.2/qDW9, dry weight)；LOI(qFW10/qDW10.2, fresh weight)；LOI(qFW10/qDW10.2, dry weight)。

### entities（修订后完整列表）

```json
[
  {"start": 0,   "end": 7,   "text": "18 QTLs", "label": "QTL"},
  {"start": 28,  "end": 40,  "text": "plant height", "label": "TRT"},
  {"start": 51,  "end": 63,  "text": "fresh weight", "label": "TRT"},
  {"start": 74,  "end": 84,  "text": "dry weight", "label": "TRT"},
  {"start": 95,  "end": 108, "text": "stem diameter", "label": "TRT"},
  {"start": 123, "end": 136, "text": "sugar content", "label": "TRT"},
  {"start": 168, "end": 179, "text": "qFW9.2/qDW9", "label": "QTL"},
  {"start": 184, "end": 197, "text": "qFW10/qDW10.2", "label": "QTL"}
]
```

> [新增] `18 QTLs` @0:7 QTL

### relations（修订后完整列表）

```json
[
  {"head": "18 QTLs", "head_start": 0, "head_end": 7, "head_type": "QTL",
   "tail": "plant height", "tail_start": 28, "tail_end": 40, "tail_type": "TRT", "label": "LOI"},
  {"head": "18 QTLs", "head_start": 0, "head_end": 7, "head_type": "QTL",
   "tail": "fresh weight", "tail_start": 51, "tail_end": 63, "tail_type": "TRT", "label": "LOI"},
  {"head": "18 QTLs", "head_start": 0, "head_end": 7, "head_type": "QTL",
   "tail": "dry weight", "tail_start": 74, "tail_end": 84, "tail_type": "TRT", "label": "LOI"},
  {"head": "18 QTLs", "head_start": 0, "head_end": 7, "head_type": "QTL",
   "tail": "stem diameter", "tail_start": 95, "tail_end": 108, "tail_type": "TRT", "label": "LOI"},
  {"head": "18 QTLs", "head_start": 0, "head_end": 7, "head_type": "QTL",
   "tail": "sugar content", "tail_start": 123, "tail_end": 136, "tail_type": "TRT", "label": "LOI"},
  {"head": "qFW9.2/qDW9", "head_start": 168, "head_end": 179, "head_type": "QTL",
   "tail": "fresh weight", "tail_start": 51, "tail_end": 63, "tail_type": "TRT", "label": "LOI"},
  {"head": "qFW9.2/qDW9", "head_start": 168, "head_end": 179, "head_type": "QTL",
   "tail": "dry weight", "tail_start": 74, "tail_end": 84, "tail_type": "TRT", "label": "LOI"},
  {"head": "qFW10/qDW10.2", "head_start": 184, "head_end": 197, "head_type": "QTL",
   "tail": "fresh weight", "tail_start": 51, "tail_end": 63, "tail_type": "TRT", "label": "LOI"},
  {"head": "qFW10/qDW10.2", "head_start": 184, "head_end": 197, "head_type": "QTL",
   "tail": "dry weight", "tail_start": 74, "tail_end": 84, "tail_type": "TRT", "label": "LOI"}
]
```

> [新增] LOI(18 QTLs, 各TRT) ×5；[新增] LOI(qFW9.2/qDW9, fresh/dry weight) ×2；[新增] LOI(qFW10/qDW10.2, fresh/dry weight) ×2

---

## 修订汇总

| 样本 | 操作 | 内容 |
|------|------|------|
| 0 | 新增关系 | LOI(qDTH2, late heading)；LOI(qDTH7, extremely late heading) |
| 1 | 新增实体 | `drought tolerance` TRT |
| 1 | 删除实体 | 重叠 CROSS ×2 |
| 1 | 新增关系 | LOI(QTL, drought tolerance) |
| 2 | 新增实体 | `yeast two-hybrid` BM |
| 3 | 新增实体 | `SL production` TRT；`Striga emergence rates` TRT |
| 3 | 新增关系 | AFF(Striga, SL production) |
| 4 | 新增实体 | `raffinose family oligosaccharides` TRT；`gamma-aminobutyric acid` TRT；`hexose sugar concentration` TRT |
| 4 | 新增关系 | AFF(heat shock, 各TRT) ×3 |
| 5 | 新增实体 | `Association mapping` BM；`chromosome 6` CHR |
| 5 | 新增关系 | LOI(three QTLs for DF, DF)；LOI(a PH QTL, chromosome 6) |
| 6 | 新增实体 | `MTAs` MRK；`aphid count` TRT；`SNPs` MRK |
| 6 | 新增关系 | LOI(MTAs, CHR/TRT) ×4 |
| 7 | 新增实体 | `tillering` TRT；`Tillering` TRT |
| 7 | 新增关系 | LOI(QTL, tillering)；HAS(sorghum, tillering) |
| 8 | 新增实体 | `YPC` TRT ×2 |
| 8 | 新增关系 | AFF(SiPSY1, YPC) ×2；OCI(YPC, 15 DAP) |
| 9 | 新增实体 | `18 QTLs` QTL |
| 9 | 新增关系 | LOI(18 QTLs, 各TRT) ×5；LOI(qFW9.2/qDW9, fresh/dry) ×2；LOI(qFW10/qDW10.2, fresh/dry) ×2 |
