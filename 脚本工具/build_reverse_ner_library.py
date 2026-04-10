#!/usr/bin/env python3.11
"""
ReverseNER 自生成示例库构建脚本
基于论文: ReverseNER (arXiv:2411.00533v4)

核心流程:
1. 从测试集提取特征句（K-means聚类，取聚类中心句）
2. 给定实体类型定义，让LLM模仿特征句结构生成合成句子（实体展开）
3. 合成句子天然带有实体标注，构成伪少样本（Pseudo Few-shot）示例库
4. 对每条测试句，检索最相似的合成示例作为Few-shot
5. （可选）实体级自一致性评分（Entity-Level SC）提升精确率

使用方法:
  python3.11 build_reverse_ner_library.py
  
输出:
  /home/ubuntu/bisai/数据/reverse_ner_library.json  -- 合成示例库
  /home/ubuntu/bisai/数据/reverse_ner_index.pkl     -- TF-IDF检索索引
"""

import json
import os
import pickle
import time
import logging
from collections import Counter
from openai import OpenAI

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

client = OpenAI()
MODEL = "gpt-4.1-mini"

# ─────────────────────────────────────────────
# 1. 实体类型定义（MGBIE 官方 Schema）
# ─────────────────────────────────────────────
ENTITY_DEFINITIONS = {
    "CROP":  "作物名称，如水稻、小麦、玉米、大豆、高粱、谷子、棉花等粮食或经济作物。",
    "VAR":   "品种名称，指具体的作物品种或育种材料，如'中稻3号'、'郑单958'等。",
    "GENE":  "基因名称，指具体的基因或基因座，如'Ghd7'、'OsMADS'等，通常为斜体英文。",
    "QTL":   "数量性状基因座（QTL），指控制数量性状的染色体区段，如'qTGW6'、'qSH1'等。",
    "MRK":   "分子标记，指用于基因型鉴定的DNA标记，如SSR标记'RM223'、SNP标记等。",
    "TRT":   "性状，指被研究的表型特征，如产量、株高、抗病性、千粒重、开花期等。",
    "BM":    "生物标记，指用于测量性状的生化或分子指标，如蛋白质含量、叶绿素含量等。",
    "LOI":   "研究位置/区间，指QTL或基因所在的染色体区间，如'第3染色体短臂'。",
}

# 合法关系类型（用于生成时约束）
VALID_RELATIONS = [
    "CROP-CON-VAR", "VAR-HAS-TRT", "VAR-USE-BM", "VAR-OCI-GENE",
    "GENE-AFF-TRT", "GENE-LOI-TRT", "GENE-LOI-CHR",
    "QTL-LOI-TRT", "QTL-LOI-CHR", "MRK-LOI-CHR",
    "TRT-HAS-BM", "TRT-AFF-BM",
]

# ─────────────────────────────────────────────
# 2. 加载数据
# ─────────────────────────────────────────────
def load_data():
    with open("/home/ubuntu/official_mgbie/dataset/train.json") as f:
        train = json.load(f)
    with open("/home/ubuntu/official_mgbie/dataset/test_A.json") as f:
        test = json.load(f)
    return train, test

# ─────────────────────────────────────────────
# 3. 特征句提取（K-means聚类）
# ─────────────────────────────────────────────
def extract_feature_sentences(test_data, n_clusters=10):
    """从测试集中提取代表性特征句（聚类中心句）"""
    texts = [item["text"] for item in test_data]
    
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=5000)
    X = vectorizer.fit_transform(texts)
    
    n_clusters = min(n_clusters, len(texts))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X)
    
    feature_sentences = []
    for i in range(n_clusters):
        cluster_indices = np.where(kmeans.labels_ == i)[0]
        center = kmeans.cluster_centers_[i]
        cluster_vectors = X[cluster_indices]
        sims = cosine_similarity(cluster_vectors, center.reshape(1, -1)).flatten()
        best_idx = cluster_indices[np.argmax(sims)]
        feature_sentences.append(texts[best_idx])
    
    logger.info(f"提取了 {len(feature_sentences)} 条特征句")
    return feature_sentences, vectorizer

