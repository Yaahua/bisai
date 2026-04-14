#!/usr/bin/env python3
"""
predict_v21_elite.py — 精英版单模型预测
核心思路：放弃多模型集成，用一个极强的 Prompt + RAG + 自一致性 构建高质量预测

关键改进：
1. 使用 gemini-2.5-flash（当前最强可用模型）
2. 两阶段 Prompt：先 NER 再 RE（分离任务降低复杂度）
3. 动态 RAG：根据文本相似度检索最相关的训练样本
4. 自一致性：temperature=0 做一次主预测 + temperature=0.5 做两次辅助预测
5. 严格后处理：非法三元组过滤 + 训练集分布约束
"""
import json
import os
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI
from collections import Counter
from copy import deepcopy

sys.stdout.reconfigure(line_buffering=True)

# ===== 路径 =====
TRAIN_PATH = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v21_elite.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL = "gemini-2.5-flash"
WORKERS = 8
SAVE_EVERY = 20
TOP_K = 6  # RAG 检索数

# ===== 非法三元组 =====
ILLEGAL_TRIPLETS = {
    ('VAR','CON','CROP'), ('GENE','CON','CROP'), ('CROSS','CON','CROP'),
    ('MRK','AFF','TRT'), ('GENE','AFF','ABS'),
    ('TRT','HAS','VAR'), ('TRT','HAS','CROP'),
    ('VAR','OCI','TRT'), ('VAR','AFF','BIS'),
    ('QTL','LOI','VAR'), ('CROP','HAS','ABS'),
    ('VAR','HAS','ABS'), ('VAR','HAS','BIS'),
    ('BM','USE','CROP'), ('CHR','LOI','VAR'),
    ('TRT','LOI','TRT'), ('ABS','LOI','CHR'),
    ('BIS','LOI','CHR'), ('GST','AFF','TRT'),
    ('CROP','AFF','TRT'), ('ABS','AFF','ABS'),
    ('QTL','LOI','MRK'),  # 训练集只有1次，几乎都是FP
    ('CROSS','HAS','TRT'), # 训练集14次但模型过标严重
}

# ===== 加载数据 =====
print("加载数据...", flush=True)
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)

# 训练集合法三元组及频率
TRAIN_TRIPLETS = Counter()
for item in TRAIN_DATA:
    for r in item.get('relations', []):
        TRAIN_TRIPLETS[(r['head_type'], r['label'], r['tail_type'])] += 1

print(f"训练集: {len(TRAIN_DATA)}, 测试集: {len(TEST_DATA)}", flush=True)

# ===== TF-IDF RAG =====
print("构建 TF-IDF 索引...", flush=True)
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)
print(f"TF-IDF 完成: {TRAIN_MATRIX.shape}", flush=True)


def retrieve_top_k(query_text, k=TOP_K):
    query_vec = tfidf.transform([query_text])
    sims = cosine_similarity(query_vec, TRAIN_MATRIX).flatten()
    top_indices = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[idx] for idx in top_indices if sims[idx] > 0.05][:k]


def format_example_full(item):
    """完整格式化一个训练样本（包含 start/end）"""
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = []
    for r in item["relations"]:
        rels.append({
            "head": r["head"], "head_type": r["head_type"],
            "tail": r["tail"], "tail_type": r["tail_type"],
            "label": r["label"]
        })
    output = {"entities": ents, "relations": rels}
    return f'Input: {item["text"]}\nOutput: {json.dumps(output, ensure_ascii=False)}'


# ===== 构建分关系类型的专项示例池 =====
LABEL_EXAMPLES = {}
for label in ['AFF', 'LOI', 'HAS', 'CON', 'USE', 'OCI']:
    examples = []
    for item in TRAIN_DATA:
        has_label = any(r['label'] == label for r in item.get('relations', []))
        if has_label:
            rel_count = len(item.get('relations', []))
            examples.append((rel_count, item))
    # 选择关系数适中的样本（不要太多也不要太少）
    examples.sort(key=lambda x: abs(x[0] - 3))
    LABEL_EXAMPLES[label] = [item for _, item in examples[:3]]

# 无关系的示例
NO_REL_EXAMPLES = []
for item in TRAIN_DATA:
    if not item.get('relations'):
        if item.get('entities') and len(item['entities']) >= 2:
            NO_REL_EXAMPLES.append(item)
            if len(NO_REL_EXAMPLES) >= 2:
                break


