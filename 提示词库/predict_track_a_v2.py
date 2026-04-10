#!/usr/bin/env python3
"""
MGBIE Track-A 优化版预测脚本 v2
改进点：
1. 更严格的 Prompt：明确禁止非法关系模式，区分 LOI vs AFF
2. 新 Few-shot：覆盖漏标最严重的 GENE→LOI→TRT 和 MRK→LOI→TRT 模式
3. 内置后处理：自动过滤训练集中不存在的非法关系三元组
4. 20 线程并发，每 20 条保存一次
"""
import json, os, re, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from collections import Counter

# ===== 配置 =====
MODEL = "gpt-4.1-mini"
WORKERS = 20
SAVE_EVERY = 20
OUTPUT_PATH = '/home/ubuntu/bisai_clone/数据/A榜/submit_v2.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 加载数据 =====
with open('/home/ubuntu/official_mgbie/dataset/test_A.json') as f:
    ALL_DATA = json.load(f)
with open('/home/ubuntu/fewshot_v2.json') as f:
    FEWSHOT = json.load(f)

# 提取训练集合法关系三元组（用于后处理过滤）
with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    train = json.load(f)
VALID_TRIPLES = set()
for item in train:
    for r in item.get('relations', []):
        VALID_TRIPLES.add((r['head_type'], r['label'], r['tail_type']))

# ===== 优化版系统提示词 =====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature.

## Entity Types (12)
CROP: crop species (e.g. barley, sorghum, foxtail millet)
VAR: named cultivar/variety (e.g. "JiaYan 2", "Tx623")
GENE: gene name or ID (e.g. SbWRKY51, GsNAC2, sdw1)
QTL: quantitative trait loci (e.g. "qPH9", "QTL for plant height")
MRK: molecular marker (e.g. SSR, SNP, AFLP, DArT markers)
TRT: measurable trait or phenotype (e.g. plant height, yield, drought tolerance)
ABS: abiotic stress (e.g. drought stress, salt stress, high salinity)
BIS: biotic stress or pathogen (e.g. powdery mildew, E. graminis, rust)
BM: breeding method (e.g. GWAS, marker-assisted breeding, QTL mapping) — NOT lab techniques like RT-qPCR, RNA-seq, CRISPR
CHR: chromosome identifier (e.g. "2H", "chromosome 6", "LG10")
CROSS: hybrid/mapping population (e.g. RILs, DH lines, F2 population, F-1 hybrids)
GST: growth stage (e.g. seedling stage, germination, jointing stage)

## Relation Types (6) — with EXACT allowed head→tail combinations
AFF (affects): ABS→TRT, ABS→GENE, GENE→TRT, GENE→GENE, BIS→TRT, BIS→CROP, BM→TRT, TRT→TRT, MRK→TRT, QTL→TRT(rare)
LOI (located on/associated with): QTL→TRT, QTL→CHR, GENE→TRT, GENE→CHR, MRK→TRT, MRK→CHR, MRK→GENE, MRK→QTL
HAS (has trait): VAR→TRT, CROP→TRT, CROSS→TRT, GENE→TRT
CON (contains): CROP→VAR, CROP→GENE, CROP→CROSS, CROSS→VAR, GENE→GENE, TRT→TRT, CROP→CROP
USE (uses method): VAR→BM, CROP→BM, CROSS→BM
OCI (occurs at stage): TRT→GST, ABS→GST

## CRITICAL DISTINCTION: LOI vs AFF
- LOI = the head entity IS MAPPED/LOCATED/ASSOCIATED with the tail (structural/positional relationship)
  → "Gene X was mapped to chromosome 2H" → GENE LOI CHR
  → "QTL qPH9 is associated with plant height" → QTL LOI TRT
  → "Marker SSR-X linked to yield" → MRK LOI TRT
- AFF = the head entity CAUSES CHANGE in the tail (functional/causal relationship)
  → "Drought stress reduced plant height" → ABS AFF TRT
  → "Gene SbWRKY51 regulates salt tolerance" → GENE AFF TRT
- When a GENE or MRK is "associated with", "linked to", "mapped to" a TRT → use LOI, NOT AFF

## STRICT RULES
1. ONLY output relations from the allowed combinations above. Do NOT invent new head→tail type combinations.
2. 32.7% of sentences have NO relations. When the sentence only describes methods, counts, or background without explicit entity interactions → output empty relations [].
3. Do NOT output (BM, USE, CROP), (VAR, AFF, GENE), (CHR, LOI, QTL), (CROP, HAS, ABS), (VAR, LOI, CHR) — these NEVER appear in the training data.
4. Entity "text" must be an EXACT substring of the input sentence.
5. Do NOT annotate: ddRAD-seq, RT-qPCR, RNA-seq, CRISPR, Western blot as BM.
6. RILs, DH lines, F2 populations → CROSS (not VAR).
7. Strip type prefixes: "marker Xgwm11" → entity text = "Xgwm11"; "chromosome 2H" → "2H".
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
        # 后处理：过滤非法三元组
        if (hty, rl, tty) not in VALID_TRIPLES:
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

def predict_one(idx, text):
    client = get_client()
    for attempt in range(3):
        try:
            extra = "\nSTRICTLY output valid JSON only. Entity text must be exact substrings of the input." if attempt > 0 else ""
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
            time.sleep(2 ** attempt)
    return idx, text, [], [], "max_retries"

# ===== 主程序 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH) as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

pending = [i for i in range(400) if i not in results_dict]
print(f"待处理: {len(pending)} 条，使用 {WORKERS} 线程并发")

save_lock = threading.Lock()
completed_count = [0]
failed_list = []

def save_results():
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
            status = f"✓ 实体:{len(ents)} 关系:{len(rels)}"
            if err:
                failed_list.append(idx)
                status = f"⚠ 失败({err})"
            print(f"[{idx+1}/400] {text[:55]}... {status}")
            if done % SAVE_EVERY == 0:
                save_results()
                print(f"  >>> 已保存 {len(results_dict)}/400 条 <<<")

save_results()
print(f"\n===== 全部完成 =====")
print(f"总条数: 400 | 成功: {400-len(failed_list)} | 失败: {len(failed_list)}")
if failed_list:
    print(f"失败索引: {sorted(failed_list)}")
print(f"输出: {OUTPUT_PATH}")
