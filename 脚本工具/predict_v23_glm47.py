#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v23 — GLM-4.7 版本
==========================================
基于 v10 (Gemini) 的 Prompt 和逻辑，换用 GLM-4.7 模型
目的：作为第四投票模型，与 v7/v9/v10 进行四模型集成投票

使用方法：
  python3.11 predict_v23_glm47.py

输出：
  /home/ubuntu/bisai/数据/A榜/submit_v23_glm47.json

注意：
  - 运行前先跑 20 条小批量测试，确认质量后再全量运行
  - 小批量测试：将 TEST_LIMIT = 20，全量运行时改为 None
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
TRAIN_PATH  = '/home/ubuntu/CCL2026-MGBIE/dataset/train.json'
TEST_PATH   = '/home/ubuntu/CCL2026-MGBIE/dataset/test_A.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v23_glm47.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "glm-4.7"       # GLM-4.7 最新模型
WORKERS    = 10               # 并发线程数（GLM API 限速较严，保守设置）
SAVE_EVERY = 20
TOP_K      = 5
TEST_LIMIT = None             # None = 全量；设为 20 = 小批量测试

# GLM API 配置
GLM_API_KEY  = '5e46ee14f1944eb4a705900c7f9d7b43.K35eAOcogzUiPlhd'
GLM_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4/'

# ===== 非法三元组黑名单 =====
ILLEGAL_TRIPLETS = {
    ('VAR',  'CON', 'CROP'), ('GENE', 'CON', 'CROP'), ('CROSS','CON', 'CROP'),
    ('MRK',  'AFF', 'TRT'),  ('GENE', 'AFF', 'ABS'),
    ('TRT',  'HAS', 'VAR'),  ('TRT',  'HAS', 'CROP'), ('VAR',  'OCI', 'TRT'),
    ('VAR',  'AFF', 'BIS'),  ('QTL',  'LOI', 'VAR'),  ('CROP', 'HAS', 'ABS'),
    ('VAR',  'HAS', 'ABS'),  ('VAR',  'HAS', 'BIS'),  ('BM',   'USE', 'CROP'),
    ('CHR',  'LOI', 'VAR'),  ('TRT',  'LOI', 'TRT'),  ('ABS',  'LOI', 'CHR'),
    ('BIS',  'LOI', 'CHR'),  ('GST',  'AFF', 'TRT'),  ('CROP', 'AFF', 'TRT'),
}

# ===== 加载数据 =====
print("加载数据...")
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA_ALL = json.load(f)

# 小批量测试支持
TEST_DATA = TEST_DATA_ALL[:TEST_LIMIT] if TEST_LIMIT else TEST_DATA_ALL
print(f"训练集: {len(TRAIN_DATA)} 条 | 测试集: {len(TEST_DATA)} 条")

# 构建合法三元组集合
LEGAL_TRIPLETS = set()
for item in TRAIN_DATA:
    for r in item.get('relations', []):
        LEGAL_TRIPLETS.add((r['head_type'], r['label'], r['tail_type']))

# ===== TF-IDF 检索索引 =====
print("构建 TF-IDF 检索索引...")
TRAIN_TEXTS  = [item['text'] for item in TRAIN_DATA]
tfidf        = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)
print(f"完成，维度：{TRAIN_MATRIX.shape}")

# ===== 专项漏标示例 =====
def find_examples_for_triplet(head_type, rel, tail_type, n=2):
    examples = []
    for item in TRAIN_DATA:
        for r in item.get('relations', []):
            if r['head_type'] == head_type and r['label'] == rel and r['tail_type'] == tail_type:
                examples.append(item)
                break
        if len(examples) >= n:
            break
    return examples

GENE_LOI_TRT_EX = find_examples_for_triplet('GENE', 'LOI', 'TRT', 2)
MRK_LOI_CHR_EX  = find_examples_for_triplet('MRK',  'LOI', 'CHR', 2)
VAR_USE_BM_EX   = find_examples_for_triplet('VAR',  'USE', 'BM',  2)


def retrieve_top_k(query_text: str, k: int = TOP_K) -> list:
    vec  = tfidf.transform([query_text])
    sims = cosine_similarity(vec, TRAIN_MATRIX).flatten()
    top  = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[i] for i in top if sims[i] > 0.01][:k]


