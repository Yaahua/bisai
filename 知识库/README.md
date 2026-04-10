# 知识库

## 当前状态：已清空

本目录已完成精简，所有文件均已删除。

### 删除原因

| 文件 | 删除原因 |
|---|---|
| `K6_literature_corpus.md` | 内容已转化为 `提示词库/fewshot_v3.json`（5 条精选 Few-shot 样本），原始 458 行文档不再需要 |
| `K7_confusing_cases.md` | 规则基于学术标准制定，与官方标注偏好存在偏差；核心规则已内嵌到 `prompt_template.md` 的 STRICT RULES 中 |
| `K8_dataset_taxonomy.md` | 实体与关系定义已完全内嵌到 `prompt_template.md` 的 System Prompt 中，且原文件的 LOI 定义与官方训练集实际分布不符（误导模型） |

### 真正有用的内容在哪里

- **实体/关系定义** → `提示词库/prompt_template.md`（System Prompt 第 1~13 行）
- **关键标注规则** → `提示词库/prompt_template.md`（STRICT RULES 8 条）
- **LOI vs AFF 区分** → `提示词库/prompt_template.md`（CRITICAL DISTINCTION 部分）
- **官方数据统计规律** → `提示词库/official_patterns.md`
- **Few-shot 示例** → `提示词库/fewshot_v3.json`（5 条，覆盖所有关键关系类型）
