import pandas as pd 
import matplotlib.pyplot as plt

throughput_path = "../../api/throughput.csv"

# show histogram of throughput 
throughput_df = pd.read_csv(throughput_path, names=["timestamp", "endpoint", "textbook", "chapter", "requested_count", "status_code", "cards_returned", "throughput", "error"], skiprows=1)

trials = [f"Trial {i+1}" for i in range(len(throughput_df))]

plt.bar(trials, throughput_df["throughput"], edgecolor="black", color="salmon")
plt.title("Flashcard Throughput by Trial")
plt.xlabel("Trial")
plt.ylabel("Throughput (s/flashcard)")
plt.savefig("throughput_histogram.png")