def format_example(item: dict) -> str:
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return f'Input: {item["text"]}\nOutput: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}'


def build_fewshot(rag_samples: list, text: str) -> str:
    lines = ["## Positive Examples (retrieved by similarity + targeted)"]
    for s in rag_samples:
        lines.append(format_example(s))
        lines.append("")
    text_lower = text.lower()
    injected   = set()
    if any(w in text_lower for w in ['gene', 'locus', 'loci', 'allele']) and GENE_LOI_TRT_EX:
        ex = GENE_LOI_TRT_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: GENE-LOI-TRT pattern", format_example(ex), ""]
            injected.add(id(ex))
    if any(w in text_lower for w in ['marker', 'ssr', 'snp', 'qtl', 'chromosome']) and MRK_LOI_CHR_EX:
        ex = MRK_LOI_CHR_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: MRK-LOI-CHR pattern", format_example(ex), ""]
            injected.add(id(ex))
    if any(w in text_lower for w in ['breeding', 'selection', 'backcross', 'gwas', 'mas', 'mabc']) and VAR_USE_BM_EX:
        ex = VAR_USE_BM_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: VAR-USE-BM pattern", format_example(ex), ""]
            injected.add(id(ex))
    return "\n".join(lines)


CICL_BLOCK = '''
## Contrastive Examples (avoid these common mistakes)

# MISTAKE 1: Over-predicting TRT — only annotate the MAIN trait, not every parameter
# WRONG: label "leaf area", "stomatal conductance" as TRT when they are just measurements
# CORRECT: only the primary trait under investigation is TRT

# MISTAKE 2: Missing CROP entities — ALWAYS annotate crop species names
# WRONG: annotate "BTx623" as VAR but miss "sorghum" as CROP
# CORRECT: {"text": "BTx623", "label": "VAR"}, {"text": "sorghum", "label": "CROP"}

# MISTAKE 3: Missing GENE-LOI-TRT — when a gene is mapped to a trait locus
# "The Dw3 gene was mapped to a region associated with plant height"
# CORRECT: GENE-LOI-TRT relation must be annotated here

# MISTAKE 4: Illegal HAS direction — HAS must be (CROP or VAR) → TRT
# WRONG: {"head": "Grain yield", "head_type": "TRT", "tail": "Pioneer 9306", "tail_type": "VAR", "label": "HAS"}
# CORRECT: {"head": "Pioneer 9306", "head_type": "VAR", "tail": "Grain yield", "tail_type": "TRT", "label": "HAS"}

# MISTAKE 5: Missing CON — when CROP explicitly contains/includes multiple VARs
# "Sorghum varieties including BTx623 and Tx430 were evaluated"
# CORRECT: CON(sorghum→BTx623), CON(sorghum→Tx430)
'''

SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Entity Types (12)
CROP: crop species name — ALWAYS annotate crop species even if mentioned briefly (sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea, etc.)
VAR: cultivar/variety name (e.g., BTx623, Morex, Pioneer 9306, Yugu1)
GENE: gene name or ID (e.g., Dw3, HvCBF4, SbDREB, SiMYB)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1, qGY-2H)
MRK: molecular marker (e.g., Xgwm11, RM223, SSR markers, SNP markers)
TRT: trait/phenotype — ONLY the MAIN trait under study. Do NOT over-annotate measurement parameters.
ABS: abiotic stress (e.g., drought, heat, salinity, cold, waterlogging)
BIS: biotic stress (e.g., Fusarium, rust, aphid, Colletotrichum)
BM: breeding method (GWAS, QTL mapping, MAS, MABC, backcross — NOT lab techniques like RNA-seq/PCR/CRISPR)
CHR: chromosome identifier — strip "chromosome" prefix (e.g., "chromosome 2H" → "2H")
CROSS: hybrid/segregating population (RILs, DH lines, F2 population — NOT VAR)
GST: growth stage (e.g., seedling stage, heading stage, anthesis, flowering)

## Relation Types (6)
AFF: biological causation — REQUIRES causal verbs: regulates/controls/affects/influences/increases/decreases/promotes/inhibits/encodes/determines
LOI: physical mapping — REQUIRES mapping language: mapped/located/associated with/linked/detected on/identified on/found on
HAS: possession — (CROP or VAR) POSSESSES a trait. Head MUST be CROP or VAR. NEVER TRT→VAR.
CON: composition — CROP contains VAR or GENE
USE: (VAR or CROSS or CROP) uses breeding method (BM)
OCI: occurs at growth stage — head is entity, tail is GST

