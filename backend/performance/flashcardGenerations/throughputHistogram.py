import pandas as pd 
import matplotlib.pyplot as plt

throughput_path = "../../api/throughput.csv"

# show histogram of throughput 
throughput_df = pd.read_csv(throughput_path, names=["timestamp", "endpoint", "textbook", "chapter", "requested_count", "status_code", "cards_returned", "throughput", "error"], skiprows=1)

# Get the chapter names
chapter_labels = throughput_df["chapter"]

# For each chapter, grab its throughput values
chapters = []
for ch in chapter_labels:
    throughput_values = throughput_df[throughput_df["chapter"] == ch]["throughput"]
    chapters.append(throughput_values)

plt.boxplot(chapters, labels=chapter_labels, patch_artist=True,
            boxprops=dict(facecolor="lightgreen", color="black"),
            medianprops=dict(color="black"))

plt.title("Flashcard Throughput by Chapter")
plt.xlabel("Chapter")
plt.ylabel("Throughput (s/flashcard)")
plt.xticks(rotation=45, ha="right")
plt.savefig("throughput_boxplots.png")


#source myenv/bin/activate