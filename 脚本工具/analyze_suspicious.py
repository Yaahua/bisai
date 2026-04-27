#!/usr/bin/env python3
"""
analyze_suspicious.py — 分析底座中高假阳性风险的关系类型
重点：TRT-OCI-GST（超距38.7%）、MRK-LOI-TRT（超距31.8%）、GENE-CON-GENE（超距35.3%）、TRT-AFF-TRT（超距33.3%）
"""
import json
import re
import statistics
from collections import Counter, defaultdict

with open('/home/ubuntu/bisai/数据/官方原始数据/train.json') as f:
    train = json.load(f)
with open('/home/ubuntu/bisai/数据/A榜/submit_v41_sub_conservative.json') as f:
    base = json.load(f)

def get_between_text(text, h_start, h_end, t_start, t_end):
    if h_end <= t_start:
        return text[h_end:t_start].strip().lower()
    elif t_end <= h_start:
        return text[t_end:h_start].strip().lower()
    return ""

def triplet(r):
    return (r['head_type'], r['label'], r['tail_type'])

def rel_key(r):
    return (r['head'].strip().lower(), r['head_type'], r['label'],
            r['tail'].strip().lower(), r['tail_type'])

# 高假阳性风险类型（超距比例高）
focus_types = [
    ('TRT', 'OCI', 'GST'),   # 38.7%
    ('MRK', 'LOI', 'TRT'),   # 31.8%
    ('GENE', 'CON', 'GENE'),  # 35.3%
    ('TRT', 'AFF', 'TRT'),   # 33.3%
]

all_suspicious = []

for ft in focus_types:
    print(f"\n{'='*70}")
    print(f"=== {ft[0]}-{ft[1]}-{ft[2]} ===")
    
    # 训练集分析
    train_dists = []
    train_betweens = []
    train_between_words = Counter()
    for item in train:
        text = item.get('text', '')
        for r in item.get('relations', []):
            if triplet(r) == ft:
                between = get_between_text(text, r['head_start'], r['head_end'],
                                           r['tail_start'], r['tail_end'])
                dist = abs(r.get('head_start', 0) - r.get('tail_start', 0))
                train_dists.append(dist)
                train_betweens.append(between)
                words = re.findall(r'\b[a-z]{3,}\b', between)
                for w in words:
                    train_between_words[w] += 1
    
    if not train_dists:
        print("训练集中无此类型")
        continue
    
    p75 = sorted(train_dists)[int(len(train_dists)*0.75)]
    p90 = sorted(train_dists)[int(len(train_dists)*0.90)]
    print(f"训练集: {len(train_dists)}条, 中位距={statistics.median(train_dists):.0f}, P75={p75:.0f}, P90={p90:.0f}")
    top_words = train_between_words.most_common(15)
    print(f"训练集 between 词 Top15: {top_words}")
    
    # 底座分析
    base_rels = []
    for idx, item in enumerate(base):
        text = item.get('text', '')
        for r in item.get('relations', []):
            if triplet(r) == ft:
                between = get_between_text(text, r['head_start'], r['head_end'],
                                           r['tail_start'], r['tail_end'])
                dist = abs(r.get('head_start', 0) - r.get('tail_start', 0))
                base_rels.append((idx, r, between, dist))
    
    print(f"\n底座: {len(base_rels)}条")
    
    # 可疑关系：超过P75距离
    suspicious = [(idx, r, b, d) for idx, r, b, d in base_rels if d > p75]
    print(f"超过P75({p75:.0f})的可疑关系: {len(suspicious)}条")
    
    # 更可疑：between词不在训练集top词中
    top_word_set = {w for w, c in train_between_words.most_common(30)}
    
    for idx, r, b, d in suspicious:
        between_words = set(re.findall(r'\b[a-z]{3,}\b', b))
        overlap = between_words & top_word_set
        overlap_ratio = len(overlap) / max(len(between_words), 1)
        score = 0
        if d > p90:
            score += 2
        elif d > p75:
            score += 1
        if overlap_ratio < 0.3:
            score += 1
        
        all_suspicious.append({
            'idx': idx,
            'type': f"{ft[0]}-{ft[1]}-{ft[2]}",
            'head': r['head'],
            'tail': r['tail'],
            'between': b[:80],
            'dist': d,
            'overlap_ratio': overlap_ratio,
            'score': score,
            'rel': r,
        })
        
        if score >= 2:
            print(f"  ⚠️ score={score} [{r['head']}] → [{r['tail']}] | dist={d} | between='{b[:60]}'")
        else:
            print(f"     score={score} [{r['head']}] → [{r['tail']}] | dist={d} | between='{b[:60]}'")

print(f"\n{'='*70}")
print(f"汇总：共发现 {len(all_suspicious)} 个可疑关系")
high_risk = [s for s in all_suspicious if s['score'] >= 2]
print(f"高风险（score≥2）：{len(high_risk)} 个")
for s in sorted(high_risk, key=lambda x: x['score'], reverse=True):
    print(f"  [{s['type']}] score={s['score']} [{s['head']}] → [{s['tail']}] | dist={s['dist']} | between='{s['between'][:50]}'")
