# CrossPL: A Benchmark for Cross-Programming Language Code Generation

**CrossPL** is the first benchmark specifically designed to evaluate the ability of large language models (LLMs) to generate **cross-programming language (CPL)** interoperating code. It focuses on **Inter-Process Communication (IPC)**, a foundational technique that supports interaction between components written in different programming languages.

---

## 🧠 Motivation

LLMs have demonstrated impressive performance in general code generation, but their ability to **accurately generate IPC-based cross-language code remains largely underexplored**. CrossPL fills this gap by offering a large-scale, systematically constructed benchmark.

---

## 🔍 Why CrossPL?

Modern software systems often consist of components written in multiple languages (e.g., Python + C++). However, existing benchmarks only assess single-language code generation. **CrossPL addresses this gap** by:

- Covering **6 programming languages**: Java, Python, JavaScript, Go, PHP, and C++
- Including **7 IPC technologies**: **HTTP**, **TCP**, **UDP**, **WebSocket**, **Pipe**, **gRPC**, and **Message Queue**
- Featuring **1982 high-quality CPL interaction tasks**, extracted from **19169** GitHub repositories using **156** FSMs (Finite State Machines)

---

## 🧪 Key Features
- ✅ **Automated LLM-based extraction pipeline**
- ✅ **FSM-based validation framework**
- ✅ **Evaluation across 20 state-of-the-art LLMs**
  
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
