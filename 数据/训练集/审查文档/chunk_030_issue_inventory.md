# chunk_030 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_030（10 条样本）
**输入物**：chunk_030.json + chunk_030_annotated.md + chunk_030_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 0 | 语义审查 | AFF(saline-alkali treatment @22:45 ABS, GsNAC2 @0:6 GENE)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。ABS→GENE 不是合法的 AFF 关系类型 | 高 |
| 2 | 样本 5 | 语义审查 | USE(CRISPR/Cas9 @140:151 BM, SiUBC39 @59:66 GENE)：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，不能是 BM。BM→GENE 不是合法的 USE 关系类型 | 高 |
| 3 | 样本 7 | 语义审查 | LOI(Molecular markers @0:17 MRK, morphological loci @32:50 QTL)：K8 §2.5 规定 LOI 的 head 应为 QTL/GENE，不能为 MRK。MRK→QTL 不是合法的 LOI 关系类型 | 高 |
| 4 | 样本 8 | 语义审查 | AFF(SbWRKY50 @0:8 GENE, SOS1 @56:60 GENE)、AFF(SbWRKY50 @100:108, SOS1 @153:157)、AFF(SbWRKY50 @100:108, HKT1 @162:166)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。GENE→GENE 不是合法的 AFF 关系类型（与 chunk_027/029 同类问题） | 高 |
| 5 | 样本 4 | 语义审查 | CON(Arta/Harmal population @122:144 CROSS, barley @225:231 CROP)：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→CROP 不是合法的 CON 关系类型 | 高 |
| 6 | 样本 3 | 语义审查 | USE(GWAS @0:4 BM, RSA traits @17:27 TRT)、USE(GWAS, GP accuracy @32:43 TRT)：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，不能是 BM。BM→TRT 不是合法的 USE 关系类型 | 高 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 9 | 语义审查 | AFF(Septoria avenae f. sp. avenae @45:74 BIS, oats @19:23 CROP)、AFF(septoria leaf blotch disease @76:104 BIS, oats @19:23 CROP)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 CROP。BIS→CROP 不是合法的 AFF 关系类型。但 K6 文献语料库中有 BIS→CROP AFF 先例（病原体侵染作物），需确认 |
| P2 | 样本 0 | 语义审查 | `GsNAC2`（@79:85 GENE）与 `GsNAC2-overexpressing sorghum`（@79:108 VAR）起始偏移相同（@79），形成嵌套实体。K1 §1.3 规定嵌套实体需处理，但此处 GENE 被包含在 VAR 内，语义上合理（VAR 包含 GENE 名称），保留 |
| P3 | 样本 4 | 语义审查 | HAS(Arta/Harmal population @122:144 CROSS, drought tolerance @204:221 TRT)：K8 §2.3 规定 HAS 关系为 HAS(VAR/CROP/CROSS, TRT)，CROSS→TRT 是否合法需确认。K8 §2.3 明确列出 CROSS 为合法 head 类型，保留 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 0：若删除 AFF(ABS, GENE)，`saline-alkali treatment` 实体无其他关系依赖，可安全删除该关系 |
| A2 | 样本 5：若删除 USE(BM, GENE)，`CRISPR/Cas9` 实体无其他关系依赖，可安全删除该关系 |
| A3 | 样本 7：若删除 LOI(MRK, QTL)，`Molecular markers` 实体无其他关系依赖，可安全删除该关系 |
| A4 | 样本 8：若删除 AFF(GENE, GENE) ×3，`SbWRKY50` 和 `SOS1`/`HKT1` 实体无其他关系依赖，可安全删除这些关系 |
| A5 | 样本 4：若删除 CON(CROSS, CROP)，`Arta/Harmal population` 实体仍有 HAS 关系依赖，可安全删除 CON |
| A6 | 样本 3：若删除 USE(BM, TRT) ×2，`GWAS` 实体无其他关系依赖，可安全删除这些关系 |
