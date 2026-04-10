#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 图1：官方标注规律总览（4宫格）
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('Official Train.json Annotation Patterns\n(1000 samples, Ground Truth)', fontsize=14, fontweight='bold')

# --- 左上：实体标签分布 ---
ent_labels = ['TRT', 'GENE', 'CROP', 'VAR', 'ABS', 'QTL', 'BM', 'MRK', 'CHR', 'CROSS', 'GST', 'BIS']
ent_counts = [1415, 994, 717, 638, 522, 469, 311, 298, 237, 114, 100, 98]
colors_ent = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c',
              '#e67e22','#34495e','#95a5a6','#d35400','#27ae60','#8e44ad']
bars = axes[0,0].barh(ent_labels[::-1], ent_counts[::-1], color=colors_ent[::-1], alpha=0.85)
axes[0,0].set_xlabel('Count', fontsize=10)
axes[0,0].set_title('Entity Label Distribution (5,913 total)', fontsize=11, fontweight='bold')
for bar, cnt in zip(bars, ent_counts[::-1]):
    axes[0,0].text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                   f'{cnt} ({cnt/5913*100:.1f}%)', va='center', fontsize=8)
axes[0,0].set_xlim(0, 1700)

# --- 右上：关系标签分布 ---
rel_labels = ['AFF', 'LOI', 'HAS', 'CON', 'OCI', 'USE']
rel_counts_v = [845, 714, 542, 514, 96, 91]
rel_colors = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#e67e22']
bars2 = axes[0,1].bar(rel_labels, rel_counts_v, color=rel_colors, alpha=0.85, width=0.6)
axes[0,1].set_ylabel('Count', fontsize=10)
axes[0,1].set_title('Relation Label Distribution (2,802 total)\n[RE weight=0.6 → most important!]',
                     fontsize=11, fontweight='bold')
for bar, cnt in zip(bars2, rel_counts_v):
    axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                   f'{cnt}\n({cnt/2802*100:.1f}%)', ha='center', va='bottom', fontsize=9)
axes[0,1].set_ylim(0, 1000)

# --- 左下：每条样本关系数分布 ---
rel_dist_k = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,24,28]
rel_dist_v = [327,113,157,88,90,70,46,25,24,11,12,9,7,6,2,1,2,2,2,1,1,2,1,1]
axes[1,0].bar(rel_dist_k, rel_dist_v, color='#3498db', alpha=0.8)
axes[1,0].set_xlabel('Relations per Sample', fontsize=10)
axes[1,0].set_ylabel('Sample Count', fontsize=10)
axes[1,0].set_title(f'Relations per Sample Distribution\n(32.7% samples have 0 relations!)', fontsize=11, fontweight='bold')
axes[1,0].axvline(x=0, color='red', linestyle='--', alpha=0.5)
axes[1,0].text(0.5, 310, '327 samples\n(32.7%)\nhave 0 rels', ha='left', fontsize=8, color='red')

# --- 右下：关键关系类型头尾组合（TOP 组合热力图风格）---
# 用堆叠条形图展示 AFF 和 LOI 的头尾类型分布
aff_pairs = ['ABS→TRT', 'GENE→TRT', 'ABS→GENE', 'TRT→TRT', 'BM→TRT', 'Others']
aff_vals  = [285, 177, 91, 48, 33, 211]
loi_pairs = ['QTL→TRT', 'QTL→CHR', 'GENE→TRT', 'MRK→TRT', 'MRK→CHR', 'Others']
loi_vals  = [224, 141, 85, 67, 46, 151]

x = np.arange(2)
width = 0.35
bottom_aff = 0
bottom_loi = 0
pair_colors = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#bdc3c7']

for i, (av, lv, label) in enumerate(zip(aff_vals, loi_vals, aff_pairs)):
    axes[1,1].bar(0, av, width, bottom=bottom_aff, color=pair_colors[i], alpha=0.85,
                  label=f'AFF: {aff_pairs[i]}')
    axes[1,1].bar(1, lv, width, bottom=bottom_loi, color=pair_colors[i], alpha=0.85)
    bottom_aff += av
    bottom_loi += lv

axes[1,1].set_xticks([0, 1])
axes[1,1].set_xticklabels(['AFF (845 total)', 'LOI (714 total)'], fontsize=10)
axes[1,1].set_ylabel('Count', fontsize=10)
axes[1,1].set_title('AFF & LOI Head→Tail Type Breakdown\n(These 2 relations = 55.7% of all relations)',
                     fontsize=11, fontweight='bold')

