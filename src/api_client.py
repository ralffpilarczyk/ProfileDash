"""
API Client module for ProfileDash
Handles API interactions with Google Generative AI
"""

import os
import json
import hashlib
import time
import random
import google.generativeai as genai
import traceback # For more detailed error logging
# --- ADD THIS IMPORT ---
import google.api_core.exceptions # Import the specific exceptions module
# --- END OF ADDED IMPORT ---

# Simple cache for API responses
api_cache = {}
cache_file = "api_cache.json"

# Load cache if it exists
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r") as f:
            api_cache = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load API cache from {cache_file}. Error: {e}")
        api_cache = {}

def get_cache_key(model_name, prompt):
    """Generate a cache key based on model and prompt"""
    # Ensure prompt is string for hashing
    prompt_str = str(prompt)
    return hashlib.md5((model_name + prompt_str).encode()).hexdigest()

# --- CORRECTED: REMOVED start_time_ref argument ---
def cached_generate_content(model, prompt, section_num=None, cache_enabled=True, max_retries=5, timeout=120):
    """Generate content with caching and exponential backoff for rate limits"""
    # Use the imported get_elapsed_time from main module (relies on global start time)
    try:
        from .utils import get_elapsed_time
    except ImportError:
        # Fallback timer if import fails (less accurate if script runs long before this)
        _start = time.time()
        def get_elapsed_time():
            elapsed = time.time() - _start
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            return f"{minutes}'{seconds:02d}\""

    if not cache_enabled:
        print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} Cache disabled, calling API directly.")
        time.sleep(2) # Use the configured sleep time even if cache disabled
        return model.generate_content(prompt)

    # Try to get model name robustly
    model_name = "unknown_model"
    if hasattr(model, 'model_name'):
        model_name = model.model_name
    elif hasattr(model, '_model_name'): # Sometimes it's private
         model_name = model._model_name

    cache_key = get_cache_key(model_name, str(prompt))

    if cache_key in api_cache:
        print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} Using cached response")
        cached_response_data = api_cache[cache_key]
        # Create a response-like object with a text attribute
        class CachedResponse:
            def __init__(self, text_data):
                 # Ensure text_data is a string
                self.text = str(text_data) if text_data is not None else ""
                self.prompt_feedback = None # Mimic structure if needed elsewhere
                self.candidates = [] # Mimic structure if needed elsewhere
        return CachedResponse(cached_response_data)

    # --- Pace the API calls ---
    time.sleep(2)  # <<< USING SLEEP TIME OF 2 SECONDS >>>

    request_start_time = time.time() # Time for this specific request attempt cycle
    overall_timeout = timeout  # Overall timeout for this request cycle

    # Try with exponential backoff
    for retry in range(max_retries):
        # Check if we've already exceeded overall timeout for *this request*
        current_elapsed = time.time() - request_start_time
        if current_elapsed > overall_timeout:
            error_msg = f"Request timed out after {current_elapsed:.1f} seconds (limit: {overall_timeout}s)"
            print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} {error_msg}")
            raise TimeoutError(error_msg)

        # Calculate time remaining for this attempt's *check*
        time_left_overall = overall_timeout - current_elapsed
        # The attempt_timeout is just for the check, not a hard limit on the API call itself
        attempt_timeout_check = min(30 * (retry + 1), time_left_overall)

        if attempt_timeout_check <= 0:
             error_msg = f"Not enough time left for attempt {retry+1}/{max_retries} (left: {time_left_overall:.1f}s)"
             print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} {error_msg}")
             raise TimeoutError(error_msg) # Raise timeout if no time left

        try:
            # Log attempt (using the check value for info)
            # --- CORRECTED: Use get_elapsed_time without argument ---
            print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} API attempt {retry+1}/{max_retries}, (time budget check val: {attempt_timeout_check:.1f}s)")

            # --- Make the API call ---
            response = model.generate_content(prompt)
            # --- API Call Succeeded ---

            # Basic check if response is valid before accessing text
            if response is None: raise ValueError("API returned None response.")

            # Check structure more carefully - adapted for potential direct .text access
            response_text = ""
            if hasattr(response, 'text'):
                 response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Check if the first candidate has content and parts
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                    response_text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text')) # Concatenate parts
                else: # Check finish reason if no parts
                    finish_reason = getattr(candidate, 'finish_reason', None)
                    if finish_reason != 1: # 1 is typically "STOP"
                         feedback = getattr(response, 'prompt_feedback', 'No feedback')
                         safety = getattr(candidate, 'safety_ratings', 'No safety ratings')
                         print(f"Warning: API response section {section_num} finish_reason={finish_reason}. Feedback: {feedback}, Safety: {safety}")
                         # Return empty text but don't raise error unless desired
                         response_text = "" # Force empty text
            else: # Completely unexpected structure
                 feedback = getattr(response, 'prompt_feedback', 'No feedback available')
                 print(f"Warning: Unexpected API response structure section {section_num}. Feedback: {feedback}")
                 # Decide behavior: raise error or return empty
                 # raise AttributeError("API response object missing expected structure.")
                 response_text = ""

            # Ensure .text attribute exists, even if empty
            if not hasattr(response, 'text'):
                 # Assign the extracted/default text to the response object if possible
                 # This might fail if the response object is immutable, but worth trying
                 try:
                      response.text = response_text
                 except: # Fallback if assignment fails
                      print(f"Warning: Could not assign .text attribute to response object for section {section_num}.")
                      # Create a simple object with .text if response cannot be modified
                      class SimpleResponse: text = response_text
                      response = SimpleResponse()


            # Cache only if we got some text
            if response.text:
                 api_cache[cache_key] = response.text
                 if len(api_cache) % 5 == 0:
                     try:
                         with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
                     except Exception as e: print(f"Warning: Failed to save API cache: {e}")
            elif not response.text:
                 print(f"Warning: API response for section {section_num} resulted in empty text. Caching skipped.")


            return response # Return the successful response

        except Exception as e:
            # Check if time is up *after* the exception occurred
            request_end_time = time.time()
            if request_end_time - request_start_time > overall_timeout:
                error_msg = f"Request timed out after {request_end_time - request_start_time:.1f}s during attempt {retry+1} (limit: {overall_timeout}s)"
                print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} {error_msg}")
                print(f"Original error before timeout check: {type(e).__name__}: {e}"); traceback.print_exc()
                raise TimeoutError(error_msg) from e

            # Check if this is a rate limit error (429) more robustly
            is_rate_limit = False
            # --- USE THE IMPORTED MODULE HERE ---
            if isinstance(e, google.api_core.exceptions.ResourceExhausted) or "429" in str(e):
                 is_rate_limit = True
            # --- END OF CHANGE ---

            if is_rate_limit and retry < max_retries - 1:
                base_wait = 5; wait_time = (base_wait * (2 ** retry)) + random.uniform(0, 1)
                time_left = overall_timeout - (time.time() - request_start_time); wait_time = min(wait_time, time_left - 1) # Ensure wait doesn't exceed total timeout
                if wait_time <= 0:
                     print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} Rate limit hit, but no time left to wait/retry. Failing."); raise e
                # --- CORRECTED: Use get_elapsed_time without argument ---
                print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} Rate limit hit. Waiting {wait_time:.2f}s before retry {retry+2}/{max_retries}"); time.sleep(wait_time)
                continue
            else:
                # --- CORRECTED: Use get_elapsed_time without argument ---
                print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} Error on API attempt {retry+1}/{max_retries}: {type(e).__name__}: {str(e)}")
                if not is_rate_limit: traceback.print_exc()
                raise e # Re-raise the original error

    # Fallback if loop completes without success
    final_error_msg = f"API request failed after {max_retries} retries."
    print(f"{get_elapsed_time()} {'Section ' + str(section_num) + ':' if section_num else 'Project:'} {final_error_msg}")
    raise Exception(final_error_msg)


def create_model_config(temperature=0.5, top_p=0.8, top_k=40):
    """Create a model with specific generation parameters"""
    model_name = "gemini-2.0-flash"
    print(f"Creating model: {model_name}")
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1, temperature=temperature, max_output_tokens=8192, top_p=top_p, top_k=top_k
            ),
             safety_settings=[ # Standard safety settings
                {"category": c, "threshold": "BLOCK_MEDIUM_AND_ABOVE"} for c in [
                    "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"
                ]
             ]
        )
        return model
    except Exception as e: print(f"ERROR Creating model '{model_name}': {e}"); raise

def create_fact_model():
    """Create a conservative model for fact-checking tasks"""
    return create_model_config(temperature=0.2, top_p=0.8, top_k=40)

def create_insight_model():
    """Create a slightly more creative model for generation/insight"""
    return create_model_config(temperature=0.5, top_p=0.9, top_k=50)

# --- rate_answer function definition is removed ---