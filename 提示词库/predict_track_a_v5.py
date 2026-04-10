#!/usr/bin/env python3
"""
MGBIE Track-A 多线程预测脚本
- 20 线程并发调用 API
- 每完成 20 条自动保存一次
- 支持断点续传
- 模型只输出文本标签，脚本自动计算精确字符偏移量
"""
import json, os, re, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# ===== 配置 =====
MODEL = "gpt-4.1-mini"
WORKERS = 20          # 并发线程数
SAVE_EVERY = 20       # 每完成多少条保存一次
OUTPUT_PATH = '/home/ubuntu/bisai_clone/数据/A榜/submit_v5.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 加载数据 =====
with open('/home/ubuntu/official_mgbie/dataset/test_A.json') as f:
    ALL_DATA = json.load(f)
with open('/home/ubuntu/bisai_clone/提示词库/fewshot_v3.json') as f:
    FEWSHOT = json.load(f)

# ===== 系统提示词 =====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature.

## Entity Types (12)
CROP: crop species | VAR: cultivar/variety | GENE: gene name/ID | QTL: quantitative trait loci
MRK: molecular marker | TRT: trait/phenotype | ABS: abiotic stress | BIS: biotic stress
BM: breeding method | CHR: chromosome identifier | CROSS: hybrid population | GST: growth stage

## Relation Types (6)
AFF: head affects tail (ABS→TRT 34%, GENE→TRT 21%, ABS→GENE 11%)
LOI: head located on/associated with tail (QTL→TRT 31%, QTL→CHR 20%, MRK→CHR 6%)
HAS: head has trait (VAR→TRT 61%, CROP→TRT 30%)
CON: head contains tail (CROP→VAR 43%, CROP→GENE 12%)
USE: head uses method (VAR→BM 45%, CROP→BM 9%)
OCI: head occurs at stage (TRT→GST 46%, ABS→GST 34%)

## Critical Rules
1. LOI(QTL→TRT) is the most common LOI pattern (31%). Do NOT convert to AFF.
2. 32.7% of sentences have NO relations. Output empty relations [] when unclear.
3. Entity "text" must be an EXACT substring of the input sentence.
4. Do NOT annotate lab techniques (ddRAD-seq, RT-qPCR, RNA-seq, CRISPR) as BM.
5. RILs, DH lines, F2 populations → CROSS (not VAR).
6. Strip type prefixes: "marker Xgwm11" → "Xgwm11" (MRK); "chromosome 2H" → "2H" (CHR).
7. AFF head = influencing party (ABS/GENE/MRK/QTL/BIS/BM); tail = TRT/GENE.
8. Output valid JSON only. No explanation. No markdown fences.

## Output Format
{"entities": [{"text": "<exact substring>", "label": "<TYPE>"}], "relations": [{"head": "<text>", "head_type": "<TYPE>", "tail": "<text>", "tail_type": "<TYPE>", "label": "<REL>"}]}"""

# ===== 构建 Few-shot 块 =====
def build_fewshot():
    lines = []
    for s in FEWSHOT:
        ents = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels = [{"head": r["head"], "head_type": r["head_type"],
                 "tail": r["tail"], "tail_type": r["tail_type"],
                 "label": r["label"]} for r in s["relations"]]
        lines.append(f'Input: {s["text"]}')
        lines.append(f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')
        lines.append("")
    return "\n".join(lines)

FEWSHOT_BLOCK = build_fewshot()

# ===== 偏移量解析 =====
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

# ===== 单条预测（线程安全，每个线程独立 client） =====
_thread_local = threading.local()

def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client

def predict_one(idx, text):
    client = get_client()
    for attempt in range(3):
        try:
            extra = "\nRemember: output ONLY valid JSON. Entity text must be exact substrings." if attempt > 0 else ""
            user_msg = f"## Examples\n{FEWSHOT_BLOCK}\n## Now annotate:\nInput: {text}\nOutput:{extra}"
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0,
                max_tokens=2048
            )
            raw_str = resp.choices[0].message.content.strip()
            raw_str = re.sub(r'^```json\s*', '', raw_str)
            raw_str = re.sub(r'^```\s*', '', raw_str)
            raw_str = re.sub(r'\s*```$', '', raw_str)
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
# 断点续传
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH) as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

# 找出待处理的索引
pending = [i for i in range(400) if i not in results_dict]
print(f"待处理: {len(pending)} 条，使用 {WORKERS} 线程并发")

save_lock = threading.Lock()
completed_count = [0]
failed_list = []

def save_results():
    """按顺序保存所有已完成的结果"""
    ordered = [results_dict[i] for i in sorted(results_dict.keys())]
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(predict_one, i, ALL_DATA[i]["text"]): i for i in pending}
    
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
            
            print(f"[{idx+1}/400] {text[:55]}... {status}")
            
            # 每完成 SAVE_EVERY 条保存一次
            if done % SAVE_EVERY == 0:
                save_results()
                print(f"  >>> 已保存 {total_done}/400 条 <<<")

# 最终保存
save_results()
print(f"\n===== 全部完成 =====")
print(f"总条数: 400 | 成功: {400-len(failed_list)} | 失败: {len(failed_list)}")
if failed_list:
    print(f"失败索引: {sorted(failed_list)}")
print(f"输出: {OUTPUT_PATH}")
