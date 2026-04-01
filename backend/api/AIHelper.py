import asyncio
from google import genai 


async def get_gemini_response(prompt: str) -> str:
    '''
    Sends a prompt to Google Gemini and returns the model's response as a string.
    Uses async so the program remains responsive while waiting for the API.
    '''

    def call_gemini():
        '''
        Creates a Gemini client and requests a response for the given prompt.
        Returns the response text if successful, raises an error otherwise.
        '''
        client = genai.Client() 
        try:
            # Updated model name to 3.1-flash-lite
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview", 
                contents=prompt
            )
            return response.text.strip()
            
        except Exception as e:
            print("An error occurred:", e)
            raise e

    return await asyncio.to_thread(call_gemini)