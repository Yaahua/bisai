#!/usr/bin/env python3
"""
MGBIE Track-A 预测脚本
用法: python3 predict_track_a.py --test <test_A.json路径> --train <train.json路径> --output <输出路径>
"""
import json, os, re, argparse, time
from openai import OpenAI

client = OpenAI()  # 使用环境变量中的 API Key 和 Base URL

# ===== 加载数据 =====
def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# ===== 验证输出格式 =====
def validate_output(text_str, pred):
    """验证实体边界和关系锚点"""
    errors = []
    for e in pred.get('entities', []):
        try:
            if text_str[e['start']:e['end']] != e['text']:
                errors.append(f"实体边界错误: {e}")
        except Exception as ex:
            errors.append(f"实体字段异常: {e} | {ex}")
    for r in pred.get('relations', []):
        try:
            if text_str[r['head_start']:r['head_end']] != r['head']:
                errors.append(f"关系head边界错误: {r}")
            if text_str[r['tail_start']:r['tail_end']] != r['tail']:
                errors.append(f"关系tail边界错误: {r}")
        except Exception as ex:
            errors.append(f"关系字段异常: {r} | {ex}")
    return errors

# ===== 构建系统提示词 =====
SYSTEM_PROMPT = """You are an expert in Named Entity Recognition (NER) and Relation Extraction (RE) for coarse grain crop breeding literature.

Your task: Given a sentence from a scientific paper, extract all entities and relations according to the annotation schema below.

## Entity Types (12 types)
- CROP: Crop species names (e.g., sorghum, foxtail millet, buckwheat, barley, oat)
- VAR: Specific cultivar or variety names (e.g., BTx623, Hegari)
- GENE: Gene names, gene IDs, transcription factors (e.g., SbWRKY50, ABI5)
- QTL: Quantitative trait loci (e.g., qGY-1, QTL for grain yield)
- MRK: Molecular markers (e.g., SSR markers, SNP markers, Xgwm11)
- TRT: Traits or phenotypes (e.g., grain yield, drought resistance, plant height)
- ABS: Abiotic stress conditions (e.g., drought, salinity, heat stress)
- BIS: Biotic stress (e.g., powdery mildew, rust, nematodes)
- BM: Breeding methods (e.g., marker-assisted breeding, GWAS, QTL mapping)
- CHR: Chromosome identifiers (e.g., 1A, 2H, chromosome 3)
- CROSS: Hybrid populations or crossing materials (e.g., RILs, DH lines, F2 population)
- GST: Growth stages (e.g., seedling stage, germination, flowering)

## Relation Types (6 types)
- AFF: head affects/influences tail (e.g., ABS→TRT, GENE→TRT, ABS→GENE)
- LOI: head is located on/associated with tail (e.g., QTL→TRT, QTL→CHR, MRK→CHR)
- HAS: head has/possesses tail as a trait (e.g., VAR→TRT, CROP→TRT)
- CON: head contains/consists of tail (e.g., CROP→VAR, CROP→GENE)
- USE: head uses/employs tail (e.g., VAR→BM, CROP→BM)
- OCI: head occurs at/during tail (e.g., TRT→GST, ABS→GST)

## Critical Rules (MUST follow)
1. LOI(QTL→TRT) is the most common LOI pattern (31.4%). Do NOT convert it to AFF.
2. 32.7% of sentences have NO relations. Leave relations as [] if none are clear.
3. Entity boundary must be exact: text[start:end] must equal entity "text" field exactly.
4. Do NOT annotate experimental techniques (ddRAD-seq, RT-qPCR, RNA-seq) as BM.
5. Do NOT annotate protein names as TRT; annotate as GENE or skip.
6. RILs, DH lines, F2 populations are CROSS, not VAR.
7. Latin species names paired with common names are NOT CON relations.
8. Strip "marker", "gene", "chromosome" prefixes: e.g., "marker Xgwm11" → only "Xgwm11" is MRK.
9. AFF head must be the influencing party (ABS/GENE/MRK/QTL/BM/BIS), tail is usually TRT/GENE.
10. Output valid JSON only. No explanation, no markdown fences.

## Output Format
{"entities": [{"start": <int>, "end": <int>, "text": "<exact substring>", "label": "<type>"}], "relations": [{"head": "<text>", "head_start": <int>, "head_end": <int>, "head_type": "<type>", "tail": "<text>", "tail_start": <int>, "tail_end": <int>, "tail_type": "<type>", "label": "<rel_type>"}]}"""

