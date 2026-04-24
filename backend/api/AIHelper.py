import asyncio
from google import genai
from google.genai import errors as genai_errors
import logging
import uuid

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 4
BASE_BACKOFF_SECONDS = 0.5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


async def get_gemini_response(prompt: str) -> str:
    '''
    Sends a prompt to Gemini and returns the model's response as a string.
    Retries with exponential backoff on transient upstream errors
    (503 overloaded, 429 rate limit, 5xx). Non-retryable errors raise
    immediately.
    '''
    request_id = str(uuid.uuid4())

    logger.info(f"[{request_id}] Starting Gemini request")
    logger.debug(f"[{request_id}] Prompt preview: {prompt[:100]}")

    def call_gemini():
        client = genai.Client()
        logger.info(f"[{request_id}] Calling Gemini API...")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
        )

        if not response.text:
            logger.warning(f"[{request_id}] Gemini returned empty response")
            return ""

        logger.debug(f"[{request_id}] Response preview: {response.text[:100]}")
        return response.text.strip()

    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            result = await asyncio.to_thread(call_gemini)
            logger.info(
                f"[{request_id}] Gemini request succeeded on attempt {attempt}"
            )
            return result
        except genai_errors.APIError as e:
            last_error = e
            status_code = getattr(e, "code", None) or 0
            if status_code not in RETRYABLE_STATUS_CODES or attempt == MAX_ATTEMPTS:
                logger.error(
                    f"[{request_id}] Gemini failed (status={status_code}) on attempt {attempt}; not retrying"
                )
                raise
            delay = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                f"[{request_id}] Gemini status={status_code} on attempt {attempt}; retrying in {delay:.1f}s"
            )
            await asyncio.sleep(delay)
        except Exception:
            logger.exception(f"[{request_id}] Gemini call raised non-API exception")
            raise

    # Loop should always either return or raise — this is defensive.
    assert last_error is not None
    raise last_error
