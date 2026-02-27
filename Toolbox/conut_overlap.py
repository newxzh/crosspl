import os
import ast
import json
import re

def extract_names_from_code(code_str):
    func_names = []
    class_names = []
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                class_names.append(node.name)
    except Exception:
        pass
    return func_names, class_names



py_root = "/home/xiong/ffi/crosspl/pygsl-main/"

Func_list = []
Class_list = []

for dirpath, _, filenames in os.walk(py_root):
    for filename in filenames:
        if filename.endswith(".py"):
            py_path = os.path.join(dirpath, filename)
            try:
                with open(py_path, "r", encoding="utf-8") as f:
                    code = f.read()
                funcs, classes = extract_names_from_code(code)
                Func_list.extend(funcs)
                Class_list.extend(classes)
            except Exception:
                continue


json_root = "/home/xiong/ffi/crosspl/PolyBench/FFI_Bench/"

Func_list_json = []
Class_list_json = []

func_pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
class_pattern = re.compile(r"class\s+([A-Za-z_][A-Za-z0-9_]*)\s*:", re.MULTILINE)

for dirpath, _, filenames in os.walk(json_root):
    for filename in filenames:
        if filename.endswith(".json"):
            json_path = os.path.join(dirpath, filename)
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "Canonical_solution" in data:
                    code_str = data["Canonical_solution"]

                    funcs, classes = extract_names_from_code(code_str)
                    funcs += func_pattern.findall(code_str)
                    classes += class_pattern.findall(code_str)

                    Func_list_json.extend(funcs)
                    Class_list_json.extend(classes)

            except Exception:
                continue

same_funcs = set(Func_list) & set(Func_list_json)
same_classes = set(Class_list) & set(Class_list_json)

print("Number of functions in Python file:", len(Func_list))
print("Number of functions in JSON:", len(Func_list_json))
print("Number of functions with the same name:", len(same_funcs))
print("List of functions with the same name:", same_funcs)

print("\nNumber of classes in Python file:", len(Class_list))
print("Number of classes in JSON:", len(Class_list_json))
print("Number of classes with the same name:", len(same_classes))
print("List of classes with the same name:", same_classes)