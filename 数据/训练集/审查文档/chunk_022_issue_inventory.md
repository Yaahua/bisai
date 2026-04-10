# chunk_022 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_022（10 条样本）
**输入物**：chunk_022.json + chunk_022_annotated.md + chunk_022_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 1 | 语义审查 | `SCAR_3456624` LOI `Pc39`：关系方向为 LOI(MRK→GENE)，表示标记定位于基因，正确。但 tail 指向 @63:67 的 Pc39，而非 @136:140 的 Pc39。需确认哪个 Pc39 是真正被定位的（原文说 "within 0.37 cM of Pc39"，第二个 Pc39 @136:140 才是被定位的那个） | 高 |
| 2 | 样本 2 | 知识审查 | `BSR inoculation tests`（@183:204）标为 BM，但 "inoculation tests" 是接种鉴定实验，属于育种方法（BM）正确。但 BSR（@183:186）已被 BM 包含，不应再单独标注为 BIS。annotated.md 中已删除 BIS 单独标注，正确 | 低（已处理） |
| 3 | 样本 2 | 拆分审查 | `F-3 lines`（@88:97）标为 CROSS，但原文说 "105 F-3 lines from a cross between BSR-resistant 'Syumari' and susceptible 'Buchishoryukei-1'"，这里 F-3 lines 是杂交后代群体，CROSS 正确。但 `Syumari`（@135:142）和 `Buchishoryukei-1`（@161:177）是亲本品种，应标为 VAR，annotated.md 中已正确标注 | 低（已处理） |
| 4 | 样本 5 | 词块审查 | `average proline`（@97:112）标为 TRT，但 "average" 是统计修饰词，不是性状名称的一部分。应改为 `proline`（@105:112）。验证：text[105:112]="proline" | 中 |
| 5 | 样本 6 | 拆分审查 | `preflowering drought stress`（@290:317）标为 ABS，这是一个复合词，"preflowering" 是时间修饰词，"drought stress" 是胁迫。应考虑是否拆分为 `drought stress`（@303:317）ABS + `preflowering`（@290:302）GST。但 "preflowering drought stress" 作为整体是固定搭配，可保留整体标注 | 低（建议保留） |
| 6 | 样本 7 | 知识审查 | `transcriptome`（@277:290）标为 BM，但 "transcriptome integration" 是数据整合方法，BM 边界应扩展为 `transcriptome integration`（@277:301）。验证：text[277:301]="transcriptome integration" | 低 |
| 7 | 样本 9 | 语义审查 | LOI(QLB-czas1/2/8, CHR)：三个 QTL 都定位到同一个 `chromosomes 1, 2, and 8` 实体（@65:88），但 QLB-czas1 应在 Chr1，QLB-czas2 在 Chr2，QLB-czas8 在 Chr8。将三个 QTL 都关联到同一个多染色体枚举实体，语义不精确，但考虑到原文确实将三者并列描述，且拆分 CHR 实体会增加复杂度，建议保留 | 低（建议保留） |
| 8 | 样本 4 | 语义审查 | `USE(sorghum, marker assisted selection)` 在样本 6 中标注，但 K8 §2.6 规定 USE 关系 head 必须是 VAR，不能是 CROP。应删除该关系，或将 head 改为具体品种 VAR | 高 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 1 | 知识审查 | `KNOTTED ARABIDOPSIS THALIANA7 (KNAT7)`（@206:243）标为 GENE，边界包含全称和缩写。这是合理的整体标注（含括号缩写），训练数据中有先例，保留 |
| P2 | 样本 3 | 知识审查 | `CCD7`、`CCD8`、`MAX1` 是独脚金内酯生物合成基因，标为 GENE 正确。原文说 "Loss-of-function mutations in CCD7, CCD8, MAX1, and DUF genes"，DUF 已正确删除 |
| P3 | 样本 7 | 知识审查 | `abscisic acid`、`gibberellic acid`、`brassinosteroid`、`auxin` 在原文中并列出现，但 annotated.md 中未标注这些植物激素。这些是信号分子，在胁迫响应语境中可标为 ABS，但在基因功能语境中不强制标注。建议不标 |
| P4 | 样本 8 | 知识审查 | `phenotypic diversity`（@120:139）标为 TRT，但 "diversity" 是多样性描述，不是具体性状。考虑到训练数据中有类似标注，保留 |
| P5 | 样本 9 | 词块审查 | `Bulked segregant analysis`（@265:290）标为 BM 正确；`RNA sequencing`（@295:309）标为 BM 正确（遗传分析方法） |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 1：若修正 LOI(SCAR_3456624, Pc39) 的 tail 锚点为 @136:140，需同步修改关系的 tail_start/tail_end |
| A2 | 样本 5：若 `average proline` 改为 `proline`，需同步修改所有依赖该实体的 HAS 关系（Qing1 HAS proline；Long4 HAS proline）的 tail_start/tail_end |
| A3 | 样本 6：若删除 USE(sorghum, marker assisted selection)，需同步检查是否有其他关系依赖 `sorghum`（@230:237）或 `marker assisted selection`（@258:283） |
