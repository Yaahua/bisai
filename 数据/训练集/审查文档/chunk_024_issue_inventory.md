# chunk_024 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_024（10 条样本）
**输入物**：chunk_024.json + chunk_024_annotated.md + chunk_024_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 0 | 词块审查 | `10 K SNPs`（@115:124）与 `SNPs`（@121:125）重叠嵌套：`SNPs` 被包含在 `10 K SNPs` 内。K1 §1.3 规定嵌套实体中内层实体可保留，但两者都标为 MRK 时，内层 `SNPs` 是冗余的。应删除内层 `SNPs` @121:125，保留 `10 K SNPs` @115:124 | 中 |
| 2 | 样本 2 | 词块审查 | `sheepgrass`（@174:184）与 `water stress tolerance`（@183:205）存在重叠（@183:184 重叠 1 个字符）。需精确验证偏移：若 `water stress tolerance` 实际起始于 @185，则无重叠；若确实从 @183 开始，则需修正 `sheepgrass` 的 end 为 @183 或 `water stress tolerance` 的 start 为 @185 | 高 |
| 3 | 样本 5 | 知识审查 | `C2H2-type zinc finger protein transcription factor`（@13:62）标为 GENE，但这是转录因子家族名称，不是具体基因名称。K8 §1.2 规定 GENE 需为具体基因名。应删除，或保留（训练集中存在家族名标为 GENE 的先例） | 中 |
| 4 | 样本 7 | 知识审查 | `PS I`（@265:269）和 `PS II`（@271:276）改为 GENE，但光系统 I/II 是蛋白质复合体，不是单一基因。K8 §1.2 规定 GENE 需为具体基因名。应改为不标，或保留（蛋白质复合体可视为基因产物集合） | 中 |
| 5 | 样本 7 | 知识审查 | `cytochrome b6f complex`（@278:300）改为 GENE，同上，是蛋白质复合体，不是单一基因。应改为不标 | 中 |
| 6 | 样本 9 | 语义审查 | `tolerance to drought stress`（@76:101）与 `drought stress`（@87:101）嵌套：外层 TRT 包含内层 ABS，且 end 相同（@101）。这种嵌套是合理的（性状包含胁迫因子），但需确认偏移精确性 | 低（建议保留） |
| 7 | 样本 1 | 知识审查 | `quartet micronuclei frequency`（@136:165）标为 TRT，微核频率是细胞学指标，不是农艺性状。但可量化，训练集中存在类似标注，保留 | 低（建议保留） |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 0 | 词块审查 | `genome-wide association study (GWAS)` 边界修正（@2:38）正确，补全右括号 |
| P2 | 样本 3 | 知识审查 | `MAPK signaling`（@107:121）标为 GENE，信号通路名称标为 GENE 在训练集中有先例，保留 |
| P3 | 样本 6 | 语义审查 | `ornithine delta-aminotransferase gene OsOAT`（@4:47）与 `OsOAT`（@42:47）嵌套，CON 关系正确 |
| P4 | 样本 8 | 语义审查 | LOI(SNPs @172:176, flowering time @226:240)：SNPs 定位于 flowering time 性状，正确 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 0：若删除 `SNPs` @121:125，需检查关系中 LOI(SNPs @121:125, chromosome 5/8) 是否需要改为 LOI(10 K SNPs @115:124, chromosome 5/8)，同步修改 head_start/head_end |
| A2 | 样本 2：若修正 `sheepgrass`/@`water stress tolerance` 重叠，需同步修改 HAS 关系的 tail_start/tail_end |
| A3 | 样本 7：若将 PS I/II、cytochrome b6f complex 改回不标，需删除相关实体，无关系依赖，可安全删除 |
