#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v8 — 两阶段管道 (NER → RE Pipeline)
============================================================
学术依据：
  Lu et al. (2025). CROSSAGENTIE: Cross-Type and Cross-Task Multi-Agent LLM
  Collaboration for Zero-Shot Information Extraction. ACL 2025 Findings.
  https://aclanthology.org/2025.findings-acl.718/

核心思路：
  将原来"一次性同时预测 NER + RE"的复杂任务，拆分为两个独立的、更简单的子任务：
  
  阶段 1 (NER Agent)：
    - 只负责识别实体，不预测关系
    - 任务更简单，准确率更高
    - 使用 RAG 动态检索相似训练样本
  
  阶段 2 (RE Agent)：
    - 接收原文 + 阶段 1 预测的实体列表
    - 只在给定的实体对之间判断关系（大幅缩小搜索空间）
    - 使用 c-ICL 硬负样本避免过标

优势：
  - 降低单次任务复杂度，减少 LLM 幻觉
  - RE 阶段的搜索空间从"所有可能的实体对"缩小到"已识别的实体对"
  - 两个阶段可以独立优化

运行前提：
  pip install scikit-learn openai

输出：submit_v8_pipeline.json
"""
import json
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

# ===== 路径配置 =====
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v8_pipeline.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gpt-4.1-mini"
WORKERS    = 10   # 管道模式每条需要 2 次 API 调用，适当降低并发
SAVE_EVERY = 20
TOP_K      = 4

# ===== 非法三元组 =====
ILLEGAL_TRIPLETS = {
    ('VAR',   'CON', 'CROP'),
    ('GENE',  'CON', 'CROP'),
    ('CROSS', 'CON', 'CROP'),
    ('MRK',   'AFF', 'TRT'),
    ('GENE',  'AFF', 'ABS'),
}

# ===== 加载数据 =====
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)

# ===== 构建 TF-IDF 检索索引 =====
print("正在构建 TF-IDF 检索索引（1000 条训练集）...")
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)
print(f"TF-IDF 索引构建完成，维度：{TRAIN_MATRIX.shape}")


def retrieve_top_k(query_text: str, k: int = TOP_K) -> list:
    query_vec = tfidf.transform([query_text])
    sims = cosine_similarity(query_vec, TRAIN_MATRIX).flatten()
    top_indices = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[idx] for idx in top_indices if sims[idx] > 0.01][:k]


def build_ner_fewshot(samples: list) -> str:
    """构建 NER 阶段的 Few-shot 示例（只含实体，不含关系）"""
    lines = []
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Output: {json.dumps({"entities": ents}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


def build_re_fewshot(samples: list) -> str:
    """构建 RE 阶段的 Few-shot 示例（含实体列表和关系）"""
    lines = []
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [
            {"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]}
            for r in s["relations"]
        ]
        ent_list = json.dumps(ents, ensure_ascii=False)
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Entities: {ent_list}')
        lines.append(f'Output: {json.dumps({"relations": rels}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


# ===== 阶段 1 系统提示词（NER 专用）=====
NER_SYSTEM = """You are an expert Named Entity Recognition (NER) annotator for crop breeding literature.

## Entity Types (12)
CROP: crop species (e.g., sorghum, barley, millet, quinoa, foxtail millet)
VAR: cultivar/variety name (e.g., BTx623, Morex, Pioneer)
GENE: gene name or ID (e.g., Dw3, HvCBF4, SbDREB)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1, qGY-2H)
MRK: molecular marker (e.g., Xgwm11, RM223, SNP markers)
TRT: trait/phenotype (e.g., drought tolerance, grain yield, plant height, starch content)
ABS: abiotic stress (e.g., drought, heat, salinity, cold, waterlogging)
BIS: biotic stress (e.g., Fusarium, rust, aphid, Colletotrichum)
BM: breeding method (GWAS, QTL mapping, MAS, MABC, backcross — NOT lab techniques like RNA-seq/PCR)
CHR: chromosome identifier (e.g., 2H, chr3, 7A — strip "chromosome" prefix)
CROSS: hybrid/segregating population (RILs, DH lines, F2 population — NOT VAR)
GST: growth stage (e.g., seedling stage, heading stage, anthesis, flowering)

