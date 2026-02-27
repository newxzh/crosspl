# CrossPL: CrossPL: Systematic Evaluation of Large Language Models for Cross Programming Language Interoperating Code Generation

**CrossPL** is the first benchmark for systematically assessing LLM performance of **cross-programming language (CPL)** code generation across two primary interoperation modes and 2534 tasks, specifically 1,982 **Inter-Process Communication (IPC)** tasks spanning six languages and 522 Python–C **Foreign Function Interface(FFI)** tasks.

---
## Table of Contents

- [Why CrossPL? (Motivation)](#why-crosspl-motivation)
- [Our Contributions](#our-contributions)
- [Benchmark Construction Workflow](#benchmark-construction-workflow)
- [Statistics of *CrossPL*](#statistics-of-crosspl)
- [Key Findings](#key-findings)
  
---

## Why CrossPL? (Motivation)

Modern software systems are inherently **multi-language**—over 80% of real-world projects use two or more programming languages to combine complementary strengths (e.g., Python for productivity, C/C++ for performance).

Existing LLM benchmarks focus on:
- Single-language code generation  
- Cross-language code translation  

They **do not evaluate** whether models can generate *interoperating code* that enables real cross-language collaboration.

In practice, cross-language systems rely on two core mechanisms:

- **IPC (Inter-Process Communication):** protocol compliance, serialization, synchronization, and correct state transitions  
- **FFI (Foreign Function Interface):** function signatures, type conversion, and memory management  

These scenarios require correctness beyond syntax—errors can cause deadlocks, crashes, or undefined behavior.

**CrossPL** addresses this gap by systematically evaluating LLMs’ ability to generate correct and executable cross-language interoperating code across IPC and FFI settings.
<div align="center">
  <img src="https://github.com/user-attachments/assets/bd5160b2-b642-4d74-bd2d-33d93169b84b" alt="ipc demo" width="900"/><br>
  <h4><b>Figure 1:</b> Examples of CPL interoperating (IPC and FFI).</h4>
</div>

---

## Our Contributions

### 1. CrossPL Benchmark

- We introduce **CrossPL**, the first benchmark specifically designed to evaluate LLMs’ ability to generate **cross-programming-language (CPL) interoperating code** involving both IPC and FFI.
- The benchmark contains **2,534 tasks** in total:
  - **IPC subset:** 1,982 tasks spanning six programming languages  
  - **FFI subset:** 522 Python–C interoperability tasks  

### 2. Automated Benchmark Construction Methodology

We propose a unified and automated construction framework that combines **FSM-based IPC interface characterization** with **LLM-driven workflows**.

- **FSM-based IPC modeling**
  - Designed **156 finite state machines (FSMs)** based on official CPL interface specifications.
  - Formally characterize IPC interaction patterns.
  - Enable automatic detection and extraction of IPC snippets from real-world GitHub repositories.
  - Serve as structured evaluators for protocol compliance and state-transition coverage.

- **Two LLM-based construction pipelines**
  - **CrossPL-IPC pipeline:**  
     FSM-guided snippet identification → LLM-based Judgement → Code extraction → FSM-based validation → Instruction generation → Human check → performance evaluation.
  - **CrossPL-FFI pipeline:**  
     Focused Python–C task construction with controlled compilation environments and assertion-based testing for functional correctness.

### 3. Large-scale Empirical Study

- Evaluated **20 representative LLMs** on CrossPL.
- Systematically investigated whether current LLMs can accurately generate **cross-language interoperating code**.
- Revealed substantial performance gaps compared to single-language code generation benchmarks.
- Demonstrated that CPL interoperability remains a significantly underexplored and challenging capability for modern LLMs.

---

## Benchmark Construction Workflow
<div align="center">
  <img src="https://github.com/user-attachments/assets/93031460-b30e-4e58-b5ae-7468c86d4f44" alt="framework" width="900"/><br>
  <h4><b>Figure 2:</b> Framework for CPL Interoperating Code Analysis, Extraction, Generation and Evaluation.</h4>
</div>

CrossPL is constructed using two LLM-driven workflow, including **CrossPL-IPC** workflow and **CrossPL-FFI** workflow.

---

### CrossPL-IPC Construction Workflow
⚠️ **Note:** The following prompt templates for **Judger**, **Function Extractor**, and **Class Extractor** are exemplified using Java. Prompt templates for other programming languages can be found in the `prompt_template` directory of the project.

🤖 **FSMs for detect CPL interface among MPL repositories**: using the 156 FSMs to identify CPL interoperating instances among 19169 GitHub MPL repositories and record their metadata.

The following figure illustrates an example of FSM-modeled CPL interoperating. 

<div align="center">
  <img src="https://github.com/user-attachments/assets/8ca70ebb-7806-442c-a716-adf96ee98462" alt="FSM-modeled CPL Interoperability" width="700"/>
  <h4><b>Figure 3:</b> An example of FSM-modeled CPL interoperating.</h4>
</div>

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `cae.py`, `Analyzer.py`, `LangApiAnalyzer.py`, `Extraction_and_Benchmark_Construction.py`, `Algorithm 1` and `Algorithm 2` in our paper.

---

🤖 **Judger:** Determine whether a given code file contains any CPL interaction code snippets. If such a snippet is found and corresponds to a function-level implementation, return "Function-level"; if it corresponds to a class-level implementation, return "Class-level"; if no CPL interaction code is present, return "null". The prompt template used by this LLM tool is as follows:

<p align="center">
  <img width="900" alt="judger" src="https://github.com/user-attachments/assets/3de3f582-8148-491d-8967-7961e6d9ea6e" />
</p>

⚠️ **Note:** Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`.

---

🤖 **Function Extractor**: Used for extracting "function-level" CPL interaction code snippets. Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`. The prompt template used by this LLM tool is as follows:
<p align="center">
  <img width="900" alt="Func" src="https://github.com/user-attachments/assets/1a8430da-2711-4fdf-962e-b5daddfc7276"/>
</p>

⚠️ **Note:** Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`.

---

🤖 **Class Extractor:** Used for extracting "Class-level" CPL interaction code snippets. Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`. The prompt template used by this LLM tool is as follows:

<p align="center">
  <img width="900" alt="Class" src="https://github.com/user-attachments/assets/71be9695-36af-402f-85cf-57a495223473" />
</p>

⚠️ **Note:** Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`.

---

🤖 **FSM-based validator**: The correctness of the interaction snippets extracted by LLMs is verified using FSMs corresponding to the specific CPL techniques.

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `cae.py`, `Evaluation.py`, `Analyzer.py`, `LangApiAnalyzer.py`, `Extraction_and_Benchmark_Construction.py`, `Algorithm 1` and `Algorithm 2`.

---

🤖 **Instructor**: If the verification is successful, the interaction snippet extracted by the LLM is passed to the "Instructor" to generate the corresponding instruction. Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`. The prompt template used by the Instructor is as follows:

<p align="center">
  <img width="900" alt="instruction" src="https://github.com/user-attachments/assets/51d0ec7f-f363-4f5f-a2d5-7eace8155f33" />
</p>

⚠️ **Note:** Additional implementation details can be found in `Extraction_and_Benchmark_Construction.py`.

---

🔍 **Evaluation**:  The correctness of the interaction snippets generate by LLMs is verified using FSMs corresponding to the specific CPL techniques. 

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `tmp_test\testexample.py`,`Analyzer.py`, `LangApiAnalyzer.py`, `Algorithm 1` and `Algorithm 2` in our paper.

---
### CrossPL-IPC Construction Workflow
Algorithm 3 in paper illustrates the construction of the CrossPL-FFI for Python-C external function calls. The underlying C code is sourced from the GNU Scientific Library (GSL), a widely used and self-contained library of mathematical and statistical functions. The workflow begins by compiling the GSL library into shared object (.so) files using Autotools and Make, establishing the runtime environment. C source files are then cleaned and applied using an initial FFI prompt and an error-revision prompt. Execution of the candidate solution is performed in the environment where the precompiled .so files are available for FFI calls; successful executions are saved as benchmark entries, while failures are iteratively refined via the LLM (powered by Deepseek-V3). This approach ensures a scalable, reproducible, and controlled benchmark for assessing LLMs’ ability to generate correct Python-C FFI code. Additionally, key information from the canonical solution, including class names, function names, and parameter names, is incorporated into the ``Instruction'' field of the benchmark. Finally, these benchmark entries are provided as tasks to the LLMs under evaluation. The outputs from the LLMs are combined with automatically generated assertion test cases to verify correctness, enabling systematic execution and testing. This approach ensures a scalable, reproducible, and controlled benchmark for assessing LLMs’ ability to generate correct Python-C FFI code. Figs.4-7 provide the detailed prompt information.

---

<div align="center">
  <img src="https://github.com/user-attachments/assets/626ca08b-9b86-42ee-b36e-f152536aaafa" alt="4" width="900"/><br>
  <h4><b>Figure 4:</b> Prompt template for constructing CrossPL-FFI.</h4>
</div>

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `FFI_Consruction.py`,`execute_solution.py`and `Algorithm 3` in our paper.

---

<div align="center">
  <img src="https://github.com/user-attachments/assets/933aba60-9283-45de-ac79-815ae938b35b" alt="1" width="900"/><br>
  <h4><b>Figure 5:</b> Prompt template with error information for constructing CrossPL-FFI.</h4>
</div>

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `FFI_Consruction.py`,`execute_solution.py` and `Algorithm 3` in our paper.

---
<div align="center">
  <img src="https://github.com/user-attachments/assets/8fc0dd2d-6a94-4a2d-8d96-da3536f578bf" alt="2" width="900"/><br>
  <h4><b>Figure 6:</b> Add class information to the Instruction.</h4>
</div>

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `FFI_Consruction.py`,`Add_Info.py` and `Algorithm 3` in our paper.

---
<div align="center">
  <img src="https://github.com/user-attachments/assets/fa034320-29c6-4489-bad0-df0f4b6de767" alt="3" width="900"/><br>
  <h4><b>Figure 7:</b> Add class information to the Instruction.</h4>
</div>

⚠️ **Note:** A more comprehensive understanding of the implementation details can be obtained by referring to `FFI_Consruction.py`,`Add_Info.py` and `Algorithm 3` in our paper.

---

## Statistics of *CrossPL*

In constructing CrossPL-IPC benchmark, we conducted a thorough search and review of official documentation related to IPC technologies in CPL projects using keywords such as gRPC, Pipe, message queue, TCP, UDP, WebSocket, and HTTP across different programming languages. Fig.8(a) summarizes the distribution in CrossPL-IPC from different perspectives. Overall it covers six programming languages and seven IPC technologies, comprising a total of 1982 tasks. Among the programming languages, Java accounts for the highest proportion of IPC-related tasks with 615 instances (31.03%), whereas C++  the fewest, with 51 tasks (2.57%). Among IPC technologies, HTTP accounts for the highest proportion of tasks with 779 (39.30%), while UDP for the lowest with 92 tasks (4.64%).

Fig.8(b) further details the distribution of IPC technologies used by different programming languages within the CrossPL-IPC. Due to the distinct characteristics of each language, the proportional use of IPC technologies varies considerably; for example, Java tasks are predominantly associated with TCP, while JavaScript tasks are mostly related to HTTP. Notably, some IPC techniques cannot be fully implemented within a single function and require implementation at the class level. Consequently, during IPC-related code extraction, we distinguished between class-level and function-level code. Overall, class-level code accounts for 59.99% of the CrossPL-IPC, while function-level code constitutes 40.01%. This distribution reflects language-specific design patterns: for example, class-level implementations dominate in Java and PHP due to their object-oriented paradigms, while languages like Go and JavaScript tend to favor function-level or lightweight constructs. Such variations emphasize the necessity of handling both granularities in CrossPL-IPC to faithfully capture real-world IPC usage across different programming ecosystems.
<div align="center">

  <div style="display: inline-block; text-align: center; margin: 0 15px;">
    <img src="https://github.com/user-attachments/assets/30ab2885-f595-4f94-b9cc-89b70dae32d4"
         alt="Language Distribution"
         width="400"/>
    <p><b>(a) Pie chart of CrossPL-IPC dataset from different view.</b></p>
  </div>

  <div style="display: inline-block; text-align: center; margin: 0 15px;">
    <img src="https://github.com/user-attachments/assets/cc457ed7-8e00-4c36-a022-758546217a96"
         alt="Task Distribution"
         width="400"/>
    <p><b>(b) Distribution of different IPC technologies across different programming languages.</b></p>
  </div>

  <br>
  <h4><b>Figure 8:</b> Distribution of CrossPL benchmark.</h4>

</div>

---

Fig.9 presents the distribution of code line counts in the canonical solutions across CrossPL. Fig.9(a) presents the distribution of Canonical solution Code Lines of CrossPL-IPC. Fig.9(b) presents the distribution of Canonical solution Code Lines of CrossPL_FFI. Specifically, the code line of the CrossPL_IPC exhibits a median of 51 lines, an average of 66.96 lines, and a maximum of 483 lines. In contrast, the CrossPL_FFI shows a more compact distribution, with a median of 44 lines, an average of 47.1 lines, a maximum of 112 lines, and a minimum of 8 lines.
<div align="center">
  <img src="https://github.com/user-attachments/assets/9c2b5960-f79a-4a25-9778-f7eccef0a7f9" alt="x" width="900"/><br>
  <h4><b>Figure 9:</b> Distribution of Canonical solution Code Lines of CrossPL-IPC and CrossPL-FFI.</h4>
</div>

---

Fig.10 illustrates the distribution of instruction lengths, measured in characters, across the canonical solutions of CrossPL. Fig.10(a) shows the distribution of instruction length (characters) of CrossPL-IPC. Fig.10(b) presents the distribution of instruction length (characters) of CrossPL-FFI. For the CrossPL-IPC, the instructions have a median length of 1204 characters, an average of 1284.64 characters, and a minimum of 473 characters. In comparison, the length of instruction in CrossPL-FFI shows a slightly larger scale, with a median of 1277.5 characters, an average of 1329.74 characters, a maximum of 2421 characters, and a minimum of 973 characters.
<div align="center">
  <img src="https://github.com/user-attachments/assets/73797924-8fb6-4539-b4aa-2cc6245a752a" alt="y" width="900"/><br>
  <h4><b>Figure 10:</b> Distribution of instruction length (characters) of CrossPL-IPC and CrossPL-FFI.</h4>
</div>

⚠️ **Note:** The benchmark is stored in the `PolyBench/IPC_Bench` and `PolyBench/FFI_Bench` directories.

---

## Key Findings

- LLMs generate IPC code with varying effectiveness, performing better with C++ and \textit{gRPC} and worse with Go and low-level protocols like \textit{Pipe}. Failures for models like GPT-4o often stem from protocol and data transmission setup, while Llama3-8b-instruct frequently fails earlier at library configuration. 
- LLMs struggle with FFI-based CPL code generation (GPT-4o 19.54\% Pass@1; Llama3-8b-instruct $<$1\%), with failures dominated by symbol resolution, runtime, calling, and memory errors.
- Model characteristics, such as think mode, improve performance in reasoning-intensive FFI tasks but have limited or even negative impact on IPC tasks, which rely on well-structured communication patterns.
  
---
