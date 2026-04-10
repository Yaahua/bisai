# chunk_023 问题清单 (issue_inventory.md)

**审查时间**：2026-04-10
**审查范围**：chunk_023（10 条样本）
**输入物**：chunk_023.json + chunk_023_annotated.md + chunk_023_review.md

---

## 一、已确认问题

| # | 样本 | 维度 | 问题描述 | 严重性 |
|---|------|------|----------|--------|
| 1 | 样本 0 | 语义审查 | `qDTH2` AFF `late heading` 与 `qDTH2` LOI `late heading` 同时存在（@32:37→@45:57），形成重复关系。QTL 与性状的关系应统一为 LOI，不应同时存在 AFF 和 LOI | 高 |
| 2 | 样本 1 | 语义审查 | LOI(QTL @153:156, drought @75:82)：QTL 定位于 drought（ABS），但 LOI 的 tail 应为 TRT 或 CHR，不应为 ABS。原文说 "identify QTL for drought tolerance"，tail 应为 `drought tolerance`（TRT），而非 `drought`（ABS） | 高 |
| 3 | 样本 5 | 词块审查 | `a PH QTL on chromosome 6`（@435:459）标为 QTL，边界包含 "a"、"on chromosome 6" 等修饰词。应缩减为 `PH QTL`（@437:443）或更短形式。但训练集中存在此类完整标注，且该实体与 `chromosome 6` 形成嵌套，保留 | 低（建议保留） |
| 4 | 样本 5 | 语义审查 | USE(sorghum mini core (MC) collection, 6,094,317 SNP markers)：K8 §2.6 规定 USE head 必须是 VAR。此处 head 为 `sorghum mini core (MC) collection`（VAR），tail 为 `6,094,317 SNP markers`（MRK）。K8 §2.6 规定 USE(VAR, BM)，tail 应为 BM，不能为 MRK | 高 |
| 5 | 样本 5 | 语义审查 | USE(sorghum reference set (RS), 265,500 SNPs)：同上，tail 为 MRK，违反 USE 关系约束 | 高 |
| 6 | 样本 6 | 知识审查 | `Avr proteins`（@280:292）标为 GENE，但 "Avr proteins" 是蛋白质类别名（Avirulence proteins），不是具体基因名。应删除或改为不标 | 中 |
| 7 | 样本 3 | 语义审查 | AFF(Striga @133:139 BIS, SL production @27:40 TRT)：关系方向为 BIS→TRT，表示病虫害影响性状。但原文说的是 "lower SL production had delayed or reduced Striga emergence rates"，因果方向是 SL production 影响 Striga emergence，而非 Striga 影响 SL production。应改为 AFF(SL production, Striga emergence rates) | 高 |

---

## 二、潜在问题

| # | 样本 | 维度 | 潜在问题描述 |
|---|------|------|------------|
| P1 | 样本 4 | 知识审查 | `raffinose family oligosaccharides`（@367:399）标为 TRT，但这是代谢物名称，不是性状。考虑到原文说 "up-regulation of raffinose family oligosaccharides"（上调），可视为代谢物含量性状，保留 TRT |
| P2 | 样本 4 | 知识审查 | `gamma-aminobutyric acid`（@422:444）标为 TRT，同上，原文说 "down-regulation of the gamma-aminobutyric acid catalytic pathway"，这是代谢通路，不是代谢物含量。应考虑改为不标或标为 TRT（代谢通路活性）。保留 |
| P3 | 样本 5 | 词块审查 | `6,094,317 SNP markers`（@253:274）和 `265,500 SNPs`（@289:301）包含数量词，但训练集中存在此类标注，保留 |
| P4 | 样本 7 | 拆分审查 | `Tillering`（@43:52）和 `tillering`（@22:31）是同一性状的两次出现，分别标注正确 |
| P5 | 样本 8 | 语义审查 | OCI(YPC @66:69, 15 DAP @24:30)：性状 YPC 在 15 DAP 时期发生，OCI 关系（性状在某时期出现）正确 |

---

## 三、关联问题 / 需要同步检查的字段

| # | 关联问题 |
|---|---------|
| A1 | 样本 0：若删除 AFF(qDTH2, late heading) 和 AFF(qDTH7, extremely late heading)，保留 LOI，需同步修改关系列表 |
| A2 | 样本 1：若修正 LOI(QTL, drought) → LOI(QTL, drought tolerance)，需同步修改 tail_start=157、tail_end=172、tail_type=TRT |
| A3 | 样本 3：若修正 AFF 方向，需删除 AFF(Striga, SL production)，新增 AFF(SL production, Striga emergence rates)，同步修改 head/tail 锚点 |
| A4 | 样本 5：若删除 USE(VAR, MRK) 关系 ×2，需确认无其他关系依赖这两个 MRK 实体 |
| A5 | 样本 6：若删除 `Avr proteins` 实体，需检查是否有关系依赖它（当前关系列表中无依赖，可安全删除） |
