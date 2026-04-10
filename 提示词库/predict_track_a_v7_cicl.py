#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v7 — RAG + 对比上下文学习 (c-ICL)
==========================================================
学术依据：
  Mo et al. (2024). c-ICL: Contrastive In-context Learning for Information Extraction.
  Findings of EMNLP 2024. https://arxiv.org/html/2402.11254v2

核心改进（相比 v6 纯 RAG）：
  1. 在 Prompt 中引入"硬负样本"（Hard Negative Examples）
     即：容易犯错的典型错误案例 + 正确答案对比 + 错误原因说明
  2. 硬负样本针对 bisai 仓库历史失分点精心设计：
     - QTL/GENE + TRT 同现但无明确关系 → 不标 LOI/AFF
     - CROP + TRT 并列提及 → 不标 HAS
     - 实验技术（RNA-seq 等）→ 不标 BM
     - 无关系的背景描述句 → 空关系 []
  3. 保留 v6 的 TF-IDF RAG 动态检索（Top-K 正样本）
  4. 保留非法三元组过滤

运行前提：
  pip install scikit-learn openai

输出：submit_v7_cicl.json
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
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gpt-4.1-mini"
WORKERS    = 20
SAVE_EVERY = 20
TOP_K      = 4   # v7 减少正样本数量，腾出空间给硬负样本（总 prompt 长度控制）

# ===== 非法三元组 =====
ILLEGAL_TRIPLETS = {
    ('VAR',   'CON', 'CROP'),
    ('GENE',  'CON', 'CROP'),
    ('CROSS', 'CON', 'CROP'),
    ('MRK',   'AFF', 'TRT'),
    ('GENE',  'AFF', 'ABS'),
}

# ===== 硬负样本（c-ICL 核心）=====
# 基于 bisai 仓库历史失分点精心设计，每个样本包含：
#   - 容易犯错的输入
#   - 错误的预测（Bad Output）
#   - 正确的预测（Good Output）
#   - 错误原因（Reason）
HARD_NEGATIVES = """
## Hard Negative Examples (Common Mistakes to AVOID)

### Mistake 1: Do NOT create LOI(QTL→TRT) when there is no explicit mapping statement
Input: "Several QTLs were detected in this study. Grain yield is an important trait in barley."
Bad Output: {"entities": [{"text": "QTLs", "label": "QTL"}, {"text": "Grain yield", "label": "TRT"}, {"text": "barley", "label": "CROP"}], "relations": [{"head": "QTLs", "head_type": "QTL", "tail": "Grain yield", "tail_type": "TRT", "label": "LOI"}]}
Good Output: {"entities": [{"text": "QTLs", "label": "QTL"}, {"text": "Grain yield", "label": "TRT"}, {"text": "barley", "label": "CROP"}], "relations": []}
Reason: The two sentences are independent. There is no explicit "mapped to", "associated with", or "located on" language linking the QTL to grain yield. Do NOT create LOI just because QTL and TRT appear in the same passage.

### Mistake 2: Do NOT create HAS(CROP→TRT) when crop and trait are merely mentioned together
Input: "Sorghum is an important cereal crop. Drought tolerance is a critical trait for crop improvement."
Bad Output: {"entities": [{"text": "Sorghum", "label": "CROP"}, {"text": "Drought tolerance", "label": "TRT"}], "relations": [{"head": "Sorghum", "head_type": "CROP", "tail": "Drought tolerance", "tail_type": "TRT", "label": "HAS"}]}
Good Output: {"entities": [{"text": "Sorghum", "label": "CROP"}, {"text": "Drought tolerance", "label": "TRT"}], "relations": []}
Reason: HAS requires that the crop POSSESSES the trait (e.g., "Sorghum has drought tolerance" or "drought-tolerant sorghum"). A general background statement does not establish a HAS relationship.

### Mistake 3: Do NOT annotate lab/sequencing techniques as BM (Breeding Method)
Input: "RNA-seq analysis was performed to identify differentially expressed genes under drought stress."
Bad Output: {"entities": [{"text": "RNA-seq", "label": "BM"}, {"text": "drought stress", "label": "ABS"}], "relations": [{"head": "RNA-seq", "head_type": "BM", "tail": "drought stress", "tail_type": "ABS", "label": "AFF"}]}
Good Output: {"entities": [{"text": "drought stress", "label": "ABS"}], "relations": []}
Reason: RNA-seq, RT-qPCR, CRISPR, ddRAD-seq, PCR are laboratory/sequencing techniques, NOT breeding methods. BM should be GWAS, QTL mapping, MAS, MABC, backcross, etc.

### Mistake 4: Do NOT create AFF(GENE→TRT) without explicit causal language
Input: "The Dw3 gene and plant height were both studied in this sorghum population."
Bad Output: {"entities": [{"text": "Dw3", "label": "GENE"}, {"text": "plant height", "label": "TRT"}, {"text": "sorghum", "label": "CROP"}], "relations": [{"head": "Dw3", "head_type": "GENE", "tail": "plant height", "tail_type": "TRT", "label": "AFF"}]}
Good Output: {"entities": [{"text": "Dw3", "label": "GENE"}, {"text": "plant height", "label": "TRT"}, {"text": "sorghum", "label": "CROP"}], "relations": []}
Reason: AFF requires explicit causal verbs: regulates, controls, affects, influences, increases, decreases, promotes, inhibits, encodes, etc. Simply studying both entities together does NOT establish AFF.
"""

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
    results = []
    for idx in top_indices:
        if sims[idx] > 0.01:
            results.append(TRAIN_DATA[idx])
    return results[:k]