# ─────────────────────────────────────────────
# 4. 实体展开（LLM生成合成句子）
# ─────────────────────────────────────────────
EXPAND_SYSTEM_PROMPT = """你是一个农业生物信息学领域的专家，专门研究作物育种和基因组学。

你的任务是：给定一个实体类型和一些参考句子的结构，生成包含该类型实体的真实学术句子。

要求：
1. 生成的句子必须是真实的农业育种研究语境，语言风格与参考句子一致
2. 实体必须真实存在或符合命名规范（如基因用斜体英文，品种用中文或英文）
3. 每个句子必须包含指定的实体类型，并可能包含其他相关实体
4. 句子长度在 30-100 字之间
5. 严格按照 JSON 格式输出，不要添加任何解释

输出格式（JSON数组）：
[
  {
    "text": "生成的句子",
    "entities": [{"entity": "实体文本", "type": "实体类型", "start": 开始位置, "end": 结束位置}],
    "relations": [{"subject": "主体实体", "predicate": "关系类型", "object": "客体实体"}]
  }
]"""

def generate_synthetic_examples(entity_type, entity_def, feature_sentences, n_examples=3):
    """让LLM模仿特征句结构，生成包含指定实体类型的合成句子"""
    
    # 随机选择2-3条特征句作为结构参考
    selected_features = np.random.choice(feature_sentences, size=min(3, len(feature_sentences)), replace=False)
    structure_refs = "\n".join([f"- {s}" for s in selected_features])
    
    user_prompt = f"""请生成 {n_examples} 条包含【{entity_type}（{entity_def}）】实体的农业育种研究句子。

参考以下句子的结构和语言风格（不要直接复制，只参考结构）：
{structure_refs}

合法的关系类型有：{', '.join(VALID_RELATIONS)}

请生成 {n_examples} 条不同的句子，每条句子都必须包含至少一个 {entity_type} 类型的实体。

严格按照以下 JSON 格式输出（必须包含 examples 键）：
{{"examples": [{{"text": "句子内容", "entities": [{{"entity": "实体文本", "type": "{entity_type}", "start": 0, "end": 2}}], "relations": []}}]}}"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": EXPAND_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"},
                timeout=30
            )
            raw = resp.choices[0].message.content.strip()
            # 解析JSON
            parsed = json.loads(raw)
            # 兼容不同的返回格式，优先读取 examples 键
            if "examples" in parsed:
                examples = parsed["examples"]
            elif isinstance(parsed, list):
                examples = parsed
            elif "sentences" in parsed:
                examples = parsed["sentences"]
            elif "data" in parsed:
                examples = parsed["data"]
            else:
                # 取第一个list类型的値
                examples = []
                for v in parsed.values():
                    if isinstance(v, list) and len(v) > 0:
                        examples = v
                        break
            
            # 验证格式
            valid = []
            for ex in examples:
                if isinstance(ex, dict) and "text" in ex and "entities" in ex:
                    valid.append(ex)
            
            if valid:
                return valid
        except Exception as e:
            logger.warning(f"生成 {entity_type} 示例失败 (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    
    return []

# ─────────────────────────────────────────────
# 5. 构建完整示例库
# ─────────────────────────────────────────────
def build_example_library(feature_sentences, examples_per_type=3):
    """为每种实体类型生成合成示例，构建完整示例库"""
    library = []
    
    for entity_type, entity_def in ENTITY_DEFINITIONS.items():
        logger.info(f"正在为 {entity_type} 生成示例...")
        examples = generate_synthetic_examples(entity_type, entity_def, feature_sentences, n_examples=examples_per_type)
        for ex in examples:
            ex["source_entity_type"] = entity_type
            library.append(ex)
        logger.info(f"  {entity_type}: 生成了 {len(examples)} 条合成示例")
        time.sleep(0.5)
    
    logger.info(f"示例库构建完成，共 {len(library)} 条合成示例")
    return library

# ─────────────────────────────────────────────
# 6. 构建检索索引
# ─────────────────────────────────────────────
def build_retrieval_index(library, vectorizer=None):
    """为示例库构建 TF-IDF 检索索引"""
    texts = [ex["text"] for ex in library]
    
    if vectorizer is None:
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=5000)
        vectorizer.fit(texts)
    
    X = vectorizer.transform(texts)
    return vectorizer, X

def retrieve_similar_examples(query_text, library, vectorizer, library_matrix, top_k=4):
    """检索与查询句最相似的 top_k 条合成示例"""
    query_vec = vectorizer.transform([query_text])
    sims = cosine_similarity(query_vec, library_matrix).flatten()
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [library[i] for i in top_indices]

# ─────────────────────────────────────────────
# 7. 实体级自一致性评分（Entity-Level SC）
# ─────────────────────────────────────────────
def entity_level_sc_scoring(text, predict_fn, n_samples=3, threshold=0.5):
    """
    对同一句子多次采样，按实体出现频率进行投票
    只保留出现次数 >= threshold * n_samples 的实体
    
    Args:
        text: 待预测的句子
        predict_fn: 预测函数，接受text返回(entities, relations)
        n_samples: 采样次数（建议3-5次）
        threshold: 实体保留阈值（0.5 = 多数同意）
    
    Returns:
        (entities, relations): 经过SC过滤的最终结果
    """
    all_entities = []
    all_relations = []
    
    for i in range(n_samples):
        try:
            entities, relations = predict_fn(text)
            all_entities.append(entities)
            all_relations.append(relations)
        except Exception as e:
            logger.warning(f"SC采样 {i+1} 失败: {e}")
    
    if not all_entities:
        return [], []
    
    # 实体级投票：统计每个实体（文本+类型）的出现次数
    entity_counter = Counter()
    entity_objects = {}
    for entities in all_entities:
        seen = set()
        for ent in entities:
            key = (ent.get("entity", ""), ent.get("type", ""))
            if key not in seen:
                entity_counter[key] += 1
                entity_objects[key] = ent
                seen.add(key)
    
    min_votes = max(1, int(threshold * len(all_entities)))
    final_entities = [
        entity_objects[key] for key, count in entity_counter.items()
        if count >= min_votes
    ]
    
    # 关系级投票：统计每个三元组的出现次数
    relation_counter = Counter()
    relation_objects = {}
    for relations in all_relations:
        seen = set()
        for rel in relations:
            key = (rel.get("subject", ""), rel.get("predicate", ""), rel.get("object", ""))
            if key not in seen:
                relation_counter[key] += 1
                relation_objects[key] = rel
                seen.add(key)
    
    final_relations = [
        relation_objects[key] for key, count in relation_counter.items()
        if count >= min_votes
    ]
    
    return final_entities, final_relations

# ─────────────────────────────────────────────
# 8. 主流程
# ─────────────────────────────────────────────
def main():
    output_dir = "/home/ubuntu/bisai/数据"
    os.makedirs(output_dir, exist_ok=True)
    
    library_path = os.path.join(output_dir, "reverse_ner_library.json")
    index_path = os.path.join(output_dir, "reverse_ner_index.pkl")
    
    # 如果已存在则跳过生成
    if os.path.exists(library_path) and os.path.exists(index_path):
        logger.info("示例库已存在，跳过生成步骤")
        with open(library_path) as f:
            library = json.load(f)
        logger.info(f"加载已有示例库: {len(library)} 条")
        return library
    
    logger.info("=== ReverseNER 示例库构建开始 ===")
    
    # 加载数据
    train_data, test_data = load_data()
    logger.info(f"训练集: {len(train_data)} 条, 测试集: {len(test_data)} 条")
    
    # 提取特征句（从测试集聚类）
    feature_sentences, tfidf_vectorizer = extract_feature_sentences(test_data, n_clusters=10)
    logger.info("特征句示例:")
    for i, s in enumerate(feature_sentences[:3]):
        logger.info(f"  [{i+1}] {s[:60]}...")
    
    # 构建示例库（每种实体类型生成3条）
    library = build_example_library(feature_sentences, examples_per_type=3)
    
    # 保存示例库
    with open(library_path, "w", encoding="utf-8") as f:
        json.dump(library, f, ensure_ascii=False, indent=2)
    logger.info(f"示例库已保存至: {library_path}")
    
    # 构建检索索引并保存
    lib_vectorizer, lib_matrix = build_retrieval_index(library)
    with open(index_path, "wb") as f:
        pickle.dump({"vectorizer": lib_vectorizer, "matrix": lib_matrix, "library": library}, f)
    logger.info(f"检索索引已保存至: {index_path}")
    
    # 输出统计
    type_counts = Counter(ex["source_entity_type"] for ex in library)
    logger.info("各实体类型示例数量:")
    for t, c in type_counts.items():
        logger.info(f"  {t}: {c} 条")
    
    logger.info("=== ReverseNER 示例库构建完成 ===")
    return library

if __name__ == "__main__":
    main()
