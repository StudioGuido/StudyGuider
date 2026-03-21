import os
import psycopg2
import time
import asyncpg
import asyncio

# docker exec -it studyguider_db psql -U bruno -d mydb

max_retries = 10
retry_delay = 2


async def init_db():
    """
    Initializes and sets up the PostgreSQL database schema, including required tables and extensions.

    This function will attempt to connect to the database up to `max_retries` times,
    with a delay of `retry_delay` seconds between attempts. Once a connection is successfully
    established, it does the following:

    1. Enables the pgvector extension (if not already enabled).
    2. Creates the following tables (if they do not exist):
       - textbooks
       - chapters
       - chapter_embeddings (includes pgvector field)
       - users
       - flash_card_set
       - master_flashcard
       - flash_card_set_assignment (weak entity: set ↔ master_flashcard)
       - seen_card
       - summary

    Table Schemas:
    ---------------

    textbooks
    ------------
    - id          : SERIAL PRIMARY KEY — unique identifier for each textbook
    - title       : TEXT NOT NULL — the title of the textbook
    - author      : TEXT NOT NULL — the author of the textbook
    - description : TEXT NOT NULL,
    - image_path  : TEXT NOT NULL

    chapters
    -----------
    - textbook_id     : INTEGER NOT NULL — FK to textbooks.id
    - chapter_number  : INTEGER NOT NULL — the chapter number
    - chapter_title   : TEXT NOT NULL — the title of the chapter
    - PRIMARY KEY     : (textbook_id, chapter_number)
    - FOREIGN KEY     : textbook_id REFERENCES textbooks(id) ON DELETE CASCADE

    chapter_embeddings
    ---------------------
    - textbook_id     : INTEGER NOT NULL — FK to textbooks.id
    - chapter_number  : INTEGER NOT NULL — FK to chapters.chapter_number
    - chunk_index     : INTEGER NOT NULL — index of the text chunk in that chapter
    - embedding       : VECTOR(384) NOT NULL — vector representation of the chunk (e.g., 384-dim from MiniLM)
    - chunk_text      : TEXT NOT NULL — the actual text of the chunk
    - PRIMARY KEY     : (textbook_id, chapter_number, chunk_index)
    - FOREIGN KEY     : (textbook_id, chapter_number) REFERENCES chapters(textbook_id, chapter_number) ON DELETE CASCADE

    users
    -----
    - supabase_uid : VARCHAR(255) PRIMARY KEY — Supabase auth user id
    - username     : VARCHAR(150) UNIQUE NOT NULL
    - created_at   : TIMESTAMP DEFAULT NOW()
    - last_login   : TIMESTAMP — optional

    flash_card_set
    ----------------
    - fcset_id  : SERIAL PRIMARY KEY
    - set_title : VARCHAR(255) NOT NULL — title unique per user
    - user_id   : VARCHAR(255) NOT NULL — FK to users(supabase_uid)
    - UNIQUE (user_id, set_title)

    master_flashcard
    -----------------
    - fc_id : SERIAL PRIMARY KEY — canonical Q/A tied to one text chunk
    - question, answer : TEXT NOT NULL
    - textbook_id, chapter_number, chunk_index — FK to chapter_embeddings (same composite key)

    flash_card_set_assignment (weak entity)
    -----------------------------------------
    - Identifying owners: flash_card_set(fcset_id), master_flashcard(fc_id)
    - PRIMARY KEY (fcset_id, master_fc_id) — each master card at most once per set

    seen_card
    ---------
    - user_id, flashcard_id — PK; tracks which master cards a user has seen

    summary
    -------
    - summary_id : SERIAL PRIMARY KEY
    - user_id    : VARCHAR(255) — FK to users(supabase_uid)
    - title      : VARCHAR(255) NOT NULL
    - content    : TEXT NOT NULL
    """
    for attempt in range(max_retries):
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("DATABASE_NAME"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
            )

            # attach pgvector onto our app
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            # add a user_role which is either "user, admin"
            await conn.execute(
                """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                    CREATE TYPE user_role AS ENUM ('admin', 'user');
                END IF;
            END
            $$;
            """
            )

            create_textbook_table_query = """
            CREATE TABLE IF NOT EXISTS textbooks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                description TEXT NOT NULL,
                image_path TEXT NOT NULL
            );
            """
            await conn.execute(create_textbook_table_query)

            chaptersTable = """
            CREATE TABLE IF NOT EXISTS chapters (
                textbook_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                chapter_title TEXT NOT NULL,
                PRIMARY KEY (textbook_id, chapter_number),
                FOREIGN KEY (textbook_id) REFERENCES textbooks (id)
                    ON DELETE CASCADE
            );
            """
            await conn.execute(chaptersTable)

            embeddingTable = """
            CREATE TABLE IF NOT EXISTS chapter_embeddings (
                textbook_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding vector(384) NOT NULL,
                chunk_text TEXT NOT NULL,
                PRIMARY KEY (textbook_id, chapter_number, chunk_index),
                FOREIGN KEY (textbook_id, chapter_number) REFERENCES chapters (textbook_id, chapter_number)
                    ON DELETE CASCADE
            );
            """
            await conn.execute(embeddingTable)
            
            usersTable = """
            CREATE TABLE IF NOT EXISTS users (
            supabase_uid VARCHAR(255) PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP
            );
            """
            await conn.execute(usersTable)

            flashCardSetTable = """
            CREATE TABLE IF NOT EXISTS flash_card_set (
                fcset_id SERIAL PRIMARY KEY,
                set_title VARCHAR(255) NOT NULL,
                user_id VARCHAR(255) REFERENCES users(supabase_uid) ON DELETE CASCADE,
                UNIQUE (user_id, set_title)
            );
            """
            await conn.execute(flashCardSetTable)

            master_flashcard_table = """
            CREATE TABLE IF NOT EXISTS master_flashcard(
                fc_id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                textbook_id INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                FOREIGN KEY (textbook_id, chapter_number, chunk_index)
                REFERENCES chapter_embeddings(textbook_id, chapter_number, chunk_index)
                ON DELETE CASCADE
            );
            """
            await conn.execute(master_flashcard_table)

            flash_card_set_assignment_table = """
            CREATE TABLE IF NOT EXISTS flash_card_set_assignment (
                fcset_id INTEGER NOT NULL REFERENCES flash_card_set(fcset_id) ON DELETE CASCADE,
                master_fc_id INTEGER NOT NULL REFERENCES master_flashcard(fc_id) ON DELETE CASCADE,
                PRIMARY KEY (fcset_id, master_fc_id)
            );
            """
            await conn.execute(flash_card_set_assignment_table)
            
            seenflashcards_table = """
            CREATE TABLE IF NOT EXISTS seen_card (
                user_id VARCHAR(255) REFERENCES users(supabase_uid) ON DELETE CASCADE,
                flashcard_id INTEGER NOT NULL REFERENCES master_flashcard(fc_id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, flashcard_id)
            );
            """
            await conn.execute(seenflashcards_table)

            summaryTable = """
            CREATE TABLE IF NOT EXISTS summary (
            summary_id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) REFERENCES users(supabase_uid) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL
            );
            """
            await conn.execute(summaryTable)

            await conn.close()

            print("✅ Created All Tables!")
            break

        except Exception as e:
            print(
                f"❌ Attempt {attempt+1}/{max_retries}: Database not ready, retrying in {retry_delay}s... ({e})"
            )
            await asyncio.sleep(retry_delay)


asyncio.run(init_db())
