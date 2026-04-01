import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_og = pd.read_csv("data/llm_as_judge_100pt.csv")
df_new = pd.read_csv("data/reranked_llm_as_judge.csv")

fig, ax = plt.subplots(figsize=(8,6))

bp1 = ax.boxplot(df_og["score"], positions=[1], tick_labels=["Without Cross-Encoder Re-ranking"],
                 patch_artist=True,
                 boxprops=dict(facecolor="red", alpha=0.4, color="black", linewidth=2),
                 medianprops=dict(color="gold", linewidth=4),
                 whiskerprops=dict(color="black", linewidth=2),
                 capprops=dict(color="black", linewidth=2))

bp2 = ax.boxplot(df_new["score"], positions=[2], tick_labels=["With Cross-Encoder Re-ranking"],
                 patch_artist=True,
                 boxprops=dict(facecolor="green", alpha=0.4, color="black", linewidth=2),
                 medianprops=dict(color="gold", linewidth=4),
                 whiskerprops=dict(color="black", linewidth=2),
                 capprops=dict(color="black", linewidth=2))

ax.set_ylabel("Context Retrieval Score")

plt.title("Chunk Context Retrieval Evaluation")


plt.savefig("data/boxplot.png")

plt.close()