def build_dynamic_fewshot(samples: list) -> str:
    lines = ["## Retrieved Positive Examples (most similar to your input)"]
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [
            {"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]}
            for r in s["relations"]
        ]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


# ===== 系统提示词（结构化，含 c-ICL 硬负样本）=====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Task Description
Extract named entities and relations from agricultural breeding texts. Output ONLY valid JSON.

## Entity Types (12)
CROP: crop species | VAR: cultivar/variety | GENE: gene name/ID | QTL: quantitative trait loci
MRK: molecular marker | TRT: trait/phenotype | ABS: abiotic stress | BIS: biotic stress
BM: breeding method (GWAS/QTL mapping/MAS/MABC/backcross — NOT lab techniques)
CHR: chromosome identifier | CROSS: hybrid population (RILs/DH lines/F2) | GST: growth stage

## Relation Types (6)
AFF: biological causation — needs explicit causal verbs (regulates/controls/affects/increases/decreases/promotes/inhibits/encodes)
LOI: physical mapping — needs explicit mapping language (mapped/located/associated with/linked/detected on)
HAS: possession — crop/variety POSSESSES a trait (not just mentioned together)
CON: composition — CROP contains VAR/GENE
USE: head uses breeding method
OCI: occurs at growth stage

## Absolute Rules
1. LOI(QTL→TRT) is the most common LOI pattern (31%). Never convert to AFF.
2. 32.7% of sentences have NO relations. Output [] when no clear semantic link exists.
3. Entity "text" MUST be an EXACT substring of the input sentence.
4. Do NOT annotate lab techniques (RNA-seq/RT-qPCR/CRISPR/ddRAD-seq/PCR) as BM.
5. RILs/DH lines/F2 populations → CROSS (not VAR).
6. Strip type prefixes: "marker Xgwm11" → "Xgwm11" (MRK); "chromosome 2H" → "2H" (CHR).
7. Output valid JSON only. No explanation. No markdown fences.""" + "\n" + HARD_NEGATIVES


# ===== 偏移量解析 =====
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


# ===== 单条预测 =====
_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one(idx: int, text: str):
    client = get_client()
    top_k_samples = retrieve_top_k(text, k=TOP_K)
    fewshot_block = build_dynamic_fewshot(top_k_samples)

    for attempt in range(3):
        try:
            extra = "\nRemember: output ONLY valid JSON. Entity text must be exact substrings." if attempt > 0 else ""
            user_msg = (
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
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS} | RAG Top-K: {TOP_K} | c-ICL 硬负样本: 4条")

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
