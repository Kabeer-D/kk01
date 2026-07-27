import json
from pathlib import Path

from agents.locator_agent import LocatorAgent


def test_locator_agent_generates_expected_output():
    workspace_root = Path(__file__).resolve().parents[1]
    data_path = workspace_root / "generated" / "page_elements.json"
    payload = json.loads(data_path.read_text(encoding="utf-8"))

    agent = LocatorAgent()
    result = agent.run(payload)

    assert isinstance(result, dict)
    assert {"search_box", "search_button", "cart_button", "sign_in_button", "navigation_menu", "product_links"}.issubset(result.keys())

    output_path = workspace_root / "generated" / "amazon_locators.json"
    assert output_path.exists()

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["search_box"]["type"] == "input"
    assert saved["search_button"]["type"] == "button"
