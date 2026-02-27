import os
import ast
import json

class Add_Info():
    def __init__(self):
        self.file_path_list = self.get_file_path_list("/home/xiong/ffi/crosspl/PolyBench/FFI_Bench/")
        self.add_class_path = "/home/xiong/ffi/crosspl/prompt_template/FFI/Add_Info_With_Class.txt"
        self.add_func_path = "/home/xiong/ffi/crosspl/prompt_template/FFI/Add_Info_Without_Class.txt"
        self.prompt_with_class = self.get_prompt(self.add_class_path)
        self.prompt_without_class = self.get_prompt(self.add_func_path)

    def get_file_path_list(self,root_dir):
        json_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.lower().endswith(".json"):
                    json_files.append(os.path.join(dirpath, filename))
        return json_files

    def get_prompt(self, code_file_path):
        """Reads the content of a prompt file."""
        with open(code_file_path, "r", encoding="utf-8") as file:
            code = file.read()
        return code

    def extract_classes_and_functions(self,filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            source = json.load(f)
        code = source["Canonical_solution"]
        tree = ast.parse(code)
        classes = []
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                if node.name == "assert_test":
                    continue
                args = [arg.arg for arg in node.args.args]
                functions.append((node.name, args))
        return classes, functions

    def revise_instruction(self,filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            Bench = json.load(f)
        instruction = Bench["Instruction"]
        class_names,functin_names = self.extract_classes_and_functions(filepath)
        if class_names:
            filter_variables = {
                "class_names": class_names,
                "functin_names": functin_names,
            }
            instruction = str(instruction) + str(self.prompt_with_class.format(**filter_variables))
        else:
            filter_variables = {
                "functin_names": functin_names,
            }
            instruction = str(instruction) + str(self.prompt_without_class.format(**filter_variables))

        Bench["Instruction"] = instruction
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(Bench, f, indent=2, ensure_ascii=False)
        print(f"saved: {filepath}")


    def update_json(self):
        for path in self.file_path_list:
            self.revise_instruction(path)

if  __name__ == "__main__":
    add_info = Add_Info()
    add_info.update_json()