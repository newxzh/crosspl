import re
import ast
import sys
import json
import subprocess
from math import comb
from collections import Counter
Greedy_path = "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-235b/think.json"
report_path = "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-235b/think_report.json"

Pass5_path = "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-32b/pass5.json"
Pass5_report_path = "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-32b/pass5_report.json"


with open(Greedy_path, "r", encoding="utf-8") as f:
    greedy_data = json.load(f)

with open(Pass5_path, "r", encoding="utf-8") as f:
    pass5_data = json.load(f)


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

def Greedy_test(data_list):
    right_num = 0
    wrong_num = 0
    test_report = []
    for i in range(len(data_list)):
        report = {}
        canditate = clean_code_string(greedy_data[i]["Greedy_Answer"])
        assert_test = greedy_data[i]["assert_test"]
        Task_id = greedy_data[i]["Task_id"]
        main_entry = "if __name__ == \"__main__\":\n    assert_test()"
        exec_code = canditate+"\n"+assert_test+"\n"+main_entry
        solution_json = json.dumps({"Canonical_solution": exec_code})
        try:
            process = subprocess.run(
                [sys.executable, 'execute_solution.py'],
                input=solution_json.encode('utf-8'),
                capture_output=True,
                timeout=60
            )
        except:
            report["Task_id"] = Task_id
            report["test_result"] = "Fail"
            report["Return_code"] = "None"
            report["Error_info"] = "Time out"
            wrong_num += 1
            continue

        if process.returncode == 0:
            report["Task_id"] = Task_id
            report["test_result"] = "Pass"
            report["Return_code"] = 0
            report["Error_info"] = ""
            right_num += 1
        else:
            reture_code = process.returncode
            error_information = process.stderr.decode('utf-8')
            report["Task_id"] = Task_id
            report["test_result"] = "Fail"
            report["Return_code"] = reture_code
            report["Error_info"] = error_information
            wrong_num += 1
        test_report.append(report)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(test_report, f)
    print(right_num/(right_num+wrong_num))


def Get_return_code():
    with open(report_path, "r", encoding="utf-8") as f:
        report_data = json.load(f)
    return_code_list = []
    for i in range(len(report_data)):
        return_code_list.append(report_data[i]["Return_code"])
    return return_code_list

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


def Pass5_test(data_list):
    test_report = []
    pass_5_total = 0
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
        pass_5 = pass_at_k(10, right_num, 5)
        pass_5_total += pass_5
        test_report.append(report)
        with open(Pass5_report_path, "w", encoding="utf-8") as f:
            json.dump(test_report, f)
    return pass_5_total/len(data_list)


if __name__ == "__main__":
    # Greedy test
    # Greedy_test(data_list = greedy_data)
    # return_code_list = Get_return_code()
    # class_num,freq_num = count_unique_numbers(return_code_list)
    # print(class_num,freq_num)
    # Pass@5 test
    pass5 = Pass5_test(data_list = pass5_data)
    print(pass5)





