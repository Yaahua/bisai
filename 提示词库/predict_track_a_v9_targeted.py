#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v9 — 针对性修复版（基于 v7 差距分析）
=============================================================
基于对 v7（0.3746）的深度分析，发现以下四个明确瓶颈：

【瓶颈 1】非法关系（FP 假阳性）：v7 预测了 40+ 个训练集中从未出现的三元组
  - TRT-HAS-VAR (8次), VAR-OCI-TRT (6次), VAR-AFF-BIS (4次) 等
  - 修复：扩展非法三元组黑名单，在后处理中强制删除

【瓶颈 2】关键三元组漏标（FN 假阴性）：
  - GENE-LOI-TRT: 期望 34 次，v7 仅 13 次（0.38x，严重漏标）
  - MRK-LOI-CHR: 期望 18 次，v7 仅 7 次（0.38x，严重漏标）
  - VAR-USE-BM: 期望 16 次，v7 仅 4 次（0.24x，严重漏标）
  - 修复：在 Few-shot 中专门加入这三种关系的示例

【瓶颈 3】TRT 实体过标（+5.2%）：
  - v7 TRT 比例 29.1%，训练集仅 23.9%
  - 过多 TRT 实体导致关系过标（如 TRT-AFF-TRT 1.56x，TRT-OCI-GST 1.70x）
  - 修复：在 Prompt 中强化 TRT 的识别标准，避免将一般描述性词汇标为 TRT

【瓶颈 4】CROP 实体漏标（-3.2%）：
  - v7 CROP 比例 8.9%，训练集 12.1%
  - CROP 漏标导致 CROP-CON-VAR（0.61x）和 CROP-HAS-TRT（0.71x）漏标
  - 修复：在 Prompt 中强化 CROP 的识别，包括缩写和别名

策略：在 v7 基础上，结合以上修复 + RAG 动态检索 + 代码风格 c-ICL
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
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v9_targeted.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gpt-4.1-mini"
WORKERS    = 20
SAVE_EVERY = 20
TOP_K      = 5   # 增加到 5 个正样本，覆盖更多关系类型

# ===== 扩展非法三元组黑名单（v7 分析新增）=====
ILLEGAL_TRIPLETS = {
    # 原有
    ('VAR',  'CON', 'CROP'),
    ('GENE', 'CON', 'CROP'),
    ('CROSS','CON', 'CROP'),
    ('MRK',  'AFF', 'TRT'),
    ('GENE', 'AFF', 'ABS'),
    # v7 分析新增（训练集中从未出现）
    ('TRT',  'HAS', 'VAR'),
    ('TRT',  'HAS', 'CROP'),
    ('VAR',  'OCI', 'TRT'),
    ('VAR',  'AFF', 'BIS'),
    ('QTL',  'LOI', 'VAR'),
    ('CROP', 'HAS', 'ABS'),
    ('VAR',  'HAS', 'ABS'),
    ('VAR',  'HAS', 'BIS'),
    ('BM',   'USE', 'CROP'),
    ('CHR',  'LOI', 'VAR'),
    ('TRT',  'LOI', 'TRT'),
    ('ABS',  'LOI', 'CHR'),
    ('BIS',  'LOI', 'CHR'),
    ('GST',  'AFF', 'TRT'),
    ('CROP', 'AFF', 'TRT'),
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

# ===== 从训练集中提取漏标三元组的专项示例 =====
def find_examples_for_triplet(head_type, rel, tail_type, n=2):
    """从训练集中找到包含特定三元组的示例"""
    examples = []
    for item in TRAIN_DATA:
        for r in item.get('relations', []):
            if r['head_type'] == head_type and r['label'] == rel and r['tail_type'] == tail_type:
                examples.append(item)
                break
        if len(examples) >= n:
            break
    return examples

# 预先提取漏标三元组的专项示例
GENE_LOI_TRT_EXAMPLES = find_examples_for_triplet('GENE', 'LOI', 'TRT', 2)
MRK_LOI_CHR_EXAMPLES  = find_examples_for_triplet('MRK',  'LOI', 'CHR', 2)
VAR_USE_BM_EXAMPLES   = find_examples_for_triplet('VAR',  'USE', 'BM',  2)
print(f"专项示例：GENE-LOI-TRT {len(GENE_LOI_TRT_EXAMPLES)}条, MRK-LOI-CHR {len(MRK_LOI_CHR_EXAMPLES)}条, VAR-USE-BM {len(VAR_USE_BM_EXAMPLES)}条")


def retrieve_top_k(query_text: str, k: int = TOP_K) -> list:
    query_vec = tfidf.transform([query_text])
    sims = cosine_similarity(query_vec, TRAIN_MATRIX).flatten()
    top_indices = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[idx] for idx in top_indices if sims[idx] > 0.01][:k]


