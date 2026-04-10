# 脚本工具库

本目录存放用于数据分析、评分模拟、图表生成的各类 Python 脚本。这些脚本不直接参与 A 榜预测，而是用于辅助决策和策略制定。

## 核心脚本说明

### 1. 数据分析与规律提取
- `analyze_data.py`：基础数据分析脚本，用于统计实体和关系的数量。
- `deep_analysis.py`：深度分析脚本，用于挖掘官方训练集中的共现模式和特殊规律。
- `extract_official_patterns.py`：官方规律提取脚本，自动生成用于 Prompt 的统计数据和 Few-shot 样本。

### 2. 评分与诊断
- `official_score.py`：官方评分模拟脚本，使用比赛官方的 Precision/Recall/F1 计算公式，用于本地自评。
- `analyze_prediction.py`：预测结果诊断脚本，对比预测结果与训练集期望分布，找出过标和漏标的具体模式。

### 3. 可视化图表生成
- `plot_scores.py`：生成自评得分的可视化图表（总体得分、各类别得分、TP/FP/FN 分布）。
- `plot_official_patterns.py`：生成官方标注规律的可视化图表（实体分布、关系分布、评分权重分解）。
- `plot_competition.py`：生成不同策略下的分数预测区间图。
- `plot_tracka_prediction.py`：生成 Track-A 竞争力预测对比图。

> **注意**：所有图表生成脚本均使用 `matplotlib` 和 `seaborn`，生成的图片保存在 `分析报告/` 目录下。
