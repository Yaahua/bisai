#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v15 — SuperICL 混合协作版
=================================================
核心创新（基于最新学术研究）：

【1】GLiNER 本地零样本预标注（零 API 成本）
  - 使用 GLiNER small 模型在本地对所有 400 条测试集进行 NER 预标注
  - 零 API 消耗，速度极快（CPU 上约 1-2 秒/条）
  - 将预标注结果注入 Prompt，作为 SuperICL 的"小模型建议"

【2】SuperICL 混合协作（大幅降低 API Token 消耗）
  - GLM 不再从头抽取所有信息，而是在 GLiNER 预标注基础上进行"校验+补充"
  - Prompt 格式：先给出 GLiNER 的预标注结果，再让 GLM 修正并补充关系
  - 预计节省 30-50% 的 Token 消耗

【3】语义缓存（Semantic Caching）
  - 对 400 条测试集进行 TF-IDF 相似度聚类
  - 相似度 > 0.85 的句子复用已有预测结果（仅替换实体文本）
  - 预计减少 15-25% 的 API 调用

【4】免费 GLM-4.7-Flash API（零成本）
  - 使用智谱 GLM-4.7-Flash（完全免费）替代 OpenAI API
  - 支持 200K 上下文，完全满足我们的 Prompt 长度需求

预期效果：API 消耗降低 50-70%，分数持平或超越 ensemble_v3（0.4172）
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
from gliner import GLiNER

# ===== 路径配置 =====
TRAIN_PATH  = '/home/ubuntu/official_mgbie/dataset/train.json'
TEST_PATH   = '/home/ubuntu/official_mgbie/dataset/test_A.json'
OUTPUT_PATH = '/home/ubuntu/bisai/数据/A榜/submit_v15_superICL.json'
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ===== 超参数 =====
GLM_API_KEY = '5e46ee14f1944eb4a705900c7f9d7b43.K35eAOcogzUiPlhd'
GLM_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4/'
MODEL       = 'glm-4-flash'   # 完全免费！
WORKERS     = 10               # GLM 免费版并发限制，保守设置
SAVE_EVERY  = 20
TOP_K       = 4                # RAG 检索数量
CACHE_THRESHOLD = 0.88         # 语义缓存相似度阈值

# ===== MGBIE 实体类型（GLiNER 使用）=====
ENTITY_LABELS = [
    'CROP', 'VAR', 'GENE', 'QTL', 'MRK', 'TRT',
    'ABS', 'BIS', 'BM', 'CHR', 'CROSS', 'GST'
]
GLINER_THRESHOLD = 0.45   # GLiNER 置信度阈值（稍低，保证召回）

# ===== 加载数据 =====
print("加载数据集...")
with open(TRAIN_PATH, encoding='utf-8') as f:
    TRAIN_DATA = json.load(f)
with open(TEST_PATH, encoding='utf-8') as f:
    TEST_DATA = json.load(f)

# ===== 加载 GLiNER 模型（本地，零 API 成本）=====
print("加载 GLiNER 本地模型（零 API 成本）...")
gliner_model = GLiNER.from_pretrained('urchade/gliner_small-v2.1')
print("GLiNER 加载完成！")

# ===== 构建 TF-IDF 检索索引 =====
print("构建 TF-IDF 检索索引...")
TRAIN_TEXTS = [item['text'] for item in TRAIN_DATA]
TEST_TEXTS  = [item['text'] for item in TEST_DATA]
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=50000, sublinear_tf=True)
ALL_TEXTS = TRAIN_TEXTS + TEST_TEXTS
tfidf.fit(ALL_TEXTS)
TRAIN_MATRIX = tfidf.transform(TRAIN_TEXTS)
TEST_MATRIX  = tfidf.transform(TEST_TEXTS)
print(f"TF-IDF 索引构建完成，维度：{TRAIN_MATRIX.shape}")

