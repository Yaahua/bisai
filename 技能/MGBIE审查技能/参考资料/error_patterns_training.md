# MGBIE 分类错误模式收集与训练上下文

> 本文件基于当前已完成批次的训练数据分类与审查实践持续归纳更新，记录典型错误模式及相应的正确做法。
> 每次完成新一批数据块的分类后，应将新发现的错误模式追加到本文件中，持续积累上下文能力。

---

## 一、关键发现：原始训练数据中的非标准关系模式

原始训练数据中存在大量"非标准"关系模式（即不符合标注指南中关系约束定义的模式）。这些模式**不一定是错误**，而是标注者有意为之的扩展用法。在分类时必须尊重原始数据的标注模式，不要过度纠正。

### 1.1 高频非标准关系模式（必须保留）

| 模式 | 频次 | 说明 | 处理策略 |
|------|------|------|------|
| `LOI: (QTL, TRT)` | 30 | QTL 定位于某性状（实际含义：QTL 与性状关联） | **保留**，这是原始数据最常见的非标准模式 |
| `HAS: (CROP, TRT)` | 24 | 作物具有某性状（指南要求 head 为 VAR） | **保留**，原始数据中 CROP 和 VAR 在 HAS 关系中可互换 |
| `AFF: (ABS, GENE)` | 18 | 胁迫影响基因（指南要求 tail 为 TRT） | **保留**，原始数据中 AFF 的 tail 可以是 GENE |
| `LOI: (GENE, TRT)` | 10 | 基因定位于性状 | **保留**，原始数据的扩展用法 |

### 1.2 教训：不要将这些模式"修正"为标准模式

**错误做法**：将 `LOI: (QTL, TRT)` 改为 `AFF: (QTL, TRT)`
**正确做法**：保留原始的 `LOI: (QTL, TRT)`，因为模型需要学习这些模式

---

## 二、实体分类典型错误

### 2.1 复合实体拆分过度

**错误模式**：将 "drought resistance" 拆分为 ABS("drought") + TRT("resistance")
**正确做法**：依据 [TaeC-2024] 最大共识原则，"drought resistance" 作为一个整体标注为 TRT

> 判断标准：如果复合词在育种领域是一个固定搭配（如 drought resistance, salt tolerance, powdery mildew resistance），应作为整体标注为 TRT，不拆分。

**类似案例**：
- "cold tolerance" → TRT（整体）
- "salt stress tolerance" → TRT（整体）
- "grain yield" → TRT（整体）

### 2.2 实体边界包含描述词

**错误模式**：
- `"marker OPA 12(383)"` → MRK（"marker" 是描述词）
- `"Gene Si1g06530"` → GENE（"Gene" 是描述词）
- `"chromosome 2H"` → CHR（"chromosome" 是描述词）
- `"related QTL"` → QTL（"related" 是修饰词）

**正确做法**：
- `"OPA 12(383)"` → MRK
- `"Si1g06530"` → GENE
- `"2H"` → CHR
- `"QTL"` → QTL

> 但注意例外：如果 "chromosome 3" 在原始训练数据中被标注为 CHR，则保留。要尊重原始数据的标注模式。

### 2.3 GENE vs TRT 混淆

**错误模式**：将蛋白质名称标注为 TRT
- `"G protein gamma-subunit"` → TRT（错误，蛋白质不是性状）

**正确做法**：蛋白质是基因的产物，不应标注为 TRT。如果蛋白质名称与基因名称相同，标注为 GENE。

### 2.4 VAR vs CROSS vs CROP 混淆

**错误模式**：
- 将 "RILs"（重组自交系）标注为 VAR → 应为 CROSS
- 将 "BC lines"（回交系）标注为 VAR → 应为 BM（育种材料/方法）
- 将 "sweet sorghum" 标注为 VAR → 应为 CROP
- 将 "eight sorghum lines" 标注为 VAR → 可保留为 VAR

**判断标准**：
- 具体品种名称（如 "晋谷21"、"Morex"）→ VAR
- 杂交后代群体（如 "F1 hybrids"、"RILs"、"DH lines"）→ CROSS
- 物种或亚种名称（如 "foxtail millet"、"sweet sorghum"）→ CROP

### 2.5 CHR 的数量描述 vs 具体编号

**错误模式**：将 "18 chromosomes" 标注为 CHR
**正确做法**：
- "18 chromosomes"（染色体数量描述）→ TRT（核型性状）
- "chromosome 3"（具体染色体编号）→ CHR
- "Chr1"（具体编号）→ CHR

### 2.6 ABS vs BIS 混淆

