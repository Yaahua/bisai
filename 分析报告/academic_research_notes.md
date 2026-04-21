# 学术调研笔记（2026-04-21）

## 一、POSW-Vote 论文核心方法

**来源**：Hoang Van Toan et al., "POSW-Vote: A precision-oriented weighted voting framework for robust information extraction from domain-specific reports", JMST 2025

### 核心思路
对同一文档运行 N 次 LLM，将 N 个 JSON 输出通过 POSW-Vote 算法聚合为一个最终结果。

### 三步算法（Algorithm 1）

**Step 1: 候选聚类（Candidate Clustering，lines 1-14）**
- 对每个 schema 字段的所有候选值，用 Jaccard 相似度（token 级别）聚类
- 公式：`J(a,b) = |T(a) ∩ T(b)| / |T(a) ∪ T(b)|`，阈值 τ
- 相似度 ≥ τ 的值归入同一簇，否则新建簇

**Step 2: 加权评分（Weighted Scoring，lines 16-20）**
- 每个簇的得分 = Σ(run 权重 w_i) for all v_i in cluster
- 按得分降序排列
- 若 |C| > 1 且 (S(C1) - S(C2))/S(C1) < λ，则弃权（uncertain）

**Step 3: 超字符串选择（Superstring Selection，lines 21-27）**
- 从得分最高簇中选最完整的值（包含其他候选的最长字符串）
- 若 best 包含 v，则 best = best；否则若 len(v) > len(best)，则 best = v

### 关键参数
- τ（Jaccard 相似度阈值）：控制聚类粒度
- λ（置信度边界）：控制弃权阈值
- w（每次 run 的权重）：默认均等

### 实验结果
- 在越南军事报告数据集上，POSW-Vote 相比单次运行和模型内集成，**一致提升 Precision 和 F1**
- 跨异质模型（不同 LLM）也保持鲁棒性

---

## 二、一致性-准确性相关性论文核心发现

**来源**：Xinzhi Yao et al., "Consistency–accuracy correlation in hard-prompted LLMs for entity and relation extraction: empirical findings from plant-health data", Genomics Informatics 2026

### 关键发现
1. **一致性与准确性的相关性很弱（0.10-0.30）**：不能用一致性作为准确性的代理指标
2. **NER+RE 联合提示优于纯 RE 提示**：先让 LLM 识别实体，再做关系抽取，准确性和一致性均更高
3. **文档越长/越复杂，准确性和一致性越低**
4. **温度 0.2、top-p 0.1 效果最好**（在植物健康数据集上）
5. **5 次重复采样**足够评估一致性，更多次数对准确性提升有限

### 对我们的启示
- 多次采样 + 投票可以提升稳定性，但不能保证提升准确性
- 联合 NER+RE 提示是更好的 prompt 设计
- 对于关系抽取，语义等价匹配（同义词/缩写）很重要

---

## 三、对当前竞赛的应用方案

### 方案 A：多次采样 + POSW-Vote 聚合（高优先级）

**原理**：对 test_A 中所有样本，用 gpt-4.1-mini 运行 3-5 次，将多次输出用 POSW-Vote 聚合，只保留在多次运行中一致出现的关系。

**实现步骤**：
1. 对每个样本运行 3 次 LLM（温度 0.3-0.5，增加多样性）
2. 对每次输出的关系三元组（entity1, relation_type, entity2）进行 Jaccard 相似度聚类
3. 只保留在 ≥2 次运行中出现的关系（多数投票）
4. 过滤掉不在训练集关系类型中的幻觉

**预期效果**：提升精度，减少假阳性，可能提升 F1

**成本估计**：111 个无关系样本 × 3 次 = 333 次 API 调用，约 $0.5-1

### 方案 B：基于训练集的关系类型置信度加权

**原理**：不同关系类型的 LLM 抽取精度不同，训练集高频类型（VAR-HAS-TRT:328、CROP-HAS-TRT:165）比低频类型（BM-USE-GENE:3）更可靠。

**实现**：对 LLM 输出的关系，按训练集频次加权置信度：
- 频次 ≥ 100：置信度系数 1.0（直接接受）
- 频次 50-100：置信度系数 0.8（需要额外验证）
- 频次 < 50：置信度系数 0.5（高风险，谨慎接受）

### 方案 C：扩展 LLM 覆盖到有关系样本（最激进）

**原理**：当前 LLM 只处理了 111 个无关系样本。如果对有关系样本也运行 LLM，可能发现被底座遗漏的关系。

**风险**：有关系样本中 LLM 可能产生大量假阳性（与底座冲突），需要谨慎过滤。

---

## 四、明日提交优先级（结合学术调研）

| 优先级 | 版本 | 策略 | 预期 |
| :--- | :--- | :--- | :--- |
| **1** | `submit_v37_gene_trt` | 双重背书 GENE-AFF-TRT:22 | 稳健，低风险 |
| **2** | `submit_v37_crop_has` | 双重背书 CROP-HAS-TRT:18 | 稳健，低风险 |
| **3** | `submit_v38_llm_highconf` | LLM 高置信度 127 条 | 中风险，验证 LLM 路线 |
| **备用** | 新生成：多次采样 POSW-Vote 版本 | 方案 A | 高潜力，需今日生成 |
