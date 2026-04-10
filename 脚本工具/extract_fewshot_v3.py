import json

with open('/home/ubuntu/official_mgbie/dataset/train.json') as f:
    train = json.load(f)

# 目标：覆盖 v3 漏标的 CROP-CON-VAR, GENE-LOI-TRT, MRK-LOI-TRT
# 以及给正确示范的 QTL-LOI-TRT, QTL-LOI-CHR, VAR-HAS-TRT, ABS-AFF-TRT, CROP-HAS-TRT
target_rels = {
    'CROP-CON-VAR', 'GENE-LOI-TRT', 'MRK-LOI-TRT',
    'QTL-LOI-TRT', 'QTL-LOI-CHR', 'VAR-HAS-TRT',
    'ABS-AFF-TRT', 'CROP-HAS-TRT'
}

# 为每条训练样本计算覆盖的关系类型
scored = []
for i, item in enumerate(train):
    rels = set()
    for r in item.get('relations', []):
        rels.add(f"{r['head_type']}-{r['label']}-{r['tail_type']}")
    coverage = len(rels & target_rels)
    if coverage >= 2 and len(item.get('entities', [])) >= 3:
        scored.append((coverage, len(rels), i, item))

scored.sort(key=lambda x: (-x[0], -x[1]))

# 贪心选择5条，最大化覆盖
selected = []
covered = set()
for cov, nrel, idx, item in scored:
    rels = set()
    for r in item.get('relations', []):
        rels.add(f"{r['head_type']}-{r['label']}-{r['tail_type']}")
    new_coverage = (rels & target_rels) - covered
    if new_coverage or len(selected) < 5:
        selected.append(item)
        covered |= (rels & target_rels)
        print(f"选中 train[{idx}]: 覆盖 {rels & target_rels}")
        if len(selected) == 5:
            break

print(f"\n总覆盖: {covered}")
print(f"未覆盖: {target_rels - covered}")

# 再加一条无关系的负样本（教模型输出空关系）
for i, item in enumerate(train):
    if len(item.get('relations', [])) == 0 and len(item.get('entities', [])) >= 2:
        selected.append(item)
        print(f"\n负样本: train[{i}] (无关系, {len(item['entities'])} 个实体)")
        break

with open('/home/ubuntu/bisai_clone/提示词库/fewshot_v3.json', 'w', encoding='utf-8') as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)
print(f"\n已保存 {len(selected)} 条到 fewshot_v3.json")
