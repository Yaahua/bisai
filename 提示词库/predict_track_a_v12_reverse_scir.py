#!/usr/bin/env python3.11
"""
MGBIE Track-A 预测脚本 v12 — ReverseNER + SCIR 守擂版
=============================================================
基于守擂规划（文档9）实施：
  - 阶段一：ReverseNER 自生成示例增强（解决召回率断崖问题）
  - 阶段二：Schema-based SCIR 自纠正（消除非法三元组和漏标）

核心改进（相比 v9_clean 0.3893）：
1. Few-shot 来源：训练集 RAG（5条）+ ReverseNER 合成示例（2条）
   - 合成示例专门针对测试集的文本结构生成，覆盖低频关系
2. SCIR 自纠正：预测后自动检测非法三元组和漏标，触发二次修正
3. 保留 v9 的所有优化：c-ICL 对比示例、专项漏标注入、非法关系黑名单
"""
import json
import os
import re
import sys
import time
import pickle
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# ===== 路径配置 =====
TRAIN_PATH    = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH     = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_v12_reverse_scir.json'
LIBRARY_PATH  = '/home/ubuntu/bisai/数据/reverse_ner_library.json'
INDEX_PATH    = '/home/ubuntu/bisai/数据/reverse_ner_index.pkl'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gpt-4.1-mini"
WORKERS    = 15
SAVE_EVERY = 20
TOP_K_RAG  = 4   # 训练集 RAG 检索数量
TOP_K_SYN  = 2   # ReverseNER 合成示例数量
SCIR_ENABLED = True  # 是否启用 SCIR 自纠正

client = OpenAI()

# ===== 合法三元组集合 =====
VALID_TRIPLES = {
    "CROP-CON-VAR", "VAR-HAS-TRT", "VAR-USE-BM", "VAR-OCI-GENE",
    "GENE-AFF-TRT", "GENE-LOI-TRT", "GENE-LOI-CHR",
    "QTL-LOI-TRT", "QTL-LOI-CHR", "MRK-LOI-CHR",
    "TRT-HAS-BM", "TRT-AFF-BM",
    "CROP-CON-GENE", "CROP-CON-QTL", "CROP-CON-MRK",
    "VAR-HAS-GENE", "VAR-HAS-QTL",
}

# 非法三元组黑名单（从 v9 继承并扩展）
ILLEGAL_TRIPLETS = {
    ('VAR',  'CON', 'CROP'), ('GENE', 'CON', 'CROP'),
    ('MRK',  'AFF', 'TRT'), ('TRT',  'HAS', 'VAR'),
    ('TRT',  'HAS', 'CROP'), ('VAR',  'OCI', 'TRT'),
    ('QTL',  'LOI', 'VAR'), ('CROP', 'HAS', 'ABS'),
    ('VAR',  'HAS', 'ABS'), ('BM',   'USE', 'CROP'),
    ('TRT',  'LOI', 'TRT'), ('CROP', 'AFF', 'TRT'),
    ('GST',  'AFF', 'TRT'), ('CHR',  'LOI', 'VAR'),
}

# ===== 加载数据 =====
logger.info("加载数据...")
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)

# ===== 构建训练集 TF-IDF 检索索引 =====
logger.info("构建训练集 TF-IDF 检索索引...")
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
tfidf_train = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf_train.fit_transform(TRAIN_TEXTS)
logger.info(f"训练集索引完成，维度：{TRAIN_MATRIX.shape}")

# ===== 加载 ReverseNER 示例库 =====
logger.info("加载 ReverseNER 合成示例库...")
if os.path.exists(INDEX_PATH):
    with open(INDEX_PATH, 'rb') as f:
        index_data = pickle.load(f)
    SYN_VECTORIZER = index_data['vectorizer']
    SYN_MATRIX     = index_data['matrix']
    SYN_LIBRARY    = index_data['library']
    logger.info(f"合成示例库加载完成，共 {len(SYN_LIBRARY)} 条")
