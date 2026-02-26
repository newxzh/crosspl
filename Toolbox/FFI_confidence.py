import os
import math
import json
import random
import numpy as np
from math import comb
from tqdm import trange

def get_all_subfolders(root_dir):
    folder_list = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            folder_list.append(full_path)
    return folder_list

def pass5_from_c(c, n=10, k=5):
    # c: integer success count in n trials
    if n - c < k:
        return 1.0
    # comb may error if arguments invalid; handle edge cases
    total = comb(n, k)
    num = comb(n - c, k)
    return 1.0 - num / total

def per_sample_pass5_list(c_list, n=10, k=5):
    return [pass5_from_c(int(c), n, k) for c in c_list]

def macro_mean(pass5_list):
    arr = np.array(pass5_list, dtype=float)
    return arr.mean()

def bootstrap_macro_ci(pass5_list, B=5000, alpha=0.05, seed=None, use_tqdm=False):
    rng = random.Random(seed)
    n = len(pass5_list)
    boot_means = []
    iterable = range(B)
    if use_tqdm:
        iterable = trange(B)
    for _ in iterable:
        sample_idx = [rng.randrange(0, n) for _ in range(n)]
        sample_vals = [pass5_list[i] for i in sample_idx]
        boot_means.append(np.mean(sample_vals))
    lower = np.percentile(boot_means, 100 * (alpha/2))
    upper = np.percentile(boot_means, 100 * (1 - alpha/2))
    return lower, upper, np.array(boot_means)

def normal_approx_ci(pass5_list, alpha=0.05):
    arr = np.array(pass5_list, dtype=float)
    mean = arr.mean()
    s = arr.std(ddof=1)
    se = s / math.sqrt(len(arr))
    z = 1.96 if abs(alpha-0.05) < 1e-9 else abs(np.round(np.percentile(np.random.normal(size=1000000), [100*(1-alpha/2)])[0],4))
    # simpler: use scipy.stats.norm.ppf if available; here we use 1.96 for 95%
    lower = mean - 1.96 * se
    upper = mean + 1.96 * se
    # clamp to [0,1]
    lower = max(0.0, lower)
    upper = min(1.0, upper)
    return lower, upper, mean, se, s

if __name__ == "__main__":
    python_paths = [
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/GPT-4o",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/GPT-4o-mini",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Gemini-1.5-pro",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/GLM4-plus",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/DS-V3",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-235b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-32b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-30b-a3b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-14b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-8b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen3-4b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/GLM4-9b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeGeeX",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen2.5-coder-32b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen2.5-coder-14b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Qwen2.5-coder-7b",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeGemma",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/CodeLlama",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Gemma",
        "/home/xiong/ffi/crosspl/Test_results/FFI_results/Llama3"
    ]
    for i in range(len(python_paths)):
        print(os.path.basename(python_paths[i]))
        path = os.path.join(python_paths[i],"pass1_report.json")
        c_list = []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for i in range(len(data)):
            fail_count = data[i]["test_result"].count("Fail")
            c_list.append(10-fail_count)

        print(len(c_list))

        pass5_list = per_sample_pass5_list(c_list, n=10, k=5)
        mean_macro = macro_mean(pass5_list)

        # Bootstrap CI
        lower_b, upper_b, boot_means = bootstrap_macro_ci(pass5_list, B=5000, alpha=0.05, seed=1234, use_tqdm=False)

        # Normal approx CI
        lower_n, upper_n, mean_n, se, s = normal_approx_ci(pass5_list, alpha=0.05)

        print(f"Macro mean pass@5 = {mean_macro*100:.2f}%")
        print(f"Bootstrap 95% CI = [{lower_b*100:.2f}%, {upper_b*100:.2f}%] (B=5000)")
        # print(f"Normal approx 95% CI = [{lower_n:.6f}, {upper_n:.6f}] (mean={mean_n:.6f}, se={se:.6f}, sd={s:.6f})")