## Critical Rules
1. CROP: ALWAYS annotate crop species names — this is the most commonly missed entity type.
2. TRT: Do NOT over-annotate. Only the primary trait being studied.
3. LOI(GENE→TRT) is common — do not miss it when a gene is mapped to a trait.
4. HAS direction: ALWAYS (CROP/VAR) → TRT. NEVER TRT → anything.
5. 32.7% of sentences have NO relations. Output [] when no clear semantic link exists.
6. Entity "text" MUST be EXACT substring of input sentence.
7. Output valid JSON only: {"entities": [...], "relations": [...]}"""


def resolve(text: str, raw: dict):
    entities_out, relations_out = [], []
    used_spans, entity_map = set(), {}
    for e in raw.get("entities", []):
        et, lb = e.get("text", "").strip(), e.get("label", "")
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
        ht, tt = r.get("head", "").strip(), r.get("tail", "").strip()
        hty, tty, rl = r.get("head_type", ""), r.get("tail_type", ""), r.get("label", "")
        if not all([ht, tt, hty, tty, rl]):
            continue
        if (hty, rl, tty) in ILLEGAL_TRIPLETS:
            continue
        if (hty, rl, tty) not in LEGAL_TRIPLETS:
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
    """获取 GLM API 客户端（线程安全，使用 OpenAI 兼容接口）"""
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI(api_key=GLM_API_KEY, base_url=GLM_BASE_URL)
    return _thread_local.client


def predict_one(idx: int, text: str):
    rag_samples   = retrieve_top_k(text)
    fewshot_block = build_fewshot(rag_samples, text)
    for attempt in range(3):
        try:
            time.sleep(attempt * 2)
            client = get_client()
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": (
                        f"{fewshot_block}\n{CICL_BLOCK}\n"
                        f"## Now annotate:\nInput: {text}\nOutput:"
                    )}
                ],
                temperature=0.1,   # 略高于 0，保留少量多样性但保持稳定
                max_tokens=2048
            )
            raw_str = resp.choices[0].message.content.strip()
            raw_str = re.sub(r'^```json\s*', '', raw_str)
            raw_str = re.sub(r'^```\s*',     '', raw_str)
            raw_str = re.sub(r'\s*```$',     '', raw_str)
            raw = json.loads(raw_str)
            ents, rels = resolve(text, raw)
            return idx, text, ents, rels, None
        except json.JSONDecodeError:
            if attempt == 2:
                return idx, text, [], [], "JSONError"
        except Exception as ex:
            if attempt == 2:
                return idx, text, [], [], f"Error: {str(ex)[:60]}"
            time.sleep(2 ** attempt)
    return idx, text, [], [], "max_retries"


# ===== 主程序 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    # 只加载与当前 TEST_DATA 长度匹配的部分
    for i, r in enumerate(existing[:len(TEST_DATA)]):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS}")

save_lock       = threading.Lock()
completed_count = [0]
failed_list     = []


def save_results():
    ordered = [results_dict[i] for i in sorted(results_dict.keys())]
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)


with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(predict_one, i, TEST_DATA[i]["text"]): i for i in pending}
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
            print(f"[{idx+1:>3}/{len(TEST_DATA)}] {text[:50]}... {status}")
            if done % SAVE_EVERY == 0:
                save_results()
                print(f"  >>> 已保存 {len(results_dict)}/{len(TEST_DATA)} 条 <<<")

save_results()
print(f"\n===== 全部完成 =====")
print(f"总条数: {len(TEST_DATA)} | 成功: {len(TEST_DATA)-len(failed_list)} | 失败: {len(failed_list)}")
if failed_list:
    print(f"失败索引: {sorted(failed_list)}")
print(f"输出: {OUTPUT_PATH}")

# ===== 统计输出 =====
total_rel = sum(len(d.get('relations', [])) for d in results_dict.values())
no_rel    = sum(1 for d in results_dict.values() if not d.get('relations'))
n = len(results_dict)
if n > 0:
    print(f"\n关系均值: {total_rel/n:.2f} | 无关系比: {no_rel/n*100:.1f}%")
    print(f"(参考: v17=2.24, 训练集期望=2.80)")
