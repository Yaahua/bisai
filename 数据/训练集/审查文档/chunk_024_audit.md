# chunk_024 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_024.json + chunk_024_annotated.md + chunk_024_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 0 | 0 | 0 | 0 |
| 语义审查 | 2 | 1 | 0 | 1 |
| 词块审查 | 2 | 1 | 1 | 0 |
| 知识审查 | 4 | 0 | 3 | 1 |
| **合计** | **8** | **2** | **4** | **2** |

---

## 详细审查结果

### 问题 1：样本 2 — `sheepgrass` 与 `water stress tolerance` 偏移重叠（语义审查，高）

**错误位置**：样本 2，`sheepgrass`（@174:184）与 `water stress tolerance`（@183:205）

**问题描述**：两实体在 @183:184 处重叠 1 个字符。原文为 "Little is known about sheepgrass water stress tolerance"，`sheepgrass` 结束于 @184，`water stress tolerance` 起始于 @183，存在 1 字符重叠，违反 K1 §1.3（实体不得重叠，嵌套除外）。

**修改建议**：修正 `water stress tolerance` 的 start 为 @185（"water stress tolerance" 在 "sheepgrass " 之后，空格后起始）。验证：原文 "sheepgrass water stress tolerance"，sheepgrass @174:184，空格 @184:185，water @185:190。修正为 `water stress tolerance`（@185:207）。

**权威依据**：K1 §1.3（实体边界不得重叠）；error_patterns §2.4（偏移精度）

**联动风险**：需同步修改 HAS(Sheepgrass, water stress tolerance) 的 tail_start=185、tail_end=207。

---

### 问题 2：样本 0 — `SNPs` 与 `10 K SNPs` 冗余嵌套（词块审查，中）

**错误位置**：样本 0，`10 K SNPs`（@115:124）与 `SNPs`（@121:125）

**问题描述**：`SNPs`（@121:125）被包含在 `10 K SNPs`（@115:124）内，形成冗余嵌套。两者都标为 MRK，内层 `SNPs` 是冗余的。

**修改建议**：删除内层 `SNPs`（@121:125），保留 `10 K SNPs`（@115:124）。同步将关系 LOI(SNPs @121:125, chromosome 5/8) 改为 LOI(10 K SNPs @115:124, chromosome 5/8)。

**权威依据**：K1 §1.3（同类型嵌套时保留外层）；error_patterns §2.4

**联动风险**：需同步修改 2 条 LOI 关系的 head_start=115、head_end=124。

---

### 问题 3：样本 5 — `C2H2-type zinc finger protein transcription factor` 标签（知识审查，中）

**错误位置**：样本 5，`C2H2-type zinc finger protein transcription factor`（@13:62）GENE

**问题描述**：这是转录因子家族名称，不是具体基因名称。K8 §1.2 规定 GENE 需为具体基因名。但训练集中存在转录因子家族名标为 GENE 的先例（error_patterns §2.3 注释）。

**修改建议**：建议保留，但标注为 GENE 时需注意这是家族级别标注。若训练集中无明确先例，应删除。

**权威依据**：K8 §1.2 GENE；error_patterns §2.3

---

### 问题 4：样本 7 — `PS I`、`PS II`、`cytochrome b6f complex` 标签（知识审查，中）

**错误位置**：样本 7，`PS I`（@265:269）、`PS II`（@271:276）、`cytochrome b6f complex`（@278:300）均改为 GENE

**问题描述**：光系统 I/II 和细胞色素 b6f 复合体是蛋白质复合体，不是单一基因。K8 §1.2 规定 GENE 需为具体基因名。但在光合作用研究语境中，这些复合体常被视为基因产物集合。

**修改建议**：建议改为不标，或保留为 GENE（接受家族/复合体级别标注）。以训练集一致性为准。

**权威依据**：K8 §1.2 GENE；error_patterns §2.3

---

### 问题 5：样本 9 — `tolerance to drought stress` 嵌套（语义审查，低）

**审查结论**：`tolerance to drought stress`（@76:101 TRT）包含 `drought stress`（@87:101 ABS），嵌套合理（性状包含胁迫因子）。**确认保留**。

**权威依据**：K1 §1.3（允许嵌套）

---

### 问题 6：样本 1 — `quartet micronuclei frequency` 标签（知识审查，低）

**审查结论**：微核频率是可量化的细胞学指标，训练集中存在类似标注，标为 TRT 合理。**确认保留**。

---

## 总结与改进建议

**必须修改（2 项）**：
1. 样本 2：修正 `water stress tolerance` 起始偏移（@183→@185），同步修改 HAS 关系锚点
2. 样本 0：删除冗余 `SNPs`（@121:125），同步修改 2 条 LOI 关系 head 锚点为 @115:124

**建议修改（4 项）**：
3. 样本 5：确认 `C2H2-type zinc finger protein transcription factor` 是否有训练集先例，若无则删除
4. 样本 7：`PS I`、`PS II`、`cytochrome b6f complex` 改为不标（蛋白质复合体非具体基因名）

**确认保留（2 项）**：`tolerance to drought stress` 嵌套、`quartet micronuclei frequency` TRT
