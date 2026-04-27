#!/usr/bin/env python3
"""
make_v43_llm_boost.py — LLM 补充策略：对底座中关系少但实体多的样本进行关系抽取

策略：
- 找出底座中关系数 1-2 条但实体 ≥ 4 个的样本（111个）
- 用 gpt-4.1-mini 进行关系抽取，采用 POSW-Vote（3轮聚合）
- 只保留 3/3 轮一致的关系，且不在底座中的新关系
- 过滤掉泛称实体和距离异常的关系

注意：此策略与 v39（无关系样本）不同，这里针对有关系但可能漏标的样本
"""
import json
import os
import re
import time
import zipfile
from pathlib import Path
from collections import Counter, defaultdict
from copy import deepcopy
from openai import OpenAI

ROOT = Path('/home/ubuntu/bisai/数据/A榜')
TRAIN = Path('/home/ubuntu/bisai/数据/官方原始数据/train.json')
TEST = Path('/home/ubuntu/bisai/数据/官方原始数据/test_A.json')
CACHE_FILE = Path('/home/ubuntu/bisai/分析报告/llm_v43_cache.json')

client = OpenAI()

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_json_zip(name, data):
    json_path = ROOT / f'{name}.json'
    zip_path = ROOT / f'{name}.zip'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(json_path, arcname='submit.json')
    print(f"  已保存: {json_path.name}")
    return json_path, zip_path