## Rules
1. Entity "text" MUST be an EXACT substring of the input sentence.
2. Do NOT annotate lab techniques (RNA-seq, RT-qPCR, CRISPR, ddRAD-seq, PCR) as BM.
3. RILs, DH lines, F2 populations → CROSS (not VAR).
4. Strip type prefixes: "marker Xgwm11" → "Xgwm11" (MRK); "chromosome 2H" → "2H" (CHR).
5. Output valid JSON only. No explanation. No markdown fences.

## Output Format
{"entities": [{"text": "<exact substring>", "label": "<TYPE>"}]}"""

# ===== 阶段 2 系统提示词（RE 专用）=====
RE_SYSTEM = """You are an expert Relation Extraction (RE) annotator for crop breeding literature.
You are given a text and a list of pre-identified entities. Your task is to identify relations ONLY between the provided entities.

## Relation Types (6)
AFF: biological causation — REQUIRES explicit causal verbs: regulates/controls/affects/influences/increases/decreases/promotes/inhibits/encodes/determines
LOI: physical mapping — REQUIRES explicit mapping language: mapped/located/associated with/linked/detected on/identified on/found on
HAS: possession — crop/variety POSSESSES a trait (not just mentioned together)
CON: composition — CROP contains VAR/GENE
USE: head uses breeding method
OCI: occurs at growth stage

## Critical Rules
1. LOI(QTL→TRT) is the MOST COMMON LOI pattern (31%). Never convert to AFF.
2. 32.7% of sentences have NO relations. Output {"relations": []} when no clear semantic link exists.
3. Do NOT create relations just because two entities appear in the same sentence.
4. AFF requires EXPLICIT causal verbs. LOI requires EXPLICIT mapping language.
5. HAS requires the crop/variety to POSSESS the trait, not just be mentioned with it.
6. Output valid JSON only. No explanation. No markdown fences.

## Hard Negative Examples (AVOID these mistakes)
- QTL and TRT in same sentence but no mapping language → relations: []
- CROP and TRT in same sentence but no possession language → relations: []
- GENE and TRT in same sentence but no causal verb → relations: []

