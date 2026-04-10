#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v7_v2 — RAG + c-ICL（学术修正版）
=========================================================
学术依据：
  Mo et al. (2024). c-ICL: Contrastive In-context Learning for Information Extraction.
  EMNLP 2024 Findings. https://arxiv.org/html/2402.11254v2

相比 v7 的关键修正（基于学术查证文档）：
  1. 【核心修正】将自然语言硬负样本改为"代码风格 Prompt"（Code-Style Prompts）
     文献 Figure 4-6 明确使用 Python 函数格式，而非自然语言描述
  2. 【核心修正】硬负样本从 generate_hard_negatives.py 自动生成，而非手写
     如果 hard_negatives.json 不存在，回退到内置的手工样本
  3. 正负样本比例：4 正 + 2 负（文献推荐 2:1，Figure 9c）
  4. 温度参数：确定性关系用 0.3，模糊关系用 0.6（文献推荐）

运行前提：
  1. 先运行 generate_hard_negatives.py 生成 hard_negatives.json（可选，有则更好）
  2. pip install scikit-learn openai

输出：submit_v7_cicl_v2.json
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
TRAIN_PATH      = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH       = '/home/ubuntu/official_mgbie/dataset/test_A.json'
HN_PATH         = '/home/ubuntu/bisai/提示词库/hard_negatives.json'  # 自动生成的硬负样本
OUTPUT_PATH     = '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gpt-4.1-mini"
WORKERS    = 20
SAVE_EVERY = 20
TOP_K      = 4   # 正样本数（负样本 2 个，比例 2:1）

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

# ===== 加载硬负样本（自动生成或手工备用）=====
def load_hard_negatives() -> list:
    """加载硬负样本，优先使用自动生成的，否则使用手工备用"""
    if os.path.exists(HN_PATH):
        with open(HN_PATH, encoding='utf-8') as f:
            hn_data = json.load(f)
        print(f"✓ 加载自动生成的硬负样本：{len(hn_data)} 个")
        return hn_data[:2]  # 只取前 2 个（2:1 比例）
    else:
        print("⚠ 未找到 hard_negatives.json，使用内置手工备用样本")
        return []  # 返回空，使用内置备用

HARD_NEGATIVES_DATA = load_hard_negatives()

# ===== 内置手工备用硬负样本（当自动生成文件不存在时使用）=====
# 格式：代码风格 Prompt（文献 Figure 4-6 所示格式）
BUILTIN_CODE_STYLE_HN = '''
## Contrastive Examples (Code-Style, showing common mistakes)

# Example of WRONG annotation (over-predicting relations):
def annotate_wrong():
    text = "Several QTLs were detected in this study. Grain yield is an important trait in barley."
    result = {
        "entities": [{"text": "QTLs", "label": "QTL"}, {"text": "Grain yield", "label": "TRT"}, {"text": "barley", "label": "CROP"}],
        "relations": [{"head": "QTLs", "head_type": "QTL", "tail": "Grain yield", "tail_type": "TRT", "label": "LOI"}]
    }
    # ERROR: No mapping language ("mapped to", "associated with") between QTL and TRT. Relations should be [].

# Corrected annotation:
def annotate_correct():
    text = "Several QTLs were detected in this study. Grain yield is an important trait in barley."
    result = {
        "entities": [{"text": "QTLs", "label": "QTL"}, {"text": "Grain yield", "label": "TRT"}, {"text": "barley", "label": "CROP"}],
        "relations": []
    }
    # CORRECT: Two independent sentences, no explicit mapping relationship.

# Example of WRONG annotation (creating AFF without causal verb):
def annotate_wrong_2():
    text = "The Dw3 gene and plant height were both studied in this sorghum population."
    result = {
        "entities": [{"text": "Dw3", "label": "GENE"}, {"text": "plant height", "label": "TRT"}, {"text": "sorghum", "label": "CROP"}],
        "relations": [{"head": "Dw3", "head_type": "GENE", "tail": "plant height", "tail_type": "TRT", "label": "AFF"}]
    }
    # ERROR: AFF requires explicit causal verbs: regulates/controls/affects/increases/decreases/promotes/inhibits.

# Corrected annotation:
def annotate_correct_2():
    text = "The Dw3 gene and plant height were both studied in this sorghum population."
    result = {
        "entities": [{"text": "Dw3", "label": "GENE"}, {"text": "plant height", "label": "TRT"}, {"text": "sorghum", "label": "CROP"}],
        "relations": []
    }
    # CORRECT: "studied" is not a causal verb. No AFF relationship.
'''


