#!/usr/bin/env python3
"""
提交文件验证脚本
用法: python3 validate_submission.py <submit.json路径>
"""
import json, sys, os

def validate(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    
    errors = []
    warnings = []
    
    for i, item in enumerate(data):
        text = item.get('text', '')
        
        # 检查必要字段
        if 'entities' not in item:
            errors.append(f"[{i}] 缺少 entities 字段")
        if 'relations' not in item:
            errors.append(f"[{i}] 缺少 relations 字段")
        
        # 检查实体边界
        for e in item.get('entities', []):
            if not isinstance(e.get('start'), int) or not isinstance(e.get('end'), int):
                errors.append(f"[{i}] 实体 start/end 不是整数: {e}")
                continue
            if text[e['start']:e['end']] != e.get('text', ''):
                errors.append(f"[{i}] 实体边界不匹配: text[{e['start']}:{e['end']}]={repr(text[e['start']:e['end']])} != {repr(e.get('text',''))}")
            valid_labels = {'CROP','VAR','GENE','QTL','MRK','TRT','ABS','BIS','BM','CHR','CROSS','GST'}
            if e.get('label') not in valid_labels:
                errors.append(f"[{i}] 非法实体类型: {e.get('label')}")
        
        # 检查关系锚点
        for r in item.get('relations', []):
            required = ['head','head_start','head_end','head_type','tail','tail_start','tail_end','tail_type','label']
            for k in required:
                if k not in r:
                    errors.append(f"[{i}] 关系缺少字段 {k}: {r}")
                    break
            else:
                if text[r['head_start']:r['head_end']] != r['head']:
                    errors.append(f"[{i}] 关系head边界错误: {r['head']}")
                if text[r['tail_start']:r['tail_end']] != r['tail']:
                    errors.append(f"[{i}] 关系tail边界错误: {r['tail']}")
                valid_rels = {'AFF','LOI','HAS','CON','USE','OCI'}
                if r.get('label') not in valid_rels:
                    errors.append(f"[{i}] 非法关系类型: {r.get('label')}")
        
        # 警告：空标注
        if len(item.get('entities', [])) == 0:
            warnings.append(f"[{i}] 无实体（可能正常，约0.9%样本无实体）")
    
    print(f"===== 验证结果 =====")
    print(f"总条数: {len(data)}")
    print(f"错误数: {len(errors)}")
    print(f"警告数: {len(warnings)}")
    
    if errors:
        print(f"\n前20条错误:")
        for e in errors[:20]:
            print(f"  ✗ {e}")
    else:
        print(f"\n✓ 所有边界和格式验证通过！")
    
    if warnings[:5]:
        print(f"\n前5条警告（可忽略）:")
        for w in warnings[:5]:
            print(f"  ⚠ {w}")
    
    return len(errors) == 0

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '/home/ubuntu/bisai_clone/数据/A榜/submit.json'
    ok = validate(path)
    sys.exit(0 if ok else 1)
