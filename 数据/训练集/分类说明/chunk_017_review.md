**数据块编号**: chunk_017
**处理时间**: 2026-04-10 00:00:00

## 1. 整体处理情况

本块共 10 条，已按“只处理当前一个 chunk”的要求完成初步标注与结构校验。整体处理上，我继续沿用前面块已经固定下来的策略：对命名材料、命名 QTL、明确性状与稳定胁迫词进行吸收；对过于泛化的家族词、研究背景词与不稳定推断关系进行收缩；对训练集中已存在的高频非标准关系模式，在不制造新歧义的前提下予以保留。

| 指标 | 数值 |
|------|------|
| 总条数 | 10 |
| 成功处理条数 | 10 |
| 包含保守留空处理的条数 | 5 |

## 2. 关键分类理由与权威依据

### 2.1 F2 群体明确归入 CROSS，父母本材料保留为 VAR

首条样本中的 `F-2 population` 明确表示杂交后代群体，因此根据技能文件“杂交后代群体优先标为 **CROSS**”的规则，直接归为 **CROSS**。`SA2313` 与 `Hiro-1` 属于具体品种/材料，分别保留为 **VAR**，并与 `grain sorghum`、`Sudan-grass` 建立 `CROP -> VAR` 的 **CON**，再由两个亲本材料与 `F-2 population` 建立 **CON**。这与技能中关于 `CROSS` 和 `VAR` 的区分完全一致，也与权威参考中对育种群体与亲本材料层次的定义一致。

### 2.2 一般 QTL 与命名 QTL 可并行保留

同一条样本后半句同时出现了泛称 `QTL` 与命名位点 `qGW1`。在这种情况下，本块没有删去泛称 `QTL`，而是将其与 `100-grain weight` 建立一般性 **LOI** 关系，并保留 `qGW1 -> 100-grain weight` 的更具体 **LOI**。之所以允许二者并存，是因为原文确实先报告“检测到七个 QTL”，后再强调一个命名 QTL；两层信息并不冲突，而是概括与实例的关系。

### 2.3 胁迫作用于基因表达时，沿用 `ABS -> GENE` 的训练集习惯

第二条样本 `Most PgB3 genes show upregulated expression under drought and high-temperature stresses` 明确表达了胁迫条件对基因表达的影响。因此本块将 `drought` 与 `high-temperature stresses` 归入 **ABS**，`PgB3` 归入 **GENE**，并建立 **AFF**。技能文件已明确指出，虽然 `AFF: (ABS, GENE)` 并非最严格的生物学本体关系，但在该任务现有训练集中是高频模式，因此不应擅自清洗掉。相较之下，`RAV` 只是亚家族泛称，不如 `PgRAV-04` 稳定，所以被移除，避免“家族名—成员名”混杂。

### 2.4 避免制造重叠噪声实体

第三条样本原始标注把 `drought` 同时作为 `drought-responsive genes` 的前缀片段和 `drought tolerance` 的前缀片段单独标出，这会产生无必要的重叠实体。为减少边界噪声，本块仅保留完整短语 `drought-responsive genes`、`drought tolerance` 与 `sorghum`，并用 `sorghum -> drought tolerance` 的 **HAS** 保留最核心的作物—目标性状信息。这样的简化符合词块审查所强调的“尽量用最小充分实体替代无增益的重叠标注”。

### 2.5 RIL 不再误判为 VAR

第四条样本中的 `recombinant inbred lines` 原先被标为 **VAR**。根据技能规则，这类群体应标为 **CROSS**，因此本块改正为 **CROSS**。同时保留 `QTLs` 与 `kernel area`、`kernel length`、`kernel width`、`groat percentage` 的 **LOI** 关系，反映原文中“QTLs for trait”这一训练集常用表达。`marker-assisted selection (MAS)` 以及 `RFLP`、`AFLP` 也予以保留，以维持原句中“以标记分析服务于辅助选择评估”的技术链条。

### 2.6 否定句中的 QTL 不与性状强建关系

