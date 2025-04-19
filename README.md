---
title: ProfileDash
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: ">=4.0" 
app_file: app.py
pinned: false
---

# ProfileDash

ProfileDash automatically generates comprehensive company profiles by analyzing uploaded PDF documents using Google Generative AI (Gemini). It provides a simple web interface built with Gradio for easy interaction and leverages a Hugging Face Dataset for logging, configuration, and storing results.

## Key Features

*   **LLM-Powered Analysis:** Leverages Google's Gemini models to analyze content from PDF documents.
*   **Gradio Web Interface:** Simple UI for uploading files and monitoring progress.
*   **Multi-PDF Upload:** Supports uploading multiple PDF documents for analysis.
*   **Hugging Face Dataset Integration:**
    *   Stores user activity logs (requires `HF_TOKEN`).
    *   Saves intermediate section outputs and final generated profiles (JSON/HTML).
    *   Loads user access configuration (`permitted_users.json`) from the dataset.
*   **Email Authentication:** Requires authentication using an email address configured in the HF Dataset (or matching a fallback domain) via a code sent using SendGrid.
*   **User-Provided API Key:** Users must provide their own Google AI API key after successful authentication.
*   **Parallel Processing:** Generates different profile sections concurrently for faster results.
*   **Base64 PDF Handling:** Encodes PDFs in base64 for direct processing by the multimodal Gemini API.

## Prerequisites

*   Python (3.10 or newer recommended)
*   `pip` (Python package installer)
*   Git (for cloning the repository)
*   A SendGrid account with an API key and a verified sender email address.
*   A Google AI (Gemini) API Key.
*   A Hugging Face account.
*   A Hugging Face **write** access token (`HF_TOKEN`).
*   A Hugging Face Dataset repository (default `ralfpilarczyk/ProfileDashData`) configured with a `permitted_users.json` file and writable by the `HF_TOKEN`.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url> # Replace with the actual URL
    cd ProfileDash
    ```

2.  **Configure Hugging Face Dataset:**
    *   Ensure you have created a **private** Hugging Face Dataset repository (e.g., `your-username/ProfileDashData`).
    *   In `app.py`, update the `DATASET_REPO_ID` variable to point to your repository ID.
    *   Create a `permitted_users.json` file in the root of your dataset with the following structure:
        ```json
        {
          "allowed_domains": ["yourcompany.com", "anotherdomain.org"],
          "allowed_emails": ["specific.user@example.com"]
        }
        ```
        *(Populate with actual domains/emails allowed to use the app).*

3.  **Create and Activate a Virtual Environment (Recommended):**
    *   **macOS/Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv .venv
        .\.venv\Scripts\activate
        ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (Environment Variables / `.env` File)

Create a file named `.env` in the root directory (`ProfileDash/`) of the project OR set these as environment variables (e.g., Hugging Face Space secrets).

```dotenv
# .env file
SENDGRID_API_KEY=your_actual_sendgrid_api_key_here
HF_TOKEN=your_hugging_face_write_token_here
```

*   Replace placeholders with your actual SendGrid API key and Hugging Face write token.
*   The `HF_TOKEN` needs write access to the configured `DATASET_REPO_ID`.
*   Ensure you have configured a verified sender email address in your SendGrid account (the application uses `ProfileDash.NoReply@gmail.com` by default; change this in `app.py` if needed, but it must match a verified sender in SendGrid).
*   **Note:** The `GOOGLE_API_KEY` is **NOT** configured here; users will enter it via the web interface.

## Running the Application

1.  **Ensure Environment Variables are set** (or `.env` file is present).
2.  **Activate your virtual environment** (if you created one).
3.  **Run the Gradio app:**
    ```bash
    python app.py
    ```
4.  The application will start, and you will see output in your terminal indicating the local URL, typically:
    `Running on local URL: http://0.0.0.0:7860` or `http://127.0.0.1:7860`.
5.  Open this URL in your web browser.

## Authentication Flow

1.  **Enter Email:** Provide your email address. It must be listed in the `allowed_emails` or belong to a domain in the `allowed_domains` within the `permitted_users.json` file hosted on the configured Hugging Face Dataset. (If the dataset config fails to load, it may fall back to the `ALLOWED_DOMAIN` hardcoded in `app.py`).
2.  **Send Code:** Click "Send Code".
3.  **Receive Code:** Check your email inbox (and spam folder) for a 4-digit authentication code. (If SendGrid is not configured correctly or sending fails, the app may display a message and allow using the test code `1234` if enabled).
4.  **Verify Code:** Enter the received code and click "Verify Code".
5.  **Enter API Key:** Upon successful verification, you will be prompted to enter your Google AI API Key.
    *   You can get a key from [Google AI Studio](https://aistudio.google.com/) by signing in, clicking "Get API key", and creating one in a new project. **Copy the key immediately** as it won't be shown again.
6.  **Submit API Key:** Paste your key and click "Submit API Key".

## Usage Instructions

1.  **Upload PDFs:** Once authenticated and the API key is accepted, use the "Upload PDF Documents" area to select the relevant PDF files.
2.  **Generate:** Click the "Generate Profile & Download" button.
3.  **Monitor:** Observe the "Status / Log" area and the progress bar for updates. Profile generation involves analyzing documents, generating sections, and combining them. This can take several minutes depending on document size/complexity and API responsiveness. Logs, intermediate results, and final profiles (JSON/HTML) are saved to the configured Hugging Face Dataset repository during this process.
4.  **Result Access:** Upon completion, the application *attempts* to trigger an email notification (if SendGrid is configured) containing the final HTML profile as an attachment. However, the primary location for the results (HTML and JSON) is the configured Hugging Face Dataset repository (usually in a `results/` folder).
5.  **Reset:** After a run (successful or not), click the "Produce New Profile" button to clear the file input and status log for a new run. Your authentication and API key will remain active for the session.

## Disclaimer

This application is provided under the MIT License. Use is at your own risk. The creators assume no liability for the accuracy, suitability, or consequences of using the generated content or stored data. AI-generated outputs may contain inaccuracies or hallucinations; please verify all information independently before relying on it. Ensure compliance with Google AI's terms of service, Hugging Face's terms, SendGrid's terms, and any data privacy regulations relevant to the documents you upload and the user data logged. You are responsible for securing your Hugging Face Dataset and API keys.

## Known Issues / Future Work

*   Multi-file selection on mobile browsers is often limited by the operating system.
*   Refinement logic (fact-checking, insight improvement) exists in the codebase but is currently inactive in the Gradio UI.
*   Error handling for API issues (rate limits, content blocking) and Hugging Face interactions can be further improved.
*   The automatic email notification might fail silently if SendGrid has issues; relying on the HF Dataset for results is more robust.

---