# chunk_023 审查报告 (audit.md)

**审查时间**：2026-04-10
**审查员**：mgbie-review-agent
**输入物**：chunk_023.json + chunk_023_annotated.md + chunk_023_review.md

---

## 审查概况表

| 维度 | 问题数 | 严重（需修改） | 中等（建议修改） | 低（确认保留） |
|------|--------|--------------|----------------|--------------|
| 拆分审查 | 1 | 0 | 0 | 1 |
| 语义审查 | 5 | 4 | 0 | 1 |
| 词块审查 | 1 | 0 | 0 | 1 |
| 知识审查 | 2 | 0 | 1 | 1 |
| **合计** | **9** | **4** | **1** | **4** |

---

## 详细审查结果

### 问题 1：样本 0 — AFF/LOI 重复关系（语义审查，高）

**错误位置**：样本 0，qDTH2 同时存在 AFF(qDTH2, late heading) 和 LOI(qDTH2, late heading)

**问题描述**：QTL 与性状的关系不应同时存在 AFF 和 LOI。AFF 表示影响，LOI 表示定位/关联。对于 QTL 与性状，训练数据中两种关系均有出现（error_patterns §1.1），但同一对实体不应同时建立两种关系。

**修改建议**：删除 AFF(qDTH2, late heading) 和 AFF(qDTH7, extremely late heading)，保留 LOI 关系。或删除 LOI，保留 AFF。参考训练集中同类样本的处理方式，优先保留 LOI（QTL→TRT 定位关系更常见）。

**权威依据**：K8 §2.3 AFF vs §2.5 LOI；error_patterns §1.1（LOI: QTL→TRT 频次 30，保留）

**联动风险**：需同步删除 2 条 AFF 关系，保留 2 条 LOI 关系。

---

### 问题 2：样本 1 — LOI tail 类型错误（语义审查，高）

**错误位置**：样本 1，LOI(QTL @153:156, drought @75:82 ABS)

**问题描述**：LOI 关系的 tail 为 `drought`（ABS），但 K8 §2.5 规定 LOI 的 tail 应为 TRT 或 CHR，不能为 ABS。原文说 "identify QTL for drought tolerance"，正确的 tail 应为 `drought tolerance`（TRT @157:172）。

**修改建议**：将 LOI 关系的 tail 改为 `drought tolerance`（tail_start=157, tail_end=172, tail_type=TRT）。

**权威依据**：K8 §2.5 LOI（tail: TRT/CHR）；K2 §1.3（关系类型约束）

**联动风险**：需同步修改关系的 tail_start/tail_end/tail_type。

---

### 问题 3：样本 3 — AFF 方向错误（语义审查，高）

**错误位置**：样本 3，AFF(Striga @133:139 BIS, SL production @27:40 TRT)

**问题描述**：原文为 "Edited lines with lower SL production had delayed or reduced Striga emergence rates"，因果方向是 SL production（性状）影响 Striga emergence rates（性状），而非 Striga（病虫害）影响 SL production。当前 AFF 方向颠倒。

**修改建议**：删除 AFF(Striga, SL production)，新增 AFF(SL production @27:40 TRT, Striga emergence rates @133:155 TRT)。

**权威依据**：K2 §1.1（AFF 方向：head 为影响发起方）；error_patterns §3.1（AFF 方向颠倒）

**联动风险**：需同步修改 head/tail 实体及其锚点。

---

### 问题 4：样本 5 — USE 关系 tail 类型错误（语义审查，高×2）

**错误位置**：样本 5，USE(sorghum mini core (MC) collection, 6,094,317 SNP markers) 和 USE(sorghum reference set (RS), 265,500 SNPs)

**问题描述**：K8 §2.6 规定 USE 关系为 USE(VAR, BM)，tail 必须是 BM（育种方法）。此处 tail 为 MRK（分子标记），违反关系类型约束。

**修改建议**：删除这 2 条 USE 关系。若需要表达"使用标记进行关联分析"，应通过 BM 实体（Association mapping）建立关系，而非直接 USE(VAR, MRK)。

**权威依据**：K8 §2.6 USE（head: VAR, tail: BM）；K2 §2.1（关系类型约束）

**联动风险**：删除 2 条关系，不影响其他实体。

---

### 问题 5：样本 6 — `Avr proteins` 标签（知识审查，中）

**错误位置**：样本 6，`Avr proteins`（@280:292）GENE

**问题描述**：`Avr proteins` 是无毒蛋白（Avirulence proteins）的类别名，不是具体基因名称。K8 §1.2 规定 GENE 需为具体基因名。

**修改建议**：删除 `Avr proteins` 实体。

**权威依据**：K8 §1.2 GENE（需为具体基因名）；error_patterns §2.3（蛋白质类别名不标为 GENE）

**联动风险**：当前关系列表中无依赖 `Avr proteins` 的关系，可安全删除。

---

### 问题 6：样本 5 — `a PH QTL on chromosome 6` 边界（词块审查，低）

**审查结论**：边界包含修饰词，但与 `chromosome 6` 形成嵌套，且训练集中存在此类完整标注。**确认保留**。

**权威依据**：error_patterns §2.2（训练集先例优先）

---

### 问题 7：样本 1 — `semi-arid tropics` 标签（语义审查，低）

**审查结论**：`semi-arid tropics` 标为 ABS（气候环境背景），K7 §2.6 允许将气候环境视为非生物胁迫背景。**确认保留**。

---

## 总结与改进建议

**必须修改（4 项）**：
1. 样本 0：删除 AFF(qDTH2/qDTH7, TRT)，保留 LOI（重复关系）
2. 样本 1：修正 LOI tail 为 `drought tolerance`（TRT）
3. 样本 3：修正 AFF 方向，改为 AFF(SL production, Striga emergence rates)
4. 样本 5：删除 USE(VAR, MRK) ×2

**建议修改（1 项）**：
5. 样本 6：删除 `Avr proteins` 实体（蛋白质类别名）

**确认保留（4 项）**：`a PH QTL` 边界、`semi-arid tropics` ABS、代谢物标为 TRT、数量词 QTL 标注