## Output Format
{"relations": [{"head": "<text>", "head_type": "<TYPE>", "tail": "<text>", "tail_type": "<TYPE>", "label": "<REL>"}]}"""


# ===== 偏移量解析 =====
def resolve_entities(text: str, raw_entities: list):
    """解析实体偏移量"""
    entities_out = []
    used_spans = set()
    entity_map = {}

    for e in raw_entities:
        et = e.get("text", "").strip()
        lb = e.get("label", "")
        if not et or not lb:
            continue
        idx = text.find(et)
        while idx != -1 and (idx, idx + len(et)) in used_spans:
            idx = text.find(et, idx + 1)
        if idx == -1:
            lo = text.lower().find(et.lower())
            if lo != -1 and (lo, lo + len(et)) not in used_spans:
                idx = lo
            else:
                continue
        s, en = idx, idx + len(et)
        used_spans.add((s, en))
        actual = text[s:en]
        entities_out.append({"start": s, "end": en, "text": actual, "label": lb})
        if et not in entity_map:
            entity_map[et] = (s, en, actual, lb)

    return entities_out, entity_map


def resolve_relations(raw_relations: list, entity_map: dict):
    """解析关系偏移量"""
    relations_out = []
    for r in raw_relations:
        ht  = r.get("head", "").strip()
        tt  = r.get("tail", "").strip()
        hty = r.get("head_type", "")
        tty = r.get("tail_type", "")
        rl  = r.get("label", "")
        if not all([ht, tt, hty, tty, rl]):
            continue
        if (hty, rl, tty) in ILLEGAL_TRIPLETS:
            continue
        if ht not in entity_map or tt not in entity_map:
            continue
        hs, he, ha, _ = entity_map[ht]
        ts, te, ta, _ = entity_map[tt]
        relations_out.append({
            "head": ha, "head_start": hs, "head_end": he, "head_type": hty,
            "tail": ta, "tail_start": ts, "tail_end": te, "tail_type": tty,
            "label": rl
        })
    return relations_out


# ===== 单条预测（两阶段管道）=====
_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one(idx: int, text: str):
    client = get_client()
    top_k_samples = retrieve_top_k(text, k=TOP_K)

    # ===== 阶段 1：NER =====
    ner_fewshot = build_ner_fewshot(top_k_samples)
    entities_out = []
    entity_map = {}

    for attempt in range(3):
        try:
            ner_user = (
                f"## Examples\n{ner_fewshot}\n"
                f"## Now annotate entities only:\n"
                f"Input: {text}\n"
                f"Output:"
            )
            resp1 = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": NER_SYSTEM},
                    {"role": "user",   "content": ner_user}
                ],
                temperature=0,
                max_tokens=1024
            )
            raw1 = resp1.choices[0].message.content.strip()
            raw1 = re.sub(r'^```json\s*', '', raw1)
            raw1 = re.sub(r'^```\s*',     '', raw1)
            raw1 = re.sub(r'\s*```$',     '', raw1)
            parsed1 = json.loads(raw1)
            entities_out, entity_map = resolve_entities(text, parsed1.get("entities", []))
            break
        except Exception:
            if attempt == 2:
                return idx, text, [], [], "NER_failed"
            time.sleep(1)

    if not entities_out:
        return idx, text, [], [], None  # 无实体，无关系

    # ===== 阶段 2：RE（基于已识别实体）=====
    re_fewshot = build_re_fewshot(top_k_samples)
    ent_list_for_re = json.dumps(
        [{"text": e["text"], "label": e["label"]} for e in entities_out],
        ensure_ascii=False
    )
    relations_out = []

    for attempt in range(3):
        try:
            re_user = (
                f"## Examples\n{re_fewshot}\n"
                f"## Now extract relations:\n"
                f"Input: {text}\n"
                f"Entities: {ent_list_for_re}\n"
                f"Output:"
            )
            resp2 = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": RE_SYSTEM},
                    {"role": "user",   "content": re_user}
                ],
                temperature=0,
                max_tokens=1024
            )
            raw2 = resp2.choices[0].message.content.strip()
            raw2 = re.sub(r'^```json\s*', '', raw2)
            raw2 = re.sub(r'^```\s*',     '', raw2)
            raw2 = re.sub(r'\s*```$',     '', raw2)
            parsed2 = json.loads(raw2)
            relations_out = resolve_relations(parsed2.get("relations", []), entity_map)
            break
        except Exception:
            if attempt == 2:
                pass  # RE 失败时保留实体，关系为空
            time.sleep(1)

    return idx, text, entities_out, relations_out, None


# ===== 主程序 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS} | 两阶段管道模式")
print(f"注意：每条文本需要 2 次 API 调用（NER + RE），总调用次数约 {len(pending)*2}")

save_lock = threading.Lock()
completed_count = [0]
failed_list = []


def save_results():
    ordered = [results_dict[i] for i in sorted(results_dict.keys())]
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)


with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {
        executor.submit(predict_one, i, TEST_DATA[i]["text"]): i
        for i in pending
    }
    for future in as_completed(futures):
        idx, text, ents, rels, err = future.result()
        with save_lock:
            results_dict[idx] = {"text": text, "entities": ents, "relations": rels}
            completed_count[0] += 1
            done = completed_count[0]
            total_done = len(results_dict)

            status = f"✓ 实体:{len(ents)} 关系:{len(rels)}"
            if err:
                failed_list.append(idx)
                status = f"⚠ 失败({err})"
            print(f"[{idx+1:>3}/{len(TEST_DATA)}] {text[:50]}... {status}")

            if done % SAVE_EVERY == 0:
                save_results()
                print(f"  >>> 已保存 {total_done}/{len(TEST_DATA)} 条 <<<")

save_results()
print(f"\n===== 全部完成 =====")
print(f"总条数: {len(TEST_DATA)} | 成功: {len(TEST_DATA)-len(failed_list)} | 失败: {len(failed_list)}")
if failed_list:
    print(f"失败索引: {sorted(failed_list)}")
print(f"输出: {OUTPUT_PATH}")
