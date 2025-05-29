import os
import re
import json
import copy
from openai import OpenAI
from LangApiAnalyzer import LangApiAnalyzer
api_key = "xxx"
base_url = "xxx"
from math import comb
def pass_at_k(n, c, k):
    if c == 0:
        return 0.0
    if k > n:
        return 1.0
    return 1 - comb(n - c, k) / comb(n, k)

def Match_state (signature,String):
    if re.search(signature, String) != None: # If self.signature matches part of a key string in String, return True.
        return True
    else:
        return False

def Match_FSM(states, result, suffix):
    state_stack = copy.deepcopy(states)
    if not state_stack:
        return False
    lines = result.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        for state in state_stack:
            if not Match_state(state.signature, line):
                continue
            if not state.next:
                return True
            for next_state in state.next:
                if next_state not in state_stack:
                    state_stack.append(next_state)
    return False

class IRI_Gen_test():
    def __init__(self, folder_path="D:\CAE\PolyBench\IPC_Bench\php_ipc"):
        self.folder_path = folder_path

    def get_bench_paths(self, folder_path):
        return [os.path.join(folder_path, fn) for fn in os.listdir(folder_path) if fn.endswith(".json")]

    def read_bench_data(self, json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_json_if_exists(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def run_test(self):
        bench_paths = self.get_bench_paths(self.folder_path)
        CCAnalyzer = LangApiAnalyzer()
        IRIClfList = CCAnalyzer.IRIClfList
        results_path = r"D:\CAE\Test_results\php_ipc\Qwen3-235b-a22b\results_10.json"
        result_list = self.load_json_if_exists(results_path)
        finished_task_ids = {entry["Task_id"] for entry in result_list}

        task_index = 1
        pass_5_total = 0
        pass_3_total = 0
        for path in bench_paths:
            bench_data = self.read_bench_data(path)
            task_id = bench_data["Task_id"]

            if task_id in finished_task_ids:
                print(f"Skipping already processed Task_id: {task_id}")
                task_index += 1
                continue

            FSMID_for_test = bench_data["FSMID_for_test"]
            suffix = bench_data["suffix"]
            print(f"======> Task {task_index} in {self.folder_path}, interface: {bench_data['Interface_name']}, task id: {task_id} <======")

            client = OpenAI(api_key=api_key, base_url=base_url)
            matched_results = []
            unmatched_results = []

            for i in range(10):
                response = client.chat.completions.create(
                    model="qwen3-235b-a22b",
                    messages=[
                        {"role": "system",
                         "content": "You are an advanced programmer specializing in multi-language interaction and inter-process communication. Your task is to output code only. Do not include any explanation, markdown formatting, language tags (e.g., ```php), or phrases like 'Output:', 'PHP code:', or 'Here's the generation code'. Return only the raw code string, with no headers, footers, or comments outside the actual code. The output must be a clean code block that can be parsed or executed directly."
                         },
                        {"role": "user", "content": bench_data["Instruction"]},
                    ],
                    temperature=0.2,
                    top_p=0.95,
                    extra_body={"enable_thinking": False},
                    stream=True
                )
                result = ""
                for chunk in response:
                    content_piece = chunk.choices[0].delta.content
                    if content_piece is not None:
                        result += content_piece

                Clf = IRIClfList[FSMID_for_test]
                States = Clf.States
                is_match = Match_FSM(States, result, suffix)
                if is_match:
                    matched_results.append(result)
                else:
                    unmatched_results.append(result)
            result_dict = {
                "Task_id": task_id,
                "Instruction": bench_data["Instruction"],
                "Canonical_solution": bench_data["Canonical_solution"],
                "Code_level": bench_data["Code_level"],
                "FSMID_for_test": FSMID_for_test,
                "matched_results": matched_results,
                "unmatched_results": unmatched_results,
                "match_count": len(matched_results),
                "pass@3": pass_at_k(10, len(matched_results), 3),
                "pass@5": pass_at_k(10, len(matched_results), 5)
            }
            result_list.append(result_dict)
            print("match_count: {0}".format(len(matched_results)))
            pass_3 = pass_at_k(10, len(matched_results), 3)
            pass_5 = pass_at_k(10, len(matched_results), 5)
            print("pass@3 is {0}".format(pass_3))
            print("pass@5 is {0}".format(pass_5))
            pass_5_total += pass_5
            pass_3_total += pass_3
            with open(results_path, "w", encoding="utf-8") as f:
                json.dump(result_list, f, indent=2, ensure_ascii=False)
            task_index += 1
        return pass_5_total / task_index, pass_3_total / task_index


class IRI_Extract_validation():
    def __init__(self,LLM_result,FSM_ID):
        self.LLM_result = LLM_result
        self.FSM_ID = FSM_ID
    def validation(self,suffix):
        CCAnalyzer = LangApiAnalyzer()
        IRIClfList = CCAnalyzer.IRIClfList
        Clf = IRIClfList[self.FSM_ID]
        States = Clf.States
        IsMatch = Match_FSM(States,self.LLM_result,suffix)
        return IsMatch

if __name__ == "__main__":
    t = IRI_Gen_test()
    macro_pass_5,macro_pass_3 = t.run_test()
    print(macro_pass_5,macro_pass_3)

