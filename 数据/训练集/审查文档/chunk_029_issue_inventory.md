# chunk_029 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_029（10 条样本）
**输入物**：chunk_029.json + chunk_029_annotated.md + chunk_029_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 1 | 语义审查 | AFF(drought stress @240:254 ABS, Arta/Harmal @172:183 CROSS)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 CROSS。ABS→CROSS 不是合法的 AFF 关系类型 | 高 |
| 2 | 样本 6 | 语义审查 | AFF(SiARDP @96:102 GENE, SiLTP @116:121 GENE)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。GENE→GENE 不是合法的 AFF 关系类型 | 高 |
| 3 | 样本 7 | 语义审查 | AFF(oxidative stress @48:64 ABS, oxidative stress tolerance @48:74 TRT)：两实体起始偏移相同（@48），ABS 被包含在 TRT 内（嵌套），形成嵌套 AFF 关系（与 chunk_026/chunk_028 同类问题） | 中 |
| 4 | 样本 7 | 语义审查 | AFF(dehydration @340:351 ABS, dehydration tolerance @340:361 TRT)：两实体起始偏移相同（@340），ABS 被包含在 TRT 内（嵌套），形成嵌套 AFF 关系 | 中 |
| 5 | 样本 9 | 语义审查 | CON(GWPS @184:188 TRT, grain weight per spike @160:182 TRT)：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。TRT→TRT 不是合法的 CON 关系类型。此处 GWPS 是 grain weight per spike 的缩写，应改为 CON(grain weight per spike GENE全称, GWPS 缩写)，但两者均为 TRT，无法直接改为合法 CON。建议删除 CON(TRT, TRT) | 高 |
| 6 | 样本 3 | 语义审查 | AFF(Cd treatment @85:97 ABS, WRKY @8:12 GENE)、AFF(Cd treatment, MYB/ERF/bHLH GENE)：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。ABS→GENE 不是合法的 AFF 关系类型 | 高 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 8 | 语义审查 | AFF(salt @122:126 ABS, salt tolerance @122:136 TRT)：两实体起始偏移相同（@122），ABS 被包含在 TRT 内（嵌套），与 chunk_026/028/029 同类问题，建议删除 |
| P2 | 样本 9 | 语义审查 | AFF(SRN @83:86 TRT, SL @64:66 TRT)、AFF(SD @91:93 TRT, SL @64:66 TRT)：TRT→TRT AFF，与 chunk_027/028 一致，有先例，保留 |
| P3 | 样本 5 | 语义审查 | LOI(five insertion and deletion markers @68:103 MRK, ~255 kb region @135:149 CHR)：K8 §2.5 规定 LOI 的 head 应为 QTL/GENE，不能为 MRK。MRK→CHR 不是合法的 LOI 关系类型 | 

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 1：若删除 AFF(ABS, CROSS)，`drought stress` 实体无其他关系依赖，可安全删除该关系 |
| A2 | 样本 6：若删除 AFF(GENE, GENE)，`SiARDP` 和 `SiLTP` 实体无其他关系依赖，可安全删除该关系 |
| A3 | 样本 3：若删除 AFF(ABS, GENE) ×4，`Cd treatment` 实体无其他关系依赖，可安全删除这些关系 |
| A4 | 样本 9：若删除 CON(TRT, TRT)，`GWPS` 和 `grain weight per spike` 实体仍有 LOI 关系依赖，可安全删除 CON |
| A5 | 样本 5：若删除 LOI(MRK, CHR)，`five insertion and deletion markers` 实体无其他关系依赖，可安全删除该关系 |
