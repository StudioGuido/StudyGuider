import csv
import os
from pathlib import Path

def save_flashcard(question, answer, textbook, chapter):
    #Save single flashcard to CSV file
    CSV_PATH = Path(__file__).resolve().parent / "flashcards.csv"

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        #add the header if there is not one yet
        if os.path.getsize(CSV_PATH) == 0:
            writer.writerow(["question", "answer", "textbook", "chapter"])
        #add the actual flashcard data
        writer.writerow([question, answer, textbook, chapter])