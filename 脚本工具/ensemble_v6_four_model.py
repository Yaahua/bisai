#!/usr/bin/env python3
"""
四模型集成脚本 ensemble_v6_four_model.py
=========================================
将 v7 / v9 / v10(Gemini) / v23(GLM-4.7) 四个模型的预测结果进行集成投票

支持两种策略：
  - MIN_VOTES=2 (四选二)：召回率更高，适合 GLM 质量较好时
  - MIN_VOTES=3 (四选三)：精确率更高，适合 GLM 质量一般时

使用方法：
  # 四选二（推荐先试）
  python3.11 ensemble_v6_four_model.py --votes 2

  # 四选三
  python3.11 ensemble_v6_four_model.py --votes 3

  # 先评估 GLM 单体质量（只统计，不生成提交文件）
  python3.11 ensemble_v6_four_model.py --eval-only

输出：
  /home/ubuntu/bisai/数据/A榜/submit_v24_ensemble_v6_votes{N}.json
  /home/ubuntu/bisai/数据/A榜/submit_v24_ensemble_v6_votes{N}.zip

依赖：
  - submit_v7_cicl_v2.json      (v7 预测结果)
  - submit_v9_targeted.json     (v9 预测结果)
  - submit_v10_gemini.json      (v10 Gemini 预测结果)
  - submit_v23_glm47.json       (v23 GLM-4.7 预测结果，需先运行 predict_v23_glm47.py)
"""
import json
import os
import re
import zipfile
import argparse
from collections import defaultdict, Counter

# ===== 路径配置 =====
DATA_DIR = '/home/ubuntu/bisai/数据/A榜'
MODEL_FILES = {
    'v7':  os.path.join(DATA_DIR, 'submit_v7_cicl_v2.json'),
    'v9':  os.path.join(DATA_DIR, 'submit_v9_targeted.json'),
    'v10': os.path.join(DATA_DIR, 'submit_v10_gemini.json'),
    'v23': os.path.join(DATA_DIR, 'submit_v23_glm47.json'),
}
V17_PATH = os.path.join(DATA_DIR, 'submit_v17_whitelist.json')

# ===== 参数解析 =====
parser = argparse.ArgumentParser()
parser.add_argument('--votes', type=int, default=2, choices=[2, 3],
                    help='最小投票数：2=四选二，3=四选三（默认2）')
parser.add_argument('--eval-only', action='store_true',
                    help='仅评估各模型质量，不生成提交文件')
parser.add_argument('--with-whitelist', action='store_true',
                    help='在集成结果上叠加 v17 白名单后处理')
args = parser.parse_args()

MIN_VOTES = args.votes

# ===== 加载模型预测 =====
print("加载模型预测文件...")
models = {}
for name, path in MODEL_FILES.items():
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            models[name] = json.load(f)
        print(f"  ✓ {name}: {path} ({len(models[name])} 条)")
    else:
        print(f"  ✗ {name}: 文件不存在 — {path}")

if len(models) < 3:
    print("错误：至少需要 3 个模型文件才能运行集成")
    exit(1)

available_models = list(models.keys())
n_docs = len(models[available_models[0]])
print(f"\n可用模型: {available_models} | 文档数: {n_docs} | 最小投票数: {MIN_VOTES}")

# ===== 评估各模型单体质量 =====
print("\n===== 各模型单体统计 =====")
for name, data in models.items():
    total_rel = sum(len(d.get('relations', [])) for d in data)
    no_rel    = sum(1 for d in data if not d.get('relations'))
    n = len(data)
    label_cnt = Counter()
    for d in data:
        for r in d.get('relations', []):
            label_cnt[r['label']] += 1
    print(f"{name}: 关系均值={total_rel/n:.2f} | 无关系={no_rel/n*100:.1f}% | "
          f"AFF={label_cnt['AFF']} HAS={label_cnt['HAS']} LOI={label_cnt['LOI']} "
          f"CON={label_cnt['CON']} OCI={label_cnt['OCI']} USE={label_cnt['USE']}")

if args.eval_only:
    print("\n--eval-only 模式，退出。")
    exit(0)

# ===== 语义加权投票集成 =====
def normalize_entity(text: str) -> str:
    """标准化实体文本，用于模糊匹配"""
    return text.lower().strip()

def rel_key_strict(r: dict) -> tuple:
    """严格匹配键（完全字符串匹配）"""
    return (
        normalize_entity(r['head']),
        r['head_type'],
        r['label'],
        normalize_entity(r['tail']),
        r['tail_type']
    )

def rel_key_fuzzy(r: dict) -> tuple:
    """模糊匹配键（忽略实体边界差异）
    策略：取实体文本的前 N 个词作为键，避免 'drought stress' vs 'drought' 的差异
    """
    def head_words(text, n=3):
        words = normalize_entity(text).split()
        return ' '.join(words[:n])
    return (
        head_words(r['head']),
        r['head_type'],
        r['label'],
        head_words(r['tail']),
        r['tail_type']
    )

print(f"\n===== 开始四模型集成（MIN_VOTES={MIN_VOTES}）=====")

