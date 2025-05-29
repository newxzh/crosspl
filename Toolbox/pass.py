# from typing import List, Tuple
# def macro_average_pass_at_k(results: List[Tuple[int, int]], k: int) -> float:
#     """
#     Compute macro-averaged pass@k over multiple code generation tasks.
#
#     Parameters:
#     - results (List[Tuple[int, int]]): A list where each tuple is (n, c) for a task.
#     - k (int): top-k to evaluate (e.g., Pass@1, Pass@5)
#
#     Returns:
#     - float: macro-averaged pass@k score
#     """
#     scores = [pass_at_k(n, c, k) for n, c in results]
#     return sum(scores) / len(scores) if scores else 0.0


# import matplotlib.pyplot as plt
from math import comb
import json

right_path = r"D:\CAE\Test_results\js_ipc\Qwen3-235b-a22b\greedy_pass_nonethink.json"
wrong_path = r"D:\CAE\Test_results\js_ipc\Qwen3-235b-a22b\greedy_fail_nonethink.json"
with open(right_path, "r") as f:
    right = json.load(f)
with open(wrong_path, "r") as f:
    wrong = json.load(f)
len_right = len(right)
len_wrong = len(wrong)

def pass_at_k(n, c, k):
    if c == 0:
        return 0.0
    if k > n:
        return 1.0
    return 1 - comb(n - c, k) / comb(n, k)

pass1 = pass_at_k(len_right+len_wrong,len_right,1)
print(len_right+len_wrong)
print(pass1)

# def compute_passk_curve(success_counts, n=10, max_k=10):
#     num_prompts = len(success_counts)
#     passk_scores = []
#
#     for k in range(1, max_k + 1):
#         scores = [pass_at_k(n, c, k) for c in success_counts]
#         avg = sum(scores) / num_prompts
#         passk_scores.append(avg)
#
#     return passk_scores


# model_names = ["Model A", "Model B", "Model C", "Model D", "Model E"]
# model_scores = [
#     [0.20, 0.35, 0.50, 0.60, 0.68, 0.74, 0.78, 0.81, 0.83, 0.85],  # Model A
#     [0.25, 0.40, 0.55, 0.65, 0.72, 0.77, 0.81, 0.84, 0.86, 0.88],  # Model B
#     [0.15, 0.30, 0.45, 0.58, 0.65, 0.70, 0.75, 0.78, 0.80, 0.82],  # Model C
#     [0.28, 0.43, 0.59, 0.69, 0.76, 0.80, 0.84, 0.86, 0.88, 0.90],  # Model D
#     [0.18, 0.33, 0.48, 0.60, 0.67, 0.73, 0.77, 0.80, 0.83, 0.85]   # Model E
# ]
#
#
# def plot_multiple_passk_curves(model_scores, model_names):
#     ks = list(range(1, len(model_scores[0]) + 1))
#     plt.figure(figsize=(10, 6))
#
#     # 可选颜色和样式
#     styles = ['--o', '--s', '--^', '--v', '--D']
#     colors = ['dodgerblue', 'darkorange', 'green', 'purple', 'crimson']
#
#     for i, scores in enumerate(model_scores):
#         plt.plot(ks, scores,
#                  linestyle='--',
#                  marker=styles[i][2],  # 从 '--o' 取出 'o'
#                  color=colors[i],
#                  label=model_names[i],
#                  linewidth=2)
#
#     plt.title("Pass@k Comparison Across Models", fontsize=16)
#     plt.xlabel("k", fontsize=13)
#     plt.ylabel("Pass@k", fontsize=13)
#     plt.xticks(ks)
#     plt.ylim(0, 1.05)
#     plt.grid(True, linestyle='--', alpha=0.5)
#     plt.legend(fontsize=12)
#     plt.tight_layout()
#     plt.show()
#
# # 调用示例
# plot_multiple_passk_curves(model_scores, model_names)

