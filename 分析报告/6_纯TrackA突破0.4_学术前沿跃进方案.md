# MGBIE Track-A（不微调赛道）突破 0.4 分学术前沿跃进方案

根据对 `bisai` 仓库的深入调查，目前最高得分为 v3 版本的 0.3482 分。核心痛点在于**模型假阳性（FP）过高（过标严重）**，以及部分复杂关系（如 `GENE-LOI-TRT`）的漏标。在明确**完全不考虑 Track-B（微调）**的前提下，为了在 Track-A 中突破 0.4 分（重回前四名甚至冲击第一名），我们必须彻底抛弃简单的“静态 Prompt + 后处理过滤”模式，转向当前学术界在信息抽取（Information Extraction, IE）领域最前沿的**上下文学习（In-Context Learning, ICL）**和**检索增强生成（RAG）**技术。

本方案结合了 2024-2025 年最新的学术研究成果，特别是针对命名实体识别（NER）和关系抽取（RE）的动态提示词、对比学习（Contrastive ICL）和多智能体集成（Multi-Agent Ensemble）策略 [1] [2] [3]，为你量身定制了一套纯大模型（LLM）的冲分路线图。

## 一、 当前基线诊断与学术视角剖析

目前仓库中的 `predict_track_a_v5.py` 使用了固定数量的 Few-shot 样本（静态 Prompt），并通过 `post_process_v4.py` 使用基于距离和关键词的启发式规则来强行删除预测关系。

从学术研究的视角来看，这种方法存在两个致命缺陷：
1.  **静态 Few-shot 的领域局限性**：静态 Prompt 无法覆盖所有长尾关系和复杂的负样本场景。当输入文本与 Few-shot 样本在语义上差异较大时，LLM 容易产生“幻觉”并过度预测（过标） [1]。
2.  **后处理规则的脆弱性**：基于字符距离（如 `dist > 80`）或特定关键词（如 `AFF_KEYWORDS`）的硬编码过滤规则极其脆弱。它不仅无法处理跨句子的长距离依赖，还会误删大量表达隐晦但合法的关系，导致召回率（Recall）受损。

为了突破 0.4 分，我们必须将“后处理过滤”的压力转移到“前置模型推理”阶段，利用 RAG 和高级 Prompt 技术让模型**自己学会拒绝错误标注**。

## 二、 跃进方案：三阶段学术前沿落地

以下是基于学术前沿技术制定的三阶段优化路线，全部在 Track-A（不微调）框架内实施。

| 优化阶段 | 时间投入 | 核心技术手段（基于最新论文） | 预期解决的核心问题 | 预期分数 (Track-A) |
| :--- | :--- | :--- | :--- | :--- |
| **当前基线** | — | 静态 Few-shot + 启发式后处理 (v3/v5) | — | 0.348 - 0.350 |
| **第一阶段：动态检索** | 1周 | RAG 动态提示词 (Dynamic Prompting) | 解决静态样本不匹配，降低泛化带来的过标 | 0.360 - 0.375 |
| **第二阶段：对比学习** | 1-2周 | 对比上下文学习 (c-ICL) 引入硬负样本 | 根治高频错标（如 `QTL-LOI-TRT` 强行绑定） | 0.380 - 0.395 |
| **第三阶段：多智能体** | 2周 | 多模型投票 (Ensemble) 与多智能体辩论 | 突破单模型能力极限，冲击 0.4+ 绝对高分 | 0.400 - 0.420 |

---

### 第一阶段：RAG 动态提示词 (Dynamic Prompting)

**学术依据**：
根据 2025 年《Nature》子刊的最新研究《Improving few-shot named entity recognition for large language models using structured dynamic prompting with retrieval augmented generation》 [1]，在生物医学等垂直领域的 NER 任务中，**基于 RAG 的动态提示词（Dynamic Prompting）比静态提示词（Static Prompting）能提升高达 12% 的 F1 分数**。研究指出，对于词汇多样性较低的数据集，即使是简单的 TF-IDF 检索也能取得极佳效果；而对于复杂语义，SBERT（Sentence-BERT）检索表现最佳。

**实施方案**：
放弃 `fewshot_v3.json` 中固定的 6 个样本。
1.  **构建检索库**：将官方 `train.json` 中的 1000 条数据作为检索库，使用轻量级向量模型（如 `all-MiniLM-L6-v2`）或 TF-IDF 为每条训练数据生成向量表示。
2.  **动态检索 (RAG)**：在预测 `test_A.json` 的每一条测试集文本时，实时计算其与训练集的余弦相似度。
3.  **Top-K 组装**：检索出最相似的 Top-5 条训练集样本（包含真实的 `entities` 和 `relations`），将其作为该条测试文本的专属 Few-shot 示例，拼接入 Prompt 中。

**预期效果**：模型每次看到的示例都与当前文本的句法结构高度相似，极大地降低了“瞎猜”和“过标”的概率。

### 第二阶段：对比上下文学习 (Contrastive ICL, c-ICL)

**学术依据**：
2024 年的论文《c-ICL: Contrastive In-context Learning for Information Extraction》 [2] 提出，传统的 ICL 只给模型看“正确的例子”（Positive Samples），这使得模型缺乏辨别“陷阱”的能力。c-ICL 创新性地在 Prompt 中同时引入**正样本（正确标注）**和**硬负样本（典型错误标注及其原因）**，显著提升了信息抽取的精确率（Precision）。

