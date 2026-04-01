import pandas as pd
import os

csv_file_path = "data/reranked_llm_as_judge.csv"
excel_path = "data/reranked_llm_as_judge.xlsx"

df = pd.read_csv(csv_file_path)

df.to_excel(excel_path, index=False, sheet_name="sheet1")
