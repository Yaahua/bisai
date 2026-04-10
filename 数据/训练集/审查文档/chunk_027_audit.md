# chunk_027 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_027.json + chunk_027_annotated.md + chunk_027_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 6 | 5 | 1 | 0 |
| 词块审查 | 0 | 0 | 0 | 0 |
| 知识审查 | 2 | 0 | 0 | 2 |
| **合计** | **8** | **5** | **1** | **2** |

---

## 详细审查结果

### 问题 1：样本 4 — CON(CROSS, VAR) 类型错误（语义审查，高）

**错误位置**：样本 4，CON(F5 population @3:16 CROSS, Xinliang52/XL52/W455 VAR) ×3

**问题描述**：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→VAR 不是合法的 CON 关系类型。

**修改建议**：删除 CON(CROSS, VAR) 3 条。

**权威依据**：K8 §2.4 CON（合法类型约束）；K2 §2.1

**联动风险**：删除后 F5 population 实体无关系依赖，可安全删除或保留实体。

---

### 问题 2：样本 7 — CON(CROSS, CROSS) 类型错误（语义审查，高）

**错误位置**：样本 7，CON(crosses @82:89 CROSS, F-2 population @56:70 CROSS)

**问题描述**：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→CROSS 不是合法的 CON 关系类型（与 chunk_025 问题 2 一致）。

**修改建议**：删除 CON(CROSS, CROSS)。

**权威依据**：K8 §2.4 CON（合法类型约束）；K2 §2.1

---

### 问题 3：样本 1 — AFF(GENE, ABS) 类型错误（语义审查，高）

**错误位置**：样本 1，AFF(C2 domain family proteins @43:68 GENE, abiotic stress @101:115 ABS)、AFF(C2 domain family proteins, salt and drought stress @124:147 ABS)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 ABS。GENE→ABS 不是合法的 AFF 关系类型。

**修改建议**：删除 AFF(GENE, ABS) 2 条。若需表达"基因响应胁迫"，可考虑补标 `abiotic stress response` TRT，但当前文本中无此明确表述，不强制补标。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 4：样本 3 — AFF(GENE, GENE) 类型错误（语义审查，高）

**错误位置**：样本 3，AFF(AtOAT @168:173 GENE, proline biosynthesis-associated genes @269:306 GENE)、AFF(AtOAT, proline catabolic gene @331:353 GENE)

**问题描述**：K8 §2.2 规定 AFF 的 tail 应为 TRT，不能为 GENE。GENE→GENE 不是合法的 AFF 关系类型。

**修改建议**：删除 AFF(GENE, GENE) 2 条。

**权威依据**：K8 §2.2 AFF（tail: TRT）；K2 §2.1

---

### 问题 5：样本 5 — USE(CROP, BM) 类型错误（语义审查，高）

**错误位置**：样本 5，USE(hulless oat @50:61 CROP, genotyping-by-sequencing @86:110 BM)

**问题描述**：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，不能是 CROP。

**修改建议**：删除 USE(CROP, BM)。若需表达"使用 genotyping-by-sequencing 对 hulless oat 进行分析"，可改为 USE(hulless oats @143:155 VAR, genotyping-by-sequencing)。

**权威依据**：K8 §2.6 USE（head: VAR）；K2 §2.1

---

### 问题 6：样本 4 — LOI(QTL, MRK) 类型错误（语义审查，中）

**错误位置**：样本 4，LOI(QTL @159:162, SSR marker Xtxp97 @208:225 MRK)

**问题描述**：K8 §2.5 规定 LOI 的 tail 应为 TRT 或 CHR，不能为 MRK（与 chunk_026 问题 4 一致）。

**修改建议**：删除 LOI(QTL, MRK)，保留 LOI(QTL, stem juice yield TRT)。

**权威依据**：K8 §2.5 LOI（tail: TRT/CHR）；K2 §2.1

---

### 问题 7：样本 8 — AFF(TRT, TRT) 类型（语义审查，低）

**审查结论**：AFF(seed-setting rate TRT, Grain number TRT) 等 TRT→TRT 关系，K8 §2.2 规定 AFF head 应为 GENE/ABS/BIS，但 TRT→TRT 的 AFF 在 K6 文献语料库中有先例（性状间相关性）。**确认保留**，但需在 error_patterns 中记录此特殊情况。

**权威依据**：K6 §3.1（TRT→TRT AFF 先例）；K8 §2.2

---

## 总结与改进建议

**必须修改（5 项）**：
1. 样本 4：删除 CON(CROSS, VAR) ×3（关系类型约束违反）
2. 样本 7：删除 CON(CROSS, CROSS)（关系类型约束违反）
3. 样本 1：删除 AFF(GENE, ABS) ×2（AFF tail 类型错误）
4. 样本 3：删除 AFF(GENE, GENE) ×2（AFF tail 类型错误）
5. 样本 5：删除 USE(CROP, BM)，改为 USE(hulless oats VAR, genotyping-by-sequencing)

**建议修改（1 项）**：
6. 样本 4：删除 LOI(QTL, MRK)（LOI tail 类型错误）

**确认保留（2 项）**：AFF(TRT, TRT)（性状间相关性，有先例）；jasmonic acid ABS（胁迫处理语境）
