# import os
# import re
# import json
# from openai import OpenAI
#
# api_key = ""
# base_url = "https://api.deepseek.com"
#
# class Extract_FFI_Snippets():
#     def __init__(self):
#         # The data in each column read in is stored in the form of a list.
#         self.ffi_path = self.get_source_path()
#         self.main_lang = "Python-C"
#         self.instruction_gen_path = "/home/xiong/ffi/crosspl/prompt_template/FFI/Instruction_Gen.txt"
#         self.instruction_with_error = "/home/xiong/ffi/crosspl/prompt_template/FFI/Instruction_with_error.txt"
#         self.instruction_prompt = self.get_prompt(self.instruction_gen_path)
#         self.prompt_with_error = self.get_prompt(self.instruction_with_error)
#
#     def get_source_path(self, root_dir="/home/xiong/gsl-2.8/"):
#         file_path_list = []
#         for dirpath, dirnames, filenames in os.walk(root_dir):
#             for filename in filenames:
#                 if filename.endswith(".c") and "test" not in filename.lower():
#                     file_path = os.path.join(dirpath, filename)
#                     file_path_list.append(file_path)
#         return file_path_list
#
#     def read_code_without_comments(self, filepath):
#         in_block_comment = False
#         result = ""
#         with open(filepath, "r", encoding="utf-8") as f:
#             for line in f:
#                 raw_line = line.rstrip("\n")
#                 if in_block_comment:
#                     if "*/" in raw_line:
#                         in_block_comment = False
#                     continue
#                 if raw_line.lstrip().startswith("//"):
#                     continue
#                 if "/*" in raw_line:
#                     in_block_comment = True
#                     if raw_line.find("/*") < raw_line.find("*/"):
#                         in_block_comment = False
#                     continue
#                 result += raw_line + "\n"
#         return result
#
#     def get_prompt(self, code_file_path):
#         with open(code_file_path, "r", encoding="utf-8") as file:
#             code = file.read()
#         return code
#
#     def safe_json_parse(self, text):
#         """Attempt to extract JSON from LLM output and parse it"""
#         if not text:
#             return None
#         # Extract content wrapped in ```json ... ```
#         match = re.search(r"```(?:json|python)?\s*(.*?)\s*```", text, re.DOTALL)
#         if match:
#             text = match.group(1).strip()
#         try:
#             return json.loads(text)
#         except json.JSONDecodeError as e:
#             print("JSON parsing failed:", e)
#             print("Original output:", repr(text[:300]), "...")
#             return None
#
#     def FFI_Benchmark_Construction(self):
#         Benchmark = {}
#         Interface_class = "FFI"
#         Task_ID = 1
#
#         for i, path in enumerate(self.ffi_path, start=1):
#             Raw_Code = self.read_code_without_comments(path)
#             Instruction = ""
#             Canonical_solution = ""
#             error_information = ""
#             client = OpenAI(api_key=api_key, base_url=base_url)
#
#             print(f"Task {Task_ID}, source code location {path}")
#             for k in range(5):
#                 print(f"Task {Task_ID}, attempt {k+1}")
#
#                 if k == 0:
#                     filter_variables = {"source_code": Raw_Code}
#                     formatted_extraction_prompt = self.instruction_prompt.format(**filter_variables)
#
#                     response = client.chat.completions.create(
#                         model="deepseek-chat",
#                         messages=[
#                             {"role": "system",
#                              "content": "You are a senior programmer with expertise in cross-language programming. You are particularly skilled in working with various Foreign Function Interfaces."},
#                             {"role": "user", "content": formatted_extraction_prompt},
#                         ],
#                         temperature=0,
#                         top_p=1,
#                         stream=False
#                     )
#                     result = response.choices[0].message.content
#                     result = self.safe_json_parse(result)
#                     print(result)
#                     if not result:
#                         print("Model did not return valid JSON, skipping this file")
#                         break
#
#                     Instruction = result.get("Instruction", "")
#                     # Canonical_solution = result.get("Canonical_solution", "")
#                     Canonical_solution = result["Canonical_solution"].encode('utf-8').decode('unicode_escape')
#
#                 else:  
#                     revise_variables = {
#                         "source_code": Raw_Code,
#                         "Instruction": Instruction,
#                         "Canonical_solution": Canonical_solution,
#                         "error_message": error_information
#                     }
#                     formatted_prompt = self.prompt_with_error.format(**revise_variables)
#
#                     response = client.chat.completions.create(
#                         model="deepseek-chat",
#                         messages=[
#                             {"role": "system",
#                              "content": "You are a senior programmer with expertise in cross-language programming. You are particularly skilled in working with various Foreign Function Interfaces."},
#                             {"role": "user", "content": formatted_prompt},
#                         ],
#                         temperature=0,
#                         top_p=1,
#                         stream=False
#                     )
#                     result = response.choices[0].message.content
#                     result = self.safe_json_parse(result)
#
#                     print(result)
#                     if not result:
#                         print("Still not valid JSON after repair, skipping")
#                         break
#
#                     # Canonical_solution = result.get("Canonical_solution", "")
#                     Canonical_solution = result["Canonical_solution"].encode('utf-8').decode('unicode_escape')
#
#                 # Execute Canonical_solution
#                 try:
#                     exec(Canonical_solution, globals())
#                     Benchmark["Task_id"] = Task_ID
#                     Benchmark["Interface_name"] = Interface_class
#                     Benchmark["Instruction"] = Instruction
#                     Benchmark["Canonical_solution"] = Canonical_solution
#
#                     save_path = f"/home/xiong/ffi/crosspl/PolyBench/FFI_Bench/{Interface_class}_{Task_ID}.json"
#                     with open(save_path, "w", encoding="utf-8") as f:
#                         json.dump(Benchmark, f, indent=2, ensure_ascii=False)
#                         print(f"Success: Result saved to {save_path}")
#                     Task_ID += 1
#                     break
#
#                 except Exception as e:
#                     error_information = str(e)
#                     print("Error executing Canonical_solution:", error_information)
#
# if __name__ == "__main__":
#     ffi = Extract_FFI_Snippets()
#     ffi.FFI_Benchmark_Construction()
import os
import re
import json
import subprocess
import sys
from openai import OpenAI
api_key = ""
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

