"""
v4 后处理脚本：在 v3 基础上精准砍掉三种最严重的过标模式
策略：
1. QTL-LOI-TRT：实体间距 > 80 字符且无定位关键词 → 删除
2. GENE-AFF-TRT：无因果动词 → 删除
3. CROP-HAS-TRT：实体间距 > 100 字符 → 删除
4. ABS-AFF-GENE：无因果动词 → 删除（训练集期望36，预测74，过标2x）
5. VAR-CON-CROP：训练集中不存在此方向（只有CROP-CON-VAR），全删
6. GENE-CON-CROP：训练集中不存在，全删
"""
import json
import re

# ===== 关键词库 =====
LOI_KEYWORDS = [
    'map', 'mapped', 'locat', 'link', 'associ', 'detect', 'identif',
    'found', 'position', 'anchor', 'flank', 'interval', 'region',
    'locus', 'loci', 'qtl', 'marker', 'snp', 'ssr', 'kasp', 'indel',
    'chromosome', 'chr', 'explain', 'account', 'contribut'
]

AFF_KEYWORDS = [
    'regulat', 'control', 'affect', 'influenc', 'increas', 'decreas',
    'promot', 'inhibit', 'enhanc', 'reduc', 'improv', 'determin',
    'contribut', 'associat', 'caus', 'lead', 'result', 'induc',
    'suppress', 'activat', 'express', 'encod', 'function', 'play',
    'significant', 'effect', 'impact', 'modif', 'alter', 'chang'
]

# 训练集中完全不存在的非法三元组（全删）
ILLEGAL_TRIPLETS = {
    ('VAR', 'CON', 'CROP'),   # 训练集只有 CROP-CON-VAR，不存在反向
    ('GENE', 'CON', 'CROP'),  # 训练集不存在
    ('CROSS', 'CON', 'CROP'), # 训练集期望只有2，但预测了18个，过标9x
    ('MRK', 'AFF', 'TRT'),    # 训练集期望1，预测21，过标21x
    ('GENE', 'AFF', 'ABS'),   # 训练集期望6，预测18，过标3x，且语义上ABS影响GENE而非反向
}

def get_char_distance(text, start1, end1, start2, end2):
    """计算两个实体在文本中的最近字符距离"""
    if end1 <= start2:
        return start2 - end1  # entity1 在 entity2 左边
    elif end2 <= start1:
        return start1 - end2  # entity2 在 entity1 左边
    else:
        return 0  # 重叠

def get_between_text(text, start1, end1, start2, end2):
    """获取两个实体之间的文本"""
    left_end = min(end1, end2)
    right_start = max(start1, start2)
    if left_end < right_start:
        return text[left_end:right_start].lower()
    return ""

def has_keyword(text_between, keywords):
    """检查两实体之间的文本是否包含关键词"""
    for kw in keywords:
        if kw in text_between:
            return True
    return False

def should_keep_relation(text, rel):
    """判断一个关系是否应该保留"""
    head_type = rel['head_type']
    tail_type = rel['tail_type']
    label = rel['label']
    head_start = rel['head_start']
    head_end = rel['head_end']
    tail_start = rel['tail_start']
    tail_end = rel['tail_end']
    
    triplet = (head_type, label, tail_type)
    
    # 规则0：完全非法的三元组直接删除
    if triplet in ILLEGAL_TRIPLETS:
        return False, "非法三元组"
    
    # 获取两实体之间的文本和距离
    dist = get_char_distance(text, head_start, head_end, tail_start, tail_end)
    between = get_between_text(text, head_start, head_end, tail_start, tail_end)
    
    # 规则1：QTL-LOI-TRT 距离限制（放宽，大部分是合法的）
    # 只删除距离超过200且无任何关联词的极端情况
    if triplet == ('QTL', 'LOI', 'TRT'):
        if dist > 200 and not has_keyword(between, LOI_KEYWORDS):
            return False, f"QTL-LOI-TRT 距离{dist}>200且无定位词"
    
    # 规则2：GENE-AFF-TRT 关键词验证 + 距离限制
    if triplet == ('GENE', 'AFF', 'TRT'):
        # 扩大搜索范围：取实体前后各80字符的上下文
        context_start = max(0, min(head_start, tail_start) - 80)
        context_end = min(len(text), max(head_end, tail_end) + 80)
        context = text[context_start:context_end].lower()
        # 无因果动词直接删
        if not has_keyword(context, AFF_KEYWORDS):
            return False, "GENE-AFF-TRT 无因果动词"
        # 有因果动词但距离超过150，需要更强的词（regul/control/encod）
        STRONG_AFF = ['regulat', 'control', 'encod', 'promot', 'inhibit', 'suppress', 'activat']
        if dist > 150 and not has_keyword(context, STRONG_AFF):
            return False, f"GENE-AFF-TRT 距离{dist}>150且无强因果词"
    
    # 规则3：CROP-HAS-TRT 距离限制（超远的不可能有直接关系）
    if triplet == ('CROP', 'HAS', 'TRT'):
        if dist > 120:
            return False, f"CROP-HAS-TRT 距离{dist}>120"
    
    # 规则4：ABS-AFF-GENE 关键词验证
    if triplet == ('ABS', 'AFF', 'GENE'):
        context_start = max(0, min(head_start, tail_start) - 30)
        context_end = min(len(text), max(head_end, tail_end) + 30)
        context = text[context_start:context_end].lower()
        if not has_keyword(context, AFF_KEYWORDS):
            return False, "ABS-AFF-GENE 无因果动词"
    
    # 规则5：TRT-OCI-GST 距离限制（训练集期望17，预测38，过标2.2x）
    if triplet == ('TRT', 'OCI', 'GST'):
        if dist > 100:
            return False, f"TRT-OCI-GST 距离{dist}>100"
    
    # 规则6：BM-AFF-TRT 关键词验证（训练集期望13，预测25）
    if triplet == ('BM', 'AFF', 'TRT'):
        context_start = max(0, min(head_start, tail_start) - 30)
        context_end = min(len(text), max(head_end, tail_end) + 30)
        context = text[context_start:context_end].lower()
        if not has_keyword(context, AFF_KEYWORDS):
            return False, "BM-AFF-TRT 无因果动词"
    
    return True, "保留"

