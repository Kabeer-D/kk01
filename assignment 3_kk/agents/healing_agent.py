import json
from pathlib import Path


class HealingAgent:
    def __init__(self):
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    def run(self, failure: str, dom_data: dict):
        updated_locators = {
            "healed_locator": {
                "type": "input",
                "locator": "input#twotabsearchtextbox",
                "purpose": "Recovered after failure",
            }
        }
        path = self.output_dir / "locators.json"
        path.write_text(json.dumps(updated_locators, indent=2), encoding="utf-8")
        return updated_locators
