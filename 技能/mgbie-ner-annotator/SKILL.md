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
   - 按以下顺序读取知识库文件（**必须全部读完再开始分类**）：
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

1. **先固化切分规则，再停止回读参考仓库**
   - 若任务要求“沿用既有训练集的切分方式”，只允许**一次性**读取参考仓库/目录。
   - 将观察到的目录结构、文件命名、编号位数、每块条数、JSON 字段结构记录到本地 `*_split_scheme_record.md`。
   - 记录完成后，后续切分与处理**只依据该记录执行**，不再回读参考仓库，避免来回比对造成漂移。

2. **建立固定工作目录**
   - 至少创建：`chunks_XX_YY/`, `reviews/`, `audits/`, `verified/`。
   - 使用 `scripts/chunk_data.py` 将目标 `train.json` 按“每块 10 条、三位编号”的既定方案拆分。

3. **锁定处理范围与当前块**
   - 明确本次仅处理哪个区间（如 `chunk_011` ~ `chunk_020`）。
   - 若用户仅要求某一批次，不得自行扩展到其他历史批次；发现其他批次也有缺口时，只能登记为候选事项，需单独确认后再处理。
   - 任一时刻只允许存在**一个 current chunk**；未完成当前块的 JSON、说明文档与校验，不得打开下一块。

4. **中断恢复协议**
   - 若任务中途恢复或上下文压缩，先重读：当前 `chunk_XXX.json`、对应 `chunk_XXX_review.md` / `chunk_XXX_audit.md` / `chunk_XXX_issue_inventory.md`（若存在）以及 `references/error_patterns_training.md`。
   - 恢复时**只恢复当前块**，不得顺手展开后续块。

### 阶段一：初步分类与说明撰写

1. **分类前准备**
   - 必读：`references/annotation_guidelines.md` + `references/error_patterns_training.md`。
   - 如任务要求沿用历史切分方式，先读取本地 `*_split_scheme_record.md`，不要再次读取来源仓库。

2. **逐块顺序分类**
   - 严格按 `chunk_001 → chunk_002 → ...` 的顺序处理；本任务类场景中，若指定为 `11–20`，则按 `chunk_011 → chunk_012 → ... → chunk_020` 顺序推进。
   - **禁止为了“提前了解全貌”预读后续 chunk**。当前块的 `review.md` 未完成前，不得打开下一块。
   - 每块处理完后立即做实体边界检查：`text[start:end] == entity['text']`。

3. **撰写分类说明**
   - 每块输出一份 `chunk_XXX_review.md`，引用权威文件阐释分类理由。
   - 使用 `templates/review_template.md` 模板。
   - 说明文档写完并保存后，当前块才算“初标完成”。

### 阶段二：对抗性审查（由 mgbie-review-agent 执行）

- 在整批初标完成后，再由 `mgbie-review-agent` 逐块执行四维审查。
- 审查阶段也必须保持单块顺序，不得跨块抢跑。
- 审查技能输出 `chunk_XXX_audit.md`，供阶段三使用。

### 阶段三：全量修正与最终输出

1. **逐块生成问题清单，再修正**（严禁并行）
   - 读取当前块 JSON 与对应审查文档，先生成 `chunk_XXX_issue_inventory.md`。
   - 问题清单必须至少包含三类：`已确认问题`、`潜在问题`、`关联字段/关联关系同步项`。
   - 只有在问题清单写完后，才允许编写修订脚本或直接回写 JSON。

2. **逐项完成当前块全量修正**
   - 修一个实体时，同时检查：同名实体、并列 mention、重叠 mention、引用该实体的全部关系、同一句中的方向性关系。
   - 修一条关系时，同时检查：head/tail 文本、head/tail 起止位置、对应实体是否仍存在、同句是否有遗漏的并列关系。
   - 若修正后实体数比原始少 3 个以上，回退到原始标注并重新审查该块。

3. **执行双重技术验证**
   - 先运行 `scripts/format_checker.py` 做结构校验。
   - 再执行确定性一致性校验，至少覆盖：
     1. `text[start:end] == entity['text']`
     2. `text[head_start:head_end] == head`
     3. `text[tail_start:tail_end] == tail`
     4. 关系引用的 head/tail 与当前实体边界保持同步
     5. 不存在指向已删除实体的关系
     6. 每个 chunk 仍保持 10 条样本，样本顺序不变
   - **仅通过格式校验并不代表可提交**；必须同时通过 span/anchor 一致性校验。

4. **更新错误收集文件并输出最终结果**
   - 将本批次发现的新错误模式、新流程教训和技术性防呆要求追加到 `references/error_patterns_training.md`。
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
| `references/annotation_guidelines.md` | 12类实体+6类关系定义（旧版，已被K8取代，保留供参考） | 可选 |
| `references/error_patterns_training.md` | 典型错误模式与正确做法 | 分类前必读，修正后追加 |
| `scripts/chunk_data.py` | 数据分块脚本 | 阶段一 |
| `scripts/format_checker.py` | 格式验证脚本 | 阶段三 |
| `templates/review_template.md` | 分类说明模板 | 阶段一 |

## 执行准则

- **单线程顺序处理**：严禁并行，逐块处理并即时验证。
- **当前块锁定**：任何时刻只允许处理一个 current chunk；当前块未完成 `JSON + review + validation` 前不得打开下一块。
- **范围锁定**：未经用户明确确认，不得把当前批次的补齐、同步或上传任务扩展到其他批次。
- **先记录切分规则，再离线执行**：需要沿用历史切分方式时，先做一次性记录，后续不再回读来源仓库。
- **问题清单先行**：全量修正前先列出“已确认问题、潜在问题、关联问题”，再逐项修复。
- **双重验证**：既做格式校验，也做实体/关系 span 与 anchor 一致性校验。
- **边界即时验证**：每块处理完后立即检查 `text[start:end] == entity['text']`。
- **准确性优先**：宁可留空也不错分。
- **有理有据**：引用权威文件（国标、行标、教材、论文）。
- **持续学习**：每批处理后更新 `error_patterns_training.md`。
- **尊重原始模式**：不过度纠正训练数据中的非标准关系模式。
