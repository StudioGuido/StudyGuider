import pandas as pd
import matplotlib.pyplot as plt
import ast

latency_path = "../../api/latency.csv"


latency_df = pd.read_csv(latency_path, names=["textbook", "chapter", "cards", "latency"], skiprows=1)

chapter_labels = latency_df["chapter"].unique()

chapters = [] #needs to be list of lists 
for ch in chapter_labels:
    # Get all rows for this chapter
    chapter_rows = latency_df[latency_df["chapter"] == ch]
    
    # Collect all latency values across all trials
    all_values = []
    for latency_list in chapter_rows["latency"]:
        values = ast.literal_eval(latency_list)  # convert string to list
        for v in values:
            all_values.append(v)
    
    chapters.append(all_values)


plt.boxplot(chapters, labels=chapter_labels, patch_artist=True,
            boxprops=dict(facecolor="lightblue", color="black"),
            medianprops=dict(color="black"))

plt.title("Flashcard Latency by Chapter")
plt.xlabel("Chapter")
plt.ylabel("Latency (s)")
plt.xticks(rotation=45, ha="right")
plt.savefig("latency_boxplots.png")













'''
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
'''



















































'''


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
'''