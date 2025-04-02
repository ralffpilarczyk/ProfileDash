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

# Simple cache for API responses
api_cache = {}
cache_file = "api_cache.json"
CACHE_ENABLED_GLOBAL = True # Keep global switch if needed later

# Load cache if it exists
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
    # Handle both string prompts and list inputs (for multimodal)
    if isinstance(prompt_or_input_list, list):
        # Create a stable string representation of the list
        # For dictionaries (like document parts), sort keys for consistency
        try:
            input_str = json.dumps(prompt_or_input_list, sort_keys=True)
        except TypeError: # Handle potential non-serializable items if necessary
             input_str = str(prompt_or_input_list)
    else:
        input_str = str(prompt_or_input_list)

    return hashlib.md5((model_name + input_str).encode('utf-8')).hexdigest()

def cached_generate_content(model, prompt_or_input_list, section_num=None, cache_enabled=True, max_retries=5, timeout=300): # Increased default timeout
    """Generate content with caching and exponential backoff for rate limits"""
    # Check global cache setting - if globally disabled, override local setting
    global CACHE_ENABLED_GLOBAL
    if not CACHE_ENABLED_GLOBAL:
        cache_enabled = False

    # Removed utils.get_elapsed_time dependency

    # Try to get model name robustly
    model_name = "unknown_model"
    if hasattr(model, 'model_name'):
        model_name = model.model_name
    elif hasattr(model, '_model_name'): # Sometimes it's private
         model_name = model._model_name

    cache_key = get_cache_key(model_name, prompt_or_input_list)

    if cache_enabled and cache_key in api_cache:
        print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} Using cached response")
        cached_response_data = api_cache[cache_key]
        # Create a response-like object with a text attribute
        class CachedResponse:
            def __init__(self, text_data):
                self.text = str(text_data) if text_data is not None else ""
                self.prompt_feedback = None # Mimic structure if needed
                self.candidates = [] # Mimic structure if needed
        return CachedResponse(cached_response_data)

    # If not cached or cache disabled:
    print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} Calling API directly (Cache {'disabled' if not cache_enabled else 'miss'})")

    # --- Pace the API calls ---
    time.sleep(random.uniform(1.5, 3.0)) # Slightly increased random sleep

    request_start_time = time.time() # Time for this specific request attempt cycle
    overall_timeout = timeout  # Overall timeout for this request cycle

    # Try with exponential backoff
    for retry in range(max_retries):
        current_elapsed = time.time() - request_start_time
        if current_elapsed > overall_timeout:
            error_msg = f"Request timed out after {current_elapsed:.1f} seconds (limit: {overall_timeout}s)"
            print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} {error_msg}")
            raise TimeoutError(error_msg)

        # Check time left before attempting
        time_left_overall = overall_timeout - current_elapsed
        if time_left_overall <= 1.0: # Need at least a second
             error_msg = f"Not enough time left for API attempt {retry+1}/{max_retries} (left: {time_left_overall:.1f}s)"
             print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} {error_msg}")
             raise TimeoutError(error_msg)

        try:
            print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} API attempt {retry+1}/{max_retries}...")

            # --- Make the API call ---
            # Pass the prompt or the list directly
            response = model.generate_content(prompt_or_input_list)
            # --- API Call Succeeded ---

            if response is None: raise ValueError("API returned None response.")

            # Extract text, handling potential lack of parts or different finish reasons
            response_text = ""
            finish_reason = "UNKNOWN"
            safety_ratings = "UNKNOWN"

            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', "NO_REASON")
                safety_ratings = getattr(candidate, 'safety_ratings', "NO_RATINGS")

                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                    response_text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                elif finish_reason != 1 and finish_reason != "STOP": # 1 or "STOP" is normal
                     print(f"API Client Warning: Section {section_num} finished with reason '{finish_reason}'. Safety: {safety_ratings}. No text parts found.")
                     # Optionally check safety ratings for blocks
                     if finish_reason == "SAFETY": # Specific check for safety blocks
                          raise google.api_core.exceptions.PermissionDenied(f"Content blocked due to safety settings for section {section_num}. Ratings: {safety_ratings}")
                     response_text = "" # Return empty text for other non-stop reasons without parts
                # else: Normal stop but no parts, text remains ""
            elif hasattr(response, 'text'): # Fallback if structure is simpler
                 response_text = response.text
                 finish_reason = "SIMPLE_TEXT_RESPONSE"
            else: # Unexpected structure
                 print(f"API Client Warning: Unexpected API response structure section {section_num}. Feedback: {getattr(response, 'prompt_feedback', 'N/A')}")
                 response_text = ""

            # Assign text to response object if it wasn't there directly (best effort)
            if not hasattr(response, 'text'):
                 try: response.text = response_text
                 except: pass # Ignore if response object is immutable

            print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} API attempt {retry+1} successful. Finish Reason: {finish_reason}. Chars: {len(response_text)}.")

            # Cache the response text if successful and cache is enabled
            if cache_enabled and response.text:
                 api_cache[cache_key] = response.text
                 # Save cache periodically to avoid data loss on interruption
                 if len(api_cache) % 5 == 0: # Save every 5 new entries
                     try:
                         with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
                         print(f"API Cache: Saved {len(api_cache)} items to {cache_file}")
                     except Exception as e: print(f"API Cache Warning: Failed to save API cache: {e}")
            elif cache_enabled and not response.text:
                 print(f"API Client Warning: Section {section_num} resulted in empty text. Caching skipped.")


            return response # Return the successful response object

        except (google.api_core.exceptions.ResourceExhausted, google.api_core.exceptions.DeadlineExceeded, google.api_core.exceptions.ServiceUnavailable) as e_rate_limit:
            # Specific handling for retriable API errors (like 429 Rate Limit, 503 Service Unavailable)
            if retry < max_retries - 1:
                base_wait = 5
                # Exponential backoff with jitter
                wait_time = (base_wait * (2 ** retry)) + random.uniform(0, 2)
                # Ensure wait doesn't exceed remaining timeout
                time_left = overall_timeout - (time.time() - request_start_time)
                wait_time = min(wait_time, max(0, time_left - 1)) # Leave 1s buffer

                if wait_time <= 0:
                     print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Rate limit/server error hit ({type(e_rate_limit).__name__}), but no time left to wait/retry. Failing.")
                     raise e_rate_limit # Re-raise the specific error
                print(f"API Client Warning: {'Section ' + str(section_num) + ':' if section_num else ''} Rate limit/server error hit ({type(e_rate_limit).__name__}). Waiting {wait_time:.2f}s before retry {retry+2}/{max_retries}")
                time.sleep(wait_time)
                continue # Go to the next retry iteration
            else:
                # Max retries reached for a retriable error
                print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Max retries ({max_retries}) reached after API error: {type(e_rate_limit).__name__}: {str(e_rate_limit)}")
                raise e_rate_limit # Re-raise the error

        except google.api_core.exceptions.PermissionDenied as e_perm:
             # Content blocked by safety or other permission issues - Not retriable
            print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Permission Denied / Safety Block: {str(e_perm)}")
            traceback.print_exc()
            raise e_perm # Re-raise immediately

        except Exception as e_general:
             # Handle other unexpected errors during the API call
            print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Unexpected error on attempt {retry+1}/{max_retries}: {type(e_general).__name__}: {str(e_general)}")
            traceback.print_exc()
            # Check if timeout occurred during the exception handling itself
            if time.time() - request_start_time > overall_timeout:
                 print(f"API Client Error: {'Section ' + str(section_num) + ':' if section_num else ''} Request timed out during error handling.")
                 raise TimeoutError("Request timed out during error handling") from e_general
            # Decide if this general error is worth retrying (less likely)
            # For now, re-raise immediately for most general errors
            raise e_general # Re-raise the original error

    # Fallback if loop completes without success (should theoretically be caught by exceptions)
    final_error_msg = f"API request failed after {max_retries} retries for section {section_num}."
    print(f"API Client Error: {final_error_msg}")
    raise Exception(final_error_msg)


