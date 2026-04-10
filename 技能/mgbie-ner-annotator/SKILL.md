---
name: mgbie-track-a-predictor
description: MGBIE 比赛 Track-A（不微调赛道）专用预测技能。用于读取官方 test_A.json，利用大模型上下文能力（In-Context Learning）进行批量预测，并生成符合天池提交要求的 submit.json。核心要求：严格遵循官方标注规律，禁止 AI 自行纠错，确保实体边界和关系锚点 100% 准确。
---

# MGBIE Track-A Predictor

本技能提供专门针对 CCL 2026 MGBIE 比赛 Track-A（不微调赛道）的预测工作流。
**核心理念：官方数据就是 Ground Truth，一切以拟合官方标注偏好为唯一准绳，禁止任何形式的"学术纠错"。**

## 核心工作流

### 1. 启动前准备

- 确保已克隆官方数据集仓库到 `/home/ubuntu/official_mgbie/`
- 确保已克隆你的比赛仓库到 `/home/ubuntu/bisai_clone/`
- 确保已配置 `OPENAI_API_KEY` 环境变量（用于调用 `gpt-4.1-mini`）

### 2. 认知官方铁律（禁止违反）

在执行预测前，必须阅读并深刻理解 `references/official_patterns.md` 中的官方统计规律。
最关键的几条：
1. **LOI(QTL→TRT) 是合法的**：官方 31.4% 的 LOI 关系都是 QTL 定位到性状，**绝对不要把它改成 AFF**。
2. **32.7% 的样本无关系**：看不出明确关系时，relations 留空数组即可，不要强行脑补。
3. **AFF 的方向**：head 必须是影响发起方（ABS/GENE/MRK/QTL/BM/BIS），tail 通常是 TRT/GENE。
4. **实体边界极度严格**：`text[start:end]` 必须等于 `entity["text"]`，字符级别不能有偏差。

### 3. 执行批量预测

使用提供的 Python 脚本进行自动化批量预测。该脚本内置了比赛级 Prompt、Few-shot 示例、自动重试机制和边界校验逻辑。

```bash
# 运行预测脚本（耗时约 10-15 分钟，支持断点续传）
python3 /home/ubuntu/skills/mgbie-ner-annotator/scripts/predict_track_a.py \
  --test /home/ubuntu/official_mgbie/dataset/test_A.json \
  --output /home/ubuntu/bisai_clone/数据/A榜/submit.json
```

**脚本特性：**
- **Temperature=0**：确保输出的确定性。
- **自动校验**：每次大模型返回 JSON 后，脚本会自动校验实体边界和关系锚点。
- **自动重试**：如果校验失败或 JSON 格式错误，脚本会自动带上错误提示重试（最多 3 次）。
- **断点续传**：如果中途中断，再次运行脚本会自动从上次断开的地方继续。

### 4. 提交前终检与打包

预测完成后，必须运行验证脚本，确保生成的 `submit.json` 100% 符合天池的提交要求。

```bash
# 运行验证脚本
python3 /home/ubuntu/skills/mgbie-ner-annotator/scripts/validate_submission.py \
  /home/ubuntu/bisai_clone/数据/A榜/submit.json
```

如果验证通过（输出 `✓ 所有边界和格式验证通过！`），则进行打包：

```bash
# 打包为 submit.zip
cd /home/ubuntu/bisai_clone/数据/A榜/
zip submit.zip submit.json
```

将 `submit.zip` 提交至天池 A 榜即可。

## 资源文件说明

| 文件 | 说明 | 何时使用 |
|------|------|------|
| `references/official_patterns.md` | 官方 1000 条训练数据的真实统计规律与铁律 | 预测前必读，构建 Prompt 的核心依据 |
| `references/prompt_template.md` | 比赛级系统提示词与 Few-shot 组装模板 | 了解脚本内部 Prompt 结构时查阅 |
| `scripts/predict_track_a.py` | 自动化批量预测脚本（含 API 调用、重试、校验） | 阶段三执行预测时使用 |
| `scripts/validate_submission.py` | 提交文件格式与边界终检脚本 | 阶段四打包前使用 |

## 执行准则

- **放弃纠错**：不要试图用国标、行标或论文去纠正官方的标注偏好。
- **边界至上**：宁可漏标一个实体，也绝不能提交边界计算错误的实体（会导致整个文件评测失败）。
- **拥抱空白**：遇到确实没有实体或关系的句子，勇敢地输出空数组 `[]`，这符合官方 32.7% 的数据分布。
- **自动化优先**：不要手动一条条去改 JSON，全部交由 `predict_track_a.py` 脚本处理，脚本内置的校验逻辑比人眼更可靠。
