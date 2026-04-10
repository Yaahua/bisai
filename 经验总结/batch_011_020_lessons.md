# 批次 011–020 修订复盘与技能更新要点

## 一、范围说明

本批次复盘仅覆盖 `chunk_011` 至 `chunk_020`。用户已明确取消“把前 10 块（100 条）训练数据对应的错误清单也同步修订后再统一上传”这一步，因此后续补齐、同步与上传准备均不得再自动扩展到 `chunk_001` 至 `chunk_010`。

## 二、本批次沉淀出的关键教训

| 类别 | 现象 | 约束/改进动作 |
|------|------|------|
| 业务范围 | 曾出现把当前批次任务外扩到前 10 块的倾向 | 启动时先锁定用户批准的 chunk 区间；超范围事项只能登记，不自动执行 |
| 流程控制 | 011–020 批次早段缺少部分 `issue_inventory` 文档 | 全量修订前必须先补齐 `issue_inventory`，再进入数据回写与仓库同步 |
| 文档齐备 | 个别块在审查链条中缺少初标说明或问题清单 | 审查前先核对 `chunk_XXX.json`、`chunk_XXX_review.md`、`chunk_XXX_issue_inventory.md` 是否齐备 |
| 关系锚点 | 同一实体在文中多次出现时，关系容易借错 occurrence | 修关系时必须以真实 occurrence 为准，并同步更新全部 anchor 字段 |
| 并列结构 | 并列实体缺失常伴随并列关系缺失 | 发现并列 `TRT` 漏标时，要同步检查与同一 head 相连的整组关系 |
| 语义过标 | 来源性描述或材料分组词容易被过度实体化/关系化 | `Israeli accession` 这类来源性短语默认不标 `VAR`；`salt-sensitive accessions` 不应机械提升为 `HAS(CROP, TRT)` |

## 三、典型实例

| chunk | 问题 | 修订原则 |
|------|------|------|
| 011 | 两条 `AFF` 关系将后文真正起效的 `SbMYBHv33` 锚到前文第一次出现处 | 关系必须绑定到承担语义的真实 mention |
| 012 | 将 accession 分组词 `salt-sensitive` / `salt-tolerant` 直接提升为 `foxtail millet` 的整体性状 | 先判断性状修饰对象是材料群体还是作物整体 |
| 012 | 漏标 `superoxide dismutase`、`peroxidase`、`catalase activities`，并连带漏掉 3 条 `FtNAC31 -> TRT` `AFF` | 并列实体和并列关系必须成组补齐 |
| 013 | 将 `Israeli accession` 误当成稳定 `VAR` | 来源性描述默认不实体化，除非具备可复核编号或专名 |
| 013 | `soybean` / `soybeans` 出现竞争边界，关系借错单数锚点 | 删除竞争实体后，关系需改绑真实 occurrence |

## 四、已完成的技能更新

本轮已将上述经验同步写入以下技能文件：

| 技能包 | 已更新文件 | 更新主题 |
|------|------|------|
| `MGBIE标注技能` | `SKILL.md` | 新增“范围锁定”规则，禁止未经确认扩展到其他批次 |
| `MGBIE标注技能` | `参考资料/error_patterns_training.md` | 新增来源性描述、材料分组过度提升、重复 mention 锚点借位、并列关系漏标、批次边界防呆等经验 |
| `MGBIE审查技能` | `SKILL.md` | 新增“范围锁定”规则，要求审查补齐与同步动作严格受用户批准区间约束 |
| `MGBIE审查技能` | `参考资料/error_patterns_training.md` | 与 annotator 侧保持一致，补入同批次流程与技术教训 |

## 五、后续同步原则

后续若进行仓库同步或统一上传准备，只同步以下内容：

1. `chunk_011` 至 `chunk_020` 的修订成果与配套文档；
2. 两个 MGBIE 技能包中已更新的 `SKILL.md` 与 `参考资料/error_patterns_training.md`；
3. 本复盘文件。

对于 `chunk_001` 至 `chunk_010`，除非用户再次明确授权，否则不纳入当前批次处理范围。
