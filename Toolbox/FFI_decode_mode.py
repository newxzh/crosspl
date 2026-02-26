import re
import ast
import sys
import json
import subprocess
from math import comb
from collections import Counter

# Pass1_path_list = ["/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.2/pass1.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.4/pass1.json",
#               "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.6/pass1.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.8/pass1.json",
#               "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=1.0/pass1.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=1.2/pass1.json"]
# Pass1_report_path_list = ["/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.2/pass1_report.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.4/pass1_report.json",
#                      "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.6/pass1_report.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=0.8/pass1_report.json",
#                      "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=1.0/pass1_report.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b/T=1.2/pass1_report.json"]

Pass1_path_list = ["/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeLlama/T=1.0/pass1.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeLlama/T=1.2/pass1.json"]
Pass1_report_path_list = ["/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeLlama/T=1.0/pass1_report.json","/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeLlama/T=1.2/pass1_report.json"]


def clean_code_string(s: str) -> str:
    s = re.sub(r'\\$', r'\\\\', s)
    try:
        return ast.literal_eval(f"'{s}'")
    except Exception:
        s = s.replace("\\n", "\n")
        s = s.replace("\\t", "\t")
        s = s.replace("\\r", "\r")
        s = s.replace("\\\"", "\"")
        s = s.replace("\\'", "'")
        s = s.replace("\\\\", "\\")
        return s

def count_unique_numbers(lst):
    counter = Counter(lst)
    num_categories = len(counter)
    return num_categories, dict(counter)

def pass_at_k(n, c, k):
    if c == 0:
        return 0.0
    if k > n:
        return 1.0
    return 1 - comb(n - c, k) / comb(n, k)
def ensure_code_string(x):
    if isinstance(x, (tuple, list)):
        x = x[0]
    if not isinstance(x, str):
        x = str(x)
    return clean_code_string(x)

def Pass1_test(data_list,Pass1_report_path):
    test_report = []
    pass_1_total = 0
    for i in range(len(data_list)):
        right_num = 0
        report = {}
        sub_data_list = data_list[i]["Answer_list"]
        assert_test = data_list[i]["assert_test"]
        Task_id = data_list[i]["Task_id"]
        main_entry = "if __name__ == \"__main__\":\n    assert_test()"

        report["Task_id"] = Task_id
        report["test_result"] = []
        report["Return_code"] = []
        report["Error_info"] = []
        for j in range(len(sub_data_list)):
            canditate = clean_code_string(sub_data_list[j])
            canditate = ensure_code_string(canditate)
            exec_code = canditate + "\n" + assert_test + "\n" + main_entry
            solution_json = json.dumps({"Canonical_solution": exec_code})
            try:
                process = subprocess.run(
                    [sys.executable, 'execute_solution.py'],
                    input=solution_json.encode('utf-8'),
                    capture_output=True,
                    timeout=60
                )
            except:
                report["test_result"].append("Fail")
                report["Return_code"].append("None")
                report["Error_info"].append("Time out")
                continue

            if process.returncode == 0:
                report["test_result"].append("Pass")
                report["Return_code"].append(0)
                report["Error_info"].append("")
                right_num += 1
            else:
                reture_code = process.returncode
                error_information = process.stderr.decode('utf-8')
                report["test_result"].append("Fail")
                report["Return_code"].append(reture_code)
                report["Error_info"].append(error_information)
        pass_1 = pass_at_k(5, right_num, 1)
        pass_1_total += pass_1
        test_report.append(report)
        with open(Pass1_report_path, "w", encoding="utf-8") as f:
            json.dump(test_report, f)
    return pass_1_total/len(data_list)


if __name__ == "__main__":
    # temperature_list = [0.2, 0.4, 0.6, 0.8, 1.0,1.2]
    temperature_list = [1.0, 1.2]
    for i in range(len(Pass1_path_list)):
        print("Temperature:",temperature_list[i])
        with open(Pass1_path_list[i], "r", encoding="utf-8") as f:
            pass1_data = json.load(f)
        path = Pass1_report_path_list[i]
        pass1 = Pass1_test(data_list = pass1_data,Pass1_report_path = path)
        print(pass1)