def format_example(item: dict) -> str:
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return (f'Input: {item["text"]}\n'
            f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')


def build_fewshot(rag_samples: list, text: str) -> str:
    """构建 Few-shot，RAG 样本 + 针对漏标三元组的专项样本"""
    lines = ["## Positive Examples (retrieved by similarity + targeted for common missed patterns)"]

    # RAG 检索的相似样本
    for s in rag_samples:
        lines.append(format_example(s))
        lines.append("")

    # 根据文本内容，判断是否需要注入专项示例
    text_lower = text.lower()
    injected = set()

    # 如果文本含有 gene/locus 相关词，注入 GENE-LOI-TRT 示例
    if any(w in text_lower for w in ['gene', 'locus', 'loci', 'allele']) and GENE_LOI_TRT_EXAMPLES:
        for ex in GENE_LOI_TRT_EXAMPLES[:1]:
            key = id(ex)
            if key not in injected:
                lines.append("# Targeted example for GENE-LOI-TRT pattern:")
                lines.append(format_example(ex))
                lines.append("")
                injected.add(key)

    # 如果文本含有 marker/SSR/SNP 相关词，注入 MRK-LOI-CHR 示例
    if any(w in text_lower for w in ['marker', 'ssr', 'snp', 'qtl', 'chromosome']) and MRK_LOI_CHR_EXAMPLES:
        for ex in MRK_LOI_CHR_EXAMPLES[:1]:
            key = id(ex)
            if key not in injected:
                lines.append("# Targeted example for MRK-LOI-CHR pattern:")
                lines.append(format_example(ex))
                lines.append("")
                injected.add(key)

    # 如果文本含有 breeding/selection/backcross 相关词，注入 VAR-USE-BM 示例
    if any(w in text_lower for w in ['breeding', 'selection', 'backcross', 'gwas', 'mas', 'mabc']) and VAR_USE_BM_EXAMPLES:
        for ex in VAR_USE_BM_EXAMPLES[:1]:
            key = id(ex)
            if key not in injected:
                lines.append("# Targeted example for VAR-USE-BM pattern:")
                lines.append(format_example(ex))
                lines.append("")
                injected.add(key)

    return "\n".join(lines)


# ===== 代码风格 c-ICL 对比示例（针对 v7 的具体错误）=====
CICL_BLOCK = '''
## Contrastive Examples (Code-Style — showing v7's specific mistakes to avoid)

# MISTAKE 1: Over-predicting TRT entities (TRT is 29% in v7, should be 24%)
def annotate_wrong():
    text = "The drought stress caused significant changes in leaf area, stomatal conductance, and water use efficiency in barley."
    result = {"entities": [
        {"text": "drought stress", "label": "ABS"},
        {"text": "leaf area", "label": "TRT"},
        {"text": "stomatal conductance", "label": "TRT"},
        {"text": "water use efficiency", "label": "TRT"},
        {"text": "barley", "label": "CROP"}
    ]}
    # ERROR: "leaf area", "stomatal conductance" are measurement parameters here, not traits being studied.

def annotate_correct():
    text = "The drought stress caused significant changes in leaf area, stomatal conductance, and water use efficiency in barley."
    result = {"entities": [
        {"text": "drought stress", "label": "ABS"},
        {"text": "water use efficiency", "label": "TRT"},
        {"text": "barley", "label": "CROP"}
    ]}
    # CORRECT: Only annotate the main trait under study as TRT.

# MISTAKE 2: Missing CROP entities (CROP is 8.9% in v7, should be 12.1%)
def annotate_wrong_2():
    text = "BTx623 sorghum showed enhanced drought tolerance compared to wild-type plants."
    result = {"entities": [
        {"text": "BTx623", "label": "VAR"},
        {"text": "drought tolerance", "label": "TRT"}
    ]}
    # ERROR: "sorghum" is a CROP entity and must be annotated.

def annotate_correct_2():
    text = "BTx623 sorghum showed enhanced drought tolerance compared to wild-type plants."
    result = {"entities": [
        {"text": "BTx623", "label": "VAR"},
        {"text": "sorghum", "label": "CROP"},
        {"text": "drought tolerance", "label": "TRT"}
    ], "relations": [
        {"head": "BTx623", "head_type": "VAR", "tail": "drought tolerance", "tail_type": "TRT", "label": "HAS"}
    ]}
    # CORRECT: Always annotate the crop species name as CROP.

# MISTAKE 3: Missing GENE-LOI-TRT (v7 predicts only 38% of expected)
def annotate_wrong_3():
    text = "The Dw3 gene was mapped to a region associated with plant height on chromosome 7."
    result = {"entities": [
        {"text": "Dw3", "label": "GENE"},
        {"text": "plant height", "label": "TRT"},
        {"text": "chromosome 7", "label": "CHR"}
    ], "relations": [
        {"head": "Dw3", "head_type": "GENE", "tail": "chromosome 7", "tail_type": "CHR", "label": "LOI"}
    ]}
    # ERROR: "Dw3 gene mapped to region associated with plant height" = GENE-LOI-TRT. Missing this relation.

def annotate_correct_3():
    text = "The Dw3 gene was mapped to a region associated with plant height on chromosome 7."
    result = {"entities": [
        {"text": "Dw3", "label": "GENE"},
        {"text": "plant height", "label": "TRT"},
        {"text": "7", "label": "CHR"}
    ], "relations": [
        {"head": "Dw3", "head_type": "GENE", "tail": "plant height", "tail_type": "TRT", "label": "LOI"},
        {"head": "Dw3", "head_type": "GENE", "tail": "7", "tail_type": "CHR", "label": "LOI"}
    ]}
    # CORRECT: "mapped to region associated with" triggers GENE-LOI-TRT AND GENE-LOI-CHR.

# MISTAKE 4: Illegal relation TRT-HAS-VAR (appears 8 times in v7, never in training set)
def annotate_wrong_4():
    text = "Grain yield trait was observed in cultivar Pioneer 9306 under drought conditions."
    result = {"relations": [
        {"head": "Grain yield", "head_type": "TRT", "tail": "Pioneer 9306", "tail_type": "VAR", "label": "HAS"}
    ]}
    # ERROR: HAS direction must be CROP/VAR → TRT, never TRT → VAR. This is an illegal triplet.

def annotate_correct_4():
    text = "Grain yield trait was observed in cultivar Pioneer 9306 under drought conditions."
    result = {"relations": [
        {"head": "Pioneer 9306", "head_type": "VAR", "tail": "Grain yield", "tail_type": "TRT", "label": "HAS"}
    ]}
    # CORRECT: HAS = (CROP or VAR) → TRT. Head must be CROP or VAR.
'''

# ===== 系统提示词（强化 CROP 识别和 TRT 精确性）=====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Entity Types (12)
CROP: crop species name — ALWAYS annotate crop species even if mentioned briefly (e.g., sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea). This is frequently missed.
VAR: cultivar/variety name (e.g., BTx623, Morex, Pioneer 9306, Yugu1)
GENE: gene name or ID (e.g., Dw3, HvCBF4, SbDREB, SiMYB)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1, qGY-2H)
MRK: molecular marker (e.g., Xgwm11, RM223, SSR markers, SNP markers)
TRT: trait/phenotype — ONLY annotate the MAIN trait under study, NOT every measurement parameter. (e.g., drought tolerance, grain yield, plant height, starch content). Do NOT over-annotate.
ABS: abiotic stress (e.g., drought, heat, salinity, cold, waterlogging)
BIS: biotic stress (e.g., Fusarium, rust, aphid, Colletotrichum)
BM: breeding method (GWAS, QTL mapping, MAS, MABC, backcross — NOT lab techniques like RNA-seq/PCR/CRISPR)
CHR: chromosome identifier — strip "chromosome" prefix (e.g., "chromosome 2H" → "2H", "chr3" → "3")
CROSS: hybrid/segregating population (RILs, DH lines, F2 population — NOT VAR)
GST: growth stage (e.g., seedling stage, heading stage, anthesis, flowering)

