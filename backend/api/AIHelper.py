import asyncio
from google import genai 
import logging

logger = logging.getLogger(__name__)

async def get_gemini_response(prompt: str) -> str:
    '''
    Sends a prompt to Gemini and returns the model's response as a string.
    Uses async so the program remains responsive while waiting for the API.
    '''
    logger.info("Starting Gemini request")
    logger.debug(f"Prompt preview: {prompt[:100]}")

    def call_gemini():
        '''
        Creates an Gemini client and requests a response for the given prompt.
        Returns the response text if successful, raises an error otherwise.
        '''
        client = genai.Client() 
        try:
            logger.info("Calling Gemini API...")
            response = client.models.generate_content(
                model= "gemini-3.1-flash-lite-preview", 
                contents=prompt)
            
            logger.info("Gemini response received")
            
            if not response.text:
                logger.warning("Gemini returned empty response")
                return ""

            logger.debug(f"Response preview: {response.text[:100]}")
            return response.text.strip()
            
        except Exception as e:
            print("An error occurred:", e)
            raise e

    result = await asyncio.to_thread(call_gemini)
    logger.info("Finished Gemini request")
    return result