def create_model_config(temperature=0.5, top_p=0.9, top_k=50): # Adjusted defaults based on 'Old version'
    """Creates a GenerativeModel instance with specific configuration."""
    # Using gemini-2.0-flash as a good balance of capability and speed/cost
    # Adjust model_name if you specifically need Pro or another variant
    model_name = "gemini-2.0-flash"
    print(f"API Client: Creating model: {model_name} with temp={temperature}, top_p={top_p}, top_k={top_k}")
    try:
        # Define safety settings - BLOCK_MEDIUM_AND_ABOVE is a reasonable default
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
                max_output_tokens=8192, # Max for Flash
                top_p=top_p,
                top_k=top_k
            ),
             safety_settings=safety_settings
        )
        return model
    except Exception as e:
        print(f"API Client ERROR: Creating model '{model_name}' failed: {e}")
        traceback.print_exc()
        raise # Re-raise the exception to prevent app from continuing without a model

def create_fact_model():
    """Create a conservative model for fact-checking tasks (Lower temperature)."""
    # Kept for potential future use of refinement
    return create_model_config(temperature=0.2, top_p=0.8, top_k=40)

def create_insight_model():
    """Creates the primary model used for initial section generation."""
    # Using the parameters from the 'Old version' api_client.py
    return create_model_config(temperature=0.5, top_p=0.9, top_k=50)

# Function to set global cache state (kept if useful for debugging)
def set_global_cache_state(enabled=True):
    """Enable or disable caching globally"""
    global CACHE_ENABLED_GLOBAL
    CACHE_ENABLED_GLOBAL = enabled
    state_msg = 'ENABLED' if enabled else 'DISABLED'
    print(f"API Cache: Global API cache state set to: {state_msg}")
    # Try to save cache when disabled to persist current state
    if not enabled:
         try:
             with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
             print(f"API Cache: Saved cache to {cache_file} while disabling.")
         except Exception as e: print(f"API Cache Warning: Failed to save cache on disable: {e}")
    return CACHE_ENABLED_GLOBAL