## Relation Types (6)
AFF: biological causation — REQUIRES explicit causal verbs: regulates/controls/affects/influences/increases/decreases/promotes/inhibits/encodes/determines
LOI: physical mapping — REQUIRES explicit mapping language: mapped/located/associated with/linked/detected on/identified on/found on. GENE-LOI-TRT is common (when gene is mapped to trait locus).
HAS: possession — (CROP or VAR) POSSESSES a trait. Head MUST be CROP or VAR. NEVER TRT→VAR or TRT→CROP.
CON: composition — CROP contains VAR or GENE (not the reverse)
USE: (VAR or CROSS or CROP) uses breeding method (BM)
OCI: occurs at growth stage — head is entity, tail is GST

## Critical Rules
1. CROP entities: ALWAYS annotate crop species names. They are frequently missed. Look for: sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea, etc.
2. TRT entities: Do NOT over-annotate. Only the main trait being studied, not every measurement parameter.
3. LOI(QTL→TRT) is the most common LOI pattern (31%). LOI(GENE→TRT) is also common — do not miss it.
4. HAS direction: ALWAYS (CROP/VAR) → TRT. NEVER TRT → anything.
5. 32.7% of sentences have NO relations. Output [] when no clear semantic link.
6. Entity "text" MUST be EXACT substring of input sentence.
7. Output valid JSON only. No explanation. No markdown fences."""


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
    rag_samples = retrieve_top_k(text, k=TOP_K)
    fewshot_block = build_fewshot(rag_samples, text)

    for attempt in range(3):
        try:
            user_msg = (
                f"{fewshot_block}\n"
                f"{CICL_BLOCK}\n"
                f"## Now annotate (remember: annotate ALL crop species as CROP; "
                f"do not over-annotate TRT; check for GENE-LOI-TRT patterns):\n"
                f"Input: {text}\n"
                f"Output:"
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
                return idx, text, [], [], f"JSONError"
        except Exception as ex:
            if attempt == 2:
                return idx, text, [], [], f"Error: {str(ex)[:40]}"
            time.sleep(2 ** attempt)
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
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS}")
print(f"修复项：扩展非法三元组黑名单 | 专项漏标示例注入 | 强化 CROP/TRT 识别")

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
