#!/usr/bin/env python3
"""
修复失败条目：对指定 JSON 文件中实体和关系均为空的条目，用 v6 RAG 方式重新预测
使用较低并发（5线程）+ 更长重试间隔，避免 429 限速
"""
import json, os, re, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'

# 要修复的目标文件
TARGET_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v9_targeted.json'

MODEL   = "gpt-4.1-mini"
WORKERS = 5    # 降低并发避免 429
TOP_K   = 4

ILLEGAL_TRIPLETS = {
    ('VAR','CON','CROP'), ('GENE','CON','CROP'), ('CROSS','CON','CROP'),
    ('MRK','AFF','TRT'), ('GENE','AFF','ABS'),
}

with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)
with open(TARGET_PATH, encoding='utf-8') as f:
    RESULTS = json.load(f)

# 找出失败条目（实体和关系均为空，但原文非空）
FAILED_INDICES = [
    i for i, r in enumerate(RESULTS)
    if len(r.get('entities', [])) == 0 and len(r.get('relations', [])) == 0
    and r.get('text', '')
]
print(f"需要修复的条目数：{len(FAILED_INDICES)}")
print(f"失败索引：{FAILED_INDICES}")

# TF-IDF 索引
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
tfidf = TfidfVectorizer(ngram_range=(1,2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)

def retrieve_top_k(text, k=TOP_K):
    vec = tfidf.transform([text])
    sims = cosine_similarity(vec, TRAIN_MATRIX).flatten()
    top = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[i] for i in top if sims[i] > 0.01][:k]

SYSTEM = """You are an expert NER and RE annotator for crop breeding literature.
Entity types: CROP, VAR, GENE, QTL, MRK, TRT, ABS, BIS, BM, CHR, CROSS, GST
Relation types: AFF(needs causal verb), LOI(needs mapping language), HAS, CON, USE, OCI
Rules: entity text MUST be exact substring; 32.7% sentences have no relations.
Output valid JSON only: {"entities": [{"text":"...","label":"..."}], "relations": [...]}"""

_tl = threading.local()
def get_client():
    if not hasattr(_tl, 'c'):
        _tl.c = OpenAI()
    return _tl.c

def fix_one(idx):
    text = TEST_DATA[idx]['text']
    client = get_client()
    samples = retrieve_top_k(text)
    fewshot = ""
    for s in samples:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [{"head": r["head"], "head_type": r["head_type"],
                 "tail": r["tail"], "tail_type": r["tail_type"],
                 "label": r["label"]} for r in s["relations"]]
        fewshot += f'Input: {s["text"]}\nOutput: {json.dumps({"entities":ents,"relations":rels},ensure_ascii=False)}\n\n'

    for attempt in range(4):
        try:
            time.sleep(attempt * 3)  # 递增等待
            resp = get_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": f"## Examples\n{fewshot}## Now annotate:\nInput: {text}\nOutput:"}
                ],
                temperature=0, max_tokens=2048
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r'^```json\s*','',raw); raw = re.sub(r'^```\s*','',raw); raw = re.sub(r'\s*```$','',raw)
            parsed = json.loads(raw)
            # 解析偏移量
            ents_out, rels_out = [], []
            used, emap = set(), {}
            for e in parsed.get('entities',[]):
                et, lb = e.get('text','').strip(), e.get('label','')
                if not et or not lb: continue
                i = text.find(et)
                while i != -1 and (i, i+len(et)) in used: i = text.find(et, i+1)
                if i == -1:
                    lo = text.lower().find(et.lower())
                    if lo != -1 and (lo,lo+len(et)) not in used: i = lo
                    else: continue
                s2, en = i, i+len(et)
                used.add((s2,en)); actual = text[s2:en]
                ents_out.append({"start":s2,"end":en,"text":actual,"label":lb})
                if et not in emap: emap[et] = (s2,en,actual,lb)
            for r in parsed.get('relations',[]):
                ht,tt,hty,tty,rl = r.get('head','').strip(),r.get('tail','').strip(),r.get('head_type',''),r.get('tail_type',''),r.get('label','')
                if not all([ht,tt,hty,tty,rl]): continue
                if (hty,rl,tty) in ILLEGAL_TRIPLETS: continue
                if ht not in emap or tt not in emap: continue
                hs,he,ha,_ = emap[ht]; ts,te,ta,_ = emap[tt]
                rels_out.append({"head":ha,"head_start":hs,"head_end":he,"head_type":hty,"tail":ta,"tail_start":ts,"tail_end":te,"tail_type":tty,"label":rl})
            return idx, text, ents_out, rels_out
        except Exception as ex:
            if attempt == 3:
                print(f"  [{idx}] 最终失败: {str(ex)[:60]}")
                return idx, text, [], []
            time.sleep(5 + attempt * 5)
    return idx, text, [], []

print(f"\n开始修复 {len(FAILED_INDICES)} 条失败记录（降速模式：{WORKERS}线程）...")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futures = {ex.submit(fix_one, i): i for i in FAILED_INDICES}
    for future in as_completed(futures):
        idx, text, ents, rels = future.result()
        RESULTS[idx] = {"text": text, "entities": ents, "relations": rels}
        print(f"  [{idx+1:>3}/400] 修复完成 → 实体:{len(ents)} 关系:{len(rels)}")

with open(TARGET_PATH, 'w', encoding='utf-8') as f:
    json.dump(RESULTS, f, ensure_ascii=False, indent=2)

still_empty = sum(1 for r in RESULTS if not r.get('entities') and not r.get('relations'))
print(f"\n修复完成！仍为空的条目数：{still_empty}")
print(f"文件已更新：{TARGET_PATH}")
