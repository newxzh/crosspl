import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 读取 CSV 文件
df = pd.read_csv(r"C:\Users\xio\Desktop\pass1.csv")

# 编程语言列表
languages = ["Java", "Python", "Go", "JavaScript", "PHP", "C++"]

# 人民币配色（红、绿、紫、朱、粉、灰蓝）
colors = {
    "Java": "#D97696",         # 粉红
    "Python": "#99BD7E",       # 翠绿
    "Go": "#C89FDE",           # 浅紫
    "JavaScript": "#FF785A",   # 朱红
    "PHP": "#F4C2C2",          # 浅粉
    "C++": "#779ECB"           # 灰蓝
}

# 补闭环的模型名
labels = df['Model'].tolist()
labels.append(labels[0])  # 闭环

# 创建角度数组（闭环）
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=True)

# 创建雷达图
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# 绘制每种语言的折线和填充
for lang in languages:
    values = df[lang].tolist()
    values.append(values[0])  # 闭环
    ax.plot(angles, values, "-",label=lang, color=colors[lang], linewidth=2)
    ax.fill(angles, values, color=colors[lang], alpha=0.1)  # 颜色填充

# 设置角度刻度
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels[:-1], fontsize=9)

# 美化
ax.set_yticklabels([])
ax.spines['polar'].set_visible(False)
ax.grid(True, linestyle='--', linewidth=2.2, alpha=1)
ax.set_title('Pass@1 Radar Chart across Languages', size=16, y=1.1)
# 设置角度刻度
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels[:-1], fontsize=12)  # 字体大小由9 → 14（可根据需要调整）

ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
ax.set_ylim(0, 1.0)
plt.tight_layout()
plt.savefig(r"D:\CAE\show_results\ridar_pass1.pdf", format='pdf')
plt.show()
