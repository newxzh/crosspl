import os

def delete_matching_json_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.startswith("FFI") and file.endswith("_candidate_1.json"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

# 使用示例
delete_matching_json_files("D:\CAE\PolyBench\FFI_Bench\ctypes")
