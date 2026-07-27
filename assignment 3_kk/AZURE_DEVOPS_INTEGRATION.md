# Azure DevOps Integration

## What was added
- Azure Pipelines configuration in [azure-pipelines.yml](azure-pipelines.yml)
- Automated dependency installation
- Playwright browser install step
- Pytest execution in CI
- Test report and report artifact publishing

## How to connect this repository to Azure DevOps
1. Push this repository to Azure Repos or GitHub.
2. In Azure DevOps, create a new Pipeline.
3. Select the repository and choose the existing YAML file: [azure-pipelines.yml](azure-pipelines.yml).
4. If you use Groq features, create a `.env` based on `.env.example` and configure the `GROQ_API_KEY` secret in pipeline variables if needed.
5. Run the pipeline.

## Expected result
The pipeline will install Python dependencies, run the automation suite, publish test results, and upload the generated HTML/JSON reports from the reports folder.
