import os
import re
import json
import copy
import matplotlib.pyplot as plt
from code_preprocess import skip_note
from LangApiAnalyzer import LangApiAnalyzer

def Match_state (signature,String):
    if re.search(signature, String) != None: # If self.signature matches part of a key string in String, return True.
        return True
    else:
        return False

def Match_FSM(States, result, suffix):
    flag = 0
    StateStack = copy.deepcopy(States)
    if len(StateStack) == 0:
        return False, 0, "None", 0  # 返回0作为长度，表示没有匹配成功
    lines = result.split('\n')

    last_matched_index = 0  # 记录最后匹配到的 state 的索引 +1
    stop_index = 1
    signature = ""

    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith("/*") or line.endswith("*/"):
            flag += 1
        if line.startswith("'''") or line.endswith("'''"):
            flag += 1
        if line.startswith('"""') or line.endswith('"""'):
            flag += 1
        if line.startswith("<!--") or line.endswith("-->"):
            flag += 1
        if skip_note(line, suffix, flag):
            continue

        for idx, state in enumerate(StateStack):
            isMatch = Match_state(state.signature, line)
            if not isMatch:
                stop_index = idx
                signature = state.signature
                continue

            if len(state.next) == 0:
                return True, idx, signature

            for next in state.next:
                if next not in StateStack:
                    StateStack.append(next)

    return False, stop_index, signature


def total(States):
    StateStack = copy.deepcopy(States)
    length = 0
    for idx, state in enumerate(StateStack):
        if len(state.next) == 0:
            length = idx + 1
            return length
        for next in state.next:
            if next not in StateStack:
                StateStack.append(next)

    return length

class IRI_Gen_test():
    def __init__(self,folder_path = "D:\CAE\PolyBench\IPC_Bench\java_ipc"):
        self.folder_path = folder_path

    def get_bench_paths(self,folder_path):
        bench_paths = []
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                bench_paths.append(file_path)
        return bench_paths

    def read_bench_data(self,json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            bench_data = json.load(f)
        return bench_data

    def load_json_if_exists(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def run_test(self):
        CCAnalyzer = LangApiAnalyzer()
        IRIClfList = CCAnalyzer.IRIClfList
        wrong_path = r"D:\crosspl\Test_results\c++_ipc\GPT-4o-mini\greedy_fail.json"
        right_path = r"D:\crosspl\Test_results\c++_ipc\GPT-4o-mini\greedy_pass.json"
        wrong_list = self.load_json_if_exists(wrong_path)
        print(wrong_list)
        right_list = self.load_json_if_exists(right_path)
        answer_list = right_list+wrong_list
        stop_list = []
        total_list = []
        FSM_ID = []
        for i in range(len(answer_list)):
            if i+1 <=len(right_list):
                test_result = answer_list[i]["right_result"]
            else:
                test_result = answer_list[i]["wrong_result"]
            FSMID_for_test = answer_list[i]["FSMID_for_test"]
            suffix = ".cpp"

            Clf = IRIClfList[FSMID_for_test]
            States = Clf.States
            length = total(States)
            IsMatch, last_idx, sig = Match_FSM(States, test_result, suffix)
            stop_list.append(last_idx)
            total_list.append(length)
            FSM_ID.append(FSMID_for_test)
        return stop_list,total_list,FSM_ID


if __name__ == "__main__":
    t = IRI_Gen_test()
    stop_length,total_length,fsm_id = t.run_test()
    x = fsm_id
    plt.figure(figsize=(8, 5))
    plt.scatter(x, stop_length, label="Stopped State ID of the FSM's State Chain", linewidth=2, marker='o', alpha=0.7)
    plt.scatter(x, total_length, label="FSM's State Chain Length", linewidth=2, marker='s', alpha=0.7)

    plt.xlabel("FSM ID", fontsize=10)
    plt.ylabel("State Chain Length", fontsize=10)
    plt.legend(loc="upper left", fontsize=10)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.savefig("D:\crosspl\ipc_error\GPT-4o-error-C++.pdf", format='pdf',bbox_inches='tight')
    plt.show()
    mean_mis = sum(stop_length) / len(stop_length)
    mean_total = sum(total_length) / len(total_length)

    print(mean_mis)
    print(mean_total)


