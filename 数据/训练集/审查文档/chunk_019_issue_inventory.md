# Chunk 019 问题清单

## 1. 已确认问题

| 样本 | 问题类型 | 当前问题 | 直接修复动作 |
| --- | --- | --- | --- |
| Sample 5 | 条件类型误判 | `cold sowing conditions` 被标成 **GST**，且以 `TRT -> GST (OCI)` 建模 | 改为 **ABS**，并将关系改为 `ABS -> TRT (AFF)` |
| Sample 6 | 泛化基因家族误入库 | `ZF-HD family` 被当作 **GENE** 保留 | 删除 `ZF-HD family` 实体与 `quinoa -> ZF-HD family (CON)` |
| Sample 7 | 泛化基因群误入库 | `MAX1-like genes` 被当作 **GENE** 保留 | 删除该实体与 `rice -> MAX1-like genes (CON)` |

## 2. 潜在关联问题

| 样本 | 潜在影响 | 复核要点 |
| --- | --- | --- |
| Sample 5 | 条件实体改型后，原 `OCI` 关系会整体失配 | 需同步检查 `head/tail type`、方向和 occurrence，避免只改标签不改关系 |
| Sample 6 | 删除家族实体后，`quinoa` 仍需保留与具体基因 `CqZF-HD14` 的归属关系 | 保留 `quinoa -> CqZF-HD14 (CON)`，并确认两个 `CqZF-HD14` occurrence 不混淆 |
| Sample 7 | 删除泛称基因后，水稻部分仍应保留 `OsMAX1`、`OsHAM2` | 确认 rice 子句仍完整，且不影响 sugarcane 子句的 `CON/AFF` 网格 |

## 3. 关联修复原则

1. 只删除**泛称家族/基因群**，不删除句中已出现的**稳定命名基因**。
2. 凡 `under ... conditions` 且语义指向环境处理的表达，优先按 **ABS** 建模。
3. 每次修复后必须同步校验实体 span、关系 span、关系方向、重复 occurrence 和孤立实体问题。

## 4. 本块修订目标

本块全量修正仅处理审查已确认的 3 处核心问题，但执行时同步排查其关联字段，确保不存在：

- 仅改实体标签、不改关系类型；
- 删除实体后残留 relation；
- occurrence 因删除前序实体而错指；
- 水稻、藜麦、甜高粱/甘蔗等并列结构在局部修复后出现顾此失彼的情况。
