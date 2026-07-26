# How to run this project in VS Code

This project is easy to run in VS Code. A user only needs to download the project, create a local environment file, install the packages, and run the Python script.

## 1. Download the project from GitHub
- Go to the GitHub page of the project.
- Click Code.
- Choose Download ZIP.
- Extract the ZIP file into a folder on your computer.

## 2. Open the folder in VS Code
- Open VS Code.
- Click File > Open Folder.
- Choose the folder where you extracted the project.

## 3. Open the terminal in VS Code
- Press Ctrl + `.
- Or go to Terminal > New Terminal.

## 4. Create a virtual environment
Run this in the terminal:

```powershell
python -m venv .venv
```

Then activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 5. Install the required packages
Run:

```powershell
pip install python-dotenv langchain-groq langgraph
```

## 6. Create a local .env file
Create a file named .env in the project folder.

Inside it, add the following values:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_CANDIDATE_MODELS=openai/gpt-oss-120b,openai/gpt-4o-mini
GROQ_EVALUATION_MODEL=openai/gpt-oss-120b
GROQ_AUTO_MODEL_SELECTION=1
```

You can also add these optional agent-specific values if you want:

```env
GROQ_REQUIREMENTS_ANALYST_MODEL=openai/gpt-oss-120b
GROQ_TEST_DESIGNER_MODEL=openai/gpt-oss-120b
GROQ_QA_REVIEWER_MODEL=openai/gpt-oss-120b
GROQ_SECURITY_REVIEWER_MODEL=openai/gpt-oss-120b
```

## 7. Run the script
Basic run:

```powershell
python "RAG assignment_AI 1.py"
```

Auto-selection run:

```powershell
python "RAG assignment_AI 1.py" --auto-select-models
```

## 8. Notes
- The script reads the requirements from requirements_doc.md.
- If no model list is found, it may ask you in the terminal.
- Press Enter if you want to use the default model: openai/gpt-oss-120b.
- Do not share your .env file publicly or upload it to GitHub.
