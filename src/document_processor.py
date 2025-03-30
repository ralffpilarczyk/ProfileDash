"""
Document processing module for ProfileDash
Handles document upload and preprocessing
"""

import os
import base64
import tkinter as tk
from tkinter import filedialog
from .html_generator import extract_text_from_html

def upload_documents():
    """
    Open a file dialog to select PDF files
    Returns a dictionary of filename: content pairs
    """
    # Create and hide the root window
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog
    files = filedialog.askopenfilenames(
        title='Select PDF files',
        filetypes=[('PDF files', '*.pdf')]
    )
    
    # Create a dictionary similar to files.upload() return format
    uploaded = {}
    for file_path in files:
        with open(file_path, 'rb') as file:
            filename = os.path.basename(file_path)  # Get just the filename
            uploaded[filename] = file.read()
    
    # Print info about uploaded files
    for fn in uploaded.keys():
        print('User uploaded file "{name}" with length {length} bytes'.format(
            name=fn, length=len(uploaded[fn])))
    
    return uploaded


# Global variable to store current documents
_current_documents = []

def get_current_documents():
    """Return a copy of the current documents"""
    return _current_documents.copy()

def load_document_content(uploaded):
    """
    Process uploaded documents and convert to format needed for API
    Returns a list of document dictionaries with extracted text
    """
    global _current_documents
    documents = []
    
    for fn in uploaded.keys():
        file_content = uploaded[fn]
        try:
            # Extract text from PDF
            text_content = extract_text_from_html(file_content)
            if not text_content:
                print(f"Warning: No text content extracted from {fn}")
                continue
                
            # Add document with extracted text
            documents.append({
                'mime_type': 'text/plain',
                'data': text_content
            })
        except Exception as e:
            print(f"Error processing document {fn}: {e}")
            continue
    
    # Store documents in global variable for later access
    _current_documents = documents
    
    if not documents:
        print("Warning: No documents were successfully processed")
    
    return documents