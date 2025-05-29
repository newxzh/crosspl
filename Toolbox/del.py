import os
import json


def clean_instruction_field(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    instruction = data.get("Instruction", "")
                    if isinstance(instruction, str):
                        stripped_instruction = instruction.strip()

                        # 记录包含特定开头内容的文件
                        if stripped_instruction.startswith("Here is the structured analysis of the provided code"):
                            print(f"[Match] Starts with target phrase: {file_path}")

                        # 清理开头和结尾的```plaintext和```
                        if stripped_instruction.startswith("```plaintext"):
                            instruction = stripped_instruction[12:]  # 去掉 "```plaintext"
                        if instruction.strip().endswith("```"):
                            instruction = instruction.strip()
                            instruction = instruction[:instruction.rfind("```")].strip()

                        data["Instruction"] = instruction

                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                        # print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")


# 示例路径
target_directory = r'D:\CAE\PolyBench\FFI_Bench\pythonh'
clean_instruction_field(target_directory)
