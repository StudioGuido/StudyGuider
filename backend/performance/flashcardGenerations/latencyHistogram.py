import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

latency_path = "../../api/latency.csv"


latency_df = pd.read_csv(latency_path, names=["cards", "chapter", "latency", "textbook"], skiprows=1)


#trial averages in one graph

trials = []
avgs = []

for i, row in latency_df.iterrows():
    latencies = eval(row["latency"])
    trials.append(f"Trial {i+1}")
    avgs.append(np.mean(latencies))

plt.bar(trials, avgs, edgecolor="black", color="skyblue")
plt.title("Average Flashcard Latency by Trial")
plt.xlabel("Trial")
plt.ylabel("Avg Latency (s)")
plt.savefig("latency_histogram.png")























































#show histogram of latencies new png per trial 
for i, row in latency_df.iterrows():
    latencies = eval(row["latency"])
    card_numbers = list(range(1, len(latencies) + 1))
    
   
    plt.bar(card_numbers, latencies, edgecolor="black", color="skyblue")
    plt.title(f"Trial {i+1} {row['chapter']}")
    plt.xlabel("Flashcard Number")
    plt.ylabel("Latency (s)")
    plt.xticks(card_numbers)
    plt.savefig(f"trial_{i+1}_latency.png")
