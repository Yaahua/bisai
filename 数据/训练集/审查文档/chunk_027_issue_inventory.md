# chunk_027 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_027（10 条样本）
**输入物**：chunk_027.json + chunk_027_annotated.md + chunk_027_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 4 | 语义审查 | CON(F5 population @3:16 CROSS, Xinliang52 @57:67 VAR)、CON(F5 population, XL52)、CON(F5 population, W455)：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→VAR 不是合法的 CON 关系类型 | 高 |
| 2 | 样本 7 | 语义审查 | CON(crosses @82:89 CROSS, F-2 population @56:70 CROSS)：CROSS→CROSS 不是合法的 CON 关系类型（同 chunk_025 问题 2） | 高 |
| 3 | 样本 1 | 语义审查 | AFF(C2 domain family proteins @43:68 GENE, abiotic stress @101:115 ABS)、AFF(C2 domain family proteins, salt and drought stress @124:147 ABS)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 ABS。GENE→ABS 不是合法的 AFF 关系类型 | 高 |
| 4 | 样本 3 | 语义审查 | AFF(AtOAT @168:173 GENE, proline biosynthesis-associated genes @269:306 GENE)、AFF(AtOAT, proline catabolic gene @331:353 GENE)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。GENE→GENE 不是合法的 AFF 关系类型 | 高 |
| 5 | 样本 5 | 语义审查 | USE(hulless oat @50:61 CROP, genotyping-by-sequencing @86:110 BM)：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，不能是 CROP | 高 |
| 6 | 样本 8 | 语义审查 | AFF(seed-setting rate @4:21 TRT, Grain number @67:79 TRT)、AFF(Grain number, flower number @100:113 TRT)：K8 §2.2 规定 AFF 的 head 应为 GENE/ABS/BIS，不能为 TRT。TRT→TRT 的 AFF 关系类型需确认是否合法 | 中 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 0 | 知识审查 | AFF(Puccinia striiformis @132:182 BIS, stripe rust infection @41:62 BIS)：BIS→BIS 关系，病原体导致病害，K2 §1.3 允许 BIS AFF BIS，保留 |
| P2 | 样本 2 | 知识审查 | `jasmonic acid`（@249:261）标为 ABS，茉莉酸是植物激素，在胁迫处理语境中可视为 ABS，与 chunk_026 样本 7 保持一致，保留 |
| P3 | 样本 4 | 语义审查 | LOI(QTL @159:162, SSR marker Xtxp97 @208:225 MRK)：同 chunk_026 问题 4，LOI tail 不能为 MRK，应删除 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 4：若删除 CON(CROSS, VAR) 3 条，需确认 F5 population 实体是否还有其他关系依赖 |
| A2 | 样本 7：若删除 CON(CROSS, CROSS)，需确认是否有其他关系依赖 |
| A3 | 样本 1：若删除 AFF(GENE, ABS) 2 条，需考虑是否补标响应性状 TRT |
| A4 | 样本 3：若删除 AFF(GENE, GENE) 2 条，需确认是否有其他关系依赖 |
