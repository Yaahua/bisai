#!/usr/bin/env python3
"""
glm_nli_judge_v21.py
====================
GLM NLI 验证器：对 v4a 独有的 183 条关系进行 True/False 判定
理论依据：NLI-based Relation Extraction (NAACL 2025) + SCIR 自纠正框架 (AAAI 2026)

核心策略：
1. 将关系验证转化为 NLI 任务（不是"抽取关系"，而是"验证假设是否成立"）
2. 批量处理（每批 10 条），控制 API 调用次数
3. 对置信度低的样本进行自一致性采样（Self-Consistency）
4. 通过验证的关系追加到 v17_whitelist，生成 v21
"""
import json, os, time, copy
from collections import Counter
from openai import OpenAI

# ===== 配置 =====
CANDIDATES_PATH = '/home/ubuntu/bisai/数据/v4a_only_candidates.json'
BASE_PATH       = '/home/ubuntu/bisai/数据/A榜/submit_v17_whitelist.json'
OUTPUT_PATH     = '/home/ubuntu/bisai/数据/A榜/submit_v21_nli_judge.json'
CACHE_PATH      = '/home/ubuntu/bisai/数据/v21_nli_cache.json'

GLM_API_KEY  = '5e46ee14f1944eb4a705900c7f9d7b43.K35eAOcogzUiPlhd'
GLM_BASE_URL = 'https://open.bigmodel.cn/api/paas/v4/'
MODEL        = 'glm-4-flash'

BATCH_SIZE       = 10
MIN_CONFIDENCE   = 0.75   # 置信度阈值
SC_THRESHOLD     = 0.65   # 低于此置信度触发自一致性采样
SC_SAMPLES       = 3      # 自一致性采样次数

client = OpenAI(api_key=GLM_API_KEY, base_url=GLM_BASE_URL)

# ===== 关系类型定义 =====
RELATION_DEFS = {
    'LOI': 'LOI (Locus of Interest): A QTL/MRK/GENE is located on/mapped to a chromosome (CHR), or co-localized with a marker (MRK), or associated with a trait locus (TRT)',
    'AFF': 'AFF (Affects): A GENE/QTL/BM/ABS directly regulates, affects, controls, enhances, reduces, or influences a trait (TRT). The causal direction must be explicit.',
    'HAS': 'HAS (Has Trait): A CROP/VAR/CROSS variety/species has, exhibits, shows, or is characterized by a trait (TRT)',
    'CON': 'CON (Contains): A CROP species contains, includes, or encompasses a VAR variety/cultivar/genotype',
    'USE': 'USE (Used for): A BM/MRK biomarker/marker is used for, applied to, or employed in detecting/selecting/improving a trait (TRT) or biological method (BM)',
    'OCI': 'OCI (Occurs in): An entity (CROP/VAR/GENE/QTL) occurs, is observed, or is studied at/during a specific growth stage (GST)',
}

SYSTEM_PROMPT = """You are a strict expert in plant genetics and breeding information extraction. 
Your task is to verify whether proposed relationships between biological entities are EXPLICITLY and DIRECTLY stated in the given text.

Relationship type definitions:
- LOI: A QTL/MRK/GENE is located on/mapped to a chromosome (CHR) or co-localized with a marker (MRK)
- AFF: A GENE/QTL/BM directly regulates/affects/controls/influences a trait (TRT) — causal direction must be explicit
- HAS: A CROP/VAR/CROSS has/exhibits/shows a trait (TRT)
- CON: A CROP contains/includes a VAR variety/cultivar/genotype
- USE: A BM/MRK is used for detecting/selecting/improving a trait (TRT)
- OCI: An entity occurs/is observed at/during a growth stage (GST)

STRICT RULES — mark FALSE if ANY of these apply:
1. The relationship is only IMPLIED or INFERRED, not explicitly stated
2. The entity types do not match the relationship schema
3. The entities do not appear in the text with their stated types
4. The relationship direction is reversed or ambiguous
5. The relationship spans across different sentences without a clear connector

Respond ONLY with a valid JSON object in this exact format:
{"results": [{"id": <int>, "verdict": "TRUE" or "FALSE", "confidence": <float 0.0-1.0>, "reason": "<max 15 words>"}]}"""


def build_batch_prompt(batch):
    items = []
    for item in batch:
        r = item['relation']
        rel_def = RELATION_DEFS.get(r['label'], r['label'])
        items.append(
            f'[ID {item["id"]}]\n'
            f'Text: "{item["text"][:400]}"\n'
            f'Hypothesis: ({r["head"]} [{r["head_type"]}]) --[{r["label"]}]--> ({r["tail"]} [{r["tail_type"]}])\n'
            f'Schema: {rel_def}'
        )
    return '\n\n---\n\n'.join(items)


