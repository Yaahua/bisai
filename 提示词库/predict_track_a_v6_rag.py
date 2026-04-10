#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v6 — RAG 动态提示词
===========================================
学术依据：
  Ge et al. (2026). Improving few-shot NER using structured dynamic prompting with RAG.
  npj Artificial Intelligence, 2(39). https://www.nature.com/articles/s44387-025-00062-2

核心改进（相比 v5 静态 Few-shot）：
  1. 放弃固定的 fewshot_v3.json，改为 TF-IDF 实时检索最相似的 Top-K 训练样本
  2. 检索池：官方 train.json 全量 1000 条
  3. 每条测试文本独立检索，保证语义相关性
  4. 保留 v5 的 resolve() 偏移量计算逻辑（字符级精确匹配）
  5. 保留 v5 的非法三元组过滤（post_process 逻辑内嵌）

运行前提：
  pip install scikit-learn openai

输出：submit_v6_rag.json（格式与官方要求一致）
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
TRAIN_PATH   = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH    = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_v6_rag.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL     = "gpt-4.1-mini"   # 可替换为 gpt-4.1 / gemini-2.5-flash
WORKERS   = 20               # 并发线程数
SAVE_EVERY = 20              # 每完成多少条保存一次
TOP_K     = 5                # RAG 检索的 Few-shot 样本数量（论文推荐 5-10）

# ===== 非法三元组（训练集中从未出现，全部删除）=====
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
tfidf = TfidfVectorizer(
    ngram_range=(1, 2),   # 使用 unigram + bigram，对专业术语效果更好
    max_features=50000,
    sublinear_tf=True
)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)
print(f"TF-IDF 索引构建完成，维度：{TRAIN_MATRIX.shape}")


def retrieve_top_k(query_text: str, k: int = TOP_K) -> list:
    """
    对给定查询文本，从训练集中检索最相似的 Top-K 样本。
    返回训练集样本列表（含 text, entities, relations）。
    """
    query_vec = tfidf.transform([query_text])
    sims = cosine_similarity(query_vec, TRAIN_MATRIX).flatten()
    # 取相似度最高的 Top-K 索引（排除相似度为 0 的）
    top_indices = np.argsort(sims)[::-1][:k]
    results = []
    for idx in top_indices:
        if sims[idx] > 0.01:  # 过滤掉完全不相关的样本
            results.append(TRAIN_DATA[idx])
    return results[:k]


def build_dynamic_fewshot(samples: list) -> str:
    """
    将检索到的训练样本格式化为 Few-shot 示例块。
    """
    lines = []
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [
            {
                "head": r["head"], "head_type": r["head_type"],
                "tail": r["tail"], "tail_type": r["tail_type"],
                "label": r["label"]
            }
            for r in s["relations"]
        ]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


# ===== 系统提示词（结构化静态部分，参考论文 6 要素框架）=====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Task Description
Extract named entities and relations from agricultural breeding texts. Output ONLY valid JSON.

## Entity Types (12)
CROP: crop species (e.g., sorghum, barley, millet)
VAR: cultivar/variety name (e.g., BTx623, Morex)
GENE: gene name or ID (e.g., Dw3, HvCBF4)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1)
MRK: molecular marker (e.g., Xgwm11, RM223, SNP)
TRT: trait/phenotype (e.g., drought tolerance, grain yield, plant height)
ABS: abiotic stress (e.g., drought, heat, salinity, cold)
BIS: biotic stress (e.g., Fusarium, rust, aphid)
BM: breeding method (e.g., GWAS, QTL mapping, MAS, MABC)
CHR: chromosome identifier (e.g., 2H, chr3, 7A)
CROSS: hybrid/segregating population (e.g., RILs, DH lines, F2 population)
GST: growth stage (e.g., seedling stage, heading stage, anthesis)

## Relation Types (6)
AFF: head AFFECTS tail — biological causation (e.g., ABS→TRT, GENE→TRT, ABS→GENE)
LOI: head LOCATED ON / ASSOCIATED WITH tail — physical mapping (e.g., QTL→TRT, QTL→CHR, GENE→TRT, MRK→CHR)
HAS: head HAS trait — possession (e.g., VAR→TRT, CROP→TRT)
CON: head CONTAINS tail — composition (e.g., CROP→VAR, CROP→GENE)
USE: head USES method (e.g., VAR→BM, CROP→BM)
OCI: head OCCURS AT stage (e.g., TRT→GST, ABS→GST)

