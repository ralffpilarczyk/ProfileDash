import gradio as gr
import time
import os
import traceback # For error logging
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
from datetime import datetime # Add import for logging

# --- App Version ---
APP_VERSION = "v1.0.0"
LOG_FILE = "user_log.json"

# --- Import necessary functions from your modules within the 'src' directory ---
try:
    from src.document_processor import load_document_content
    from src.html_generator import create_profile_folder, generate_full_html_profile
    from src.section_processor import generate_initial_section
    from src.section_definitions import sections
    from src.prompts import persona, analysis_specs, output_format
    from src.utils import get_elapsed_time

    # For API key and SendGrid key loading
    from dotenv import load_dotenv
    load_dotenv() # Load .env file for local development

    # --- SendGrid Setup ---
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content

    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDER_EMAIL = "ProfileDash.NoReply@gmail.com" # Your verified SendGrid sender

    if not SENDGRID_API_KEY:
        print("Warning: SENDGRID_API_KEY not found. Set it in .env or HF Secrets.")
    else:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        print("SendGrid client initialized.")

    # --- Google AI Setup (will be configured dynamically) ---
    import google.generativeai as genai
    # No global genai.configure() here anymore

except ImportError as e:
    print(f"Error importing ProfileDash modules: {e}")
    print("Please ensure app.py is in the root directory and the 'src' directory with all modules exists.")
    raise
except Exception as general_e:
    print(f"An unexpected error occurred during setup: {general_e}")
    traceback.print_exc()
    raise

# --- Configuration ---
MAX_WORKERS = 2  # Reduced from 3 to help with rate limiting
MAX_UPLOAD_MB = 20
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_DOMAIN = "sc.com" # Restrict access


# --- Helper Functions ---

def clear_api_cache():
    """Clear the API cache file to ensure fresh document analysis."""
    cache_file = "api_cache.json"
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
            print(f"Successfully deleted API cache file: {cache_file}")
            return True
        except Exception as e:
            print(f"Error deleting API cache file: {e}")
            return False
    else:
        print(f"Cache file {cache_file} not found. No need to clear.")
        return True

def toggle_caching(enable_cache=True):
    """Enable or disable API response caching."""
    try:
        from src.api_client import set_global_cache_state
        cache_state = set_global_cache_state(enable_cache)
        print(f"Global caching {'enabled' if cache_state else 'disabled'}")
        return cache_state
    except ImportError:
        print("Warning: Could not set caching state")
        return False

def generate_auth_code():
    """Generates a 4-digit authentication code."""
    return str(random.randint(1000, 9999))

