#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v15 — GLM-4.7-Flash + RAG + 强化 Prompt
=================================================================
策略：
1. 使用智谱 GLM-4.7-Flash（完全免费，200K 上下文）
2. TF-IDF RAG 动态检索 Top-4 训练样本作为 Few-shot
3. 强化 Prompt：明确 32.7% 无关系比例，强调召回率
4. 多线程并发（10 线程），断点续传
5. 对 ensemble_v3 的无关系句子进行补充预测（召回率提升）

目标：超越 ensemble_v3（0.4172）
"""
import json, os, re, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from openai import OpenAI

# ===== 路径配置 =====
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v15_glm.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== API 配置 =====
GLM_API_KEY  = '5e46ee14f1944eb4a705900c7f9d7b43.K35eAOcogzUiPlhd'
GLM_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4/'
MODEL        = 'glm-4-flash'

# ===== 超参数 =====
WORKERS    = 8
SAVE_EVERY = 25
TOP_K      = 4

# ===== 加载数据 =====
print("加载数据集...")
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)
print(f"训练集: {len(TRAIN_DATA)} 条，测试集: {len(TEST_DATA)} 条")

# ===== TF-IDF 检索索引 =====
print("构建 TF-IDF 检索索引...")
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
TEST_TEXTS  = [item['text'] for item in TEST_DATA]
tfidf = TfidfVectorizer(ngram_range=(1,2), max_features=50000, sublinear_tf=True)
tfidf.fit(TRAIN_TEXTS + TEST_TEXTS)
TRAIN_MATRIX = tfidf.transform(TRAIN_TEXTS)
TEST_MATRIX  = tfidf.transform(TEST_TEXTS)
print(f"TF-IDF 索引完成，维度: {TRAIN_MATRIX.shape}")

def retrieve_top_k(query_idx: int, k: int = TOP_K) -> list:
    sims = cosine_similarity(TEST_MATRIX[query_idx], TRAIN_MATRIX).flatten()
    top_idx = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[i] for i in top_idx if sims[i] > 0.01][:k]

def fmt_example(item: dict) -> str:
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return (f'Input: {item["text"]}\n'
            f'Output: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}')

# ===== 预加载专项示例（针对高频漏标类型）=====
def get_typed_examples(head_type, rel, tail_type, n=2):
    out = []
    for item in TRAIN_DATA:
        for r in item.get('relations', []):
            if r['head_type']==head_type and r['label']==rel and r['tail_type']==tail_type:
                out.append(item); break
        if len(out) >= n: break
    return out

EXAMPLES_GENE_LOI = get_typed_examples('GENE', 'LOI', 'TRT', 2)
EXAMPLES_MRK_LOI  = get_typed_examples('MRK',  'LOI', 'CHR', 2)
EXAMPLES_VAR_USE  = get_typed_examples('VAR',  'USE', 'BM',  2)
EXAMPLES_CROP_HAS = get_typed_examples('CROP', 'HAS', 'TRT', 2)
EXAMPLES_NO_REL   = [item for item in TRAIN_DATA if not item.get('relations')][:3]
print(f"专项示例加载完成")

# ===== 系统提示词（强化版 v2 — 防过度抽取）=====
SYSTEM = """You are a precise information extraction annotator for the MGBIE crop breeding NLP task.

## Entity Types (12 types)
- CROP: crop species name (sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea)
- VAR: cultivar/variety/inbred line name (e.g., BTx623, Morex, Pioneer 9306, Yugu1, IS 3620C)
- GENE: gene name or locus ID (e.g., Dw3, HvCBF4, SbDREB2, SiMYB3, ma1)
- QTL: quantitative trait loci name with prefix (e.g., qDT-3H, SbDT1, qGY-2H, qPH-7)
- MRK: molecular marker name (e.g., Xgwm11, RM223, Xtxp, SSR markers, SNP markers)
- TRT: trait/phenotype — the MAIN biological trait (e.g., drought tolerance, grain yield, plant height, flowering time)
- ABS: abiotic stress (drought, heat, cold, salinity, waterlogging, osmotic stress, nitrogen deficiency)
- BIS: biotic stress pathogen/pest (Fusarium head blight, rust, aphid, Colletotrichum, powdery mildew)
- BM: breeding/analysis method (GWAS, QTL mapping, MAS, MABC, backcross breeding, genomic selection)
- CHR: chromosome identifier — STRIP "chromosome" prefix ("chromosome 2H" → "2H", "Chr3" → "3", "LG10" → "LG10")
- CROSS: hybrid/segregating population (RILs, DH lines, F2 population, BC1F2, mapping population)
- GST: growth stage (seedling stage, heading stage, anthesis, flowering stage, grain filling stage)