## Critical Annotation Rules
1. LOI(QTL→TRT) is the MOST COMMON LOI pattern (31%). Never convert it to AFF.
2. 32.7% of sentences have NO relations at all. Output empty relations [] when no clear semantic link exists.
3. Entity "text" MUST be an EXACT substring of the input sentence (case-sensitive).
4. Do NOT annotate lab techniques (ddRAD-seq, RT-qPCR, RNA-seq, CRISPR, PCR) as BM.
5. RILs, DH lines, F2 populations → CROSS (not VAR).
6. Strip type prefixes: "marker Xgwm11" → entity text is "Xgwm11" (MRK); "chromosome 2H" → "2H" (CHR).
7. AFF head = influencing party (ABS/GENE/MRK/QTL/BIS/BM); tail = TRT/GENE.
8. LOI vs AFF distinction: LOI = physical mapping/location; AFF = biological function/causation.
9. Output valid JSON only. No explanation. No markdown fences.

## Output Format
{"entities": [{"text": "<exact substring>", "label": "<TYPE>"}], "relations": [{"head": "<text>", "head_type": "<TYPE>", "tail": "<text>", "tail_type": "<TYPE>", "label": "<REL>"}]}"""


# ===== 偏移量解析（与 v5 相同，字符级精确匹配）=====
def resolve(text: str, raw: dict):
    entities_out, relations_out = [], []
    used_spans = set()
    entity_map = {}

    for e in raw.get("entities", []):
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

    for r in raw.get("relations", []):
        ht  = r.get("head", "").strip()
        tt  = r.get("tail", "").strip()
        hty = r.get("head_type", "")
        tty = r.get("tail_type", "")
        rl  = r.get("label", "")
        if not all([ht, tt, hty, tty, rl]):
            continue
        # 过滤非法三元组
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
    return entities_out, relations_out


# ===== 单条预测（线程安全，每个线程独立 client）=====
_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one(idx: int, text: str):
    client = get_client()
    # RAG：为当前文本动态检索最相似的 Top-K 训练样本
    top_k_samples = retrieve_top_k(text, k=TOP_K)
    fewshot_block = build_dynamic_fewshot(top_k_samples)

    for attempt in range(3):
        try:
            extra = "\nRemember: output ONLY valid JSON. Entity text must be exact substrings." if attempt > 0 else ""
            user_msg = (
                f"## Retrieved Examples (most similar to your input)\n"
                f"{fewshot_block}\n"
                f"## Now annotate:\n"
                f"Input: {text}\n"
                f"Output:{extra}"
            )
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": user_msg}
                ],
                temperature=0,
                max_tokens=2048
            )
            raw_str = resp.choices[0].message.content.strip()
            raw_str = re.sub(r'^```json\s*', '', raw_str)
            raw_str = re.sub(r'^```\s*',     '', raw_str)
            raw_str = re.sub(r'\s*```$',     '', raw_str)
            raw = json.loads(raw_str)
            ents, rels = resolve(text, raw)
            return idx, text, ents, rels, None
        except json.JSONDecodeError as ex:
            if attempt == 2:
                return idx, text, [], [], f"JSONError: {str(ex)[:40]}"
        except Exception as ex:
            if attempt == 2:
                return idx, text, [], [], f"Error: {str(ex)[:40]}"
            time.sleep(1)
    return idx, text, [], [], "max_retries"


# ===== 主程序 =====
results_dict = {}
# 断点续传
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS} | RAG Top-K: {TOP_K}")

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

# 最终保存
save_results()
print(f"\n===== 全部完成 =====")
print(f"总条数: {len(TEST_DATA)} | 成功: {len(TEST_DATA)-len(failed_list)} | 失败: {len(failed_list)}")
if failed_list:
    print(f"失败索引: {sorted(failed_list)}")
print(f"输出: {OUTPUT_PATH}")
