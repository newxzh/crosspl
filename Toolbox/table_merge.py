import os
import pandas as pd

# 定义存放 CSV 文件的目录
folder_path = 'D:\CAE\java_info'

# 获取目录中所有 CSV 文件的文件名
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# 读取所有 CSV 文件，并存放到一个列表中
df_list = [pd.read_csv(os.path.join(folder_path, file),on_bad_lines='warn') for file in csv_files]

# 合并所有 DataFrame
merged_df = pd.concat(df_list, ignore_index=True)

# 将合并后的 DataFrame 保存为新的 CSV 文件
merged_df.to_csv('D:\CAE\java_info\Info_IRI.csv', index=False)

print("合并完成，共合并了 {} 个文件。".format(len(csv_files)))
