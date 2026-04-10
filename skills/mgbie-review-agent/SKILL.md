---
name: mgbie-review-agent
description: AI 辅助杂粮育种信息抽取对抗性审查技能。用于在 mgbie-ner-annotator 完成初步分类后，对每个数据块进行拆分审查、语义审查、词块审查和知识审查，并输出审查文档以供主要技能进行全量修正。核心要求：审查必须有理有据，引用权威文件作为依据。
---

# MGBIE Review Agent

本技能提供对抗性审查工作流，用于审查和纠正 `mgbie-ner-annotator` 生成的初步分类结果。

## 执行模式

**必须使用单线程顺序处理**，严禁使用并行处理（map/parallel）。原因：
1. 审查需要跨数据块积累上下文，并行处理会导致审查标准不一致
2. 后续数据块的审查应参考前面数据块中已发现的错误模式
3. 单线程可确保审查文档的质量和一致性

**正确做法**：逐块顺序审查，每块审查完成后保存审查文档，再审查下一块。

## 核心工作流

### 步骤一：准备

1. 读取 `references/error_patterns_training.md`，了解已知的典型错误模式
2. 读取 `references/authoritative_references.md`，准备权威引用
3. 读取 `references/breeding_knowledge_base.md`，准备领域知识

### 步骤二：逐块四维审查

对每个数据块，读取初步 JSON 和对应的 review.md，执行以下四维审查：

#### 2.1 拆分审查

检查长复合词是否被错误地作为一个整体实体。

**关键经验**：
- "drought resistance" 等固定搭配**不应拆分**，整体标为 TRT
- "SbWRKY50 gene (Sb09g005700)" **应拆分**为两个 GENE 实体
- 判断标准：该复合词在育种领域是否为固定搭配

| 应拆分 | 不应拆分 |
|------|------|
| "基因名 gene (编号)" → 两个 GENE | "drought resistance" → 一个 TRT |
| "作物名 品种名" → CROP + VAR | "salt tolerance" → 一个 TRT |
| "胁迫 resistance gene" → BIS/ABS + TRT + GENE | "grain yield" → 一个 TRT |

#### 2.2 语义审查

检查关系方向和逻辑是否合理。

**关键经验**：
- AFF 方向：head 必须是影响发起方（ABS/GENE/MRK/QTL），tail 必须是 TRT
- 标记与基因的关系是 LOI（定位），不是 AFF（影响）
- 同义词（如拉丁学名与通用名）不应建立 CON 关系

**注意**：原始训练数据中存在非标准关系模式（如 `LOI: (QTL, TRT)` 出现30次），审查时**不要将这些标记为错误**。详见 `references/error_patterns_training.md` 第一章。

#### 2.3 词块审查

检查实体边界是否包含多余的修饰词。

**关键经验**：
- "marker X" → 去掉 "marker"，仅保留 "X"
- "Gene Si1g06530" → 去掉 "Gene"，仅保留 "Si1g06530"
- "chromosome 2H" → 去掉 "chromosome"，仅保留 "2H"
- "related QTL" → 去掉 "related"，仅保留 "QTL"

#### 2.4 知识审查

利用领域知识核对分类准确性。

**关键经验**：
- 蛋白质名称不是性状（TRT），不应标注或标为 GENE
- "18 chromosomes"（数量描述）是核型性状（TRT），不是 CHR
- "ddRAD-seq" 是实验技术，不是育种方法（BM）
- "779 bp band" 是实验现象，不是分子标记（MRK）
- "RILs"、"DH lines" 是杂交后代群体（CROSS），不是品种（VAR）
- "BC lines" 是育种材料/方法（BM），不是品种（VAR）
- "DEGs" 是差异表达基因集合，不是具体基因（GENE）

### 步骤三：输出审查文档

使用 `templates/audit_template.md` 模板，输出 `chunk_XXX_audit.md`，包含：
- 审查概况表（各维度问题数）
- 每个问题的详细描述：错误位置、错误类型、原分类、修改建议、权威依据
- 总结与改进建议

### 步骤四：更新错误模式文件

如果审查中发现了 `error_patterns_training.md` 中未记录的新错误模式，追加到该文件中。

## 资源文件说明

| 文件 | 说明 | 何时读取 |
|------|------|------|
| `references/authoritative_references.md` | 国标/行标/专著/论文引用库 | 审查前必读 |
| `references/breeding_knowledge_base.md` | 育种领域专业术语与命名规则 | 审查前必读 |
| `references/error_patterns_training.md` | 典型错误模式与正确做法 | 审查前必读 |
| `templates/audit_template.md` | 审查文档模板 | 输出时使用 |

## 执行准则

- **单线程顺序处理**：严禁并行，逐块审查并积累上下文。
- **挑剔与严谨**：采取对抗性思维，不放过任何可疑分类。
- **有理有据**：所有修改建议必须标注权威引用来源。
- **不直接修改数据**：仅输出审查文档，数据修正由 `mgbie-ner-annotator` 完成。
- **尊重原始模式**：不要将训练数据中的高频非标准关系模式标记为错误。
- **持续学习**：发现新错误模式时追加到 `error_patterns_training.md`。
