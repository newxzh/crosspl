import pandas as pd

# 读取 CSV 文件
df = pd.read_csv("D:\CrossPL-Interporate\Repo_Info\Info_IRI_python_filtered.csv", encoding="utf-8")

# 指定要替换的列和替换后的字符
target_column = "File_path"  # 替换成你实际的列名
new_char = "E"

# 替换该列中每个字符串的第一个字符
df[target_column] = df[target_column].astype(str).str.replace(r"^.", new_char, regex=True)

# 保存修改后的 CSV 文件
df.to_csv("D:\CrossPL-Interporate\Repo_Info\Info_IRI_python_filtered.csv", index=False)

print("替换完成！")
