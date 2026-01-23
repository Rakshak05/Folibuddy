"""
Gemini API client.
Does ONE job: communicates with Gemini API with retry logic.
No PDF logic, no Pydantic validation, no business logic.
"""

import os
import time
from google import genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
from dotenv import load_dotenv

load_dotenv()


def call_gemini(prompt: str, max_retries: int = 5) -> str:
    """
    Call Gemini API with retry logic for rate limits.
    
    Args:
        prompt: The prompt to send to Gemini
        max_retries: Maximum number of retry attempts
        
    Returns:
        Raw JSON response text from Gemini
        
    Raises:
        ValueError: If API key is not found
        Exception: If all retries fail
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Set GEMINI_API_KEY environment variable."
        )
    
    client = genai.Client(api_key=api_key)
    delay = 2  # Initial delay in seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                },
            )
            return response.text
            
        except (ResourceExhausted, ServiceUnavailable) as e:
            print(f"⚠️ Gemini rate limit (attempt {attempt}/{max_retries}): {e}")
            
            if attempt == max_retries:
                raise e
            
            time.sleep(delay)
            delay *= 2  # Exponential backoff
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            raise e
