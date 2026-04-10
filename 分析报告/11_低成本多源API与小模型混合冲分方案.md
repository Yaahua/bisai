# 11_低成本多源API与小模型混合冲分方案

## 1. 核心痛点与整改目标

在冲击 MGBIE Track-A 榜单的过程中，我们通过**多模型多数投票（Ensemble）**成功突破了 0.4 分的瓶颈，最高达到 **0.4172（并列第一）**。然而，这一策略也暴露出两个致命的瓶颈：

1. **API 积分消耗过快**：四模型集成意味着预测成本翻了 4 倍，在尝试进一步运行 ReverseNER 和 SCIR 自纠正时，API 积分耗尽，导致任务中断。
2. **召回率边际递减**：单纯增加模型数量并提高投票阈值（如 `MIN_VOTES=2` 或 `3`），虽然能提升精确率（Precision），但会导致召回率（Recall）断崖式下跌。

为了在**不增加甚至降低 API 成本**的前提下，继续提升分数并稳固榜首位置，我们查阅了 2024-2026 年信息抽取领域的最新学术文献，制定了以下基于**多源 API 分流**与**大小模型混合协作（SuperICL）**的整改方案。

---

## 2. 国内免费/低成本 API 替代方案

为打破对单一高价 API（如 GPT-4）的依赖，我们调研了国内顶尖大模型的最新计费标准。**智谱 GLM-4.7-Flash** 提供了极具破坏力的**完全免费**策略，且支持 200K 长上下文，是作为多模型集成中“免费选票”的完美选择。

| 模型名称 | 厂商 | 输入价格 (元/1M tokens) | 输出价格 (元/1M tokens) | 角色定位 |
| :--- | :--- | :--- | :--- | :--- |
| **GLM-4.7-Flash** | 智谱 | **免费** | **免费** | 零成本的第三/第四投票模型 |
| GLM-4.5-Air | 智谱 | 0.8 | 2.0 | 低成本验证模型 |
| MiniMax-M2.7 | MiniMax | 2.1 | 8.4 | 异质模型补充，增加投票多样性 |
| gpt-4.1-mini | OpenAI | 中等 | 中等 | 高质量基准模型 |

**整改措施 1**：在后续的多模型集成脚本（如 `ensemble_v4.py`）中，全面引入 `GLM-4.7-Flash` 作为主力投票成员，以零成本获取额外的模型视角。

---

## 3. 引入零样本小模型：GLiNER 与 GLiREL

除了更换便宜的 API，学术界最新的趋势是使用**专门针对零样本（Zero-Shot）信息抽取训练的轻量级本地模型**。这类模型无需调用外部 API，在本地 CPU/GPU 上即可快速运行，且在特定任务上甚至能超越 GPT-4。

### 3.1 GLiNER (Generalist and Lightweight Model for NER)
GLiNER 是一种基于双向 Transformer 编码器（BERT-like）的零样本 NER 模型 [1]。
- **优势**：只需在输入时提供实体类型的自然语言名称（如 "CROP", "GENE"），模型就能识别文本中的对应实体，无需任何微调。
- **生物/农业适配**：开源社区已发布 `GLiNER-BioMed` 版本 [2]，专门针对生物医学和相关领域优化，对基因、蛋白质等实体的识别率极高。

### 3.2 GLiREL (Generalist Model for Zero-Shot Relation Extraction)
GLiREL 是 2025 年 NAACL 接收的最新零样本关系抽取模型 [3]。
- **突破性性能**：在 FewRel 和 WikiZSL 基准测试中，GLiREL（结合合成预训练）的 F1 分数分别达到 **94.20** 和 **83.28**，**全面超越了 GPT-4o（89.20 和 80.03）** [3]。
- **极速推理**：只需一次前向传播，即可预测句子中所有实体对之间的关系，速度极快，**零 API 成本**。

**整改措施 2**：在本地沙盒中安装 `gliner` 和 `glirel` 库。对于测试集，先使用 GLiNER 进行实体预标注，再使用 GLiREL 进行关系预抽取，将这些高置信度的结果作为免费的“保底分数”。

