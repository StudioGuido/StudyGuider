import pandas as pd
import os
import asyncpg
import asyncio


async def fillTables():
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

            # read in the main.csv
            allTextBooks = pd.read_csv("/csv/main.csv")

            # iterate through each text book and its author
            for textbook, creator, desc, imgPath in zip(allTextBooks['Textbooks'], allTextBooks['Author'], allTextBooks['Description'], allTextBooks['image_path']):
                
                df = pd.read_csv(f"/csv/{textbook}.csv")

                # select titles
                title = str(textbook)
                author = str(creator)
                description = str(desc)
                path = str(imgPath)
                

                # finding texbook id to follow sequential pattern
                result = await conn.fetchval("SELECT MAX(id) FROM textbooks")
                next_id = (result + 1) if result is not None else 1

                # insert the text book id, title, and author
                await conn.execute("""
                    INSERT INTO textbooks (user_uid, title, author, description, image_path, status)
                    VALUES ($1, $2, $3, $4, $5, $6);
                """, next_id, title, author, description, path, "status_placeholder")

                # adding to the chapters table
                for chapter_id, group in df.groupby('chapter'):
                    chapter_title = group['Chapter_Name'].iloc[0]

                    await conn.execute("""
                        INSERT INTO chapters (textbook_id, chapter_number, chapter_title)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (textbook_id, chapter_number) DO NOTHING;
                    """, next_id, chapter_id, chapter_title)

                    # adding the vector embeddings by iterating by rows from groups
                    for chunk_index, (_, row) in enumerate(group.iterrows(), start=1):
                        embedding_str = row['text_vector_embeddings']
                        chunk_text = row['chunk_text']

                        await conn.execute("""
                            INSERT INTO chapter_embeddings (textbook_id, chapter_number, chunk_index, embedding, chunk_text)
                            VALUES ($1, $2, $3, $4, $5);
                        """, next_id, chapter_id, chunk_index, embedding_str, chunk_text)

            await conn.close()
            print("✅ All Data Was Added To Tables")
            break

        except Exception as e:
            print(f"❌ Attempt {attempt+1}/{max_retries}: {e} — retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)

asyncio.run(fillTables())
