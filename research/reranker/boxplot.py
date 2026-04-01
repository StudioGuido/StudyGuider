import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_og = pd.read_csv("data/llm_as_judge_100pt.csv")
df_new = pd.read_csv("data/reranked_llm_as_judge.csv")

fig, ax = plt.subplots(figsize=(8,6))

ax.boxplot(df_og["score"], positions=[1], tick_labels=["Without Cross-Encoder Re-ranking"])
ax.boxplot(df_new["score"], positions=[2], tick_labels=["With Cross-Encoder Re-ranking"])

plt.title("Chunking Method Evaluation")

plt.savefig("data/boxplot.png")

plt.close()

