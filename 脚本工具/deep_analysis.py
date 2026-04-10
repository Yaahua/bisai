#!/usr/bin/env python3
"""
深度分析官方原始 train.json，挖掘标注规律，为重构方案提供数据支撑。
"""
import json
from collections import Counter, defaultdict
import statistics

with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    data = json.load(f)

with open('/home/ubuntu/official_mgbie/dataset/test_A.json') as f:
    test_a = json.load(f)

print(f"训练集: {len(data)} 条 | A榜测试集: {len(test_a)} 条\n")

# ============================================================
# 1. 基础统计
# ============================================================
ent_counts = [len(d['entities']) for d in data]
rel_counts  = [len(d['relations']) for d in data]
text_lens   = [len(d['text']) for d in data]

print("===== 1. 基础统计 =====")
print(f"文本长度: 均值={statistics.mean(text_lens):.0f}, 中位={statistics.median(text_lens):.0f}, "
      f"最小={min(text_lens)}, 最大={max(text_lens)}")
print(f"实体数/条: 均值={statistics.mean(ent_counts):.2f}, 中位={statistics.median(ent_counts):.0f}, "
      f"最小={min(ent_counts)}, 最大={max(ent_counts)}")
print(f"关系数/条: 均值={statistics.mean(rel_counts):.2f}, 中位={statistics.median(rel_counts):.0f}, "
      f"最小={min(rel_counts)}, 最大={max(rel_counts)}")
zero_rel = sum(1 for d in data if len(d['relations']) == 0)
print(f"无关系的条目: {zero_rel} 条 ({zero_rel/len(data)*100:.1f}%)")

# ============================================================
# 2. 实体标签分布
# ============================================================
ent_label_cnt = Counter()
for d in data:
    for e in d['entities']:
        ent_label_cnt[e['label']] += 1

total_ents = sum(ent_label_cnt.values())
print(f"\n===== 2. 实体标签分布（共 {total_ents} 个实体）=====")
for lbl, cnt in ent_label_cnt.most_common():
    print(f"  {lbl:<8} {cnt:>5}  {cnt/total_ents*100:>5.1f}%")

# ============================================================
# 3. 关系标签分布 + 头尾类型组合
# ============================================================
rel_label_cnt = Counter()
rel_type_pairs = defaultdict(Counter)  # label -> Counter of (head_type, tail_type)

for d in data:
    for r in d['relations']:
        lbl = r['label']
        rel_label_cnt[lbl] += 1
        pair = f"{r['head_type']}→{r['tail_type']}"
        rel_type_pairs[lbl][pair] += 1

total_rels = sum(rel_label_cnt.values())
print(f"\n===== 3. 关系标签分布（共 {total_rels} 条关系）=====")
for lbl, cnt in rel_label_cnt.most_common():
    print(f"  {lbl:<8} {cnt:>5}  {cnt/total_rels*100:>5.1f}%")

print("\n===== 3b. 各关系类型的头尾实体类型 TOP 组合 =====")
for lbl in ['AFF', 'LOI', 'HAS', 'CON', 'OCI', 'USE']:
    print(f"\n  [{lbl}] 共 {rel_label_cnt[lbl]} 条:")
    for pair, cnt in rel_type_pairs[lbl].most_common(8):
        print(f"    {pair:<25} {cnt:>4}  ({cnt/rel_label_cnt[lbl]*100:.1f}%)")

# ============================================================
# 4. 每条样本的关系数分布
# ============================================================
rel_dist = Counter(rel_counts)
print("\n===== 4. 每条样本关系数分布 =====")
for k in sorted(rel_dist.keys()):
    print(f"  {k} 条关系: {rel_dist[k]} 个样本")

# ============================================================
# 5. 实体文本长度分布（词数）
# ============================================================
ent_word_lens = []
for d in data:
    for e in d['entities']:
        ent_word_lens.append(len(e['text'].split()))

print(f"\n===== 5. 实体文本词数分布 =====")
word_len_dist = Counter(ent_word_lens)
for k in sorted(word_len_dist.keys())[:10]:
    print(f"  {k} 词: {word_len_dist[k]} 个实体 ({word_len_dist[k]/len(ent_word_lens)*100:.1f}%)")

