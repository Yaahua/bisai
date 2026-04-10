#!/usr/bin/env python3.11
"""
Schema-based SCIR 自纠正模块
基于论文: SCIR (arXiv:2512.12337v1) 的零样本改造版

核心逻辑（不需要训练任何检测模型）：
1. 硬编码规则检测：检查预测结果是否违反官方 Schema
2. 触发条件：出现非法三元组 OR 高频实体漏标 OR 关系数量异常
3. 二次纠正：将检测到的问题拼入 Prompt，让 LLM 重新预测
4. 最多迭代 2 轮，避免无限循环

使用方式（在预测脚本中导入）：
  from scir_self_correct import scir_correct
  entities, relations = scir_correct(text, entities, relations, predict_fn)
"""

import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI()

# ─────────────────────────────────────────────
# 官方合法三元组集合（从训练集统计）
# ─────────────────────────────────────────────
VALID_TRIPLES = {
    "CROP-CON-VAR", "VAR-HAS-TRT", "VAR-USE-BM", "VAR-OCI-GENE",
    "GENE-AFF-TRT", "GENE-LOI-TRT", "GENE-LOI-CHR",
    "QTL-LOI-TRT", "QTL-LOI-CHR", "MRK-LOI-CHR",
    "TRT-HAS-BM", "TRT-AFF-BM",
    "CROP-CON-GENE", "CROP-CON-QTL", "CROP-CON-MRK",
    "VAR-HAS-GENE", "VAR-HAS-QTL",
}

# 高频实体关键词（用于检测漏标）
CROP_KEYWORDS = [
    "水稻", "小麦", "玉米", "大豆", "高粱", "谷子", "棉花", "油菜", "花生",
    "rice", "wheat", "maize", "soybean", "sorghum", "millet", "cotton",
    "barley", "大麦", "燕麦", "oat", "rye", "黑麦",
]

GENE_PATTERNS = ["Os", "Gh", "Zm", "Gm", "Sb", "Si"]  # 基因前缀

# ─────────────────────────────────────────────
# 规则检测器
# ─────────────────────────────────────────────
def detect_issues(text, entities, relations):
    """
    检测预测结果中的问题，返回问题列表
    
    Returns:
        issues: list of str，每条描述一个具体问题
        severity: "high" | "low" | "none"
    """
    issues = []
    
    entity_texts = {e.get("entity", ""): e.get("type", "") for e in entities}
    entity_types = set(entity_texts.values())
    
    # 1. 检测非法三元组
    for rel in relations:
        subj = rel.get("subject", "")
        pred = rel.get("predicate", "")
        obj = rel.get("object", "")
        
        subj_type = entity_texts.get(subj, "")
        obj_type = entity_texts.get(obj, "")
        
        if subj_type and obj_type:
            triple_key = f"{subj_type}-{pred}-{obj_type}"
            if triple_key not in VALID_TRIPLES:
                issues.append(f"非法关系：'{subj}'({subj_type}) -{pred}-> '{obj}'({obj_type}) 不在合法三元组集合中")
    
    # 2. 检测 CROP 漏标
    if "CROP" not in entity_types:
        for kw in CROP_KEYWORDS:
            if kw.lower() in text.lower():
                issues.append(f"疑似漏标 CROP 实体：文本中包含作物关键词 '{kw}'，但未标注任何 CROP 实体")
                break
    
    # 3. 检测 GENE 漏标（基因前缀模式）
    if "GENE" not in entity_types and "QTL" not in entity_types:
        for prefix in GENE_PATTERNS:
            if prefix in text:
                issues.append(f"疑似漏标 GENE/QTL 实体：文本中含有基因前缀 '{prefix}'，但未标注任何 GENE 或 QTL 实体")
                break
    
    # 4. 检测关系数量异常（超过 8 个关系通常是过标）
    if len(relations) > 8:
        issues.append(f"关系数量过多：共 {len(relations)} 个关系，官方平均为 2.8 个，请检查是否过标")
    
    # 5. 检测 VAR 有实体但无关系（孤立实体）
    if "VAR" in entity_types and not any(
        entity_texts.get(r.get("subject", "")) == "VAR" or 
        entity_texts.get(r.get("object", "")) == "VAR"
        for r in relations
    ):
        issues.append("VAR 实体被标注但没有任何关系，请检查是否应该有 CROP-CON-VAR 或 VAR-HAS-TRT 关系")
    
    if not issues:
        return issues, "none"
    elif len(issues) >= 2 or any("非法关系" in i for i in issues):
        return issues, "high"
    else:
        return issues, "low"