elif os.path.exists(LIBRARY_PATH):
    with open(LIBRARY_PATH) as f:
        SYN_LIBRARY = json.load(f)
    SYN_VECTORIZER = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=5000)
    SYN_MATRIX = SYN_VECTORIZER.fit_transform([ex['text'] for ex in SYN_LIBRARY])
    logger.info(f"合成示例库加载完成（重建索引），共 {len(SYN_LIBRARY)} 条")
else:
    logger.warning("未找到 ReverseNER 示例库，将仅使用训练集 RAG")
    SYN_LIBRARY = []
    SYN_VECTORIZER = None
    SYN_MATRIX = None

# ===== 专项漏标示例 =====
def find_examples_for_triplet(head_type, rel, tail_type, n=2):
    examples = []
    for item in TRAIN_DATA:
        for r in item.get('relations', []):
            if r['head_type'] == head_type and r['label'] == rel and r['tail_type'] == tail_type:
                examples.append(item)
                break
        if len(examples) >= n:
            break
    return examples

GENE_LOI_TRT_EX = find_examples_for_triplet('GENE', 'LOI', 'TRT', 2)
MRK_LOI_CHR_EX  = find_examples_for_triplet('MRK',  'LOI', 'CHR', 2)
VAR_USE_BM_EX   = find_examples_for_triplet('VAR',  'USE', 'BM',  2)
logger.info(f"专项示例：GENE-LOI-TRT {len(GENE_LOI_TRT_EX)}条, MRK-LOI-CHR {len(MRK_LOI_CHR_EX)}条, VAR-USE-BM {len(VAR_USE_BM_EX)}条")

# ===== 检索函数 =====
def retrieve_train_rag(query_text: str, k: int = TOP_K_RAG) -> list:
    """从训练集检索最相似的 k 条样本"""
    query_vec = tfidf_train.transform([query_text])
    sims = cosine_similarity(query_vec, TRAIN_MATRIX).flatten()
    top_indices = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[idx] for idx in top_indices if sims[idx] > 0.01][:k]

def retrieve_synthetic(query_text: str, k: int = TOP_K_SYN) -> list:
    """从 ReverseNER 合成示例库检索最相似的 k 条"""
    if SYN_LIBRARY is None or SYN_VECTORIZER is None:
        return []
    query_vec = SYN_VECTORIZER.transform([query_text])
    sims = cosine_similarity(query_vec, SYN_MATRIX).flatten()
    top_indices = np.argsort(sims)[::-1][:k]
    return [SYN_LIBRARY[idx] for idx in top_indices]