def log_user_activity(email):
    """Appends user email and timestamp to a JSON log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "email": email
    }
    try:
        # Ensure directory exists if log file is nested
        # os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) # Uncomment if LOG_FILE has path

        # Read existing logs or initialize if file doesn't exist/is empty
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, "r") as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list): # Ensure it's a list
                        logs = []
                except json.JSONDecodeError:
                    logs = [] # Reset if file is corrupt
        else:
            logs = []

        # Append new entry and write back
        logs.append(log_entry)
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
        print(f"Logged activity for: {email}")

    except Exception as e:
        print(f"Error writing to log file {LOG_FILE}: {e}")
        traceback.print_exc()


# --- Authentication Backend ---

def send_auth_code(email, auth_state):
    """Validates email, sends auth code via SendGrid, updates state."""
    if not email or '@' not in email:
        return "Please enter a valid email address.", auth_state, gr.update(visible=True), gr.update(visible=False) # Keep email visible, hide code input

    # Domain Check
    try:
        domain = email.split('@')[1]
        if domain.lower() != ALLOWED_DOMAIN.lower():
            return f"Access denied. Only users from the '{ALLOWED_DOMAIN}' domain are permitted.", auth_state, gr.update(visible=True), gr.update(visible=False)
    except IndexError:
         return "Invalid email format.", auth_state, gr.update(visible=True), gr.update(visible=False)

    if not SENDGRID_API_KEY or not sg:
        # Fallback for local testing if SendGrid isn't configured
        print("Warning: SendGrid not configured. Using dummy code '1234'.")
        code = "1234"
        auth_state["email"] = email
        auth_state["code"] = code
        auth_state["code_sent"] = True
        return "SendGrid not configured. For testing, use code 1234.", auth_state, gr.update(visible=False), gr.update(visible=True) # Hide email, show code

    # Generate and Send Code
    code = generate_auth_code()
    auth_state["email"] = email
    auth_state["code"] = code
    auth_state["code_sent"] = False # Mark as not sent yet

    subject = "Your ProfileDash Authentication Code"
    # Use the HTML drafted earlier
    html_content = f"""
    <div style="font-family: sans-serif; padding: 20px; max-width: 400px; margin: auto; border: 1px solid #ddd; border-radius: 5px;">
        <h2 style="text-align: center; color: #333;">ProfileDash Authentication</h2>
        <p style="text-align: center; color: #555;">Please use the following code to complete your sign-in:</p>
        <div style="font-size: 36px; font-weight: bold; text-align: center; margin: 20px 0; padding: 10px; background-color: #f0f0f0; border-radius: 3px; letter-spacing: 5px;">
            {code}
        </div>
        <p style="font-size: 12px; color: #888; text-align: center;">If you did not request this code, you can safely ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 10px; color: #aaa; text-align: center;">ProfileDash - Automated Company Profiling</p>
    </div>
    """
    message = Mail(
        from_email=Email(SENDER_EMAIL, "ProfileDash"), # Use Email object
        to_emails=To(email), # Use To object
        subject=subject,
        html_content=Content("text/html", html_content) # Use Content object
    )

    try:
        response = sg.client.mail.send.post(request_body=message.get())
        if 200 <= response.status_code < 300:
            print(f"Auth code sent successfully to {email}. Status: {response.status_code}")
            auth_state["code_sent"] = True
            log_user_activity(email) # Log successful attempt
            return f"Authentication code sent to {email}. Please check your inbox and enter the code below.", auth_state, gr.update(visible=False), gr.update(visible=True) # Hide email, show code
        else:
            print(f"Failed to send auth code to {email}. Status: {response.status_code}, Body: {response.body}")
            return f"Error sending authentication code (Status: {response.status_code}). Please try again later.", auth_state, gr.update(visible=True), gr.update(visible=False) # Show email, hide code
    except Exception as e:
        print(f"Exception sending email to {email}: {e}")
        traceback.print_exc()
        return f"An error occurred while sending the email: {e}. Please try again.", auth_state, gr.update(visible=True), gr.update(visible=False) # Show email, hide code

def verify_auth_code(entered_code, auth_state):
    """Verifies the entered code against the stored code."""
    if not auth_state.get("code_sent"):
        return "Please request an authentication code first.", auth_state, gr.update(visible=True), gr.update(visible=True), gr.update(visible=False) # Keep auth visible, hide api key

    stored_code = auth_state.get("code")
    if entered_code == stored_code:
        auth_state["authenticated"] = True
        print(f"Authentication successful for {auth_state.get('email')}")
        return "Authentication successful. Please enter your API Key.", auth_state, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True) # Hide auth, show api key
    else:
        return "Invalid authentication code. Please try again.", auth_state, gr.update(visible=True), gr.update(visible=True), gr.update(visible=False) # Keep auth visible, hide api key


# --- API Key Handling ---

def handle_api_key(api_key, auth_state):
    """Stores the API key in state and proceeds to main app."""
    if not api_key:
        return "API Key cannot be empty.", auth_state, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False) # Keep API Key visible

    # Basic validation (check if it's not empty)
    # A more robust check might try a simple API call, but that costs quota.
    auth_state["api_key"] = api_key
    auth_state["api_key_set"] = True
    print("API Key received and stored in session state.")
    return "API Key accepted. You can now upload documents and generate profiles.", auth_state, gr.update(visible=False), gr.update(visible=True), gr.update(visible=True) # Hide API Key, show Main App

# --- Reset Function ---
def reset_interface():
    """Resets the main app interface components for a new profile generation."""
    # Note: Does NOT reset auth_state (email, authenticated status, api key)
    return (
        None, # pdf_upload
        "",   # status_output
        None, # html_output
        gr.update(value=None, visible=False), # view_profile_button (reset and hide)
    )

# --- Main Gradio Processing Function (Initial Generation) ---
def run_initial_generation(file_paths, auth_state, progress=gr.Progress(track_tqdm=True)):
    """
    Takes uploaded file paths, runs the initial profile generation in parallel,
    yields status updates, and returns the final HTML.
    Uses API Key from auth_state.
    """
    # --- Pre-checks ---
    if not auth_state.get("authenticated") or not auth_state.get("api_key_set"):
        yield "Authentication or API Key setup not complete. Please restart the process.", None, gr.update(visible=False), gr.update(visible=False)
        return "Authentication or API Key setup not complete.", None, gr.update(visible=False), gr.update(visible=False)

    api_key = auth_state.get("api_key")
    if not api_key:
        yield "API Key is missing from session state.", None, gr.update(visible=False), gr.update(visible=False)
        return "API Key is missing.", None, gr.update(visible=False), gr.update(visible=False)

    # --- Clear API Cache to ensure fresh document analysis ---
    status_log = [] # Initialize status log
    
    def append_status(message):
        """Updates status_log with a new message and returns the full log."""
        nonlocal status_log
        timestamped_message = message  # We'll add timestamp later
        status_log.insert(0, timestamped_message)  # Prepend new message
        return "\n".join(status_log[:15])  # Show latest 15 lines
    
    # Clear both the cache file and in-memory cache
    cache_cleared = clear_api_cache()
    if cache_cleared:
        try:
            from src.api_client import api_cache
            api_cache.clear()  # Clear in-memory cache
            status = append_status("API cache cleared (both file and memory). Fresh document analysis will be performed.")
        except Exception as e:
            status = append_status(f"Warning: Could not clear in-memory cache: {e}")
    else:
        status = append_status("Warning: Could not clear API cache file. Results may use cached responses.")
    yield status, None, gr.update(visible=False), gr.update(visible=False)
    
    # Import and disable global caching
    try:
        from src.api_client import set_global_cache_state
        set_global_cache_state(False)  # Disable caching for this run
        status = append_status("Global caching disabled for this run to ensure fresh analysis.")
        yield status, None, gr.update(visible=False), gr.update(visible=False)
    except ImportError:
        status = append_status("Warning: Could not disable global caching. Results may use cached responses.")
        yield status, None, gr.update(visible=False), gr.update(visible=False)

    # --- Configure Google AI Client Dynamically ---
    try:
        print("Attempting to configure Google AI SDK with provided key...")
        genai.configure(api_key=api_key)
        # Test the API with a simple request to ensure it's working
        test_model = genai.GenerativeModel("gemini-2.0-flash")  # Use the same model as production
        test_response = test_model.generate_content("Hello, world!")
        print("Google AI SDK test successful:", test_response.text[:50] + "...")
    except Exception as config_e:
        error_details = f"Error type: {type(config_e).__name__}, Message: {str(config_e)}"
        traceback.print_exc()  # Print full stack trace
        error_msg = f"Error configuring Google AI SDK: {error_details}"
        print(error_msg)
        status = append_status(error_msg + "\nPlease ensure your API Key is valid.")
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)
    # --- End Dynamic Configuration ---

    start_run_time = time.time()
    status_log = [] # Reset status log after initialization

    def get_run_elapsed():
        elapsed = time.time() - start_run_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f"[{minutes}'{seconds:02d}\"]"

    def append_status(message):
        """Updates status_log with a new message and returns the full log."""
        nonlocal status_log
        timestamped_message = f"{get_run_elapsed()} {message}"
        status_log.insert(0, timestamped_message)  # Prepend new message
        return "\n".join(status_log[:15])  # Show latest 15 lines

    # --- Initial Check & Upload Size Validation ---
    if not file_paths:
        status = append_status("No PDF files uploaded. Please upload documents.")
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)

    total_size = 0
    valid_files_info = []
    uploaded_data = {}
    
    print(f"File paths type: {type(file_paths)}")
    
    # Process files based on upload type (binary vs filepath)
    if isinstance(file_paths, list):  # Should be a list with file_count="multiple"
        for file_path in file_paths:
            if file_path:
                print(f"Processing file: {type(file_path)}")
                try:
                    # For binary upload
                    if hasattr(file_path, 'name') and os.path.exists(file_path.name):
                        size = os.path.getsize(file_path.name)
                        orig_name = getattr(file_path, 'orig_name', os.path.basename(file_path.name))
                        total_size += size
                        with open(file_path.name, 'rb') as f:
                            file_content = f.read()
                            uploaded_data[orig_name] = file_content
                        valid_files_info.append((file_path.name, orig_name, size))
                        print(f"Added file: {orig_name}, size: {size // 1024}KB")
                    # For binary data directly
                    elif hasattr(file_path, 'read'):
                        # Create a temporary file
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                        file_data = file_path.read()
                        temp_file.write(file_data)
                        temp_file_path = temp_file.name
                        temp_file.close()
                        
                        size = len(file_data)
                        orig_name = getattr(file_path, 'orig_name', f"uploaded_{len(valid_files_info)}.pdf")
                        total_size += size
                        uploaded_data[orig_name] = file_data
                        valid_files_info.append((temp_file_path, orig_name, size))
                        print(f"Added binary file: {orig_name}, size: {size // 1024}KB")
                except Exception as e:
                    status = append_status(f"Warning: Could not process file: {str(e)}")
                    yield status, None, gr.update(visible=False), gr.update(visible=False)
                    print(f"File processing error: {e}")
                    traceback.print_exc()
    else:  # Handle single file upload case
        if file_paths:
            try:
                # Same logic as above for single file
                if hasattr(file_paths, 'name') and os.path.exists(file_paths.name):
                    size = os.path.getsize(file_paths.name)
                    orig_name = getattr(file_paths, 'orig_name', os.path.basename(file_paths.name))
                    total_size += size
                    with open(file_paths.name, 'rb') as f:
                        file_content = f.read()
                        uploaded_data[orig_name] = file_content
                    valid_files_info.append((file_paths.name, orig_name, size))
                elif hasattr(file_paths, 'read'):
                    # Binary data handling
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    file_data = file_paths.read()
                    temp_file.write(file_data)
                    temp_file_path = temp_file.name
                    temp_file.close()
                    
                    size = len(file_data)
                    orig_name = getattr(file_paths, 'orig_name', f"uploaded_file.pdf")
                    total_size += size
                    uploaded_data[orig_name] = file_data
                    valid_files_info.append((temp_file_path, orig_name, size))
            except Exception as e:
                status = append_status(f"Warning: Could not process file: {str(e)}")
                yield status, None, gr.update(visible=False), gr.update(visible=False)
                print(f"File processing error: {e}")
                traceback.print_exc()

    if total_size > MAX_UPLOAD_BYTES:
        error_msg = f"Upload failed: Total file size ({total_size / (1024*1024):.2f} MB) exceeds the limit of {MAX_UPLOAD_MB} MB."
        status = append_status(error_msg)
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)

    if not valid_files_info:
        status = append_status("No valid PDF files were found or processed.")
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)

    status = append_status(f"Starting processing for {len(valid_files_info)} files (Total Size: {total_size / (1024*1024):.2f} MB)...")
    yield status, None, gr.update(visible=False), gr.update(visible=False)

    # --- Process Uploaded Documents ---
    documents_for_api = []
    company_name = "Uploaded_Company"
    timestamp = time.strftime('%Y%m%d_%H%M%S')

    try:
        status = append_status("Processing uploaded documents...")
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        
        # We already have the uploaded_data from the file processing above
        status = append_status(f"Successfully read {len(uploaded_data)} files. Processing for API...")
        yield status, None, gr.update(visible=False), gr.update(visible=False)

        documents_for_api = load_document_content(uploaded_data)
        if not documents_for_api:
            status = append_status("Failed to process documents into API format.")
            yield status, None, gr.update(visible=False), gr.update(visible=False)
            return status, None, gr.update(visible=False), gr.update(visible=False)

        first_filename = next(iter(uploaded_data.keys()), "Unknown_Company")
        company_name = first_filename.split('.')[0].replace('_', ' ')

        status = append_status(f"Company Name (guess): {company_name}. Starting section generation...")
        yield status, None, gr.update(visible=False), gr.update(visible=False)

    except Exception as e:
        error_msg = f"Error during document processing phase: {str(e)}\n{traceback.format_exc()}"
        status = append_status(error_msg)
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)

    # --- 2. Generate Sections in Parallel ---
    total_sections = len(sections)
    initial_results = {}
    completed_sections = 0

    progress(0, desc="Starting section generation...")
    status = append_status(f"Starting parallel generation for {total_sections} sections (Max Workers: {MAX_WORKERS})... (This may take 10-15 mins)")
    yield status, None, gr.update(visible=False), gr.update(visible=False)

    section_processing_error = False

    try:
        # Create model instance using the proper function
        from src.api_client import create_insight_model
        insight_model = create_insight_model()
        if not insight_model:
            raise Exception("Failed to create insight model instance")

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Pass the model instance to generate_initial_section
            future_to_section = {
                executor.submit(generate_initial_section, section, documents_for_api, persona, analysis_specs, output_format, insight_model): section
                for section in sections
            }

            for future in as_completed(future_to_section):
                section_def = future_to_section[future]
                section_num = section_def["number"]
                section_title = section_def["title"]
                
                try:
                    section_num, content = future.result()
                    if not content or '<p class="error">' in content:
                        if not content:
                            content = f'<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Generation returned empty content.</p></div>'
                        initial_results[section_num] = content
                        status_update = f"PARTIAL FAIL: Section {section_num} ('{section_title}') completed with errors."
                        section_processing_error = True
                    else:
                        initial_results[section_num] = content
                        status_update = f"SUCCESS: Section {section_num} ('{section_title}') generated."

                except Exception as e:
                    original_error_msg = str(e)
                    error_msg = f"FAIL: Section {section_num} ('{section_title}') failed: {original_error_msg}"
                    print(f"{get_elapsed_time()} {error_msg}")
                    error_content = f'''<div class="section" id="section-{section_num}"><h2>{section_num}. {section_title}</h2><p class="error">ERROR: Could not generate content for section {section_num}: {original_error_msg}</p></div>'''
                    initial_results[section_num] = error_content
                    status_update = error_msg
                    section_processing_error = True

                completed_sections += 1
                progress(completed_sections / total_sections, desc=status_update)
                status = append_status(status_update)
                yield status, None, gr.update(visible=False), gr.update(visible=False)

    except Exception as e:
        error_msg = f"Error managing parallel section generation: {str(e)}\n{traceback.format_exc()}"
        status = append_status(error_msg)
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)

    status = append_status("Parallel generation finished. Aggregating final profile...")
    yield status, None, gr.update(visible=False), gr.update(visible=False)
    progress(1.0, desc="Aggregating profile...")

    # --- 3. Aggregate and Generate Final HTML ---
    ordered_initial_contents = []
    for section_def in sorted(sections, key=lambda x: x["number"]):
        sec_num = section_def["number"]
        if sec_num not in initial_results:
            print(f"Warning: Section {sec_num} missing from results! Adding error placeholder.")
            content = f'<div class="section" id="section-{sec_num}"><h2>{sec_num}. {section_def["title"]}</h2><p class="error">ERROR: Content generation result was missing.</p></div>'
            section_processing_error = True
        else:
            content = initial_results[sec_num]
        ordered_initial_contents.append(content)

    final_status_message = "Initial profile generation complete!"
    if section_processing_error:
        final_status_message += " WARNING: One or more sections failed or had errors. Review output carefully."

    status = append_status(final_status_message + " Generating final HTML...")
    yield status, None, gr.update(visible=False), gr.update(visible=False)

    try:
        # Pass APP_VERSION to the HTML generator
        final_html = generate_full_html_profile(company_name, sections, ordered_initial_contents, APP_VERSION)

        # Now make the "View Profile" button visible
        status = append_status(final_status_message)
        yield status, final_html, gr.update(visible=True, interactive=True), gr.update(visible=True)
        # Final return value for the function
        return status, final_html, gr.update(visible=True, interactive=True), gr.update(visible=True)

    except Exception as e:
        error_final = f"Error generating final HTML: {str(e)}\n{traceback.format_exc()}"
        status = append_status(error_final)
        yield status, None, gr.update(visible=False), gr.update(visible=False)
        return status, None, gr.update(visible=False), gr.update(visible=False)


# --- Build the Gradio Blocks Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    # --- State Variables ---
    auth_state = gr.State({
        "email": None,
        "code": None,
        "code_sent": False,
        "authenticated": False,
        "api_key": None,
        "api_key_set": False
    })

    # --- 1. Introduction ---
    with gr.Column(visible=True) as intro_section:
        gr.Markdown(f"""
        # **ProfileDash**
        {APP_VERSION}
        By Ralf Pilarczyk

        ProfileDash automatically generates comprehensive company profiles by analyzing uploaded PDF documents using generative AI.

        This application is provided under the MIT License. Use is at your own risk; the creators assume no liability for the accuracy or consequences of using the generated content.

        ProfileDash utilizes Large Language Models (LLMs). Outputs are generated based on the provided documents but may contain inaccuracies or omissions. Please independently verify all generated information before use.
        """)

    # --- 2. Authentication ---
    with gr.Column(visible=True) as auth_section: # Initially visible
        auth_status = gr.Textbox(label="Authentication Status", value="Start with entering your email address below", interactive=False)
        with gr.Row(visible=True) as email_input_row:
            email_input = gr.Textbox(label="Enter Your Email (@sc.com domain only)", placeholder="your.email@sc.com")
            send_code_button = gr.Button("Send Code")
        with gr.Row(visible=False) as code_input_row: # Initially hidden
            code_input = gr.Textbox(label="Enter 4-Digit Code from Email")
            verify_code_button = gr.Button("Verify Code")

    # --- 3. API Key Input ---
    with gr.Column(visible=False) as api_key_section: # Initially hidden
        gr.Markdown("### Enter Your Google AI API Key")
        api_key_input = gr.Textbox(label="API Key", type="password", placeholder="Paste your API key here")
        gr.Markdown("""
        **How to get your Google AI (Gemini) API Key:**

        If you don't have one, it's easy and free to get started:

        1.  **Go to Google AI Studio:** Visit [https://aistudio.google.com/](https://aistudio.google.com/).
        2.  **Sign In:** Log in using your regular Google (Gmail) account. You may need to agree to their Terms of Service.
        3.  **Get API Key:** Once logged in, look for an option like "Get API key" (often on the left-hand menu or a prominent button).
        4.  **Create Key:** Click on "Create API key in new project". Google AI Studio will generate a new key for you.
        5.  **Copy Your Key:** Immediately copy the generated API key. **Save it securely** like a password – you won't be able to see the full key again!
        6.  **Paste Here:** Paste the copied API key into the field above.

        *Note: Your API key is used directly by your browser to make calls to the Google AI API during profile generation. ProfileDash does not store your key.*
        """)
        submit_api_key_button = gr.Button("Submit API Key")

    # --- 4. Main Application Interface ---
    with gr.Column(visible=False) as main_app_section: # Initially hidden
        gr.Markdown("# ProfileDash - Profile Generator")
        gr.Markdown("Upload PDF documents for the company you want to profile.")
        gr.Markdown(f"**Important:** Initial generation can take 10-15 minutes. Please keep this tab active. Max upload size: {MAX_UPLOAD_MB} MB.")
        gr.Markdown("*Tip: To select multiple files at once: Hold Ctrl (Windows) or Cmd (Mac) while clicking files.*")

        with gr.Row():
            # Inputs
            pdf_upload = gr.File(
                label="Upload PDF Documents",
                file_count="multiple",
                file_types=[".pdf"]
            )
            # Outputs
            with gr.Column(scale=2):
                status_output = gr.Textbox(label="Status / Log", lines=15, interactive=False, max_lines=20)
                progress_bar = gr.Progress(track_tqdm=True) # Explicit progress bar
                # Replace DownloadButton with Button that opens in new tab
                view_profile_button = gr.Button(
                    "View Full Profile",
                    visible=False,
                    interactive=False
                )
                reset_button = gr.Button("Produce New Profile", visible=False) # Hidden initially until profile is generated

        generate_button = gr.Button("Generate Profile", variant="primary")

        # HTML output below button
        html_output = gr.HTML(
            label="Generated Profile Preview",
            elem_classes="profile-preview"  # Add class for styling
        )

        # Add custom CSS for the preview
        gr.HTML("""
            <style>
                .profile-preview {
                    background-color: white !important;
                    color: #212529 !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
                    line-height: 1.6 !important;
                }
                .profile-preview p {
                    color: #343a40 !important;
                    margin-bottom: 1em !important;
                }
                .profile-preview h1, .profile-preview h2, .profile-preview h3 {
                    color: #2c3e50 !important;
                    font-weight: 600 !important;
                }
                .profile-preview .section {
                    margin-bottom: 25px !important;
                    padding-top: 10px !important;
                }
                .profile-preview .section-content {
                    padding-left: 10px !important;
                    border-left: 3px solid #f0f0f0 !important;
                    margin-top: 15px !important;
                }
                .profile-preview table.data-table {
                    border-collapse: collapse !important;
                    width: 100% !important;
                    margin: 20px 0 !important;
                    border: 1px solid #ddd !important;
                }
                .profile-preview th, .profile-preview td {
                    border: 1px solid #ddd !important;
                    padding: 10px 12px !important;
                    text-align: left !important;
                    vertical-align: top !important;
                }
                .profile-preview th {
                    background-color: #f8f9fa !important;
                    font-weight: 600 !important;
                    color: #495057 !important;
                }
                .profile-preview tbody tr:nth-child(even) {
                    background-color: #fdfdfd !important;
                }
                .profile-preview ul, .profile-preview ol {
                    margin-left: 20px !important;
                    padding-left: 15px !important;
                }
                .profile-preview li {
                    margin-bottom: 5px !important;
                }
            </style>
        """)

    # --- Event Handling Logic ---

    # Step 1: Send Auth Code
    send_code_button.click(
        fn=send_auth_code,
        inputs=[email_input, auth_state],
        outputs=[auth_status, auth_state, email_input_row, code_input_row]
    )

    # Step 2: Verify Auth Code
    verify_code_button.click(
        fn=verify_auth_code,
        inputs=[code_input, auth_state],
        outputs=[auth_status, auth_state, auth_section, code_input_row, api_key_section]
    )

    # Step 3: Handle API Key
    submit_api_key_button.click(
        fn=handle_api_key,
        inputs=[api_key_input, auth_state],
        outputs=[auth_status, auth_state, api_key_section, main_app_section, intro_section]
    )

    # Step 4: Generate Profile
    generate_button.click(
        fn=run_initial_generation,
        inputs=[pdf_upload, auth_state],
        outputs=[status_output, html_output, view_profile_button, reset_button],
        show_progress="hidden"
    )

    # Step 5: Reset Button
    reset_button.click(
        fn=reset_interface,
        inputs=[],
        outputs=[pdf_upload, status_output, html_output, view_profile_button]
    )

    # Step 6: View Profile Button
    def open_profile_in_new_tab(html_content):
        if not html_content:
            return None
        # Create a temporary file with the HTML content
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        # Return the path to be opened in a new tab
        return temp_path

    view_profile_button.click(
        fn=open_profile_in_new_tab,
        inputs=[html_output],
        outputs=[view_profile_button],
        js="(path) => { if(path) window.open(path, '_blank'); }"
    )


# --- Launch the Gradio app ---
if __name__ == "__main__":
    demo.queue() # Enable queuing
    demo.launch(share=False, server_name="0.0.0.0") # Allow local network access