def build_fewshot_block(fewshot_samples):
    """构建 Few-shot 示例块"""
    lines = ["## Examples\n"]
    for s in fewshot_samples:
        out = {"entities": s["entities"], "relations": s["relations"]}
        lines.append(f"Input: {s['text']}")
        lines.append(f"Output: {json.dumps(out, ensure_ascii=False)}\n")
    lines.append("## Now annotate:")
    return "\n".join(lines)

def predict_one(text, fewshot_block, max_retries=3):
    """预测单条文本，失败自动重试"""
    user_msg = f"{fewshot_block}\nInput: {text}\nOutput:"
    
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg if attempt == 0 
                     else user_msg + "\nRemember: output ONLY valid JSON, no explanation."}
                ],
                temperature=0,
                max_tokens=2048
            )
            raw = resp.choices[0].message.content.strip()
            # 清理可能的 markdown 代码块
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'^```\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            pred = json.loads(raw)
            errors = validate_output(text, pred)
            if not errors:
                return pred, None
            else:
                print(f"  [验证失败 attempt {attempt+1}] {errors[:2]}")
        except json.JSONDecodeError as e:
            print(f"  [JSON解析失败 attempt {attempt+1}] {e}")
        except Exception as e:
            print(f"  [API错误 attempt {attempt+1}] {e}")
            time.sleep(2)
    
    # 全部重试失败，返回空标注
    return {"entities": [], "relations": []}, "max_retries_exceeded"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', default='/home/ubuntu/official_mgbie/dataset/test_A.json')
    parser.add_argument('--train', default='/home/ubuntu/official_mgbie/dataset/train.json')
    parser.add_argument('--fewshot', default='/home/ubuntu/fewshot_samples.json')
    parser.add_argument('--output', default='/home/ubuntu/bisai_clone/数据/A榜/submit.json')
    parser.add_argument('--start', type=int, default=0, help='从第几条开始（断点续传）')
    args = parser.parse_args()

    test_data = load_json(args.test)
    fewshot_samples = load_json(args.fewshot)
    fewshot_block = build_fewshot_block(fewshot_samples)
    
    # 断点续传：若输出文件已存在，加载已完成的结果
    results = []
    if os.path.exists(args.output) and args.start > 0:
        with open(args.output, encoding='utf-8') as f:
            results = json.load(f)
        print(f"断点续传：已加载 {len(results)} 条结果")

    total = len(test_data)
    failed = []
    
    for i, item in enumerate(test_data[args.start:], start=args.start):
        print(f"[{i+1}/{total}] 预测中... text[:50]={item['text'][:50]}")
        pred, err = predict_one(item['text'], fewshot_block)
        result = {
            "text": item["text"],
            "entities": pred.get("entities", []),
            "relations": pred.get("relations", [])
        }
        results.append(result)
        if err:
            failed.append(i)
            print(f"  ⚠ 第{i+1}条失败，已用空标注占位")
        
        # 每50条保存一次（防止中断丢失）
        if (i + 1) % 50 == 0:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 已保存 {len(results)} 条")
        
        time.sleep(0.3)  # 避免触发速率限制

    # 最终保存
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n===== 预测完成 =====")
    print(f"总条数: {total}")
    print(f"成功: {total - len(failed)}")
    print(f"失败（空标注占位）: {len(failed)} 条，索引: {failed}")
    print(f"输出文件: {args.output}")

if __name__ == '__main__':
    main()