# ===== 语义缓存：预计算测试集内部相似度 =====
print("计算测试集内部语义相似度（用于缓存）...")
TEST_SIM_MATRIX = cosine_similarity(TEST_MATRIX, TEST_MATRIX)
# 对于每条测试句，找到比它索引小且相似度 > 阈值的句子（已处理过的）
CACHE_MAP = {}   # {test_idx: source_idx}  source_idx < test_idx
for i in range(len(TEST_DATA)):
    for j in range(i):
        if TEST_SIM_MATRIX[i, j] >= CACHE_THRESHOLD:
            CACHE_MAP[i] = j
            break
cache_hits = len(CACHE_MAP)
print(f"语义缓存：{cache_hits} 条可复用（节省 {cache_hits/len(TEST_DATA)*100:.1f}% API 调用）")

# ===== 从训练集中提取专项示例 =====
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

GENE_LOI_TRT_EXAMPLES = find_examples_for_triplet('GENE', 'LOI', 'TRT', 2)
MRK_LOI_CHR_EXAMPLES  = find_examples_for_triplet('MRK',  'LOI', 'CHR', 2)
VAR_USE_BM_EXAMPLES   = find_examples_for_triplet('VAR',  'USE', 'BM',  2)
print(f"专项示例加载完成")

# ===== RAG 检索 =====
def retrieve_top_k(query_idx: int, k: int = TOP_K) -> list:
    query_vec = TEST_MATRIX[query_idx]
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

# ===== GLiNER 预标注（SuperICL 的"小模型建议"）=====
print("\n开始 GLiNER 批量预标注（零 API 成本）...")
GLINER_CACHE = {}   # {test_idx: [{text, label, score}]}

