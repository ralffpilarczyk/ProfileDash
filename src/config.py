"""
Central configuration constants for ProfileDash.
This module contains values that need to be read by multiple modules.
Keeping them here avoids circular-import issues (e.g. importing from app.py during
initialisation).
"""

import os

# Default Gemini model to use for all Google Generative AI calls.
# Can be overridden at runtime via the GEMINI_MODEL_NAME environment variable.
GEMINI_MODEL_NAME: str = os.getenv(
    "GEMINI_MODEL_NAME", "gemini-2.0-flash"
) 