def format_train_example(item: dict) -> str:
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return (f'Input: {item["text"]}\n'
            f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')

def format_synthetic_example(item: dict) -> str:
    """格式化 ReverseNER 合成示例"""
    ents = [{"text": e.get("entity", e.get("text", "")), "label": e.get("type", e.get("label", ""))}
            for e in item.get("entities", [])]
    rels = []
    for r in item.get("relations", []):
        subj = r.get("subject", r.get("head", ""))
        pred = r.get("predicate", r.get("label", ""))
        obj  = r.get("object", r.get("tail", ""))
        if subj and pred and obj:
            rels.append({"head": subj, "tail": obj, "label": pred})
    return (f'# [Synthetic Example - ReverseNER]\n'
            f'Input: {item["text"]}\n'
            f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')

# ===== 构建 Few-shot =====
def build_fewshot(rag_samples: list, syn_samples: list, text: str) -> str:
    lines = ["## Positive Examples (RAG from training set + ReverseNER synthetic)"]

    # 1. 训练集 RAG 样本
    for s in rag_samples:
        lines.append(format_train_example(s))
        lines.append("")

    # 2. ReverseNER 合成样本（补充低频关系覆盖）
    if syn_samples:
        lines.append("# Synthetic examples generated by ReverseNER to cover low-frequency relations:")
        for s in syn_samples:
            lines.append(format_synthetic_example(s))
            lines.append("")

    # 3. 专项漏标示例（根据文本内容动态注入）
    text_lower = text.lower()
    injected = set()

    if any(w in text_lower for w in ['gene', 'locus', 'loci', 'allele']) and GENE_LOI_TRT_EX:
        for ex in GENE_LOI_TRT_EX[:1]:
            key = id(ex)
            if key not in injected:
                lines.append("# Targeted example for GENE-LOI-TRT pattern:")
                lines.append(format_train_example(ex))
                lines.append("")
                injected.add(key)

    if any(w in text_lower for w in ['marker', 'ssr', 'snp', 'qtl', 'chromosome']) and MRK_LOI_CHR_EX:
        for ex in MRK_LOI_CHR_EX[:1]:
            key = id(ex)
            if key not in injected:
                lines.append("# Targeted example for MRK-LOI-CHR pattern:")
                lines.append(format_train_example(ex))
                lines.append("")
                injected.add(key)

    if any(w in text_lower for w in ['breeding', 'selection', 'backcross', 'gwas', 'mas']) and VAR_USE_BM_EX:
        for ex in VAR_USE_BM_EX[:1]:
            key = id(ex)
            if key not in injected:
                lines.append("# Targeted example for VAR-USE-BM pattern:")
                lines.append(format_train_example(ex))
                lines.append("")
                injected.add(key)

    return "\n".join(lines)

# ===== 系统提示词 =====
SYSTEM_PROMPT = """You are an expert in agricultural bioinformatics, specializing in Named Entity Recognition (NER) and Relation Extraction (RE) for crop breeding research papers.

## Entity Types
- CROP: Crop species names (rice, wheat, maize, soybean, sorghum, barley, millet, cotton, etc.)
- VAR: Variety/cultivar names (specific breeding lines or cultivars)
- GENE: Gene names (e.g., OsGW5, GhCesA, ZmVPP1)
- QTL: Quantitative trait loci (e.g., qTGW6, qSH1)
- MRK: Molecular markers (SSR, SNP, RFLP markers)
- TRT: Traits (yield, drought tolerance, plant height, flowering time — main research traits ONLY)
- BM: Biological markers (biochemical or molecular indicators used to measure traits)
- LOI: Location of interest (chromosomal regions, intervals)

## Valid Relation Types (ONLY these are allowed)
CROP-CON-VAR, VAR-HAS-TRT, VAR-USE-BM, VAR-OCI-GENE,
GENE-AFF-TRT, GENE-LOI-TRT, GENE-LOI-CHR,
QTL-LOI-TRT, QTL-LOI-CHR, MRK-LOI-CHR,
TRT-HAS-BM, TRT-AFF-BM, CROP-CON-GENE, CROP-CON-QTL, CROP-CON-MRK

## Critical Rules
1. CROP: Always annotate crop species names. Never miss rice/wheat/maize/soybean/sorghum.
2. TRT: Only annotate the PRIMARY trait being studied. Do NOT annotate measurement parameters or general descriptions.
3. Relations: ONLY use the valid relation types listed above. Any other combination is ILLEGAL.
4. Empty output: If no entities or relations exist, output empty arrays [].
5. Boundaries: entity text must exactly match the original text (character-level).

## Output Format (JSON only, no explanation)
{"entities": [{"text": "...", "label": "TYPE", "start": N, "end": N}], "relations": [{"head": "...", "head_type": "TYPE", "tail": "...", "tail_type": "TYPE", "label": "REL"}]}"""

# ===== SCIR 自纠正模块 =====
CROP_KEYWORDS = ["water rice", "rice", "wheat", "maize", "corn", "soybean", "sorghum",
                 "barley", "millet", "cotton", "oat", "rye", "rapeseed", "sunflower",
                 "水稻", "小麦", "玉米", "大豆", "高粱", "谷子", "棉花", "油菜"]
GENE_PREFIXES = ["Os", "Gh", "Zm", "Gm", "Sb", "Si", "Hv", "Ta"]

def detect_scir_issues(text, entities, relations):
    """检测预测结果中的问题"""
    issues = []
    entity_map = {e.get("text", ""): e.get("label", "") for e in entities}
    entity_types = set(entity_map.values())

    # 1. 非法三元组
    for rel in relations:
        h_type = entity_map.get(rel.get("head", ""), rel.get("head_type", ""))
        t_type = entity_map.get(rel.get("tail", ""), rel.get("tail_type", ""))
        label  = rel.get("label", "")
        if h_type and t_type:
            triple_key = f"{h_type}-{label}-{t_type}"
            if triple_key not in VALID_TRIPLES:
                issues.append(f"ILLEGAL relation: '{rel.get('head')}' ({h_type}) -{label}-> '{rel.get('tail')}' ({t_type}) is not in valid triples")

    # 2. CROP 漏标
    if "CROP" not in entity_types:
        for kw in CROP_KEYWORDS:
            if kw.lower() in text.lower():
                issues.append(f"MISSING CROP: text contains crop keyword '{kw}' but no CROP entity annotated")
                break

    # 3. 关系数量异常（>8 通常是过标）
    if len(relations) > 8:
        issues.append(f"OVER-PREDICTION: {len(relations)} relations found, expected ~2.8 on average")

    return issues

SCIR_CORRECTION_SYSTEM = """You are an expert in agricultural bioinformatics information extraction.
Review and fix the following extraction result based on the reported issues.

Valid relation types: CROP-CON-VAR, VAR-HAS-TRT, VAR-USE-BM, VAR-OCI-GENE, GENE-AFF-TRT, GENE-LOI-TRT, GENE-LOI-CHR, QTL-LOI-TRT, QTL-LOI-CHR, MRK-LOI-CHR, TRT-HAS-BM, TRT-AFF-BM, CROP-CON-GENE, CROP-CON-QTL, CROP-CON-MRK

Rules: Remove illegal relations. Add missing CROP entities if crop keywords present. Keep all correct entities and relations.
Output JSON only: {"entities": [...], "relations": [...]}"""

def scir_correct(text, entities, relations, max_rounds=1):
    """SCIR 自纠正（最多 1 轮，避免增加过多 API 调用）"""
    if not SCIR_ENABLED:
        return entities, relations

    issues = detect_scir_issues(text, entities, relations)
    if not issues:
        return entities, relations

    # 只有高严重度才触发（有非法关系或 CROP 漏标）
    high_severity = any("ILLEGAL" in i or "MISSING CROP" in i for i in issues)
    if not high_severity:
        return entities, relations

    issues_text = "\n".join([f"- {i}" for i in issues])
    correction_prompt = f"""Text: {text}

Current prediction:
Entities: {json.dumps(entities, ensure_ascii=False)}
Relations: {json.dumps(relations, ensure_ascii=False)}

Issues detected:
{issues_text}

Fix the prediction and output corrected JSON."""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SCIR_CORRECTION_SYSTEM},
                {"role": "user", "content": correction_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            timeout=25
        )
        corrected = json.loads(resp.choices[0].message.content.strip())
        new_entities = corrected.get("entities", entities)
        new_relations = corrected.get("relations", relations)

        # 验证修正是否有效（问题数量减少）
        new_issues = detect_scir_issues(text, new_entities, new_relations)
        if len(new_issues) < len(issues):
            return new_entities, new_relations
    except Exception as e:
        logger.debug(f"SCIR 纠正失败: {e}")

    return entities, relations

# ===== 主预测函数 =====
def predict_one(item: dict) -> dict:
    text = item['text']

    # 1. 检索 RAG 样本（训练集 + 合成库）
    rag_samples = retrieve_train_rag(text, k=TOP_K_RAG)
    syn_samples = retrieve_synthetic(text, k=TOP_K_SYN)

    # 2. 构建 Few-shot
    fewshot = build_fewshot(rag_samples, syn_samples, text)

    # 3. 调用 LLM 预测
    user_msg = f"""{fewshot}

## Task
Now annotate the following text:
Input: {text}
Output:"""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                timeout=30
            )
            raw = resp.choices[0].message.content.strip()
            parsed = json.loads(raw)

            entities  = parsed.get("entities", [])
            relations = parsed.get("relations", [])

            # 4. 校验实体边界
            valid_entities = []
            for e in entities:
                t = e.get("text", "")
                if t and t in text:
                    idx = text.find(t)
                    e["start"] = idx
                    e["end"]   = idx + len(t)
                    valid_entities.append(e)

            # 5. 过滤非法三元组（黑名单）
            valid_relations = []
            entity_map = {e.get("text", ""): e.get("label", "") for e in valid_entities}
            for r in relations:
                h = r.get("head", "")
                t = r.get("tail", "")
                l = r.get("label", "")
                h_type = entity_map.get(h, r.get("head_type", ""))
                t_type = entity_map.get(t, r.get("tail_type", ""))
                if (h_type, l, t_type) not in ILLEGAL_TRIPLETS:
                    r["head_type"] = h_type
                    r["tail_type"] = t_type
                    valid_relations.append(r)

            # 6. SCIR 自纠正
            final_entities, final_relations = scir_correct(text, valid_entities, valid_relations)

            return {
                "id": item.get("id", ""),
                "text": text,
                "entities": final_entities,
                "relations": final_relations
            }

        except Exception as e:
            if attempt < 2:
                wait = 2 ** attempt + (1 if "429" in str(e) else 0)
                time.sleep(wait)
            else:
                logger.warning(f"预测失败（3次重试）: {text[:40]}... 错误: {e}")
                return {"id": item.get("id", ""), "text": text, "entities": [], "relations": []}

