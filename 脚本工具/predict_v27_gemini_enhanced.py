#!/usr/bin/env python3
"""
predict_v27_gemini_enhanced.py — Gemini 增强版预测脚本
核心改进（相比 v10）：
1. 针对高缺口三元组（ABS-AFF-TRT, CROP-CON-VAR, BM-AFF-TRT, VAR-USE-BM）添加专项示例
2. 改进 CICL 对比示例，专门展示这些三元组的正确标注方式
3. 在 System Prompt 中明确说明这些三元组的触发词模式
4. 扩展 RAG Top-K 到 6（覆盖更多关系类型）
目标：提升 ABS-AFF-TRT（缺口46条）、CROP-CON-VAR（缺口37条）等的召回率
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
import sys
sys.stdout.reconfigure(line_buffering=True)

# ===== 路径配置 =====
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v27_gemini_enhanced.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
MODEL      = "gemini-2.5-flash"
WORKERS    = 15
SAVE_EVERY = 20
TOP_K      = 6   # 增加到 6，覆盖更多关系类型

# ===== 非法三元组黑名单 =====
ILLEGAL_TRIPLETS = {
    ('VAR',  'CON', 'CROP'), ('GENE', 'CON', 'CROP'), ('CROSS','CON', 'CROP'),
    ('MRK',  'AFF', 'TRT'),  ('GENE', 'AFF', 'ABS'),
    ('TRT',  'HAS', 'VAR'),  ('TRT',  'HAS', 'CROP'), ('VAR',  'OCI', 'TRT'),
    ('VAR',  'AFF', 'BIS'),  ('QTL',  'LOI', 'VAR'),  ('CROP', 'HAS', 'ABS'),
    ('VAR',  'HAS', 'ABS'),  ('VAR',  'HAS', 'BIS'),  ('BM',   'USE', 'CROP'),
    ('CHR',  'LOI', 'VAR'),  ('TRT',  'LOI', 'TRT'),  ('ABS',  'LOI', 'CHR'),
    ('BIS',  'LOI', 'CHR'),  ('GST',  'AFF', 'TRT'),  ('CROP', 'AFF', 'TRT'),
    ('ABS',  'AFF', 'ABS'),  ('QTL',  'LOI', 'MRK'),
    ('CROSS','HAS', 'TRT'),  # 训练集14次但模型过标严重
}

# ===== 加载数据 =====
print("加载数据...", flush=True)
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)

# 构建合法三元组集合
LEGAL_TRIPLETS = set()
for item in TRAIN_DATA:
    for r in item.get('relations', []):
        LEGAL_TRIPLETS.add((r['head_type'], r['label'], r['tail_type']))
# 移除非法三元组
LEGAL_TRIPLETS -= ILLEGAL_TRIPLETS
print(f"合法三元组类型: {len(LEGAL_TRIPLETS)}", flush=True)

# ===== TF-IDF 检索索引 =====
print("构建 TF-IDF 检索索引...", flush=True)
TRAIN_TEXTS  = [item['text'] for item in TRAIN_DATA]
tfidf        = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
TRAIN_MATRIX = tfidf.fit_transform(TRAIN_TEXTS)
print(f"完成，维度：{TRAIN_MATRIX.shape}", flush=True)

# ===== 专项漏标示例提取 =====
def find_examples_for_triplet(head_type, rel, tail_type, n=2):
    """从训练集中找到包含特定三元组的示例（选关系数适中的）"""
    examples = []
    for item in TRAIN_DATA:
        for r in item.get('relations', []):
            if r['head_type'] == head_type and r['label'] == rel and r['tail_type'] == tail_type:
                examples.append(item)
                break
        if len(examples) >= n:
            break
    return examples

# 高缺口三元组专项示例
ABS_AFF_TRT_EX  = find_examples_for_triplet('ABS',  'AFF', 'TRT', 2)
CROP_CON_VAR_EX = find_examples_for_triplet('CROP', 'CON', 'VAR', 2)
BM_AFF_TRT_EX   = find_examples_for_triplet('BM',   'AFF', 'TRT', 2)
VAR_USE_BM_EX   = find_examples_for_triplet('VAR',  'USE', 'BM',  2)
GENE_LOI_TRT_EX = find_examples_for_triplet('GENE', 'LOI', 'TRT', 2)
MRK_LOI_CHR_EX  = find_examples_for_triplet('MRK',  'LOI', 'CHR', 2)
BIS_AFF_TRT_EX  = find_examples_for_triplet('BIS',  'AFF', 'TRT', 2)
QTL_AFF_TRT_EX  = find_examples_for_triplet('QTL',  'AFF', 'TRT', 2)

print(f"专项示例：ABS-AFF-TRT {len(ABS_AFF_TRT_EX)}, CROP-CON-VAR {len(CROP_CON_VAR_EX)}, "
      f"BM-AFF-TRT {len(BM_AFF_TRT_EX)}, VAR-USE-BM {len(VAR_USE_BM_EX)}", flush=True)

# ===== 检索函数 =====
def retrieve_top_k(query_text: str, k: int = TOP_K) -> list:
    vec  = tfidf.transform([query_text])
    sims = cosine_similarity(vec, TRAIN_MATRIX).flatten()
    top  = np.argsort(sims)[::-1][:k]
    return [TRAIN_DATA[i] for i in top if sims[i] > 0.01][:k]

# ===== 格式化示例 =====
def format_example(item: dict) -> str:
    ents = [{"text": e["text"], "label": e["label"]} for e in item["entities"]]
    rels = [{"head": r["head"], "head_type": r["head_type"],
             "tail": r["tail"], "tail_type": r["tail_type"],
             "label": r["label"]} for r in item["relations"]]
    return f'Input: {item["text"]}\nOutput: {json.dumps({"entities": ents, "relations": rels}, ensure_ascii=False)}'

# ===== 构建 Few-shot =====
def build_fewshot(rag_samples: list, text: str) -> str:
    lines = ["## Positive Examples (retrieved by similarity + targeted for high-gap patterns)"]
    
    # RAG 检索的相似样本
    for s in rag_samples:
        lines.append(format_example(s))
        lines.append("")
    
    text_lower = text.lower()
    injected   = set()
    
    # 1. ABS-AFF-TRT：检测到 stress/drought/heat/salinity/cold 等关键词
    if any(w in text_lower for w in ['stress', 'drought', 'heat', 'salt', 'salinity', 'cold', 'waterlogging', 'flooding', 'tolerance', 'resistance']) and ABS_AFF_TRT_EX:
        ex = ABS_AFF_TRT_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: ABS-AFF-TRT pattern (stress affects trait)", format_example(ex), ""]
            injected.add(id(ex))
    
    # 2. CROP-CON-VAR：检测到 variety/cultivar/accession/line 等关键词
    if any(w in text_lower for w in ['variety', 'varieties', 'cultivar', 'cultivars', 'accession', 'accessions', 'genotype', 'genotypes', 'line', 'lines']) and CROP_CON_VAR_EX:
        ex = CROP_CON_VAR_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: CROP-CON-VAR pattern (crop contains variety)", format_example(ex), ""]
            injected.add(id(ex))
    
    # 3. BM-AFF-TRT：检测到 intercropping/cropping/system 等关键词
    if any(w in text_lower for w in ['intercropping', 'monocropping', 'cropping', 'system', 'enhanced', 'improved', 'increased']) and BM_AFF_TRT_EX:
        ex = BM_AFF_TRT_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: BM-AFF-TRT pattern (breeding method affects trait)", format_example(ex), ""]
            injected.add(id(ex))
    
    # 4. VAR-USE-BM：检测到 breeding/selection/gwas/mas/mabc 等关键词
    if any(w in text_lower for w in ['breeding', 'selection', 'backcross', 'gwas', 'mas', 'mabc', 'marker-assisted']) and VAR_USE_BM_EX:
        ex = VAR_USE_BM_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: VAR-USE-BM pattern (variety uses breeding method)", format_example(ex), ""]
            injected.add(id(ex))
    
    # 5. GENE-LOI-TRT：检测到 gene/locus/loci/allele 等关键词
    if any(w in text_lower for w in ['gene', 'locus', 'loci', 'allele']) and GENE_LOI_TRT_EX:
        ex = GENE_LOI_TRT_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: GENE-LOI-TRT pattern", format_example(ex), ""]
            injected.add(id(ex))
    
    # 6. MRK-LOI-CHR：检测到 marker/ssr/snp/chromosome 等关键词
    if any(w in text_lower for w in ['marker', 'ssr', 'snp', 'qtl', 'chromosome']) and MRK_LOI_CHR_EX:
        ex = MRK_LOI_CHR_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: MRK-LOI-CHR pattern", format_example(ex), ""]
            injected.add(id(ex))
    
    # 7. BIS-AFF-TRT：检测到 disease/pathogen/fungal/rust/blast 等关键词
    if any(w in text_lower for w in ['disease', 'pathogen', 'fungal', 'rust', 'blast', 'blight', 'mildew', 'aphid', 'insect']) and BIS_AFF_TRT_EX:
        ex = BIS_AFF_TRT_EX[0]
        if id(ex) not in injected:
            lines += ["# Targeted: BIS-AFF-TRT pattern", format_example(ex), ""]
            injected.add(id(ex))
    
    return "\n".join(lines)

# ===== CICL 对比示例（专门针对高缺口三元组）=====
CICL_BLOCK = '''
## Contrastive Examples (Code-Style — common annotation mistakes to avoid)

# MISTAKE 1: Missing ABS-AFF-TRT — abiotic stress affects trait
# When ABS (drought/heat/salt/cold) CAUSES or AFFECTS a TRT, use AFF relation.
def annotate_wrong_abs_aff():
    text = "Drought stress significantly reduced grain yield in sorghum."
    result = {"entities": [{"text": "Drought stress", "label": "ABS"}, {"text": "grain yield", "label": "TRT"}, {"text": "sorghum", "label": "CROP"}], "relations": []}
    # ERROR: "reduced" is a causal verb. ABS-AFF-TRT must be annotated.
def annotate_correct_abs_aff():
    text = "Drought stress significantly reduced grain yield in sorghum."
    result = {"entities": [{"text": "Drought stress", "label": "ABS"}, {"text": "grain yield", "label": "TRT"}, {"text": "sorghum", "label": "CROP"}],
              "relations": [{"head": "Drought stress", "head_type": "ABS", "tail": "grain yield", "tail_type": "TRT", "label": "AFF"}]}
    # CORRECT: "reduced" triggers ABS-AFF-TRT. AFF verbs: reduced/increased/enhanced/decreased/affected/influenced/improved.

# MISTAKE 2: Missing CROP-CON-VAR — crop contains variety/cultivar/accession
# When a CROP species "contains" or "includes" named varieties, use CON relation.
def annotate_wrong_crop_con():
    text = "Two sorghum varieties, BTx623 and IS9830, were evaluated for drought tolerance."
    result = {"entities": [{"text": "sorghum", "label": "CROP"}, {"text": "BTx623", "label": "VAR"}, {"text": "IS9830", "label": "VAR"}, {"text": "drought tolerance", "label": "TRT"}], "relations": []}
    # ERROR: "sorghum varieties, BTx623 and IS9830" = CROP-CON-VAR for BOTH varieties.
def annotate_correct_crop_con():
    text = "Two sorghum varieties, BTx623 and IS9830, were evaluated for drought tolerance."
    result = {"entities": [{"text": "sorghum", "label": "CROP"}, {"text": "BTx623", "label": "VAR"}, {"text": "IS9830", "label": "VAR"}, {"text": "drought tolerance", "label": "TRT"}],
              "relations": [{"head": "sorghum", "head_type": "CROP", "tail": "BTx623", "tail_type": "VAR", "label": "CON"},
                            {"head": "sorghum", "head_type": "CROP", "tail": "IS9830", "tail_type": "VAR", "label": "CON"}]}
    # CORRECT: When crop contains multiple varieties in a list, annotate CON for EACH variety.

# MISTAKE 3: Missing BM-AFF-TRT — breeding method affects trait
# When a BM (intercropping/GWAS/MAS) ENHANCES or AFFECTS a TRT, use AFF.
def annotate_wrong_bm_aff():
    text = "Maize-peanut intercropping enhanced carbon fixation and carboxylation."
    result = {"entities": [{"text": "Maize-peanut intercropping", "label": "BM"}, {"text": "carbon fixation", "label": "TRT"}, {"text": "carboxylation", "label": "TRT"}], "relations": []}
    # ERROR: "enhanced" triggers BM-AFF-TRT for BOTH traits.
def annotate_correct_bm_aff():
    text = "Maize-peanut intercropping enhanced carbon fixation and carboxylation."
    result = {"entities": [{"text": "Maize-peanut intercropping", "label": "BM"}, {"text": "carbon fixation", "label": "TRT"}, {"text": "carboxylation", "label": "TRT"}],
              "relations": [{"head": "Maize-peanut intercropping", "head_type": "BM", "tail": "carbon fixation", "tail_type": "TRT", "label": "AFF"},
                            {"head": "Maize-peanut intercropping", "head_type": "BM", "tail": "carboxylation", "tail_type": "TRT", "label": "AFF"}]}
    # CORRECT: BM-AFF-TRT when breeding method enhances/improves/increases/decreases a trait.

# MISTAKE 4: Missing CROP entities — always annotate crop species names
def annotate_wrong_crop():
    text = "BTx623 sorghum showed enhanced drought tolerance."
    result = {"entities": [{"text": "BTx623", "label": "VAR"}, {"text": "drought tolerance", "label": "TRT"}], "relations": [{"head": "BTx623", "head_type": "VAR", "tail": "drought tolerance", "tail_type": "TRT", "label": "HAS"}]}
    # ERROR: "sorghum" is a CROP entity and must be annotated.
def annotate_correct_crop():
    text = "BTx623 sorghum showed enhanced drought tolerance."
    result = {"entities": [{"text": "BTx623", "label": "VAR"}, {"text": "sorghum", "label": "CROP"}, {"text": "drought tolerance", "label": "TRT"}],
              "relations": [{"head": "BTx623", "head_type": "VAR", "tail": "drought tolerance", "tail_type": "TRT", "label": "HAS"},
                            {"head": "sorghum", "head_type": "CROP", "tail": "BTx623", "tail_type": "VAR", "label": "CON"}]}
    # CORRECT: Always annotate crop species. Also add CROP-CON-VAR when crop contains the variety.

# MISTAKE 5: Illegal HAS direction — HAS must be (CROP or VAR) → TRT
def annotate_wrong_has():
    text = "Grain yield was observed in Pioneer 9306 under drought."
    result = {"relations": [{"head": "Grain yield", "head_type": "TRT", "tail": "Pioneer 9306", "tail_type": "VAR", "label": "HAS"}]}
    # ERROR: HAS direction must be (CROP/VAR) → TRT, NEVER TRT → VAR.
def annotate_correct_has():
    text = "Grain yield was observed in Pioneer 9306 under drought."
    result = {"relations": [{"head": "Pioneer 9306", "head_type": "VAR", "tail": "Grain yield", "tail_type": "TRT", "label": "HAS"}]}
    # CORRECT: HAS = (CROP or VAR) → TRT.
'''

# ===== System Prompt =====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).
## Entity Types (12)
CROP: crop species name — ALWAYS annotate crop species even if mentioned briefly (sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea, etc.)
VAR: cultivar/variety/line/accession name (e.g., BTx623, Morex, Pioneer 9306, Yugu1, IS9830)
GENE: gene name or ID (e.g., Dw3, HvCBF4, SbDREB, SiMYB, Waxy)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1, qGY-2H, QTL regions)
MRK: molecular marker (e.g., Xgwm11, RM223, SSR markers, SNP markers, SNPs)
TRT: trait/phenotype — ONLY the MAIN trait under study. Do NOT over-annotate measurement parameters.
ABS: abiotic stress (e.g., drought, heat, salinity, cold, waterlogging, drought stress, salt stress)
BIS: biotic stress (e.g., Fusarium, rust, aphid, Colletotrichum, blast, blight)
BM: breeding method (GWAS, QTL mapping, MAS, MABC, backcross, intercropping — NOT lab techniques like RNA-seq/PCR/CRISPR)
CHR: chromosome identifier — strip "chromosome" prefix (e.g., "chromosome 2H" → "2H", "chr3" → "3")
CROSS: hybrid/segregating population (RILs, DH lines, F2 population — NOT VAR)
GST: growth stage (e.g., seedling stage, heading stage, anthesis, flowering, germination)

## Relation Types (6) — with trigger words
AFF: biological causation — REQUIRES causal verbs: regulates/controls/affects/influences/increases/decreases/promotes/inhibits/encodes/determines/reduces/enhances/improves/confers/caused/resulted in
  - ABS-AFF-TRT: stress CAUSES/AFFECTS/REDUCES/INCREASES a trait (very common! ~285 in training)
  - GENE-AFF-TRT: gene REGULATES/CONTROLS/AFFECTS a trait
  - BM-AFF-TRT: breeding method ENHANCES/IMPROVES/INCREASES a trait
  - QTL-AFF-TRT: QTL AFFECTS/CONTROLS a trait
LOI: physical mapping — REQUIRES mapping language: mapped/located/associated with/linked/detected on/identified on/found on/for (QTL for TRT)
HAS: possession — (CROP or VAR) POSSESSES a trait. Head MUST be CROP or VAR. NEVER TRT→anything.
CON: composition — CROP contains VAR or GENE. Triggered by: variety/cultivar/accession/line/genotype/cv./including/such as/comprising
  - CROP-CON-VAR: very common (~222 in training). When crop species "contains" named varieties.
  - When a sentence lists multiple varieties of a crop (e.g., "sorghum varieties A and B"), annotate CON for EACH variety.
USE: (VAR or CROSS or CROP) uses breeding method (BM). Triggered by: using/used/via/through/by/employed/applied
OCI: occurs at growth stage — head is entity, tail is GST

## Critical Rules
1. CROP: ALWAYS annotate crop species names — most commonly missed entity type.
2. TRT: Do NOT over-annotate. Only the primary trait being studied.
3. ABS-AFF-TRT: When abiotic stress (drought/heat/salt/cold) affects a trait, ALWAYS annotate AFF. This is frequently missed.
4. CROP-CON-VAR: When a crop species contains named varieties/cultivars/accessions, ALWAYS annotate CON for EACH variety.
5. BM-AFF-TRT: When a breeding method (intercropping/GWAS/MAS) enhances/improves a trait, annotate AFF.
6. HAS direction: ALWAYS (CROP/VAR) → TRT. NEVER TRT → anything.
7. 32.7% of sentences have NO relations. Output [] when no clear semantic link exists.
8. Entity "text" MUST be EXACT substring of input sentence.
9. Output valid JSON only: {"entities": [...], "relations": [...]}"""

