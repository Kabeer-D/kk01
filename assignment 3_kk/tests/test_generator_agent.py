import json
from pathlib import Path

from agents.generator_agent import GeneratorAgent


def test_generator_agent_creates_test_files():
    workspace_root = Path(__file__).resolve().parents[1]
    locators_path = workspace_root / "generated" / "amazon_locators.json"
    scenarios_path = workspace_root / "generated" / "test_scenarios.json"

    assert locators_path.exists(), "Locators file not found"
    assert scenarios_path.exists(), "Scenarios file not found"

    locators = json.loads(locators_path.read_text(encoding="utf-8"))
    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))

    agent = GeneratorAgent()
    result = agent.run(locators, scenarios)

    assert result["tests_generated"] >= 3
    generated_files = list((workspace_root / "tests" / "generated").glob("test_ai_*.py"))
    assert len(generated_files) >= 3
    assert (workspace_root / "generated" / "generated_tests.json").exists()
