import json
from pathlib import Path

from agents.functionality_agent import FunctionalityAgent


def test_functionality_agent_creates_scenarios():
    workspace_root = Path(__file__).resolve().parents[1]
    scraper_data_path = workspace_root / "generated" / "page_elements.json"
    locator_data_path = workspace_root / "generated" / "amazon_locators.json"

    assert scraper_data_path.exists(), "Scraper output not found"
    assert locator_data_path.exists(), "Locator output not found"

    scraper_data = json.loads(scraper_data_path.read_text(encoding="utf-8"))
    locator_data = json.loads(locator_data_path.read_text(encoding="utf-8"))

    agent = FunctionalityAgent()
    scenarios = agent.run(scraper_data=scraper_data, locator_data=locator_data)

    assert isinstance(scenarios, list)
    assert len(scenarios) >= 3

    output_path = workspace_root / "generated" / "test_scenarios.json"
    assert output_path.exists()

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(saved) >= 3
