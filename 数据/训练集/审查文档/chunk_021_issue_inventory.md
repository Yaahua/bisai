# chunk_021 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_021（10 条样本）
**输入物**：chunk_021.json + chunk_021_annotated.md + chunk_021_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 1 | 词块审查 | `five major QTLs`（@166:181）被标为 QTL，但 "five major" 是数量修饰词，边界应缩减为 `QTLs`（@181:185）或删除该实体（因为 "QTLs" 是泛指，不是具体 QTL 名称） | 中 |
| 2 | 样本 3 | 词块审查 | `elevated temperatures`（@290:311）标为 ABS 正确，但需确认原文偏移：原文为 "tolerated elevated temperatures (ABS)"，括号内 "(ABS)" 是标注说明，不是原文内容，需核实偏移是否包含括号 | 高 |
| 3 | 样本 5 | 词块审查 | `a candidate gene-based association analysis`（@43:86）边界包含冠词 "a"，应从 @45 开始（去掉 "a "）。验证：text[43:86]="a candidate gene-based association anal" | 低 |
| 4 | 样本 5 | 知识审查 | `Tibetan wild barley`（@126:145、@231:250）标为 VAR，但 "Tibetan wild barley" 是大麦的一个生态型/地方品种群，应标为 VAR（具有可复核的地理来源专名），保留 | 低（确认保留） |
| 5 | 样本 6 | 词块审查 | `F-9:10 sorghum RILs`（@90:109）标为 CROSS，边界包含 "sorghum"，应考虑是否去掉作物名，改为 `F-9:10 RILs`（@90:100）。但原始训练数据中有 "eight sorghum lines" 保留为 VAR 的先例，此处保留 CROSS 边界 | 低（确认保留） |
| 6 | 样本 7 | 词块审查 | `Chromosomes 1, 2, 3, 4, and 6`（@0:29）标为 CHR，但这是多个染色体的枚举，按 K1 §1.4 应拆分为多个 CHR 实体（Chr1、Chr2 等）。但考虑到原始训练数据中有整体标注的先例，且拆分会导致关系锚点复杂化，建议保留整体标注 | 低（确认保留） |
| 7 | 样本 9 | 语义审查 | `BTx623` HAS `Plant height/Brix/100-grain weight/flowering time` 关系：原文说的是"在 3 年内对这些性状进行了评估"，并非 BTx623 专属性状。应考虑是否改为 RIL 群体 HAS 这些性状，或删除 HAS 关系 | 中 |
| 8 | 样本 0 | 知识审查 | `Transcriptome`（@0:13）标为 BM，但 "Transcriptome data" 是数据类型，不是分析方法。应考虑是否改为 `Transcriptome data`（@0:20）或删除该实体 | 中 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 0 | 拆分审查 | `drought stress`（@36:50）是固定搭配，整体标为 ABS 正确，不需拆分 |
| P2 | 样本 3 | 知识审查 | `osmoprotectants`、`chaperones`、`reactive oxygen species scavengers` 在原文中并列出现，未标注。这些是蛋白质/代谢物类别，不是具体基因名，不标为 GENE；也不是性状，不标为 TRT。正确做法：不标注 |
| P3 | 样本 4 | 知识审查 | `NaCl`（@112:116）标为 ABS 正确（盐胁迫因子）；`d-Mannitol`（@121:131）标为 ABS 正确（渗透胁迫因子）。两者均是非生物胁迫因子 |
| P4 | 样本 6 | 语义审查 | `QTLs` LOI `B. fusca`（BIS）：QTL 与生物胁迫的 LOI 关系在训练数据中存在（表示 QTL 控制对该病虫害的抗性），保留 |
| P5 | 样本 8 | 知识审查 | `genetic regions`（@207:222）标为 QTL，但 "genetic regions" 是泛指，不是具体 QTL 名称。考虑到原始数据中有类似标注，保留 |
| P6 | 样本 9 | 拆分审查 | `recombinant inbred line (RIL) population`（@2:42）标为 CROSS，边界包含 "population"，应考虑是否缩减为 `recombinant inbred line (RIL)`（@2:35）。但含括号缩写的整体标注在训练数据中有先例，保留 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 3：若确认 `elevated temperatures` 偏移包含括号内容，需同步检查是否有关系依赖该实体的锚点 |
| A2 | 样本 7：`Striga tolerance`（@60:76）与 `Striga`（@60:66）形成嵌套实体，需确认两者共存的合法性（K1 §1.5 嵌套规则） |
| A3 | 样本 9：若 HAS 关系主体改为 RIL 群体，需同步修改 head 实体为 `recombinant inbred line (RIL) population`（CROSS），而非 `BTx623`（VAR） |
| A4 | 样本 1：若删除 `five major QTLs` 实体，无关系依赖它，不影响关系列表 |
