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

### 启动前固定动作（用于"一键开机"）

0. **加载共享知识库（每次启动必须执行）**
   - 执行以下命令同步最新知识库：
     ```bash
     cd /home/ubuntu/bisai_clone && git pull origin main
     ```
   - 若目录不存在，先克隆：
     ```bash
     gh repo clone Yaahua/bisai /home/ubuntu/bisai_clone
     ```
   - 按以下顺序读取知识库文件（**必须全部读完再开始审查**）：
     1. `知识库/K8_dataset_taxonomy.md` — 12类实体+6类关系完整分类学体系（最高优先级）
     2. `知识库/K1_entity_boundary_rules.md` — 实体边界判定规则
     3. `知识库/K2_relation_direction_rules.md` — 关系方向判定规则
     4. `知识库/K7_confusing_cases.md` — 易混淆案例库
     5. `知识库/K4_nomenclature_guidelines.md` — 基因/QTL/标记命名规范
     6. `知识库/K3_crop_terminology_glossary.md` — 生僻术语词表
     7. `知识库/K5_standard_excerpts.md` — 国标条文摘录（需要引用依据时查阅）
     8. `知识库/K6_literature_corpus.md` — 文献语料库（需要 Few-shot 示例时查阅）
   - **知识库路径**：`/home/ubuntu/bisai_clone/知识库/`
   - **GitHub 仓库**：https://github.com/Yaahua/bisai（`知识库/` 子目录）

1. **确认输入物齐备**
   - 本技能启动前，必须已经存在：当前块 `chunk_XXX.json` 与对应的 `chunk_XXX_review.md`。
   - 如果当前块缺少初标说明文档，不得跳过核对逻辑；应先补齐该块说明，再进入审查。

2. **锁定本次处理范围与当前块**
   - 明确审查区间（如 `chunk_011` ~ `chunk_020`）。
   - 若用户仅要求某一批次，不得自行扩展到其他历史批次；发现其他批次也有缺口时，只能登记为候选事项，需单独确认后再处理。
   - 任一时刻只允许审查**一个 current chunk**；当前块 `audit.md` 未完成前，不得打开下一块。

3. **准备统一依据**
   - 读取 `references/error_patterns_training.md`，了解已知的典型错误模式。
   - 读取 `references/authoritative_references.md`，准备权威引用。
   - 读取 `references/breeding_knowledge_base.md`，准备领域知识。

4. **中断恢复协议**
   - 若任务从中途恢复，先重读：当前 `chunk_XXX.json`、对应 `chunk_XXX_review.md`、已生成的 `chunk_XXX_audit.md` / `chunk_XXX_issue_inventory.md`（若存在）以及 `references/error_patterns_training.md`。
   - 恢复时只处理当前块，不得顺手预读后续块。

### 步骤一：准备

1. 读取 `references/error_patterns_training.md`，了解已知的典型错误模式
2. 读取 `references/authoritative_references.md`，准备权威引用
3. 读取 `references/breeding_knowledge_base.md`，准备领域知识
4. 检查当前块的 `chunk_XXX_review.md` 是否存在；不存在则先补齐，再进入四维审查

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

### 步骤三：先生成问题清单，再输出审查文档

1. 先为当前块生成 `chunk_XXX_issue_inventory.md`，至少包含三类内容：
   - `已确认问题`
   - `潜在问题`
   - `关联问题/需要同步检查的字段`
2. 在问题清单基础上，使用 `templates/audit_template.md` 模板输出 `chunk_XXX_audit.md`，包含：
   - 审查概况表（各维度问题数）
   - 每个问题的详细描述：错误位置、错误类型、原分类、修改建议、权威依据
   - 与主问题相关的边界、并列实体、方向性关系、同句遗漏关系等联动风险
   - 总结与改进建议

### 步骤四：更新错误模式文件

如果审查中发现了 `error_patterns_training.md` 中未记录的新错误模式、新流程失误或新的技术性漏检点，追加到该文件中。

## 资源文件说明

### 共享知识库（最高优先级，每次启动必须加载）

| 文件 | 说明 | 何时读取 |
|------|------|------|
| `bisai_clone/知识库/K8_dataset_taxonomy.md` | 12类实体+6类关系分类学体系（含官方定义+论文证据+真实数据统计） | **启动时必读** |
| `bisai_clone/知识库/K1_entity_boundary_rules.md` | 实体边界判定规则（最大共识原则、各类实体边界细则） | **启动时必读** |
| `bisai_clone/知识库/K2_relation_direction_rules.md` | 关系方向判定规则（因果逻辑、头尾实体类型约束） | **启动时必读** |
| `bisai_clone/知识库/K7_confusing_cases.md` | 易混淆案例库（边界案例、方向混淆、分类混淆的标准判定） | **启动时必读** |
| `bisai_clone/知识库/K4_nomenclature_guidelines.md` | 基因/QTL/分子标记命名规范（CGSNL、IONC 等国际标准） | 遇到命名问题时查阅 |
| `bisai_clone/知识库/K3_crop_terminology_glossary.md` | 杂粮作物生僻术语词表 | 遇到生僻术语时查阅 |
| `bisai_clone/知识库/K5_standard_excerpts.md` | 国家/行业标准关键条文摘录（NY/T 2425、NY/T 2355、NY/T 2645） | 需要引用权威依据时查阅 |
| `bisai_clone/知识库/K6_literature_corpus.md` | 文献语料库与标注示例（Few-shot 样本） | 需要参考示例时查阅 |

### 本地技能文件

| 文件 | 说明 | 何时读取 |
|------|------|------|
| `references/authoritative_references.md` | 国标/行标/专著/论文引用库（旧版，已被K5/K6取代，保留供参考） | 可选 |
| `references/breeding_knowledge_base.md` | 育种领域专业术语与命名规则（旧版，已被K3/K4取代，保留供参考） | 可选 |
| `references/error_patterns_training.md` | 典型错误模式与正确做法 | 审查前必读 |
| `templates/audit_template.md` | 审查文档模板 | 输出时使用 |

## 执行准则

- **单线程顺序处理**：严禁并行，逐块审查并积累上下文。
- **当前块锁定**：任何时刻只允许审查一个 current chunk；当前块 `audit.md` 未完成前不得打开下一块。
- **范围锁定**：未经用户明确确认，不得把当前批次的审查补齐、同步或上传任务扩展到其他批次。
- **先核对输入物，再开始审查**：缺少 `chunk_XXX_review.md` 时，先补齐说明文档，不得跳审或带缺口审查。
- **问题清单先行**：先列出已确认问题、潜在问题和关联问题，再写正式审查文档。
- **挑剔与严谨**：采取对抗性思维，不放过任何可疑分类。
- **有理有据**：所有修改建议必须标注权威引用来源。
- **不直接修改数据**：仅输出审查文档，数据修正由 `mgbie-ner-annotator` 完成。
- **尊重原始模式**：不要将训练数据中的高频非标准关系模式标记为错误。
- **持续学习**：发现新错误模式、新流程失误或新的技术性漏检点时追加到 `error_patterns_training.md`。