---

## 4. 大小模型混合协作架构 (SuperICL)

为了将小模型（GLiNER/GLiREL）的低成本与大模型（GPT/GLM）的强推理能力结合，我们将采用 **Super In-Context Learning (SuperICL)** 框架 [4]。

SuperICL 的核心思想是：**将本地小模型的预测结果及其置信度，作为上下文（Context）注入到大模型的 Prompt 中**。

### 实施流程
1. **本地预跑（零成本）**：使用 GLiNER 识别实体，GLiREL 预测关系。
2. **置信度过滤**：筛选出 GLiREL 预测概率低于阈值（如 0.6）的“不确定关系”。
3. **大模型裁决（低频调用）**：只将这些“不确定关系”发送给大模型（如 GLM-4.7-Flash）进行二次确认，Prompt 设计如下：
   > "本地模型初步预测句子中的 'Sorghum' (CROP) 和 'height' (TRT) 存在 HAS 关系，置信度为 0.55。请结合你的知识，判断这个关系是否成立？"
4. **优势**：大模型不需要从头抽取所有信息（大幅减少 Token 消耗和幻觉），只需做简单的二分类（Yes/No）判断。这能将 API 调用量降低 70% 以上，同时结合了小模型的专业性与大模型的常识推理能力。

---

## 5. 语义缓存 (Semantic Caching)

为了进一步压榨 API 成本，我们引入**语义缓存（Semantic Caching）**技术 [5]。

在 MGBIE 的 400 条测试集中，存在大量句式结构高度相似、仅实体名称不同的句子。例如：
- 句子 A: "We identified a novel QTL for plant height in maize."
- 句子 B: "We identified a novel QTL for grain yield in rice."

### 实施流程
1. **向量化与聚类**：使用轻量级的 Embedding 模型（如 `all-MiniLM-L6-v2`）将所有测试集句子向量化，并进行相似度聚类。
2. **代表性调用**：每个聚类簇只挑选 1-2 个代表性句子调用大模型 API。
3. **缓存替换**：对于簇内的其他句子，直接复用代表性句子的抽取结构，仅将实体文本替换为当前句子的实体（如把 "maize" 替换为 "rice"）。
4. **预期收益**：据研究表明，语义缓存最高可减少 86% 的 API 调用量 [6]。在 MGBIE 场景下，保守估计可节省 40-50% 的成本。

---

## 6. 总结与执行路线图

通过上述整改，我们彻底摆脱了“堆 API 冲分”的死胡同，转向了**高技术含量的精细化工程**。

**执行路线图：**
- **第一步**：接入智谱 GLM-4.7-Flash（免费），跑通基础的多源 API 投票。
- **第二步**：本地部署 GLiNER 和 GLiREL，跑出第一版零成本预标注结果。
- **第三步**：实现 SuperICL 混合推理，让 GLM 校验 GLiREL 的低置信度结果。
- **第四步**：引入语义缓存，进一步压缩测试集的实际处理量。

这套方案不仅能帮助我们在 Track-A 稳固第一名，其低成本、高效率的特性更是为即将到来的 B 榜（可能包含更大规模的数据）做好了完美的架构准备。

---

## References
[1] Ziqing Yang et al., "GLiNER: Generalist and Lightweight Model for Named Entity Recognition," arXiv preprint arXiv:2311.08526 (2023).  
[2] Ihor et al., "GLiNER-BioMed: A suite of efficient models for open biomedical named entity recognition," arXiv preprint arXiv:2504.00676 (2025).  
[3] Jack Boylan et al., "GLiREL -- Generalist Model for Zero-Shot Relation Extraction," arXiv preprint arXiv:2501.03172 (2025).  
[4] Can Xu et al., "Small Models are Valuable Plug-ins for Large Language Models," arXiv preprint arXiv:2305.08848 (2023).  
[5] GPTCache Contributors, "Gptcache: An open-source semantic cache for llm applications enabling faster answers and cost savings," ACL NLPOSS (2023).  
[6] N. Deplace, "Semantic Caching: a Solution to Exploding LLM Costs," Medium (2025).
