import os
import re
import json
import copy
from math import comb
from openai import OpenAI
from zhipuai import ZhipuAI
from code_preprocess import skip_note
from LangApiAnalyzer import LangApiAnalyzer

api_key = "xxxxx"

def Match_state (signature,String):
    if re.search(signature, String) != None: # If self.signature matches part of a key string in String, return True.
        return True
    else:
        return False

def Match_FSM (States, result,suffix):
    flag = 0
    StateStack = copy.deepcopy(States)
    if len (StateStack) == 0:
        return False
    lines = result.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue

        for state in StateStack:
            isMatch = Match_state(state.signature,line)
            if isMatch == False:
                continue
            if len (state.next) == 0:
                return True
            for next in state.next:
                if next not in StateStack:
                    StateStack.append (next)
    return False

def pass_at_k(n, c, k):
    if c == 0:
        return 0.0
    if k > n:
        return 1.0 if c > 0 else 0.0
    return 1.0 - (comb(n - c, k) / comb(n, k))

class IRI_Gen_test():
    def __init__(self,folder_path = "D:\CrossPL\PolyBench\IPC_Bench\php_ipc"):
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
        bench_paths = self.get_bench_paths(self.folder_path)
        CCAnalyzer = LangApiAnalyzer()
        IRIClfList = CCAnalyzer.IRIClfList
        pass_num = 0
        task_k = 1

        right_path = r"D:\CrossPL\Test_results\php_ipc\CcodeGeeX\greedy_pass.json"
        wrong_path = r"D:\CrossPL\Test_results\php_ipc\CcodeGeeX\greedy_fail.json"

        right_list = self.load_json_if_exists(right_path)
        wrong_list = self.load_json_if_exists(wrong_path)

        finished_task_ids = {entry["Task_id"] for entry in right_list + wrong_list}

        for path in bench_paths:
            bench_data = self.read_bench_data(path)
            task_id = bench_data["Task_id"]

            if task_id in finished_task_ids:
                print(f"Skipping already processed Task_id: {task_id}")
                task_k += 1
                continue

            FSMID_for_test = bench_data["FSMID_for_test"]
            suffix = bench_data["suffix"]

            print(f"======> Task {task_k} in {self.folder_path}, interface: {bench_data['Interface_name']}, task id: {task_id} <======")

            client = ZhipuAI(api_key=api_key)
            response = client.chat.completions.create(
                model="codegeex-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an advanced programmer specializing in multi-language interaction and inter-process communication. Your task is to output code only. Do not include any explanation, markdown formatting, language tags (e.g., ```php, <?php, ```), or phrases like 'Output:', 'PHP code:', or 'Here's the generation code'. Return only the raw code string, with no headers, footers, or comments outside the actual code. The output must be a clean code block that can be parsed or executed directly."
                    },
                    {
                        "role": "user",
                        "content": bench_data["Instruction"]
                    }
                ],
                temperature=0,
                max_tokens=32*1024,
                stop=["<|endoftext|>", "<|user|>", "<|assistant|>", "<|observation|>"]
            )
            LLM_result = response.choices[0].message.content
            Clf = IRIClfList[FSMID_for_test]
            States = Clf.States
            IsMatch = Match_FSM(States, LLM_result, suffix)

            result_dict = {
                "Task_id": task_id,
                "Instruction": bench_data["Instruction"],
                "Canonical_solution": bench_data["Canonical_solution"],
                "Code_level": bench_data["Code_level"],
                "FSMID_for_test": FSMID_for_test,
            }

            if IsMatch:
                print("This task is Pass")
                pass_num += 1
                result_dict["right_result"] = LLM_result
                right_list.append(result_dict)
            else:
                print("This task is Fail")
                result_dict["wrong_result"] = LLM_result
                wrong_list.append(result_dict)

            with open(right_path, "w") as f:
                json.dump(right_list, f, indent=2)

            with open(wrong_path, "w") as f:
                json.dump(wrong_list, f, indent=2)

            task_k += 1

        pass_rate = (pass_num / len(bench_paths)) * 100
        return pass_rate



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
    pass_1 = t.run_test()
    print(pass_1)

