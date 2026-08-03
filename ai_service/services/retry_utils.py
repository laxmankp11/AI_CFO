"""
Retry utility with exponential backoff for Gemini API rate limiting.
"""
import time
import re

def call_with_retry(fn, max_retries=3, initial_delay=8):
    """
    Wraps a callable and retries on 429 RESOURCE_EXHAUSTED errors.
    Uses exponential backoff: 8s -> 16s -> 32s.
    Also tries to parse the retry delay from the error message.
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                last_exception = e
                if attempt < max_retries:
                    # Try to parse server-suggested delay
                    match = re.search(r'retry in (\d+\.?\d*)', error_str, re.IGNORECASE)
                    if match:
                        delay = float(match.group(1)) + 1  # Add 1s buffer
                    else:
                        delay = initial_delay * (2 ** attempt)
                    print(f"  ⏳ Rate limited (attempt {attempt+1}/{max_retries+1}). Retrying in {delay:.0f}s...")
                    time.sleep(delay)
                else:
                    raise last_exception
            else:
                raise  # Non-rate-limit error, propagate immediately
