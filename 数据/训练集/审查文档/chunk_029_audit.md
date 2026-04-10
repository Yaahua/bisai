# chunk_029 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_029.json + chunk_029_annotated.md + chunk_029_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 7 | 4 | 3 | 0 |
| 词块审查 | 0 | 0 | 0 | 0 |
| 知识审查 | 0 | 0 | 0 | 0 |
| **合计** | **7** | **4** | **3** | **0** |

---

## 详细审查结果

### 问题 1：样本 1 — AFF(ABS, CROSS) 类型错误（语义审查，高）

**错误位置**：样本 1，AFF(drought stress @240:254 ABS, Arta/Harmal @172:183 CROSS)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 CROSS。ABS→CROSS 不是合法的 AFF 关系类型。

**修改建议**：删除 AFF(drought stress, Arta/Harmal)。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 2：样本 3 — AFF(ABS, GENE) 类型错误（语义审查，高）

**错误位置**：样本 3，AFF(Cd treatment @85:97 ABS, WRKY/MYB/ERF/bHLH GENE) ×4

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。ABS→GENE 不是合法的 AFF 关系类型。

**修改建议**：删除 AFF(Cd treatment, WRKY/MYB/ERF/bHLH) ×4。若需表达"Cd 处理影响转录因子表达"，可补标 `transcription factor expression` TRT，但当前文本中无此明确表述，不强制补标。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 3：样本 6 — AFF(GENE, GENE) 类型错误（语义审查，高）

**错误位置**：样本 6，AFF(SiARDP @96:102 GENE, SiLTP @116:121 GENE)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。GENE→GENE 不是合法的 AFF 关系类型（与 chunk_027 样本 3 一致）。

**修改建议**：删除 AFF(SiARDP, SiLTP)。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 4：样本 9 — CON(TRT, TRT) 类型错误（语义审查，高）

**错误位置**：样本 9，CON(GWPS @184:188 TRT, grain weight per spike @160:182 TRT)

**问题描述**：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。TRT→TRT 不是合法的 CON 关系类型。

**修改建议**：删除 CON(TRT, TRT)。

**权威依据**：K8 §2.4 CON（合法类型约束）；K2 §2.1

---

### 问题 5：样本 7 — AFF 嵌套关系 ×2（语义审查，中）

**错误位置**：样本 7，AFF(oxidative stress @48:64 ABS, oxidative stress tolerance @48:74 TRT)；AFF(dehydration @340:351 ABS, dehydration tolerance @340:361 TRT)

**问题描述**：两对实体均起始偏移相同，ABS 被包含在 TRT 内（嵌套），形成嵌套 AFF 关系（与 chunk_026/028 同类问题）。

**修改建议**：删除 AFF(oxidative stress, oxidative stress tolerance) 和 AFF(dehydration, dehydration tolerance)（嵌套自引用）。

**权威依据**：error_patterns §3.2（避免嵌套实体间的 AFF 关系）；K2 §1.1

---

### 问题 6：样本 5 — LOI(MRK, CHR) 类型错误（语义审查，中）

**错误位置**：样本 5，LOI(five insertion and deletion markers @68:103 MRK, ~255 kb region @135:149 CHR)

**问题描述**：K8 §2.5 规定 LOI 的 head 应为 QTL/GENE，不能为 MRK。MRK→CHR 不是合法的 LOI 关系类型。

**修改建议**：删除 LOI(MRK, CHR)。

**权威依据**：K8 §2.5 LOI（head: QTL/GENE）；K2 §2.1

---

### 问题 7：样本 8 — AFF 嵌套关系（语义审查，中）

**错误位置**：样本 8，AFF(salt @122:126 ABS, salt tolerance @122:136 TRT)

**问题描述**：两实体起始偏移相同（@122），ABS 被包含在 TRT 内（嵌套），与 chunk_026/028/029 同类问题。

**修改建议**：删除 AFF(salt, salt tolerance)（嵌套自引用）。

**权威依据**：error_patterns §3.2（避免嵌套实体间的 AFF 关系）；K2 §1.1

---

## 总结与改进建议

**必须修改（4 项）**：
1. 样本 1：删除 AFF(ABS, CROSS)（AFF tail 类型错误）
2. 样本 3：删除 AFF(ABS, GENE) ×4（AFF tail 类型错误）
3. 样本 6：删除 AFF(GENE, GENE)（AFF tail 类型错误）
4. 样本 9：删除 CON(TRT, TRT)（CON 类型约束违反）

**建议修改（3 项）**：
5. 样本 7：删除 AFF 嵌套关系 ×2（嵌套自引用）
6. 样本 5：删除 LOI(MRK, CHR)（LOI head 类型错误）
7. 样本 8：删除 AFF(salt, salt tolerance)（嵌套自引用）

**确认保留（0 项）**
