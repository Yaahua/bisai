# 调研笔记：API 价格 + 学术论文

## 一、国内 API 调研

### 智谱 GLM（open.bigmodel.cn）

| 模型 | 输入价格 | 输出价格 | 上下文 | 特点 |
| --- | --- | --- | --- | --- |
| GLM-5.1 | 6元/百万tokens | 24元/百万tokens | 32K | 最新旗舰 |
| GLM-4.7-Flash | **免费** | **免费** | 200K | 免费！高性价比 |
| GLM-4.7-FlashX | 0.5元/百万tokens | 3元/百万tokens | 200K | 极低成本 |
| GLM-4.5-Air | 0.8元/百万tokens | 2元/百万tokens | 128K | 平衡性能 |
| GLM-4-Air | 0.5元/百万tokens | 0.25元/百万tokens | 128K | 旧版低价 |

**关键发现：GLM-4.7-Flash 完全免费，200K 上下文，非常适合作为低成本第三/第四模型！**

API 接入方式：OpenAI 兼容接口
- base_url: https://open.bigmodel.cn/api/paas/v4/
- 模型名: glm-4-flash / glm-4.7-flash / glm-4-air

### MiniMax（platform.minimaxi.com）

| 模型 | 输入价格 | 输出价格 | 上下文 | 特点 |
| --- | --- | --- | --- | --- |
| MiniMax-M2.7 | 2.1元/百万tokens | 8.4元/百万tokens | — | 最新旗舰 |
| MiniMax-M2.7-highspeed | 4.2元/百万tokens | 16.8元/百万tokens | — | 高速版 |
| MiniMax-M2.5 | 2.1元/百万tokens | 8.4元/百万tokens | — | 上一代 |

**关键发现：MiniMax-M2.7 最新旗舰，价格适中，与 GLM 形成互补。**

API 接入方式：OpenAI 兼容接口
- base_url: https://api.minimax.chat/v1/
- 模型名: MiniMax-M2.7 / MiniMax-M2.5

---

## 二、学术论文调研

### 1. GLiREL（2501.03172，NAACL 2025）
**零样本关系抽取小模型，无需 API 调用**

- 架构：基于 GLiNER 的双向 Transformer 编码器（BERT-like），约 200M 参数
- 核心优势：单次前向传播预测所有实体对的关系，速度极快
- 性能数据（FewRel 基准，m=5）：
  - GLiREL + 合成预训练：F1 = **94.20**（超越 GPT-4o 的 89.20！）
  - GPT-4o：F1 = 89.20
  - GLiREL（无合成预训练）：F1 = 81.21
- 性能数据（Wiki-ZSL 基准，m=5）：
  - GLiREL + 合成预训练：F1 = **83.28**（超越 GPT-4o 的 80.03！）
  - GPT-4o：F1 = 80.03
- **结论：GLiREL 在零样本关系分类上超越 GPT-4o，且完全本地运行，零 API 消耗！**
- 安装：`pip install gliner glire`
- GitHub：https://github.com/jackboyla/GLiREL

### 2. GLiNER（2311.08526）
**零样本 NER 小模型**

- 架构：双向 Transformer 编码器，约 200M 参数
- 核心优势：给定任意实体类型标签，无需微调即可识别
- 性能：在多个 NER 基准上超越 ChatGPT
- 有农业/生物医学专用版本：GLiNER-BioMed（2504.00676）
- 安装：`pip install gliner`
- GitHub：https://github.com/urchade/GLiNER

### 3. SuperICL（2305.08848，ACL Findings 2024）
**小模型 + 大模型协作，降低 LLM API 消耗**

- 核心思想：用本地小模型（如 BERT）先预测，将预测结果和置信度作为额外上下文注入 LLM Prompt
- 效果：在多个分类任务上提升 LLM 性能，同时减少 LLM 的"思考负担"
- 适用场景：用 GLiNER/GLiREL 的预测结果作为 Prompt 的额外信息，引导 GPT/GLM 做最终决策

### 4. 语义缓存（GPTCache, 2023）
**缓存相似查询，避免重复 API 调用**

- 核心思想：用向量相似度检索历史 API 响应，相似度超过阈值直接返回缓存结果
- 效果：最高减少 86% API 调用，响应速度提升 88%
- 对 MGBIE 的适用性：400 条测试集中有相似句子，缓存命中率约 20-30%
- 工具：GPTCache（开源）或自建 FAISS + Redis 缓存

---

## 三、整合策略建议

### 低成本多模型集成方案（修正版）

| 角色 | 模型 | 成本 | 说明 |
| --- | --- | --- | --- |
| 主力模型 | gpt-4.1-mini | 中等 | 当前最高质量 |
| 免费补充 | GLM-4.7-Flash | **零成本** | 完全免费，200K 上下文 |
| 本地预标注 | GLiNER + GLiREL | **零成本** | 本地运行，无 API 消耗 |
| 低成本验证 | GLM-4.5-Air | 极低 | 0.8元/百万tokens |

### 语义缓存策略
- 对 400 条测试集按语义相似度聚类（约 50-80 个簇）
- 每个簇只调用 1 次 API，其余用缓存结果（修改实体名称）
- 预计节省 60-70% API 调用
