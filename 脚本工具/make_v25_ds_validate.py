#!/usr/bin/env python3
"""
v25: 用 DeepSeek 验证 v7/v9/v10 三模型中只有 1 票的关系
策略：
  - v17（三选二集成+白名单）是基线
  - 从 v7/v9/v10 的 1 票关系中，找 DeepSeek 也认同的（即 1+1=2 票）
  - 追加到 v17 上，生成 v25
"""
import json, copy, zipfile, os
from collections import defaultdict

# 文件路径
V7_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_v7_cicl_v2.json'
V9_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_v9_targeted.json'
V10_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_v10_gemini.json'
V17_PATH  = '/home/ubuntu/bisai/数据/A榜/submit_v17_whitelist.json'
DS_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_v23_glm47.json'
OUT_JSON  = '/home/ubuntu/bisai/数据/A榜/submit_v25_ds_validate.json'
OUT_ZIP   = '/home/ubuntu/bisai/数据/A榜/submit_v25_ds_validate.zip'

# Schema 合法性检查
VALID_SCHEMA = {
    'AFF': [('GENE','TRT'),('GENE','ABS'),('GENE','BIS'),('GENE','BM'),('GENE','GST'),
            ('QTL','TRT'),('QTL','ABS'),('QTL','BIS'),('QTL','BM'),('QTL','GST'),
            ('MRK','TRT'),('MRK','ABS'),('MRK','BIS'),('MRK','BM'),('MRK','GST'),
            ('VAR','TRT'),('VAR','ABS'),('VAR','BIS'),('VAR','BM'),('VAR','GST'),
            ('CROP','TRT'),('CROP','ABS'),('CROP','BIS'),('CROP','BM'),('CROP','GST'),
            ('CROSS','TRT'),('CROSS','ABS'),('CROSS','BIS'),('CROSS','BM'),('CROSS','GST')],
    'LOI': [('GENE','CHR'),('GENE','MRK'),('QTL','CHR'),('QTL','MRK'),
            ('MRK','CHR'),('MRK','MRK'),('GENE','GENE')],
    'HAS': [('CROP','GENE'),('CROP','QTL'),('CROP','MRK'),('CROP','CHR'),
            ('VAR','GENE'),('VAR','QTL'),('VAR','MRK'),
            ('CROSS','GENE'),('CROSS','QTL'),('CROSS','MRK'),
            ('GENE','GENE'),('QTL','MRK'),('QTL','GENE')],
    'CON': [('CROP','VAR'),('CROP','GENE'),('CROP','CROSS'),('CROP','QTL'),('CROP','MRK'),
            ('CROP','CROP'),('CROP','CHR'),('CROP','TRT'),('CROP','BM'),
            ('VAR','VAR'),('VAR','GENE'),('VAR','QTL'),('VAR','MRK'),('VAR','CROSS'),
            ('VAR','TRT'),('VAR','CROP'),
            ('GENE','GENE'),('GENE','CROP'),('GENE','VAR'),('GENE','CROSS'),('GENE','QTL'),
            ('GENE','TRT'),
            ('CROSS','VAR'),('CROSS','CROP'),('CROSS','CROSS'),('CROSS','GENE'),
            ('QTL','GENE'),('QTL','MRK'),('QTL','QTL'),('QTL','CHR'),
            ('MRK','MRK'),('TRT','TRT'),('TRT','GENE'),('TRT','CHR'),('TRT','CROP'),
            ('ABS','ABS'),('BM','BM'),('BM','GENE'),('BM','BIS'),('BM','TRT'),
            ('BIS','BIS'),('CHR','CHR'),('GST','GST')],
    'USE': [('MRK','GENE'),('MRK','QTL'),('MRK','VAR'),('MRK','CROP'),('MRK','CROSS'),
            ('MRK','TRT'),('MRK','ABS'),('MRK','BM'),('MRK','BIS'),('MRK','CHR'),
            ('GENE','VAR'),('GENE','CROP')],
    'OCI': [('GENE','GST'),('QTL','GST'),('MRK','GST'),('VAR','GST'),
            ('CROP','GST'),('CROSS','GST'),('GENE','TRT'),('QTL','TRT')]
}

