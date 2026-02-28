import requests
import pandas as pd
import os
import time


"""
1. Look into summary to reunite chuncks
2. Ask questions on those chuncks
3. Make a CSV --> |textbook, chapter, question|
4. Write a different script that will read in CSV and reformat data into what you want
5. Write a function that will send this to our server
6. Save what the server writes back on a CSV
7. Another file read that CSV and set-up LLM as a judge
"""
questions = [
    # ch 1 - the way of the program
    # ch 2 - variables, expressions and statements
    # ch 3 - functions
    # ch 4 - case study: interface design
    # ch 5 - conditionals and recursion
    # ch 6 - fruitful functions
    # ch 7 - iteration
    # ch 8 - strings
    # ch 9 - case study: word play
    # ch 10 - lists
    # ch 11 - dictionaries
    # ch 12 - tuples
    # ch 13 - case study: data structure selection
    # ch 14 - files
    # ch 16 - clsses and object
    # ch 17 - classes and functions
    # ch 18 - classes and methods
    # ch 19 - inheritance
]


df = pd.read_csv("../../backend/bookAdders/csv/thinkpython2.csv")
print(df['chunk_text'])
print(df)

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