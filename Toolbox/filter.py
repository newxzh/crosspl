# import pandas as pd
# # 读取 CSV 文件
# df = pd.read_csv("D:\CrossPL-Interporate\Repo_Info\Info_IRI_C++.csv")
# # 按 label 分组，每组随机采样最多100个
# sampled_df = df.groupby("Interface_name", group_keys=False).apply(lambda x: x.sample(n=min(len(x), 100), random_state=42))
# # 保存结果
# sampled_df.to_csv("D:\CrossPL-Interporate\Repo_Info\Info_IRI_C++_filtered.csv", index=False)


import pandas as pd
import tiktoken
import os

# === 配置部分 ===
csv_path = "D:\CrossPL-Interporate\Repo_Info\Info_IRI_python_filtered.csv"            # 输入 CSV 文件路径
filepath_column = "File_path"          # 存放文本路径的列名
token_limit = 64000                   # 最大 token 限制（DeepSeek-V3 为例）
output_csv_path = "D:\CrossPL-Interporate\Repo_Info\Info_IRI_PHP_filtered.csv"

# 使用 tiktoken 的 tokenizer（用的是 GPT-3.5 tokenizer，兼容性好）
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens_in_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"读取或编码失败: {file_path}, 错误: {e}")
        return float('inf')  # 无法读取的文件视为非法

def main():
    df = pd.read_csv(csv_path)

    if filepath_column not in df.columns:
        print(f"CSV 中未找到列 '{filepath_column}'")
        return

    token_counts = []
    for path in df[filepath_column]:
        if not os.path.isfile(path):
            print(f"路径不存在: {path}")
            token_counts.append(float('inf'))
        else:
            tokens = count_tokens_in_file(path)
            print(f"{path} ==> {tokens} tokens")
            token_counts.append(tokens)

    df["token_count"] = token_counts

    # 过滤掉超过 token 限制的行
    filtered_df = df[df["token_count"] <= token_limit]

    # 写入新 CSV
    filtered_df.drop(columns=["token_count"]).to_csv(output_csv_path, index=False)
    print(f"过滤完成，输出文件: {output_csv_path}")

if __name__ == "__main__":
    main()
