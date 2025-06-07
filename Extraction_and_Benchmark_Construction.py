import re
import os
import csv
import json
import pandas as pd
from openai import OpenAI
from Evaluation import IRI_Extract_validation
api_key = "your_apikey"
base_url = "base_url"

Example_func_path = "D:\CAE\Splited_Repository\\1\BookReader_64817102\\app\src\main\java\com\justwayward\\reader\wifitransfer\\NanoHTTPD.java"

Example_extract_func_path = "D:\CAE\Reference_Extract_Code\Java_IPC\\reference_extract_func.txt"

Example_class_path = "D:\CAE\Splited_Repository\8\SpringBoot-Labs_148496687\lab-25\lab-websocket-25-01\src\main\java\cn\iocoder\springboot\lab25\springwebsocket\websocket\WebsocketServerEndpoint.java"

Example_extract_class_path = "D:\CAE\Reference_Extract_Code\Java_IPC\\reference_extract_class.txt"

with open("D:\CAE\prompt_template\Java_IPC\\function_extraction_prompt_template.txt", "r", encoding="utf-8") as file:
    function_extraction_prompt = file.read()

with open("D:\CAE\prompt_template\Java_IPC\class_extraction_prompt_template.txt", "r", encoding="utf-8") as file:
    class_extraction_prompt = file.read()

with open("D:\CAE\prompt_template\Java_IPC\Fliter_prompt_template.txt", "r", encoding="utf-8") as file:
    filter_prompt = file.read()

with open("D:\CAE\prompt_template\Java_IPC\Instruction_Generation_prompt_template.txt", "r", encoding="utf-8") as file:
    Instruction_Generation_prompt = file.read()


