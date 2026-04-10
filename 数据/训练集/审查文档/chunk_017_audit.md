**数据块编号**: chunk_017
**审查时间**: 2026-04-10 17:58:00

## 1. 审查概况

| 指标 | 结果 |
| --- | --- |
| 总条数 | 10 |
| 发现错误/遗漏条数 | 3 |
| 主要错误类型分布 | 泛称实体过宽 3 处；关系过度外推 1 处 |

本块在群体、材料、QTL 与显式性状方面的处理总体稳定，尤其是 `F-2 population` 归为 **CROSS**、对否定句中 `No QTL were detected for CGR` 不误建关系、以及 `DTF3A -> chromosome three` 的定位恢复，均符合技能要求。统一审查后发现的问题主要集中在“把家族名或泛称集合词当作稳定 GENE”这一类过宽吸收上，另有一处作物—性状关系存在语义外推风险。

## 2. 详细审查意见与权威依据

### 问题 1: `PgB3` 为家族层表达，不宜直接当作稳定命名基因

- **错误位置**: Sample 2
- **原分类结果**: 将 `PgB3` 标为 **GENE**，并建立 `drought -> PgB3`、`high-temperature stresses -> PgB3` 的 **AFF**。
- **修改建议**: 建议删除 `PgB3` 实体及其两条 **AFF** 关系，仅保留明确命名成员 `PgRAV-04`。
- **权威依据**: 原句是 `Most PgB3 genes show upregulated expression...`，其中 `PgB3` 指向的是基因家族/集合层级，而非稳定命名的单个基因。根据技能中的“命名对象优先、家族/泛称从严”规则，以及 `[SUN-2019]` 对家族名与成员名区分的要求，这类集合概念不宜直接固化为 **GENE** 实体，更不宜继续接收具体胁迫关系。

### 问题 2: `drought-responsive genes` 为泛称集合，且 `sorghum -> drought tolerance` 存在轻度外推

- **错误位置**: Sample 3
- **原分类结果**: 保留 `drought-responsive genes` 为 **GENE**，并建立 `sorghum -> drought tolerance` 的 **HAS**。
- **修改建议**: 建议删除 `drought-responsive genes` 实体；同时对 `sorghum -> drought tolerance` 进行收紧，原则上可删除该关系，仅保留 `drought tolerance` 与 `sorghum` 作为文本中的主题对象。
- **权威依据**: `drought-responsive genes` 是功能性集合短语，不是命名基因。按照技能的词块审查原则，此类表达默认不稳定，不应直接写入 **GENE**。同时，原句 `contributes to drought tolerance improvement in sorghum` 更接近“研究资源服务于耐旱改良”的用途性表述，并非直接陈述“sorghum 拥有该性状”的稳定事实，因此把它固定为 **HAS** 关系有一定过度外推风险。[TaeC-2024] 亦强调，应优先保留原句直接可验证的结构，避免将改良目标重写为固有属性关系。

### 问题 3: `FT genes` 仍属泛称集合，不宜直接作为 GENE 保留

- **错误位置**: Sample 10
- **原分类结果**: 将 `FT genes` 标为 **GENE**，但未建立关系。
- **修改建议**: 建议删除 `FT genes` 实体，保留 `major QTL`、`DTF3A`、`flowering time`、`short-day conditions` 与 `chromosome three` 的核心骨架。
- **权威依据**: `a cluster of three FT genes` 仍然是簇/集合描述，不是可唯一落点的命名基因。根据技能中的“泛称从严、命名优先”规则，这类表述在缺少具体成员名时，不宜进入最终监督数据。若保留，会在模型训练中把集合短语误学为单一基因实体。

## 3. 审查总结与后续建议

本块说明一个高频问题：当句子谈论的是“基因家族”“响应性基因集合”或“基因簇”时，初标阶段很容易为了不漏信息而把其整体吸收为 **GENE**。但从统一审查角度看，只要没有稳定命名成员，这类表达应尽量回收。相反，像 `F-2 population`、`qGW1`、`DTF3A` 这类边界稳定、语义明确的实体则应继续坚决保留。

建议在后续全量修正与经验沉淀中补充一条专门规则：**凡出现 family / genes / gene cluster / responsive genes 等集合性基因表达，若无具体成员名，默认不入 GENE；若已误入，优先在审查阶段回收。**
