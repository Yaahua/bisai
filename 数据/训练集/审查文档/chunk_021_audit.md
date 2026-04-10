# chunk_021 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_021.json + chunk_021_annotated.md + chunk_021_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 1 | 0 | 0 | 1 |
| 语义审查 | 2 | 0 | 1 | 1 |
| 词块审查 | 4 | 1 | 1 | 2 |
| 知识审查 | 3 | 0 | 2 | 1 |
| **合计** | **10** | **1** | **4** | **5** |

---

## 详细审查结果

### 问题 1：样本 3 — 偏移核实（词块审查，高）

**错误位置**：样本 3，`elevated temperatures` @290:311

**问题描述**：原文为 `"Tol tolerated elevated temperatures (ABS) due to..."` 其中 `(ABS)` 是标注说明文字，不是原始文本的一部分。需要确认原始 chunk_021.json 中样本 3 的文本是否包含 `(ABS)` 这个括号内容，以及 `elevated temperatures` 的真实偏移。

**修改建议**：
- 若原文不含 `(ABS)` 括号，则 `elevated temperatures` 的偏移应重新计算。
- 若原文含括号，则偏移 @290:311 正确。

**权威依据**：K1 §1.1（偏移必须与原文精确匹配）

**联动风险**：无关系依赖该实体，偏移修正不影响关系列表。

---

### 问题 2：样本 1 — `five major QTLs` 边界（词块审查，中）

**错误位置**：样本 1，`five major QTLs`（@166:181）标为 QTL

**问题描述**：`five major QTLs` 包含数量修饰词 "five major"，不是具体 QTL 名称。按 K1 §1.2（修饰词边界规则），应删除该实体，或缩减为 `QTLs`（@181:185）。但 "QTLs" 是泛指，也不是具体 QTL 名称，建议删除。

**修改建议**：删除 `five major QTLs` 实体。

**权威依据**：K1 §1.2（修饰词不应包含在实体边界内）；K8 §1.6 QTL（需为具体 QTL 名称）

**联动风险**：无关系依赖该实体，删除不影响关系列表。

---

### 问题 3：样本 0 — `Transcriptome` 标签（知识审查，中）

**错误位置**：样本 0，`Transcriptome`（@0:13）标为 BM

**问题描述**：原文为 "Transcriptome data before and after drought stress..."，`Transcriptome data` 是数据类型，不是分析方法。BM 应为具体的育种/分析方法（如 GWAS、WGCNA），而非数据类型名词。

**修改建议**：删除 `Transcriptome` 实体，或扩展为 `Transcriptome data`（@0:20）并改标为 BM（如果认为转录组数据分析是一种分析方法）。考虑到训练数据中有 "transcriptome analysis" 标为 BM 的先例，建议保留但扩展边界为 `Transcriptome data`（@0:20）。

**权威依据**：K8 §1.4 BM（育种方法/分析方法）；K6 文献语料库（transcriptome analysis 标注示例）

**联动风险**：无关系依赖该实体，修改不影响关系列表。

---

### 问题 4：样本 9 — HAS 关系主体（语义审查，中）

**错误位置**：样本 9，HAS(BTx623, Plant height/Brix/100-grain weight/flowering time)

**问题描述**：原文说的是 "Plant height, Brix, 100-grain weight, and flowering time were evaluated over 3 years"，这些性状是在 RIL 群体中评估的，并非 BTx623 专属性状。BTx623 是亲本之一，不是性状的直接拥有者。

**修改建议**：将 HAS 关系的 head 改为 `recombinant inbred line (RIL) population`（CROSS），而非 `BTx623`（VAR）。或者删除 HAS 关系，仅保留 CON 关系。

**权威依据**：K2 §1.1（HAS 关系：head 为 CROP/VAR/CROSS，tail 为 TRT，表示该材料具有该性状）；K8 §2.1 HAS

**联动风险**：若修改 head，需同步修改 4 条 HAS 关系的 head_start/head_end/head_type。

---

### 问题 5：样本 5 — `a candidate gene-based association analysis` 边界（词块审查，低）

**错误位置**：样本 5，`a candidate gene-based association analysis`（@43:86）

**问题描述**：边界包含冠词 "a"，按 K1 §1.2 应去掉冠词，从 @45 开始。但考虑到训练数据中有保留冠词的先例，且影响较小，建议修正。

**修改建议**：修改为 `candidate gene-based association analysis`（@45:86）。

**权威依据**：K1 §1.2（冠词不应包含在实体边界内）

**联动风险**：无关系依赖该实体，修改不影响关系列表。

---

### 问题 6：样本 7 — 嵌套实体合法性（拆分审查，低）

**错误位置**：样本 7，`Striga`（@60:66）BIS 与 `Striga tolerance`（@60:76）TRT 嵌套

**问题描述**：两个实体共享起始偏移 @60，形成嵌套。K1 §1.5 允许嵌套标注（如 "powdery mildew resistance" 中嵌套 "powdery mildew"），此处 Striga（病害）与 Striga tolerance（抗性性状）的嵌套符合规范。

**审查结论**：**确认保留**，嵌套合法。

**权威依据**：K1 §1.5（嵌套实体规则）；error_patterns §2.1（复合实体不应拆分）

---

### 问题 7：样本 4 — `Tibetan wild barley` 标签（知识审查，低）

**审查结论**：`Tibetan wild barley` 是具有可复核地理来源专名的大麦生态型，标为 VAR 合理。**确认保留**。

**权威依据**：error_patterns §2.8（具有稳定专名的材料保留为 VAR）

---

### 问题 8：样本 6 — `F-9:10 sorghum RILs` 边界（词块审查，低）

**审查结论**：`F-9:10 sorghum RILs` 标为 CROSS，边界包含作物名 "sorghum"，但训练数据中有类似先例，且删除作物名会导致 "F-9:10 RILs" 语义不完整。**确认保留**。

**权威依据**：error_patterns §2.4（杂交后代群体标为 CROSS）

---

## 总结与改进建议

**必须修改（1 项）**：
1. 样本 3：核实 `elevated temperatures` 偏移，确认原文是否包含 `(ABS)` 括号

**建议修改（4 项）**：
2. 样本 1：删除 `five major QTLs` 实体（泛指，非具体 QTL 名称）
3. 样本 0：扩展 `Transcriptome` → `Transcriptome data`（@0:20）
4. 样本 9：将 HAS 关系 head 改为 RIL 群体（CROSS）
5. 样本 5：修正冠词边界 @43 → @45

**确认保留（5 项）**：嵌套实体、Tibetan wild barley、F-9:10 sorghum RILs 边界、QTL LOI BIS 关系、genetic regions 标为 QTL