**错误模式**：将 "H2O2"（过氧化氢）标注为 TRT
**正确做法**：H2O2 在胁迫语境中是非生物胁迫因子 → ABS

**判断标准**：
- 环境因素（drought, salt, cold, heat, H2O2）→ ABS
- 病虫害（powdery mildew, aphid, E. graminis, crown rust）→ BIS

### 2.7 BM 的边界判断

**错误模式**：将 "ddRAD-seq" 标注为 BM
**正确做法**：ddRAD-seq 是分子生物学技术手段，不是育种方法。应不标注或标注为 MRK 相关技术。

**BM 的正确范围**：
- 宏观育种方法：hybridization, marker-assisted selection, GWAS, backcross breeding
- 不是 BM：ddRAD-seq, PCR, gel electrophoresis（这些是实验技术）

### 2.8 来源性描述不等于稳定材料实体

**错误模式**：将 "Israeli accession"、"local accession"、"wild accession" 等仅表示来源或群体归属的短语直接标为 VAR。

**正确做法**：只有在短语同时包含稳定品种名、材料编号或可复核专名时，才保留为 VAR；若只是来源性说明，应建议删除该实体或视为普通文本，不强行实体化。

> 判断标准：`accession` 必须能够被唯一指认。像 "CAV 1979" 这类带稳定编号的材料可保留；仅有地域或泛化来源描述时默认不标为 VAR。

### 2.9 材料分组词不可过度提升为作物整体性状

**错误模式**：看到 `salt-sensitive accessions`、`salt-tolerant accessions` 就直接审成 `HAS(CROP, TRT)` 的合理关系，把材料分组误当成作物整体固有性状。

**正确做法**：审查时先判断性状究竟修饰的是作物整体，还是某一批材料/群体。若原文真正修饰的是 accession 或 material group，则应指出该 `CROP -> TRT` 关系属于过度提升。

> 可以接受 `stress -> trait` 的 `AFF`，但不能因为句中同时出现作物名，就自动把该性状视为作物整体属性。

### 2.10 重复作物名的单复数竞争边界

**错误模式**：同一句或前后句同时出现 `soybean` / `soybeans` 时，在同一偏移保留两个竞争性实体，或借用前一句的偏移去支撑后一句关系。

**正确做法**：审查时必须确认每个实体都绑定到原文中的真实 occurrence；若前后句分别出现单复数形式，应分别按真实位置建实体，禁止在同一偏移制造单复数双实体。

> 若发现错误实体，还要继续检查所有依赖它的 `HAS/AFF/CON` 等关系是否也需要同步改写。

---

## 三、关系分类典型错误

### 3.1 AFF 关系方向颠倒

**错误模式**：`(TRT, AFF, QTL)` — 性状影响QTL
**正确做法**：`(QTL, AFF, TRT)` — QTL影响性状

> AFF 关系的 head 必须是影响发起方（ABS/GENE/MRK/QTL），tail 必须是被影响的性状（TRT）

### 3.2 同义词误用 CON

**错误模式**：`CON(foxtail millet, Setaria italica)` — 将拉丁学名和通用名建立包含关系
**正确做法**：不建立关系。拉丁学名和通用名是同义词，不是包含关系。

### 3.3 LOI vs AFF 混淆

**错误模式**：`AFF(LW7 marker, rf4)` — 标记影响基因
**正确做法**：`LOI(LW7 marker, rf4)` — 标记定位于/关联基因

> 分子标记用于识别或筛选携带某基因的个体，是定位关系（LOI），不是影响关系（AFF）

### 3.4 MRK→BM 的 USE 关系

**错误模式**：`USE(MRK, BM)` — 标记采用育种方法
**正确做法**：USE 关系的 head 必须是 VAR，tail 必须是 BM

### 3.5 重复 mention 的关系锚点借位

**错误模式**：同一基因、作物或胁迫词在一句中多次出现时，把后文真正承担关系语义的 mention 错绑到前文第一次出现的位置。

**正确做法**：审查时要核对关系是否绑定到**真实承担语义的那一次出现**。若 head/tail 指向的是后文 mention，就不能沿用前文偏移；审查建议中要明确指出需要同步更新全部 anchor 字段。

> 典型风险包括：后文因果分句借用前文基因位置、后一句单数作物名借用前一句复数作物名偏移。

### 3.6 并列实体漏标常与并列关系漏标联动

**错误模式**：并列结构中只发现一部分 `TRT` 实体问题，或指出实体缺失却没有连带指出与同一 `GENE/ABS/MRK/QTL` 相连的成组关系也缺失。

