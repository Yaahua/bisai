# chunk_030 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_030.json + chunk_030_annotated.md + chunk_030_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 7 | 6 | 0 | 1 |
| 词块审查 | 0 | 0 | 0 | 0 |
| 知识审查 | 0 | 0 | 0 | 0 |
| **合计** | **7** | **6** | **0** | **1** |

---

## 详细审查结果

### 问题 1：样本 0 — AFF(ABS, GENE) 类型错误（语义审查，高）

**错误位置**：样本 0，AFF(saline-alkali treatment @22:45 ABS, GsNAC2 @0:6 GENE)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。ABS→GENE 不是合法的 AFF 关系类型。

**修改建议**：删除 AFF(saline-alkali treatment, GsNAC2)。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 2：样本 3 — USE(BM, TRT) 类型错误（语义审查，高）

**错误位置**：样本 3，USE(GWAS @0:4 BM, RSA traits @17:27 TRT)、USE(GWAS, GP accuracy @32:43 TRT)

**问题描述**：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，不能是 BM。BM→TRT 双重违反约束。

**修改建议**：删除 USE(BM, TRT) ×2。

**权威依据**：K8 §2.6 USE（head: VAR, tail: BM）；K2 §2.1

---

### 问题 3：样本 4 — CON(CROSS, CROP) 类型错误（语义审查，高）

**错误位置**：样本 4，CON(Arta/Harmal population @122:144 CROSS, barley @225:231 CROP)

**问题描述**：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→CROP 不是合法的 CON 关系类型。

**修改建议**：删除 CON(CROSS, CROP)。

**权威依据**：K8 §2.4 CON（合法类型约束）；K2 §2.1

---

### 问题 4：样本 5 — USE(BM, GENE) 类型错误（语义审查，高）

**错误位置**：样本 5，USE(CRISPR/Cas9 @140:151 BM, SiUBC39 @59:66 GENE)

**问题描述**：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，tail 必须是 BM。BM→GENE 双重违反约束。

**修改建议**：删除 USE(CRISPR/Cas9, SiUBC39)。

**权威依据**：K8 §2.6 USE（head: VAR, tail: BM）；K2 §2.1

---

### 问题 5：样本 7 — LOI(MRK, QTL) 类型错误（语义审查，高）

**错误位置**：样本 7，LOI(Molecular markers @0:17 MRK, morphological loci @32:50 QTL)

**问题描述**：K8 §2.5 规定 LOI 的 head 应为 QTL/GENE，不能为 MRK。MRK→QTL 不是合法的 LOI 关系类型（与 chunk_029 样本 5 一致）。

**修改建议**：删除 LOI(MRK, QTL)。

**权威依据**：K8 §2.5 LOI（head: QTL/GENE）；K2 §2.1

---

### 问题 6：样本 8 — AFF(GENE, GENE) 类型错误（语义审查，高）

**错误位置**：样本 8，AFF(SbWRKY50 @0:8 GENE, SOS1 @56:60 GENE)、AFF(SbWRKY50 @100:108, SOS1 @153:157)、AFF(SbWRKY50 @100:108, HKT1 @162:166)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。GENE→GENE 不是合法的 AFF 关系类型（与 chunk_027/029 同类问题）。

**修改建议**：删除 AFF(GENE, GENE) ×3。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 7：样本 9 — AFF(BIS, CROP) 类型（语义审查，低）

**审查结论**：AFF(Septoria avenae f. sp. avenae BIS, oats CROP) 和 AFF(septoria leaf blotch disease BIS, oats CROP)，K8 §2.2 规定 AFF 的 tail 应为 TRT，但 K6 文献语料库中有 BIS→CROP AFF 先例（病原体侵染作物，表达"影响"语义）。**确认保留**，记录为特殊情况。

**权威依据**：K6 §3.2（BIS→CROP AFF 先例）；K8 §2.2

---

## 总结与改进建议

**必须修改（6 项）**：
1. 样本 0：删除 AFF(ABS, GENE)（AFF tail 类型错误）
2. 样本 3：删除 USE(BM, TRT) ×2（USE head/tail 双重类型错误）
3. 样本 4：删除 CON(CROSS, CROP)（CON 类型约束违反）
4. 样本 5：删除 USE(BM, GENE)（USE head/tail 双重类型错误）
5. 样本 7：删除 LOI(MRK, QTL)（LOI head 类型错误）
6. 样本 8：删除 AFF(GENE, GENE) ×3（AFF tail 类型错误）

**建议修改（0 项）**

**确认保留（1 项）**：AFF(BIS, CROP)（病原体侵染作物，有先例）
