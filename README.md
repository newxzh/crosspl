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

- Covering **6 programming languages**: Java, Python, JavaScript, Go, PHP, and C++
- Including **7 IPC technologies**: **HTTP**, **TCP**, **UDP**, **WebSocket**, **Pipe**, **gRPC**, and **Message Queue**
- Featuring **1982 high-quality CPL interaction tasks**, extracted from **19169** GitHub MPL repositories using **156** FSMs (Finite State Machines)

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
  <h4><b>Figure 2:</b> Distribution of CrossPL benchmark.</h4>

</div>

⚠️ **Note:** The benchmark is stored in the `PolyBench/IPC_Bench` and `PolyBench/FFI_Bench` directories.

---

## Key Findings

- LLMs vary widely in their ability to generate IPC code across languages and techniques.
- High-level protocols like **gRPC** yield better performance due to structured semantics.
- Performance on **Go** is generally weaker, likely due to mismatch with class-based training data.
- Larger model size doesn’t guarantee better performance; **“thinking mode” is not always helpful**.

---
