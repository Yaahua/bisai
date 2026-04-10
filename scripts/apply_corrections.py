#!/usr/bin/env python3
"""
全量修正脚本：读取各块原始 JSON + annotated.md 中的修订后标注结果，
依据 audit.md 的必须修改项，生成最终修订 JSON 文件。

修正策略：
1. 以 annotated.md 中的 entities/relations 为基础（已包含初步修正）
2. 在此基础上应用 audit.md 中的必须修改项（删除非法关系）
3. 输出最终 JSON 到 修订结果/ 目录
"""

import json
import os
import copy

BASE_DIR = "/home/ubuntu/bisai_clone/数据/训练集"
ORIG_DIR = os.path.join(BASE_DIR, "原始切分块")
RESULT_DIR = os.path.join(BASE_DIR, "修订结果")
os.makedirs(RESULT_DIR, exist_ok=True)

# ============================================================
# 各块的修正规则（基于 audit.md 必须修改项）
# 格式：每条规则为 (chunk_id, sample_idx, action, match_criteria)
# action: "delete_relation" | "delete_entity" | "change_entity_label"
# ============================================================

# 每块的修正规则：chunk_id -> list of (sample_idx, action, criteria_dict)
CORRECTIONS = {
    # chunk_021: 1项必须修改（偏移核实），已在 annotated.md 中处理
    "chunk_021": [],

    # chunk_022: 2项必须修改
    "chunk_022": [
        # 问题1: LOI 锚点错误 - 在 annotated.md 中已处理
        # 问题2: USE 主体类型错误 - 在 annotated.md 中已处理
    ],

    # chunk_023: 4项必须修改 - 在 annotated.md 中已处理
    "chunk_023": [],

    # chunk_024: 2项必须修改 - 在 annotated.md 中已处理
    "chunk_024": [],

    # chunk_025: 2项必须修改 - 在 annotated.md 中已处理
    "chunk_025": [],

    # chunk_026: 4项必须修改 - 在 annotated.md 中已处理
    "chunk_026": [],

    # chunk_027: 5项必须修改
    "chunk_027": [
        # 样本4: 删除 CON(CROSS, VAR) ×3
        (4, "delete_relations_by_type", {"head_type": "CROSS", "tail_type": "VAR", "label": "CON"}),
        # 样本7: 删除 CON(CROSS, CROSS)
        (7, "delete_relations_by_type", {"head_type": "CROSS", "tail_type": "CROSS", "label": "CON"}),
        # 样本1: 删除 AFF(GENE, ABS) ×2
        (1, "delete_relations_by_type", {"head_type": "GENE", "tail_type": "ABS", "label": "AFF"}),
        # 样本3: 删除 AFF(GENE, GENE) ×2
        (3, "delete_relations_by_type", {"head_type": "GENE", "tail_type": "GENE", "label": "AFF"}),
        # 样本5: 删除 USE(CROP, BM)，改为 USE(VAR, BM) - 在 annotated.md 中已有 USE(hulless oats VAR, genotyping-by-sequencing)
        (5, "delete_relations_by_type", {"head_type": "CROP", "tail_type": "BM", "label": "USE"}),
        # 建议修改: 样本4 删除 LOI(QTL, MRK)
        (4, "delete_relations_by_type", {"head_type": "QTL", "tail_type": "MRK", "label": "LOI"}),
    ],

    # chunk_028: 2项必须修改
    "chunk_028": [
        # 样本2: 删除 AFF(ABS, VAR)
        (2, "delete_relations_by_type", {"head_type": "ABS", "tail_type": "VAR", "label": "AFF"}),
        # 样本5: 删除 AFF(CROP, ABS)
        (5, "delete_relations_by_type", {"head_type": "CROP", "tail_type": "ABS", "label": "AFF"}),
        # 建议修改: 样本9 删除冗余 M-81E @144:149
        (9, "delete_entity_by_offset", {"start": 144, "end": 149}),
        # 建议修改: 样本6 删除 AFF(waterlogging @142:154, waterlogging sensitive @142:164)
        (6, "delete_relation_by_offsets", {"head_start": 142, "head_end": 154, "tail_start": 142, "tail_end": 164, "label": "AFF"}),
    ],

    # chunk_029: 4项必须修改
    "chunk_029": [
        # 样本1: 删除 AFF(ABS, CROSS)
        (1, "delete_relations_by_type", {"head_type": "ABS", "tail_type": "CROSS", "label": "AFF"}),
        # 样本3: 删除 AFF(ABS, GENE) ×4
        (3, "delete_relations_by_type", {"head_type": "ABS", "tail_type": "GENE", "label": "AFF"}),
        # 样本6: 删除 AFF(GENE, GENE)
        (6, "delete_relations_by_type", {"head_type": "GENE", "tail_type": "GENE", "label": "AFF"}),
        # 样本9: 删除 CON(TRT, TRT)
        (9, "delete_relations_by_type", {"head_type": "TRT", "tail_type": "TRT", "label": "CON"}),
        # 建议修改: 样本7 删除 AFF 嵌套关系 ×2
        (7, "delete_relation_by_offsets", {"head_start": 48, "head_end": 64, "tail_start": 48, "tail_end": 74, "label": "AFF"}),
        (7, "delete_relation_by_offsets", {"head_start": 340, "head_end": 351, "tail_start": 340, "tail_end": 361, "label": "AFF"}),
        # 建议修改: 样本5 删除 LOI(MRK, CHR)
        (5, "delete_relations_by_type", {"head_type": "MRK", "tail_type": "CHR", "label": "LOI"}),
        # 建议修改: 样本8 删除 AFF(salt @122:126, salt tolerance @122:136)
        (8, "delete_relation_by_offsets", {"head_start": 122, "head_end": 126, "tail_start": 122, "tail_end": 136, "label": "AFF"}),
    ],

    # chunk_030: 6项必须修改
    "chunk_030": [
        # 样本0: 删除 AFF(ABS, GENE)
        (0, "delete_relations_by_type", {"head_type": "ABS", "tail_type": "GENE", "label": "AFF"}),
        # 样本3: 删除 USE(BM, TRT) ×2
        (3, "delete_relations_by_type", {"head_type": "BM", "tail_type": "TRT", "label": "USE"}),
        # 样本4: 删除 CON(CROSS, CROP)
        (4, "delete_relations_by_type", {"head_type": "CROSS", "tail_type": "CROP", "label": "CON"}),
        # 样本5: 删除 USE(BM, GENE)
        (5, "delete_relations_by_type", {"head_type": "BM", "tail_type": "GENE", "label": "USE"}),
        # 样本7: 删除 LOI(MRK, QTL)
        (7, "delete_relations_by_type", {"head_type": "MRK", "tail_type": "QTL", "label": "LOI"}),
        # 样本8: 删除 AFF(GENE, GENE) ×3
        (8, "delete_relations_by_type", {"head_type": "GENE", "tail_type": "GENE", "label": "AFF"}),
    ],
}


