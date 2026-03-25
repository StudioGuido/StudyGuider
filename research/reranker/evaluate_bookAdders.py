import requests
import pandas as pd
import os
import csv


"""
1. Look into summary to reunite chunks - DONE
2. Ask questions on those chunks - DONE
3. Make a CSV --> |textbook, chapter, question| - DONE
4. Write a different script that will read in CSV and reformat data into what you want - DONE
5. Write a function that will send this to our server - DONE
6. Save what the server writes back on a CSV - DONE
7. Another file read that CSV and set-up LLM as a judge - TODO
"""

# read the questions csv using pandas
df = pd.read_csv("generated_questions.csv")

# create an empty list to store the questions
questions = []

# iterate through the csv writing each row to a json object and appending it to the list
for i, row in df.iterrows():
    textbook = row["textbook"]
    chapter = row["chapter"]
    question = row["question"]

    data = {
        "prompt": question,
        "textbook": textbook,
        "chapter": chapter
    }

    questions.append(data)

# create an empty list to store the model responses and context
llm_responses = []

# for every question hit the generate api endpoint and store the question, response and context to a JSON object
# append that object to the llm_responses list
for question in questions:
    response = requests.post("http://0.0.0.0:8000/api/generate", json=question)

    data = response.json()
    answer = data["response"]
    context = data["context"]

    llm_responses.append({
        "input": question["prompt"],
        "context": context,
        "response": answer
    })

# csv setup
output_file = "llm_as_judge.csv"
file_exist = os.path.isfile(output_file)

with open(output_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # if the file does not exist, add the appropriate headers
    if not file_exist:
        writer.writerow(["question", "response", "context"])

    # go through response list and write to csv
    for llm_response in llm_responses:
        question = llm_response["input"]
        context = llm_response["context"]
        response = llm_response["response"]
        
        writer.writerow([question, response, context])

