import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv(r"C:\Users\xio\Desktop\pass5.csv")

# 设置语言顺序
languages = ['Java', 'Python', 'Go', 'JavaScript', 'PHP', 'C++']

# 更加清淡的人民币风格配色
colors = ['#FBE4E2', '#DDEFE2', '#E9DDEB', '#FCF5DD', '#E5ECE3', '#E2EDF3']
# colors = ['#F4C7C3', '#F7DDD9', '#F8E5C2', '#DAEAD6', '#CFE9CE', '#E3F1E1']

# 设置画布
plt.figure(figsize=(8, 5))

# 绘制箱线图
box = plt.boxplot([df[lang] * 100 for lang in languages],
                  labels=languages,
                  patch_artist=True,
                  medianprops=dict(color='black'))

# 设置箱体颜色 + 加粗边框
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_linewidth(1.3)  # 加粗边框

# 加粗须、顶线、底线、中位线、异常值
for element in ['whiskers', 'caps', 'medians', 'fliers']:
    for item in box[element]:
        item.set_linewidth(1.5)

# 设置标题与坐标轴
plt.title("Pass@1 Score Distribution per Language", fontsize=14, fontname='Times New Roman', pad=15)
plt.ylabel("Pass@1 Score (%)", fontsize=11, fontname='Times New Roman')
plt.xticks(fontsize=10, fontname='Times New Roman')
plt.yticks(fontsize=10, fontname='Times New Roman')

# 调整y轴范围，减少空白
y_max = max(df[languages].max()) * 100
plt.ylim(0, y_max * 1.05)

# 添加轻柔的网格线
plt.grid(axis='y', linestyle='--', alpha=0.3)

# 紧凑布局
plt.subplots_adjust(left=0.10, right=0.96, top=0.88, bottom=0.12)

# 保存图像
plt.savefig(r"D:\CAE\show_results\pass5_boxplot_softcolors.pdf", format='pdf')

# 显示图像
plt.show()
