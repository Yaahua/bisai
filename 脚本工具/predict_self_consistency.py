#!/usr/bin/env python3
"""
predict_self_consistency.py
单模型自一致性采样：使用 gemini-2.5-flash 进行 N 次独立预测
然后在单模型内部进行多数投票，提升召回率同时保持精确率

策略：
- 使用 temperature=0.7 进行 5 次独立预测
- 对每条数据的 5 次预测结果做投票
- 出现 >= 2 次的关系保留（2/5 投票门槛）
- 与 v18 白名单合并，得到最终结果
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
from collections import Counter, defaultdict
from copy import deepcopy

# ===== 路径配置 =====
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'
SC_OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_sc_gemini.json'
FINAL_OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v20_sc_merged.json'
V18_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v18_whitelist.json'
os.makedirs(os.path.dirname(SC_OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL = "gemini-2.5-flash"
N_SAMPLES = 5       # 采样次数
VOTE_THRESHOLD = 2   # 投票门槛
WORKERS = 10         # 并发线程
SAVE_EVERY = 20
TOP_K = 4            # RAG 检索数

# ===== 非法三元组黑名单 =====
ILLEGAL_TRIPLETS = {
    ('VAR',  'CON', 'CROP'), ('GENE', 'CON', 'CROP'), ('CROSS','CON', 'CROP'),
    ('MRK',  'AFF', 'TRT'),  ('GENE', 'AFF', 'ABS'),
    ('TRT',  'HAS', 'VAR'),  ('TRT',  'HAS', 'CROP'),
    ('VAR',  'OCI', 'TRT'),  ('VAR',  'AFF', 'BIS'),
    ('QTL',  'LOI', 'VAR'),  ('CROP', 'HAS', 'ABS'),
    ('VAR',  'HAS', 'ABS'),  ('VAR',  'HAS', 'BIS'),
    ('BM',   'USE', 'CROP'), ('CHR',  'LOI', 'VAR'),
    ('TRT',  'LOI', 'TRT'),  ('ABS',  'LOI', 'CHR'),
    ('BIS',  'LOI', 'CHR'),  ('GST',  'AFF', 'TRT'),
    ('CROP', 'AFF', 'TRT'),  ('ABS',  'AFF', 'ABS'),
}

# ===== 加载数据 =====
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)

# ===== TF-IDF 检索索引 =====
print("构建 TF-IDF 检索索引...")
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)
print(f"TF-IDF 索引完成: {TRAIN_MATRIX.shape}")


def retrieve_top_k(query_text, k=TOP_K):
    query_vec = tfidf.transform([query_text])
    sims = cosine_similarity(query_vec, TRAIN_MATRIX).flatten()
    top_indices = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[idx] for idx in top_indices if sims[idx] > 0.01][:k]


def format_example(item):
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return (f'Input: {item["text"]}\n'
            f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')


SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Entity Types (12)
CROP: crop species name — ALWAYS annotate (sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea, etc.)
VAR: cultivar/variety name (e.g., BTx623, Morex, Pioneer 9306)
GENE: gene name or ID (e.g., Dw3, HvCBF4, SbDREB)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1)
MRK: molecular marker (e.g., Xgwm11, RM223, SSR markers)
TRT: trait/phenotype — ONLY the MAIN trait under study
ABS: abiotic stress (drought, salt, heat, cold stress)
BIS: biotic stress (Fusarium, rust, aphid)
BM: breeding method (GWAS, QTL mapping, MAS, MABC)
CHR: chromosome identifier — strip "chromosome" prefix
CROSS: hybrid/segregating population (RILs, DH lines, F2)
GST: growth stage (seedling stage, heading stage, anthesis)

## Relation Types (6)
AFF: biological causation — REQUIRES explicit causal verbs
LOI: physical mapping — REQUIRES explicit mapping language. GENE-LOI-TRT is common.
HAS: possession — (CROP or VAR) → TRT. Head MUST be CROP or VAR.
CON: composition — CROP contains VAR or GENE
USE: (VAR/CROSS/CROP) uses breeding method (BM)
OCI: occurs at growth stage — tail MUST be GST

## Rules
1. ALWAYS annotate crop species as CROP
2. Do NOT over-annotate TRT
3. ~33% of sentences have NO relations
4. Entity text MUST be EXACT substring
5. Output valid JSON only"""


def resolve(text, raw):
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


# ===== 单次预测 =====
_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one_sample(idx, text, rag_samples, sample_id):
    """执行一次预测"""
    client = get_client()
    
    fewshot_lines = ["## Examples:"]
    for s in rag_samples:
        fewshot_lines.append(format_example(s))
        fewshot_lines.append("")
    fewshot = "\n".join(fewshot_lines)
    
    for attempt in range(3):
        try:
            user_msg = (
                f"{fewshot}\n"
                f"## Now annotate:\n"
                f"Input: {text}\n"
                f"Output:"
            )
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": user_msg}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            raw_str = resp.choices[0].message.content.strip()
            raw_str = re.sub(r'^```json\s*', '', raw_str)
            raw_str = re.sub(r'^```\s*',     '', raw_str)
            raw_str = re.sub(r'\s*```$',     '', raw_str)
            raw = json.loads(raw_str)
            ents, rels = resolve(text, raw)
            return ents, rels
        except json.JSONDecodeError:
            if attempt == 2:
                return [], []
        except Exception as ex:
            if attempt == 2:
                return [], []
            time.sleep(2 ** attempt)
    return [], []


