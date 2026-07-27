# AI Automation Testing Framework (Assignment 3)

## What this project teaches

This repository shows how to build an AI-assisted automation framework that:
- uses a multi-agent architecture
- extracts page locators via a browser MCP layer
- uses Groq AI to identify key page elements and generate test code
- executes generated pytest tests automatically
- writes a structured execution report with test status
- includes Azure DevOps pipeline integration

## Architecture

1. `main.py`: entry point that starts the orchestrator.
2. `agents/orchestrator_agent.py`: runs the workflow across agents.
3. `agents/scraper_agent.py`: opens the page and extracts DOM element metadata.
4. `agents/locator_agent.py`: identifies the most important locators.
5. `agents/functionality_agent.py`: identifies user workflows and scenarios.
6. `agents/generator_agent.py`: generates pytest Playwright tests with Groq.
7. `agents/executor_agent.py`: runs the generated tests and produces report output.
8. `agents/healing_agent.py`: placeholder for locator recovery.

## Repository structure

- `agents/`: agent modules and orchestrator logic
- `mcp/`: browser MCP helper for scraping page elements
- `pages/`: page object model classes
- `tests/`: pytest fixtures and generated tests
- `utils/`: Groq API client wrapper
- `azure-pipelines.yml`: Azure DevOps pipeline configuration
- `.env.example`: environment variable template

## Setup

For a step-by-step guide that starts from downloading the ZIP file and reading the project documentation, see [HOW_TO_RUN.md](HOW_TO_RUN.md).

1. Clone the repository.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the environment:

```bash
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Install Playwright browsers:

```bash
playwright install chromium
```

6. Copy the environment example:

```bash
copy .env.example .env
```

7. Edit `.env` and set the URL and key:

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
WEBSITE_URL=https://www.amazon.com
```

## Run the workflow

```bash
python main.py --url https://www.amazon.com
```

or use the `.env` variable:

```bash
python main.py
```

## Run generated tests

```bash
pytest -vv tests/generated
```

## Azure DevOps

The pipeline defined in `azure-pipelines.yml` installs dependencies, executes generated tests, and publishes reports. Configure `GROQ_API_KEY` as a secret variable in Azure DevOps.

## Notes

The framework writes temporary and generated output to:
- `generated/`
- `test-results/`
- `reports/`

These folders are ignored by Git, so only source files remain in the repository.