# ===== 断点续传 =====
results = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for r in existing:
        results[r.get("id", r.get("text", ""))] = r
    logger.info(f"断点续传：已加载 {len(results)} 条已有结果")

lock = threading.Lock()
save_counter = [0]

def save_results():
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(results.values()), f, ensure_ascii=False, indent=2)

def process_item(item):
    key = item.get("id", item.get("text", ""))
    if key in results:
        return None  # 跳过已处理

    result = predict_one(item)

    with lock:
        results[key] = result
        save_counter[0] += 1
        if save_counter[0] % SAVE_EVERY == 0:
            save_results()
            logger.info(f"已保存 {len(results)}/{len(TEST_DATA)} 条")

    return result

# ===== 主流程 =====
if __name__ == "__main__":
    logger.info(f"=== v12 ReverseNER + SCIR 预测开始 ===")
    logger.info(f"模型: {MODEL}, 并发: {WORKERS}, RAG: {TOP_K_RAG}条训练集 + {TOP_K_SYN}条合成")
    logger.info(f"SCIR 自纠正: {'启用' if SCIR_ENABLED else '禁用'}")
    logger.info(f"待处理: {len(TEST_DATA) - len(results)} 条（共 {len(TEST_DATA)} 条）")

    pending = [item for item in TEST_DATA
               if item.get("id", item.get("text", "")) not in results]

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(process_item, item): item for item in pending}
        done = 0
        failed = 0
        for future in as_completed(futures):
            try:
                result = future.result()
                if result is not None:
                    done += 1
            except Exception as e:
                failed += 1
                logger.error(f"任务异常: {e}")

    save_results()
    logger.info(f"=== v12 预测完成 ===")
    logger.info(f"成功: {done}, 失败: {failed}, 总计: {len(results)}")

    # 输出统计
    total_rels = sum(len(r.get("relations", [])) for r in results.values())
    no_rel = sum(1 for r in results.values() if not r.get("relations"))
    logger.info(f"关系均值: {total_rels/len(results):.2f}/条")
    logger.info(f"无关系比例: {no_rel/len(results)*100:.1f}%")
    logger.info(f"（官方期望：2.80/条，32.7%）")
