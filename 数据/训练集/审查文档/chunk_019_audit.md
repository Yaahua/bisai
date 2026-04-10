**数据块编号**: chunk_019
**审查时间**: 2026-04-10 18:12:00

## 1. 审查概况

| 指标 | 结果 |
| --- | --- |
| 总条数 | 10 |
| 发现错误/遗漏条数 | 3 |
| 主要错误类型分布 | 泛化基因家族/基因群实体 2 处；条件类型误判及关系方向不稳 1 处 |

本块初标在标记、QTL、材料集合和温度区间处理上总体较稳，尤其是 `CqZF-HD14` 的方向修正、`sorghum germplasm resources` 的整体保留以及 QTL—TRT—CHR 的核心框架，均有较好一致性。统一审查后发现的主要问题集中在**泛化基因家族表达**和**条件实体类型判断**两个方面，均属于跨块一致性必须收紧的项目。

## 2. 详细审查意见与权威依据

### 问题 1: `ZF-HD family` 属于基因家族泛称，不应在最终结果中作为稳定 GENE 实体保留

- **错误位置**: Sample 6
- **原分类结果**: 将 `ZF-HD family` 标为 **GENE**，并保留 `quinoa -> ZF-HD family (CON)`。
- **修改建议**: 建议删除 `ZF-HD family` 实体及其对应 `CON` 关系，仅保留命名且可稳定定位的 `CqZF-HD14`。
- **权威依据**: `ZF-HD family` 是家族层面的集合表述，不是稳定单基因命名。按照审查技能的“命名优先、家族/群体泛称从严”原则，只有 `CqZF-HD14` 这类符合标准命名模式的对象应作为最终 **GENE** 保留。[CGSNL-2011] 对基因命名强调稳定、可定位与可区分性，家族泛称若单独入库，会使训练集混淆“具体基因”和“家族类别”。该问题与 chunk_017 中已发现的 `PgB3`/`FT genes` 类似，属于应统一清理的泛化 GENE 模式。

### 问题 2: `MAX1-like genes` 与前一问题同类，属于泛称基因群，不宜作为最终 GENE 实体

- **错误位置**: Sample 7
- **原分类结果**: 将 `MAX1-like genes` 标为 **GENE**，并保留 `rice -> MAX1-like genes (CON)`。
- **修改建议**: 建议删除 `MAX1-like genes` 实体及其 `CON` 关系，仅保留 `OsMAX1`、`OsHAM2` 等命名明确的基因。
- **权威依据**: 原句以并列列举方式同时出现“MAX1-like genes”与具体基因名 `OsMAX1`、`OsHAM2`。此时泛称只起概括说明作用，不应与具体命名基因并列进入最终标注。若同时保留，会把“家族概括项”和“成员项”混成同等级实体，破坏标签边界的一致性。该项应与上一问题共同纳入跨块统一规则：**family / genes / responsive genes / like genes 等泛称结构，若无独立稳定命名，不进入最终 GENE 结果。**

### 问题 3: `cold sowing conditions` 更接近环境处理条件，当前标为 GST 并使用 `TRT -> GST (OCI)` 不够稳

- **错误位置**: Sample 5
- **原分类结果**: 将 `cold sowing conditions` 标为 **GST**，并建立 `frost survival -> cold sowing conditions (OCI)` 与 `plant emergence -> cold sowing conditions (OCI)`。
- **修改建议**: 建议将 `cold sowing conditions` 改标为 **ABS**；关系改为 `cold sowing conditions -> frost survival (AFF)` 与 `cold sowing conditions -> plant emergence (AFF)`。若全量修正阶段认为条件语义仍过宽，也可退而删除该条件实体，仅保留 `QTL -> TRT` 与 `QTL -> CHR` 两类核心关系。
- **权威依据**: `cold sowing conditions` 描述的是低温播种环境下的实验/生产条件，而非单纯“生育时期”本体。技能中 **GST** 主要对应明确阶段性表达，如 `germination stage`、`seedling stage`、`heading stage` 等；而此处主干是“under cold sowing conditions”，语义上更接近环境胁迫/处理条件，应按 **ABS** 理解。继续使用 `OCI` 会让训练集把环境条件误学成阶段归属，降低关系语义清晰度。

## 3. 审查总结与后续建议

本块最重要的统一经验有两条。其一，**只要句中已经出现稳定命名基因，就应优先删除 family、like genes、responsive genes 等泛称实体**；其二，**凡含有 under + condition/temperature/stress 的表达，应优先从 ABS 视角判断，而不要因为出现 sowing、germination 等词就机械落入 GST。**

建议在后续全量修正时补充跨块规则：一律回查所有带 `family`、`genes`、`-like genes` 的 GENE 实体；同时复核所有 GST 标签，确认其是否真为阶段而非环境条件。