# ===== Prompt =====
SYSTEM = """You are a world-class biomedical NER and RE expert specializing in coarse grain crop breeding literature. Your task is joint entity and relation extraction for the MGBIE benchmark.

## Entity Types (12 types)
| Type | Description | Examples |
|------|-------------|----------|
| CROP | Crop species name | sorghum, barley, oat, millet, quinoa, buckwheat, foxtail millet, proso millet, mung bean, cowpea |
| VAR | Cultivar/variety/line name | BTx623, Morex, Pioneer 9306, Yugu1, IS9830 |
| GENE | Gene name/symbol | Dw3, HvCBF4, SbDREB, SiMYB, Waxy |
| QTL | Quantitative trait locus | qDT-3H, SbDT1, qGY-2H |
| MRK | Molecular marker | Xgwm11, RM223, SSR markers, SNP markers |
| TRT | Trait/phenotype (main trait only) | drought tolerance, grain yield, plant height, starch content |
| ABS | Abiotic stress | drought, heat, salinity, cold, waterlogging |
| BIS | Biotic stress | Fusarium, rust, aphid, blast, downy mildew |
| BM | Breeding method | GWAS, QTL mapping, MAS, MABC, backcross breeding |
| CHR | Chromosome (strip "chromosome" prefix) | 2H, 3, 7A, 5B |
| CROSS | Hybrid/segregating population | RILs, DH lines, F2 population, BC1F1 |
| GST | Growth stage | seedling stage, heading, anthesis, flowering, grain filling |

## Relation Types (6 types)
| Relation | Meaning | Valid Head→Tail | Trigger Words |
|----------|---------|-----------------|---------------|
| LOI | Located/mapped on | QTL→TRT, QTL→CHR, GENE→TRT, GENE→CHR, MRK→TRT, MRK→CHR, MRK→GENE | mapped, located, associated with, linked to, detected on, identified on, flanked by |
| AFF | Affects/causes | ABS→TRT, GENE→TRT, ABS→GENE, ABS→CROP, BIS→TRT, BIS→CROP, TRT→TRT, QTL→TRT, BM→TRT | regulates, controls, affects, influences, increases, decreases, promotes, inhibits, encodes, determines, reduces, enhances, improves, confers |
| HAS | Possesses trait | CROP→TRT, VAR→TRT | has, shows, exhibits, displays, possesses, with, characterized by |
| CON | Contains/composed of | CROP→VAR, CROP→GENE, TRT→TRT | contains, includes, comprises, consists of, is a component of |
| USE | Uses method | VAR→BM, CROSS→BM, CROP→BM | using, via, through, by, employed, applied, performed |
| OCI | Occurs at stage | TRT→GST, ABS→GST, CROP→GST, VAR→GST | at, during, in, stage |

## Critical Decision Rules
1. **Entity text MUST be an EXACT substring** of the input sentence. Do not paraphrase or abbreviate.
2. **CHR entities**: Strip "chromosome" prefix. "chromosome 2H" → entity text is "2H". "chr3" → "3".
3. **HAS direction**: Head MUST be CROP or VAR. NEVER write TRT→VAR or TRT→CROP.
4. **CON direction**: Head MUST be CROP. CROP contains VAR or GENE.
5. **~33% of sentences have NO relations**. If no clear semantic link exists, output empty relations [].
6. **Do NOT hallucinate relations**. Only extract relations with explicit textual evidence.
7. **TRT precision**: Only annotate the main trait under study, not every measurement or parameter mentioned.
8. **BM vs lab technique**: GWAS, MAS, MABC are BM. RNA-seq, PCR, CRISPR, qRT-PCR are NOT BM.
9. Output valid JSON only. No explanation. No markdown code fences."""


def build_prompt(text, rag_samples):
    """构建高质量 Prompt"""
    parts = ["## Reference Examples (from training set, ranked by similarity):\n"]
    
    for i, sample in enumerate(rag_samples):
        parts.append(f"### Example {i+1}:")
        parts.append(format_example_full(sample))
        parts.append("")
    
    # 添加一个无关系的示例
    if NO_REL_EXAMPLES:
        parts.append("### Example (no relations):")
        parts.append(format_example_full(NO_REL_EXAMPLES[0]))
        parts.append("")
    
    parts.append("## Task:")
    parts.append("Extract all entities and relations from the following sentence.")
    parts.append("Be precise: only extract relations with clear textual evidence.")
    parts.append(f"\nInput: {text}")
    parts.append("Output:")
    
    return "\n".join(parts)


