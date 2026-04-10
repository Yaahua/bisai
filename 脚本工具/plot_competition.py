#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('CCL2026-MGBIE A-Board Leaderboard vs Your Predicted Score\n(As of 2026-04-10)',
             fontsize=13, fontweight='bold')

# ============================================================
# 左图：Track-A 不微调榜
# ============================================================
track_a_teams = ['分母\n(Jiangxi Normal)', '12345\n(Nanjing U)', 'ZZUnlp\n(Zhengzhou U)',
                 '郑友无双\n(Zhengzhou U)', '混子队\n(Wenzhou)', 'ggb\n(Tsinghua)',
                 '幽默彭博士\n(Xinshijie)', '个人', 'LLM-地下']
track_a_scores = [0.417, 0.351, 0.343, 0.292, 0.280, 0.277, 0.227, 0.093, 0.021]

# 你的预测区间
your_lower_a = 0.30   # 悲观：直接用修正数据（有标准偏移）
your_upper_a = 0.42   # 乐观：用官方原始数据+强大Few-shot
your_realistic_a = 0.35  # 现实：中等水平Few-shot

colors_a = ['#e74c3c' if s >= 0.35 else '#f39c12' if s >= 0.25 else '#95a5a6'
            for s in track_a_scores]

y_pos = np.arange(len(track_a_teams))
bars = axes[0].barh(y_pos, track_a_scores, color=colors_a, alpha=0.85, height=0.6)
axes[0].set_yticks(y_pos)
axes[0].set_yticklabels(track_a_teams, fontsize=8.5)
axes[0].set_xlabel('Total Score', fontsize=10)
axes[0].set_title('Track-A (No Fine-tuning)\n9 teams currently', fontsize=11, fontweight='bold')
axes[0].set_xlim(0, 0.55)

for bar, score in zip(bars, track_a_scores):
    axes[0].text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                 f'{score:.3f}', va='center', fontsize=9, fontweight='bold')

# 你的预测区间
axes[0].axvspan(your_lower_a, your_upper_a, alpha=0.12, color='#2ecc71', zorder=0)
axes[0].axvline(x=your_realistic_a, color='#27ae60', linestyle='--', linewidth=2, zorder=5)
axes[0].text(your_realistic_a + 0.005, 8.5, 'Your realistic\nprediction\n~0.35', 
             fontsize=8, color='#27ae60', fontweight='bold', va='top')
axes[0].axvline(x=0.351, color='gray', linestyle=':', linewidth=1.2, alpha=0.6)
axes[0].text(0.351, -0.7, 'Baseline\n0.351', fontsize=7.5, color='gray', ha='center')

# 标注第1名
axes[0].annotate('★ 1st: 0.417', xy=(0.417, 8), xytext=(0.44, 7.5),
                 fontsize=8.5, color='#e74c3c', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.2))

# 图例
patch_green = mpatches.Patch(color='#2ecc71', alpha=0.3, label='Your predicted range (0.30~0.42)')
axes[0].legend(handles=[patch_green], fontsize=8, loc='lower right')

# ============================================================
# 右图：Track-B 微调榜
# ============================================================
track_b_teams = ['郑友无双\n(Zhengzhou U)', '分母\n(Jiangxi Normal)',
                 'wcy_young\n(S.China Normal)', 'ggb\n(Tsinghua)', '幽默彭博士\n(Xinshijie)']
track_b_scores = [0.417, 0.347, 0.345, 0.258, 0.221]

your_lower_b = 0.32
your_upper_b = 0.45
your_realistic_b = 0.38

colors_b = ['#e74c3c' if s >= 0.35 else '#f39c12' if s >= 0.25 else '#95a5a6'
            for s in track_b_scores]

y_pos_b = np.arange(len(track_b_teams))
bars_b = axes[1].barh(y_pos_b, track_b_scores, color=colors_b, alpha=0.85, height=0.5)
axes[1].set_yticks(y_pos_b)
axes[1].set_yticklabels(track_b_teams, fontsize=9)
axes[1].set_xlabel('Total Score', fontsize=10)
axes[1].set_title('Track-B (Fine-tuning, ≤7B)\n5 teams currently', fontsize=11, fontweight='bold')
axes[1].set_xlim(0, 0.58)

for bar, score in zip(bars_b, track_b_scores):
    axes[1].text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                 f'{score:.3f}', va='center', fontsize=9, fontweight='bold')

axes[1].axvspan(your_lower_b, your_upper_b, alpha=0.12, color='#3498db', zorder=0)
axes[1].axvline(x=your_realistic_b, color='#2980b9', linestyle='--', linewidth=2, zorder=5)
axes[1].text(your_realistic_b + 0.005, 4.4, 'Your realistic\nprediction\n~0.38', 
             fontsize=8, color='#2980b9', fontweight='bold', va='top')
axes[1].axvline(x=0.340, color='gray', linestyle=':', linewidth=1.2, alpha=0.6)
axes[1].text(0.340, -0.5, 'Baseline\n0.340', fontsize=7.5, color='gray', ha='center')

patch_blue = mpatches.Patch(color='#3498db', alpha=0.3, label='Your predicted range (0.32~0.45)')
axes[1].legend(handles=[patch_blue], fontsize=8, loc='lower right')

plt.tight_layout()
plt.savefig('/home/ubuntu/competition_prediction.png', dpi=150, bbox_inches='tight')
plt.close()
print("竞争力对比图已保存")