第五条样本第一句为 `No QTL were detected for CGR`。由于这里是否定句，`QTL -> CGR` 关系并不存在，因此本块只保留 `QTL` 与 `CGR` 实体，不建立关系。相对地，后两句明确说 `QTL were found for P-R` 与 `QTL was found for E-G`，因此分别建立第二、第三处 `QTL` 与对应性状的 **LOI**。这样做体现了技能中“否定信息不得误转成正向关系”的基本原则。

### 2.7 仅保留可稳定落点的命名基因

第六条样本 `SiNP1 encodes a glucose-methanol-choline oxidoreductase` 中，最稳定的信息就是命名基因 `SiNP1`。至于蛋白功能说明与表达部位 `panicle`，一方面不在本任务实体体系中稳定对应，另一方面若强行扩展会引入额外解释负担，因此本块仅保留 `SiNP1`。这与技能中“蛋白名称和功能短语不要轻率扩展为实体”的要求一致。

### 2.8 群体定位不清时，不把 QTL 强连到染色体

第七条样本虽出现 `qPH1`、`qPH2`、`qPH3`、`qFSW1`、`qFSW2` 以及两组 `Chr 6`、`Chr 9`，但原文只说这些 QTL 集合“were detected on Chr 6 and Chr 9”，并未给出每个命名 QTL 与哪条染色体的一一映射。因此本块保守处理：保留所有 QTL、相关性状和染色体实体，但只建立 `QTL -> TRT` 的 **LOI**，不把每个命名 QTL 同时强连到两条染色体。这样可以避免制造伪定位关系。

### 2.9 品种耐盐描述不等于稳定的实体关系

第八条样本描述 `ST 47` 和 `SS 212` 在 Na+ 毒害相关生理反应上的差异。这里虽然可以识别出 `ST 47`、`SS 212` 与 `Na+ toxicity`，并补充 `biomass accumulation` 作为性状，但句子的主体是较复杂的比较与机制叙述，并不存在一个足够稳定、可直接落入现有六类关系标签的简单结构。因此本块仅保留实体，不新增关系，等待后续统一审查再判断是否需要补充。

### 2.10 病害与作物的影响关系保留，防控策略不强行关系化

第九条样本中，`Anthracnose` 是病害，`Colletotrichum sublineolum` 是病原对象，两者都归入 **BIS**。病害作用于 `sorghum` 与 `Sorghum bicolor` 的事实在句中较明确，因此保留 `BIS -> CROP` 的 **AFF**。但 `resistance genes` 仅出现在“最有效控制策略是导入抗性基因”的策略性表达中，并未给出具体基因或稳定目标对象，因此没有继续保留 `resistance genes -> Anthracnose` 的 **AFF**，以免把防治建议误当成确定因果关系。

### 2.11 DTF3A 兼具命名 QTL 与染色体定位信息

第十条样本原始标注缺少 `flowering time`、`major QTL` 与 `DTF3A`。本块补入这几个关键实体，并建立 `major QTL -> flowering time`、`DTF3A -> flowering time` 以及 `DTF3A -> chromosome three` 的 **LOI**。同时保留 `domesticated chickpea` 与 `wild progenitor Cicer reticulatum` 对 `growth habit` 和前文 `flowering time` 的 **HAS**。`FT genes` 虽保留为 **GENE**，但因句中只说明其在区间内存在并上调表达，尚不足以稳定绑定到现有关系类型，所以暂不扩展关系。

## 3. 审查反馈与全量修正记录 (仅在阶段三填写)

当前尚未进入统一审查阶段，本节留待后续四维审查完成后回填。

## 4. 其他备注

本块最值得在统一审查时重点复核的是第二条 `PgB3` 作为基因家族简称的吸收是否过宽，以及第四条 `MAS -> RFLP/AFLP` 的 **USE** 是否需要在尊重训练集风格与减少技术性噪声之间再平衡一次。若后续审查认为应进一步收缩，将按单块回修原则处理，不提前波及其他 chunk。
