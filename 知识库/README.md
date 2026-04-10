# MGBIE 杂粮育种信息抽取 — 共享知识库

本仓库为 CCL 2026 MGBIE（Miscellaneous Grain Breeding Information Extraction）比赛的共享知识库，供 `mgbie-ner-annotator` 和 `mgbie-review-agent` 两个技能调用。

## 知识库结构

| 文件 | 内容 | 优先级 |
|---|---|---|
| `K1_entity_boundary_rules.md` | 实体边界判定规则（最大共识原则、各类实体边界细则） | ★★★★★ |
| `K2_relation_direction_rules.md` | 关系方向判定规则（因果逻辑、头尾实体类型约束） | ★★★★★ |
| `K3_crop_terminology_glossary.md` | 生僻术语词表（谷子、燕麦、高粱、荞麦专用术语） | ★★★★ |
| `K4_nomenclature_guidelines.md` | 基因/QTL/分子标记命名规范（CGSNL、IONC 等国际标准） | ★★★★ |
| `K5_standard_excerpts.md` | 国家/行业标准关键条文摘录（NY/T 2425、NY/T 2355、NY/T 2645） | ★★★★ |
| `K6_literature_corpus.md` | 文献语料库与标注示例（Few-shot 样本，含实体+关系标注） | ★★★★ |
| `K7_confusing_cases.md` | 易混淆案例库（边界案例、方向混淆、分类混淆的标准判定） | ★★★★★ |
| `K8_dataset_taxonomy.md` | 实体与关系分类学体系（基于官方标注说明+真实数据统计） | ★★★★★ |

## 使用方式

在执行标注或审查任务前，按以下顺序加载知识库：

1. 首先读取 `K8_dataset_taxonomy.md`（掌握完整的类别体系）
2. 然后读取 `K1_entity_boundary_rules.md` 和 `K2_relation_direction_rules.md`（掌握判定规则）
3. 遇到生僻术语时查阅 `K3_crop_terminology_glossary.md`
4. 遇到基因/QTL/标记命名问题时查阅 `K4_nomenclature_guidelines.md`
5. 需要引用权威依据时查阅 `K5_standard_excerpts.md`
6. 需要 Few-shot 示例时查阅 `K6_literature_corpus.md`
7. 遇到边界模糊案例时优先查阅 `K7_confusing_cases.md`

## 数据来源与引用

本知识库内容来源于以下权威文献和标准：

- **国际命名规范**：CGSNL (2008), Rice; Jellen et al. (2024), Crop & Pasture Science
- **国家行业标准**：NY/T 2425-2013, NY/T 2355-2013, NY/T 2645-2014
- **高引用综述**：Baloch et al. (2023), Front. Genetics; Yabe et al. (2020), Mol. Breeding
- **比赛官方数据**：CCL 2026 MGBIE train.json（1000条真实标注样本）
