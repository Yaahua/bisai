---
name: mgbie-track-a-predictor
description: MGBIE 比赛 Track-A（不微调赛道）专用预测技能。用于读取官方 test_A.json，利用大模型上下文能力（In-Context Learning）进行批量预测，并生成符合天池提交要求的 submit.json。包含 RAG 动态提示词、多模型多数投票集成（Ensemble）、纯规则后处理召回补充等高分策略。当前最高分 0.4172（并列第一）。
---

# MGBIE Track-A Predictor

**当前最高分：0.4172（ensemble_v3，并列第一）**

核心理念：**多模型集成保精确率 + 纯规则后处理补召回率**，两手都要抓。

---

## 一、标准冲分工作流

### Step 1：单模型批量预测（RAG 动态提示词）

用 TF-IDF 为每条测试文本动态检索 Top-4 最相似训练样本作为 Few-shot，比固定样本效果好得多。

```bash
python3.11 /home/ubuntu/bisai/提示词库/predict_track_a_v7_cicl_v2.py   # GPT-4.1-mini
python3.11 /home/ubuntu/bisai/提示词库/predict_track_a_v10_gemini.py    # Gemini-2.5-flash（异质模型）
```

**关键参数：**
- `WORKERS=10`，`temperature=0.0`
- RAG Top-K=4，TF-IDF ngram_range=(1,2)，sublinear_tf=True
- 断点续传：脚本启动时自动加载已有结果，跳过已完成条目

### Step 2：多模型集成投票

三个模型（v7 + v9_clean + v10_gemini）多数投票（MIN_VOTES=2），系统性消除单模型独立错误。

```bash
python3.11 /home/ubuntu/bisai/提示词库/ensemble_vote.py
```

集成后统计特征（ensemble_v3）：关系均值 2.16/条，无关系比例 38.2%。

### Step 3：纯规则后处理（零 API，补召回率）

集成后召回率偏低（2.16 vs 期望 2.80），用规则脚本精准补充漏标关系。

```bash
python3.11 /home/ubuntu/bisai/提示词库/postprocess_v3_rules.py
```

**效果：** 关系均值 2.16 → 2.75，无关系比例 38.2% → 30.2%，新增 238 条高置信度关系，零 API 消耗。

### Step 4：打包提交

```bash
cd /home/ubuntu/bisai/数据/A榜
cp submit_v16_rules.json submit.json
zip -j submit_v16_rules.zip submit.json
```

---

## 二、关键规律（来自训练集分析）

| 指标 | 训练集期望值 | 说明 |
|------|------------|------|
| 关系均值 | **2.80/条** | 低于此值说明召回不足，高于此值说明过度抽取 |
| 无关系比例 | **32.7%** | 约 1/3 的句子真的没有关系 |
| 关系类型分布 | AFF>LOI>HAS>CON>OCI>USE | 按频率排序 |

**最容易漏标的三元组类型（按严重程度）：**

| 三元组 | 触发词（出现在两实体之间） |
|--------|--------------------------|
| CROP→CON→VAR | including, such as, contains, comprising |
| VAR/CROSS→USE→BM | using, used, by, via, through, employed |
| QTL→AFF→TRT | for, of, associated with, controlling |
| MRK→LOI→CHR | on, at, mapped to, located on, detected on |
| ABS/TRT→OCI→GST | at, during, at the, during the |

**规则核心约束：** 触发词必须出现在两个实体之间的文本中（不做全句匹配），且实体间距离 < 60~100 字符，否则误报率极高。

---

## 三、Prompt 设计要点

**System Prompt 必须包含：**
1. 12 种实体类型的精确定义（含反例，如 CHR 要 strip "chromosome" 前缀）
2. 6 种关系类型的合法 head/tail 类型约束
3. 明确告知"32.7% 的句子无关系"
4. "每个实体对最多一个关系"
5. "不要抽取数字、百分比、统计值作为实体"

**Few-shot 示例选择：**
- RAG 检索 Top-4 相似训练样本（主力）
- 动态注入专项示例：检测到 gene/locus 关键词时注入 GENE-LOI-TRT 示例，检测到 marker/chromosome 时注入 MRK-LOI-CHR 示例

---

## 四、经验教训（避坑指南）

**1. 大模型（GLM/GPT）直接预测的过度抽取问题**
即使在 Prompt 中加了严格限制，GLM-4.7-Flash 的关系均值仍高达 5.76（期望 2.80）。不要依赖单个免费模型做全量预测，它们天然倾向于过度抽取。

**2. 集成投票导致召回率下降**
三模型多数投票后，关系均值从 ~3.0 降到 2.16，无关系比例从 ~30% 升到 38.2%。这是正常现象——集成提升精确率的同时会损失召回率。**必须用规则后处理来补回召回率。**

**3. 规则后处理的两个版本教训**
- 第一版（全句匹配触发词）：新增 867 条关系，均值飙到 4.33，过度添加。
- 第二版（实体间文本匹配）：新增 238 条，均值 2.75，接近期望。**规则必须精准，触发词只在两实体之间的文本中检查。**

**4. 不要删除"非法关系"**
之前以为 VALID_TRIPLES 只有 17 种，实际训练集有 153 种三元组类型。不要基于有限的合法列表清洗关系，会误删大量正确预测。

**5. 无关系句子几乎都有实体**
ensemble_v3 中 153 条"无关系"句子，100% 都提取出了实体，说明这些是漏标关系而非真的无关系。可以用规则脚本精准补充。

---

## 五、资源文件

| 文件 | 说明 |
|------|------|
| `提示词库/predict_track_a_v7_cicl_v2.py` | 最佳单模型脚本（GPT，得分 0.3746） |
| `提示词库/predict_track_a_v10_gemini.py` | Gemini 异质模型脚本 |
| `提示词库/ensemble_vote.py` | 多模型多数投票集成（产出 0.4172） |
| `提示词库/postprocess_v3_rules.py` | 纯规则后处理，补充漏标关系（零 API） |
| `数据/A榜/submit_ensemble_v3.json` | 当前最高分基础文件（0.4172） |
| `数据/A榜/submit_v16_rules.json` | v16 规则后处理结果（待提交验证） |
| `分析报告/5_项目交流与试错日志.md` | 完整版本演进记录 |
