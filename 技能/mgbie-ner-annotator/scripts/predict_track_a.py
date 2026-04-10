#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本 v2
核心改进：模型只输出实体文本和标签，脚本自动计算精确字符偏移量，彻底消除边界计算错误。
用法: python3 predict_track_a.py --test <test_A.json路径> --output <输出路径>
"""
import json, os, re, argparse, time
from openai import OpenAI

client = OpenAI()

def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# ===== 系统提示词：模型只输出文本，不输出数字偏移 =====
SYSTEM_PROMPT = """You are an expert in Named Entity Recognition (NER) and Relation Extraction (RE) for coarse grain crop breeding literature.

Your task: Given a sentence, extract entities and relations using the schema below.

## Entity Types (12 types)
- CROP: Crop species (e.g., sorghum, foxtail millet, buckwheat, barley, oat)
- VAR: Specific cultivar/variety names (e.g., BTx623, Hegari, Zhonggu 9)
- GENE: Gene names, gene IDs, transcription factors (e.g., SbWRKY50, ABI5, Sb09g005700)
- QTL: Quantitative trait loci (e.g., qGY-1, QTL)
- MRK: Molecular markers (e.g., Xgwm11, SSR marker names, SNP IDs)
- TRT: Traits or phenotypes (e.g., grain yield, drought resistance, plant height)
- ABS: Abiotic stress conditions (e.g., drought, salinity, heat stress, high temperature)
- BIS: Biotic stress (e.g., powdery mildew, rust, nematodes, Erysiphe graminis)
- BM: Breeding methods (e.g., marker-assisted breeding, GWAS, QTL mapping, composite interval mapping)
- CHR: Chromosome identifiers (e.g., 1A, 2H, 3B, chromosome 5)
- CROSS: Hybrid populations (e.g., RILs, DH lines, F2 population, BC lines)
- GST: Growth stages (e.g., seedling stage, germination, flowering, heading)

## Relation Types (6 types)
- AFF: head affects/influences tail (ABS→TRT, GENE→TRT, ABS→GENE most common)
- LOI: head is located on/associated with tail (QTL→TRT 31%, QTL→CHR 20%, MRK→CHR 6%)
- HAS: head has/possesses trait (VAR→TRT 61%, CROP→TRT 30%)
- CON: head contains/consists of tail (CROP→VAR 43%, CROP→GENE 12%)
- USE: head uses/employs tail (VAR→BM 45%, CROP→BM 9%)
- OCI: head occurs at/during tail (TRT→GST 46%, ABS→GST 34%)

## Critical Rules
1. LOI(QTL→TRT) is the most common LOI pattern (31%). Do NOT convert it to AFF.
2. 32.7% of sentences have NO relations at all. Leave relations empty if unclear.
3. Entity text must be an EXACT substring of the input sentence.
4. Do NOT annotate: ddRAD-seq, RT-qPCR, RNA-seq, CRISPR as BM (they are lab techniques, not breeding methods).
5. Do NOT annotate protein names as TRT.
6. RILs, DH lines, F2 populations → CROSS (not VAR).
7. Latin name + common name pairs → do NOT create CON relation.
8. Strip type prefixes: "marker Xgwm11" → entity text is "Xgwm11" (MRK); "chromosome 2H" → "2H" (CHR).
9. AFF head = influencing party (ABS/GENE/MRK/QTL/BM/BIS); tail = TRT/GENE usually.