class Extract_FFI_Snippets():
    """
    Extracts and tests FFI snippets from C source files.
    """

    def __init__(self):
        """Initializes the FFI snippet extraction process."""
        self.ffi_path = self.get_source_path()
        self.main_lang = "Python-C"

        # Prompt templates
        self.instruction_gen_path = "/home/xiong/ffi/crosspl/prompt_template/FFI/Instruction_Gen.txt"
        self.instruction_with_error = "/home/xiong/ffi/crosspl/prompt_template/FFI/Instruction_with_error.txt"
        self.instruction_prompt = self.get_prompt(self.instruction_gen_path)
        self.prompt_with_error = self.get_prompt(self.instruction_with_error)

        # Output directory
        self.output_dir = "/home/xiong/ffi/crosspl/PolyBench/qwen/"

        # Load finished tasks (key for breakpoint resumption)
        self.finished_paths = self.load_finished_paths()

        # Auto compute next Task ID（avoid duplicate IDs）
        self.next_task_id = self.get_next_task_id()

    def get_source_path(self, root_dir="/home/xiong/gsl-2.8/"):
        """Recursively gets all .c files (excluding tests)."""
        file_path_list = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(".c") and "test" not in filename.lower():
                    file_path = os.path.join(dirpath, filename)
                    file_path_list.append(file_path)
        return file_path_list

    def read_code_without_comments(self, filepath):
        """Reads a C file and removes comments."""
        in_block_comment = False
        result = ""
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                raw_line = line.rstrip("\n")
                if in_block_comment:
                    if "*/" in raw_line:
                        in_block_comment = False
                    continue
                if raw_line.lstrip().startswith("//"):
                    continue
                if "/*" in raw_line:
                    in_block_comment = True
                    if raw_line.find("/*") < raw_line.find("*/"):
                        in_block_comment = False
                    continue
                result += raw_line + "\n"
        return result

    def get_prompt(self, code_file_path):
        """Reads the content of a prompt file."""
        with open(code_file_path, "r", encoding="utf-8") as file:
            code = file.read()
        return code

    def safe_json_parse(self, text):
        """Safely extracts and parses JSON from LLM output."""
        if not text:
            return None

        match = re.search(r"```(?:json|python)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", e)
            print("Original output:", repr(text[:300]), "...")
            return None

    def load_finished_paths(self):
        """Scan all generated JSON files and collect finished source_code paths."""
        finished = set()
        if not os.path.exists(self.output_dir):
            return finished

        for fname in os.listdir(self.output_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self.output_dir, fname)

            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    src = data.get("source_code_location", None)
                    if src:
                        finished.add(src)
            except Exception:
                pass

        print(f"Loaded {len(finished)} completed tasks from JSON.")
        return finished

    def get_next_task_id(self):
        """Extract max Task_ID from existing JSON files to continue."""
        max_id = 0

        if not os.path.exists(self.output_dir):
            return 1

        for fname in os.listdir(self.output_dir):
            if fname.startswith("FFI_") and fname.endswith(".json"):
                try:
                    num = int(fname.split("_")[1].split(".")[0])
                    max_id = max(max_id, num)
                except:
                    continue

        return max_id + 1

    def FFI_Benchmark_Construction(self):
        """Constructs the FFI benchmark by extracting, executing, and saving snippets."""
        Interface_class = "FFI"
        Task_ID = self.next_task_id

        for i, path in enumerate(self.ffi_path[919:], start=1):

            # ========== Skip completed tasks (core of breakpoint resumption) ==========
            if path in self.finished_paths:
                print(f"Skipping already completed file: {path}")
                continue

            print(f"\n=====================================")
            print(f"Task {Task_ID}, source code location: {path}")
            print(f"=====================================\n")

            Raw_Code = self.read_code_without_comments(path)
            Instruction = ""
            Canonical_solution = ""
            error_information = ""

            client = OpenAI(api_key=api_key, base_url=base_url)

            for k in range(5):
                print(f"Task {Task_ID}, attempt {k + 1}")

                # ---------- First attempt ----------
                if k == 0:
                    filter_variables = {"source_code": Raw_Code}
                    formatted_extraction_prompt = self.instruction_prompt.format(**filter_variables)

                    try:
                        response = client.chat.completions.create(
                            model="qwen3-4b",
                            messages=[
                                {"role": "system",
                                 "content": "You are a senior programmer with expertise in cross-language programming. You are particularly skilled in working with various Foreign Function Interfaces."},
                                {"role": "user", "content": formatted_extraction_prompt},
                            ],
                            extra_body={"enable_thinking": False},
                            temperature=0,
                            top_p=1,
                            stream=False
                        )
                    except Exception as e:
                        print(f"[Error] Task {Task_ID}, attempt {k + 1} failed: {e}")
                        print("⚠️  Skip this task due to model error.\n")
                        Task_ID += 1
                        break

                    result = self.safe_json_parse(response.choices[0].message.content)
                    print(result)
                    if not result:
                        print("Model did not return valid JSON, skipping this file.")
                        break

                    Instruction = result.get("Instruction", "")
                    Canonical_solution = result.get("Canonical_solution", "")

                    if isinstance(Canonical_solution, str):
                        Canonical_solution = Canonical_solution.encode('utf-8').decode('unicode_escape')

                # ---------- Fix attempt ----------
                else:
                    revise_variables = {
                        "source_code": Raw_Code,
                        "Instruction": Instruction,
                        "Canonical_solution": Canonical_solution,
                        "error_message": error_information
                    }
                    formatted_prompt = self.prompt_with_error.format(**revise_variables)

                    try:
                        response = client.chat.completions.create(
                            model="qwen3-4b",
                            messages=[
                                {"role": "system",
                                 "content": "You are a senior programmer with expertise in cross-language programming."},
                                {"role": "user", "content": formatted_prompt},
                            ],
                            extra_body={"enable_thinking": False},
                            temperature=0,
                            top_p=1,
                            stream=False
                        )
                    except Exception as e:
                        print(f"[Error] Task {Task_ID}, attempt {k + 1} failed: {e}")
                        print("⚠️  Skip this task due to model error.\n")
                        Task_ID += 1
                        break

                    result = self.safe_json_parse(response.choices[0].message.content)
                    print(result)

                    if not result:
                        print("Fix attempt still not valid JSON, skipping.")
                        break

                    Canonical_solution = result.get("Canonical_solution", "")

                    if isinstance(Canonical_solution, str):
                        Canonical_solution = Canonical_solution.encode('utf-8').decode('unicode_escape')

                # ---------- Execute solution ----------
                try:
                    solution_json = json.dumps({"Canonical_solution": Canonical_solution})
                    process = subprocess.run(
                        [sys.executable, 'execute_solution.py'],
                        input=solution_json.encode('utf-8'),
                        capture_output=True,
                        timeout=30
                    )

                    if process.returncode == 0:
                        print("Canonical_solution executed successfully.")

                        Benchmark = {
                            "Task_id": Task_ID,
                            "Interface_name": Interface_class,
                            "Instruction": Instruction,
                            "Canonical_solution": Canonical_solution,
                            "source_code_location": path  # Key field for breakpoint resumption
                        }

                        save_path = f"{self.output_dir}/{Interface_class}_{Task_ID}.json"
                        with open(save_path, "w", encoding="utf-8") as f:
                            json.dump(Benchmark, f, indent=2, ensure_ascii=False)
                            print(f"Success: Result saved to {save_path}")

                        Task_ID += 1
                        break

                    else:
                        error_information = f"Execution failed: {process.stderr.decode('utf-8')}"

                except subprocess.TimeoutExpired:
                    error_information = "Execution timed out."

                except Exception as e:
                    error_information = str(e)


if __name__ == "__main__":
    ffi = Extract_FFI_Snippets()
    ffi.FFI_Benchmark_Construction()