def vote_relations(all_samples_rels, threshold=VOTE_THRESHOLD):
    """对多次采样的关系进行投票"""
    rel_counter = Counter()
    rel_data = {}
    
    for rels in all_samples_rels:
        seen = set()
        for r in rels:
            key = (r['head'].strip().lower(), r['tail'].strip().lower(), r['label'])
            if key not in seen:
                rel_counter[key] += 1
                seen.add(key)
                if key not in rel_data:
                    rel_data[key] = r
    
    voted_rels = []
    for key, count in rel_counter.items():
        if count >= threshold:
            voted_rels.append(rel_data[key])
    
    return voted_rels


def vote_entities(all_samples_ents, threshold=VOTE_THRESHOLD):
    """对多次采样的实体进行投票"""
    ent_counter = Counter()
    ent_data = {}
    
    for ents in all_samples_ents:
        seen = set()
        for e in ents:
            key = (e['text'].strip().lower(), e['label'])
            if key not in seen:
                ent_counter[key] += 1
                seen.add(key)
                if key not in ent_data:
                    ent_data[key] = e
    
    voted_ents = []
    for key, count in ent_counter.items():
        if count >= threshold:
            voted_ents.append(ent_data[key])
    
    return voted_ents


# ===== 主预测循环 =====
# 检查是否有中间结果
SC_RAW_PATH = '/home/ubuntu/bisai/数据/A榜/sc_raw_samples.json'
raw_results = {}
if os.path.exists(SC_RAW_PATH):
    raw_results = json.load(open(SC_RAW_PATH, encoding='utf-8'))
    raw_results = {int(k): v for k, v in raw_results.items()}
    print(f"断点续传：已有 {len(raw_results)} 条原始采样")

pending = [i for i in range(len(TEST_DATA)) if i not in raw_results]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 采样: {N_SAMPLES}次 | 投票门槛: {VOTE_THRESHOLD}")

save_lock = threading.Lock()
completed = [0]


def process_one(idx):
    """对一条数据进行 N 次采样"""
    text = TEST_DATA[idx]['text']
    rag_samples = retrieve_top_k(text, k=TOP_K)
    
    all_ents = []
    all_rels = []
    
    for sample_id in range(N_SAMPLES):
        ents, rels = predict_one_sample(idx, text, rag_samples, sample_id)
        all_ents.append(ents)
        all_rels.append(rels)
    
    return idx, text, all_ents, all_rels


def save_raw():
    with open(SC_RAW_PATH, 'w', encoding='utf-8') as f:
        json.dump(raw_results, f, ensure_ascii=False, indent=2)


with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(process_one, i): i for i in pending}
    for future in as_completed(futures):
        idx, text, all_ents, all_rels = future.result()
        with save_lock:
            raw_results[idx] = {
                'text': text,
                'all_ents': all_ents,
                'all_rels': all_rels
            }
            completed[0] += 1
            
            # 统计
            total_rels_per_sample = [len(r) for r in all_rels]
            print(f"[{completed[0]:>3}/{len(pending)}] idx={idx} 各采样关系数: {total_rels_per_sample}")
            
            if completed[0] % SAVE_EVERY == 0:
                save_raw()
                print(f"  >>> 已保存 {len(raw_results)}/{len(TEST_DATA)} 条原始采样 <<<")

save_raw()
print(f"\n原始采样完成: {len(raw_results)} 条")

# ===== 投票聚合 =====
print(f"\n=== 投票聚合（门槛: {VOTE_THRESHOLD}/{N_SAMPLES}）===")

sc_output = []
for i in range(len(TEST_DATA)):
    data = raw_results[i]
    text = data['text']
    
    voted_ents = vote_entities(data['all_ents'], threshold=VOTE_THRESHOLD)
    voted_rels = vote_relations(data['all_rels'], threshold=VOTE_THRESHOLD)
    
    sc_output.append({
        'text': text,
        'entities': voted_ents,
        'relations': voted_rels
    })

json.dump(sc_output, open(SC_OUTPUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

sc_total_rels = sum(len(x.get('relations', [])) for x in sc_output)
sc_no_rel = sum(1 for x in sc_output if not x.get('relations'))
print(f"SC 投票结果: 关系={sc_total_rels}, 均值={sc_total_rels/400:.2f}, 无关系={sc_no_rel}({sc_no_rel/4:.1f}%)")

# ===== 与 v18 白名单合并 =====
print(f"\n=== 与 v18 白名单合并 ===")
v18 = json.load(open(V18_PATH, encoding='utf-8'))

merged = deepcopy(v18)
new_from_sc = 0

for i in range(400):
    v18_rels = set()
    for r in v18[i].get('relations', []):
        v18_rels.add((r['head'].strip().lower(), r['tail'].strip().lower(), r['label']))
    
    for r in sc_output[i].get('relations', []):
        key = (r['head'].strip().lower(), r['tail'].strip().lower(), r['label'])
        if key not in v18_rels:
            # 验证三元组合法性
            trip = (r.get('head_type', ''), r['label'], r.get('tail_type', ''))
            if trip in ILLEGAL_TRIPLETS:
                continue
            merged[i]['relations'].append(r)
            v18_rels.add(key)
            new_from_sc += 1

json.dump(merged, open(FINAL_OUTPUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

merged_total = sum(len(x.get('relations', [])) for x in merged)
merged_norel = sum(1 for x in merged if not x.get('relations'))
print(f"合并结果: 关系={merged_total}, 均值={merged_total/400:.2f}, 无关系={merged_norel}({merged_norel/4:.1f}%)")
print(f"从 SC 新增: {new_from_sc} 条关系")
print(f"文件: {FINAL_OUTPUT_PATH}")
