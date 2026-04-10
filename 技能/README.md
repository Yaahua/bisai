# Manus AI 技能库

本目录存放针对 CCL2026-MGBIE 比赛定制的 Manus AI 技能定义文档。

## 核心技能

### `mgbie-ner-annotator`
- **功能**：MGBIE 比赛 Track-A（不微调赛道）专用预测技能。
- **工作流**：
  1. 从官方 `train.json` 提取规律和 Few-shot 示例。
  2. 构建比赛级 Prompt，明确写入官方铁律（LOI/AFF/HAS 的真实分布），禁止 AI 自行纠错。
  3. 批量预测 `test_A.json` 400 条，自动校验边界和锚点，失败则单条重试。
  4. 打包 `submit.zip`，直接可提交天池。
- **文档**：`SKILL.md` 包含完整的技能定义和执行步骤。

> **注意**：原有的 `mgbie-review-agent` 技能已被删除，因为本方案已放弃对训练集进行 AI 修正，对抗性审查技能不再适用。
