import os
import json
import statistics
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
def skip_note(line, ext, flag):
    line = line.strip()
    if ext in [".rb",".sh",".r",".py"]:
        if flag % 2 == 1:
            return True
        if line.startswith('#'):
            return True
        if "'''" in line or '"""' in line:
            return True
        return False

    elif ext in [".cpp",".cc",".java",".c",".js",".ts",".php",".rs",".kt",".swift",".scala",".dart"]:
        if line.startswith('//'):
            return True
        if flag % 2 == 1:
            return True
        if line.startswith('/*') and line.endswith('*/'):
            return True
        if line.startswith('*/'):
            return True
        return False

    elif ext in [".html",".m",".mm"]:
        if line.startswith("<!--") and line.endswith("-->"):
            return True
        if flag % 2 == 1:
            return True
        return False

    elif ext == ".as":
        if line.startswith(";") or line.startswith("#"):
            return True
        return False
    else:
        return False

def count_code_lines(code_str, ext):
    lines = code_str.splitlines()
    count = 0
    flag = 0  
    for line in lines:
        stripped = line.strip()
        if ext in [".py", ".rb", ".r"]:
            if "'''" in stripped or '"""' in stripped:
                flag += 1
                if skip_note(stripped, ext, flag):
                    continue
        elif ext in [".cpp",".cc",".java",".c",".js",".ts",".php",".rs",".kt",".swift",".scala",".dart"]:
            if stripped.startswith("/*"):
                flag += 1
                if skip_note(stripped, ext, flag):
                    continue
            if stripped.endswith("*/") and flag > 0:
                flag -= 1
                continue

        if not skip_note(stripped, ext, flag):
            count += 1
    return count


folder_path = "/home/xiong/ffi/crosspl/PolyBench/FFI_Bench/" 
# folder_path_total = ["/home/xiong/ffi/crosspl/PolyBench/IPC_Bench/java_ipc/","/home/xiong/ffi/crosspl/PolyBench/IPC_Bench/python_ipc/" ,"/home/xiong/ffi/crosspl/PolyBench/IPC_Bench/js_ipc/" ,
#                "/home/xiong/ffi/crosspl/PolyBench/IPC_Bench/php_ipc/" ,"/home/xiong/ffi/crosspl/PolyBench/IPC_Bench/go_ipc/" ,"/home/xiong/ffi/crosspl/PolyBench/IPC_Bench/c++_ipc/" ] 

ext_list = [".java",".py",".js",".php",".go",".cc"]


line_counts = []
# for i in range(6):
    # folder_path = folder_path_total[i]
json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
for json_file in json_files:
    file_path = os.path.join(folder_path, json_file)
    ext = ".py" 
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        canonical_solution = data.get("Canonical_solution", "")
        lines = count_code_lines(canonical_solution, ext)
        line_counts.append(lines)


# plt.figure(figsize=(8,5))
# plt.hist(line_counts, bins=50, color='skyblue', edgecolor='black')
# plt.xlabel("Code lines of CrossPL-IPC")
# plt.ylabel("Number of Tasks")
# plt.title("Distribution of Canonical solution Code Lines")
# plt.grid(axis='y', alpha=0.75)
# # plt.savefig("/home/xiong/ffi/crosspl/PolyBench/ipc.pdf", format='pdf', bbox_inches='tight')

# print(f"Processed {len(json_files)} JSON files.")
print(f"Mid code lines: {statistics.median(line_counts)}")
print(f"Average code lines: {sum(line_counts)/len(line_counts):.2f}")
print(f"Max code lines: {max(line_counts)}, Min code lines: {min(line_counts)}")
