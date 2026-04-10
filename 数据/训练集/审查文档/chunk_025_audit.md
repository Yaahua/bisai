# chunk_025 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_025.json + chunk_025_annotated.md + chunk_025_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 3 | 2 | 1 | 0 |
| 词块审查 | 1 | 0 | 1 | 0 |
| 知识审查 | 3 | 0 | 3 | 0 |
| **合计** | **7** | **2** | **5** | **0** |

---

## 详细审查结果

### 问题 1：样本 3 — USE 关系主体类型错误（语义审查，高）

**错误位置**：样本 3，USE(QTL-seq analysis @2:18 BM, F2 population @116:129 CROSS)

**问题描述**：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，head 必须是 VAR，tail 必须是 BM。此处 head 为 BM（QTL-seq analysis），tail 为 CROSS（F2 population），双重违反约束。

**修改建议**：删除该 USE 关系。若需表达"使用 F2 群体进行 QTL-seq 分析"，可考虑不建立关系（无合适关系类型）。

**权威依据**：K8 §2.6 USE（head: VAR, tail: BM）；K2 §2.1

**联动风险**：删除该关系不影响其他实体。

---

### 问题 2：样本 3 — CON(CROSS, CROSS) 类型错误（语义审查，高）

**错误位置**：样本 3，CON(F2 population @116:129 CROSS, crosses between... @143:244 CROSS)

**问题描述**：K8 §2.4 规定 CON 关系合法类型为 CON(CROP, VAR) 或 CON(GENE全称, GENE缩写)。CROSS→CROSS 不是合法的 CON 关系类型。

**修改建议**：删除该 CON 关系。

**权威依据**：K8 §2.4 CON（合法类型约束）；K2 §2.1

**联动风险**：删除该关系不影响其他实体。

---

### 问题 3：样本 3 — `transgressive segregation of DTH toward late heading` 边界（词块审查，中）

**错误位置**：样本 3，`transgressive segregation of DTH toward late heading`（@270:322）TRT

**问题描述**：边界包含 "of DTH toward late heading" 修饰词，不是性状名称的核心部分。K1 §1.2 规定修饰词不应包含在实体边界内。

**修改建议**：缩减为 `transgressive segregation`（@270:294）TRT。同步修改 OCI 关系的 head_end=294。

**权威依据**：K1 §1.2（修饰词边界规则）；error_patterns §2.2

---

### 问题 4：样本 0 — `abscisic acid` 标为 ABS（知识审查，中）

**错误位置**：样本 0，`abscisic acid`（@107:120）ABS

**问题描述**：脱落酸（ABA）是植物激素，是信号分子，不是非生物胁迫因子。K8 §1.7 ABS 定义为非生物胁迫（drought、heat、cold、salinity 等），ABA 不符合。

**修改建议**：删除 `abscisic acid` ABS 标注。

**权威依据**：K8 §1.7 ABS；error_patterns §2.3（植物激素不标为 ABS）

---

### 问题 5：样本 2 — `ABA` 标为 ABS（知识审查，中）

**错误位置**：样本 2，`ABA`（@363:366）ABS

**问题描述**：同上，ABA 是植物激素，不是非生物胁迫因子。

**修改建议**：删除 `ABA` ABS 标注。

**权威依据**：K8 §1.7 ABS；error_patterns §2.3

---

### 问题 6：样本 9 — PSI/PSII 标签（知识审查，中）

**错误位置**：样本 9，`PSI`（@219:222）、`PSII`（@62:66、@265:269）改为 GENE

**问题描述**：光系统 I/II 是蛋白质复合体，不是单一基因。与 chunk_024 样本 7 的处理方式需保持一致。

**修改建议**：与 chunk_024 保持一致决策——若 chunk_024 中 PS I/II 改为不标，则此处也改为不标；若保留 GENE，则此处也保留。建议统一改为不标。

**权威依据**：K8 §1.2 GENE；error_patterns §2.3

---

## 总结与改进建议

**必须修改（2 项）**：
1. 样本 3：删除 USE(BM, CROSS)（关系类型约束违反）
2. 样本 3：删除 CON(CROSS, CROSS)（关系类型约束违反）

**建议修改（5 项）**：
3. 样本 3：缩减 `transgressive segregation of DTH toward late heading` → `transgressive segregation`
4. 样本 0：删除 `abscisic acid` ABS（植物激素非胁迫因子）
5. 样本 2：删除 `ABA` ABS（植物激素非胁迫因子）
6. 样本 9：PSI/PSII 改为不标（与 chunk_024 保持一致）
7. 样本 5：`glutathione S-transferase` 和 `MYB-bHLH-WD40 complex` 标为 GENE 需确认训练集先例