def format_hn_as_code_style(hn_item: dict) -> str:
    """将自动生成的硬负样本格式化为代码风格 Prompt"""
    text = hn_item["text"]
    bad  = hn_item["bad_prediction"]
    gold = hn_item["gold"]
    err  = hn_item.get("error_description", "Incorrect annotation")

    bad_ents  = json.dumps(bad.get("entities", []),  ensure_ascii=False)
    bad_rels  = json.dumps(bad.get("relations", []),  ensure_ascii=False)
    gold_ents = json.dumps(gold.get("entities", []), ensure_ascii=False)
    gold_rels = json.dumps(gold.get("relations", []), ensure_ascii=False)

    return f'''
# Auto-generated hard negative example (F1={hn_item.get("f1", 0):.2f}):
def annotate_wrong():
    text = "{text[:100]}..."
    result = {{"entities": {bad_ents}, "relations": {bad_rels}}}
    # ERROR: {err}

def annotate_correct():
    text = "{text[:100]}..."
    result = {{"entities": {gold_ents}, "relations": {gold_rels}}}
    # CORRECT: Matches official annotation standard.
'''


def build_cicl_block() -> str:
    """构建 c-ICL 代码风格对比示例块"""
    if HARD_NEGATIVES_DATA:
        # 使用自动生成的硬负样本
        parts = ["## Contrastive Examples (Code-Style, showing common mistakes)"]
        for hn in HARD_NEGATIVES_DATA:
            parts.append(format_hn_as_code_style(hn))
        return "\n".join(parts)
    else:
        # 使用内置手工备用样本
        return BUILTIN_CODE_STYLE_HN


CICL_BLOCK = build_cicl_block()

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


def build_positive_fewshot(samples: list) -> str:
    """构建正样本 Few-shot 示例（代码风格）"""
    lines = ["## Positive Examples (correct annotations, retrieved by similarity)"]
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [{"head": r["head"], "head_type": r["head_type"],
                 "tail": r["tail"], "tail_type": r["tail_type"],
                 "label": r["label"]} for r in s["relations"]]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


# ===== 系统提示词 =====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Entity Types (12)
CROP: crop species | VAR: cultivar/variety | GENE: gene name/ID | QTL: quantitative trait loci
MRK: molecular marker | TRT: trait/phenotype | ABS: abiotic stress | BIS: biotic stress
BM: breeding method (GWAS/QTL mapping/MAS/MABC — NOT lab techniques like RNA-seq/PCR/CRISPR)
CHR: chromosome identifier | CROSS: hybrid population (RILs/DH lines/F2) | GST: growth stage

## Relation Types (6)
AFF: biological causation (needs: regulates/controls/affects/increases/decreases/promotes/inhibits/encodes)
LOI: physical mapping (needs: mapped/located/associated with/linked/detected on/identified on)
HAS: possession (crop/variety POSSESSES a trait, not just mentioned together)
CON: composition (CROP contains VAR/GENE)
USE: uses breeding method | OCI: occurs at growth stage

## Absolute Rules
1. LOI(QTL→TRT) = most common LOI pattern (31%). NEVER convert to AFF.
2. 32.7% of sentences have NO relations. Output [] when no clear semantic link.
3. Entity "text" MUST be EXACT substring of input sentence.
4. AFF requires EXPLICIT causal verbs. LOI requires EXPLICIT mapping language.
5. Output valid JSON only. No explanation. No markdown fences."""


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
    positive_block = build_positive_fewshot(top_k_samples)

    for attempt in range(3):
        try:
            extra = "\nRemember: output ONLY valid JSON. Entity text must be exact substrings." if attempt > 0 else ""
            user_msg = (
                f"{positive_block}\n"
                f"{CICL_BLOCK}\n"
                f"## Now annotate (apply lessons from contrastive examples above):\n"
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
hn_source = "自动生成" if HARD_NEGATIVES_DATA else "内置手工备用"
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS}")
print(f"RAG Top-K: {TOP_K} 正样本 | c-ICL 硬负样本: 2 个（{hn_source}）| 比例 2:1")

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
