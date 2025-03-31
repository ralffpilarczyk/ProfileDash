---
title: ProfileDash
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.23.1" # Or another recent Gradio 4.x version
app_file: app.py
pinned: false
---

# ProfileDash

ProfileDash automatically generates comprehensive company profiles by analyzing uploaded PDF documents using Google Generative AI (Gemini). It provides a simple web interface built with Gradio for easy interaction.

## Key Features

*   **AI-Powered Analysis:** Leverages Google's Gemini models to analyze content from PDF documents.
*   **Gradio Web Interface:** Simple UI for uploading files and monitoring progress.
*   **Multi-PDF Upload:** Supports uploading multiple PDF documents for analysis.
*   **Email Authentication:** Requires authentication using a company email address (domain restricted) via a code sent using SendGrid.
*   **User-Provided API Key:** Users must provide their own Google AI API key after successful authentication.
*   **Parallel Processing:** Generates different profile sections concurrently for faster results.
*   **Base64 PDF Handling:** Encodes PDFs in base64 for direct processing by the multimodal Gemini API.
*   **Automatic Download:** Automatically triggers the download of the final generated HTML profile upon completion.

## Prerequisites

*   Python (3.10 or newer recommended)
*   `pip` (Python package installer)
*   Git (for cloning the repository)
*   A SendGrid account with an API key and a verified sender email address.
*   A Google AI (Gemini) API Key.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd ProfileDash
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
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

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (`.env` File)

Create a file named `.env` in the root directory (`ProfileDash/`) of the project. Add your SendGrid API key to this file:

```dotenv
# .env file
SENDGRID_API_KEY=your_actual_sendgrid_api_key_here
```

*   Replace `your_actual_sendgrid_api_key_here` with your key obtained from SendGrid.
*   Ensure you have configured a verified sender email address in your SendGrid account (the application uses `ProfileDash.NoReply@gmail.com` by default, change this in `app.py` if needed, but it must match a verified sender in SendGrid).
*   **Note:** The `GOOGLE_API_KEY` is **NOT** configured in the `.env` file; users will enter it via the web interface.

## Running the Application

1.  **Activate your virtual environment** (if you created one).
2.  **Run the Gradio app:**
    ```bash
    python app.py
    ```
3.  The application will start, and you will see output in your terminal indicating the local URL, typically:
    `Running on local URL: http://0.0.0.0:7860` or `http://127.0.0.1:7860`.
4.  Open this URL in your web browser.

## Authentication Flow

1.  **Enter Email:** Provide your company email address (must match the `ALLOWED_DOMAIN` set in `app.py`, currently `sc.com`).
2.  **Send Code:** Click "Send Code".
3.  **Receive Code:** Check your email inbox (and spam folder) for a 4-digit authentication code. (If SendGrid is not configured correctly, the app will display a message and allow using the test code `1234`).
4.  **Verify Code:** Enter the received code and click "Verify Code".
5.  **Enter API Key:** Upon successful verification, you will be prompted to enter your Google AI API Key.
    *   You can get a key from [Google AI Studio](https://aistudio.google.com/) by signing in, clicking "Get API key", and creating one in a new project. **Copy the key immediately** as it won't be shown again.
6.  **Submit API Key:** Paste your key and click "Submit API Key".

## Usage Instructions

1.  **Upload PDFs:** Once authenticated and the API key is accepted, use the "Upload PDF Documents" area to select the relevant PDF files.
    *   *Desktop:* Hold Ctrl (Windows) or Cmd (Mac) while clicking to select multiple files.
    *   *Mobile:* Multi-file selection may be limited. Look for a "Select" option within your phone's file browser if available, otherwise you may need to upload sequentially (less ideal) or use a desktop.
2.  **Generate:** Click the "Generate Profile & Download" button.
3.  **Monitor:** Observe the "Status / Log" area and the progress bar for updates. Profile generation can take 10-15 minutes depending on the number/size of documents and API responsiveness.
4.  **Download:** Once processing is complete, your browser should automatically initiate the download of the generated HTML file (e.g., `CompanyName_Profile_Timestamp.html`). Check your browser's downloads.
5.  **Reset:** After a profile is generated (or if you want to start over), click the "Produce New Profile" button to clear the file input and status log for a new run. Your authentication and API key will remain active for the session.

## Disclaimer

This application is provided under the MIT License. Use is at your own risk. The creators assume no liability for the accuracy, suitability, or consequences of using the generated content. AI-generated outputs may contain inaccuracies or hallucinations; please verify all information independently before relying on it. Ensure compliance with Google AI's terms of service and any data privacy regulations relevant to the documents you upload.

## Known Issues / Future Work

*   Multi-file selection on mobile browsers (especially iOS) is often limited by the operating system.
*   Refinement logic (fact-checking, insight improvement) exists in the codebase but is currently inactive in the Gradio UI. It could be integrated in future versions.
*   Error handling for API issues (rate limits, content blocking) can be further improved with more specific user feedback.

---