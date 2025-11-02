

import asyncio
from google import genai 


async def get_gemini_response(prompt: str) -> str:
    '''
    Sends a prompt to OpenAI and returns the model's response as a string.
    Uses async so the program remains responsive while waiting for the API.
    '''

    def call_gemini():
        '''
        Creates an OpenAI client and requests a response for the given prompt.
        Returns the response text if successful, raises an error otherwise.
        '''
        client = genai.Client() 
        try:
            response = client.models.generate_content(
                model= "gemini-2.0-flash", 
                contents=prompt
            )
            return response.text.strip()
            
        except Exception as e:
            print("An error occurred:", e)
            raise e

    return await asyncio.to_thread(call_gemini)
