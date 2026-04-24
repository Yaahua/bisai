#!/usr/bin/env python3
"""汇总所有 v41 候选版本的统计信息"""
import json
from pathlib import Path

ROOT = Path('/home/ubuntu/bisai/数据/A榜')

# 底座统计
base = json.load(open(ROOT / 'submit_v36_gene_abs.json'))
n = len(base)
base_rels = sum(len(x.get('relations', [])) for x in base)
base_no_rel = sum(1 for x in base if not x.get('relations'))
print(f"底座 (submit_v36_gene_abs): rels={base_rels}, avg={base_rels/n:.2f}, "
      f"no_rel={base_no_rel} ({base_no_rel/n*100:.1f}%)")
print()

# 列出所有 v41 版本
v41_files = sorted(ROOT.glob('submit_v41_*.json'))
print(f"v41 候选版本总数: {len(v41_files)}")
print()

results = []
for f in v41_files:
    data = json.load(open(f))
    total_rels = sum(len(x.get('relations', [])) for x in data)
    no_rel = sum(1 for x in data if not x.get('relations'))
    diff = total_rels - base_rels
    name = f.stem
    results.append({
        'name': name,
        'total_rels': total_rels,
        'rel_avg': total_rels / n,
        'no_rel': no_rel,
        'no_rel_pct': no_rel / n * 100,
        'diff': diff,
    })

# 按 diff 排序
results.sort(key=lambda x: x['diff'])

header = f"{'版本名':<52} {'总关系':>6} {'均值':>6} {'无关系':>8} {'差异':>6}"
print(header)
print("-" * 82)
for r in results:
    line = (f"{r['name']:<52} {r['total_rels']:>6} {r['rel_avg']:>6.2f} "
            f"{r['no_rel']:>4}({r['no_rel_pct']:>4.1f}%) {r['diff']:>+6}")
    print(line)

# 分类汇总
print("\n\n===== 分类汇总 =====")

print("\n--- 减法版本（删除假阳性）---")
for r in results:
    if 'sub_' in r['name'] and 'plus' not in r['name']:
        print(f"  {r['name']}: diff={r['diff']:+d}, rel_avg={r['rel_avg']:.2f}")

print("\n--- 纯加法版本（规则补充）---")
for r in results:
    if 'rule_' in r['name'] or 'precise_' in r['name']:
        if 'sub_' not in r['name']:
            print(f"  {r['name']}: diff={r['diff']:+d}, rel_avg={r['rel_avg']:.2f}")

print("\n--- 减法+加法组合版本 ---")
for r in results:
    if 'sub_' in r['name'] and 'plus' in r['name']:
        print(f"  {r['name']}: diff={r['diff']:+d}, rel_avg={r['rel_avg']:.2f}")
