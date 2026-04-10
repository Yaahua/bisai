# 对抗性审查文档 (Audit Report)

**数据块编号**: chunk_002
**审查时间**: 2026-04-10 10:00:00

## 1. 审查概况

- **总条数**: 10
- **发现错误/遗漏条数**: 5
- **主要错误类型分布**: 知识审查错误 3 处, 词块审查错误 2 处, 语义审查错误 1 处, 拆分审查错误 1 处

## 2. 详细审查意见与权威依据

### 问题 1: 知识审查错误 (实体分类错误)

- **错误位置**: Sample 1, Entity 7
- **原分类结果**: "H2O2" (TRT)
- **修改建议**: 将 "H2O2" 归类为非生物胁迫指标 (ABS) 或代谢物，而非性状 (TRT)。在当前分类体系下，ABS 更为合适，因为它代表了氧化胁迫状态。
- **权威依据**: 依据 **[通用生物学常识]**，H2O2 (过氧化氢) 是一种活性氧 (ROS)，是细胞氧化应激水平的直接指标，属于非生物胁迫的范畴。

### 问题 2: 词块审查错误 (实体边界不准确)

- **错误位置**: Sample 1, Entity 8
- **原分类结果**: "O2 center"
- **修改建议**: 实体文本应与原文完全匹配，应为 "O2 center dot-"。
- **权威依据**: 依据 **[TaeC-2024]** 的标注原则，实体边界必须精确，不能遗漏字符。

### 问题 3: 语义审查错误 (关系方向错误)

- **错误位置**: Sample 6, Relations 1, 2, 3
- **原分类结果**: (drought, SiLRR-RLK) -> AFF, (salinity, SiLRR-RLK) -> AFF, (pathogen infection, SiLRR-RLK) -> AFF
- **修改建议**: 关系方向应为基因影响其对胁迫的响应，即 (SiLRR-RLK, drought) -> AFF, (SiLRR-RLK, salinity) -> AFF, (SiLRR-RLK, pathogen infection) -> AFF。
- **权威依据**: 依据 **[breeding_knowledge_base.md]**，AFF 关系通常指基因/QTL影响性状或胁迫响应，因此 head 应为基因。

### 问题 4: 词块审查错误 (实体边界包含修饰词)

- **错误位置**: Sample 7, Entity 3
- **原分类结果**: "abnormal pollen tube subapical growth" (TRT)
- **修改建议**: 去除修饰词 "abnormal"，将实体标注为 "pollen tube subapical growth"。
- **权威依据**: 依据 **[词块审查标准]**，实体不应包含 "abnormal" 等主观或程度修饰词。

### 问题 5: 拆分审查错误 (复合实体未拆分)

- **错误位置**: Sample 8, Entity 6
- **原分类结果**: "spring oat germplasm" (CROP)
- **修改建议**: 拆分为 "spring oat" (VAR) 和 "germplasm" (TRT)。
- **权威依据**: 依据 **[拆分审查标准]** 和 **[GB 4404.1]**，"spring oat" 是一个具体的品种类型，而 "germplasm" (种质) 是育种材料，应分别标注。

### 问题 6: 知识审查错误 (实体分类错误)

- **错误位置**: Sample 8, Entity 4
- **原分类结果**: "agronomic" (TRT)
- **修改建议**: "agronomic" 是一个形容词，应与后面的 "traits" 结合，将 "agronomic traits" 整体标注为 TRT。
- **权威依据**: 依据 **[NY/T 2645-2014]**，农艺性状是一个完整的概念，单独的形容词 "agronomic" 无法构成一个性状实体。

### 问题 7: 知识审查错误 (实体分类错误)

- **错误位置**: Sample 10, Entity 1
- **原分类结果**: "Drought stress" (TRT)
- **修改建议**: "Drought stress" 应被分类为非生物胁迫 (ABS)。
- **权威依据**: 依据 **[breeding_knowledge_base.md]**，"Drought" (干旱) 及其相关表述属于典型的非生物胁迫 (ABS)。

## 3. 审查总结与后续建议

本次审查共发现 7 处问题，涉及全部四种审查类型。主要问题集中在知识应用和实体边界划分上，例如将胁迫错误地分类为性状、未能精确匹配原文以及未能拆分复合实体。建议 `mgbie-ner-annotator` 技能在后续处理中：
1.  加强对胁迫类型 (ABS/BIS) 与性状 (TRT) 的区分，特别是当文本中出现 "stress" 字样时。
2.  严格执行实体边界匹配，确保标注文本与原文完全一致。
3.  对包含作物名和材料类型的复合词进行审慎拆分。
