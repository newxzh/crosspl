# CrossPL: A Benchmark for Cross-Programming Language Code Generation

**CrossPL** is the first benchmark specifically designed to evaluate the ability of large language models (LLMs) to generate **cross-programming language (CPL)** interoperating code. It focuses on **Inter-Process Communication (IPC)**, a foundational technique that supports interaction between components written in different programming languages.

---
## Table of Contents

- [Why CrossPL? (Motivation)](#why-crosspl-motivation)
- [Statistics of *CrossPL*](#statistics-of-crosspl)
- [Our Contributions](#our-contributions)
- [Benchmark Construction Workflow](#benchmark-construction-workflow)
- [Key Findings](#key-findings)
  
---

## Why CrossPL?(Motivation)

Modern software systems often consist of components written in multiple proframming languages (MPL). The follow figure illustrates an example of CPL interaction between Python and C++ by an IPC protocol (*Socket*). Such examples are widely found in MPL projects involving Python and C++ for data science, robotics, and embedded systems.

<div align="center">
  <img src="https://github.com/user-attachments/assets/e3515723-bf37-4837-82eb-7449b0ef8192" alt="ipc demo" width="500"/><br>
  <sub><b>Figure 1:</b> CPL interaction between Python and C++ by an IPC protocol (<i>Socket</i>).</sub>
</div>

However, existing code generation benchmarks predominantly focus on a single programming language. Although a few benchmarks for multi-language code generation have been developed, they cannot assess an LLM’s ability to generate code for CPL interaction and thus cannot answer the crucial question: “Can LLMs produce correct cross-programming-language interoperating code?”. 

---

## Statistics of *CrossPL*

- Covering **6 programming languages**: Java, Python, JavaScript, Go, PHP, and C++
- Including **7 IPC technologies**: **HTTP**, **TCP**, **UDP**, **WebSocket**, **Pipe**, **gRPC**, and **Message Queue**
- Featuring **1982 high-quality CPL interaction tasks**, extracted from **19169** GitHub MPL repositories using **156** FSMs (Finite State Machines)

<div align="center">
  <img src="https://github.com/user-attachments/assets/30ab2885-f595-4f94-b9cc-89b70dae32d4" alt="fan chart" width="400"/>
  <img src="https://github.com/user-attachments/assets/cc457ed7-8e00-4c36-a022-758546217a96" alt="bar chart" width="400"/>
  <br>
  <sub><b>Figure 2:</b> Distribution of CrossPL benchmark.</sub>
</div>


---

## Our contributions
- ✅ **CrossPL benchmark**:We propose **CrossPL**, to our knowledge the first benchmark aimed at evaluating the ability of LLMs to generate CPL interoperating code involving IPC. It comprises 1982 instances, encompassing six programming languages and seven major IPC technologies.
- ✅ **Comprehensive FSM-based interface characterization**: We carefully constructed 156 FSMs based on the official CPL interface specifications to formally characterize the IPC-based interaction interfaces. Such FSM-based characterization can not only facilitate us to detect IPC code snippets in real-world GitHub repositories, but also used to evaluate the capability of LLMs to generate CPL code under specific IPC scenarios. Each state in these FSMs is annotated with semantic information, which helps guide LLMs in extracting relevant IPC code snippets. 
- ✅ **LLM-based automatic analysis workflow**:  Based on the FSM-based interaction characterization, we further develop a LLM-based workflow that automatically extract relevant CPL code snippets, generate natural-language prompts and construct evaluation tasks for constructing the benchmark.
- ✅ **Large-scale empirical study**: We evaluate 20 representative LLMs to answer the key question: **whether LLMs can accurately generate cross-language interoperating code**. The findings highlight the need for more dedicated effort in this critical yet underexplored area.
  
---

## Benchmark Construction Workflow

<p align="center">
<img width="900" alt="judger" src="https://github.com/user-attachments/assets/eb510bd1-365e-46e4-a56c-bd401e4249f6" />
</p>

CrossPL is constructed using an LLM-driven workflow:

⚠️ **Note:** The following prompt templates for **Judger**, **Function Extractor**, and **Class Extractor** are exemplified using Java. Prompt templates for other programming languages can be found in the `prompt_template` directory of the project.

- **FSMs for detect CPL interface among MPL repositories**: using the 156 FSMs to identify CPL interoperating instances among 19169 GitHub MPL repositories and record their metadata.
  
- **Judger**: Determine whether a given code file contains any CPL interaction code snippets. If such a snippet is found and corresponds to a function-level implementation, return "Function-level"; if it corresponds to a class-level implementation, return "Class-level"; if no CPL interaction code is present, return "null".The prompt template used by this LLM tool is as follows:

<p align="center">
<img width="900" alt="judger" src="https://github.com/user-attachments/assets/3de3f582-8148-491d-8967-7961e6d9ea6e" />
</p>

- **Function Extractor**: Used for extract "function-level" CPL interaction code snippets.The prompt template used by this LLM tool is as follows:
<p align="center">
<img width="900" alt="Func" src="https://github.com/user-attachments/assets/1a8430da-2711-4fdf-962e-b5daddfc7276"/>
</p>

- **Class Extractor**: Used for extract "function-level" CPL interaction code snippets. .The prompt template used by this LLM tool is as follows:

<p align="center">
<img width="900" alt="Class" src="https://github.com/user-attachments/assets/71be9695-36af-402f-85cf-57a495223473" />
</p>

- **FSM-based validator**: The correctness of the interaction snippets extracted by LLMs is verified using FSMs corresponding to the specific CPL techniques.

- **Instructor**: If the verification is successful, the interaction snippet extracted by the LLM is passed to the "Instructor" to generate the corresponding instruction. The prompt template used by the Instructor is as follows:

<p align="center">
<img width="900" alt="instruction" src="https://github.com/user-attachments/assets/51d0ec7f-f363-4f5f-a2d5-7eace8155f33" />
</p>

- **Evaluation**:  The correctness of the interaction snippets generate by LLMs is verified using FSMs corresponding to the specific CPL techniques.

---

## Key Findings

- LLMs vary widely in their ability to generate IPC code across languages and techniques.
- High-level protocols like **gRPC** yield better performance due to structured semantics.
- Performance on **Go** is generally weaker, likely due to mismatch with class-based training data.
- Larger model size doesn’t guarantee better performance; **“thinking mode” is not always helpful**.
<p align="center">
  <img src="https://github.com/user-attachments/assets/a485ca3d-7cc9-476e-8453-a69e1419f336" width="45%" style="margin-right: 10px;"/>
  <img src="https://github.com/user-attachments/assets/0a681988-10e7-4366-b207-b69bab714489" width="45%"/>
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/7483b2dc-4ac0-48d5-a758-08cf2256ab71" width="45%" style="margin-right: 10px;"/>
  <img src="https://github.com/user-attachments/assets/cb3461b5-1b20-4e4d-ab1e-d6a6d047a65b" width="45%"/>
</p>

---
