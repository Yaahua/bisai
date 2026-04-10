#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 当前 Track-A 排行榜数据（2026-04-10 实测）
# ============================================================
teams  = ['1. Fenmu\n(Jiangxi Normal)', '2. 12345\n(Nanjing U)',
          '3. ZZUnlp\n(Zhengzhou U)', '4. Zhengyou\n(Zhengzhou U)',
          '5. Hunzi\n(Wenzhou)', '6. ggb\n(Tsinghua)',
          '7. Youmo Peng\n(Xinshijie)', '8. Geren', '9. LLM-Dixia']
scores = [0.417, 0.351, 0.343, 0.292, 0.280, 0.277, 0.227, 0.093, 0.021]

# ============================================================
# 你的三种场景预测
# ============================================================
# 场景1：直接提交修正数据（当前状态，已知有标准偏移）
# 训练集自评 0.6074，但测试集是未知数据，且有 14 条 text 被篡改无法匹配
# 测试集上的 RE 偏移会更严重 → 保守估计 0.28~0.33
scenario_direct = {'label': 'Scenario A\n(Submit corrected data as-is)',
                   'low': 0.25, 'mid': 0.29, 'high': 0.33,
                   'color': '#e74c3c', 'note': 'AFF/LOI bias → RE drags down'}

# 场景2：用官方原始数据做 Few-shot（中等质量 Prompt，5-8条示例）
# 对标当前第2~3名水平，大模型能力强但 Prompt 工程有限
# → 预测 0.32~0.38
scenario_fewshot = {'label': 'Scenario B\n(Official data Few-shot, basic prompt)',
                    'low': 0.32, 'mid': 0.36, 'high': 0.40,
                    'color': '#f39c12', 'note': 'Competitive, ~2nd-3rd range'}

# 场景3：精心设计 Prompt（含官方规律约束 + 链式思考 + 类型约束）
# 对标第1名水平，需要精细的 Prompt 工程
# → 预测 0.38~0.45
scenario_optimized = {'label': 'Scenario C\n(Optimized prompt + official rules)',
                      'low': 0.38, 'mid': 0.42, 'high': 0.46,
                      'color': '#2ecc71', 'note': 'Top-1 competitive'}

scenarios = [scenario_direct, scenario_fewshot, scenario_optimized]

# ============================================================
# 绘图
# ============================================================
fig = plt.figure(figsize=(16, 9))

# --- 左图：排行榜 + 你的预测区间 ---
ax1 = fig.add_axes([0.05, 0.12, 0.52, 0.78])

y_pos = np.arange(len(teams))
bar_colors = []
for s in scores:
    if s >= 0.40: bar_colors.append('#c0392b')
    elif s >= 0.34: bar_colors.append('#e67e22')
    elif s >= 0.25: bar_colors.append('#f39c12')
    else: bar_colors.append('#bdc3c7')

bars = ax1.barh(y_pos, scores, color=bar_colors, alpha=0.88, height=0.55, zorder=3)

# 分数标注
for bar, score in zip(bars, scores):
    ax1.text(bar.get_width() + 0.004, bar.get_y() + bar.get_height()/2,
             f'{score:.3f}', va='center', fontsize=10, fontweight='bold', color='#2c3e50')

ax1.set_yticks(y_pos)
ax1.set_yticklabels(teams, fontsize=9)
ax1.set_xlabel('Total Score  (0.4×NER_F1 + 0.6×RE_F1)', fontsize=10)
ax1.set_title('Track-A Leaderboard (2026-04-10)\n+ Your Score Prediction Zones',
              fontsize=11, fontweight='bold')
ax1.set_xlim(0, 0.56)
ax1.grid(axis='x', alpha=0.3, zorder=0)

# Baseline 线
ax1.axvline(x=0.351, color='#7f8c8d', linestyle=':', linewidth=1.5, alpha=0.8, zorder=2)
ax1.text(0.351, -0.8, 'Baseline\n0.351', fontsize=8, color='#7f8c8d', ha='center')

