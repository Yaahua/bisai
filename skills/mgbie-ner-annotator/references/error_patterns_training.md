# MGBIE 分类错误模式收集与训练上下文

> 本文件从前10块（100条）训练数据的分类实践中提炼而成，记录了典型错误模式和正确做法。
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

---

## 六、持续更新指引

每完成一批新的数据块分类后，请按以下步骤更新本文件：

1. 在"五、错误收集日志"中追加新批次的错误案例表格
2. 如果发现新的错误模式，在对应的"二/三/四"章节中补充
3. 如果发现需要修正的已有规则（如原始数据的新模式），更新"一"章节
4. 每10个批次后，回顾并精简重复内容
