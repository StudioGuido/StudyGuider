import pandas as pd
from openai import OpenAI
from pathlib import Path
import os
import csv
from dotenv import load_dotenv

# load env so we can use openai API key
load_dotenv()

# use pandas to read CSV
csv_path = "../../backend/bookAdders/csv/thinkpython2.csv"
df = pd.read_csv(csv_path)

# create empty chapters list
chapters = []

# group the CSV by chapter and append the "chunk_text"s for each chapter together
# creates an array of dictonaryies where every entry has a key "chapter" and value "text"
for chapter, group in df.groupby("chapter"):
    full_text = " ".join(group["chunk_text"])
    chapter_name = group["Chapter_Name"].iloc[0]
    chapters.append({
        "chapter": chapter_name,
        "text": full_text
    })

# chapters = chapters[:1] # TEMP: only look at chapter 1 for testing purposes

client = OpenAI()

# CSV setup
textbook = Path(csv_path).stem
output_file = "generated_questions.csv"
file_exists = os.path.isfile(output_file)

with open(output_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # if the file does not exist yet, add the headers
    if not file_exists:
        writer.writerow(["textbook", "chapter", "question"])

    # for each chapter, prompt openai to generate 5 questions
    # store those 5 questions into a CSV --> |textbook, chapter, question|
    for chapter_data in chapters:
        chapter = chapter_data["chapter"]
        full_text = chapter_data["text"]

        # create clear and concise prompt for generating questions via LLM
        prompt = f"""
        Context:
        {full_text}

        Generate 5 questions that test understanding of the key concepts in this chapter.

        Format:
        1. question
        2. question
        3. question
        4. question
        5. question
        """

        # prompt the LLM and store the results
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7 # slightly more precise than default 1.0
        )

        # set output equal to just the text extraction of the LLM response
        output = response.choices[0].message.content

        # create an empty list to store results
        questions = []

        # break model output into lines
        for line in output.split("\n"):
            # remove extra spaces and invisible chars
            line = line.strip()

            # checks that lines isn't empty and the first char is a number
            if line and line[0].isdigit():
                # remove the number at the start and store just the question
                question = line.split(".", 1)[1].strip()
                questions.append(question)

        # append questions to the CSV
        for q in questions:
            writer.writerow([textbook, chapter, q])

