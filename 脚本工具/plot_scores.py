#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 设置中文字体
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 图1：总体得分概览（横向条形图）
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('CCL2026-MGBIE Score Analysis\n(Your Corrected Data vs Official Gold, 286 matched samples)',
             fontsize=13, fontweight='bold')

# 左图：NER 和 RE 指标对比
categories = ['Precision', 'Recall', 'F1', 'Score']
ner_vals = [0.7462, 0.8445, 0.7923, 0.7938]
re_vals  = [0.4699, 0.4968, 0.4830, 0.4832]

x = np.arange(len(categories))
width = 0.35

bars1 = axes[0].bar(x - width/2, ner_vals, width, label='NER', color='#4C72B0', alpha=0.85)
bars2 = axes[0].bar(x + width/2, re_vals,  width, label='RE',  color='#DD8452', alpha=0.85)

axes[0].set_ylim(0, 1.05)
axes[0].set_xticks(x)
axes[0].set_xticklabels(categories, fontsize=11)
axes[0].set_ylabel('Score', fontsize=11)
axes[0].set_title('NER vs RE Metrics', fontsize=12)
axes[0].legend(fontsize=10)
axes[0].axhline(y=0.351, color='red', linestyle='--', linewidth=1.2, alpha=0.7, label='Baseline')
axes[0].legend(fontsize=10)

for bar in bars1:
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f'{bar.get_height():.3f}', ha='center', va='bottom', fontsize=9)

# 右图：最终得分 vs Baseline
score_labels = ['Your Score\n(Corrected vs Gold)', 'Baseline\nTrack-A', 'Baseline\nTrack-B']
score_vals   = [0.6074, 0.351, 0.340]
colors       = ['#2ca02c', '#d62728', '#d62728']

bars = axes[1].bar(score_labels, score_vals, color=colors, alpha=0.85, width=0.4)
axes[1].set_ylim(0, 0.75)
axes[1].set_ylabel('Total Score', fontsize=11)
axes[1].set_title('Total Score vs Baseline', fontsize=12)

for bar in bars:
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f'{bar.get_height():.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

axes[1].text(0, 0.62, '↑ +0.256 vs Track-A Baseline', ha='center', fontsize=9, color='#2ca02c')

