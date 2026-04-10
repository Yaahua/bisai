# MGBIE 数据块 chunk_008 修正记录
## Sample 3 (Index 2)
- **采纳建议**: 移除了实体 `779 bp band`。  - **理由**: 根据审查报告，`bp band` 是电泳实验的观测现象，而非分子标记本身，此建议符合通用生物学常识。  - **修正前**: `{"text": "779 bp band", "label": "MRK"}`  - **修正后**: 实体被移除。
- **采纳建议**: 将关系 `(LW7 marker, AFF, rf4)` 的类型从 `AFF` 修改为 `LOI`。  - **理由**: 审查报告指出，标记是用于识别或定位基因，而非直接影响其功能。`LOI` (定位/关联) 更准确地描述了这种关系。  - **修正前**: `{"head": "LW7 marker", "label": "AFF", "tail": "rf4"}`  - **修正后**: `{"head": "LW7 marker", "label": "LOI", "tail": "rf4"}`
## Sample 5 (Index 4)
- **采纳建议**: 将实体 `related QTL` 修正为 `QTL`。  - **理由**: 遵循“核心名词”原则，剔除不必要的修饰词 `related`，使实体边界更精确。  - **修正前**: `{"text": "related QTL", "start": 171, "end": 181}`  - **修正后**: `{"text": "QTL", "start": 179, "end": 182}`
## Sample 6 (Index 5)
- **部分采纳/不适用**: 审查建议移除 `V1` 实体。  - **理由**: 经核查，当前 `verified/chunk_008.json` 的条目5中并不包含 `V1` 实体。该建议可能针对早期版本，故在此版本中不适用。未做修改。
## Sample 7 & 8 (Index 6 & 7)
- **未采纳建议**: 审查建议拆分 `sorghum genotypes` 和 `sorghum genotype`。  - **理由**: 经核查，`verified/chunk_008.json` 的条目6和7中已将 `sorghum` 和 `genotypes`/`genotype` 分别标注，不存在需要拆分的复合实体。审查建议不适用。
## Sample 9 (Index 8)
- **采纳建议**: 移除关系 `(Stay-green, AFF, drought tolerance)`。  - **理由**: 根据权威依据 `[NY/T 2645-2014]`，`Stay-green` (叶片持绿性) 是耐旱性状的一种表现，两者为同义或包含关系，而非影响关系。  - **修正前**: `{"head": "Stay-green", "label": "AFF", "tail": "drought tolerance"}`  - **修正后**: 关系被移除。
