# CrossPL: A Benchmark for Cross-Programming Language Code Generation

**CrossPL** is the first benchmark specifically designed to evaluate the ability of large language models (LLMs) to generate **cross-programming language (CPL)** interoperating code. It focuses on **Inter-Process Communication (IPC)**, a foundational technique that supports interaction between components written in different programming languages.

---

## 🔍 Why CrossPL?(🧠 Motivation)

Modern software systems often consist of components written in multiple languages (e.g., Python + C++). However, existing code generation benchmarks predominantly focus on a single programming language. Although a few benchmarks for multi-language code generation have been developed, they cannot assess an LLM’s ability to generate code for cross-language interaction and thus cannot answer the crucial question: “Can LLMs produce correct cross-programming-language interoperating code?”. **CrossPL addresses this gap** by:
[demo_ipc.pdf](https://github.com/user-attachments/files/20631329/demo_ipc.pdf)

- Covering **6 programming languages**: Java, Python, JavaScript, Go, PHP, and C++
- Including **7 IPC technologies**: **HTTP**, **TCP**, **UDP**, **WebSocket**, **Pipe**, **gRPC**, and **Message Queue**
- Featuring **1982 high-quality CPL interaction tasks**, extracted from **19169** GitHub repositories using **156** FSMs (Finite State Machines)

---

## 🧪 Our contribution
- ✅ **CrossPL benchmark**:We propose **CrossPL**, to our knowledge the first benchmark aimed at evaluating the ability of LLMs to generate CPL interoperating code involving IPC. It comprises 1982 instances, encompassing six programming languages and seven major IPC technologies.
- ✅ **Comprehensive FSM-based interface characterization**: We carefully constructed 156 FSMs based on the official CPL interface specifications to formally characterize the IPC-based interaction interfaces. Such FSM-based characterization can not only facilitate us to detect IPC code snippets in real-world GitHub repositories, but also used to evaluate the capability of LLMs to generate CPL code under specific IPC scenarios. Each state in these FSMs is annotated with semantic information, which helps guide LLMs in extracting relevant IPC code snippets. 
- ✅ **LLM-based automatic analysis workflow**:  Based on the FSM-based interaction characterization, we further develop a LLM-based workflow that automatically extract relevant CPL code snippets, generate natural-language prompts and construct evaluation tasks for constructing the benchmark.
- ✅ **Large-scale empirical study**: We evaluate 20 representative LLMs to answer the key question: **whether LLMs can accurately generate cross-language interoperating code**. The findings highlight the need for more dedicated effort in this critical yet underexplored area.
  
---

## 🛠️ Benchmark Construction Workflow
![Framework_page_1](https://github.com/user-attachments/assets/eb510bd1-365e-46e4-a56c-bd401e4249f6)

CrossPL is constructed using an LLM-driven workflow:

---

## 🔎 Key Findings

- LLMs vary widely in their ability to generate IPC code across languages and techniques.
- High-level protocols like **gRPC** yield better performance due to structured semantics.
- Performance on **Go** is generally weaker, likely due to mismatch with class-based training data.
- Larger model size doesn’t guarantee better performance; **“thinking mode” is not always helpful**.

---
