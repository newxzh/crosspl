import os
import json

def is_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False

def count_and_rename_json_files(directory):
    json_file_count = 0
    for root, dirs, files in os.walk(directory):
        print(f"Looking in: {root}")
        for file in files:
            file_path = os.path.join(root, file)
            if is_json_file(file_path):
                json_file_count += 1
                # 检查是否已有 .json 后缀
                if not file.lower().endswith('.json'):
                    new_file = file + '.json'
                    new_path = os.path.join(root, new_file)
                    os.rename(file_path, new_path)
                    print(f"Renamed: {file_path} -> {new_path}")
                else:
                    print(f"Valid JSON with .json: {file_path}")
    return json_file_count

# Example usage
directory_path = 'D:\CAE\PolyBench\FFI_Bench\pythonh'
json_file_count = count_and_rename_json_files(directory_path)
print(f'Total valid JSON files found and renamed if needed: {json_file_count}')
