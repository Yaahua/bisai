#!/usr/bin/env python3
"""
全量修正脚本（完整版）
策略：直接读取各块 annotated.md 中已解析好的 entities/relations JSON 块，
      再叠加 audit.md 的必须修改项（删除非法关系/实体），
      最终生成修订后 JSON 文件写入 修订结果/ 目录。

由于 annotated.md 已包含完整的修订后标注（含新增/修改/删除），
本脚本的主要工作是：
1. 从原始 JSON 读取 text 和 id 字段
2. 用 annotated.md 中解析的 entities/relations 替换原始标注
3. 叠加 audit 修正（删除非法关系）
4. 输出最终 JSON
"""

import json
import re
import os
import copy

BASE_DIR = "/home/ubuntu/bisai_clone/数据/训练集"
ORIG_DIR = os.path.join(BASE_DIR, "原始切分块")
ANNOTATED_DIR = os.path.join(BASE_DIR, "标注结果")
RESULT_DIR = os.path.join(BASE_DIR, "修订结果")
os.makedirs(RESULT_DIR, exist_ok=True)


def load_original_json(chunk_id):
    path = os.path.join(ORIG_DIR, f"{chunk_id}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_json_blocks(md_content):
    """从 markdown 内容中提取所有 ```json ... ``` 块，按顺序返回"""
    pattern = r"```json\s*([\s\S]*?)```"
    blocks = re.findall(pattern, md_content)
    return blocks


def parse_annotated_md(chunk_id):
    """
    解析 annotated.md，提取每个样本的 entities 和 relations。
    返回列表：[(entities_list, relations_list), ...]，按样本顺序。
    """
    path = os.path.join(ANNOTATED_DIR, f"{chunk_id}_annotated.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 按样本分割
    # 每个样本以 "## 样本 N" 开头，最后是 "## 修订汇总"
    sample_pattern = r"## 样本 (\d+)([\s\S]*?)(?=## 样本 \d+|## 修订汇总|$)"
    samples = re.findall(sample_pattern, content)

    result = []
    for sample_idx, sample_content in samples:
        # 提取该样本内的所有 json 块
        json_blocks = extract_json_blocks(sample_content)
        entities = []
        relations = []
        if len(json_blocks) >= 1:
            try:
                entities = json.loads(json_blocks[0])
            except json.JSONDecodeError as e:
                print(f"  警告: {chunk_id} 样本{sample_idx} entities 解析失败: {e}")
        if len(json_blocks) >= 2:
            try:
                relations = json.loads(json_blocks[1])
            except json.JSONDecodeError as e:
                print(f"  警告: {chunk_id} 样本{sample_idx} relations 解析失败: {e}")
        result.append((entities, relations))

    return result


def apply_audit_corrections(sample_idx, entities, relations, chunk_id):
    """
    依据 audit.md 的必须修改项，对单个样本的 entities/relations 进行修正。
    返回修正后的 (entities, relations)。
    """
    entities = copy.deepcopy(entities)
    relations = copy.deepcopy(relations)

    def delete_relations_by_type(head_type=None, tail_type=None, label=None):
        nonlocal relations
        new_rels = []
        for r in relations:
            match = True
            if head_type and r.get("head_type") != head_type:
                match = False
            if tail_type and r.get("tail_type") != tail_type:
                match = False
            if label and r.get("label") != label:
                match = False
            if not match:
                new_rels.append(r)
        deleted = len(relations) - len(new_rels)
        if deleted > 0:
            print(f"    [{chunk_id} 样本{sample_idx}] 删除 {label}({head_type},{tail_type}) ×{deleted}")
        relations = new_rels

    def delete_entity_by_offset(start, end):
        nonlocal entities
        new_ents = [e for e in entities if not (e.get("start") == start and e.get("end") == end)]
        deleted = len(entities) - len(new_ents)
        if deleted > 0:
            print(f"    [{chunk_id} 样本{sample_idx}] 删除实体 @{start}:{end} ×{deleted}")
        entities = new_ents

    def delete_relation_by_offsets(head_start, head_end, tail_start, tail_end, label):
        nonlocal relations
        new_rels = []
        for r in relations:
            if (r.get("head_start") == head_start and r.get("head_end") == head_end and
                    r.get("tail_start") == tail_start and r.get("tail_end") == tail_end and
                    r.get("label") == label):
                print(f"    [{chunk_id} 样本{sample_idx}] 删除嵌套关系 {label}(@{head_start}:{head_end}, @{tail_start}:{tail_end})")
                continue
            new_rels.append(r)
        relations = new_rels

    # ============================================================
    # chunk_027 修正规则
    # ============================================================
    if chunk_id == "chunk_027":
        if sample_idx == 4:
            delete_relations_by_type("CROSS", "VAR", "CON")
            delete_relations_by_type("QTL", "MRK", "LOI")
        elif sample_idx == 7:
            delete_relations_by_type("CROSS", "CROSS", "CON")
        elif sample_idx == 1:
            delete_relations_by_type("GENE", "ABS", "AFF")
        elif sample_idx == 3:
            delete_relations_by_type("GENE", "GENE", "AFF")
        elif sample_idx == 5:
            delete_relations_by_type("CROP", "BM", "USE")

    # ============================================================
    # chunk_028 修正规则
    # ============================================================
    elif chunk_id == "chunk_028":
        if sample_idx == 2:
            delete_relations_by_type("ABS", "VAR", "AFF")
        elif sample_idx == 5:
            delete_relations_by_type("CROP", "ABS", "AFF")
        elif sample_idx == 9:
            delete_entity_by_offset(144, 149)
        elif sample_idx == 6:
            delete_relation_by_offsets(142, 154, 142, 164, "AFF")

    # ============================================================
    # chunk_029 修正规则
    # ============================================================
    elif chunk_id == "chunk_029":
        if sample_idx == 1:
            delete_relations_by_type("ABS", "CROSS", "AFF")
        elif sample_idx == 3:
            delete_relations_by_type("ABS", "GENE", "AFF")
        elif sample_idx == 6:
            delete_relations_by_type("GENE", "GENE", "AFF")
        elif sample_idx == 9:
            delete_relations_by_type("TRT", "TRT", "CON")
        elif sample_idx == 7:
            delete_relation_by_offsets(48, 64, 48, 74, "AFF")
            delete_relation_by_offsets(340, 351, 340, 361, "AFF")
        elif sample_idx == 5:
            delete_relations_by_type("MRK", "CHR", "LOI")
        elif sample_idx == 8:
            delete_relation_by_offsets(122, 126, 122, 136, "AFF")

    # ============================================================
    # chunk_030 修正规则
    # ============================================================
    elif chunk_id == "chunk_030":
        if sample_idx == 0:
            delete_relations_by_type("ABS", "GENE", "AFF")
        elif sample_idx == 3:
            delete_relations_by_type("BM", "TRT", "USE")
        elif sample_idx == 4:
            delete_relations_by_type("CROSS", "CROP", "CON")
        elif sample_idx == 5:
            delete_relations_by_type("BM", "GENE", "USE")
        elif sample_idx == 7:
            delete_relations_by_type("MRK", "QTL", "LOI")
        elif sample_idx == 8:
            delete_relations_by_type("GENE", "GENE", "AFF")

    return entities, relations


def process_chunk(chunk_id):
    """处理单个 chunk，生成修订后 JSON"""
    print(f"\n处理 {chunk_id}...")

    # 加载原始 JSON（获取 text、id 等字段）
    orig_data = load_original_json(chunk_id)

    # 解析 annotated.md（获取修订后的 entities/relations）
    annotated = parse_annotated_md(chunk_id)

    if len(annotated) != len(orig_data):
        print(f"  警告: {chunk_id} annotated 样本数({len(annotated)}) != 原始样本数({len(orig_data)})")

    result = []
    for i, orig_sample in enumerate(orig_data):
        new_sample = copy.deepcopy(orig_sample)

        if i < len(annotated):
            entities, relations = annotated[i]
            # 叠加 audit 修正
            entities, relations = apply_audit_corrections(i, entities, relations, chunk_id)
            new_sample["entities"] = entities
            new_sample["relations"] = relations
        else:
            print(f"  警告: {chunk_id} 样本{i} 无 annotated 数据，保留原始标注")

        result.append(new_sample)

    # 保存结果
    out_path = os.path.join(RESULT_DIR, f"{chunk_id}_corrected.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  已保存: {out_path}")

    # 统计
    total_entities = sum(len(s.get("entities", [])) for s in result)
    total_relations = sum(len(s.get("relations", [])) for s in result)
    print(f"  统计: {len(result)} 条样本，{total_entities} 个实体，{total_relations} 条关系")

    return result


def main():
    chunks = [f"chunk_0{i:02d}" for i in range(21, 31)]
    all_results = {}

    for chunk_id in chunks:
        try:
            result = process_chunk(chunk_id)
            all_results[chunk_id] = result
        except Exception as e:
            print(f"  错误: {chunk_id} 处理失败: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n全量修正完成，共处理 {len(all_results)} 个块。")
    print(f"结果已保存到: {RESULT_DIR}")


if __name__ == "__main__":
    main()