# 手动图例
legend_patches = [mpatches.Patch(color=pair_colors[i], label=f'{aff_pairs[i]} / {loi_pairs[i]}')
                  for i in range(6)]
axes[1,1].legend(handles=legend_patches, fontsize=7, loc='upper right')

plt.tight_layout()
plt.savefig('/home/ubuntu/official_patterns.png', dpi=150, bbox_inches='tight')
plt.close()
print("官方标注规律图已保存")

# ============================================================
# 图2：评分权重分解图（决策树式）
# ============================================================
fig, ax = plt.subplots(figsize=(14, 7))
ax.set_xlim(0, 14)
ax.set_ylim(0, 7)
ax.axis('off')
ax.set_title('Score Decomposition & Where to Focus', fontsize=14, fontweight='bold', pad=20)

def box(ax, x, y, w, h, text, color, fontsize=10, bold=False):
    rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='#2c3e50', linewidth=1.5, zorder=2)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize,
            fontweight=weight, zorder=3, wrap=True)

def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=1.5))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.05, my, label, fontsize=9, color='#e74c3c', fontweight='bold')

# 总分
box(ax, 5.5, 5.8, 3, 0.8, 'Total Score\n= 0.4×NER + 0.6×RE', '#2c3e50', fontsize=10, bold=True)
ax.texts[-1].set_color('white')

# NER / RE
box(ax, 1.5, 4.0, 3.5, 1.0, 'Score_NER\n(Weight: 40%)\nF1=0.792 (current)', '#3498db', fontsize=9)
box(ax, 9.0, 4.0, 3.5, 1.0, 'Score_RE\n(Weight: 60%) ★\nF1=0.483 (current)', '#e74c3c', fontsize=9)
ax.texts[-1].set_color('white')
ax.texts[-2].set_color('white')

arrow(ax, 7.0, 6.2, 3.25, 5.0, '×0.4')
arrow(ax, 7.0, 6.2, 10.75, 5.0, '×0.6')

# NER 子项
box(ax, 0.2, 2.2, 1.5, 1.0, 'BM\nF1=0.617\n(weak)', '#e67e22', fontsize=8)
box(ax, 1.9, 2.2, 1.5, 1.0, 'TRT\nF1=0.742\n(medium)', '#f39c12', fontsize=8)
box(ax, 3.6, 2.2, 1.5, 1.0, 'Others\nF1>0.78\n(good)', '#27ae60', fontsize=8)

arrow(ax, 3.25, 4.0, 0.95, 3.2)
arrow(ax, 3.25, 4.0, 2.65, 3.2)
arrow(ax, 3.25, 4.0, 4.35, 3.2)

# RE 子项
box(ax, 7.5, 2.2, 1.5, 1.0, 'AFF\nF1=0.439\n★ Fix!', '#c0392b', fontsize=8, bold=True)
box(ax, 9.2, 2.2, 1.5, 1.0, 'LOI\nF1=0.358\n★ Fix!', '#c0392b', fontsize=8, bold=True)
box(ax, 10.9, 2.2, 1.5, 1.0, 'HAS\nF1=0.646\n(ok)', '#f39c12', fontsize=8)
box(ax, 12.3, 2.2, 1.2, 1.0, 'CON\nF1=0.553', '#f39c12', fontsize=8)

arrow(ax, 10.75, 4.0, 8.25, 3.2)
arrow(ax, 10.75, 4.0, 9.95, 3.2)
arrow(ax, 10.75, 4.0, 11.65, 3.2)
arrow(ax, 10.75, 4.0, 12.9, 3.2)

# 根因分析
box(ax, 7.0, 0.3, 2.2, 1.5,
    'AFF Root Cause:\nAI added 211 FP\n(GENE→TRT, ABS→TRT)\nbut official has fewer',
    '#fadbd8', fontsize=7.5)
box(ax, 9.4, 0.3, 2.2, 1.5,
    'LOI Root Cause:\nAI deleted official\nLOI(QTL→TRT) patterns\n(53% of LOI is →TRT!)',
    '#fadbd8', fontsize=7.5)

arrow(ax, 8.25, 2.2, 8.1, 1.8)
arrow(ax, 9.95, 2.2, 10.5, 1.8)

plt.tight_layout()
plt.savefig('/home/ubuntu/score_decomposition.png', dpi=150, bbox_inches='tight')
plt.close()
print("评分权重分解图已保存")