# ─────────────────────────────────────────────
# SCIR 纠正 Prompt
# ─────────────────────────────────────────────
CORRECTION_SYSTEM = """你是一个农业生物信息学信息抽取专家。你的任务是检查并修正一段实体关系抽取的结果。

合法的关系类型（三元组格式：主体类型-关系-客体类型）：
CROP-CON-VAR, VAR-HAS-TRT, VAR-USE-BM, VAR-OCI-GENE,
GENE-AFF-TRT, GENE-LOI-TRT, GENE-LOI-CHR,
QTL-LOI-TRT, QTL-LOI-CHR, MRK-LOI-CHR,
TRT-HAS-BM, TRT-AFF-BM, CROP-CON-GENE, CROP-CON-QTL, CROP-CON-MRK

实体类型：CROP（作物）, VAR（品种）, GENE（基因）, QTL（数量性状基因座）, MRK（分子标记）, TRT（性状）, BM（生物标记）, LOI（研究位置）

规则：
1. 删除所有不在合法三元组集合中的关系
2. 如果文本中有作物名称但未标注 CROP，请补充标注
3. 如果文本中有基因名称（如 OsXXX、GhXXX）但未标注，请补充标注
4. 实体的 start/end 必须与文本完全匹配（字符级别）
5. 关系中的 subject 和 object 必须是已标注的实体文本

严格按照以下 JSON 格式输出，不要添加任何解释：
{"entities": [...], "relations": [...]}"""

def scir_correct(text, entities, relations, model="gpt-4.1-mini", max_rounds=2):
    """
    SCIR 自纠正主函数
    
    Args:
        text: 原始文本
        entities: 初始预测的实体列表
        relations: 初始预测的关系列表
        model: 使用的模型
        max_rounds: 最大纠正轮数
    
    Returns:
        (entities, relations): 纠正后的结果
    """
    current_entities = entities
    current_relations = relations
    
    for round_idx in range(max_rounds):
        issues, severity = detect_issues(text, current_entities, current_relations)
        
        if severity == "none":
            logger.debug(f"SCIR: 无问题，跳过纠正")
            break
        
        logger.debug(f"SCIR round {round_idx+1}: 检测到 {len(issues)} 个问题 (severity={severity})")
        
        # 只有高严重度或第一轮才触发纠正
        if severity == "low" and round_idx > 0:
            break
        
        issues_text = "\n".join([f"- {issue}" for issue in issues])
        
        correction_prompt = f"""请检查并修正以下实体关系抽取结果。

原始文本：
{text}

当前预测结果：
实体：{json.dumps(current_entities, ensure_ascii=False)}
关系：{json.dumps(current_relations, ensure_ascii=False)}

检测到的问题：
{issues_text}

请根据上述问题修正预测结果，输出修正后的完整 JSON。"""

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": CORRECTION_SYSTEM},
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
                timeout=30
            )
            raw = resp.choices[0].message.content.strip()
            corrected = json.loads(raw)
            
            new_entities = corrected.get("entities", current_entities)
            new_relations = corrected.get("relations", current_relations)
            
            # 验证修正后的结果
            new_issues, new_severity = detect_issues(text, new_entities, new_relations)
            
            if new_severity == "none" or len(new_issues) < len(issues):
                logger.debug(f"SCIR round {round_idx+1}: 纠正有效，问题从 {len(issues)} 减少到 {len(new_issues)}")
                current_entities = new_entities
                current_relations = new_relations
            else:
                logger.debug(f"SCIR round {round_idx+1}: 纠正无效，保持原结果")
                break
                
        except Exception as e:
            logger.warning(f"SCIR 纠正失败: {e}")
            break
    
    return current_entities, current_relations


# ─────────────────────────────────────────────
# 独立测试
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # 测试用例：包含非法关系的预测结果
    test_text = "水稻品种'中稻3号'的产量性状受基因OsGW5的调控，该基因位于第5染色体上。"
    test_entities = [
        {"entity": "水稻", "type": "CROP", "start": 0, "end": 2},
        {"entity": "中稻3号", "type": "VAR", "start": 3, "end": 7},
        {"entity": "产量", "type": "TRT", "start": 9, "end": 11},
        {"entity": "OsGW5", "type": "GENE", "start": 16, "end": 21},
        {"entity": "第5染色体", "type": "LOI", "start": 25, "end": 30},
    ]
    test_relations = [
        {"subject": "水稻", "predicate": "CON", "object": "中稻3号"},
        {"subject": "中稻3号", "predicate": "HAS", "object": "产量"},
        {"subject": "OsGW5", "predicate": "AFF", "object": "产量"},
        {"subject": "OsGW5", "predicate": "LOI", "object": "第5染色体"},
        # 非法关系
        {"subject": "产量", "predicate": "AFF", "object": "水稻"},  # TRT-AFF-CROP 非法
    ]
    
    issues, severity = detect_issues(test_text, test_entities, test_relations)
    print(f"检测到 {len(issues)} 个问题 (severity={severity}):")
    for issue in issues:
        print(f"  - {issue}")
    
    print("\n开始 SCIR 纠正...")
    corrected_entities, corrected_relations = scir_correct(test_text, test_entities, test_relations)
    print(f"纠正后关系数量: {len(test_relations)} -> {len(corrected_relations)}")
    print("纠正后关系:")
    for rel in corrected_relations:
        print(f"  {rel}")