**正确做法**：审查并列结构时，要按“实体组 + 关系组”成对检查。例如发现 `superoxide dismutase`、`peroxidase`、`catalase activities` 漏标后，也应同步指出对应的三条 `AFF` 关系漏标。

---

## 四、边界修复经验

### 4.1 并行处理导致的边界偏移

在并行子任务中，LLM 经常重新计算 start/end 位置时出错，导致大量边界偏移。

**修复策略**：
1. 在原文中搜索实体文本的所有出现位置
2. 选择最接近原始 start 位置的匹配
3. 同步更新关系中的 head_start/head_end/tail_start/tail_end

### 4.2 幻觉实体

LLM 在修正过程中可能生成原文中不存在的实体文本。

**修复策略**：
1. 验证 text[start:end] == entity['text']
2. 如果实体文本在原文中找不到，移除该实体
3. 同步移除引用该实体的关系

### 4.3 数据丢失恢复

当修正后的样本实体数比原始少3个以上时，应回退到原始标注。

### 4.4 审查前必须先核对输入物

在进入正式审查前，必须确认当前块至少具备以下输入物：
1. `chunk_XXX.json`
2. `chunk_XXX_review.md`

**错误模式**：缺少初标说明文档时直接进入审查，导致无法对照初标理由与后续修订链路。

**正确做法**：若 `chunk_XXX_review.md` 缺失，先补齐当前块说明，再输出 `chunk_XXX_audit.md`。

### 4.5 问题清单先于审查报告

**错误模式**：直接写审查报告，容易只记录显性问题，遗漏潜在问题和联动问题。

**正确做法**：先为当前块生成 `chunk_XXX_issue_inventory.md`，至少列出：
1. 已确认问题
2. 潜在问题
3. 关联问题 / 需要同步检查的字段

> 特别要检查：边界联动、关系方向联动、并列实体遗漏、括号编号实体遗漏、删除实体后的关系残留。

### 4.6 启动与恢复的单块锁定

**错误模式**：审查阶段提前展开多个块，或任务恢复时预读后续块，导致标准漂移与记录错位。

**正确做法**：
1. 审查开始时先锁定处理区间与 current chunk
2. 任一时刻只允许打开一个 current chunk
3. 当前块 `audit.md` 未完成前，不得打开下一块
4. 恢复时只重读当前块 JSON、review、audit、issue inventory 与错误模式库

### 4.7 作用域与批次边界防呆

**错误模式**：在用户只要求审查或整理 `chunk_011 ~ chunk_020` 时，未经确认就把注意力扩展到 `chunk_001 ~ chunk_010` 的历史清单、历史审查或额外上传事项。

**正确做法**：
1. 启动时先把用户指定区间写入本地工作记录
2. 所有审查补齐、问题清单重建和仓库同步都只能覆盖该区间
3. 若发现前序批次也有缺口，只登记为候选事项，不自动执行
4. 任何跨批次扩展都必须先得到用户明确确认

---

## 五、错误收集日志

> 以下为每批处理后追加的具体错误案例。格式：`[批次] 样本ID | 错误类型 | 错误内容 | 正确做法 | 依据`

### 批次1：chunk_001 ~ chunk_010（100条）

| 样本 | 错误类型 | 错误内容 | 正确做法 | 依据 |
|------|------|------|------|------|
| chunk_001 #3 | 拆分过度 | "powdery mildew resistance genes" 拆为 TRT+GENE | 可保留嵌套标注：TRT("powdery mildew resistance") + GENE("powdery mildew resistance genes") | [TaeC-2024] |
| chunk_001 #5 | 标签错误 | "sweet sorghum" 标为 VAR | 应为 CROP | [GB 4404.1] |
| chunk_002 #1 | 标签错误 | "RILs" 标为 VAR | 应为 CROSS | [SUN-2019] |
| chunk_002 #4 | 标签错误 | "H2O2" 标为 TRT | 应为 ABS | 通用生物学常识 |
| chunk_003 #9 | 同义词误用 | CON(foxtail millet, Setaria italica) | 不建立关系，是同义词 | [breeding_knowledge_base] |
| chunk_004 #2 | 边界错误 | "18 chromosomes" 标为 CHR | 应为 TRT（核型性状） | [LU-Sorghum-2006] |
| chunk_006 #3 | 标签错误 | "DEGs" 标为 GENE | DEGs 是差异表达基因集合，不是具体基因 | [CGSNL-2011] |
| chunk_007 #5 | 边界错误 | "marker OPA 12(383)" 含描述词 | 应为 "OPA 12(383)" | 词块审查标准 |
| chunk_007 #10 | 拆分 | "SbWRKY50 gene (Sb09g005700)" 整体标为 GENE | 应拆分为 "SbWRKY50" + "Sb09g005700" 两个 GENE | [CGSNL-2011] |
| chunk_008 #3 | 标签错误 | "779 bp band" 标为 MRK | 应移除，bp band 是实验现象 | 通用生物学常识 |
| chunk_008 #5 | 关系错误 | AFF(LW7 marker, rf4) | 应为 LOI(LW7 marker, rf4) | 标记定位关系 |
| chunk_009 #7 | 拆分过度 | "drought" + "resistance" 分开标 | 应合并为 "drought resistance" → TRT | [TaeC-2024] |
| chunk_009 #8 | 标签错误 | "BC lines" 标为 VAR | 应为 BM（回交系是育种材料） | [SUN-2019] |
| chunk_010 #2 | 标签错误 | "G protein gamma-subunit" 标为 TRT | 应移除，蛋白质不是性状 | [SUN-2019] |
| chunk_010 #1 | 边界错误 | "chromosome 2H" 标为 CHR | 应为 "2H" | [QTL-Nomen] |

