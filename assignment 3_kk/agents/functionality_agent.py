import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from utils.groq_client import GroqClient
from utils.site_utils import get_site_context, write_site_docs


class FunctionalityAgent:
    def __init__(self):
        try:
            self.client = GroqClient()
        except RuntimeError:
            self.client = None
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    def _load_json(self, file_name: str) -> Dict[str, Any]:
        path = self.output_dir / file_name
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _extract_json(self, response: str) -> list[dict[str, Any]]:
        text = response.strip()
        if not text:
            raise ValueError("Groq response was empty")

        if text.startswith("```"):
            text = re.sub(r"```(?:json)?", "", text).strip()

        match = re.search(r"\[.*\]", text, re.S)
        if match:
            text = match.group(0)

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON payload from Groq: {response}") from exc

        if not isinstance(parsed, list):
            raise ValueError("Groq response was not a JSON array")

        normalized = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "name": item.get("name") or "Untitled Scenario",
                    "description": item.get("description") or "",
                    "steps": item.get("steps") if isinstance(item.get("steps"), list) else [],
                    "priority": item.get("priority") or "medium",
                }
            )
        return normalized

    def _fallback_scenarios(self) -> list[dict[str, Any]]:
        site_context = get_site_context()
        hostname = site_context.get("hostname", "")
        display_name = site_context.get("display_name", "Site")

        if "amazon.com" in hostname or "flipkart.com" in hostname:
            return [
                {
                    "name": "Product Search",
                    "description": f"Search for a product using the main search bar on {display_name}",
                    "steps": [f"Open {display_name} homepage", "Enter a search term", "Click the search button", "Verify search results"],
                    "priority": "high",
                },
                {
                    "name": "Add Item to Cart",
                    "description": f"Add a product to the cart and verify the cart view on {display_name}",
                    "steps": ["Search for a product", "Open the first result", "Add the product to cart", "Open the cart page"],
                    "priority": "high",
                },
                {
                    "name": "View Shopping Cart",
                    "description": f"Open the shopping cart and inspect the current items", 
                    "steps": ["Open the cart page", "Verify cart items are displayed"],
                    "priority": "medium",
                },
                {
                    "name": "Browse Navigation",
                    "description": f"Open the main navigation or category menu on {display_name}",
                    "steps": ["Open navigation menu", "Choose a category", "Verify the page updates"],
                    "priority": "medium",
                },
            ]
        if "github.com" in hostname:
            return [
                {
                    "name": "Search Repository",
                    "description": f"Search for repositories or users from {display_name} homepage",
                    "steps": ["Open the search field", "Search for a repository or user", "Verify search results"],
                    "priority": "high",
                },
                {
                    "name": "Open Profile Menu",
                    "description": "Open the account menu to verify profile and settings actions",
                    "steps": ["Open the user menu", "Verify profile options are visible"],
                    "priority": "medium",
                },
                {
                    "name": "Explore Trending Repositories",
                    "description": f"Navigate trending or featured repositories from {display_name}",
                    "steps": ["Open trending or featured content", "Verify results are displayed"],
                    "priority": "medium",
                },
            ]
        if "wikipedia.org" in hostname:
            return [
                {
                    "name": "Search Encyclopedia",
                    "description": f"Search for an article using the main search box on {display_name}",
                    "steps": ["Open the search field", "Search for a topic", "Verify the article or results appear"],
                    "priority": "high",
                },
                {
                    "name": "Open Featured Article",
                    "description": f"Open the featured content or current events section on {display_name}",
                    "steps": ["Click the featured article or section", "Verify the content page loads"],
                    "priority": "medium",
                },
                {
                    "name": "Explore Navigation Links",
                    "description": f"Use the main navigation or site menu to explore {display_name}",
                    "steps": ["Open the site navigation", "Click a supported link", "Verify the destination page loads"],
                    "priority": "medium",
                },
            ]
        return [
            {
                "name": "Search Content",
                "description": f"Use the homepage search input to find relevant content on {display_name}",
                "steps": [f"Open {display_name} homepage", "Enter a search query", "Submit search", "Verify results"],
                "priority": "high",
            },
            {
                "name": "Open Primary Navigation",
                "description": f"Open the main navigation or menu on {display_name}",
                "steps": ["Open the navigation menu", "Select a major link", "Verify the page updates"],
                "priority": "medium",
            },
            {
                "name": "Verify Main Page Load",
                "description": f"Confirm the {display_name} homepage loads successfully and the top-level structure is visible", 
                "steps": ["Open the homepage", "Verify the main content is visible"],
                "priority": "medium",
            },
        ]

    def run(self, scraper_data: Optional[Dict[str, Any]] = None, locator_data: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        page_data = scraper_data if isinstance(scraper_data, dict) else self._load_json("page_elements.json")
        locator_payload = locator_data if isinstance(locator_data, dict) else self._load_json("amazon_locators.json")

        prompt = (
            "Analyze this webpage and identify important user workflows that should be automated. "
            "Return ONLY valid JSON as an array of scenario objects. Each object must have name, description, steps, and priority. "
            f"Page data:\n{json.dumps(page_data, indent=2)}\n\nLocator hints:\n{json.dumps(locator_payload, indent=2)}"
        )

        try:
            response = self.client.ask(prompt)
            parsed = self._extract_json(response)
        except Exception:
            parsed = self._fallback_scenarios()

        if len(parsed) < 3:
            parsed = parsed + self._fallback_scenarios()[: 3 - len(parsed)]

        path = self.output_dir / "test_scenarios.json"
        path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

        site_context = get_site_context()
        write_site_docs(site_context, scenarios=parsed, output_dir=Path("."))
        return parsed
