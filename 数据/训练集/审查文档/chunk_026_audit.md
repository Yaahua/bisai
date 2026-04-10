# chunk_026 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_026.json + chunk_026_annotated.md + chunk_026_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 5 | 4 | 0 | 1 |
| 词块审查 | 0 | 0 | 0 | 0 |
| 知识审查 | 3 | 0 | 0 | 3 |
| **合计** | **8** | **4** | **0** | **4** |

---

## 详细审查结果

### 问题 1：样本 6 — AFF 自引用嵌套（语义审查，高）

**错误位置**：样本 6，AFF(drought stress @105:119 ABS, drought stress response @105:128 TRT)

**问题描述**：`drought stress`（@105:119）被包含在 `drought stress response`（@105:128）内（相同起始偏移，ABS 是 TRT 的子串）。AFF 关系的 head 和 tail 指向嵌套关系中的内外层实体，形成逻辑上的自引用（胁迫因子"影响"包含它自身的胁迫响应性状）。虽然语义上有一定道理，但这种嵌套 AFF 关系在训练数据中不常见，且偏移重叠可能导致解析错误。

**修改建议**：删除 AFF(drought stress, drought stress response)。保留 AFF(SiUBC39, drought stress response) 即可表达基因影响胁迫响应的语义。

**权威依据**：error_patterns §3.2（避免嵌套实体间的 AFF 关系）；K2 §1.1

**联动风险**：删除该关系不影响其他实体。

---

### 问题 2：样本 8 — CON(TRT, TRT) 类型错误（语义审查，高）

**错误位置**：样本 8，CON(diastatic power @61:76 TRT, malting quality trait @80:101 TRT)

**问题描述**：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。TRT→TRT 不是合法的 CON 关系类型。原文说 "diastatic power, a malting quality trait"，这是同位语关系（diastatic power 是 malting quality trait 的一种），不应用 CON 表示。

**修改建议**：删除 CON(diastatic power, malting quality trait)。

**权威依据**：K8 §2.4 CON（合法类型约束）；K2 §2.1

**联动风险**：删除该关系不影响其他实体。

---

### 问题 3：样本 8 — AFF(VAR, VAR) 类型错误（语义审查，高）

**错误位置**：样本 8，AFF(BC1F1 individuals @107:124 VAR, final progenies @174:189 VAR)

**问题描述**：K8 §2.2 规定 AFF 关系的 head 为 GENE/ABS/BIS，tail 为 TRT。VAR→VAR 不是合法的 AFF 关系类型。

**修改建议**：删除 AFF(BC1F1 individuals, final progenies)。

**权威依据**：K8 §2.2 AFF（head: GENE/ABS/BIS, tail: TRT）；K2 §2.1

**联动风险**：删除该关系不影响其他实体。

---

### 问题 4：样本 5 — LOI(QTL, MRK) 类型错误（语义审查，高）

**错误位置**：样本 5，LOI(heat-stress QTL @69:84 QTL, bPb-5529 @101:109 MRK)

**问题描述**：K8 §2.5 规定 LOI 的 tail 应为 TRT 或 CHR，不能为 MRK。此处 tail 为 MRK（bPb-5529），违反关系类型约束。原文说 "Two heat-stress QTL were mapped to bPb-5529 on 5H"，正确的关系应为 LOI(heat-stress QTL, 5H CHR)，而非 LOI(QTL, MRK)。

**修改建议**：删除 LOI(heat-stress QTL, bPb-5529)，保留 LOI(heat-stress QTL, 5H)。

**权威依据**：K8 §2.5 LOI（tail: TRT/CHR）；K2 §2.1

**联动风险**：删除该关系不影响其他实体。

---

### 问题 5：样本 0 — HAS(CROSS, TRT) 类型错误（语义审查，高）

**错误位置**：样本 0，HAS(E232 x Murasakimochi @121:141 CROSS, yield-related traits @55:74 TRT)

**问题描述**：K8 §2.3 规定 HAS 关系为 HAS(VAR, TRT)，head 必须是 VAR，不能是 CROSS。

**修改建议**：删除 HAS(CROSS, TRT)，改为 HAS(E232 @121:125 VAR, yield-related traits) 和 HAS(Murasakimochi @128:141 VAR, yield-related traits)。

**权威依据**：K8 §2.3 HAS（head: VAR）；K2 §2.1

**联动风险**：需新增 2 条 HAS 关系。

---

### 问题 6：样本 7 — 植物激素标为 ABS（知识审查，低）

**审查结论**：`abscisic acid`、`methyl jasmonate`、`salicylic acid` 在本样本中作为"外源植物激素处理"与 salt/drought/cold 并列，在胁迫处理语境中可视为 ABS（胁迫信号分子）。与 chunk_025 中 ABA 的处理不同（chunk_025 中 ABA 出现在基因功能语境中）。**确认保留**。

**权威依据**：K8 §1.7 ABS（胁迫信号分子可标为 ABS）；error_patterns §2.3（语境决定标签）

---

## 总结与改进建议

**必须修改（4 项）**：
1. 样本 6：删除 AFF(drought stress, drought stress response)（嵌套自引用）
2. 样本 8：删除 CON(TRT, TRT)（关系类型约束违反）
3. 样本 8：删除 AFF(VAR, VAR)（关系类型约束违反）
4. 样本 5：删除 LOI(QTL, MRK)（LOI tail 类型错误）

**建议修改（1 项）**：
5. 样本 0：将 HAS(CROSS, TRT) 改为 HAS(E232 VAR, TRT) + HAS(Murasakimochi VAR, TRT)

**确认保留（4 项）**：植物激素 ABS 标注（胁迫处理语境）、`flavonoid biosynthesis` TRT、`lignin synthesis` TRT、`drought stress`/`drought stress response` 嵌套
