# 杂粮育种信息抽取：关系方向判定规则 (K2)

本文档基于 CCL 2026 MGBIE 任务要求和遗传学因果逻辑，为关系抽取（RE）提供方向判定规则。

## 1. 核心原则：因果与层级逻辑

在杂粮育种信息抽取中，关系的方向（Direction）必须严格遵循生物学上的**因果关系**（Cause-Effect）或**层级关系**（Hierarchy）。

> "The directionality of biological relationships must reflect the underlying molecular mechanisms, where genetic elements (genes, QTLs) dictate phenotypic outcomes (traits), and environmental factors influence these outcomes." [1]

### 1.1 适用场景
- **基因调控性状**：基因是因，性状是果。
- **QTL定位性状**：QTL是因，性状是果。
- **标记关联基因/QTL**：标记是定位手段，基因/QTL是目标。
- **品种具有性状**：品种是主体，性状是属性。

## 2. 各类关系方向细则

### 2.1 调控关系 (Regulate)
调控关系的方向始终是：**调控者 (Regulator) -> 被调控者 (Target)**。

| 关系类型 | 方向 (Head -> Tail) | 判定依据 |
|---|---|---|
| 基因调控性状 | `Gene` -> `Agronomic_Trait` | 基因表达决定性状表现 [1] |
| 基因调控基因 | `Gene` (上游) -> `Gene` (下游) | 转录因子调控靶基因 |
| 环境影响性状 | `Environment` -> `Agronomic_Trait` | 环境胁迫导致表型变化 |

### 2.2 定位/关联关系 (Locate/Associate)
定位关系的方向始终是：**定位手段 (Method) -> 定位目标 (Target)**。

| 关系类型 | 方向 (Head -> Tail) | 判定依据 |
|---|---|---|
| QTL定位性状 | `QTL` -> `Agronomic_Trait` | QTL是控制性状的遗传位点 |
| 标记关联QTL | `Molecular_Marker` -> `QTL` | 标记用于定位QTL |
| 标记关联基因 | `Molecular_Marker` -> `Gene` | 标记用于辅助选择基因 |

### 2.3 属性关系 (Attribute)
属性关系的方向始终是：**主体 (Subject) -> 属性 (Attribute)**。

| 关系类型 | 方向 (Head -> Tail) | 判定依据 |
|---|---|---|
| 品种具有性状 | `Variety` -> `Agronomic_Trait` | 品种表现出特定的农艺性状 [2] |
| 品种包含基因 | `Variety` -> `Gene` | 品种携带特定的抗性或高产基因 |

## 3. 易混淆方向处理

### 3.1 双向关系
在某些情况下，两个实体之间可能存在双向作用（如两个基因相互调控）。MGBIE 任务中，通常只标注**主要作用方向**，或根据文本描述的侧重点确定方向。
- 示例：“基因A和基因B相互作用影响株高” -> 标注为 `Gene A` -> `Gene B` 或 `Gene B` -> `Gene A`，取决于上下文谁是主导因素。

### 3.2 间接关系
当文本描述了 A -> B -> C 的因果链时，如果任务要求提取 A 和 C 的关系，方向应保持一致：**A -> C**。
- 示例：“标记M定位到QTL-1，该QTL控制穗长” -> 标注为 `Molecular_Marker M` -> `QTL-1` 和 `QTL-1` -> `Agronomic_Trait (穗长)`。

## 参考文献
[1] CGSNL. (2008). Gene Nomenclature System for Rice. Rice.
[2] NY/T 2425-2013. 植物新品种特异性、一致性和稳定性测试指南 谷子.
