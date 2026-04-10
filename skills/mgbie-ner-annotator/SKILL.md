---
name: mgbie-ner-annotator
description: AI 辅助杂粮育种信息抽取与分类技能。用于处理 CCL 2026 MGBIE 比赛数据，包含数据分块（每块10条）、逐块进行命名实体识别（NER）与关系抽取（RE）、撰写分类说明阐释分类理由，并最终输出符合比赛要求的 JSON 格式数据及过程文件。核心要求：分类必须有理有据，引用权威文件作为依据，并支持接入审查反馈进行全量修正。
---

# MGBIE NER Annotator

本技能提供 AI 辅助工作流，用于 CCL 2026 MGBIE 比赛的数据分类与标注任务。与 `mgbie-review-agent` 配合形成"分类→审查→全量修正"闭环。

## 执行模式

**必须使用单线程顺序处理**，严禁使用并行处理（map/parallel）。原因：
1. 并行子任务无法共享上下文，导致前后数据块的分类标准不一致
2. 并行处理中 LLM 频繁产生实体边界偏移（start/end 计算错误）
3. 并行修正过程中容易产生幻觉实体（原文中不存在的文本）
4. 数据丢失难以追踪和恢复

**正确做法**：逐块顺序处理，每处理完一块后立即验证边界正确性，再处理下一块。

## 核心工作流

### 阶段一：初步分类与说明撰写

1. **数据读取与分块**
   - 使用 `scripts/chunk_data.py` 将数据拆分为每块 10 条。
   - 创建工作目录：`chunks/`, `verified/`, `reviews/`。

2. **逐块顺序分类**
   - 逐块处理，每块完成后**立即验证** `text[start:end] == entity['text']`。
   - 分类依据：`references/annotation_guidelines.md` + `references/error_patterns_training.md`。
   - **在分类前必须阅读 `error_patterns_training.md`**，了解已知的典型错误模式和正确做法。

3. **撰写分类说明**
   - 每块输出一份 `chunk_XXX_review.md`，引用权威文件阐释分类理由。
   - 使用 `templates/review_template.md` 模板。

### 阶段二：对抗性审查（由 mgbie-review-agent 执行）

- 每完成 10 个数据块后，唤起 `mgbie-review-agent` 进行四维审查。
- 审查技能输出审查文档，供阶段三使用。

### 阶段三：全量修正与最终输出

1. **逐块顺序修正**（严禁并行）
   - 读取审查文档，逐块修正。
   - 修正后**立即验证边界**，确保 0 边界错误。
   - 若修正后实体数比原始少 3 个以上，回退到原始标注。

2. **更新错误收集文件**
   - 将本批次发现的新错误模式追加到 `references/error_patterns_training.md`。

3. **格式化输出**
   - 运行 `scripts/format_checker.py` 验证格式。
   - 合并所有数据块，生成最终 `submit.json`。

## 关键分类规则（从实践中提炼）

### 实体分类要点

| 易错场景 | 错误做法 | 正确做法 | 依据 |
|------|------|------|------|
| 复合性状词 | 拆分 "drought resistance" 为 ABS+TRT | 整体标注为 TRT | [TaeC-2024] |
| 实体含描述词 | "marker OPA12" 整体标为 MRK | 仅 "OPA12" 标为 MRK | 词块审查标准 |
| 染色体数量 | "18 chromosomes" 标为 CHR | 标为 TRT（核型性状） | [LU-Sorghum-2006] |
| 蛋白质名称 | 标为 TRT | 不标注或标为 GENE | [SUN-2019] |
| 杂交后代群体 | "RILs" 标为 VAR | 标为 CROSS | [SUN-2019] |
| 物种亚种名 | "sweet sorghum" 标为 VAR | 标为 CROP | [GB 4404.1] |
| 实验技术 | "ddRAD-seq" 标为 BM | 不标注（非育种方法） | [NY/T 2467-2025] |
| 实验现象 | "779 bp band" 标为 MRK | 不标注（非分子标记） | 生物学常识 |

### 关系分类要点

| 易错场景 | 错误做法 | 正确做法 | 依据 |
|------|------|------|------|
| AFF 方向 | (TRT, AFF, QTL) | (QTL, AFF, TRT) | AFF head 必须是影响发起方 |
| 同义词 | CON(foxtail millet, Setaria italica) | 不建立关系 | 拉丁学名=同义词 |
| 标记与基因 | AFF(marker, gene) | LOI(marker, gene) | 标记定位关系 |

### 尊重原始训练数据的非标准模式

原始数据中存在高频非标准关系模式，**不要过度纠正**：
- `LOI: (QTL, TRT)` — 30次，保留
- `HAS: (CROP, TRT)` — 24次，保留
- `AFF: (ABS, GENE)` — 18次，保留

详见 `references/error_patterns_training.md` 第一章。

## 资源文件说明

| 文件 | 说明 | 何时读取 |
|------|------|------|
| `references/annotation_guidelines.md` | 12类实体+6类关系定义 | 分类前必读 |
| `references/error_patterns_training.md` | 典型错误模式与正确做法 | 分类前必读，修正后追加 |
| `scripts/chunk_data.py` | 数据分块脚本 | 阶段一 |
| `scripts/format_checker.py` | 格式验证脚本 | 阶段三 |
| `templates/review_template.md` | 分类说明模板 | 阶段一 |

## 执行准则

- **单线程顺序处理**：严禁并行，逐块处理并即时验证。
- **边界即时验证**：每块处理完后立即检查 `text[start:end] == entity['text']`。
- **准确性优先**：宁可留空也不错分。
- **有理有据**：引用权威文件（国标、行标、教材、论文）。
- **持续学习**：每批处理后更新 `error_patterns_training.md`。
- **尊重原始模式**：不过度纠正训练数据中的非标准关系模式。