# 批量预测（GLiNER 支持批量，速度更快）
batch_size = 50
for batch_start in range(0, len(TEST_DATA), batch_size):
    batch_end = min(batch_start + batch_size, len(TEST_DATA))
    batch_texts = [TEST_DATA[i]['text'] for i in range(batch_start, batch_end)]
    batch_results = gliner_model.batch_predict_entities(batch_texts, ENTITY_LABELS, threshold=GLINER_THRESHOLD)
    for i, entities in enumerate(batch_results):
        GLINER_CACHE[batch_start + i] = entities
    if (batch_start // batch_size + 1) % 2 == 0:
        print(f"  GLiNER 预标注进度: {batch_end}/{len(TEST_DATA)}")

print(f"GLiNER 预标注完成！共 {len(GLINER_CACHE)} 条")

# 统计 GLiNER 预标注质量
total_entities = sum(len(v) for v in GLINER_CACHE.values())
print(f"GLiNER 平均实体数: {total_entities/len(TEST_DATA):.2f}/条")

# ===== 系统提示词 =====
SYSTEM = """You are an expert NER and RE annotator for coarse grain crop breeding literature (MGBIE task).

## Entity Types (12)
CROP: crop species name (sorghum, barley, millet, quinoa, oat, buckwheat, foxtail millet, proso millet, mung bean, cowpea)
VAR: cultivar/variety name (e.g., BTx623, Morex, Pioneer 9306, Yugu1)
GENE: gene name or ID (e.g., Dw3, HvCBF4, SbDREB, SiMYB)
QTL: quantitative trait loci (e.g., qDT-3H, SbDT1, qGY-2H)
MRK: molecular marker (e.g., Xgwm11, RM223, SSR markers, SNP markers)
TRT: trait/phenotype — ONLY the MAIN trait under study (e.g., drought tolerance, grain yield, plant height)
ABS: abiotic stress (drought, heat, cold, salinity, waterlogging)
BIS: biotic stress (Fusarium, rust, aphid, Colletotrichum)
BM: breeding method (GWAS, QTL mapping, MAS, MABC, backcross)
CHR: chromosome identifier — strip "chromosome" prefix (e.g., "chromosome 2H" → "2H")
CROSS: hybrid/segregating population (RILs, DH lines, F2 population)
GST: growth stage (seedling stage, heading stage, anthesis, flowering)

## Relation Types (6)
AFF: biological causation (regulates/controls/affects/influences/increases/decreases/promotes/inhibits/encodes)
LOI: physical mapping (mapped/located/associated with/linked/detected on/identified on/found on)
HAS: possession — (CROP or VAR) POSSESSES a trait. Head MUST be CROP or VAR.
CON: composition — CROP contains VAR or GENE
USE: (VAR or CROSS or CROP) uses breeding method (BM)
OCI: occurs at growth stage

## Critical Rules
1. A local small model (GLiNER) has already suggested some entities. Review them carefully — accept correct ones, fix wrong ones, add missed ones.
2. 32.7% of sentences have NO relations. Output [] when no clear semantic link.
3. Entity "text" MUST be EXACT substring of input sentence.
4. Output valid JSON only. No explanation. No markdown fences."""


def build_superICL_prompt(test_idx: int, text: str) -> str:
    """构建 SuperICL Prompt：RAG 示例 + GLiNER 预标注建议"""
    lines = []

    # Part 1: RAG 检索的相似训练样本
    rag_samples = retrieve_top_k(test_idx, k=TOP_K)
    lines.append("## Retrieved Similar Examples:")
    for s in rag_samples:
        lines.append(format_example(s))
        lines.append("")

    # Part 2: 专项漏标示例（根据文本内容动态注入）
    text_lower = text.lower()
    injected = set()
    if any(w in text_lower for w in ['gene', 'locus', 'loci', 'allele']) and GENE_LOI_TRT_EXAMPLES:
        for ex in GENE_LOI_TRT_EXAMPLES[:1]:
            if id(ex) not in injected:
                lines.append("# Targeted: GENE-LOI-TRT pattern:")
                lines.append(format_example(ex))
                lines.append("")
                injected.add(id(ex))
    if any(w in text_lower for w in ['marker', 'ssr', 'snp', 'chromosome']) and MRK_LOI_CHR_EXAMPLES:
        for ex in MRK_LOI_CHR_EXAMPLES[:1]:
            if id(ex) not in injected:
                lines.append("# Targeted: MRK-LOI-CHR pattern:")
                lines.append(format_example(ex))
                lines.append("")
                injected.add(id(ex))
    if any(w in text_lower for w in ['breeding', 'selection', 'backcross', 'gwas', 'mas']) and VAR_USE_BM_EXAMPLES:
        for ex in VAR_USE_BM_EXAMPLES[:1]:
            if id(ex) not in injected:
                lines.append("# Targeted: VAR-USE-BM pattern:")
                lines.append(format_example(ex))
                lines.append("")
                injected.add(id(ex))

    # Part 3: SuperICL — GLiNER 预标注建议
    gliner_ents = GLINER_CACHE.get(test_idx, [])
    if gliner_ents:
        gliner_suggestion = [{"text": e["text"], "label": e["label"], "confidence": round(e["score"], 2)}
                             for e in gliner_ents]
        lines.append(f"## Local Model (GLiNER) Pre-annotation Suggestion:")
        lines.append(f"# The following entities were detected by a local zero-shot NER model.")
        lines.append(f"# Review carefully: accept correct ones, fix wrong labels, add missed entities.")
        lines.append(f"# GLiNER suggestion: {json.dumps(gliner_suggestion, ensure_ascii=False)}")
        lines.append("")

    # Part 4: 最终任务
    lines.append("## Now annotate (use GLiNER suggestion as reference, but apply your expert judgment):")
    lines.append(f"Input: {text}")
    lines.append("Output:")

    return "\n".join(lines)


def apply_cache(source_result: dict, target_text: str) -> dict:
    """将缓存结果应用到目标句子（替换实体文本）"""
    # 简单策略：直接返回 source 的结果，但验证实体文本是否在目标句子中
    new_entities = []
    entity_map = {}
    for e in source_result.get('entities', []):
        if e['text'] in target_text:
            new_entities.append(e.copy())
            entity_map[e['text']] = e

    new_relations = []
    for r in source_result.get('relations', []):
        if r['head'] in entity_map and r['tail'] in entity_map:
            new_relations.append(r.copy())

    return {'entities': new_entities, 'relations': new_relations}


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
        _thread_local.client = OpenAI(
            api_key=GLM_API_KEY,
            base_url=GLM_BASE_URL
        )
    return _thread_local.client


def predict_one(idx: int, text: str):
    client = get_client()

    # 检查语义缓存
    if idx in CACHE_MAP:
        source_idx = CACHE_MAP[idx]
        if source_idx in results_dict:
            cached = apply_cache(results_dict[source_idx], text)
            ents, rels = resolve(text, cached)
            return idx, text, ents, rels, None, True  # True = 缓存命中

    # 构建 SuperICL Prompt
    user_msg = build_superICL_prompt(idx, text)

    for attempt in range(3):
        try:
            resp = get_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": user_msg}
                ],
                temperature=0.1,   # GLM 稍微加一点温度，避免过于保守
                max_tokens=2048
            )
            raw_str = resp.choices[0].message.content.strip()
            raw_str = re.sub(r'^```json\s*', '', raw_str)
            raw_str = re.sub(r'^```\s*',     '', raw_str)
            raw_str = re.sub(r'\s*```$',     '', raw_str)
            raw = json.loads(raw_str)
            ents, rels = resolve(text, raw)
            return idx, text, ents, rels, None, False
        except json.JSONDecodeError:
            if attempt == 2:
                return idx, text, [], [], "JSONError", False
        except Exception as ex:
            err_msg = str(ex)
            if '429' in err_msg or 'rate' in err_msg.lower():
                time.sleep(5 * (attempt + 1))
            elif attempt == 2:
                return idx, text, [], [], f"Error: {err_msg[:40]}", False
            else:
                time.sleep(2 ** attempt)
    return idx, text, [], [], "max_retries", False


