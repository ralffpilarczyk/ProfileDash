# ProfileDash

A Gemini-powered tool for generating initial drafts of comprehensive company profiles from corporate documents such as annual reports and quarterly financial filings. Designed for M&A practitioners and investment banking professionals.

## Overview

ProfileDash analyzes PDF documents such as annual reports, investor presentations, and other corporate materials to generate structured company profiles with detailed sections covering operations, financials, strategy, and competitive positioning.

## Repository Structure

- **src/**: Source code directory
  - `profile_dash.py`: Main application entry point
  - `document_processor.py`: Handles document upload and parsing
  - `api_client.py`: Manages API interactions with Google Generative AI
  - `html_generator.py`: Creates formatted HTML output
  - `section_processor.py`: Processes individual profile sections
  - `section_definitions.py`: Defines the 20 profile sections
  - `prompts.py`: Contains prompts for the AI model
  - `fact_refinement.py`: Improves factual accuracy of outputs
  - `insight_refinement.py`: Enhances analytical depth of outputs
  - `__init__.py`: Makes the directory a Python package

- **requirements.txt**: Lists all Python package dependencies
- **.gitignore**: Specifies files to exclude from version control
- **.env**: Environment file for API keys (you must create this)

## Setup Instructions

### Prerequisites
1. Python 3.8 or higher
2. Git
3. Visual Studio Code (recommended)
4. Google Gemini API key

### Installation

1. **Clone the repository**
```
git clone https://github.com/YourUsername/ProfileDash.git
cd ProfileDash
```

2. **Create a virtual environment**
```
python -m venv venv
```

3. **Activate the virtual environment**
   - On Windows:
```
venv\Scripts\activate
```
   - On macOS/Linux:
```
source venv/bin/activate
```

4. **Install dependencies**
```
pip install -r requirements.txt
```

5. **Set up API credentials**
   - Create a `.env` file in the project root directory
   - Add your Google Gemini API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Running ProfileDash

1. **Activate the virtual environment** (if not already activated)
   - On Windows: 
```
venv\Scripts\activate
```
   - On macOS/Linux: 
```
source venv/bin/activate
```

2. **Navigate to the source directory**
```
cd src
```

3. **Run the application**
```
python profile_dash.py
```

4. **Select documents**
   - When prompted, select PDF documents to analyze
   - The application will process these documents and generate a profile

5. **View the generated profile**
   - The HTML output should automatically open in your default browser
   - Profile files are saved in a folder named `profile_{company_name}_{timestamp}`

## Technical Details

- Uses Google's Gemini AI for document analysis
- Works with files up to 20MB in aggregate
- Implements parallel processing for efficient section generation
- Features fact-checking and insight refinement procedures
- Generates interactive HTML with expandable sections
- Caches API responses to reduce redundant calls and costs

## Troubleshooting

- **ModuleNotFoundError**: Ensure you're running from the `src` directory
- **API Key Issues**: Check that your `.env` file exists and contains the correct key
- **Import Errors**: Verify all required packages are installed and the virtual environment is activated
- **HTML Generation Errors**: Check the terminal output for specific processing errors

## Requirements

See `requirements.txt` for the complete list of dependencies.
