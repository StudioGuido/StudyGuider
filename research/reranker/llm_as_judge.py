import pandas as pd
import os
import csv
from openai import OpenAI
from dotenv import load_dotenv

# load env so we can use OpenAI API key
load_dotenv()

# use pandas to read CSV
df = pd.read_csv("data/llm_responses.csv")

# create empty list to store CSV contents
responses = []

# load data from CSV to list
for i, row in df.iterrows():

    data = {
        "question": row["question"],
        "response": row["response"],
        "context": row["context"]
    }

    responses.append(data)


# set the client
client = OpenAI()

# csv setup
output_file = "data/reranked_llm_as_judge.csv"
file_exist = os.path.isfile(output_file)

# iterate through the llm responses
with open(output_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # if the file does not exist yet, add the headers
    if not file_exist:
        writer.writerow(["question", "response", "context", "score", "reason"])

    # score each llm response and store in llm_scores list
    for r in responses:
        question = r["question"]
        response_text = r["response"]
        context = r["context"]

        prompt = f'''
        You are evaluating retrieval quality for a RAG (Retrieval-Augmented Generation) system.

        QUESTION:
        {question}

        RETRIEVED CONTEXT:
        {context}

        LLM RESPONSE:
        {response_text}

        Your task:
        Evaluate how well the retrieved context supports answering the question AND producing the given response.

        Focus on retrieval quality, not writing quality.

        Consider:
        - Does the context contain the information needed to answer the question?
        - Is the correct information present in the retrieved chunks?
        - Is important information missing due to bad chunking or retrieval?
        - Is there irrelevant or distracting text?
        - Could the response have been generated using only this context?
        - Does the response rely on outside knowledge not in the context?

        Scoring:
        100 = Perfect retrieval. Context contains all needed info, well chunked, no important info missing.
        75 = Good retrieval. Minor missing or extra info, but still sufficient.
        50 = Partial retrieval. Some relevant info, but missing key details.
        25 = Poor retrieval. Weak relevance or bad chunking makes answering difficult.
        0 = Failed retrieval. Context does not contain needed information.

        Scores between these benchmarks are allowed and encouraged when the retrieval quality falls between two levels.

        Return exactly:
        Score: <number>
        Reason: <short explanation focused on retrieval quality>
        '''

        # prompt the LLM and store the results
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7 # slightly more precise than default 1.0
        )

        output = response.choices[0].message.content

        score = None
        reason = None

        # strip responses and store raw text of score and reason
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("Score:"):
                score = line.split(":", 1)[1].strip()
            elif line.startswith("Reason:"):
                reason = line.split(":", 1)[1].strip()

        # write results to CSV
        writer.writerow([question, response_text, context, score, reason])







