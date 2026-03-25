import pandas as pd
import os

csv_file_path = "data/llm_as_judge_100pt.csv"
excel_path = "data/lm_as_judge_100pt.xlsx"

df = pd.read_csv(csv_file_path)

df.to_excel(excel_path, index=False, sheet_name="sheet1")
