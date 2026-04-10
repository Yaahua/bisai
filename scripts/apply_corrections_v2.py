#!/usr/bin/env python3
"""
全量修正脚本 v2：包含所有残留问题的修正规则（基于双重验证结果）。
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
    pattern = r"```json\s*([\s\S]*?)```"
    blocks = re.findall(pattern, md_content)
    return blocks


def parse_annotated_md(chunk_id):
    path = os.path.join(ANNOTATED_DIR, f"{chunk_id}_annotated.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sample_pattern = r"## 样本 (\d+)([\s\S]*?)(?=## 样本 \d+|## 修订汇总|$)"
    samples = re.findall(sample_pattern, content)

    result = []
    for sample_idx, sample_content in samples:
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
    entities = copy.deepcopy(entities)
    relations = copy.deepcopy(relations)

    def del_rels(head_type=None, tail_type=None, label=None):
        nonlocal relations
        new_rels = []
        for r in relations:
            match = True
            if head_type and r.get("head_type") != head_type: match = False
            if tail_type and r.get("tail_type") != tail_type: match = False
            if label and r.get("label") != label: match = False
            if not match:
                new_rels.append(r)
        deleted = len(relations) - len(new_rels)
        if deleted > 0:
            print(f"    [{chunk_id} 样本{sample_idx}] 删除 {label}({head_type},{tail_type}) ×{deleted}")
        relations = new_rels

    def del_ent(start, end):
        nonlocal entities
        new_ents = [e for e in entities if not (e.get("start") == start and e.get("end") == end)]
        deleted = len(entities) - len(new_ents)
        if deleted > 0:
            print(f"    [{chunk_id} 样本{sample_idx}] 删除实体 @{start}:{end} ×{deleted}")
        entities = new_ents

    def del_rel_offset(hs, he, ts, te, label):
        nonlocal relations
        new_rels = []
        for r in relations:
            if (r.get("head_start") == hs and r.get("head_end") == he and
                    r.get("tail_start") == ts and r.get("tail_end") == te and
                    r.get("label") == label):
                print(f"    [{chunk_id} 样本{sample_idx}] 删除 {label}(@{hs}:{he}, @{ts}:{te})")
                continue
            new_rels.append(r)
        relations = new_rels

    # ============================================================
    # chunk_021
    # ============================================================
    if chunk_id == "chunk_021":
        if sample_idx == 3:
            # AFF(ABS,GENE): heat shock -> SnRK1
            del_rels("ABS", "GENE", "AFF")
        elif sample_idx == 4:
            # AFF(GENE,ABS): SbNAC56 -> abiotic stresses
            del_rels("GENE", "ABS", "AFF")
        elif sample_idx == 6:
            # CON(CROP,CROSS): sorghum -> F-9:10 sorghum RILs
            del_rels("CROP", "CROSS", "CON")
            # LOI(QTL,BIS): QTLs -> B. fusca / C. partellus
            del_rels("QTL", "BIS", "LOI")
        elif sample_idx == 7:
            # LOI(MRK,CHR) and LOI(MRK,TRT): SNPs -> various
            del_rels("MRK", "CHR", "LOI")
            del_rels("MRK", "TRT", "LOI")
        elif sample_idx == 8:
            # LOI(MRK,TRT)×2, LOI(MRK,CHR)×2, CON(QTL,MRK)
            del_rels("MRK", "TRT", "LOI")
            del_rels("MRK", "CHR", "LOI")
            del_rels("QTL", "MRK", "CON")

    # ============================================================
    # chunk_022
    # ============================================================
    elif chunk_id == "chunk_022":
        if sample_idx == 0:
            del_rels("MRK", "GENE", "LOI")
        elif sample_idx == 1:
            del_rels("QTL", "GENE", "LOI")
        elif sample_idx == 6:
            del_rels("CROP", "BM", "USE")
        elif sample_idx == 7:
            del_rels("MRK", "TRT", "LOI")
        elif sample_idx == 9:
            del_rels("VAR", "QTL", "CON")
            del_rels("MRK", "QTL", "LOI")

    # ============================================================
    # chunk_023
    # ============================================================
    elif chunk_id == "chunk_023":
        if sample_idx == 1:
            del_rels("QTL", "ABS", "LOI")
        elif sample_idx == 5:
            del_rels("VAR", "MRK", "USE")
        elif sample_idx == 6:
            del_rels("MRK", "CHR", "LOI")
            del_rels("MRK", "TRT", "LOI")

    # ============================================================
    # chunk_024
    # ============================================================
    elif chunk_id == "chunk_024":
        if sample_idx == 0:
            del_rels("MRK", "CHR", "LOI")
        elif sample_idx == 6:
            del_rels("CROP", "CROP", "CON")
        elif sample_idx == 8:
            del_rels("MRK", "TRT", "LOI")

    # ============================================================
    # chunk_025
    # ============================================================
    elif chunk_id == "chunk_025":
        if sample_idx == 2:
            del_rels("CROP", "GENE", "CON")
        elif sample_idx == 3:
            del_rels("BM", "CROSS", "USE")
            del_rels("CROSS", "CROSS", "CON")
            del_rels("CROSS", "VAR", "CON")
        elif sample_idx == 4:
            del_rels("MRK", "TRT", "LOI")
            del_rels("MRK", "CHR", "LOI")
        elif sample_idx == 5:
            del_rels("MRK", "CHR", "LOI")

    # ============================================================
    # chunk_026
    # ============================================================
    elif chunk_id == "chunk_026":
        if sample_idx == 5:
            del_rels("QTL", "MRK", "LOI")
        elif sample_idx == 8:
            del_rels("TRT", "TRT", "CON")
            del_rels("VAR", "VAR", "AFF")
        elif sample_idx == 9:
            del_rels("MRK", "TRT", "LOI")

    # ============================================================
    # chunk_027
    # ============================================================
    elif chunk_id == "chunk_027":
        if sample_idx == 0:
            del_rels("BIS", "BIS", "AFF")
        elif sample_idx == 1:
            del_rels("GENE", "ABS", "AFF")
        elif sample_idx == 3:
            del_rels("GENE", "GENE", "AFF")
        elif sample_idx == 4:
            del_rels("CROSS", "VAR", "CON")
            del_rels("QTL", "MRK", "LOI")
        elif sample_idx == 5:
            del_rels("CROP", "BM", "USE")
            del_rels("VAR", "VAR", "CON")
        elif sample_idx == 7:
            del_rels("CROSS", "CROSS", "CON")

    # ============================================================
    # chunk_028
    # ============================================================
    elif chunk_id == "chunk_028":
        if sample_idx == 2:
            del_rels("ABS", "VAR", "AFF")
        elif sample_idx == 5:
            del_rels("CROP", "ABS", "AFF")
        elif sample_idx == 6:
            del_rel_offset(142, 154, 142, 164, "AFF")
        elif sample_idx == 9:
            del_ent(144, 149)

    # ============================================================
    # chunk_029
    # ============================================================
    elif chunk_id == "chunk_029":
        if sample_idx == 1:
            del_rels("ABS", "CROSS", "AFF")
        elif sample_idx == 3:
            del_rels("ABS", "GENE", "AFF")
        elif sample_idx == 5:
            del_rels("MRK", "CHR", "LOI")
        elif sample_idx == 6:
            del_rels("GENE", "GENE", "AFF")
        elif sample_idx == 7:
            del_rel_offset(48, 64, 48, 74, "AFF")
            del_rel_offset(340, 351, 340, 361, "AFF")
        elif sample_idx == 8:
            del_rel_offset(122, 126, 122, 136, "AFF")
        elif sample_idx == 9:
            del_rels("TRT", "TRT", "CON")

    # ============================================================
    # chunk_030
    # ============================================================
    elif chunk_id == "chunk_030":
        if sample_idx == 0:
            del_rels("ABS", "GENE", "AFF")
        elif sample_idx == 3:
            del_rels("BM", "TRT", "USE")
        elif sample_idx == 4:
            del_rels("CROSS", "CROP", "CON")
            del_rels("MRK", "TRT", "LOI")  # linked markers -> drought tolerance
        elif sample_idx == 5:
            del_rels("BM", "GENE", "USE")
        elif sample_idx == 7:
            del_rels("MRK", "QTL", "LOI")
        elif sample_idx == 8:
            del_rels("GENE", "GENE", "AFF")

    return entities, relations


def process_chunk(chunk_id):
    print(f"\n处理 {chunk_id}...")
    orig_data = load_original_json(chunk_id)
    annotated = parse_annotated_md(chunk_id)

    if len(annotated) != len(orig_data):
        print(f"  警告: {chunk_id} annotated 样本数({len(annotated)}) != 原始样本数({len(orig_data)})")

    result = []
    for i, orig_sample in enumerate(orig_data):
        new_sample = copy.deepcopy(orig_sample)
        if i < len(annotated):
            entities, relations = annotated[i]
            entities, relations = apply_audit_corrections(i, entities, relations, chunk_id)
            new_sample["entities"] = entities
            new_sample["relations"] = relations
        else:
            print(f"  警告: {chunk_id} 样本{i} 无 annotated 数据，保留原始标注")
        result.append(new_sample)

    out_path = os.path.join(RESULT_DIR, f"{chunk_id}_corrected.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total_entities = sum(len(s.get("entities", [])) for s in result)
    total_relations = sum(len(s.get("relations", [])) for s in result)
    print(f"  已保存: {out_path}")
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
    print(f"\n全量修正 v2 完成，共处理 {len(all_results)} 个块。")


if __name__ == "__main__":
    main()
