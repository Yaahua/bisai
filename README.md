# CCL2026-MGBIE 杂粮育种信息抽取比赛

本仓库是针对 [天池 CCL2026-MGBIE 杂粮育种信息抽取比赛](https://tianchi.aliyun.com/competition/entrance/532465) 的完整解决方案，专注于 **Track-A（不微调赛道）**。

## 核心策略：拟合官方偏好

经过深度数据分析，我们发现官方标注数据存在特定的偏好（例如 LOI 关系大量用于 QTL→TRT，而 AFF 关系主要用于 ABS→TRT）。
因此，本方案放弃了"学术纠错"的思路，转而采用**"严格拟合官方标注偏好"**的策略，通过 In-Context Learning（Few-shot）让大模型直接预测 A 榜测试集。

## 目录结构

- `数据/A榜/`：存放最终可提交的预测结果（`submit_v2.zip` 为最新优化版）。
- `提示词库/`：存放比赛级 Prompt 模板、Few-shot 样本、后处理脚本和预测脚本。
- `分析报告/`：存放关于赛道选择、数据偏差、官方规律提取的深度分析报告及可视化图表。
- `脚本工具/`：存放用于数据分析、评分模拟、图表生成的各类 Python 脚本。
- `知识库/`：存放领域相关的实体边界规则、关系方向规则等（可作为 Prompt 优化的参考）。

## 快速开始（预测 A 榜）

1. 确保已安装 `openai` 库并配置好 `OPENAI_API_KEY`。
2. 运行 v2 优化版预测脚本（内置多线程、断点续传、非法关系过滤）：
   ```bash
   python3 提示词库/predict_track_a_v2.py
   ```
3. 预测完成后，结果将保存在 `数据/A榜/submit_v2.json`。
4. 运行格式验证脚本：
   ```bash
   python3 提示词库/validate_submission.py 数据/A榜/submit_v2.json
   ```
5. 打包提交：
   ```bash
   cd 数据/A榜 && zip -j submit_v2.zip submit_v2.json
   ```

## 版本更新记录

- **v2 优化版**：新增 LOI vs AFF 明确区分规则，替换覆盖漏标模式的 Few-shot 样本，内置后处理过滤 153 种合法三元组之外的所有非法关系。
- **v1 基础版**：基于官方 5 条基础 Few-shot 样本，实现 0 边界错误的稳定预测。