# ============================================================
# 6. 最高频实体文本（每类 top5）
# ============================================================
ent_text_by_label = defaultdict(Counter)
for d in data:
    for e in d['entities']:
        ent_text_by_label[e['label']][e['text']] += 1

print("\n===== 6. 各类实体最高频文本（top5）=====")
for lbl in sorted(ent_text_by_label.keys()):
    top5 = ent_text_by_label[lbl].most_common(5)
    print(f"  [{lbl}]: " + " | ".join(f"'{t}'×{c}" for t,c in top5))

# ============================================================
# 7. 关系中实体是否在当前句（跨句关系检测）
# ============================================================
# 用句号分割文本，检查 head 和 tail 是否在同一句
def get_sentence_idx(text, start):
    """返回 start 位置所在的句子索引（按 '. ' 分割）"""
    pos = 0
    for i, sent in enumerate(text.split('. ')):
        pos += len(sent) + 2
        if start < pos:
            return i
    return -1

cross_sent_rels = 0
same_sent_rels = 0
for d in data:
    text = d['text']
    for r in d['relations']:
        hi = get_sentence_idx(text, r['head_start'])
        ti = get_sentence_idx(text, r['tail_start'])
        if hi == ti:
            same_sent_rels += 1
        else:
            cross_sent_rels += 1

print(f"\n===== 7. 关系跨句分析 =====")
print(f"  同句关系: {same_sent_rels} ({same_sent_rels/total_rels*100:.1f}%)")
print(f"  跨句关系: {cross_sent_rels} ({cross_sent_rels/total_rels*100:.1f}%)")

# ============================================================
# 8. 官方评分权重分析：哪个类别对总分影响最大
# ============================================================
print("\n===== 8. 官方评分权重分析 =====")
print("  总分 = 0.4×Score_NER + 0.6×Score_RE")
print("  Score_X = 0.5×F1 + 0.25×P + 0.25×R  ≈ F1（F1权重最大）")
print()
print("  RE 权重(0.6) > NER 权重(0.4)，RE 是决定性因素")
print()
print("  RE 各类别对总分的贡献（按关系数量估算）:")
for lbl, cnt in rel_label_cnt.most_common():
    weight = cnt / total_rels
    contribution = weight * 0.6  # RE 占总分 60%
    print(f"    {lbl:<8} {cnt:>4}条 ({weight*100:.1f}%) → 对总分贡献上限约 {contribution:.3f}")

# ============================================================
# 9. A 榜测试集文本长度分析
# ============================================================
test_lens = [len(d['text']) for d in test_a]
print(f"\n===== 9. A 榜测试集文本长度 =====")
print(f"  均值={statistics.mean(test_lens):.0f}, 中位={statistics.median(test_lens):.0f}, "
      f"最小={min(test_lens)}, 最大={max(test_lens)}")
print(f"  训练集均值={statistics.mean(text_lens):.0f}（对比）")

# ============================================================
# 10. 关键发现：官方 LOI 关系中 tail 是 TRT 的比例
# ============================================================
loi_tail_trt = sum(1 for d in data for r in d['relations']
                   if r['label']=='LOI' and r['tail_type']=='TRT')
loi_total = rel_label_cnt['LOI']
print(f"\n===== 10. LOI 关系中 tail=TRT 的比例 =====")
print(f"  LOI(*, TRT): {loi_tail_trt} / {loi_total} = {loi_tail_trt/loi_total*100:.1f}%")
print(f"  → 官方确实大量使用 LOI(QTL/GENE/MRK, TRT)，这是官方标准，不是错误！")

# ============================================================
# 11. 官方 AFF 关系头尾类型分析
# ============================================================
print(f"\n===== 11. 官方 AFF 关系头尾类型（完整）=====")
aff_total = rel_label_cnt['AFF']
for pair, cnt in rel_type_pairs['AFF'].most_common():
    print(f"  {pair:<25} {cnt:>4}  ({cnt/aff_total*100:.1f}%)")