# 三个场景的预测区间（水平色带）
zone_y = [-1.2, -1.85, -2.5]
zone_labels = ['A', 'B', 'C']
zone_colors = ['#e74c3c', '#f39c12', '#2ecc71']
for i, (sc, zy) in enumerate(zip(scenarios, zone_y)):
    ax1.barh(zy, sc['high'] - sc['low'], left=sc['low'],
             height=0.45, color=sc['color'], alpha=0.35, zorder=3)
    ax1.axvline(x=sc['mid'], color=sc['color'], linestyle='--',
                linewidth=2, alpha=0.9, zorder=4)
    ax1.text(sc['mid'], zy, f"  {sc['mid']:.2f}", va='center',
             fontsize=9, color=sc['color'], fontweight='bold')
    ax1.text(0.005, zy, f"Your {zone_labels[i]}: {sc['low']:.2f}~{sc['high']:.2f}",
             va='center', fontsize=8.5, color=sc['color'], fontweight='bold')

ax1.set_ylim(-3.0, len(teams) - 0.3)

# 分隔线
ax1.axhline(y=-0.5, color='#2c3e50', linewidth=1.2, linestyle='-', alpha=0.4)
ax1.text(0.28, -0.65, '▼ Your predicted score zones', fontsize=8.5,
         color='#2c3e50', style='italic')

# --- 右图：场景对比条形图 ---
ax2 = fig.add_axes([0.63, 0.12, 0.34, 0.78])

scenario_names = ['Scenario A\n(Current state,\nsubmit corrected)',
                  'Scenario B\n(Basic Few-shot\nfrom official data)',
                  'Scenario C\n(Optimized\nprompt+rules)']
mids  = [0.29, 0.36, 0.42]
lows  = [0.25, 0.32, 0.38]
highs = [0.33, 0.40, 0.46]
s_colors = ['#e74c3c', '#f39c12', '#2ecc71']

x = np.arange(3)
# 误差棒
errs_low  = [m - l for m, l in zip(mids, lows)]
errs_high = [h - m for h, m in zip(highs, mids)]

bars2 = ax2.bar(x, mids, color=s_colors, alpha=0.82, width=0.55,
                yerr=[errs_low, errs_high],
                error_kw=dict(ecolor='#2c3e50', capsize=8, capthick=2, elinewidth=2),
                zorder=3)

# 参考线
ax2.axhline(y=0.417, color='#c0392b', linestyle='--', linewidth=1.5, alpha=0.8)
ax2.text(2.4, 0.420, '1st: 0.417', fontsize=8.5, color='#c0392b', fontweight='bold')
ax2.axhline(y=0.351, color='#7f8c8d', linestyle=':', linewidth=1.5, alpha=0.8)
ax2.text(2.4, 0.354, 'Baseline: 0.351', fontsize=8, color='#7f8c8d')
ax2.axhline(y=0.343, color='#e67e22', linestyle=':', linewidth=1.2, alpha=0.6)
ax2.text(2.4, 0.335, '3rd: 0.343', fontsize=8, color='#e67e22')

for bar, mid, low, high in zip(bars2, mids, lows, highs):
    ax2.text(bar.get_x() + bar.get_width()/2, high + 0.008,
             f'{low:.2f}~{high:.2f}', ha='center', fontsize=8.5,
             fontweight='bold', color='#2c3e50')

ax2.set_xticks(x)
ax2.set_xticklabels(scenario_names, fontsize=8.5)
ax2.set_ylabel('Predicted Total Score', fontsize=10)
ax2.set_title('Your Score Prediction\nby Scenario', fontsize=11, fontweight='bold')
ax2.set_ylim(0.15, 0.54)
ax2.grid(axis='y', alpha=0.3, zorder=0)

# 排名标注
rank_notes = ['~5th-8th\n(below baseline)', '~2nd-4th\n(competitive)', '~1st-2nd\n(top tier)']
rank_colors = ['#e74c3c', '#f39c12', '#2ecc71']
for i, (note, rc) in enumerate(zip(rank_notes, rank_colors)):
    ax2.text(i, lows[i] - 0.025, note, ha='center', fontsize=8,
             color=rc, fontweight='bold')

plt.savefig('/home/ubuntu/tracka_prediction.png', dpi=150, bbox_inches='tight')
plt.close()
print("Track-A 预测图已保存")
