# chunk_025 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_025（10 条样本）
**输入物**：chunk_025.json + chunk_025_annotated.md + chunk_025_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 3 | 语义审查 | USE(QTL-seq analysis @2:18 BM, F2 population @116:129 CROSS)：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，不能是 BM。此处 head 为 BM，tail 为 CROSS，双重违反约束 | 高 |
| 2 | 样本 3 | 语义审查 | CON(F2 population @116:129 CROSS, crosses between... @143:244 CROSS)：K8 §2.4 规定 CON 关系为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→CROSS 不是合法的 CON 关系类型 | 高 |
| 3 | 样本 9 | 知识审查 | `PSI`（@219:222）、`PSII`（@62:66、@265:269）改为 GENE，但光系统 I/II 是蛋白质复合体，不是单一基因。与 chunk_024 样本 7 的处理方式不一致，需统一决策 | 中 |
| 4 | 样本 0 | 知识审查 | `abscisic acid`（@107:120）标为 ABS，但脱落酸（ABA）是植物激素，不是非生物胁迫因子。K8 §1.7 ABS 的定义是非生物胁迫（drought、heat 等），ABA 是信号分子，不应标为 ABS | 中 |
| 5 | 样本 2 | 知识审查 | `ABA`（@363:366）标为 ABS，同上，ABA 是植物激素，不是非生物胁迫因子，应删除或改为不标 | 中 |
| 6 | 样本 3 | 词块审查 | `transgressive segregation of DTH toward late heading`（@270:322）标为 TRT，边界包含 "of DTH toward late heading" 修饰词。应缩减为 `transgressive segregation`（@270:294）。验证：text[270:294]="transgressive segregation" ✓ | 中 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 3 | 语义审查 | OCI(transgressive segregation of DTH toward late heading @270:322 TRT, late heading @310:322 TRT)：外层 TRT 包含内层 TRT，且 OCI 关系（性状在某时期出现）用于 TRT→TRT 不合适，OCI 应为 TRT→GST。但 late heading 已改为 TRT，需重新评估 |
| P2 | 样本 5 | 知识审查 | `glutathione S-transferase`（@177:201）和 `MYB-bHLH-WD40 complex`（@305:327）标为 GENE，是基因家族/复合体名称，与 chunk_024 问题 3/4 类似，需统一处理 |
| P3 | 样本 7 | 语义审查 | AFF(biotic stresses @137:152 BIS, ROS homeostasis @76:91 TRT)：K8 §2.2 AFF 的 head 可以是 ABS 或 BIS，正确 |
| P4 | 样本 6 | 语义审查 | AFF(Chalk5 mRNA levels @182:200 TRT, grain chalkiness @241:257 TRT)：TRT→TRT 的 AFF 关系，表示一个性状影响另一个性状，K8 §2.2 允许此类型，正确 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 3：若删除 USE(BM, CROSS) 和 CON(CROSS, CROSS)，需检查是否有其他关系依赖这两个实体 |
| A2 | 样本 0/2：若删除 `abscisic acid` 和 `ABA` 的 ABS 标注，无关系依赖，可安全删除 |
| A3 | 样本 3：若缩减 `transgressive segregation of DTH toward late heading` 边界，需同步修改 OCI 关系的 head_end |
