#!/usr/bin/env python3.11
"""
v14 召回率补充预测
==================
策略：
- 找出 ensemble_v3 中 153 条无关系的句子
- 用更激进的 Prompt（强调"不要遗漏"）重新预测这些句子
- 将预测到的合法关系补充到 ensemble_v3 中
- 生成 submit_v14_recall_boost.json

这是一种精准的"召回率修复"，不影响 ensemble_v3 的高精确率部分
"""
import json, os, time, logging, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

client = OpenAI()
MODEL  = "gpt-4.1-mini"

E3_PATH    = '/home/ubuntu/bisai/数据/A榜/submit_ensemble_v3.json'
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
OUT_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_v14_recall_boost.json'

# 从训练集加载合法三元组
with open(TRAIN_PATH) as f:
    train_data = json.load(f)

VALID_TRIPLES = set()
for item in train_data:
    for rel in item.get('relations', []):
        h = rel.get('head_type','')
        l = rel.get('label','')
        t = rel.get('tail_type','')
        if h and l and t:
            VALID_TRIPLES.add(f"{h}-{l}-{t}")

# 构建 RAG 检索库（从训练集中有关系的句子）
train_with_rels = [item for item in train_data if item.get('relations')]
train_texts = [item['text'] for item in train_with_rels]
vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
train_matrix = vectorizer.fit_transform(train_texts)

def get_similar_examples(query_text, k=4):
    """检索最相似的训练样本作为 Few-shot 示例"""
    query_vec = vectorizer.transform([query_text])
    sims = cosine_similarity(query_vec, train_matrix).flatten()
    top_k = np.argsort(sims)[-k:][::-1]
    examples = []
    for idx in top_k:
        item = train_with_rels[idx]
        if sims[idx] < 0.05:
            continue
        examples.append(item)
    return examples

def format_example(item):
    """格式化训练样本为 Prompt 示例"""
    entities_str = json.dumps(
        [{"text": e["text"], "label": e["label"]} for e in item.get("entities", [])],
        ensure_ascii=False
    )
    relations_str = json.dumps(
        [{"head": r["head"], "head_type": r["head_type"],
          "tail": r["tail"], "tail_type": r["tail_type"],
          "label": r["label"]} for r in item.get("relations", [])],
        ensure_ascii=False
    )
    return f'Text: "{item["text"]}"\nEntities: {entities_str}\nRelations: {relations_str}'

SYSTEM_PROMPT = """You are an expert in agricultural genetics and molecular breeding. Your task is to extract ALL biomedical entities and relationships from scientific text about crop genetics.

CRITICAL: This text likely contains relationships. Do NOT return empty relations unless you are absolutely certain there are none.

Entity types: CROP, VAR, GENE, QTL, MRK, TRT, BM, LOI, CHR, ABS, BIS, CROSS, GST

Relationship labels: CON, HAS, USE, OCI, AFF, LOI

Output ONLY valid JSON with this exact format:
{
  "entities": [{"text": "...", "label": "TYPE"}],
  "relations": [{"head": "...", "head_type": "TYPE", "tail": "...", "tail_type": "TYPE", "label": "REL"}]
}"""

def predict_one(item):
    """对单条无关系句子进行补充预测"""
    text = item['text']
    examples = get_similar_examples(text, k=4)

    few_shot = ""
    if examples:
        few_shot = "\n\nHere are similar examples with their annotations:\n\n"
        for ex in examples:
            few_shot += format_example(ex) + "\n\n"

    user_prompt = f"""{few_shot}Now annotate this text. Be thorough - look for ALL relationships:

Text: "{text}"

Return JSON only."""

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                timeout=30
            )
            raw = resp.choices[0].message.content.strip()
            # 提取 JSON
            match = re.search(r'\{[\s\S]*\}', raw)
            if not match:
                continue
            result = json.loads(match.group())
            entities  = result.get("entities", [])
            relations = result.get("relations", [])

            # 过滤非法三元组
            valid_rels = []
            for rel in relations:
                h_type = rel.get("head_type","")
                t_type = rel.get("tail_type","")
                label  = rel.get("label","")
                triple_key = f"{h_type}-{label}-{t_type}"
                if triple_key in VALID_TRIPLES:
                    # 验证实体在原文中出现
                    if rel.get("head","") in text and rel.get("tail","") in text:
                        valid_rels.append(rel)

            return text, entities, valid_rels

        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                logger.warning(f"失败: {text[:30]} - {e}")
                return text, [], []

    return text, [], []

# 加载 ensemble_v3
with open(E3_PATH) as f:
    e3_data = json.load(f)

# 找出无关系的句子
no_rel_items = [item for item in e3_data if not item.get('relations')]
logger.info(f"ensemble_v3 无关系句子: {len(no_rel_items)} 条，开始补充预测...")

# 并发预测
results = {}
with ThreadPoolExecutor(max_workers=15) as executor:
    futures = {executor.submit(predict_one, item): item for item in no_rel_items}
    done = 0
    for future in as_completed(futures):
        text_key, entities, relations = future.result()
        results[text_key] = (entities, relations)
        done += 1
        if done % 20 == 0:
            logger.info(f"已完成 {done}/{len(no_rel_items)} 条")

# 合并结果
merged_data = []
added_total = 0
filled_items = 0

for e3_item in e3_data:
    text_key = e3_item.get("text", "")
    if text_key in results:
        new_entities, new_relations = results[text_key]
        if new_relations:
            filled_items += 1
            added_total += len(new_relations)
        merged_data.append({
            "text":      text_key,
            "entities":  e3_item.get("entities",[]) or new_entities,
            "relations": new_relations  # 用新预测替换空关系
        })
    else:
        merged_data.append(e3_item)

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

total = len(merged_data)
total_rels = sum(len(r.get("relations",[])) for r in merged_data)
no_rel = sum(1 for r in merged_data if not r.get("relations"))

logger.info(f"=== v14 召回率补充完成 ===")
logger.info(f"  补充了关系的句子: {filled_items}/{len(no_rel_items)} 条")
logger.info(f"  新增关系总数: {added_total} 条")
logger.info(f"  关系均值: {total_rels/total:.2f}/条 (ensemble_v3 为 2.16)")
logger.info(f"  无关系比例: {no_rel/total*100:.1f}% (ensemble_v3 为 38.2%)")
logger.info(f"  输出: {OUT_PATH}")
