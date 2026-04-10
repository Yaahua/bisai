# chunk_028 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_028.json + chunk_028_annotated.md + chunk_028_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 4 | 2 | 2 | 0 |
| 词块审查 | 0 | 0 | 0 | 0 |
| 知识审查 | 0 | 0 | 0 | 0 |
| **合计** | **4** | **2** | **2** | **0** |

---

## 详细审查结果

### 问题 1：样本 2 — AFF(ABS, VAR) 类型错误（语义审查，高）

**错误位置**：样本 2，AFF(45 degrees C @117:129 ABS, aged oat (Avena sativa) seeds @35:64 VAR)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 VAR。ABS→VAR 不是合法的 AFF 关系类型。原文语义是"在 45°C 下老化种子"，这是实验处理条件，不是 AFF 关系。

**修改建议**：删除 AFF(45 degrees C, aged oat seeds)。保留 AFF(45 degrees C, seed vigor) 即可表达胁迫影响种子活力的语义。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

**联动风险**：删除后 `45 degrees C` 实体仍有 AFF(45 degrees C, seed vigor) 关系，可安全删除。

---

### 问题 2：样本 5 — AFF(CROP, ABS) 类型错误（语义审查，高）

**错误位置**：样本 5，AFF(millet @85:91 CROP, drought stress @107:121 ABS)

**问题描述**：K8 §2.2 规定 AFF 的 head 应为 GENE/ABS/BIS，不能为 CROP；tail 应为 TRT，不能为 ABS。CROP→ABS 双重违反约束。

**修改建议**：删除 AFF(CROP, ABS)。

**权威依据**：K8 §2.2 AFF（head: GENE/ABS/BIS, tail: TRT）；K2 §2.1

**联动风险**：删除后 `millet` 实体仍有 HAS(millet, carbon fixation) 等关系，可安全删除。

---

### 问题 3：样本 9 — M-81E 重复标注（语义审查，中）

**错误位置**：样本 9，`M-81E`（@137:142）和 `M-81E`（@144:149）

**问题描述**：原文为 "than M-81E. M-81E had lower H2O2 content..."，两个 M-81E 分别出现在不同句子中，均指同一品种。重复标注本身不违反规则，但 @144:149 的 M-81E 无任何关系依赖，是冗余标注。

**修改建议**：删除 `M-81E`（@144:149），保留 `M-81E`（@137:142）及其关系。

**权威依据**：K1 §1.4（避免冗余标注）；error_patterns §2.1

---

### 问题 4：样本 6 — AFF 嵌套关系（语义审查，中）

**错误位置**：样本 6，AFF(waterlogging @142:154 ABS, waterlogging sensitive @142:164 TRT)

**问题描述**：`waterlogging`（@142:154）被包含在 `waterlogging sensitive`（@142:164）内（相同起始偏移），形成嵌套 AFF 关系（与 chunk_026 问题 1 类似）。

**修改建议**：删除 AFF(waterlogging, waterlogging sensitive)（嵌套自引用）。保留 AFF(waterlogging, waterlogging tolerant) 即可。

**权威依据**：error_patterns §3.2（避免嵌套实体间的 AFF 关系）；K2 §1.1

---

## 总结与改进建议

**必须修改（2 项）**：
1. 样本 2：删除 AFF(ABS, VAR)（AFF tail 类型错误）
2. 样本 5：删除 AFF(CROP, ABS)（AFF head/tail 双重类型错误）

**建议修改（2 项）**：
3. 样本 9：删除冗余 `M-81E`（@144:149）实体
4. 样本 6：删除 AFF(waterlogging, waterlogging sensitive)（嵌套自引用）

**确认保留（0 项）**