def apply_corrections_to_sample(sample, corrections_for_sample):
    """对单个样本应用修正规则"""
    sample = copy.deepcopy(sample)
    entities = sample.get("entities", [])
    relations = sample.get("relations", [])

    for action, criteria in corrections_for_sample:
        if action == "delete_relations_by_type":
            new_relations = []
            for r in relations:
                head_type = r.get("head_type", "")
                tail_type = r.get("tail_type", "")
                label = r.get("label", "")
                match = True
                if "head_type" in criteria and head_type != criteria["head_type"]:
                    match = False
                if "tail_type" in criteria and tail_type != criteria["tail_type"]:
                    match = False
                if "label" in criteria and label != criteria["label"]:
                    match = False
                if not match:
                    new_relations.append(r)
            relations = new_relations

        elif action == "delete_entity_by_offset":
            new_entities = []
            for e in entities:
                if e.get("start") == criteria["start"] and e.get("end") == criteria["end"]:
                    continue
                new_entities.append(e)
            entities = new_entities

        elif action == "delete_relation_by_offsets":
            new_relations = []
            for r in relations:
                match = True
                if "head_start" in criteria and r.get("head_start") != criteria["head_start"]:
                    match = False
                if "head_end" in criteria and r.get("head_end") != criteria["head_end"]:
                    match = False
                if "tail_start" in criteria and r.get("tail_start") != criteria["tail_start"]:
                    match = False
                if "tail_end" in criteria and r.get("tail_end") != criteria["tail_end"]:
                    match = False
                if "label" in criteria and r.get("label") != criteria["label"]:
                    match = False
                if not match:
                    new_relations.append(r)
            relations = new_relations

    sample["entities"] = entities
    sample["relations"] = relations
    return sample


def process_chunk_from_annotated(chunk_id, annotated_data, corrections):
    """从 annotated.md 解析的数据 + 修正规则生成最终结果"""
    result = []
    chunk_corrections = corrections.get(chunk_id, [])

    # 按样本索引分组修正规则
    sample_corrections = {}
    for item in chunk_corrections:
        sample_idx = item[0]
        action = item[1]
        criteria = item[2]
        if sample_idx not in sample_corrections:
            sample_corrections[sample_idx] = []
        sample_corrections[sample_idx].append((action, criteria))

    for i, sample in enumerate(annotated_data):
        if i in sample_corrections:
            sample = apply_corrections_to_sample(sample, sample_corrections[i])
        result.append(sample)

    return result


def load_original_json(chunk_id):
    """加载原始 JSON 文件"""
    path = os.path.join(ORIG_DIR, f"{chunk_id}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_corrected_json(chunk_id, data):
    """保存修订后的 JSON 文件"""
    path = os.path.join(RESULT_DIR, f"{chunk_id}_corrected.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已保存: {path}")
    return path


if __name__ == "__main__":
    print("全量修正脚本启动...")
    print("注意：此脚本需要配合 annotated_loader.py 使用，先加载 annotated.md 数据")
    print("请运行 apply_corrections_full.py 进行完整处理")
