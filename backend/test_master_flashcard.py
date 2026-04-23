import os
import asyncio
import asyncpg

async def test_master_flashcard():
    # Connect to the database
    conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST", "localhost"),
        database=os.getenv("DATABASE_NAME", "mydb"),
        user=os.getenv("DATABASE_USER", "bruno"),
        password=os.getenv("DATABASE_PASSWORD", "yourpassword")
    )

    print("✅ Connected to database")

    # Create the table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS master_flashcard(
        id SERIAL PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        textbook_id INTEGER NOT NULL,
        chapter_number INTEGER NOT NULL,
        chunk_index INTEGER NOT NULL,
        FOREIGN KEY (textbook_id, chapter_number)
            REFERENCES chapters(textbook_id, chapter_number)
            ON DELETE CASCADE
    );
    """
    await conn.execute(create_table_query)
    print("✅ master_flashcard table created (or already exists)")

    # Test insert
    try:
        await conn.execute("""
            INSERT INTO master_flashcard (textbook_id, chapter_number, question, answer, chunk_index)
            VALUES ($1, $2, $3, $4, $5)
        """, 1, 1, "Test Question?", "Test Answer!", 0)
        print("✅ Test insert successful")
    except Exception as e:
        print("❌ Insert failed:", e)

    # Close connection
    await conn.close()

asyncio.run(test_master_flashcard())
