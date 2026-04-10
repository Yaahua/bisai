**数据块编号**: chunk_020
**审查时间**: 2026-04-10 18:18:00

## 1. 审查概况

| 指标 | 结果 |
| --- | --- |
| 总条数 | 10 |
| 发现错误/遗漏条数 | 4 |
| 主要错误类型分布 | 泛化基因集合/基因群实体 3 处；非育种方法实体误标为 BM 1 处 |

本块在 `AFLP markers—sht1 locus`、`CROSS—VAR`、`SNP—SiDREB2—dehydration tolerance` 等结构上整体较稳，说明初标已能较好处理标记、杂交群体和胁迫响应场景。统一审查后发现，问题仍主要集中在**泛化 GENE 实体保留过宽**，以及**把一般农艺活动误收入 BM** 两类情形。这些问题与 chunk_017、chunk_019 的审查结果形成连续证据，宜在全量修正时一并统一。

## 2. 详细审查意见与权威依据

### 问题 1: `drought-inducible transcription factors` 与 `drought responsive DEGs` 都属于泛化基因集合，不宜作为最终 GENE 实体保留

- **错误位置**: Sample 1
- **原分类结果**: 将 `drought-inducible transcription factors`、`drought responsive DEGs` 均标为 **GENE**，并建立两条 `common buckwheat -> GENE (CON)` 关系。
- **修改建议**: 建议删除上述两个 GENE 实体及其 `CON` 关系；若需保留句中稳定对象，可仅保留 `common buckwheat` 与 `drought stress response`，但当前文本并未给出稳定命名成员，因此更稳妥的最终结果是只清理泛化 GENE 而不扩增新关系。
- **权威依据**: 按 **[CGSNL-2011]**，可稳定识别的基因通常具有明确命名形式；而 `transcription factors`、`DEGs` 在此句中只是功能性集合表达，不是可直接训练的单基因/稳定基因名。结合此前 chunk_017 与 chunk_019 的统一规则，凡出现 `genes / DEGs / transcription factors / responsive genes` 等集合性表述，而没有给出独立稳定命名成员时，均不应进入最终 **GENE** 标注。

### 问题 2: `barley genes or orthologs` 是概括性集合短语，不应与具体作物名重叠保留为 GENE

- **错误位置**: Sample 9
- **原分类结果**: 将 `barley genes or orthologs` 标为 **GENE**，并同时保留与其中重叠的 `barley` (CROP) 及 `CON(CROP, GENE)`。
- **修改建议**: 建议删除 `barley genes or orthologs` 实体及其 `CON` 关系，仅保留 `barley` 与 `barley grain size and weight` 等稳定对象，以及 `QTL hotspot regions` 的定位/性状关系。
- **权威依据**: 该短语不是标准基因命名，而是“候选基因或同源基因集合”的总称。若保留为 GENE，会把“具体基因实体”与“来源描述/集合性说明”混在一起，且与前部 `barley` 构成重叠，破坏边界一致性。根据审查技能的最大共识与命名优先原则，此类“X genes or orthologs”应视作说明性短语而非最终实体。

### 问题 3: `Genes determining flowering` 为功能描述性泛称，不宜作为最终 GENE 实体

- **错误位置**: Sample 10
- **原分类结果**: 将 `Genes determining flowering` 标为 **GENE**，并保留 `AFF(GENE, flowering time)`。
- **修改建议**: 建议删除该 GENE 实体与对应关系，仅保留 `Early maturity`、`flowering time`、`crop maturity`、`yield` 等性状链条；若后续确需保留上游遗传因素，也应等待出现稳定命名基因后再标。
- **权威依据**: 该表达只是“决定开花的基因”这一功能性概括，并非可复现的基因名。继续保留会把生物学常识性描述误学成具体基因实体。结合前述跨块规则，所有“Genes determining... / genes related to... / responsive genes”这类功能概括式表达，默认不进入最终 **GENE** 标签。

### 问题 4: `multiple cropping` 不是育种方法，当前标为 BM 过宽

- **错误位置**: Sample 10
- **原分类结果**: 将 `multiple cropping` 标为 **BM**。
- **修改建议**: 建议删除该实体，不再纳入最终标注。
- **权威依据**: `multiple cropping` 指复种/多熟制这一农业种植制度或生产方式，不属于分子育种、遗传分析、筛选鉴定或表型调查的“方法”本体。按 **[SUN-2019]** 与技能中的 BM 使用范围，BM 应优先对应测序、分型、PCR、图谱构建、QTL mapping、标准评价体系等程序性方法，而不是一般农艺制度。将其标为 BM 会显著拉宽标签边界，不利于训练集稳定性。

## 3. 审查总结与后续建议

本块再次证明，**泛化基因集合**是当前初标阶段最稳定的误差源。建议在全量修正时执行以下统一规则：

| 规则 | 执行动作 |
| --- | --- |
| 出现 `genes`、`orthologs`、`DEGs`、`transcription factors`、`genes determining...` 等集合/功能性表达，且无稳定命名成员 | 默认删除，不入最终 GENE |
| 术语属于种植制度、栽培方式或一般农业安排，而非分析检测流程 | 不标 BM |
| 已存在稳定命名基因/位点/标记时 | 优先保留命名实体，删除概括性上位短语 |

据此，chunk_020 在进入全量修正时，应重点清理 Sample 1、Sample 9、Sample 10 的泛化实体，并同步更新跨块经验条目。
