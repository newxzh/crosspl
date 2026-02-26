import os
import json

model_dirs = ["GPT-4o","GPT-4o-mini","Gemini-1.5-pro","GLM4-plus","DS-V3","Qwen3-235b-a22b","Qwen3-32b",
              "Qwen3-30b-a3b","Qwen3-14b","Qwen3-8b","Qwen3-4b","GLM4-9b","CodeGeeX","Qwen2.5-coder-32b-instruct",
              "Qwen2.5-coder-14b-instruct","Qwen2.5-coder-7b-instruct","codegemma","codellama-7b","gemma2","llama3-8b"]

languages = ["c++_ipc", "go_ipc", "java_ipc", "js_ipc", "php_ipc", "python_ipc"]

class IRI_Gen_test():

    def load_json_if_exists(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def run_test(self):
        for model in model_dirs:
            print("\n==============================")
            print(f"Model: {model}")
            print("==============================")

            wrong_num_before2022 = 0
            right_num_before2022 = 0

            wrong_num_2022 = 0
            right_num_2022 = 0

            wrong_num_2023 = 0
            right_num_2023 = 0

            wrong_num_2024_2025 = 0
            right_num_2024_2025 = 0

            for lang in languages:

                base_dir = rf"/home/xiong/ffi/crosspl/Test_results/{lang}/{model}"
                if model in ["Qwen3-4b","Qwen3-8b","Qwen3-14b","Qwen3-30b-a3b","Qwen3-32b","Qwen3-235b-a22b"]:
                    wrong_path = os.path.join(base_dir, "greedy_fail_nonethink.json")
                    right_path = os.path.join(base_dir, "greedy_pass_nonethink.json")
                else:
                    wrong_path = os.path.join(base_dir, "greedy_fail.json")
                    right_path = os.path.join(base_dir, "greedy_pass.json")

                wrong_list = self.load_json_if_exists(wrong_path)
                right_list = self.load_json_if_exists(right_path)

                # ---- process wrong results ----
                for item in wrong_list:
                    year = item.get("Year", "")
                    if year == "2022":
                        wrong_num_2022 += 1
                    elif year == "2023":
                        wrong_num_2023 += 1
                    elif year in ("2024", "2025"):
                        wrong_num_2024_2025 += 1
                    else:
                        wrong_num_before2022 += 1

                # ---- process right results ----
                for item in right_list:
                    year = item.get("Year", "")
                    if year == "2022":
                        right_num_2022 += 1
                    elif year == "2023":
                        right_num_2023 += 1
                    elif year in ("2024", "2025"):
                        right_num_2024_2025 += 1
                    else:
                        right_num_before2022 += 1

            # ---- output pass rates ----
            def rate(r, w):
                return r / (r + w) if (r + w) > 0 else 0.0
            print("total before 2022:", right_num_before2022 + wrong_num_before2022)
            print("total 2022:", right_num_2022 + wrong_num_2022)
            print("total 2023:", right_num_2023 + wrong_num_2023)
            print("total 2024-2025:", right_num_2024_2025 + wrong_num_2024_2025)
            print("Pass rate before 2022:", rate(right_num_before2022, wrong_num_before2022))
            print("Pass rate 2022:", rate(right_num_2022, wrong_num_2022))
            print("Pass rate 2023:", rate(right_num_2023, wrong_num_2023))
            print("Pass rate 2024-2025:", rate(right_num_2024_2025, wrong_num_2024_2025))


if __name__ == "__main__":
    t = IRI_Gen_test()
    t.run_test()