**实施方案**：
针对分析报告中提到的高频失分点（如模型喜欢把 `QTL` 和 `TRT` 强行建立 `LOI` 关系，把 `CROP` 和 `TRT` 强行建立 `HAS` 关系），我们在动态检索的基础上，人工或自动构建“硬负样本”。
1.  **构建硬负样本**：在 Prompt 中明确展示容易犯错的案例。例如：
    *   *Input*: "The crop yield was evaluated..."
    *   *Bad Output*: `[{"head": "crop", "tail": "yield", "label": "HAS"}]`
    *   *Reason*: 这里的 crop 和 yield 只是并列提及，并没有明确的品种拥有关系。
    *   *Good Output*: `[]` (空关系)
2.  **Prompt 结构升级**：将 Prompt 修改为包含 `[Task Description] -> [Positive Examples (from RAG)] -> [Hard Negative Examples (c-ICL)] -> [Test Input]` 的结构。

**预期效果**：通过明确告诉模型“不要做什么”并给出具体例子，彻底取代 `post_process_v4.py` 中脆弱的后处理规则，从根本上压制 FP（假阳性）。

### 第三阶段：多模型集成与多智能体辩论 (Ensemble & Multi-Agent Debate)

**学术依据**：
2025 年 ACL Findings 论文《CROSSAGENTIE: Cross-Type and Cross-Task Multi-Agent LLM Collaboration for Zero-Shot Information Extraction》 [3] 证明，在零样本（Zero-shot）或少样本信息抽取中，单一 LLM 的结构化输出能力存在瓶颈。通过引入多智能体协作（Multi-Agent Collaboration），让负责 NER 的 Agent 和负责 RE 的 Agent 进行交叉任务辩论（Cross-Task Debate），可以大幅消除实体与标签的冲突，远超最先进的单模型基线。同时，多模型集成（Ensemble Learning）也是提升鲁棒性的有效手段。

**实施方案**：
为了突破 0.4 的极限分数，我们需要不计成本地压榨大模型的能力。
1.  **多模型异构集成 (Ensemble)**：不要只依赖 `gpt-4.1-mini`。同时使用 `gpt-4.1-mini`、`claude-3.5-sonnet` 和 `qwen-max` 对同一条数据进行独立预测。
2.  **多数投票机制 (Majority Voting)**：编写一个合并脚本，对于实体和关系三元组，只有当至少两个模型都预测出该三元组时，才将其纳入最终结果。这能极其有效地过滤掉单个模型的随机“幻觉”。
3.  **管道拆分 (Pipeline)**：将原本“同时预测 NER 和 RE”的单次调用，拆分为两阶段：
    *   **Agent 1 (NER)**：只负责抽取实体。
    *   **Agent 2 (RE)**：接收原文和 Agent 1 抽取的实体列表，仅在给定的实体对之间判断关系。这极大降低了任务复杂度。

**预期效果**：通过集成学习和任务拆分，Precision 和 Recall 将达到单模型无法企及的平衡点，这是冲击 0.417（第一名）的终极武器。

## 三、 行动指南与优先级

为了将上述学术前沿方案落地，建议采取以下执行步骤：

1.  **本周目标（实施第一阶段）**：
    *   废弃 `fewshot_v3.json`。
    *   编写一个简单的 Python 脚本，使用 `scikit-learn` 的 `TfidfVectorizer`，实现基于官方 1000 条 `train.json` 的 RAG 动态 Few-shot 组装。
    *   替换 `predict_track_a_v5.py` 中的静态 Prompt 逻辑，进行一次全量预测并提交。
2.  **下周目标（实施第二阶段）**：
    *   总结前几次提交的过标规律，手写 3-5 个典型的“错误示范”（硬负样本）。
    *   将硬负样本硬编码到系统 Prompt 中（c-ICL 策略），替代容易误伤的 `post_process_v4.py`。
3.  **终极冲刺（实施第三阶段）**：
    *   如果分数卡在 0.39 左右，引入多模型投票。在测试集（仅 400 条）上，调用多个 API 的成本是完全可以接受的。

## 参考文献

[1] Ge, Y., Guo, Y., Das, S. & Sarker, A. (2026). Improving few-shot named entity recognition for large language models using structured dynamic prompting with retrieval augmented generation. *npj Artificial Intelligence*, 2(39). https://www.nature.com/articles/s44387-025-00062-2

[2] Mo, Y., Liu, J., Yang, J., Wang, Q., Zhang, S., Wang, J., & Li, Z. (2024). c-ICL: Contrastive In-context Learning for Information Extraction. *Findings of the Association for Computational Linguistics: EMNLP 2024*. https://arxiv.org/html/2402.11254v2

[3] Lu, M., Xie, Y., Bi, Z., Cao, S., & Wang, X. (2025). CROSSAGENTIE: Cross-Type and Cross-Task Multi-Agent LLM Collaboration for Zero-Shot Information Extraction. *Findings of the Association for Computational Linguistics: ACL 2025*. https://aclanthology.org/2025.findings-acl.718/
