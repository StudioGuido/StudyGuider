import pandas as pd
import os

csv_file_path = "../../backend/bookAdders/csv/thinkpython2.csv"
excel_path = "data/book_csv"

df = pd.read_csv(csv_file_path)

df.to_excel(excel_path, index=False, sheet_name="sheet1")