## Output Format (JSON only, no explanation, no markdown)
{
  "entities": [{"text": "<exact substring>", "label": "<TYPE>"}],
  "relations": [{"head": "<entity text>", "head_type": "<TYPE>", "tail": "<entity text>", "tail_type": "<TYPE>", "label": "<REL>"}]
}"""

def build_fewshot_block(fewshot_samples):
    """构建 Few-shot 示例（只含文本和标签，不含偏移量）"""
    lines = ["## Examples\n"]
    for s in fewshot_samples:
        ents_out = [{"text": e["text"], "label": e["label"]} for e in s["entities"]]
        rels_out = [{"head": r["head"], "head_type": r["head_type"],
                     "tail": r["tail"], "tail_type": r["tail_type"],
                     "label": r["label"]} for r in s["relations"]]
        out = {"entities": ents_out, "relations": rels_out}
        lines.append(f"Input: {s['text']}")
        lines.append(f"Output: {json.dumps(out, ensure_ascii=False)}\n")
    lines.append("## Now annotate:")
    return "\n".join(lines)

def find_span(text, entity_text, used_spans):
    """在 text 中找到 entity_text 的精确位置，避免重复使用同一 span"""
    start = 0
    while True:
        idx = text.find(entity_text, start)
        if idx == -1:
            return None, None
        end = idx + len(entity_text)
        span = (idx, end)
        if span not in used_spans:
            used_spans.add(span)
            return idx, end
        start = idx + 1

def resolve_output(text, raw_pred):
    """将模型输出的文本标签转换为带精确偏移量的标准格式"""
    entities_out = []
    relations_out = []
    used_spans = set()
    entity_map = {}  # text -> (start, end, label)

    for e in raw_pred.get("entities", []):
        ent_text = e.get("text", "").strip()
        label = e.get("label", "")
        if not ent_text or not label:
            continue
        start, end = find_span(text, ent_text, used_spans)
        if start is None:
            # 尝试大小写不敏感匹配
            lower_text = text.lower()
            lower_ent = ent_text.lower()
            idx = lower_text.find(lower_ent)
            if idx != -1:
                start, end = idx, idx + len(ent_text)
                actual_text = text[start:end]
                used_spans.add((start, end))
                entities_out.append({"start": start, "end": end, "text": actual_text, "label": label})
                entity_map[ent_text] = (start, end, label, actual_text)
            # 找不到就跳过
            continue
        entities_out.append({"start": start, "end": end, "text": text[start:end], "label": label})
        entity_map[ent_text] = (start, end, label, text[start:end])

    for r in raw_pred.get("relations", []):
        head_text = r.get("head", "").strip()
        tail_text = r.get("tail", "").strip()
        head_type = r.get("head_type", "")
        tail_type = r.get("tail_type", "")
        rel_label = r.get("label", "")
        if not all([head_text, tail_text, head_type, tail_type, rel_label]):
            continue
        if head_text not in entity_map or tail_text not in entity_map:
            continue
        hs, he, _, ha = entity_map[head_text]
        ts, te, _, ta = entity_map[tail_text]
        relations_out.append({
            "head": ha, "head_start": hs, "head_end": he, "head_type": head_type,
            "tail": ta, "tail_start": ts, "tail_end": te, "tail_type": tail_type,
            "label": rel_label
        })

    return entities_out, relations_out

def predict_one(text, fewshot_block, max_retries=3):
    """预测单条文本"""
    user_msg = f"{fewshot_block}\nInput: {text}\nOutput:"
    
    for attempt in range(max_retries):
        try:
            extra = "\nRemember: output ONLY valid JSON. Entity text must be exact substrings of the input." if attempt > 0 else ""
            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg + extra}
                ],
                temperature=0,
                max_tokens=2048
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'^```\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            raw_pred = json.loads(raw)
            entities_out, relations_out = resolve_output(text, raw_pred)
            return entities_out, relations_out, None
        except json.JSONDecodeError as e:
            print(f"  [JSON解析失败 attempt {attempt+1}] {str(e)[:60]}")
        except Exception as e:
            print(f"  [API错误 attempt {attempt+1}] {str(e)[:60]}")
            time.sleep(2)
    
    return [], [], "max_retries_exceeded"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', default='/home/ubuntu/official_mgbie/dataset/test_A.json')
    parser.add_argument('--fewshot', default='/home/ubuntu/fewshot_samples.json')
    parser.add_argument('--output', default='/home/ubuntu/bisai_clone/数据/A榜/submit.json')
    parser.add_argument('--start', type=int, default=0)
    args = parser.parse_args()

    test_data = load_json(args.test)
    fewshot_samples = load_json(args.fewshot)
    fewshot_block = build_fewshot_block(fewshot_samples)

    # 断点续传
    results = []
    if os.path.exists(args.output) and args.start > 0:
        with open(args.output, encoding='utf-8') as f:
            results = json.load(f)
        print(f"断点续传：已加载 {len(results)} 条")

    total = len(test_data)
    failed = []

    for i, item in enumerate(test_data[args.start:], start=args.start):
        text = item['text']
        print(f"[{i+1}/{total}] {text[:60]}...")
        entities, relations, err = predict_one(text, fewshot_block)
        results.append({"text": text, "entities": entities, "relations": relations})
        if err:
            failed.append(i)
            print(f"  ⚠ 失败，空标注占位")
        else:
            print(f"  ✓ 实体:{len(entities)} 关系:{len(relations)}")

        if (i + 1) % 50 == 0:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  >>> 已保存 {len(results)} 条 <<<")

        time.sleep(0.2)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n===== 预测完成 =====")
    print(f"总条数: {total} | 成功: {total-len(failed)} | 失败: {len(failed)}")
    print(f"输出: {args.output}")

if __name__ == '__main__':
    main()