plt.tight_layout()
plt.savefig('/home/ubuntu/score_overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("图1已保存")

# ============================================================
# 图2：NER 各类别 F1 分数
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.suptitle('Per-Category F1 Score Breakdown', fontsize=13, fontweight='bold')

ner_labels = ['ABS', 'BIS', 'BM', 'CHR', 'CROP', 'CROSS', 'GENE', 'GST', 'MRK', 'QTL', 'TRT', 'VAR']
ner_prec   = [0.785, 0.792, 0.504, 0.738, 0.885, 0.619, 0.819, 0.882, 0.806, 0.782, 0.658, 0.862]
ner_rec    = [0.853, 0.864, 0.795, 0.849, 0.914, 0.667, 0.838, 0.833, 0.888, 0.795, 0.851, 0.825]
ner_f1     = [0.818, 0.826, 0.617, 0.790, 0.899, 0.642, 0.829, 0.857, 0.845, 0.789, 0.742, 0.843]

x = np.arange(len(ner_labels))
width = 0.28

axes[0].bar(x - width, ner_prec, width, label='Precision', color='#4C72B0', alpha=0.8)
axes[0].bar(x,         ner_rec,  width, label='Recall',    color='#55A868', alpha=0.8)
axes[0].bar(x + width, ner_f1,   width, label='F1',        color='#C44E52', alpha=0.8)

axes[0].set_ylim(0, 1.05)
axes[0].set_xticks(x)
axes[0].set_xticklabels(ner_labels, fontsize=9)
axes[0].set_ylabel('Score', fontsize=11)
axes[0].set_title('NER Per-Category Scores', fontsize=12)
axes[0].legend(fontsize=9)
axes[0].axhline(y=0.7923, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Overall F1')

# 标注最低分
min_idx = ner_f1.index(min(ner_f1))
axes[0].annotate(f'Lowest: {min(ner_f1):.3f}',
                 xy=(min_idx + width, min(ner_f1)),
                 xytext=(min_idx + width + 0.5, min(ner_f1) + 0.08),
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='red', fontsize=9)

# RE 各类别
re_labels = ['AFF', 'CON', 'HAS', 'LOI', 'OCI', 'USE']
re_prec   = [0.387, 0.698, 0.616, 0.365, 0.750, 0.419]
re_rec    = [0.508, 0.458, 0.679, 0.352, 0.643, 0.406]
re_f1     = [0.439, 0.553, 0.646, 0.358, 0.692, 0.413]

x2 = np.arange(len(re_labels))
axes[1].bar(x2 - width, re_prec, width, label='Precision', color='#4C72B0', alpha=0.8)
axes[1].bar(x2,         re_rec,  width, label='Recall',    color='#55A868', alpha=0.8)
axes[1].bar(x2 + width, re_f1,   width, label='F1',        color='#C44E52', alpha=0.8)

axes[1].set_ylim(0, 1.05)
axes[1].set_xticks(x2)
axes[1].set_xticklabels(re_labels, fontsize=11)
axes[1].set_ylabel('Score', fontsize=11)
axes[1].set_title('RE Per-Category Scores', fontsize=12)
axes[1].legend(fontsize=9)
axes[1].axhline(y=0.4830, color='black', linestyle='--', linewidth=1, alpha=0.5)

# 标注最低分
min_idx2 = re_f1.index(min(re_f1))
axes[1].annotate(f'Lowest: {min(re_f1):.3f}',
                 xy=(min_idx2 + width, min(re_f1)),
                 xytext=(min_idx2 + width + 0.3, min(re_f1) + 0.1),
                 arrowprops=dict(arrowstyle='->', color='red'),
                 color='red', fontsize=9)

plt.tight_layout()
plt.savefig('/home/ubuntu/score_by_category.png', dpi=150, bbox_inches='tight')
plt.close()
print("图2已保存")

# ============================================================
# 图3：TP/FP/FN 堆叠图（直观看哪里丢分）
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.suptitle('TP / FP / FN Breakdown (Where Points Are Lost)', fontsize=13, fontweight='bold')

# NER
ner_tp = [139, 19, 62, 62, 169, 26, 249, 15, 87, 97, 393, 137]
ner_fp = [38,   5, 61, 22,  22, 16,  55,  2, 21, 27, 204,  22]
ner_fn = [24,   3, 16, 11,  16, 13,  48,  3, 11, 25,  69,  29]

x = np.arange(len(ner_labels))
axes[0].bar(x, ner_tp, label='TP (Correct)', color='#2ca02c', alpha=0.85)
axes[0].bar(x, ner_fp, bottom=ner_tp, label='FP (Over-predict)', color='#d62728', alpha=0.85)
axes[0].bar(x, ner_fn, bottom=[t+p for t,p in zip(ner_tp, ner_fp)],
            label='FN (Missed)', color='#ff7f0e', alpha=0.85)
axes[0].set_xticks(x)
axes[0].set_xticklabels(ner_labels, fontsize=9)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].set_title('NER: TP / FP / FN per Category', fontsize=12)
axes[0].legend(fontsize=9)

# RE
re_tp = [133, 60, 106, 62, 9, 13]
re_fp = [211, 26,  66,108, 3, 18]
re_fn = [129, 71,  50,114, 5, 19]

x2 = np.arange(len(re_labels))
axes[1].bar(x2, re_tp, label='TP (Correct)', color='#2ca02c', alpha=0.85)
axes[1].bar(x2, re_fp, bottom=re_tp, label='FP (Over-predict)', color='#d62728', alpha=0.85)
axes[1].bar(x2, re_fn, bottom=[t+p for t,p in zip(re_tp, re_fp)],
            label='FN (Missed)', color='#ff7f0e', alpha=0.85)
axes[1].set_xticks(x2)
axes[1].set_xticklabels(re_labels, fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].set_title('RE: TP / FP / FN per Category', fontsize=12)
axes[1].legend(fontsize=9)

plt.tight_layout()
plt.savefig('/home/ubuntu/score_tpfpfn.png', dpi=150, bbox_inches='tight')
plt.close()
print("图3已保存")
