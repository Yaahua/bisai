# 提示词库与预测脚本

本目录是 Track-A 预测的核心引擎，包含与大模型交互的 Prompt 模板、Few-shot 样本以及自动化预测和后处理脚本。

## 核心文件说明

### 1. Prompt 与样本
- `prompt_template.md`：比赛级系统提示词全文，包含任务定义、实体类型、关系类型及严格的约束规则。
- `official_patterns.md`：基于官方 1000 条训练数据提取的 10 条铁律约束（如 LOI 和 AFF 的真实分布）。
- `fewshot_samples.json`：从官方训练集中精选的 5 条高质量样本，覆盖全部 6 种关系类型。
- `fewshot_v2.json`：优化版样本，特别增加了易漏标的 `GENE-LOI-TRT` 和 `MRK-LOI-TRT` 模式。

### 2. 预测脚本
- `predict_track_a.py`：v1 基础预测脚本（单线程）。
- `predict_track_a_v2.py`：v2 优化版预测脚本（多线程并发、断点续传、内置非法关系过滤）。

### 3. 后处理与验证
- `post_process.py`：v3 后处理脚本，用于过滤训练集中不存在的 95 个非法三元组。
- `post_process_v4.py`：v4 精准后处理脚本，增加距离限制和关键词验证，砍掉 179 个高概率错误关系。
- `validate_submission.py`：提交前终检脚本，确保实体和关系的文本边界 100% 精确匹配原文。

## 预测工作流

1. **构建 Prompt**：脚本读取 `prompt_template.md`、`official_patterns.md` 和 `fewshot_samples.json`，组装成完整的系统提示词。
2. **批量预测**：多线程调用大模型 API 处理 `test_A.json`，模型仅输出实体文本和标签。
3. **边界计算**：脚本自动使用精确字符匹配（`str.find`）计算 start/end 偏移量，彻底消除大模型的计算幻觉。
4. **后处理过滤**：应用 `post_process_v4.py` 规则，删除明显不合理的过标关系。
5. **格式验证**：运行 `validate_submission.py` 确保零格式错误，最后打包为 `submit.zip`。
