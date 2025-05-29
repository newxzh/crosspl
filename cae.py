import os
import sys
import pandas as pd
from Config import Config
from CloneRepo import Clone_Repo
from LangCrawler import LangCrawler
from Evaluation import IRI_Gen_test
from Extraction_and_Benchmark_Construction import Extract_IRI_Snippets
# from Extraction_GPT import Extract_IRI_Snippets
# Get the current working directory
BaseDir = os.getcwd()
# Get hyperparameter information
CFG = Config ()
CFG.LoadCfg ()
username = CFG.Get("UserName")
usertoken = CFG.Get("Token")
clone_repo = Clone_Repo(username,usertoken)
def Daemonize():
    pid = os.fork()
    if pid:
        sys.exit(0)
    #os.chdir('/')
    os.umask(0)
    os.setsid()
    _pid = os.fork()
    if _pid:
        sys.exit(0)
    sys.stdout.flush()
    sys.stderr.flush()
def Action(act):
    if act == "crawler":
        """
        
        Goals of crawler:
        
            Crawl relevant information of multi-programming language projects on Github: Id, Name, Star, MainLang, Langs, ApiUrl, CloneUrl, Topics, Description, Created, Pushed, where:
            (1) ID (Project ID on Github)
            (2) Name (Project name on Github)
            (3) Star (Number of stars on the Github project)
            (4) MainLang (The programming language with the most lines of code in the project, referred to as the main language)
            (5) Langs (All programming languages used in the Github project)
            (6) ApiUrl (API URL of the Github project: This URL includes commit history, branch information, issue tracking, and release information)
            (7) CloneUrl (Clone URL of the Github project: This URL allows the project to be cloned locally)
            (8) Topics (Topics of the Github project)
            (9) Description (Description of the Github project)
            (10) Created (Creation time of the Github project)
            (11) Pushed (The time of the last upload/update of the Github project)
            
        """
        Cl = LangCrawler()
        Cl.Grab ()
    if act == "Clone_to_Local":
        """
        
        Goals of Clone_to_Local:
        
            Step1:
                Through crawler operations, relevant information of Github multi-programming language projects that meet the requirements: 
                    (1) star count between 1000 and 30000; 
                    (2) programming language count between 2 and 5
                    
            Step2:
                Save Information to RepositoryList.csv;
                
            Step3:
                Based on the clone URLs in RepositoryList.csv, all the multi-programming language projects that meet the requirements were cloned locally. 
            All projects are saved under the Repository folder, with each project named as: "Name_ID" (Project Name_Project ID).
            
        """
        RepoList_path = BaseDir+"//RepositoryList.csv"
        RepoData = pd.read_csv(RepoList_path, encoding='latin-1')
        RepoData_name = RepoData["Name"].tolist()
        RepoData_id = RepoData["Id"].tolist()
        RepoData_url = RepoData["CloneUrl"].tolist()
        Local_dir = BaseDir+"//Repository"
        for index in range(len(RepoData_url)):
        # for index in range(5000):
            local_path = Local_dir+f"//{RepoData_name[index]}_{RepoData_id[index]}"
            if not os.path.exists(local_path):
                os.mkdir(local_path)
            clone_repo.clone(f"{RepoData_url[index]}",local_path)
    if act == "Interoperability_Analysis":
        """
        
        Goals of Interoperability_Analysis:
        
        Step1 (PolyFax's work):
            Based on the finite state machine method proposed in Refs. [1-2], 
            analyze all the projects cloned locally to determine the multi-language interoperability technologies used in the projects.
            (1) "FFI"  # Foreign Function invocation
            (2) "IMI"  # Indirect remote-invocation
            (3) "EBD"  # inter-dependence
            (4) "HIT"  # Hidden interaction
            
        Step2 (Our Improvement):
            (1) Enrich the types of interactions between multiple programming languages (to avoid underreporting),
            (2) Enrich the steps of interactions between multiple programming languages (to avoid false reporting).
            (3) Use above information to assist the LLM in extracting code snippets related to multi-language interoperability from multi-programming language projects.
            
        Rederences:
            [1] Li, Wen, Li Li, and Haipeng Cai. "PolyFax: A toolkit for characterizing multi-language software." Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering. 2022.
            [2] Li, Wen, Li Li, and Haipeng Cai. "On the vulnerability proneness of multilingual code." Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering. 2022.
            [3] Li, Wen, et al. "{PolyFuzz}: Holistic Greybox Fuzzing of {Multi-Language} Systems." 32nd USENIX Security Symposium (USENIX Security 23). 2023.
            [4] Shi, Qingkai, et al. "Datalog-Based Language-Agnostic Change Impact Analysis for Microservices." 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE). IEEE Computer Society, 2025.
            [5] Li, Wen, et al. "How are multilingual systems constructed: Characterizing language use and selection in open-source multilingual software." ACM Transactions on Software Engineering and Methodology 33.3 (2024): 1-46.
            [6] Yang, Haoran, Wen Li, and Haipeng Cai. "Language-agnostic dynamic analysis of multilingual code: Promises, pitfalls, and prospects." Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering. 2022.
            [7] Li, Wen, et al. "{PolyCruise}: A {Cross-Language} dynamic information flow analysis." 31st USENIX Security Symposium (USENIX Security 22). 2022.
            
        """
        from LangApiAnalyzer import LangApiAnalyzer
        CCAnalyzer = LangApiAnalyzer()
        CCAnalyzer.StartRun()
    if act == "Construct_Benchmark":
        """
        Step 1:
        Based on the information provided in Interoperability_Analysis, 
        use the LLM + few-shots approach to extract code snippets related to multi-language interoperability from multi-programming language projects.
        
        Rederences:
        [1] Zhu Q, Cao J, Lu Y, et al. DOMAINEVAL: An Auto-Constructed Benchmark for Multi-Domain Code Generation. AAAI 2025
        
        Step 2:
        Given the canonical solution of the code, use the LLM to summarize the canonical solution and generate a prompt. 
        This prompt will be used to instruct other LLMs to generate the canonical solution.
        
        """
        extract_iri = Extract_IRI_Snippets()
        extract_iri.IRI_Benchmark_Construction()
    if act == "Test":
        """
    
        metrics:
            (1) Generate test cases with canonical  solution using LLM
            (2) FSM (The generated code must conform to the state transition rules of the FSM)
        
        """
        iri_path = "D:\CAE\PolyBench\IPC_Bench\java_ipc"
        iri_gen_test = IRI_Gen_test(iri_path)
        iri_gen_test.run_test()

if __name__ == "__main__":
    # Step 1: Crawler
    # Action("crawler")

    # Step 2: Clone to Local
    # Action("Clone_to_Local")

    # Step 3: Interoperability analysis
    # Action("Interoperability_Analysis")

    # Step 4: Construct_Benchmark(Extract interoperability snippets & Instruction Generation)
    # Action("Construct_Benchmark")

    # Step 5: Test
    Action("Test")