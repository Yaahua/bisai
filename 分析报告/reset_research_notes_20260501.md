# 重新制定计划：检索与纠偏笔记

## 1. BioCreative/BioRED data-centric ensemble 论文

来源：Wilailack Meesawad 等，Database 2025，`Enhancing biomedical relation extraction through data-centric and preprocessing-robust ensemble learning approach`，DOI: 10.1093/database/baae127。页面摘要显示，该系统面向 BioCreative VIII BioRED 关系抽取任务，采用 PubTator API、多种 PubMedBERT 分类器、prompt questions、entity ID pairs、co-occurrence contexts、special tokens/boundary tags，以及 Max Rule ensemble。论文强调 **data-centric approach**、高质量数据实例、预处理鲁棒性和多分类器集成，而不是通过删除少数低频关系来提分。

对当前任务的纠偏意义：前两次提交都是“删除 v44 关系”并从 0.4514 降至 0.4167/0.4164，说明当前公开榜对这些关系的召回非常敏感，或者 v44 的高分来源主要是保留一批看似可疑但实际命中的关系。下一阶段不应继续删关系，而应回到 v44，做 **只增加、不删除** 或 **验证 zip/底座一致性**。

## 2. Leaderboard overfitting 资料

来源：Zheng Wenjie，`Toward a Better Understanding of Leaderboard`，arXiv:1510.03349。PDF 摘要与第一页可见内容指出，leaderboard 在机器学习竞赛中会诱导参赛者 overfit validation set；文章讨论如何避免过拟合、如何解释 leaderboard 精度，以及样本复杂度与 leaderboard 精度关系。

对当前任务的纠偏意义：前两次失败不能继续用大量提交“蒙方向”。应从批量候选文件改为 **一个核心假设、一个最小提交、提交前能解释其收益来源**。如果没有强证据，宁可不提交，保护 0.4514 底座。
