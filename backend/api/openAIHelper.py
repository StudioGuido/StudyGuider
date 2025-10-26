import asyncio
from openai import OpenAI


async def get_openai_response(prompt: str) -> str:
    '''
    Sends a prompt to OpenAI and returns the model's response as a string.
    Uses async so the program remains responsive while waiting for the API..
    '''

    def call_openai():
        '''
        Creates an OpenAI client and requests a response for the given prompt.
        Returns the response text if successful, raises an error otherwise.
        '''
        client = OpenAI()
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=prompt
            )
            return response.output_text.strip()
        except Exception as e:
            print("An error occurred:", e)
            raise e

    return await asyncio.to_thread(call_openai)
