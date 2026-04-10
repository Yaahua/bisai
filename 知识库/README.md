# MGBIE 杂粮育种信息抽取 — 知识库

本目录存放对 Track-A 预测**直接有用**的领域知识文档，精简保留三个核心文件。

## 保留文件说明

| 文件 | 行数 | 作用 |
|---|---|---|
| `K6_literature_corpus.md` | 458 行 | **最核心**。基于官方 `train.json` 真实数据整理的 Few-shot 标注示例，覆盖 12 类实体和 6 类关系，可直接用于优化 Prompt。 |
| `K7_confusing_cases.md` | 87 行 | 边界模糊案例库，收录易混淆的实体边界和关系方向判定，与官方标注偏好高度一致，对提升 NER 精度有直接帮助。 |
| `K8_dataset_taxonomy.md` | 72 行 | 12 类实体和 6 类关系的完整定义与典型示例，是理解任务的基础文档，可直接粘贴进 Prompt 的任务说明部分。 |

## 已删除文件

以下文件已被清理，原因是它们主要服务于已废弃的"AI 修正训练集"流程，对当前的 A 榜预测没有直接价值：

| 删除文件 | 删除原因 |
|---|---|
| `K1_entity_boundary_rules.md` | 基于学术标准，部分规则与官方标注偏好冲突，直接使用存在标准偏移风险。 |
| `K2_relation_direction_rules.md` | 关于 LOI 和 AFF 的判定与官方实际标注有出入，是导致之前数据偏移的根源之一。 |
| `K3_crop_terminology_glossary.md` | 大模型本身已掌握农业术语，冗余度高。 |
| `K4_nomenclature_guidelines.md` | 基因/QTL 命名规范，大模型本身已掌握，冗余度高。 |
| `K5_standard_excerpts.md` | 国家行业标准摘录，主要用于"引经据典"修正训练集，已废弃。 |
| `K9_search_protocol.md` | 配套已删除的 `mgbie-review-agent` 技能的查询 SOP，已无意义。 |
