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
import google.api_core.exceptions # Import the specific exceptions module

# Dictionary to store cached API responses, mapping hash keys to response text.
api_cache = {}
# Filename for persisting the API cache.
cache_file = "api_cache.json"
# Global flag to enable/disable caching behavior.
CACHE_ENABLED_GLOBAL = True

# Load cache from file upon initialization if it exists.
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r") as f:
            api_cache = json.load(f)
        print(f"API Cache: Loaded {len(api_cache)} items from {cache_file}")
    except Exception as e:
        print(f"API Cache Warning: Could not load API cache from {cache_file}. Error: {e}")
        api_cache = {}

def get_cache_key(model_name, prompt_or_input_list):
    """Generate a cache key based on model and prompt/input list"""
    # Ensure consistent hashing regardless of input type (string or list).
    if isinstance(prompt_or_input_list, list):
        # Serialize list, sorting dictionary keys for stability.
        try:
            input_str = json.dumps(prompt_or_input_list, sort_keys=True)
        except TypeError: # Fallback for potentially non-serializable items.
             input_str = str(prompt_or_input_list)
    else:
        input_str = str(prompt_or_input_list)

    return hashlib.md5((model_name + input_str).encode('utf-8')).hexdigest()

def cached_generate_content(model, prompt_or_input_list, section_num=None, cache_enabled=True, max_retries=5, timeout=300):
    """Generate content with caching and exponential backoff for rate limits"""
    # Honor the global cache disable setting.
    global CACHE_ENABLED_GLOBAL
    if not CACHE_ENABLED_GLOBAL:
        cache_enabled = False

    # Attempt to retrieve the model name for caching purposes.
    model_name = "unknown_model"
    if hasattr(model, 'model_name'):
        model_name = model.model_name
    elif hasattr(model, '_model_name'): # Access private attribute if public one isn't available.
         model_name = model._model_name

    cache_key = get_cache_key(model_name, prompt_or_input_list)

    if cache_enabled and cache_key in api_cache:
        print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} Using cached response")
        cached_response_data = api_cache[cache_key]
        # Simulate the structure of a typical API response object for consistency.
        class CachedResponse:
            def __init__(self, text_data):
                self.text = str(text_data) if text_data is not None else ""
                self.prompt_feedback = None # Mimic attributes found in actual responses.
                self.candidates = [] # Mimic attributes found in actual responses.
        return CachedResponse(cached_response_data)

    print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} Calling API directly (Cache {'disabled' if not cache_enabled else 'miss'})")

    # Introduce a small random delay to avoid overwhelming the API endpoint.
    time.sleep(random.uniform(1.5, 3.0))

    request_start_time = time.time()
    overall_timeout = timeout

    # Retry loop with exponential backoff for handling transient API errors.
    for retry in range(max_retries):
        current_elapsed = time.time() - request_start_time
        if current_elapsed > overall_timeout:
            error_msg = f"Request timed out after {current_elapsed:.1f} seconds (limit: {overall_timeout}s)"
            print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} {error_msg}")
            raise TimeoutError(error_msg)

        # Verify sufficient time remains before the next attempt.
        time_left_overall = overall_timeout - current_elapsed
        if time_left_overall <= 1.0:
             error_msg = f"Not enough time left for API attempt {retry+1}/{max_retries} (left: {time_left_overall:.1f}s)"
             print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} {error_msg}")
             raise TimeoutError(error_msg)

        try:
            print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} API attempt {retry+1}/{max_retries}...")

            # Make the actual call to the generative AI model.
            response = model.generate_content(prompt_or_input_list)

            if response is None: raise ValueError("API returned None response.")

            # Process the response to extract text, finish reason, and safety ratings.
            response_text = ""
            finish_reason = "UNKNOWN"
            safety_ratings = "UNKNOWN"

            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', "NO_REASON")
                safety_ratings = getattr(candidate, 'safety_ratings', "NO_RATINGS")

                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                    response_text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                elif finish_reason != 1 and finish_reason != "STOP": # Check for abnormal finish reasons (1 or "STOP" are normal).
                     print(f"API Client Warning: Section {section_num} finished with reason '{finish_reason}'. Safety: {safety_ratings}. No text parts found.")
                     # Explicitly handle safety blocks.
                     if finish_reason == "SAFETY":
                          raise google.api_core.exceptions.PermissionDenied(f"Content blocked due to safety settings for section {section_num}. Ratings: {safety_ratings}")
                     response_text = "" # Ensure empty text for other non-stop reasons without parts.
                # else: Normal stop but no parts, text remains "".
            elif hasattr(response, 'text'): # Handle simpler response structures.
                 response_text = response.text
                 finish_reason = "SIMPLE_TEXT_RESPONSE"
            else: # Log unexpected structures.
                 print(f"API Client Warning: Unexpected API response structure section {section_num}. Feedback: {getattr(response, 'prompt_feedback', 'N/A')}")
                 response_text = ""

            # Ensure the response object has a `.text` attribute for consistent handling downstream.
            if not hasattr(response, 'text'):
                 try: response.text = response_text
                 except: pass # Ignore errors if the object is immutable.

            print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} API attempt {retry+1} successful. Finish Reason: {finish_reason}. Chars: {len(response_text)}.")

            # Store the successful response text in the cache if enabled.
            if cache_enabled and response.text:
                 api_cache[cache_key] = response.text
                 # Periodically save the cache to disk to prevent data loss.
                 if len(api_cache) % 5 == 0: # Save every 5 new cache entries.
                     try:
                         with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
                         print(f"API Cache: Saved {len(api_cache)} items to {cache_file}")
                     except Exception as e: print(f"API Cache Warning: Failed to save API cache: {e}")
            elif cache_enabled and not response.text:
                 print(f"API Client Warning: Section {section_num} resulted in empty text. Caching skipped.")

            return response # Return the successful response object.

        except (google.api_core.exceptions.ResourceExhausted, google.api_core.exceptions.DeadlineExceeded, google.api_core.exceptions.ServiceUnavailable) as e_rate_limit:
            # Handle specific API errors that are potentially retriable (e.g., rate limits, server issues).
            if retry < max_retries - 1:
                base_wait = 5
                # Calculate wait time with exponential backoff and jitter.
                wait_time = (base_wait * (2 ** retry)) + random.uniform(0, 2)
                # Cap wait time to not exceed the overall request timeout.
                time_left = overall_timeout - (time.time() - request_start_time)
                wait_time = min(wait_time, max(0, time_left - 1)) # Ensure at least 1s buffer before timeout.

                if wait_time <= 0:
                     print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Rate limit/server error hit ({type(e_rate_limit).__name__}), but no time left to wait/retry. Failing.")
                     raise e_rate_limit # Re-raise the error if no time left.
                print(f"API Client Warning: {'Section ' + str(section_num) + ':' if section_num else ''} Rate limit/server error hit ({type(e_rate_limit).__name__}). Waiting {wait_time:.2f}s before retry {retry+2}/{max_retries}")
                time.sleep(wait_time)
                continue # Proceed to the next retry attempt.
            else:
                # If max retries are exhausted for a retriable error, raise it.
                print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Max retries ({max_retries}) reached after API error: {type(e_rate_limit).__name__}: {str(e_rate_limit)}")
                raise e_rate_limit

        except google.api_core.exceptions.PermissionDenied as e_perm:
             # Handle non-retriable permission errors (e.g., safety blocks).
            print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Permission Denied / Safety Block: {str(e_perm)}")
            traceback.print_exc()
            raise e_perm # Re-raise immediately.

        except Exception as e_general:
             # Catch any other unexpected exceptions during the API call.
            print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Unexpected error on attempt {retry+1}/{max_retries}: {type(e_general).__name__}: {str(e_general)}")
            traceback.print_exc()
            # Check for timeout condition during exception handling itself.
            if time.time() - request_start_time > overall_timeout:
                 print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Request timed out during error handling.")
                 raise TimeoutError("Request timed out during error handling") from e_general
            # General errors are typically not retried.
            raise e_general

    # This point should ideally not be reached if exceptions are handled correctly above.
    final_error_msg = f"API request failed after {max_retries} retries for section {section_num}."
    print(f"API Client Error: {final_error_msg}")
    raise Exception(final_error_msg)