# ===== 解析函数 =====
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

# ===== 线程本地 OpenAI 客户端 =====
_thread_local = threading.local()
def get_client():
    if not hasattr(_thread_local, 'client'):
        _thread_local.client = OpenAI()
    return _thread_local.client

# ===== 单条预测 =====
def predict_one(idx: int, text: str):
    rag_samples   = retrieve_top_k(text)
    fewshot_block = build_fewshot(rag_samples, text)
    
    for attempt in range(3):
        try:
            if attempt > 0:
                time.sleep(2 ** attempt)
            resp = get_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": (
                        f"{fewshot_block}\n{CICL_BLOCK}\n"
                        f"## Now annotate:\nInput: {text}\nOutput:"
                    )}
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
        except json.JSONDecodeError:
            if attempt == 2:
                return idx, text, [], [], "JSONError"
        except Exception as ex:
            if attempt == 2:
                return idx, text, [], [], f"Error: {str(ex)[:40]}"
    return idx, text, [], [], "max_retries"

# ===== 主程序 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条", flush=True)

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"待处理: {len(pending)} 条 | 模型: {MODEL} | 线程: {WORKERS} | RAG Top-K: {TOP_K}", flush=True)

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
            print(f"[{idx+1:>3}/{len(TEST_DATA)}] {text[:50]}... {status}", flush=True)
            if done % SAVE_EVERY == 0:
                save_results()
                print(f"  >>> 已保存 {len(results_dict)}/{len(TEST_DATA)} 条 <<<", flush=True)

save_results()
print(f"\n===== 全部完成 =====", flush=True)
print(f"总条数: {len(TEST_DATA)} | 成功: {len(TEST_DATA)-len(failed_list)} | 失败: {len(failed_list)}", flush=True)
if failed_list:
    print(f"失败索引: {sorted(failed_list)}", flush=True)

# 统计
total_rels = sum(len(r.get('relations', [])) for r in results_dict.values())
no_rel = sum(1 for r in results_dict.values() if not r.get('relations', []))
print(f"关系总数: {total_rels}, 均值: {total_rels/len(results_dict):.2f}, 无关系: {no_rel} ({no_rel/len(results_dict)*100:.1f}%)", flush=True)
print(f"输出: {OUTPUT_PATH}", flush=True)