output = []
stats = {
    'strict_pass': 0,   # 严格匹配通过
    'fuzzy_pass':  0,   # 模糊匹配通过（语义加权）
    'total_pass':  0,
    'total_reject': 0,
    'per_label': Counter(),
}

for doc_idx in range(n_docs):
    # 收集所有模型对该文档的预测
    all_rels_by_model = {}
    for name in available_models:
        if doc_idx < len(models[name]):
            all_rels_by_model[name] = models[name][doc_idx].get('relations', [])
        else:
            all_rels_by_model[name] = []

    # 第一步：严格匹配投票
    strict_votes = defaultdict(list)  # key -> [(model, rel), ...]
    for name, rels in all_rels_by_model.items():
        for r in rels:
            k = rel_key_strict(r)
            strict_votes[k].append((name, r))

    # 第二步：模糊匹配（对严格匹配不足票数的关系进行二次聚合）
    fuzzy_votes = defaultdict(list)
    for name, rels in all_rels_by_model.items():
        for r in rels:
            fk = rel_key_fuzzy(r)
            fuzzy_votes[fk].append((name, r))

    # 第三步：决策
    accepted_strict_keys = set()
    doc_relations = []

    # 优先处理严格匹配
    for k, voters in strict_votes.items():
        unique_models = set(m for m, _ in voters)
        if len(unique_models) >= MIN_VOTES:
            # 选择信息最完整的那个关系（实体文本最长的）
            best_rel = max((r for _, r in voters), key=lambda r: len(r['head']) + len(r['tail']))
            doc_relations.append(best_rel)
            accepted_strict_keys.add(k)
            stats['strict_pass'] += 1

    # 模糊匹配补充（仅当严格匹配未通过时）
    accepted_fuzzy_keys = set()
    for fk, voters in fuzzy_votes.items():
        unique_models = set(m for m, _ in voters)
        if len(unique_models) >= MIN_VOTES:
            # 检查是否已被严格匹配覆盖
            already_covered = any(
                rel_key_strict(r) in accepted_strict_keys
                for _, r in voters
            )
            if not already_covered and fk not in accepted_fuzzy_keys:
                # 选择信息最完整的关系
                best_rel = max((r for _, r in voters), key=lambda r: len(r['head']) + len(r['tail']))
                doc_relations.append(best_rel)
                accepted_fuzzy_keys.add(fk)
                stats['fuzzy_pass'] += 1

    # 去重（防止同一关系被严格+模糊各加一次）
    seen_keys = set()
    deduped_rels = []
    for r in doc_relations:
        k = rel_key_strict(r)
        if k not in seen_keys:
            seen_keys.add(k)
            deduped_rels.append(r)
            stats['per_label'][r['label']] += 1

    # 获取文本（用第一个可用模型的）
    text = models[available_models[0]][doc_idx]['text'] if doc_idx < len(models[available_models[0]]) else ""

    output.append({
        "text": text,
        "entities": [],   # 集成阶段不合并实体（各模型实体差异大）
        "relations": deduped_rels
    })

stats['total_pass'] = stats['strict_pass'] + stats['fuzzy_pass']

# ===== 叠加 v17 白名单（可选）=====
if args.with_whitelist and os.path.exists(V17_PATH):
    print("\n叠加 v17 白名单后处理...")
    v17 = json.load(open(V17_PATH))
    added = 0
    for i, (out_item, v17_item) in enumerate(zip(output, v17)):
        existing_keys = {rel_key_strict(r) for r in out_item['relations']}
        for r in v17_item.get('relations', []):
            k = rel_key_strict(r)
            if k not in existing_keys:
                out_item['relations'].append(r)
                existing_keys.add(k)
                added += 1
    print(f"白名单新增: {added} 条")

# ===== 统计 =====
total_rel = sum(len(d['relations']) for d in output)
no_rel    = sum(1 for d in output if not d['relations'])
n = len(output)
print(f"\n===== 集成结果统计 =====")
print(f"严格匹配通过: {stats['strict_pass']} 条")
print(f"模糊匹配补充: {stats['fuzzy_pass']} 条")
print(f"总关系数: {total_rel} | 关系均值: {total_rel/n:.2f} | 无关系比: {no_rel/n*100:.1f}%")
print(f"各类型: {dict(stats['per_label'].most_common())}")
print(f"\n参考: v17=0.4224 (均值2.24/897条) | 训练集期望均值=2.80")

# ===== 保存 =====
suffix = f"votes{MIN_VOTES}"
if args.with_whitelist:
    suffix += "_wl"
out_json = os.path.join(DATA_DIR, f'submit_v24_ensemble_v6_{suffix}.json')
out_zip  = os.path.join(DATA_DIR, f'submit_v24_ensemble_v6_{suffix}.zip')

with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(out_json, 'submit.json')

print(f"\n输出 JSON: {out_json}")
print(f"输出 ZIP:  {out_zip} ({os.path.getsize(out_zip)/1024:.1f} KB)")
print("\n提交建议：")
print(f"  先提交 votes=2 版本，观察分数变化")
print(f"  若 GLM 质量高（单体均值>2.5），再试 votes=3 版本")