class Extract_IRI_Snippets():
    def __init__(self):
        # The data in each column read in is stored in the form of a list.
        self.iri_path = pd.read_csv("D:\CAE\Repo_Info\Info_IRI_java_filtered.csv")["File_path"].tolist()
        self.main_lang = pd.read_csv("D:\CAE\Repo_Info\Info_IRI_java_filtered.csv")["Interface_class"].tolist()
        self.interface_name = pd.read_csv("D:\CAE\Repo_Info\Info_IRI_java_filtered.csv")["Interface_name"].tolist()
        self.steps =  pd.read_csv("D:\CAE\Repo_Info\Info_IRI_java_filtered.csv")["Status_description"].tolist()
        self.fsm_id = pd.read_csv("D:\CAE\Repo_Info\Info_IRI_java_filtered.csv")["Classfier_ID"].tolist()

    def read_code_file(self,code_file_path):
        with open(code_file_path,"r",encoding="utf-8") as file:
            code = file.read()
        return code

    def get_refer_rawcode(self,erp,eep):
        with open(erp,"r", encoding="utf-8") as file:
            Example_raw_code = file.read()
        with open(eep, "r", encoding="utf-8") as file:
            Example_extract_code = file.read()
        return Example_raw_code,Example_extract_code

    def extract_folder_info(self,path):
        match = re.search(r'\\([^\\]+)_(\d+)\\', path)
        return match.groups() if match else (None, None)

    def write_to_csv(self,save_path, file_name,ipc_name,spnippet_level, count,Extracted):
        try:
            with open(save_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(['File_Name','IPC_Name','Snippet_Level','Count'])
                writer.writerow([file_name,ipc_name,spnippet_level, count, Extracted])
        except Exception as e:
            print(f"Error writing to file: {e}")

    def IRI_Benchmark_Construction(self):
        Benchmark = {}
        Interface_class = "IPC"
        Reference_raw_func,Reference_extract_func = self.get_refer_rawcode(Example_func_path,Example_extract_func_path)
        Reference_raw_class, Reference_extract_class = self.get_refer_rawcode(Example_class_path,Example_extract_class_path)
        Task_ID = 536
        for i in range(0,len(self.fsm_id)):
            FSM_ID = self.fsm_id[i]
            path = self.iri_path[i]
            suffix = os.path.splitext(path)[-1].lower()
            Github_ID = self.extract_folder_info(path)[1]
            Github_Project_Name = self.extract_folder_info(path)[0]
            PL = self.main_lang[i][:-1]
            IPC_Name = self.interface_name[i]
            Steps = self.steps[i]
            Iter_conut = 0
            Extrated = "Fail"
            with open(path,"r", encoding="utf-8", errors="ignore") as file:
                Original_code = file.read()

            filter_variables = {
                "Original_code":Original_code,
                "PL": PL,
                "IPC_Name": IPC_Name,
                "Steps": Steps
            }
            formatted_extraction_prompt = filter_prompt.format(**filter_variables)

            client = OpenAI(api_key=api_key, base_url=base_url)

            filter_response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system",
                     "content": "You are an advanced programmer who focuses on multi-language interaction and inter-process communication technology"},
                    {"role": "user", "content": formatted_extraction_prompt},
                ],
                temperature = 0,
                top_p = 1,
                stream=False
            )
            fliter_information = filter_response.choices[0].message.content
            print(fliter_information)
            if fliter_information == "null":
                print("Skip the {}-th task in the table, whose file name is {}".format(i + 883, os.path.splitext(os.path.basename(path))[0]))
                continue
            if fliter_information == "Function-level":
                extraction_variables = {
                    "function/class-level": fliter_information,
                    "Reference_raw_code": Reference_raw_func,
                    "Reference_function_level_code": Reference_extract_func,
                    "Original_code": Original_code,
                    "PL": PL,
                    "IPC_Name": IPC_Name,
                    "Steps": Steps
                }
                formatted_extraction_prompt = function_extraction_prompt.format(**extraction_variables)
            if fliter_information == "Class-level":
                extraction_variables = {
                    "function/class-level": fliter_information,
                    "Reference_raw_code": Reference_raw_class,
                    "Reference_class_level_code": Reference_extract_class,
                    "Original_code": Original_code,
                    "PL": PL,
                    "IPC_Name": IPC_Name,
                    "Steps": Steps
                }
                formatted_extraction_prompt = class_extraction_prompt.format(**extraction_variables)
            for k in range(6):
                Iter_conut = Iter_conut +1
                extraction_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "You are an advanced programmer who focuses on multi-language interaction and inter-process communication technology"},
                        {"role": "user", "content": formatted_extraction_prompt},
                    ],
                    temperature = 0 + 0.1*k,
                    top_p = 1,
                    stream=False
                )
                Canonical_solution = extraction_response.choices[0].message.content

                if not IRI_Extract_validation(Canonical_solution,FSM_ID).validation(suffix):
                    print("{0}-th Failure".format(k+1))
                    continue
                else:
                    instruction_generation_variables = {
                        "PL": PL,
                        "IPC_Name": IPC_Name,
                        "Steps": Steps,
                        "Canonical_solution": Canonical_solution,
                    }
                    formatted_instruction_generation_prompt = Instruction_Generation_prompt.format(
                        **instruction_generation_variables)

                    instruction_generation_response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system",
                             "content": "You are an advanced programmer who focuses on multi-language interaction and inter-process communication technology"},
                            {"role": "user", "content": formatted_instruction_generation_prompt},
                        ],
                        temperature=0.1,
                        top_p=0.95,
                        stream=False
                    )

                    Instruction = instruction_generation_response.choices[0].message.content
                    Benchmark["Task_id"] = Task_ID
                    Benchmark["Github_ID"] = Github_ID
                    Benchmark["Github_Project_Name"] = Github_Project_Name
                    Benchmark["Programming_Language"] = PL
                    Benchmark["suffix"] = suffix
                    Benchmark["Interface_class"] = Interface_class
                    Benchmark["Interface_name"] = IPC_Name
                    Benchmark["Instruction"] = Instruction
                    Benchmark["Canonical_solution"] = Canonical_solution
                    Benchmark["FSMID_for_test"] = FSM_ID
                    Benchmark["Code_level"] = fliter_information

                    with open("D:\CAE\PolyBench\IPC_Bench\java_ipc\{}_{}.json".format(Interface_class,Task_ID), "w") as f:
                        json.dump(Benchmark, f, indent=2)
                        print("json data have saved in D:\CAE\PolyBench\IPC_Bench\java_ipc\{}_{}.json".format(Interface_class,Task_ID))
                    Task_ID += 1
                    Extrated = "Success"
                    break
            self.write_to_csv('Static_java.csv',os.path.splitext(os.path.basename(path))[0],fliter_information,IPC_Name,Iter_conut,Extrated)
