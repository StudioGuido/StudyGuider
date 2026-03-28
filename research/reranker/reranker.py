from sentence_transformers.cross_encoder import CrossEncoder
import pandas as pd

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

df = pd.read_csv('../../backend/bookAdders/csv/thinkpython2.csv')

chapter_chunks = df[df['chapter'] == 1]['chunk_text'].tolist()

query = "What is a program?"
pairs = []
for chunk in chapter_chunks:
    pairs.append([query, chunk])

scores = model.predict(pairs)
print(scores)

#take 5 chunks
#give query
#rerank 5
#have question returned