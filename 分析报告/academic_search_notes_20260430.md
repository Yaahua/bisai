# 学术广域检索笔记（2026-04-30）

## 已访问来源

1. Frontiers 综述：Named Entity Recognition and Relation Detection for Biomedical Information Extraction，DOI: 10.3389/fcell.2020.00673。该文综述 BioNER 与 BioRD 的流程，强调关系检测依赖实体识别质量，并将关系强度与极性、词距、依存路径、图网络整合等纳入分析。
2. PMC 综述页面尝试访问时出现 reCAPTCHA，未读取正文，暂不作为可直接引用正文来源。

## 初步可迁移点

- 生物医学关系抽取不是单纯关系分类问题，而是 NER、实体规范化、触发词、关系强度、极性和图结构整合的流水线。
- 当前 bisai 方案已经大量做关系后处理，但对实体边界、实体类型规范化、极性/否定、依存路径、图一致性约束的系统利用不足。
- 后续应检索 BioCreative/BioRED、LLM4IE、data-centric IE、weak supervision、ensemble pretrained language models 等方向，寻找可带来较大增益的策略。


## 追加访问记录

3. Oxford Database 的 BioCreative VIII/BioRED data-centric ensemble 论文页面尝试打开，但正文未被提取；后续将改用检索结果、摘要页、arXiv/PMC 镜像或 DOI 元数据补充。
4. PubMed 摘要页访问时出现 reCAPTCHA，未读取正文，不作为直接引用正文来源。后续应优先使用开放全文、arXiv、ACM/ACL Anthology 或 Semantic Scholar/Crossref API 元数据。

## 当前检索方向调整

由于 NCBI/PubMed/PMC 页面可能触发验证，下一步优先使用 Frontiers、ACL Anthology、arXiv、Springer Open、Oxford 页面摘要和 GitHub 论文列表。重点追踪 BioRED、BioREx、directionality、LLM4IE、data-centric IE、weak supervision、preprocessing-robust ensemble 等关键词。

## arXiv 论文关键摘录与迁移判断

5. **Enhancing Biomedical Relation Extraction with Directionality**（arXiv:2501.14079）：该文指出 BioRED 原始标注缺少实体角色方向性，而方向性对于生物关系网络至关重要；作者补充了 **10,864 条 directionality annotations**，并提出多任务语言模型，用软提示同时识别关系、novel findings 与实体角色；摘要声称该方法在两个 benchmark 上优于 GPT-4 和 Llama-3。对 bisai 的迁移意义是：当前 v44/v45 发现方向错误路径有效，不应只做删除，而要建立完整的“方向角色判别器”和方向混淆矩阵。
6. **BioREx: Improving Biomedical Relation Extraction by Leveraging Heterogeneous Datasets**（arXiv:2306.11189）：该文提出系统化处理异构 RE 数据集并合并为大数据集的 data-centric 方法，在 BioRED 上将 F1 从 **74.4% 提升到 79.6%**。对 bisai 的迁移意义是：若目标是“大量提分”，仅靠 A 榜后处理空间有限，应把官方训练集扩展为异构伪训练/迁移训练集，至少做 schema 对齐、关系同义映射、hard prompt/soft prompt 样例扩充。

## 工具与负结果证据

7. **LLMs are not Zero-Shot Reasoners for Biomedical Information Extraction**（ACL Anthology, 2025）：摘要显示，该研究在医疗分类与 NER 上比较标准提示、CoT、自一致性和 RAG，发现 **标准提示反而稳定优于更复杂的 CoT/self-consistency/RAG**。对 bisai 的直接启示是：LLM 不能作为主提交直接生成器，更适合作为“争议样本审阅器、规则生成器、候选解释器”，最终提交仍需通过频次、方向、实体类型和训练分布约束。
8. **ncbi/BioREx GitHub 工具**：README 显示 BioREx 支持下载预训练模型并对带注释的 PubTator 输入预测新数据，且 BioLinkBERT 版本为推荐模型、被 PubTator3 beta 使用。限制是其关系类型偏 BioRED/PubTator schema，不能直接等价提交天池格式；但可作为外部弱标注器或对疾病/化合物/基因类关系的二级裁判。

## 阶段性结论

广域检索开始改变原计划：若目标是大幅提分，应从“只改提交文件”升级为三层系统，即外部弱监督候选生成、方向角色判别、保守提交融合。LLM 提示工程只能放在低权重辅助层，不能替代结构化验证。

## LLM-IE 与 QA/实体标记方向

9. **LLM-IE: a python package for biomedical generative IE**（JAMIA Open, 2025）：论文明确提供 NER、实体属性抽取、关系抽取、数据管理与可视化的完整生命周期 API。其关键工程建议是，在关系抽取阶段对 frame pairs 使用 `possible_relation_types_func` 预过滤，避免让 LLM 判断明显不可能的实体对；Sentence Frame Extractor 在 NER 上显著提升召回，Review Extractor 提升召回，但 RE 的 multi-class extractor 出现高召回低精度（recall 0.978、precision 0.3831）的典型问题。这与 bisai 历史规律一致：LLM/多分类器适合召回候选，不适合直接提交。
10. **Biomedical Relation Extraction with Entity Type Markers and Relation-specific Question Answering**（BioNLP 2023）：摘要指出 QA 型关系抽取在多个实体对共享实体时容易抽错目标关系，作者通过关系特定 question template 与 entity type markers 改进 DrugProt 关系抽取。对 bisai 的迁移意义是：三元组方向和中间实体类型应显式写入候选判别模板，例如把 `GENE-LOI-MRK` 改写为“哪个 marker/SNP 与哪个 gene 的 LOI 关系被文本直接支持？”而不是让模型自由生成关系。

## 对大跃进计划的修正方向

原计划的“只做极小步减法”仍适合作为提交纪律，但不足以实现大幅提分。新计划应加入一个离线高召回层：用 LLM-IE/QA/实体标记/外部 BioREx 生成候选，再通过 v44 底座、训练频次、方向矩阵、样本簇和人工复核严格筛选，最后仍以极小差异提交。
