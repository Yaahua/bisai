# chunk_022 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_022.json + chunk_022_annotated.md + chunk_022_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 2 | 0 | 0 | 2 |
| 语义审查 | 3 | 2 | 0 | 1 |
| 词块审查 | 2 | 0 | 1 | 1 |
| 知识审查 | 3 | 0 | 1 | 2 |
| **合计** | **10** | **2** | **2** | **6** |

---

## 详细审查结果

### 问题 1：样本 1 — LOI 关系锚点错误（语义审查，高）

**错误位置**：样本 1，LOI(SCAR_3456624 @102:114, Pc39 @63:67)

**问题描述**：原文为 "The closely linked marker SCAR_3456624 is within 0.37 cM of Pc39"，这里的 Pc39 是第二次出现（@136:140），才是被定位的那个。当前关系的 tail 指向 @63:67（第一次出现的 Pc39，在 "resistant Pc39 allele" 语境中），语义不准确。

**修改建议**：将 LOI 关系的 tail 锚点从 @63:67 改为 @136:140（第二次出现的 Pc39）。

**权威依据**：error_patterns §3.5（关系锚点必须绑定到真实承担语义的那次出现）；K2 §1.1

**联动风险**：需同步修改关系的 tail_start=136、tail_end=140。

---

### 问题 2：样本 6 — USE 关系主体类型错误（语义审查，高）

**错误位置**：样本 6，USE(sorghum @230:237 CROP, marker assisted selection @258:283 BM)

**问题描述**：K8 §2.6 规定 USE 关系的 head 必须是 VAR（品种），不能是 CROP（作物）。此处 head 为 `sorghum`（CROP），违反关系类型约束。

**修改建议**：删除该 USE 关系。若原文有具体品种名，可改 head 为对应 VAR；但本样本无具体品种名，应直接删除。

**权威依据**：K8 §2.6 USE（head: VAR, tail: BM）；K2 §2.1（关系类型约束）

**联动风险**：删除该关系不影响其他实体和关系。

---

### 问题 3：样本 5 — `average proline` 边界（词块审查，中）

**错误位置**：样本 5，`average proline`（@97:112）TRT

**问题描述**：`average` 是统计修饰词，不是性状名称的一部分。K1 §1.2 规定修饰词不应包含在实体边界内。应改为 `proline`（@105:112）。

**修改建议**：修改为 `proline`（@105:112）TRT。

**权威依据**：K1 §1.2（修饰词边界规则）；error_patterns §2.2

**联动风险**：需同步修改 HAS(Qing1, proline) 和 HAS(Long4, proline) 的 tail_start=105、tail_end=112。

---

### 问题 4：样本 7 — `transcriptome` 边界（知识审查，低）

**错误位置**：样本 7，`transcriptome`（@277:290）BM

**问题描述**：原文为 "based on transcriptome integration"，完整的分析方法是 "transcriptome integration"，边界应扩展为 @277:301。

**修改建议**：扩展为 `transcriptome integration`（@277:301）BM。

**权威依据**：K1 §1.1（实体边界应包含完整的语义单元）

**联动风险**：无关系依赖该实体，修改不影响关系列表。

---

### 问题 5：样本 6 — `preflowering drought stress` 边界（拆分审查，低）

**审查结论**：`preflowering drought stress` 作为整体是固定搭配，在育种文献中常见（指花前干旱胁迫），标为 ABS 整体合理。**确认保留**。

**权威依据**：error_patterns §2.1（固定搭配不拆分）

---

### 问题 6：样本 9 — 多 QTL 共享 CHR 实体（语义审查，低）

**审查结论**：三个 QTL 共享 `chromosomes 1, 2, and 8`（@65:88）实体，语义不精确但符合原文并列描述。考虑到拆分 CHR 实体会增加复杂度，且训练数据中有类似先例，**确认保留**。

**权威依据**：error_patterns §2.5（多染色体枚举可整体标注）

---

### 问题 7：样本 2 — BSR 标签处理（知识审查，低）

**审查结论**：`BSR`（@120:123）改为 BIS 正确（Brown Stem Rot 是大豆茎褐腐病，属于病害）；`BSR inoculation tests`（@183:204）标为 BM 正确；BIS 单独标注已删除，避免重叠。**已正确处理**。

**权威依据**：K8 §1.7 BIS；K8 §1.4 BM

---

### 问题 8：样本 3 — DUF 删除（知识审查，低）

**审查结论**：`DUF`（Domain of Unknown Function）是蛋白质结构域类别名，不是具体基因名，删除正确。**已正确处理**。

**权威依据**：K8 §1.2 GENE（需为具体基因名）

---

## 总结与改进建议

**必须修改（2 项）**：
1. 样本 1：修正 LOI(SCAR_3456624, Pc39) 的 tail 锚点为 @136:140
2. 样本 6：删除 USE(sorghum, marker assisted selection)（CROP 不能作为 USE 的 head）

**建议修改（2 项）**：
3. 样本 5：`average proline` → `proline`（@105:112），同步修改 2 条 HAS 关系锚点
4. 样本 7：`transcriptome` → `transcriptome integration`（@277:301）

**确认保留（6 项）**：BSR 处理、DUF 删除、preflowering drought stress 整体标注、多 QTL 共享 CHR 实体、KNAT7 整体边界、phenotypic diversity 标为 TRT
