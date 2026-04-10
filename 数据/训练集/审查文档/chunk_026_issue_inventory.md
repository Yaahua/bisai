# chunk_026 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_026（10 条样本）
**输入物**：chunk_026.json + chunk_026_annotated.md + chunk_026_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 6 | 语义审查 | AFF(drought stress @105:119 ABS, drought stress response @105:128 TRT)：两实体起始偏移相同（@105），且 ABS 被包含在 TRT 内（嵌套），形成自引用关系。AFF 关系的 head 和 tail 不应指向嵌套关系中的内外层实体 | 高 |
| 2 | 样本 8 | 语义审查 | CON(diastatic power @61:76 TRT, malting quality trait @80:101 TRT)：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。TRT→TRT 不是合法的 CON 关系类型 | 高 |
| 3 | 样本 8 | 语义审查 | AFF(BC1F1 individuals @107:124 VAR, final progenies @174:189 VAR)：AFF 关系的 head/tail 应为 GENE/ABS/BIS→TRT，VAR→VAR 不是合法的 AFF 关系类型 | 高 |
| 4 | 样本 7 | 知识审查 | `abscisic acid`（@239:252）标为 ABS，与 chunk_025 问题 4/5 一致：ABA 是植物激素，不是非生物胁迫因子。但在 chunk_026 样本 7 的语境中，abscisic acid 作为"外源植物激素"处理，与 salt/drought/cold 并列，可视为胁迫信号分子，保留 ABS 标注 | 低（建议保留） |
| 5 | 样本 7 | 知识审查 | `methyl jasmonate`（@254:270）和 `salicylic acid`（@272:285）标为 ABS，茉莉酸甲酯和水杨酸是植物激素/信号分子，与 abscisic acid 同类，在胁迫处理语境中可视为 ABS，保留 | 低（建议保留） |
| 6 | 样本 5 | 语义审查 | LOI(heat-stress QTL @69:84, bPb-5529 @101:109 MRK)：K8 §2.5 规定 LOI 的 tail 应为 TRT 或 CHR，不能为 MRK。应删除该关系 | 高 |
| 7 | 样本 0 | 知识审查 | HAS(E232 x Murasakimochi @121:141 CROSS, yield-related traits @55:74 TRT)：K8 §2.3 规定 HAS 关系为 HAS(VAR, TRT)，head 必须是 VAR，不能是 CROSS | 高 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 2 | 知识审查 | `flavonoid biosynthesis`（@75:96）标为 TRT，是代谢通路，不是具体性状。但 "enriched metabolic pathways" 语境下，代谢通路活性可视为 TRT，保留 |
| P2 | 样本 6 | 语义审查 | `drought stress`（@105:119 ABS）与 `drought stress response`（@105:128 TRT）嵌套：ABS 被包含在 TRT 内，嵌套合理（胁迫因子包含在胁迫响应性状中），但两实体起始偏移相同，需确认是否合法 |
| P3 | 样本 9 | 词块审查 | `lignin synthesis`（@250:266）标为 TRT，但 lignin synthesis 是生物学过程，不是农艺性状。考虑到木质素含量是可量化性状，保留 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 6：若删除 AFF(drought stress, drought stress response)，需检查是否有其他关系依赖 `drought stress response` 实体 |
| A2 | 样本 8：若删除 CON(TRT, TRT) 和 AFF(VAR, VAR)，需确认无其他关系依赖这些实体 |
| A3 | 样本 5：若删除 LOI(QTL, MRK)，需确认 `bPb-5529` 实体是否还有其他关系依赖（当前无其他依赖） |
| A4 | 样本 0：若删除 HAS(CROSS, TRT)，需考虑是否改为 HAS(E232 VAR, yield-related traits) 或 HAS(Murasakimochi VAR, yield-related traits) |