def is_valid_schema(label, head_type, tail_type):
    return (head_type, tail_type) in VALID_SCHEMA.get(label, [])

def rel_key(r):
    return (r['head'].lower().strip(), r['head_type'], r['label'], r['tail'].lower().strip(), r['tail_type'])

def fuzzy_match(key1, key2):
    """宽松匹配：实体文本包含关系"""
    h1, ht1, l1, t1, tt1 = key1
    h2, ht2, l2, t2, tt2 = key2
    if l1 != l2 or ht1 != ht2 or tt1 != tt2:
        return False
    h_match = h1 in h2 or h2 in h1
    t_match = t1 in t2 or t2 in t1
    return h_match and t_match

print("加载文件...")
with open(V7_PATH) as f:  v7  = json.load(f)
with open(V9_PATH) as f:  v9  = json.load(f)
with open(V10_PATH) as f: v10 = json.load(f)
with open(V17_PATH) as f: v17 = json.load(f)
with open(DS_PATH) as f:  ds  = json.load(f)

# 按索引对齐
models = {'v7': v7, 'v9': v9, 'v10': v10}

added_total = 0
result = copy.deepcopy(v17)

for idx in range(len(v17)):
    # 收集各模型的关系 key
    model_rels = {}
    for name, data in models.items():
        model_rels[name] = set(rel_key(r) for r in data[idx].get('relations', []))
    
    ds_rels = set(rel_key(r) for r in ds[idx].get('relations', []))
    v17_rels = set(rel_key(r) for r in v17[idx].get('relations', []))
    
    # 找 v7/v9/v10 中只有 1 票的关系
    all_model_rels = list(model_rels['v7']) + list(model_rels['v9']) + list(model_rels['v10'])
    vote_count = defaultdict(int)
    for k in all_model_rels:
        vote_count[k] += 1
    
    one_vote_rels = {k for k, v in vote_count.items() if v == 1}
    
    # 找 DeepSeek 也认同的 1 票关系（且不在 v17 中）
    validated = []
    for k in one_vote_rels:
        if k in v17_rels:
            continue  # 已在 v17 中
        # 检查 Schema 合法性
        head, ht, label, tail, tt = k
        if not is_valid_schema(label, ht, tt):
            continue
        # 检查 DeepSeek 是否认同（严格或模糊匹配）
        ds_match = k in ds_rels
        if not ds_match:
            for dk in ds_rels:
                if fuzzy_match(k, dk):
                    ds_match = True
                    break
        if ds_match:
            validated.append(k)
    
    # 从原始模型数据中找到完整的关系对象（含位置信息）
    for k in validated:
        for name, data in models.items():
            for r in data[idx].get('relations', []):
                if rel_key(r) == k:
                    result[idx]['relations'].append(copy.deepcopy(r))
                    added_total += 1
                    break
            else:
                continue
            break

print(f"\n新增关系: {added_total} 条")

# 统计
from collections import Counter
rel_dist = Counter()
zero_rel = 0
for item in result:
    n = len(item.get('relations', []))
    if n == 0: zero_rel += 1
    for r in item.get('relations', []):
        rel_dist[r['label']] += 1

total = len(result)
print(f"总关系: {sum(rel_dist.values())} | 均值: {sum(rel_dist.values())/total:.3f} | 无关系: {zero_rel}({zero_rel/total*100:.1f}%)")
print(f"分布: {dict(sorted(rel_dist.items(), key=lambda x:-x[1]))}")
print(f"v17基线: 897条/均值2.24")

# 保存
with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(OUT_JSON, 'submit.json')

print(f"\n输出: {OUT_ZIP} ({os.path.getsize(OUT_ZIP)/1024:.1f} KB)")
