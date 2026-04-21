from api._VectorCreator import VectorEmbedder
import api._FunctionsToHelpBreakDownTextBook as f
import os
import pandas as pd
import asyncpg
import asyncio
import json


def createEmbeddings(pdf_paths: list[str]):

    # this will create a map with key as chapter number and value as list of chunks for that chapter
    chapterChunksMap = f.splitIntoChunks_to_MapToChapter(pdf_paths)

    # this will create a dataframe with columns: chapter, chunk_text, chapter_name
    dataFrame = f.mapOfChapterWithChunks_to_DataFrame(chapterChunksMap)

    # this will create the vector embeddings for each chunk of text and add it to the dataframe
    vectorEmbedder = VectorEmbedder(os.getenv("MODEL_ID"), dataFrame)
    vectorEmbedder.createEmbeddings()

    # Debugging - Checks if the embeddings were created
    newFrame = vectorEmbedder.getEmbeddingsDf()

    # Resolve path relative to this file's location:
    # _creatingEmbeddings.py lives in backend/api/, so go up one level into backend/bookAdders/csv/
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.abspath(os.path.join(this_file_dir, "..", "bookAdders", "csv"))
    os.makedirs(csv_dir, exist_ok=True)

    output_path = os.path.join(csv_dir, "testingEmbeddings.csv")
    print(f"Saving CSV to: {output_path}", flush=True)
    newFrame.to_csv(output_path, index=False)
    


    # return vectorEmbedder.getEmbeddingsDf()


async def fillTables(pdf_paths: list[str], textbook_id: int):
    print(f"fillTables called with textbook_id={textbook_id}, type={type(textbook_id)}")
    '''
    Fill table is an asynchronous function that will fill our SQL tables using
    every textbook entry within the main.csv.
    '''

    retry_delay = 2
    max_retries = 10
    
    # this is to ensure that the tables retry if the database is not ready
    for attempt in range(max_retries):
        
        # connect to the database
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("DATABASE_NAME"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD")
            )

            df = createEmbeddings(pdf_paths)

            for chapter_id, group in df.groupby('chapter'):
                for chunk_index, (_, row) in enumerate(group.iterrows(), start=1):
                    embedding_list = row['text_vector_embeddings']

                    # Convert to postgres vector literal format
                    embedding_str = "[" + ",".join(str(x) for x in embedding_list) + "]"

                    chunk_text = row['chunk_text']

                    await conn.execute("""
                        INSERT INTO chapter_embeddings (textbook_id, chapter_number, chunk_index, embedding, chunk_text)
                        VALUES ($1, $2, $3, $4::vector, $5);
                    """, textbook_id, chapter_id, chunk_index, embedding_str, chunk_text)

            await conn.close()
            print("✅ All Data Was Added To Tables")
            break

        except Exception as e:
            print(f"❌ Attempt {attempt+1}/{max_retries}: {e} — retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)











#TODO: Already have the chapters split into new pdfs, change splitIntoChunks_to_MapToChapter to take in the pdfs 
# instead of the text and then create the chunks from there. 
# This will save us from having to turn the pdf into text and then back into pdfs for each chapter. 
# We can just directly create the chunks from the original pdf. 
# This will also help preserve any formatting that may be lost when converting to text and back to pdf.