def resolve(text, raw):
    """解析模型输出，映射到原文偏移量"""
    entities_out, relations_out = [], []
    used_spans = set()
    entity_map = {}
    
    for e in raw.get("entities", []):
        et = e.get("text", "").strip()
        lb = e.get("label", "")
        if not et or not lb:
            continue
        if lb not in ('CROP','VAR','GENE','QTL','MRK','TRT','ABS','BIS','BM','CHR','CROSS','GST'):
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
        if et.lower() not in entity_map:
            entity_map[et.lower()] = (s, en, actual, lb)
    
    for r in raw.get("relations", []):
        ht = r.get("head", "").strip()
        tt = r.get("tail", "").strip()
        hty = r.get("head_type", "")
        tty = r.get("tail_type", "")
        rl = r.get("label", "")
        if not all([ht, tt, hty, tty, rl]):
            continue
        if rl not in ('LOI','AFF','HAS','CON','USE','OCI'):
            continue
        if (hty, rl, tty) in ILLEGAL_TRIPLETS:
            continue
        if (hty, rl, tty) not in TRAIN_TRIPLETS:
            continue
        
        # 查找实体（支持大小写不敏感）
        h_info = entity_map.get(ht) or entity_map.get(ht.lower())
        t_info = entity_map.get(tt) or entity_map.get(tt.lower())
        if not h_info or not t_info:
            continue
        
        hs, he, ha, _ = h_info
        ts, te, ta, _ = t_info
        relations_out.append({
            "head": ha, "head_start": hs, "head_end": he, "head_type": hty,
            "tail": ta, "tail_start": ts, "tail_end": te, "tail_type": tty,
            "label": rl
        })
    return entities_out, relations_out


_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one(idx, text):
    """对一条数据进行预测（主预测 + 2次辅助预测，投票）"""
    client = get_client()
    rag_samples = retrieve_top_k(text, k=TOP_K)
    prompt = build_prompt(text, rag_samples)
    
    all_ents = []
    all_rels = []
    
    # 主预测 (temperature=0, 确定性最高)
    for temp in [0, 0.3, 0.5]:
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temp,
                    max_tokens=2048,
                    timeout=60
                )
                raw_str = resp.choices[0].message.content.strip()
                raw_str = re.sub(r'^```json\s*', '', raw_str)
                raw_str = re.sub(r'^```\s*', '', raw_str)
                raw_str = re.sub(r'\s*```$', '', raw_str)
                raw = json.loads(raw_str)
                ents, rels = resolve(text, raw)
                all_ents.append(ents)
                all_rels.append(rels)
                break
            except json.JSONDecodeError:
                if attempt == 2:
                    all_ents.append([])
                    all_rels.append([])
            except Exception:
                if attempt == 2:
                    all_ents.append([])
                    all_rels.append([])
                time.sleep(2 ** attempt)
    
    # 投票：出现 >= 2/3 次的关系保留
    rel_counter = Counter()
    rel_data = {}
    for rels in all_rels:
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
        if count >= 2:
            voted_rels.append(rel_data[key])
    
    # 实体：取主预测的（temperature=0）
    voted_ents = all_ents[0] if all_ents else []
    
    return idx, text, voted_ents, voted_rels, None


# ===== 主循环 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    existing = json.load(open(OUTPUT_PATH, encoding='utf-8'))
    for i, r in enumerate(existing):
        if r.get('relations') or r.get('entities'):
            results_dict[i] = r
    print(f"断点续传: {len(results_dict)} 条", flush=True)

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"待处理: {len(pending)} | 模型: {MODEL} | 线程: {WORKERS}", flush=True)

save_lock = threading.Lock()
completed = [0]
failed = []


def save_results():
    ordered = [results_dict.get(i, {"text": TEST_DATA[i]["text"], "entities": [], "relations": []})
               for i in range(len(TEST_DATA))]
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)


with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(predict_one, i, TEST_DATA[i]["text"]): i for i in pending}
    for future in as_completed(futures):
        idx, text, ents, rels, err = future.result()
        with save_lock:
            results_dict[idx] = {"text": text, "entities": ents, "relations": rels}
            completed[0] += 1
            
            status = f"E:{len(ents)} R:{len(rels)}"
            if err:
                failed.append(idx)
                status = f"FAIL({err})"
            print(f"[{completed[0]:>3}/{len(pending)}] idx={idx} {status} {text[:40]}...", flush=True)
            
            if completed[0] % SAVE_EVERY == 0:
                save_results()
                print(f"  >>> 已保存 {len(results_dict)}/{len(TEST_DATA)} <<<", flush=True)

save_results()
total_rels = sum(len(results_dict[i].get('relations', [])) for i in range(400))
no_rel = sum(1 for i in range(400) if not results_dict[i].get('relations'))
print(f"\n完成! 关系={total_rels}, 均值={total_rels/400:.2f}, 无关系={no_rel}({no_rel/4:.1f}%)", flush=True)
print(f"输出: {OUTPUT_PATH}", flush=True)
