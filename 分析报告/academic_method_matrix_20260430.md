# 学术检索可迁移方法矩阵

**目标**：把广域学术 API 与论文检索得到的方法，转化为当前 `bisai` 仓库可以执行的提分路线。本文不把论文方法机械照搬为提交，而是按“候选生成、候选判别、提交融合”三层重新组织。

| 方法簇 | 代表来源 | 论文/工具给出的关键信号 | 对当前比赛的迁移方式 | 预期收益类型 | 风险控制 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Data-centric 异构数据融合 | BioREx；BioRED；BioCreative VIII data-centric ensemble | BioREx 报告通过异构 RE 数据集合并将 BioRED F1 从 74.4% 提升到 79.6%；data-centric 系统强调 schema 对齐、数据清洗和集成 | 不立即重训大模型，先做“外部弱监督候选库”：把 BioREx/PubTator/训练集规则转成候选证据表，用于发现 v44 缺失或可疑关系 | 主要补召回，同时发现系统性漏项 | 必须经过天池 schema 映射、方向矩阵、样本人工复核；不能直接提交外部工具结果 |
| Directionality/实体角色方向性 | Enhancing Biomedical Relation Extraction with Directionality；v44/v45 已验证方向问题 | BioRED 原始关系缺方向角色会损害生物网络，方向性增强论文补充 10,864 条 directionality annotations 并用多任务模型识别关系和实体角色 | 把 `GENE-LOI-MRK`、`VAR-CON-CROSS`、`MRK-LOI-GENE` 等做成方向混淆矩阵；新增“方向交换候选”与“只删不换候选”成对提交 | 高精度纠错，可能同时减少 FP 和 FN | 每次只验证一个方向族；方向修正必须与删除版配对解释 |
| QA + Entity Type Markers | BioNLP 2023 Entity Type Markers and Relation-specific QA | 多实体共享时普通 QA 易抽错目标对；加入实体类型标记和关系特定问题可提升 DrugProt RE | 对每个候选三元组生成判别问题：明确 head/tail 类型、关系词、方向角色和文本证据，不让 LLM 自由生成 | 提升争议样本判别质量，尤其是方向与类型边界 | LLM 只输出证据标签，不直接改提交；需要 JSON schema 与可追溯理由 |
| LLM-IE Pipeline | JAMIA Open 2025 LLM-IE | 支持 NER/属性/RE/可视化；推荐 `possible_relation_types_func` 预过滤；Sentence Frame 召回高，Multi-class RE 高召回低精度 | 作为离线候选生成器和可视化审阅器；建立实体对预过滤函数，先排除不可能关系对，再用 LLM 或规则判别 | 扩大候选搜索空间，减少遗漏 | 严禁把高召回低精度 RE 直接提交；最终进入小步融合 |
| Noisy Label / Co-regularization | EMNLP 2021 Learning from Noisy Labels for Entity-Centric IE | 噪声标签更晚被记忆、更容易被遗忘；多模型一致性正则可减少过拟合噪声 | 不一定重训模型，可迁移为“历史提交遗忘/一致性评分”：只在高分版本反复出现且未被掉分版本新增的关系视为稳态 | 构造关系可靠度分层，辅助删假阳性 | 不能把 2/3 或 3/3 多模型一致当作充分条件；历史已有掉分证据 |
| Weak/Distant Supervision + Noise Filtering | Distant supervision；KB-refined weak supervision；negative learning/noisy student | 弱监督必须配合 KB/refined filtering/noise reduction，否则正负样本噪声很高 | 使用 STRING/PubTator/BioREx 只做外部证据特征，不做真值；把外部证据缺失但 v44 存在的低频边列入复核 | 对生物医学实体关系提供外部证据，辅助排序 | 天池作物育种 schema 与通用 biomedical schema 不完全一致，外部证据只能低权重 |
| Data-centric post-processing/ensemble | Data-centric RE、ensemble semantics、历史 v41/v44 | 高分常来自数据清洗、后处理和集成，而非单模型盲目增强 | 继续保留 v44 底座，生成 v46/v47 候选时使用“一假设一提交”；所有组合版必须由已涨分原子操作组成 | 稳定小涨分并避免回撤 | 不提交未验证组合；不再一锅端低频或大批量加法 |

## 核心判断

学术检索并没有推翻上一版“极小差异提交”的纪律，而是推翻了“只能做减法”的上限判断。真正适合第六名后的大幅提分策略应是 **离线大召回、线上小提交**：离线用外部工具、QA 模板、方向角色矩阵和弱监督证据尽可能发现候选；线上仍用 v44 底座做极小差异、可回滚、可归因提交。

## 可直接进入工程的三类产物

| 产物 | 内容 | 对应脚本/文件建议 |
| :--- | :--- | :--- |
| `candidate_evidence_table.csv` | 每条候选关系的来源、v44 是否已有、关系类型频次、方向置信、外部证据、LLM-QA 判别、人工状态 | 新建 `工具脚本/build_candidate_evidence_table.py` |
| `direction_confusion_matrix.md` | 官方训练集与 v44 中所有类型方向分布、反向类型、可疑样例 | 新建 `分析报告/direction_confusion_matrix_20260430.md` |
| `v46_atomic_candidates/` | 单方向、单类型、单样本簇、单外部证据候选的提交 json | 新建生成脚本，不覆盖 v45 |