### 批次2：chunk_011 ~ chunk_020（流程与技术教训）

| 样本 | 错误类型 | 错误内容 | 正确做法 | 依据 |
|------|------|------|------|------|
| chunk_011~020 | 业务范围错误 | 未经确认就尝试把前 10 块错误清单也纳入同步修订范围 | 严格以用户指定区间为边界；超范围事项只登记、不自动执行 | 本批次执行复盘 |
| chunk_011~020 | 流程错误 | 审查前未先核对初标说明文档是否齐备，导致个别块需要后补 review 文件 | 进入审查前先检查 `chunk_XXX_review.md`，缺失则先补齐 | 本批次执行复盘 |
| chunk_011~020 | 流程错误 | 曾出现跨块预读倾向，破坏单块锁定 | 审查阶段任一时刻只处理一个 current chunk | 本批次执行复盘 |
| chunk_011~020 | 技术错误 | 直接输出 audit 容易遗漏潜在问题与联动问题 | 先生成 `chunk_XXX_issue_inventory.md` 再输出 audit | 本批次执行复盘 |
| chunk_011 #6 | 技术错误 | 两条 `AFF` 关系把后文真正起效的 `SbMYBHv33` 错绑到前文第一次出现的位置 | 在 issue inventory 与 audit 中明确指出真实 occurrence，并要求同步修改全部 anchor 字段 | `chunk_011_issue_inventory.md` |
| chunk_012 #5 | 语义错误 | 将 `salt-sensitive`、`salt-tolerant` 这类 accession 分组词直接上挂到 `foxtail millet` | 审查时应指出这是材料分组被过度提升为作物整体性状 | `chunk_012_issue_inventory.md` |
| chunk_012 #6 | 技术错误 | 并列酶活性实体漏标，连带遗漏 3 条 `FtNAC31 -> TRT` 的 `AFF` 关系 | 审查并列结构时，实体缺失与关系缺失要成组指出 | `chunk_012_issue_inventory.md` |
| chunk_013 #4 | 语义错误 | 将 `Israeli accession` 这类来源性描述误当成稳定 `VAR` | 仅在具备可复核专名或编号时才建议保留为 `VAR` | `chunk_013_issue_inventory.md` |
| chunk_013 #5 | 技术错误 | 同偏移保留 `soybean` 与 `soybeans` 竞争实体，并让 `HAS` 借错单数锚点 | 在审查意见中同时指出竞争边界与关系重锚定要求 | `chunk_013_issue_inventory.md` |
| chunk_011~020 | 技术错误 | 关系修订时容易漏查并列实体、括号编号实体与残留锚点 | 将这些项目纳入 issue inventory 的关联问题栏目逐项核查 | 本批次执行复盘 |
| chunk_011~020 | 启动防呆 | 任务恢复时若不锁定 current chunk，审查记录容易错位 | 恢复时只重读当前块 JSON、review、audit、issue inventory | 本批次执行复盘 |

---

## 六、持续更新指引

每完成一批新的数据块分类后，请按以下步骤更新本文件：

1. 在"五、错误收集日志"中追加新批次的错误案例表格
2. 如果发现新的错误模式，在对应的"二/三/四"章节中补充
3. 如果发现需要修正的已有规则（如原始数据的新模式），更新"一"章节
4. 如果本批次暴露出新的流程错误、技术错误或启动防呆需求，也应写入第四章与第五章
5. 每10个批次后，回顾并精简重复内容
