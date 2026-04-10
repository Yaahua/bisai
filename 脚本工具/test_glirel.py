#!/usr/bin/env python3
"""测试 GLiREL 零样本关系抽取在 MGBIE 任务上的效果"""
import json
from gliner import GLiNER
from glirel import GLiREL

# 加载模型
print("加载 GLiNER 模型...")
gliner_model = GLiNER.from_pretrained('urchade/gliner_small-v2.1')
print("加载 GLiREL 模型...")
glirel_model = GLiREL.from_pretrained('jackboyla/glirel-large-v0')

# MGBIE 实体类型
ENTITY_LABELS = ['CROP', 'VAR', 'GENE', 'QTL', 'MRK', 'TRT', 'ABS', 'BIS', 'BM', 'CHR', 'CROSS', 'GST']

# MGBIE 关系类型（用自然语言描述）
RELATION_LABELS = {
    'AFF': 'affects or regulates biologically',
    'LOI': 'is located on or mapped to',
    'HAS': 'has or possesses trait',
    'CON': 'contains or includes variety',
    'USE': 'uses breeding method',
    'OCI': 'occurs at growth stage',
}

# 测试句子（来自训练集）
test_sentences = [
    "BTx623 sorghum showed enhanced drought tolerance compared to wild-type plants.",
    "The Dw3 gene was mapped to a region associated with plant height on chromosome 7.",
    "A QTL for grain yield was detected on chromosome 3H in barley using GWAS.",
    "The RIL population derived from a cross between Morex and Barke was used for QTL mapping.",
    "No significant associations were found between the markers and the traits.",
]

print("\n" + "="*60)
print("GLiREL 零样本关系抽取测试")
print("="*60)

for sent in test_sentences:
    print(f"\n句子: {sent}")
    
    # Step 1: GLiNER 识别实体
    entities = gliner_model.predict_entities(sent, ENTITY_LABELS, threshold=0.4)
    if not entities:
        print("  → 无实体识别结果")
        continue
    
    print("  实体:", [(e['text'], e['label'], f"{e['score']:.2f}") for e in entities])
    
    # Step 2: 构建 GLiREL 输入格式
    # GLiREL 需要实体的 start/end 位置
    entity_spans = []
    for e in entities:
        start = sent.find(e['text'])
        if start != -1:
            entity_spans.append({
                'start': start,
                'end': start + len(e['text']),
                'label': e['label'],
                'text': e['text']
            })
    
    if len(entity_spans) < 2:
        print("  → 实体数量不足，跳过关系抽取")
        continue
    
    # Step 3: GLiREL 预测关系
    try:
        # GLiREL 输入格式
        tokens = sent.split()
        # 重新计算 token 级别的 start/end
        relations = glirel_model.predict_relations(
            [sent],
            [list(RELATION_LABELS.values())],
            entity_spans=[entity_spans],
            threshold=0.3
        )
        print("  关系:", relations)
    except Exception as ex:
        print(f"  GLiREL 错误: {ex}")

print("\n测试完成！")
