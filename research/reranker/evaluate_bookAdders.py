import requests
import pandas as pd


"""
1. Look into summary to reunite chuncks - DONE
2. Ask questions on those chuncks - DONE
3. Make a CSV --> |textbook, chapter, question| - DONE
4. Write a different script that will read in CSV and reformat data into what you want - DONE
5. Write a function that will send this to our server
6. Save what the server writes back on a CSV
7. Another file read that CSV and set-up LLM as a judge
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

llm_responses = []

for question in questions:
    response = requests.post("http://0.0.0.0:8000/api/generate", json=question)
    print(response.status_code)
    print(response.text)
    data = response.json()
    answer = data["response"]
    context = data["context"]

    llm_responses.append({
        "input": question["prompt"],
        "context": context,
        "response": response
    })

print(llm_responses)







'''

Prompt for LLM as a judge:

You are evaluating retrieval quality.

QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Score how well the context supports answering the question.

Scoring:
5 = fully sufficient
4 = mostly sufficient
3 = partially relevant
2 = weak relevance
1 = irrelevant

Return:
Score: <number>
Reason: <short explanation>
'''