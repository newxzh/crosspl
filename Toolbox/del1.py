import os

def clean_c_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # 删除开头的 ```c
                if lines and lines[0].strip() == '```Python':
                    print(file_path)
                    lines = lines[1:]

                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"Cleaned: {file_path}")

# 用法：替换为你实际的目标路径
target_directory = r"D:\CAE\PolyBench\FFI_Bench\ctypes"
clean_c_files(target_directory)
