# GLiNER 与 GLiREL 在 Track-A 赛道的合规性调查报告

## 1. 调查背景

在针对 CCL2026-MGBIE 杂粮育种信息抽取评测的守擂规划中，我们提出了使用本地轻量级模型 GLiNER 和 GLiREL 替代高成本 API 调用的方案（详见文档 11）。用户对此提出了关键疑问：“我选择的是不微调赛道（Track-A），也可以使用这些模型吗？”

本报告旨在通过对比赛规则的严格解读，以及对 GLiNER/GLiREL 技术原理的深入查证，明确回答该问题，并评估该方案的合规性与风险。

## 2. 比赛规则解读

根据官方 GitHub 仓库（[CCL2026-BreedIE](https://github.com/zhiweihu1103/CCL2026-BreedIE)）的赛道设置说明：

> **赛道设置**
> 本次评测设置两个赛道，分为不微调和微调赛道。两条赛道的评分指标相同，最终榜单各自独立排名。
>
> | 赛道 | 允许资源/方法 |
> | :--- | :--- |
> | **Track-A（不微调）** | **不可对模型参数进行微调；可用方法：In-Context Learning** |
> | Track-B（微调） | 允许在官方提供的数据集上微调模型参数 |
>
> **注意：**
> * 两个赛道对于模型参数要求如下：微调赛道使用的模型参数规模不超过7B；**不微调赛道不限制模型参数。**
> * **允许使用外部的数据**，但最后必须确切的提供数据源以及对应外部数据。

**核心限制提炼：**
1. **禁止行为**：绝对不允许使用官方提供的数据集（如 `train.json`）去改变（微调）模型原本的权重参数。
2. **允许行为**：允许使用任何规模的预训练模型进行直接推理（Inference）；允许使用 In-Context Learning（即通过 Prompt 提供 Few-shot 示例）；允许使用外部数据。

## 3. GLiNER 与 GLiREL 技术原理分析

为了判断合规性，我们需要确认 GLiNER 和 GLiREL 在我们的使用场景中是否发生了“参数微调”。

### 3.1 GLiNER (Generalist and Lightweight Model for NER)

GLiNER 是一种基于双向 Transformer 编码器（类似 BERT）的通用命名实体识别模型 [1]。

*   **工作原理**：它在预训练阶段已经学习了如何将“实体类型的自然语言描述”与“文本中的实体片段”进行对齐。在推理时，用户只需输入文本和期望提取的实体标签列表（如 `["Crop", "Gene", "Trait"]`），模型即可在一次前向传播中输出所有匹配的实体 [2]。
*   **是否微调**：GLiNER 的核心卖点就是其强大的 **Zero-Shot（零样本）** 能力。官方 GitHub 仓库明确指出，只需调用 `GLiNER.from_pretrained()` 加载模型，然后使用 `model.predict_entities()` 进行预测即可 [2]。整个过程**完全不改变模型参数**。

### 3.2 GLiREL (Generalist Model for Zero-Shot Relation Extraction)

GLiREL 是 NAACL 2025 接收的最新零样本关系抽取模型 [3]。

*   **工作原理**：与 GLiNER 类似，GLiREL 也是一个为零样本推理设计的轻量级模型。它接收文本和预先识别出的实体，并根据用户提供的关系标签列表，在一次前向传播中预测所有实体对之间的关系 [4]。
*   **是否微调**：文献和官方文档均强调其为 **Zero-Shot Relation Extraction** 架构 [3][4]。在使用时，它仅作为推理引擎运行，**不涉及任何基于官方训练集的参数更新**。

## 4. 合规性结论与建议

### 4.1 明确结论

**在 Track-A（不微调赛道）中使用 GLiNER 和 GLiREL 是完全合规的。**

**理由如下：**
1.  **纯推理模式**：我们在本地部署 GLiNER/GLiREL 时，仅下载其预训练权重，并将其作为“黑盒”函数调用以进行前向推理（Inference）。这完全符合 Track-A“不可对模型参数进行微调”的核心限制。
2.  **参数规模不限**：Track-A 明确规定“不限制模型参数”，因此使用这些基于 BERT/DeBERTa 架构的小模型（通常小于 1B 参数）毫无问题。
3.  **零样本/ICL 性质**：将标签名称作为输入提示模型进行抽取，本质上是一种特定形式的 Prompting/Zero-Shot 推理，这与 Track-A 鼓励使用 In-Context Learning 的精神是一致的。

### 4.2 潜在风险与应对建议

尽管合规，但在实际应用中仍需注意以下几点：

1.  **避免无意间的微调**：在编写代码时，必须确保模型处于 `eval()` 模式，绝对不要编写任何涉及 `loss.backward()` 或 `optimizer.step()` 的训练循环代码，以免无意中触发参数更新导致违规。
2.  **外部数据声明**：如果您使用了专门针对生物医学领域预训练的版本（如 `GLiNER-BioMed` [5]），由于其预训练过程使用了外部数据，根据比赛规则，您可能需要在最终提交技术报告时，声明使用了该开源预训练模型及其背后的训练语料来源。
3.  **标签映射（Label Mapping）**：GLiNER/GLiREL 对自然语言标签敏感。比赛中规定的缩写（如 `CROP`, `TRT`）可能不利于模型理解。建议在推理时传入全称（如 `Crop`, `Trait`），拿到结果后再映射回官方要求的缩写。这种映射属于后处理规则，完全合规。

## 5. 总结

您可以放心大胆地在 Track-A 中推进《低成本多源 API 与小模型混合冲分方案》。将 GLiNER/GLiREL 作为零成本的本地预标注引擎，配合大模型进行 SuperICL 裁决，是在遵守“不微调”规则的前提下，突破当前 API 成本和召回率瓶颈的绝佳策略。

---
## References
[1] Ziqing Yang et al., "GLiNER: Generalist and Lightweight Model for Named Entity Recognition," *arXiv preprint arXiv:2311.08526* (2023). https://arxiv.org/abs/2311.08526
[2] Urchade Zaratiana et al., "GLiNER GitHub Repository," (2024). https://github.com/urchade/GLiNER
[3] Jack Boylan et al., "GLiREL - Generalist Model for Zero-Shot Relation Extraction," *Proceedings of NAACL 2025* (2025). https://aclanthology.org/2025.naacl-long.418/
[4] Jack Boylan, "GLiREL GitHub Repository," (2025). https://github.com/jackboyla/GLiREL
[5] Ihor Stepanov et al., "GLiNER-BioMed: A suite of efficient models for open biomedical named entity recognition," *arXiv preprint arXiv:2504.00676* (2025).
