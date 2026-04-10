# chunk_028 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_028（10 条样本）
**输入物**：chunk_028.json + chunk_028_annotated.md + chunk_028_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 2 | 语义审查 | AFF(45 degrees C @117:129 ABS, aged oat (Avena sativa) seeds @35:64 VAR)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 VAR。ABS→VAR 不是合法的 AFF 关系类型 | 高 |
| 2 | 样本 5 | 语义审查 | AFF(millet @85:91 CROP, drought stress @107:121 ABS)：K8 §2.2 规定 AFF 的 head 应为 GENE/ABS/BIS，不能为 CROP；tail 应为 TRT，不能为 ABS。CROP→ABS 双重违反约束 | 高 |
| 3 | 样本 9 | 语义审查 | M-81E 重复标注：`M-81E`（@137:142）和 `M-81E`（@144:149）两个偏移相邻，原文为 "M-81E. M-81E"（句号分隔），两个 M-81E 指向同一品种，重复标注可能导致关系歧义。需确认是否保留两个实体 | 中 |
| 4 | 样本 6 | 语义审查 | AFF(waterlogging @142:154 ABS, waterlogging sensitive @142:164 TRT)：两实体起始偏移相同（@142），ABS 被包含在 TRT 内（嵌套），与 chunk_026 问题 1 类似，形成嵌套 AFF 关系 | 中 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 3 | 语义审查 | AFF(TRT, TRT) ×5：与 chunk_027 样本 8 一致，TRT→TRT AFF 在训练数据中有先例（性状间相关性），保留 |
| P2 | 样本 1 | 知识审查 | `drought`（@432:439 ABS）与 `drought adaptation`（@432:449 TRT）嵌套：ABS 被包含在 TRT 内，与 chunk_026 问题 1 类似，但语义上合理（drought 导致 drought adaptation），保留 |
| P3 | 样本 2 | 语义审查 | USE(aged oat (Avena sativa) seeds @35:64 VAR, AsA @164:167 BM)：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，此处正确，保留 |
| P4 | 样本 6 | 语义审查 | `waterlogging`（@142:154 ABS）与 `waterlogging sensitive`（@142:164 TRT）嵌套：ABS 被包含在 TRT 内，语义上合理，但嵌套 AFF 关系需处理 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 2：若删除 AFF(ABS, VAR)，`45 degrees C` 实体仍有 AFF(45 degrees C, seed vigor) 关系，可安全删除 AFF(ABS, VAR) |
| A2 | 样本 5：若删除 AFF(CROP, ABS)，`millet` 实体仍有 HAS(millet, carbon fixation) 等关系，可安全删除 |
| A3 | 样本 9：若删除重复的 M-81E @144:149，需检查依赖该实体的关系（当前无关系依赖 @144:149，可安全删除） |
| A4 | 样本 6：若删除 AFF(waterlogging, waterlogging sensitive)，需确认是否有其他关系依赖 |
