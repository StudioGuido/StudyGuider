import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import os
import httpx
import asyncpg
import asyncio
from fastapi import HTTPException
from .openAIHelper import get_openai_response

OLLAMA_HOST  = os.getenv("OLLAMA_HOST")        # in Compose, service name "ollama"
OLLAMA_PORT  = os.getenv("OLLAMA_PORT")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")     # default model
TIMEOUT_SEC   = float(os.getenv("OLLAMA_TIMEOUT_SEC"))
OLLAMA_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

# OLLAMA_HOST=127.0.0.1:11435 ollama serve

# Load tokenizer and model
model_id = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id)

# Use MPS if available (Macs), otherwise CPU
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
model = model.to(device)


async def generate_embeddings(texts):
    '''
    This function will asynchronously run the function generate embeddings blocking
    '''
    return await asyncio.to_thread(_generate_embeddings_blocking, texts)


def _generate_embeddings_blocking(texts):
    '''
    This is a blocking function that will generate embeddings for any given text
    using the all-MiniLM-L6-v2 model
    '''

    try:
        # Check input type
        if not isinstance(texts, (str, list)):
            raise ValueError("Input must be a string or list of strings.")
        
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.cpu().numpy().tolist()
    
    except Exception as e:
        raise RuntimeError(f"Error generating embeddings: {e}")


# async def getModelResponse(prompt: str) -> str:
#     '''
#     This will provide a prompt to Ollama and return what Ollama
#     generated
#     '''

#     data = {
#         "model": OLLAMA_MODEL,
#         "prompt": prompt,
#         "stream": False
#     }
#     timeout = httpx.Timeout(60.0)
#     try: 
#         async with httpx.AsyncClient(timeout=timeout) as client:
#             resp = await client.post(OLLAMA_URL, json=data)
#     except httpx.RequestError as e:
#         raise HTTPException(
#             status_code=503,
#             detail=f"Failed to connect to Ollama: {e}"
#         )
#     resp.raise_for_status()
#     if resp.status_code != 200:
#         raise HTTPException(status_code=resp.status_code, detail=resp.text)

#     data = resp.json()
#     return data.get("response", "")

    

async def generate_Helper(prompt, chapter, textbook):
    '''
    This function will generate embeddings for a prompt then
    run similairity search on a chapters vector embeddings based
    on its textbook 
    '''

    # checking for the prompt to be less than or equal to 50 words
    try:
        if len(prompt.split()) > 50:
            raise ValueError("Prompt too long: keep it below 50 words")
    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    try:
        embedding = await generate_embeddings(prompt)
    except Exception as e:
        raise

    
    # set embedding to string of float32 values
    embedding = str(np.array(embedding).astype("float32")[0].tolist())

    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        res = await conn.fetchrow("""
            SELECT c.textbook_id, c.chapter_number
            FROM chapters c
            JOIN textbooks t ON c.textbook_id = t.id
            WHERE t.title = $1 AND c.chapter_title = $2;
        """, textbook, chapter)

        
        if not res:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {chapter} not found or textbook {textbook} not found.")


        textbook_id = res["textbook_id"]
        chapter_number = res["chapter_number"]

        rows = await conn.fetch("""
            SELECT chunk_text, embedding <-> $1 AS distance
            FROM chapter_embeddings
            WHERE textbook_id = $2 AND chapter_number = $3
            ORDER BY distance ASC
            LIMIT 1;
        """, embedding, textbook_id, chapter_number)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"Empty Table Row")
        
        # combine context and make a prompt
        context = "\n".join(row[0] for row in rows)
        prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer: Provide a concise response\nIf no similiar content then respond with: No Context Applies"

        # try:
        #     answer = await getModelResponse(prompt)
        #     if not answer:
        #         raise HTTPException(
        #             status_code=502,
        #             detail="Empty response from model."
        #         )

        try:
            answer = await get_openai_response(prompt)

        except HTTPException:
            raise

        except Exception:
            raise HTTPException(status_code=500, detail="Model Generation Error.")

        return answer
    
    except ValueError:
        raise 
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        await conn.close()


