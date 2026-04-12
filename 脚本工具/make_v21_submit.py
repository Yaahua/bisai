#!/usr/bin/env python3
"""
make_v21_submit.py
==================
将 GLM NLI 验证通过的关系追加到 v17_whitelist，生成 v21 提交文件
"""
import json, copy, zipfile, os
from collections import Counter

CACHE_PATH  = '/home/ubuntu/bisai/数据/v21_nli_cache.json'
BASE_PATH   = '/home/ubuntu/bisai/数据/A榜/submit_v17_whitelist.json'
OUTPUT_JSON = '/home/ubuntu/bisai/数据/A榜/submit_v21_nli_v17.json'
OUTPUT_ZIP  = '/home/ubuntu/bisai/数据/A榜/submit_v21_nli_v17.zip'
MIN_CONF    = 0.75

cache     = json.load(open(CACHE_PATH, encoding='utf-8'))
base_data = json.load(open(BASE_PATH,  encoding='utf-8'))
output    = copy.deepcopy(base_data)

def rel_key(r):
    return (r['head'].lower().strip(), r['head_type'], r['label'], r['tail'].lower().strip(), r['tail_type'])

# 追加通过验证的关系
added = 0
skipped_dup = 0
approved = [v for v in cache.values() if v['verdict'] == 'TRUE' and v.get('confidence', 0) >= MIN_CONF]

for item in approved:
    doc_idx = item['doc_idx']
    if doc_idx >= len(output):
        continue
    existing = {rel_key(r) for r in output[doc_idx].get('relations', [])}
    k = rel_key(item['relation'])
    if k not in existing:
        # 清理多余字段
        rel = {kk: vv for kk, vv in item['relation'].items() if kk in ['head', 'head_type', 'label', 'tail', 'tail_type']}
        output[doc_idx]['relations'].append(rel)
        added += 1
    else:
        skipped_dup += 1

# 统计
total_rel = sum(len(d.get('relations', [])) for d in output)
no_rel    = sum(1 for d in output if not d.get('relations'))
label_cnt = Counter()
for d in output:
    for r in d.get('relations', []):
        label_cnt[r['label']] += 1

print(f'=== v21 生成完成 ===')
print(f'新增关系: {added} 条（跳过重复: {skipped_dup} 条）')
print(f'关系均值: {total_rel/len(output):.2f}（v17 基线: 2.24）')
print(f'无关系比: {no_rel/len(output)*100:.1f}%（v17 基线: 35.8%）')
print(f'总关系数: {total_rel}（v17 基线: 897）')
print(f'关系分布: {dict(label_cnt.most_common())}')

# 保存 JSON
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# 打包 ZIP
with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(OUTPUT_JSON, 'submit.json')

print(f'\n输出 JSON: {OUTPUT_JSON}')
print(f'输出 ZIP:  {OUTPUT_ZIP} ({os.path.getsize(OUTPUT_ZIP)/1024:.1f} KB)')