def call_glm(batch, temperature=0.1, retries=3):
    prompt = build_batch_prompt(batch)
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Verify the following {len(batch)} relationship hypotheses:\n\n{prompt}"}
                ],
                temperature=temperature,
                max_tokens=600,
            )
            content = resp.choices[0].message.content.strip()
            # 提取 JSON
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            data = json.loads(content)
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            elif isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"  GLM 错误 (尝试 {attempt+1}/{retries}): {str(e)[:100]}")
            if attempt < retries - 1:
                time.sleep(1.5 ** attempt)
    return []


def main():
    print("=== GLM NLI 验证器 v21 ===")
    candidates = json.load(open(CANDIDATES_PATH, encoding='utf-8'))
    base_data  = json.load(open(BASE_PATH, encoding='utf-8'))

    # 加载缓存
    cache = {}
    if os.path.exists(CACHE_PATH):
        cache = json.load(open(CACHE_PATH, encoding='utf-8'))
        print(f"加载缓存: {len(cache)} 条")

    # 添加 ID
    for i, c in enumerate(candidates):
        c['id'] = i

    # 过滤已缓存
    def cache_key(c):
        r = c['relation']
        return f"{c['doc_idx']}_{r['head']}_{r['label']}_{r['tail']}"

    to_verify = [c for c in candidates if cache_key(c) not in cache]
    print(f"候选总数: {len(candidates)}，待验证: {len(to_verify)}，已缓存: {len(candidates)-len(to_verify)}")

    # 批量验证
    total_batches = (len(to_verify) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\n开始验证（{total_batches} 批，每批 {BATCH_SIZE} 条）...")

    for batch_idx in range(total_batches):
        start = batch_idx * BATCH_SIZE
        batch = to_verify[start:start + BATCH_SIZE]
        if not batch:
            break

        results = call_glm(batch, temperature=0.1)
        result_map = {str(r.get('id', '')): r for r in results if isinstance(r, dict)}

        for item in batch:
            ck = cache_key(item)
            res = result_map.get(str(item['id']), {})
            verdict    = res.get('verdict', 'FALSE').upper()
            confidence = float(res.get('confidence', 0.0))
            reason     = res.get('reason', '')

            # 自一致性采样：置信度低时重复采样
            if confidence < SC_THRESHOLD and confidence > 0:
                sc_results = []
                for _ in range(SC_SAMPLES):
                    sc_res = call_glm([item], temperature=0.6)
                    if sc_res:
                        sc_results.append(sc_res[0].get('verdict', 'FALSE').upper())
                    time.sleep(0.2)
                if sc_results:
                    true_count = sc_results.count('TRUE')
                    verdict = 'TRUE' if true_count >= 2 else 'FALSE'
                    confidence = true_count / len(sc_results)
                    reason = f"SC({true_count}/{len(sc_results)}): {reason}"

            cache[ck] = {
                'verdict': verdict, 'confidence': confidence, 'reason': reason,
                'doc_idx': item['doc_idx'], 'relation': item['relation']
            }

        # 保存缓存
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        true_so_far = sum(1 for v in cache.values() if v['verdict'] == 'TRUE' and v['confidence'] >= MIN_CONFIDENCE)
        print(f"  批次 {batch_idx+1}/{total_batches} 完成 | 累计通过: {true_so_far} 条")
        time.sleep(0.3)

    # ===== 汇总结果 =====
    print("\n=== 验证结果汇总 ===")
    approved = [v for v in cache.values() if v['verdict'] == 'TRUE' and v['confidence'] >= MIN_CONFIDENCE]
    rejected = [v for v in cache.values() if v['verdict'] == 'FALSE' or v['confidence'] < MIN_CONFIDENCE]
    print(f"通过: {len(approved)} 条 | 拒绝: {len(rejected)} 条")

    label_cnt = Counter(v['relation']['label'] for v in approved)
    print(f"通过关系类型分布: {dict(label_cnt.most_common())}")

    # ===== 追加到 v17 =====
    print("\n将通过的关系追加到 v17_whitelist...")
    output_data = copy.deepcopy(base_data)

    def rel_key(r):
        return (r['head'].lower().strip(), r['head_type'], r['label'], r['tail'].lower().strip(), r['tail_type'])

    added = 0
    for item in approved:
        doc_idx = item['doc_idx']
        if doc_idx >= len(output_data):
            continue
        existing = {rel_key(r) for r in output_data[doc_idx].get('relations', [])}
        k = rel_key(item['relation'])
        if k not in existing:
            output_data[doc_idx]['relations'].append(item['relation'])
            added += 1

    total_rel = sum(len(d.get('relations', [])) for d in output_data)
    no_rel    = sum(1 for d in output_data if not d.get('relations'))
    print(f"实际新增: {added} 条")
    print(f"关系均值: {total_rel/len(output_data):.2f}（v17 基线: 2.24）")
    print(f"无关系比: {no_rel/len(output_data)*100:.1f}%")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"\n输出文件: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
