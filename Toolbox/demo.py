# import json
#
# data = [
#     {"id": 1, "name": "Alice"},
#     {"id": 2, "name": "Bob"}
# ]
# new_entry = {"id": 3, "name": "Charlie"}
# data.append(new_entry)
# with open("data.json", "w") as f:
#     json.dump(data, f, indent=2)
# RepoDir = "D:\\CAE\\Splited_Repository" + "\\7\\"
# print(RepoDir)
# File = r"{}".format(RepoDir)
# print(File)
# with open("data.json", "r+") as f:
#     data = json.load(f)
#     data.append(new_entry)
#     f.seek(0)
#     json.dump(data, f, indent=2)
#     f.truncate()

# import pandas as pd
#
# FilePath = "D:\CAE\Repo_Info\Info_IRI_java.csv"
# # 示例数据
# df = pd.read_csv(FilePath, encoding='latin-1')
# # 按照 'name' 列去重，只保留第一次出现的行
# df_unique = df.drop_duplicates(subset=['File_path', "Classfier","Classfier_ID","Interface_class",'Interface_name','Status_description'], keep='first')
# df_unique.to_csv('111.csv', index=False,encoding='utf-8')

import pandas as pd

# 读取CSV
df = pd.read_csv("D:\CrossPL-Interporate\Repo_Info\Info_IRI_C++.csv")

# 1. 提取唯一值并排序
unique_vals = sorted(df['Classfier_ID'].unique())

# 2. 创建映射字典：原值 -> 连续编号
val_map = {val: idx+146 for idx, val in enumerate(unique_vals)}

# 3. 映射原列
df['Classfier_ID'] = df['Classfier_ID'].map(val_map)

df.to_csv('D:\CrossPL-Interporate\Repo_Info\Info_IRI_C++.csv', index=False,encoding='utf-8')

# import pickle as pkl
# with open('my_list.pkl', 'rb') as f:
#     loaded_list = pkl.load(f)
#
# print(loaded_list)  # ['python', 'c++', 'go', 'rust']

# import requests
#
# url = "https://api.siliconflow.cn/v1/chat/completions"
#
# payload = {
#     "model": "Qwen/QwQ-32B",
#     "messages": [
#         {
#             "role": "user",
#             "content": "What opportunities and challenges will the Chinese large model industry face in 2025?"
#         }
#     ],
#     "stream": False,
#     "max_tokens": 512,
#     "stop": None,
#     "temperature": 0.7,
#     "top_p": 0.7,
#     "top_k": 50,
#     "frequency_penalty": 0.5,
#     "n": 1,
#     "response_format": {"type": "text"},
#     "tools": [
#         {
#             "type": "function",
#             "function": {
#                 "description": "<string>",
#                 "name": "<string>",
#                 "parameters": {},
#                 "strict": False
#             }
#         }
#     ]
# }
# headers = {
#     "Authorization": "Bearer sk-crqkgwpzpfpcwvskxfnkxwqxuhiykhfniuqgrlrhlfklvgwk",
#     "Content-Type": "application/json"
# }
#
# response = requests.request("POST", url, json=payload, headers=headers)
#
# print(response.text)

# import pandas as pd
#
# df = pd.read_csv('D:\CAE\Repo_Info\Info_IRI_js_filtered.csv')
#
# # 2. 定位 Interface_name 列中值为指定文本的行，并将该行的 Status_description 列改为
# Status_description = ['Step 1: Create a new XMLHttpRequest object to initiate the request.','Step 2: Configure the request with the `open()` method, defining the request type (GET, POST) and the URL.',
#                       'Step 3: Set the request headers using `setRequestHeader()` for specific content types.','Step 4: Set up response callback to handle asynchronous events',
#                       'Step 5: Send the request to the server using the `send()` or `sendAsBinary()` method.']
# mask = df['Interface_name'] == 'HTTP Server - side based on XMLHttpRequest in JavaScript'
# df.loc[mask, 'Status_description'] = "{}".format(Status_description)
#
# # 3. 将修改后的 DataFrame 写回到新的 CSV（或覆盖原文件）
# df.to_csv('D:\CAE\Repo_Info\Info_IRI_js_filtered.csv', index=False)

# import os
# import json
#
#
# def load_all_json_files(directory):
#     json_data = {}
#
#     for root, _, files in os.walk(directory):
#         for file in files:
#             if file.endswith(".json"):
#                 filepath = os.path.join(root, file)
#                 try:
#                     with open(filepath, 'r', encoding='utf-8') as f:
#                         data = json.load(f)
#                         json_data[filepath] = data
#                 except Exception as e:
#                     print(f"❌ 读取失败: {filepath}，错误：{e}")
#
#     return json_data
#
#
# # 示例用法
# folder_path = "D:\CAE\PolyBench\IPC_Bench\js_ipc"  # 替换成你的路径
# all_json = load_all_json_files(folder_path)
#
# # 打印所有文件路径和对应的内容摘要
# a_l = []
# for path, content in all_json.items():
#     # print(f"\n✅ 文件: {path}")
#     if content["FSMID_for_test"] == 100:
#         print(f"\n✅ 文件: {path}")
#         a_l.append(content["FSMID_for_test"])
#     # print(f"预览: {str(content)[:200]}...")
# print(len(a_l))

#
# import re
# print(re.search("fwrite.*(GET|POST|PUT|DELETE)","fwrite(\"POST\""))
import os
import json

# # 替换为你自己的文件夹路径
# folder_path = "D:\CrossPL-Interporate\PolyBench\IPC_Bench\c++_ipc"
#
# for filename in os.listdir(folder_path):
#     if filename.endswith(".json"):
#         file_path = os.path.join(folder_path, filename)
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#
#             # 检查键是否存在并且是数字
#             if "FSMID_for_test" in data and isinstance(data["FSMID_for_test"], int):
#                 data["FSMID_for_test"] -= 2
#
#                 with open(file_path, "w", encoding="utf-8") as f:
#                     json.dump(data, f, indent=4, ensure_ascii=False)
#                 print(f"Updated {filename}")
#             else:
#                 print(f"Skipped {filename}: 'FSMID_for_test' not found or not an integer.")
#
#         except Exception as e:
#             print(f"Failed to process {filename}: {e}")




