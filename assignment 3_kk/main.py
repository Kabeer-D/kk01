import argparse
import os
import sys

from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent

load_dotenv(override=True)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="AI Automation Framework")
    parser.add_argument("--url", help="Website URL to analyze")
    args = parser.parse_args()

    url = args.url or os.getenv("WEBSITE_URL", "")
    if not url:
        print("Please provide a website URL via --url or WEBSITE_URL in .env")
        return

    os.environ["WEBSITE_URL"] = url

    print("================================")
    print(f"Using website URL: {url}")
    print("================================")
    print("AI Automation Framework")
    print("================================")

    orchestrator = OrchestratorAgent()
    summary = orchestrator.run(url)

    print(f"Website:\n{summary['website']}")
    print()
    print("Agents Completed:")
    completed = set(summary.get("agents_completed", []))
    for agent_name in ["Scraper", "Locator", "Functionality", "Generator", "Executor"]:
        marker = "✓" if agent_name.lower() in completed else "✗"
        print(f"{marker} {agent_name}")
    print()
    print(f"Tests Generated:\n{summary['tests_generated']}")
    print(f"Tests Executed:\n{summary['tests_executed']}")
    print(f"Passed:\n{summary['tests_passed']}")
    print(f"Failed:\n{summary['tests_failed']}")
    print()
    print("Test Details:")
    for test_data in summary.get("test_details", []):
        print(f"- {test_data['test']} : {test_data['status']}")
    print()
    print(f"Status:\n{summary['status']}")

    if summary.get("status") == "FAILED" and summary.get("error"):
        print(f"Error:\n{summary['error']}")


if __name__ == "__main__":
    main()
