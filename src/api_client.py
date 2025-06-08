# --- START OF FILE src/api_client.py ---
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
import traceback
import google.api_core.exceptions

# Simple cache for API responses
api_cache = {}
cache_file = "api_cache.json"
CACHE_ENABLED_GLOBAL = True

# Load cache if it exists
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r") as f:
            api_cache = json.load(f)
        print(f"API Cache: Loaded {len(api_cache)} items from {cache_file}")
    except Exception as e:
        print(f"API Cache Warning: Could not load API cache from {cache_file}. Error: {e}")
        api_cache = {}


# --- START OF REPLACEMENT for get_cache_key ---
def get_cache_key(model_name, prompt_or_input_list):
    """Generate a cache key based on model and prompt/input list"""
    # Add version prefix for v1.3 chunk-based/markdown-based calls
    cache_prefix = "v1.3_chunk_"
    
    # Handle both string prompts and list inputs (like LlamaIndex nodes)
    if isinstance(prompt_or_input_list, list):
        try:
            # For lists of nodes, serialize their text content to a stable string
            str_parts = []
            for item in prompt_or_input_list:
                if hasattr(item, 'get_content'): # LlamaIndex Node
                    str_parts.append(item.get_content())
                else: # For other list types, just convert to string
                    str_parts.append(str(item))
            input_str = "".join(str_parts)
        except TypeError:
             input_str = str(prompt_or_input_list)
    else:
        # For simple string inputs
        input_str = str(prompt_or_input_list)

    return cache_prefix + hashlib.md5((model_name + input_str).encode('utf-8')).hexdigest()
# --- END OF REPLACEMENT for get_cache_key ---

# --- START OF REPLACEMENT for cached_generate_content ---
def cached_generate_content(model, prompt_or_input_list, section_num=None, cache_enabled=True, max_retries=5, timeout=300):
    """Generate content with caching and exponential backoff for rate limits"""
    global CACHE_ENABLED_GLOBAL
    if not CACHE_ENABLED_GLOBAL:
        cache_enabled = False

    model_name = "unknown_model"
    if hasattr(model, 'model_name'):
        model_name = model.model_name
    elif hasattr(model, '_model_name'):
         model_name = model._model_name

    cache_key = get_cache_key(model_name, prompt_or_input_list)

    if cache_enabled and cache_key in api_cache:
        print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} Using cached response")
        cached_response_data = api_cache[cache_key]
        class CachedResponse:
            def __init__(self, text_data):
                self.text = str(text_data) if text_data is not None else ""
                self.prompt_feedback = None
                self.candidates = []
        return CachedResponse(cached_response_data)

    print(f"API Client: {'Section ' + str(section_num) + ':' if section_num else ''} Calling API directly (Cache {'disabled' if not cache_enabled else 'miss'})")
    time.sleep(random.uniform(1.5, 3.0))
    request_start_time = time.time()
    overall_timeout = timeout

    for retry in range(max_retries):
        current_elapsed = time.time() - request_start_time
        if current_elapsed > overall_timeout:
            error_msg = f"Request timed out after {current_elapsed:.1f} seconds"
            print(f"API Client Error: {error_msg}")
            raise TimeoutError(error_msg)

        try:
            print(f"API Client: API attempt {retry+1}/{max_retries}...")
            
            # This logic now correctly passes the string prompt directly to the API
            # as the new v1.3 functions pre-format the context from nodes into the prompt string.
            response = model.generate_content(prompt_or_input_list)

            if response is None: raise ValueError("API returned None response.")

            response_text = ""
            finish_reason = "UNKNOWN"
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', "NO_REASON")
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts') and candidate.content.parts:
                    response_text = "".join(part.text for part in candidate.content.parts if hasattr(part, 'text'))
                elif finish_reason == "SAFETY":
                     raise google.api_core.exceptions.PermissionDenied(f"Content blocked due to safety settings for section {section_num}.")
            elif hasattr(response, 'text'):
                 response_text = response.text
            
            if not hasattr(response, 'text'):
                 response.text = response_text

            print(f"API Client: API attempt {retry+1} successful. Finish Reason: {finish_reason}. Chars: {len(response_text)}.")

            if cache_enabled and response.text:
                 api_cache[cache_key] = response.text
                 if len(api_cache) % 5 == 0:
                     try:
                         with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
                     except Exception as e: print(f"API Cache Warning: Failed to save API cache: {e}")
            
            return response

        except (google.api_core.exceptions.ResourceExhausted, google.api_core.exceptions.DeadlineExceeded, google.api_core.exceptions.ServiceUnavailable) as e_rate_limit:
            if retry < max_retries - 1:
                wait_time = (5 * (2 ** retry)) + random.uniform(0, 2)
                print(f"API Client Warning: Rate limit/server error hit. Waiting {wait_time:.2f}s before retry {retry+2}/{max_retries}")
                time.sleep(wait_time)
                continue
            else:
                print(f"API Client Error: Max retries reached after API error: {e_rate_limit}")
                raise e_rate_limit

        except Exception as e_general:
            print(f"API Client Error: Unexpected error on attempt {retry+1}/{max_retries}: {e_general}")
            traceback.print_exc()
            raise e_general

    raise Exception(f"API request failed after {max_retries} retries.")
# --- END OF REPLACEMENT for cached_generate_content ---

def create_model_config(temperature=0.5, top_p=0.9, top_k=50):
    """Creates a GenerativeModel instance with specific configuration."""
    model_name = "gemini-1.5-flash-latest" # Using latest Flash model
    print(f"API Client: Creating model: {model_name} with temp={temperature}, top_p={top_p}, top_k={top_k}")
    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=temperature,
                max_output_tokens=8192,
                top_p=top_p,
                top_k=top_k
            ),
             safety_settings=safety_settings
        )
        return model
    except Exception as e:
        print(f"API Client ERROR: Creating model '{model_name}' failed: {e}")
        traceback.print_exc()
        raise

def create_fact_model():
    """Create a conservative model for fact-checking tasks."""
    return create_model_config(temperature=0.2, top_p=0.8, top_k=40)

def create_insight_model():
    """Creates the primary model used for generation and insight tasks."""
    return create_model_config(temperature=0.5, top_p=0.9, top_k=50)

def set_global_cache_state(enabled=True):
    """Enable or disable caching globally"""
    global CACHE_ENABLED_GLOBAL
    CACHE_ENABLED_GLOBAL = enabled
    if not enabled:
         try:
             with open(cache_file, "w") as f: json.dump(api_cache, f, indent=2)
         except Exception as e: print(f"API Cache Warning: Failed to save cache on disable: {e}")
# --- END OF FILE src/api_client.py ---