# How to Run This Project

## 1. Download and extract the project

1. Download the repository as a ZIP file from GitHub.
2. Extract the ZIP to a folder on your computer.
3. Open that folder in Visual Studio Code.

## 2. Read the markdown files first

Before running anything, review the documentation files in the project root:

- README.md - overview and setup instructions
- amazon-homepage-locators.md - sample locator documentation
- amazon-homepage-functionalities.md - sample functionality documentation
- amazon-homepage.feature - Gherkin feature example
- AZURE_DEVOPS_INTEGRATION.md - Azure DevOps pipeline notes

These files explain what the framework does and how the generated output is structured.

## 3. Create a Python virtual environment

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```powershell
pip install -r requirements.txt
```

Install Playwright browsers:

```powershell
playwright install chromium
```

## 5. Configure environment variables

Create a file named `.env` in the project root with the following content:

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
WEBSITE_URL=https://www.amazon.com
```

You can replace `https://www.amazon.com` with any website you want to test, such as `https://www.flipkart.com`, `https://github.com`, or any other public URL.

If you do not have a Groq API key, the framework may still run in fallback mode, but AI-generated results will be limited.

## 6. Run the main workflow

Run the project with:

```powershell
python main.py --url https://www.amazon.com
```

Or simply:

```powershell
python main.py
```

This will:

- scrape the target website
- generate locators and scenarios
- create test files
- run the generated tests
- write reports to the reports and generated folders

## 7. Run generated tests

To run the generated tests directly:

```powershell
pytest -vv tests/generated
```

## 8. Useful output folders

The workflow creates files in these folders:

- generated/
- reports/
- tests/generated/

## 9. Troubleshooting

- If Python cannot find packages, make sure the virtual environment is activated.
- If Playwright fails, run `playwright install chromium` again.
- If the website does not load correctly, check the `WEBSITE_URL` value in `.env`.
- If you want to test a different site, update `WEBSITE_URL` to that URL.
