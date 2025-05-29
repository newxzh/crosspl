import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取 CSV 文件
df = pd.read_csv(r"C:\Users\xio\Desktop\pass1.csv")
df1 = pd.read_csv(r"C:\Users\xio\Desktop\pass5.csv")

# 排序 df，并同步 df1 的顺序
df = df.sort_values(by="C++", ascending=False)
df1 = df1.set_index("Model").loc[df["Model"].values].reset_index()

# 准备数据
models = df["Model"]
x = np.arange(len(models))
bar_width = 0.4

# 设置图像大小
plt.figure(figsize=(16, 6))

# 绘制两组柱状图
bars1 = plt.bar(x - bar_width/2, df["C++"] * 100, width=bar_width, color='#F4C2C2', label="Pass@1")
bars2 = plt.bar(x + bar_width/2, df1["C++"] * 100, width=bar_width, color='#779ECB', label="Pass@5")

# 设置 x 轴标签
plt.xticks(x, models, rotation=45, ha='right', fontsize=10, fontname='Times New Roman')

# 添加数值标签
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 7, height + 0.5, f'{height:.2f}',
             ha='center', va='bottom', fontsize=9, fontname='Times New Roman')

for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 1.5, height + 0.5, f'{height:.2f}',
             ha='center', va='bottom', fontsize=9, fontname='Times New Roman')

# 图表标题与坐标轴
plt.title("Pass@1 and Pass@5 Scores of Models on C++", fontsize=16, fontname='Times New Roman')
plt.ylabel("Pass@K Score (%)", fontsize=12, fontname='Times New Roman')
plt.ylim(0, max(df1["C++"] * 100) * 1.2)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.legend()

# 自动布局与保存
plt.tight_layout()
plt.savefig(r"D:\CAE\show_results\pass_scores_C++.pdf", format='pdf')
plt.show()
