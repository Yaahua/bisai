# chunk_014 问题清单

## 1. 已确认问题

| 序号 | 位置 | 问题类型 | 具体问题 | 直接修复动作 |
| --- | --- | --- | --- | --- |
| 1 | Sample 2 | 关系漏标 | 第二处 `salt stress[102:113]` 已覆盖多个并列性状，但缺少到 `membrane permeability[221:242]` 的 `AFF` 关系。 | 补充 `(salt stress[102:113], membrane permeability[221:242]) -> AFF`。 |
| 2 | Sample 8 | 词块边界冗余 | 同一起点同时保留 `salt concentration[33:51]` 与 `salt concentrations (0, 50, 100, 150, and 200 mmol L-1)[33:88]` 两个 `ABS`，形成长短嵌套竞争。 | 删除短词块，仅保留长词块。 |
| 3 | Sample 8 | 关联关系锚点不一致 | 当前 `(ABS, salt tolerance level) -> AFF` 仍指向被删除的短词块 `salt concentration[33:51]`。 | 将该 `AFF` 的 head 统一改为长词块 `salt concentrations (0, 50, 100, 150, and 200 mmol L-1)[33:88]`。 |

## 2. 潜在问题

| 序号 | 位置 | 潜在风险 | 复核结论 |
| --- | --- | --- | --- |
| P1 | Sample 2 | 并列结构中间项最容易漏连，补关系时需同步确认其他并列性状是否已完整覆盖。 | 现有 `dry/fresh weight`、`chlorophyll content`、`MDA content`、`Na+/K+ ratio` 均已存在 `AFF`，仅缺 `membrane permeability`。 |
| P2 | Sample 8 | 删除短词块后，若关系 head 偏移未同步替换，会造成悬空关系。 | 必须同步替换 `head/head_start/head_end/head_type` 四个字段。 |
| P3 | Sample 8 | 长短实体并存时，后续格式校验可能因重复语义实体导致训练噪声。 | 修复后应确认仅保留一个 `ABS`，且文本边界与原句完全一致。 |

## 3. 关联问题

本块修复时需要把**实体修复**与**关系修复**绑定处理，不能只改其中一层。具体而言，Sample 2 的问题属于并列关系覆盖不全；Sample 8 的问题属于实体边界选择错误，并连带影响 `AFF` 关系锚点。两类问题都需要在回写后再次核对：一是关系是否与现存实体完全对齐，二是同一位置是否还残留竞争性实体。
