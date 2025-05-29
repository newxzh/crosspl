# import os
# import json
#
# # 替换为你的目标文件夹路径
# folder_path = "D:\CrossPL-Interporate\PolyBench\IPC_Bench\python_ipc"
#
# for filename in os.listdir(folder_path):
#     if filename.endswith(".json"):
#         file_path = os.path.join(folder_path, filename)
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 data = json.load(f)
#
#             # 确保"Instruction"字段存在并是字符串
#             instruction = data.get("Instruction", "")
#             if not isinstance(instruction, str):
#                 print(f"Skipped {filename}: 'Instruction' is not a string.")
#                 continue
#
#             if "Function Description" in instruction:
#                 data["Code_level"] = "Function-level"
#             elif "Class Description" in instruction:
#                 data["Code_level"] = "Class-level"
#             else:
#                 print(f"No matching pattern in 'Instruction' for {filename}")
#                 continue
#
#             with open(file_path, "w", encoding="utf-8") as f:
#                 json.dump(data, f, indent=4, ensure_ascii=False)
#             print(f"Updated {filename}")
#
#         except Exception as e:
#             print(f"Failed to process {filename}: {e}")


import os
import json

# 替换为你的目标文件夹路径
folder_path = "D:\CrossPL-Interporate\PolyBench\IPC_Bench\python_ipc"

class_count = 0
func_count = 0

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            code_level = data.get("Code_level", "")
            if code_level == "Function-level":
                func_count += 1
            elif code_level == "Class-level":
                class_count += 1

        except Exception as e:
            print(f"Failed to process {filename}: {e}")

print("Function-level count:", func_count)
print("Class-level count:", class_count)
