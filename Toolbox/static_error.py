import json
# from openai import OpenAI
#
# api_key = "sk-3SaEakbOGZC4v2yFnk0mnmqeZk1GjnMA1CanRvGioklKRClj"
# base_url = "https://yibuapi.com/v1"
#
# error_path = "/home/xiong/ffi/crosspl/Test_results/FFI_results/GPT-4o/Greedy_report.json"
# with open(error_path, "r", encoding="utf-8") as f:
#     data = json.load(f)
#
# def get_prompt(code_file_path):
#     """Reads the content of a prompt file."""
#     with open(code_file_path, "r", encoding="utf-8") as file:
#         code = file.read()
#     return code
# instruction_prompt = get_prompt("/home/xiong/ffi/crosspl/judge.txt")
# error_list = []
# for i in range(len(data)):
#     if data[i]["test_result"] == "Pass":
#         print("Task ID:", data[i]["Task_id"])
#         print("Pass")
#         continue
#     elif data[i]["Return_code"] == -11:
#         error_list.append("6")
#     elif data[i]["Return_code"] == "None":
#         error_list.append("0")
#     else:
#         print("Task ID:", data[i]["Task_id"])
#         ERROR_MESSAGE = data[i]["Error_info"]
#         filter_variables = {"ERROR_MESSAGE": ERROR_MESSAGE}
#         formatted_extraction_prompt = instruction_prompt.format(**filter_variables)
#         client = OpenAI(api_key=api_key, base_url=base_url)
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system",
#                  "content": "You are a senior programmer with expertise in cross-language programming and error analysis. "},
#                 {"role": "user", "content": formatted_extraction_prompt},
#             ],
#             temperature=0,
#             top_p=1,
#             stream=False
#         )
#         result = response.choices[0].message.content
#         print(result)
#         error_list.append(result)
#
# Benchmark = {}
# save_path = f"/home/xiong/ffi/crosspl/Test_results/FFI_results/GPT-4o/Error_List.json"
# Benchmark["Error_list"] = error_list
# with open(save_path, "w", encoding="utf-8") as f:
#     json.dump(Benchmark, f, indent=2, ensure_ascii=False)



error_path = "/home/xiong/ffi/crosspl/Test_results/FFI_results/GPT-4o/Error_List.json"
with open(error_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 假设列表如下
numbers = data["Error_list"]

counts = {str(i): 0 for i in range(1, 7)}
print(counts)
# 遍历列表统计
for num in numbers:
    if num in counts:
        counts[num] += 1

# 输出结果
print(counts)
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# 将 '0' 改名为 "Other"，其它数字改为对应错误类型名称
error_names = {
    # '0': 'Other errors',
    '1': 'Symbol resolution errors',
    '2': 'GSL runtime errors',
    '3': 'Python-level calling errors',
    '4': 'NameError/undefined symbols',
    '5': 'Assertion/test failures',
    '6': 'Memory/crash errors'
}

# 横坐标标签和纵坐标数据
labels = [error_names[k] for k in sorted(counts.keys(), key=lambda x: int(x))]
values = [counts[k] for k in sorted(counts.keys(), key=lambda x: int(x))]

# 绘制柱状图
plt.figure(figsize=(8,6))
bars = plt.bar(labels, values,alpha=0.3)
plt.ylabel("Count")
plt.xlabel("Error Type")
plt.title("Error Type Distribution")
plt.xticks(rotation=15, ha='right')

# 在每个柱子上显示数字
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 1, str(int(height)),
             ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.grid(axis='y', alpha=0.7)
plt.savefig("/home/xiong/ffi/crosspl/Test_results/FFI_results/GPT-4o/error.pdf", format='pdf', bbox_inches='tight')
plt.tight_layout()