# ===== 主程序 =====
results_dict = {}
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, encoding='utf-8') as f:
        existing = json.load(f)
    for i, r in enumerate(existing):
        results_dict[i] = r
    print(f"断点续传：已有 {len(results_dict)} 条")

pending = [i for i in range(len(TEST_DATA)) if i not in results_dict]
print(f"\n待处理: {len(pending)} 条 | 模型: {MODEL}（免费）| 线程: {WORKERS}")
print(f"技术栈: GLiNER 预标注 + SuperICL + 语义缓存 + RAG 动态检索")

save_lock = threading.Lock()
completed_count = [0]
cache_hit_count = [0]
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
        result = future.result()
        idx, text, ents, rels, err, from_cache = result

        with save_lock:
            if err:
                failed_list.append(idx)
            else:
                results_dict[idx] = {
                    "text": text,
                    "entities": ents,
                    "relations": rels
                }
                if from_cache:
                    cache_hit_count[0] += 1

            completed_count[0] += 1
            if completed_count[0] % SAVE_EVERY == 0:
                save_results()
                print(f"进度: {completed_count[0]}/{len(pending)} | "
                      f"缓存命中: {cache_hit_count[0]} | 失败: {len(failed_list)}")

save_results()
print(f"\nv15 预测完成！")
print(f"  成功: {len(results_dict)} 条")
print(f"  缓存命中: {cache_hit_count[0]} 条（节省 API 调用）")
print(f"  失败: {len(failed_list)} 条 → {failed_list[:10]}")

# 统计
total_rels = sum(len(r.get('relations', [])) for r in results_dict.values())
no_rel = sum(1 for r in results_dict.values() if not r.get('relations'))
print(f"\n统计:")
print(f"  关系均值: {total_rels/len(results_dict):.2f}/条（期望 2.80）")
print(f"  无关系比例: {no_rel/len(results_dict)*100:.1f}%（期望 32.7%）")
print(f"\n已保存到: {OUTPUT_PATH}")
