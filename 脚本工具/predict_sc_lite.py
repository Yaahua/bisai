#!/usr/bin/env python3
"""
predict_sc_lite.py — 轻量版自一致性采样
使用 gemini-2.5-flash 进行 3 次独立预测，投票门槛 2/3
去掉 TF-IDF（直接用固定 few-shot），减少内存和启动时间
"""
import json
import os
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from collections import Counter
from copy import deepcopy

# 强制 flush
sys.stdout.reconfigure(line_buffering=True)

# ===== 路径配置 =====
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'
SC_OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_sc_gemini.json'
SC_RAW_PATH = '/home/ubuntu/bisai/数据/A榜/sc_raw_samples.json'
os.makedirs(os.path.dirname(SC_OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL = "gemini-2.5-flash"
N_SAMPLES = 3        # 采样次数
VOTE_THRESHOLD = 2   # 投票门槛
WORKERS = 8          # 并发线程
SAVE_EVERY = 20

# ===== 非法三元组黑名单 =====
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
}

# ===== 加载数据 =====
print("加载数据...", flush=True)
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)
print(f"训练集: {len(TRAIN_DATA)} 条, 测试集: {len(TEST_DATA)} 条", flush=True)

# ===== 构建固定 few-shot（选择高质量、多关系类型的样本）=====
def select_diverse_examples(train_data, n=6):
    """选择覆盖不同关系类型的示例"""
    label_coverage = set()
    selected = []
    # 优先选择包含多种关系类型的样本
    scored = []
    for item in train_data:
        labels = set(r['label'] for r in item.get('relations', []))
        scored.append((len(labels), item, labels))
    scored.sort(key=lambda x: -x[0])
    
    for score, item, labels in scored:
        if len(selected) >= n:
            break
        new_labels = labels - label_coverage
        if new_labels or len(selected) < 3:
            selected.append(item)
            label_coverage.update(labels)
    
    return selected

FIXED_EXAMPLES = select_diverse_examples(TRAIN_DATA, n=5)
print(f"固定 few-shot: {len(FIXED_EXAMPLES)} 条", flush=True)

def format_example(item):
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return (f'Input: {item["text"]}\n'
            f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')

FEWSHOT_BLOCK = "\n\n".join([format_example(ex) for ex in FIXED_EXAMPLES])

SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Entity Types (12)
CROP: crop species name (sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, etc.)
VAR: cultivar/variety name | GENE: gene name | QTL: quantitative trait loci
MRK: molecular marker | TRT: trait/phenotype (ONLY main trait under study)
ABS: abiotic stress | BIS: biotic stress | BM: breeding method
CHR: chromosome (strip "chromosome" prefix) | CROSS: hybrid/segregating population | GST: growth stage

## Relation Types (6)
AFF: biological causation (requires causal verbs)
LOI: physical mapping (requires mapping language). GENE-LOI-TRT is common.
HAS: (CROP/VAR) possesses TRT. Head MUST be CROP or VAR.
CON: CROP contains VAR or GENE
USE: (VAR/CROSS/CROP) uses BM
OCI: occurs at GST (tail MUST be GST)

## Rules
1. ALWAYS annotate crop species as CROP. 2. ~33% sentences have NO relations.
3. Entity text MUST be EXACT substring. 4. Output valid JSON only."""


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
        ht = r.get("head", "").strip()
        tt = r.get("tail", "").strip()
        hty = r.get("head_type", "")
        tty = r.get("tail_type", "")
        rl = r.get("label", "")
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


_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client


def predict_one_sample(text):
    """执行一次预测"""
    client = get_client()
    
    for attempt in range(3):
        try:
            user_msg = (
                f"## Examples:\n{FEWSHOT_BLOCK}\n\n"
                f"## Now annotate:\nInput: {text}\nOutput:"
            )
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": user_msg}
                ],
                temperature=0.7,
                max_tokens=2048,
                timeout=60
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


def process_one(idx):
    """对一条数据进行 N 次采样"""
    text = TEST_DATA[idx]['text']
    all_ents = []
    all_rels = []
    
    for _ in range(N_SAMPLES):
        ents, rels = predict_one_sample(text)
        all_ents.append(ents)
        all_rels.append(rels)
    
    return idx, text, all_ents, all_rels


def vote_relations(all_samples_rels, threshold=VOTE_THRESHOLD):
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
    voted = []
    for key, count in rel_counter.items():
        if count >= threshold:
            voted.append(rel_data[key])
    return voted


def vote_entities(all_samples_ents, threshold=VOTE_THRESHOLD):
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
    voted = []
    for key, count in ent_counter.items():
        if count >= threshold:
            voted.append(ent_data[key])
    return voted


# ===== 主循环 =====
raw_results = {}
if os.path.exists(SC_RAW_PATH):
    raw_results = json.load(open(SC_RAW_PATH, encoding='utf-8'))
    raw_results = {int(k): v for k, v in raw_results.items()}
    print(f"断点续传：已有 {len(raw_results)} 条", flush=True)

pending = [i for i in range(len(TEST_DATA)) if i not in raw_results]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 采样: {N_SAMPLES}次 | 投票: {VOTE_THRESHOLD}/{N_SAMPLES}", flush=True)

save_lock = threading.Lock()
completed = [0]

def save_raw():
    with open(SC_RAW_PATH, 'w', encoding='utf-8') as f:
        json.dump({str(k): v for k, v in raw_results.items()}, f, ensure_ascii=False)

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(process_one, i): i for i in pending}
    for future in as_completed(futures):
        idx, text, all_ents, all_rels = future.result()
        with save_lock:
            raw_results[idx] = {
                'text': text,
                'all_ents': [[{'text':e['text'],'label':e['label'],'start':e['start'],'end':e['end']} for e in ents] for ents in all_ents],
                'all_rels': [[{'head':r['head'],'head_type':r['head_type'],'head_start':r['head_start'],'head_end':r['head_end'],
                              'tail':r['tail'],'tail_type':r['tail_type'],'tail_start':r['tail_start'],'tail_end':r['tail_end'],
                              'label':r['label']} for r in rels] for rels in all_rels]
            }
            completed[0] += 1
            rels_per = [len(r) for r in all_rels]
            print(f"[{completed[0]:>3}/{len(pending)}] idx={idx} rels={rels_per} text={text[:40]}...", flush=True)
            
            if completed[0] % SAVE_EVERY == 0:
                save_raw()
                print(f"  >>> 已保存 {len(raw_results)}/{len(TEST_DATA)} <<<", flush=True)

save_raw()
print(f"\n原始采样完成: {len(raw_results)} 条", flush=True)

# ===== 投票聚合 =====
print(f"\n=== 投票聚合 ===", flush=True)
sc_output = []
for i in range(len(TEST_DATA)):
    data = raw_results[i]
    text = data['text']
    voted_ents = vote_entities(data['all_ents'], threshold=VOTE_THRESHOLD)
    voted_rels = vote_relations(data['all_rels'], threshold=VOTE_THRESHOLD)
    sc_output.append({'text': text, 'entities': voted_ents, 'relations': voted_rels})

json.dump(sc_output, open(SC_OUTPUT_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

sc_total = sum(len(x.get('relations',[])) for x in sc_output)
sc_norel = sum(1 for x in sc_output if not x.get('relations'))
print(f"SC结果: 关系={sc_total}, 均值={sc_total/400:.2f}, 无关系={sc_norel}({sc_norel/4:.1f}%)", flush=True)
print("完成!", flush=True)