def process_v4(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)
    
    stats = {
        'total_rel_before': 0,
        'total_rel_after': 0,
        'removed': 0,
        'removed_by_rule': {}
    }
    
    result = []
    for item in data:
        text = item['text']
        new_relations = []
        
        for rel in item['relations']:
            stats['total_rel_before'] += 1
            keep, reason = should_keep_relation(text, rel)
            if keep:
                new_relations.append(rel)
                stats['total_rel_after'] += 1
            else:
                stats['removed'] += 1
                stats['removed_by_rule'][reason] = stats['removed_by_rule'].get(reason, 0) + 1
        
        result.append({
            'text': item['text'],
            'entities': item['entities'],
            'relations': new_relations
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"=== v4 后处理完成 ===")
    print(f"处理前关系数: {stats['total_rel_before']}")
    print(f"处理后关系数: {stats['total_rel_after']}")
    print(f"删除关系数: {stats['removed']} ({stats['removed']/stats['total_rel_before']*100:.1f}%)")
    print(f"\n各规则删除统计:")
    for rule, count in sorted(stats['removed_by_rule'].items(), key=lambda x: -x[1]):
        print(f"  {rule}: {count}")
    
    # 验证关系分布
    from collections import Counter
    pred_triplets = Counter(f"{r['head_type']}-{r['label']}-{r['tail_type']}" for item in result for r in item['relations'])
    print(f"\n=== v4 关键三元组分布 ===")
    key_triplets = ['QTL-LOI-TRT', 'GENE-AFF-TRT', 'CROP-HAS-TRT', 'ABS-AFF-TRT', 
                    'VAR-HAS-TRT', 'QTL-LOI-CHR', 'GENE-LOI-TRT', 'CROP-CON-VAR']
    expected = {'QTL-LOI-TRT': 89, 'GENE-AFF-TRT': 70, 'CROP-HAS-TRT': 66, 
                'ABS-AFF-TRT': 113, 'VAR-HAS-TRT': 131, 'QTL-LOI-CHR': 56,
                'GENE-LOI-TRT': 34, 'CROP-CON-VAR': 88}
    for t in key_triplets:
        n = pred_triplets.get(t, 0)
        exp = expected.get(t, 0)
        ratio = n/exp if exp > 0 else 0
        flag = "<<过标" if ratio > 1.3 else (">>漏标" if ratio < 0.7 else "  正常")
        print(f"  {t:<25} 预测:{n:>4} 期望:{exp:>4} 比率:{ratio:.2f} {flag}")
    
    total_rel = sum(len(item['relations']) for item in result)
    total_ent = sum(len(item['entities']) for item in result)
    print(f"\n总实体数: {total_ent}")
    print(f"总关系数: {total_rel}")
    print(f"期望关系数: 1120")
    print(f"接近程度: {total_rel/1120:.2f}x")

if __name__ == '__main__':
    process_v4(
        '/home/ubuntu/bisai_clone/数据/A榜/submit_v3.json',
        '/home/ubuntu/submit_v4.json'
    )
