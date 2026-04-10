#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v8_bidirectional — 双向反馈多智能体
===========================================================
学术依据：
  Lu et al. (2025). CROSSAGENTIE: Cross-Type and Cross-Task Multi-Agent LLM
  Collaboration for Zero-Shot Information Extraction. ACL 2025 Findings.
  https://aclanthology.org/2025.findings-acl.718/

相比 v8_pipeline 的关键修正（基于学术查证文档）：
  原 v8 是单向管道（NER → RE），丢失了 CROSSAGENTIE 的核心机制。
  本版本实现真正的双向反馈：
  
  完整流程：
  1. Agent 1 (NER)：识别实体
  2. Agent 2 (RE)：基于实体预测关系
  3. 冲突检测：检查 RE 结果中是否有实体类型冲突（如 RE 认为某实体是 GENE，但 NER 标为 TRT）
  4. 如有冲突 → 回调 Agent 1 (NER) 修正，提供 RE 的反馈意见
  5. Agent 1 修正后 → 重新运行 Agent 2 (RE)
  6. 最多迭代 2 轮（避免无限循环）

优势：
  - 实现了 NER↔RE 的真正双向信息流
  - RE 发现的实体类型不一致会反馈给 NER 修正
  - 比单向管道更接近 CROSSAGENTIE 的原始设计

运行前提：
  pip install scikit-learn openai

输出：submit_v8_bidirectional.json
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
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v8_bidirectional.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gpt-4.1-mini"
WORKERS    = 10   # 双向反馈每条需要 2-4 次 API 调用
SAVE_EVERY = 20
TOP_K      = 4
MAX_ROUNDS = 2    # 最大双向迭代轮数

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
    lines = []
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Output: {json.dumps({"entities": ents}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


def build_re_fewshot(samples: list) -> str:
    lines = []
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [{"head": r["head"], "head_type": r["head_type"],
                 "tail": r["tail"], "tail_type": r["tail_type"],
                 "label": r["label"]} for r in s["relations"]]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Entities: {json.dumps(ents, ensure_ascii=False)}')
        lines.append(f'Output: {json.dumps({"relations": rels}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)


# ===== Agent 1：NER 系统提示词 =====
NER_SYSTEM = """You are an expert Named Entity Recognition (NER) annotator for crop breeding literature.

## Entity Types (12)
CROP: crop species | VAR: cultivar/variety | GENE: gene name/ID | QTL: quantitative trait loci
MRK: molecular marker | TRT: trait/phenotype | ABS: abiotic stress | BIS: biotic stress
BM: breeding method (GWAS/QTL mapping/MAS/MABC — NOT RNA-seq/PCR/CRISPR)
CHR: chromosome identifier | CROSS: hybrid population (RILs/DH lines/F2) | GST: growth stage

## Rules
1. Entity "text" MUST be EXACT substring of input sentence.
2. Do NOT annotate lab techniques as BM.
3. RILs/DH lines/F2 → CROSS (not VAR).
4. Strip type prefixes: "marker Xgwm11" → "Xgwm11" (MRK); "chromosome 2H" → "2H" (CHR).
5. Output valid JSON only: {"entities": [{"text": "...", "label": "..."}]}"""

# ===== Agent 2：RE 系统提示词 =====
RE_SYSTEM = """You are an expert Relation Extraction (RE) annotator for crop breeding literature.
You receive a text and a list of pre-identified entities. Extract relations ONLY between provided entities.

## Relation Types (6)
AFF: biological causation (needs: regulates/controls/affects/increases/decreases/promotes/inhibits/encodes)
LOI: physical mapping (needs: mapped/located/associated with/linked/detected on)
HAS: possession (crop/variety POSSESSES trait, not just mentioned together)
CON: composition (CROP contains VAR/GENE) | USE: uses breeding method | OCI: occurs at growth stage

## Critical Rules
1. LOI(QTL→TRT) is the most common LOI pattern (31%). NEVER convert to AFF.
2. 32.7% of sentences have NO relations. Output {"relations": []} when no clear link.
3. AFF requires EXPLICIT causal verbs. LOI requires EXPLICIT mapping language.
4. Output valid JSON only: {"relations": [...], "entity_type_corrections": [...]}

## Special Output Field
If you believe any entity has a WRONG type (e.g., NER labeled it TRT but it should be GENE),
add it to "entity_type_corrections": [{"text": "...", "current_label": "...", "suggested_label": "..."}]
This feedback will be used to improve NER results."""


def call_llm(client, system: str, user: str, temperature: float = 0) -> dict:
    """调用 LLM，返回解析后的 JSON"""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user}
                ],
                temperature=temperature,
                max_tokens=1024
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'^```\s*',     '', raw)
            raw = re.sub(r'\s*```$',     '', raw)
            return json.loads(raw)
        except Exception:
            if attempt == 2:
                return {}
            time.sleep(1)
    return {}


def resolve_entities(text: str, raw_entities: list):
    """解析实体偏移量，返回 (entities_out, entity_map)"""
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


def resolve_relations(raw_relations: list, entity_map: dict) -> list:
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


# ===== 单条预测（双向反馈）=====
_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one(idx: int, text: str):
    client = get_client()
    top_k_samples = retrieve_top_k(text, k=TOP_K)
    ner_fewshot = build_ner_fewshot(top_k_samples)
    re_fewshot  = build_re_fewshot(top_k_samples)

    current_entities_raw = []
    feedback_note = ""

    for round_num in range(MAX_ROUNDS):
        # ===== Agent 1：NER =====
        ner_user = (
            f"## Examples\n{ner_fewshot}\n"
            f"## Now annotate entities only:\n"
            f"Input: {text}\n"
        )
        if feedback_note:
            ner_user += f"## Feedback from RE Agent (please correct these entity types):\n{feedback_note}\n"
        ner_user += "Output:"

        ner_result = call_llm(client, NER_SYSTEM, ner_user, temperature=0.3)
        current_entities_raw = ner_result.get("entities", [])

        if not current_entities_raw:
            # NER 没有识别到任何实体，直接返回空结果
            return idx, text, [], [], None

        # ===== Agent 2：RE =====
        ent_list_str = json.dumps(
            [{"text": e.get("text",""), "label": e.get("label","")} for e in current_entities_raw],
            ensure_ascii=False
        )
        re_user = (
            f"## Examples\n{re_fewshot}\n"
            f"## Now extract relations:\n"
            f"Input: {text}\n"
            f"Entities: {ent_list_str}\n"
            f"Output:"
        )

        re_result = call_llm(client, RE_SYSTEM, re_user, temperature=0.3)

        # ===== 冲突检测：RE 是否发现实体类型错误？=====
        corrections = re_result.get("entity_type_corrections", [])
        if corrections and round_num < MAX_ROUNDS - 1:
            # 有冲突，构建反馈并进入下一轮
            feedback_lines = []
            for c in corrections:
                feedback_lines.append(
                    f'  - Entity "{c.get("text","")}" was labeled {c.get("current_label","")}, '
                    f'but RE suggests it should be {c.get("suggested_label","")}'
                )
            feedback_note = "\n".join(feedback_lines)
            # 继续下一轮迭代
            continue
        else:
            # 无冲突或已达最大轮数，使用当前结果
            break

    # ===== 解析最终结果 =====
    entities_out, entity_map = resolve_entities(text, current_entities_raw)
    relations_out = resolve_relations(re_result.get("relations", []), entity_map)

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
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS}")
print(f"双向反馈模式 | 最大迭代轮数: {MAX_ROUNDS} | 每条约 2-4 次 API 调用")

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
