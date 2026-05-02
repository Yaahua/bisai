# v47 单候选假设卡 2026-05-02

作者：**Manus AI**  
底座：`当前工作区/底座/submit_baseline_04514_v44_del_var_con_cross.json`，已知 A 榜分数 **0.4514**  
候选策略：**单条补召回**，只新增一条关系，不删除、不换向、不复用 v46/v46b 旧包。

## 一、候选结论

本轮证据表筛选出的唯一候选是样本 **249** 的 `QTL-LOI-TRT` 关系：`QTLs` — `LOI` — `grain HIS content`。该候选不是 v36→v41 或 v41→v44 已验证删除集合中的关系，也不属于 v46/v46b 冻结体系；它来自 42 个历史提交源的一致支持，训练集中 `QTL-LOI-TRT` 类型频次为 224，并且文本中存在直接语义证据：“QTL analysis of grain HIS content ... Three QTLs were detected.”

| 字段 | 内容 |
|---|---|
| 候选名 | `v47_single_add_qtl_loi_trt_249_grain_his` |
| 样本索引 | `249` |
| 操作类型 | 单条新增关系 |
| 关系类型 | `QTL-LOI-TRT` |
| head | `QTLs` |
| head_span | `388-392` |
| tail | `grain HIS content` |
| tail_span | `4-21` |
| label | `LOI` |
| 自动闸门 | `pass` |
| 候选证据表得分 | `21.3` |
| 历史支持源数 | `42` |
| 训练集类型频次 | `224` |

## 二、文本证据

> The grain HIS content of Schooner No. 3 was 0.21 mg/g. The grain HIS content of the population ranged from 0.23 to 0.54 mg/g. Genetic linkage maps for seven barley chromosomes were constructed using 180 SSR markers. The total genetic distance was 2671.03 cM with an average marker spacing of 14.84 cM. **QTL analysis of grain HIS content in barley was performed using IciMappingV3.3. Three QTLs were detected.**

该文本证据比低频删除或方向猜测更稳健，因为它不是从类型稀有性出发，而是从明确句法语义出发：文本直接说明对 `grain HIS content` 进行 QTL 分析，并检测到 `QTLs`。因此，若以当前底座为唯一来源新增这一条关系，属于**可归因、可解释、单条补召回**。

## 三、通过与不通过闸门

| 闸门 | 状态 | 说明 |
|---|---|---|
| 底座来源唯一 | 通过 | 生成时必须从 `submit_baseline_04514_v44_del_var_con_cross.json` 复制派生 |
| 单条可归因 | 通过 | 只新增 1 条关系，不改已有关系 |
| 非删除路线 | 通过 | 不删除、不消融、不换向 |
| 非冻结类型 | 通过 | 不是 `VAR-CON-CROSS`，不是 v46/v46b 旧候选 |
| 文本证据 | 通过 | “QTL analysis of grain HIS content ... Three QTLs were detected” 明确支持 |
| 训练类型支持 | 通过 | `QTL-LOI-TRT` 在训练集中频次为 224 |
| 历史共识支持 | 通过 | 42 个历史提交源包含相同关系 |
| 失败可定位 | 通过 | 若掉分，只冻结“样本249 QTL-LOI-TRT 单条补召回”及同类弱泛化，不影响底座 |

## 四、硬性禁止

本候选生成后，只允许产生一个 JSON 和一个 ZIP；不允许同时生成第二候选，不允许把证据表前 30 名批量打包，不允许上传任何 `v46`、`v46b`、`micro_del` 或 `micro_add_consensus` 文件。若用户选择上传并反馈分数，则必须先更新提交账本和禁忌记录，再决定是否进入下一轮。