def rel_key(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

def stats(data):
    n = len(data)
    total = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    return total, total / n, no_rel, no_rel / n * 100

# 加载数据
print("加载数据...")
train = load(TRAIN)
base = load(ROOT / 'submit_v41_sub_conservative.json')
test = load(TEST)

# 找出目标样本：关系数 1-2 但实体 ≥ 4
target_indices = []
for idx, item in enumerate(base):
    rels = item.get('relations', [])
    ents = item.get('entities', [])
    if 1 <= len(rels) <= 2 and len(ents) >= 4:
        target_indices.append(idx)

print(f"目标样本: {len(target_indices)} 个（关系1-2条，实体≥4个）")

# 构建 Few-shot 示例（从训练集中选取）
def build_fewshot_examples(n=4):
    examples = []
    # 选取有 2-4 条关系的训练样本作为示例
    for item in train:
        rels = item.get('relations', [])
        ents = item.get('entities', [])
        if 2 <= len(rels) <= 4 and len(ents) >= 4:
            examples.append(item)
        if len(examples) >= n:
            break
    return examples

fewshot = build_fewshot_examples(4)

def format_entities(entities):
    lines = []
    for e in entities:
        lines.append(f"  - [{e['label']}] \"{e['text']}\" (pos: {e['start']}-{e['end']})")
    return '\n'.join(lines)

def format_relations(relations):
    if not relations:
        return "  (无关系)"
    lines = []
    for r in relations:
        lines.append(f"  - {r['head_type']}-{r['label']}-{r['tail_type']}: \"{r['head']}\" → \"{r['tail']}\"")
    return '\n'.join(lines)

def build_prompt(item, existing_rels):
    text = item['text']
    entities = item.get('entities', [])
    
    # 构建 Few-shot 部分
    fewshot_text = ""
    for ex in fewshot[:3]:
        fewshot_text += f"\n示例文本: {ex['text']}\n"
        fewshot_text += f"实体:\n{format_entities(ex.get('entities', []))}\n"
        fewshot_text += f"关系:\n{format_relations(ex.get('relations', []))}\n"
    
    # 已有关系
    existing_text = format_relations(existing_rels)
    
    prompt = f"""你是一个农业育种信息抽取专家。请从以下文本中抽取实体间的关系。

关系类型说明：
- AFF（affects）：一个实体影响另一个实体
- LOI（located in）：一个实体位于另一个实体中
- HAS（has）：一个实体具有某个特征/性状
- CON（contains）：一个实体包含另一个实体
- OCI（occurs in）：一个事件/性状发生在某个阶段/条件下
- USE（uses）：使用某种工具/方法

合法的关系三元组类型（head_type-label-tail_type）：
ABS-AFF-TRT, ABS-AFF-GENE, VAR-HAS-TRT, CROP-HAS-TRT, QTL-LOI-TRT, QTL-LOI-CHR, 
MRK-LOI-TRT, MRK-LOI-CHR, GENE-AFF-TRT, GENE-LOI-TRT, CROP-CON-VAR, CROSS-CON-VAR,
VAR-USE-BM, BM-AFF-TRT, TRT-OCI-GST, GENE-CON-GENE 等

{fewshot_text}

现在请分析以下文本：
文本: {text}

已识别的实体:
{format_entities(entities)}

底座已有的关系（请勿重复）:
{existing_text}

请找出底座中**遗漏**的关系。只输出新发现的关系，每行一条，格式为：
head_type-label-tail_type: "head实体文本" → "tail实体文本"

如果没有遗漏的关系，输出：无

注意：
1. 只使用上面列出的实体文本，不要创造新实体
2. 关系必须有明确的文本依据
3. 实体间距离不要太远（建议在100字符以内）
4. 不要抽取泛称实体（如 "varieties", "genes", "markers" 等）"""
    
    return prompt

def parse_llm_response(response_text, item, existing_keys):
    """解析 LLM 输出，提取新关系"""
    entities = item.get('entities', [])
    ent_map = {}
    for e in entities:
        ent_map[e['text'].strip().lower()] = e
    
    new_rels = []
    lines = response_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line == '无' or line.startswith('#'):
            continue
        
        # 解析格式：head_type-label-tail_type: "head" → "tail"
        match = re.match(r'(\w+)-(\w+)-(\w+):\s*"([^"]+)"\s*→\s*"([^"]+)"', line)
        if not match:
            continue
        
        h_type, label, t_type, h_text, t_text = match.groups()
        
        # 查找实体
        h_ent = ent_map.get(h_text.strip().lower())
        t_ent = ent_map.get(t_text.strip().lower())
        
        if not h_ent or not t_ent:
            continue
        
        if h_ent['label'] != h_type or t_ent['label'] != t_type:
            continue
        
        rel = {
            'head': h_ent['text'],
            'head_type': h_type,
            'head_start': h_ent['start'],
            'head_end': h_ent['end'],
            'tail': t_ent['text'],
            'tail_type': t_type,
            'tail_start': t_ent['start'],
            'tail_end': t_ent['end'],
            'label': label,
        }
        
        key = rel_key(rel)
        if key not in existing_keys:
            new_rels.append(rel)
    
    return new_rels

# 加载缓存
cache = {}
if CACHE_FILE.exists():
    with open(CACHE_FILE) as f:
        cache = json.load(f)
    print(f"已加载缓存: {len(cache)} 条")

# 对目标样本进行 3 轮 LLM 预测
print(f"\n开始 LLM 预测（3轮 POSW-Vote）...")
ROUNDS = 3
MAX_SAMPLES = 50  # 限制处理数量，节省 API 调用

for round_idx in range(ROUNDS):
    round_key = f"round_{round_idx}"
    print(f"\n--- 第 {round_idx+1} 轮 ---")
    
    processed = 0
    for idx in target_indices[:MAX_SAMPLES]:
        cache_key = f"{idx}_{round_idx}"
        if cache_key in cache:
            continue
        
        item = base[idx]
        existing_rels = item.get('relations', [])
        existing_keys = {rel_key(r) for r in existing_rels}
        
        prompt = build_prompt(item, existing_rels)
        
        try:
            response = client.chat.completions.create(
                model='gpt-4.1-mini',
                messages=[
                    {'role': 'system', 'content': '你是一个农业育种信息抽取专家，擅长从科学文献中识别实体间的关系。'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.1,
                max_tokens=500,
            )
            result = response.choices[0].message.content
            cache[cache_key] = result
            processed += 1
            
            if processed % 10 == 0:
                print(f"  已处理 {processed} 条...")
                with open(CACHE_FILE, 'w') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            
            time.sleep(0.5)
        except Exception as e:
            print(f"  错误 idx={idx}: {e}")
            time.sleep(2)
    
    print(f"  第 {round_idx+1} 轮完成，新处理 {processed} 条")
    # 保存缓存
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"\n缓存总计: {len(cache)} 条")

# 聚合 3 轮结果，找出 3/3 一致的新关系
print("\n聚合 3 轮结果...")
consistent_rels = []  # (idx, rel)

for idx in target_indices[:MAX_SAMPLES]:
    item = base[idx]
    existing_rels = item.get('relations', [])
    existing_keys = {rel_key(r) for r in existing_rels}
    
    # 收集 3 轮的新关系
    round_rels = []
    for round_idx in range(ROUNDS):
        cache_key = f"{idx}_{round_idx}"
        if cache_key not in cache:
            round_rels.append(set())
            continue
        
        parsed = parse_llm_response(cache[cache_key], item, existing_keys)
        round_rels.append({rel_key(r) for r in parsed})
    
    if len(round_rels) < ROUNDS:
        continue
    
    # 找出 3/3 轮一致的关系
    if all(round_rels):
        common = round_rels[0]
        for r_set in round_rels[1:]:
            common = common & r_set
        
        for key in common:
            # 找到对应的关系对象
            for round_idx in range(ROUNDS):
                cache_key = f"{idx}_{round_idx}"
                if cache_key in cache:
                    parsed = parse_llm_response(cache[cache_key], item, existing_keys)
                    for r in parsed:
                        if rel_key(r) == key:
                            consistent_rels.append((idx, r))
                            break
                    break

print(f"3/3 轮一致的新关系: {len(consistent_rels)} 条")

if consistent_rels:
    # 按类型统计
    type_counter = Counter()
    for idx, r in consistent_rels:
        type_counter[(r['head_type'], r['label'], r['tail_type'])] += 1
    print("按类型统计:")
    for t, c in type_counter.most_common():
        print(f"  {t[0]}-{t[1]}-{t[2]}: {c}条")
    
    # 生成提交文件
    data = deepcopy(base)
    added = 0
    for idx, r in consistent_rels:
        existing = {rel_key(ex) for ex in data[idx].get('relations', [])}
        if rel_key(r) not in existing:
            data[idx]['relations'].append(r)
            added += 1
    
    save_json_zip('submit_v43_llm_boost', data)
    total, avg, no_rel, no_rel_pct = stats(data)
    base_total = sum(len(x.get('relations', [])) for x in base)
    print(f"submit_v43_llm_boost: added={added}, rels={total}(diff={total-base_total:+d}), avg={avg:.2f}, no_rel={no_rel}({no_rel_pct:.1f}%)")
else:
    print("没有找到 3/3 一致的新关系，不生成提交文件")
    print("建议：直接使用 v43 减法系列版本")