def create_model_config(temperature=0.5, top_p=0.9, top_k=50):
    """Creates a GenerativeModel instance with specific configuration."""
    # Using gemini-2.0-flash as a good balance of capability and speed/cost
    # Adjust model_name if you specifically need Pro or another variant
    model_name = "gemini-2.0-flash"
    print(f"API Client: Creating model: {model_name} with temp={temperature}, top_p={top_p}, top_k={top_k}")
    try:
        # Configure safety settings to block potentially harmful content.
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=temperature,
                max_output_tokens=8192, # Maximum output tokens for the selected model.
                top_p=top_p,
                top_k=top_k
            ),
             safety_settings=safety_settings
        )
        return model
    except Exception as e:
        print(f"API Client ERROR: Creating model '{model_name}' failed: {e}")
        traceback.print_exc()
        raise # Critical error, stop execution if model cannot be created.

def create_fact_model():
    """Create a conservative model for fact-checking tasks (Lower temperature)."""
    # Configured for higher precision, lower creativity.
    return create_model_config(temperature=0.2, top_p=0.8, top_k=40)

def create_insight_model():
    """Creates the primary model used for initial section generation."""
    # Configured for a balance between creativity and coherence.
    return create_model_config(temperature=0.5, top_p=0.9, top_k=50)

# Utility function to control the global caching flag.
def set_global_cache_state(enabled=True):
    """Enable or disable caching globally"""
    global CACHE_ENABLED_GLOBAL
    CACHE_ENABLED_GLOBAL = enabled
    state_msg = 'ENABLED' if enabled else 'DISABLED'
    print(f"API Cache: Global API cache state set to: {state_msg}")
    # Persist the current cache content to disk when disabling caching globally.
    if not enabled:
         try:
             with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
             print(f"API Cache: Saved cache to {cache_file} while disabling.")
         except Exception as e: print(f"API Cache Warning: Failed to save cache on disable: {e}")
    return CACHE_ENABLED_GLOBAL