## Relation Types (6 types)
- AFF: biological causation — gene/QTL/MRK AFFECTS/REGULATES/CONTROLS/ENCODES/INFLUENCES a trait
  Valid heads: GENE, QTL, MRK, VAR, CROP | Valid tails: TRT, ABS, BIS, GST
- LOI: physical location — entity is MAPPED/LOCATED/ASSOCIATED WITH/DETECTED ON a chromosome/marker/locus
  Valid heads: GENE, QTL, MRK, TRT | Valid tails: CHR, MRK, GENE, QTL
- HAS: possession — CROP or VAR POSSESSES/EXHIBITS/SHOWS a trait, stress, or growth stage
  Valid heads: CROP, VAR | Valid tails: TRT, ABS, BIS, GST
- CON: composition — CROP CONTAINS/INCLUDES a variety or gene
  Valid heads: CROP | Valid tails: VAR, GENE
- USE: breeding use — entity USES/EMPLOYS a breeding method
  Valid heads: VAR, CROSS, CROP | Valid tails: BM
- OCI: occurrence — entity OCCURS AT a growth stage
  Valid heads: TRT, ABS, BIS, GENE, QTL | Valid tails: GST

## STRICT Rules (follow exactly)
1. Entity "text" MUST be an EXACT substring of the input sentence.
2. Do NOT extract numbers, percentages, statistics (e.g., "15.5%", "543", "p<0.05") as entities.
3. Do NOT extract generic words as entities (e.g., "study", "analysis", "results", "population").
4. EXACTLY 32.7% of sentences have NO relations — output [] when no clear semantic link exists.
5. Each entity pair should have AT MOST ONE relation (the most semantically appropriate one).
6. Average 2.8 relations per sentence — do NOT over-extract. Quality > Quantity.
7. For CHR: strip "chromosome" prefix. Output "2H" not "chromosome 2H".
8. Output ONLY valid JSON with keys "entities" and "relations". No markdown, no explanation."""

def build_prompt(idx: int, text: str) -> str:
    lines = []
    rag = retrieve_top_k(idx, k=TOP_K)

    # 动态注入专项示例
    text_lower = text.lower()
    injected = set()

    # 无关系示例（帮助模型学会输出空关系）
    if any(w in text_lower for w in ['however', 'although', 'while', 'despite', 'but']):
        for ex in EXAMPLES_NO_REL[:1]:
            if id(ex) not in injected:
                rag = [ex] + rag[:3]
                injected.add(id(ex))

    # 专项示例注入
    targeted = []
    if any(w in text_lower for w in ['gene', 'locus', 'loci', 'allele', 'encodes']):
        for ex in EXAMPLES_GENE_LOI[:1]:
            if id(ex) not in injected:
                targeted.append(ex); injected.add(id(ex))
    if any(w in text_lower for w in ['marker', 'ssr', 'snp', 'chromosome', 'linkage']):
        for ex in EXAMPLES_MRK_LOI[:1]:
            if id(ex) not in injected:
                targeted.append(ex); injected.add(id(ex))
    if any(w in text_lower for w in ['breeding', 'selection', 'backcross', 'gwas', 'mas', 'qtl mapping']):
        for ex in EXAMPLES_VAR_USE[:1]:
            if id(ex) not in injected:
                targeted.append(ex); injected.add(id(ex))
    if any(w in text_lower for w in ['tolerance', 'resistance', 'susceptib', 'yield', 'height', 'weight']):
        for ex in EXAMPLES_CROP_HAS[:1]:
            if id(ex) not in injected:
                targeted.append(ex); injected.add(id(ex))

    all_examples = rag + targeted
    # 去重
    seen = set()
    unique_examples = []
    for ex in all_examples:
        key = ex['text'][:50]
        if key not in seen:
            seen.add(key)
            unique_examples.append(ex)

    lines.append("## Similar Training Examples (use as reference):")
    for ex in unique_examples[:6]:
        lines.append(fmt_example(ex))
        lines.append("")

    lines.append("## Now annotate the following sentence:")
    lines.append(f"Input: {text}")
    lines.append("Output:")
    return "\n".join(lines)

def resolve(text: str, raw: dict):
    """将模型输出解析为标准格式，验证实体文本是否在原文中"""
    entities_out, relations_out = [], []
    used_spans = set()
    entity_map = {}

    for e in raw.get("entities", []):
        et = e.get("text", "").strip()
        lb = e.get("label", "")
        if not et or not lb:
            continue
        idx = text.find(et)
        if idx == -1:
            lo = text.lower().find(et.lower())
            if lo != -1:
                idx = lo
            else:
                continue
        s, en = idx, idx + len(et)
        if (s, en) in used_spans:
            continue
        used_spans.add((s, en))
        actual = text[s:en]
        entities_out.append({"start": s, "end": en, "text": actual, "label": lb})
        if et not in entity_map:
            entity_map[et] = (s, en, actual, lb)
        if actual != et and actual not in entity_map:
            entity_map[actual] = (s, en, actual, lb)

    for r in raw.get("relations", []):
        ht  = r.get("head", "").strip()
        tt  = r.get("tail", "").strip()
        hty = r.get("head_type", "")
        tty = r.get("tail_type", "")
        rl  = r.get("label", "")
        if not all([ht, tt, hty, tty, rl]):
            continue
        if ht not in entity_map and ht.lower() not in {k.lower() for k in entity_map}:
            continue
        if tt not in entity_map and tt.lower() not in {k.lower() for k in entity_map}:
            continue
        # 找到实际的 key
        hkey = ht if ht in entity_map else next((k for k in entity_map if k.lower()==ht.lower()), None)
        tkey = tt if tt in entity_map else next((k for k in entity_map if k.lower()==tt.lower()), None)
        if not hkey or not tkey:
            continue
        hs, he, ha, _ = entity_map[hkey]
        ts, te, ta, _ = entity_map[tkey]
        relations_out.append({
            "head": ha, "head_start": hs, "head_end": he, "head_type": hty,
            "tail": ta, "tail_start": ts, "tail_end": te, "tail_type": tty,
            "label": rl
        })
    return entities_out, relations_out

# ===== 单条预测 =====
_tl = threading.local()

def get_client():
    if not hasattr(_tl, 'c'):
        _tl.c = OpenAI(api_key=GLM_API_KEY, base_url=GLM_BASE_URL)
    return _tl.c

def predict_one(idx: int, text: str):
    user_msg = build_prompt(idx, text)
    for attempt in range(4):
        try:
            resp = get_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": user_msg}
                ],
                temperature=0.0,
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
            if attempt == 3:
                return idx, text, [], [], "JSONError"
            time.sleep(1)
        except Exception as ex:
            msg = str(ex)
            if '429' in msg or 'rate' in msg.lower():
                time.sleep(8 * (attempt + 1))
            elif '401' in msg or 'auth' in msg.lower():
                return idx, text, [], [], f"AuthError"
            elif attempt == 3:
                return idx, text, [], [], f"Error:{msg[:40]}"
            else:
                time.sleep(2 ** attempt)
    return idx, text, [], [], "max_retries"

# ===== 主程序 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传: 已有 {len(results_dict)} 条")

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"\n待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS}")

save_lock = threading.Lock()
done = [0]
failed = []

def save_all():
    ordered = [results_dict[i] for i in sorted(results_dict.keys())]
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    futures = {executor.submit(predict_one, i, TEST_DATA[i]["text"]): i for i in pending}
    for fut in as_completed(futures):
        idx, text, ents, rels, err = fut.result()
        with save_lock:
            if err:
                failed.append((idx, err))
                print(f"  [FAIL] idx={idx} err={err}")
            else:
                results_dict[idx] = {"text": text, "entities": ents, "relations": rels}
            done[0] += 1
            if done[0] % SAVE_EVERY == 0:
                save_all()
                print(f"  进度: {done[0]}/{len(pending)} | 失败: {len(failed)}")

save_all()
print(f"\n✅ v15 预测完成！")
print(f"  成功: {len(results_dict)} 条 | 失败: {len(failed)}")

total_rels = sum(len(r.get('relations',[])) for r in results_dict.values())
no_rel = sum(1 for r in results_dict.values() if not r.get('relations'))
n = len(results_dict)
print(f"  关系均值: {total_rels/n:.2f}/条（期望 2.80）")
print(f"  无关系比例: {no_rel/n*100:.1f}%（期望 32.7%）")
print(f"  输出路径: {OUTPUT_PATH}")
