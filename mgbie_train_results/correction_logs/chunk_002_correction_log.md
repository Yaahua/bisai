# MGBIE 数据块 chunk_002 修正记录

**审查建议采纳情况**: 共采纳 4 条，未采纳 3 条。

## 详细修正日志

1. **采纳**: 将 Sample 1 中的实体 'H2O2' 的标签从 TRT 修改为 ABS。理由：根据[通用生物学常识]，H2O2是活性氧，属于非生物胁迫指标。

2. **采纳**: 修正 Sample 1 中的实体边界，从 'O2 center' 修正为 'O2 center dot-'。理由：根据[TaeC-2024]原则，实体边界必须与原文精确匹配。

3. **未采纳**: 关于 Sample 6 中 AFF 关系方向的修改建议。理由：审查建议的 (GENE, ABS/BIS) -> AFF 关系不符合官方定义（AFF 的结尾必须是 TRT）。原关系 (ABS/BIS, GENE) -> AFF 同样不合规。因此，拒绝该建议并删除所有不合规的关系。

4. **采纳**: 修正 Sample 7 中的实体边界，从 'abnormal pollen tube subapical growth' 修正为 'pollen tube subapical growth'。理由：根据[词块审查标准]，实体不应包含主观或程度修饰词。

5. **未采纳**: 关于 Sample 8 中拆分 'spring oat germplasm' 的建议。理由：'spring oat' (春燕麦) 是作物类别 (CROP)，而非具体品种 (VAR)；'germplasm' (种质) 是育种材料，不属于性状 (TRT)。原标注更合理。

6. **采纳**: 关于 Sample 8 中 'agronomic' 实体的修改建议。理由：根据[NY/T 2645-2014]，单独的形容词无法构成性状实体。由于原文中 'agronomic' 与 'traits' 不连续，故删除此无效实体。

7. **未采纳**: 关于 Sample 10 中将 'Drought stress' 分类为 ABS 的建议。理由：在初步分类 JSON 数据的 Sample 10 中未找到 'Drought stress' 实体，该建议无法执行。