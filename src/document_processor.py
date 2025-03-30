"""
Document processing module for ProfileDash
Handles document upload and preprocessing using base64 encoding for Gemini.
"""

import os
import base64
import traceback

# upload_documents (tkinter) and get_current_documents (global state) are removed.

def load_document_content(uploaded_data):
    """
    Process uploaded documents (passed as a dict of filename: bytes)
    and convert to base64 format needed for the Gemini API multi-modal input.

    Args:
        uploaded_data (dict): Dictionary where keys are filenames and values
                              are the binary content (bytes) of the PDF files.

    Returns:
        list: A list of document dictionaries suitable for the Generative AI API,
              e.g., [{'mime_type': 'application/pdf', 'data': 'base64encodedstring...'}]
              Returns an empty list if no documents could be processed.
    """
    documents_for_api = []
    # Print message confirming THIS version is running
    print(f"Document Processor: Starting base64 encoding for {len(uploaded_data)} files...")

    for filename, file_content_bytes in uploaded_data.items():
        # Print message confirming loop within THIS version
        print(f"Document Processor: Encoding file '{filename}'...")
        try:
            if not file_content_bytes:
                print(f"Document Processor Warning: Skipping empty file {filename}.")
                continue

            # Encode the binary content to base64
            encoded_content = base64.standard_b64encode(file_content_bytes).decode("utf-8")

            # Add document with base64 encoded data and correct mime type
            documents_for_api.append({
                'mime_type': 'application/pdf', # Crucial for Gemini to recognize it
                'data': encoded_content
            })
            print(f"Document Processor: Successfully encoded {filename} ({len(file_content_bytes)} bytes).")

        except Exception as e:
            print(f"Document Processor Error processing document {filename} for base64 encoding: {type(e).__name__} - {e}")
            traceback.print_exc()
            continue # Skip this document on error

    if not documents_for_api:
        print("Document Processor Warning: No documents were successfully processed and encoded.")

    print(f"Document Processor: Finished processing. {len(documents_for_api)} documents ready for API.")
    return documents_for_api