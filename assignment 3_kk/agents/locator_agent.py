import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from utils.groq_client import GroqClient
from utils.site_utils import get_site_context, write_site_docs


class LocatorAgent:
    def __init__(self):
        try:
            self.client = GroqClient()
        except RuntimeError:
            self.client = None
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    def _load_scraper_data(self, scraper_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(scraper_data, dict):
            return scraper_data

        data_path = self.output_dir / "page_elements.json"
        if not data_path.exists():
            raise FileNotFoundError(f"Scraper output not found: {data_path}")
        return json.loads(data_path.read_text(encoding="utf-8"))

    def _normalize_result(self, payload: Any) -> Dict[str, Dict[str, Any]]:
        if not isinstance(payload, dict):
            raise ValueError("Groq response was not a JSON object")

        normalized = {}
        for key in [
            "search_box",
            "search_button",
            "cart_button",
            "sign_in_button",
            "account_button",
            "deals_link",
            "navigation_menu",
            "product_links",
        ]:
            item = payload.get(key)
            if isinstance(item, dict):
                normalized[key] = {
                    "name": item.get("name") or key.replace("_", " ").title(),
                    "type": item.get("type") or "element",
                    "selector": item.get("selector") or "",
                    "xpath": item.get("xpath") or "",
                    "description": item.get("description") or "",
                }
            else:
                normalized[key] = {"name": key.replace("_", " ").title(), "type": "element", "selector": "", "xpath": "", "description": ""}

        return normalized

    def _extract_json(self, response: str) -> Dict[str, Dict[str, Any]]:
        text = response.strip()
        if not text:
            raise ValueError("Groq response was empty")

        if text.startswith("```"):
            text = re.sub(r"```(?:json)?", "", text).strip()

        match = re.search(r"\{.*\}", text, re.S)
        if match:
            text = match.group(0)

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON payload from Groq: {response}") from exc

        return self._normalize_result(parsed)

    def _fallback_locators(self, scraper_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        inputs = scraper_data.get("inputs", [])
        buttons = scraper_data.get("buttons", [])
        links = scraper_data.get("links", [])

        search_input = next(
            (
                item
                for item in inputs
                if item.get("id") == "twotabsearchtextbox"
                or "search" in str(item.get("placeholder", "")).lower()
                or "search" in str(item.get("name", "")).lower()
            ),
            None,
        )
        search_button = next(
            (
                item
                for item in inputs
                if item.get("input_type") == "submit"
                and (
                    item.get("id") == "nav-search-submit-button"
                    or "search" in str(item.get("placeholder", "")).lower()
                    or "search" in str(item.get("name", "")).lower()
                    or item.get("css_selector")
                    or item.get("xpath")
                )
            ),
            None,
        )
        cart_link = next(
            (
                item
                for item in links
                if str(item.get("text", "")).lower().strip().startswith("cart")
                or "cart" in str(item.get("href", "")).lower()
                or "cart" in str(item.get("text", "")).lower()
            ),
            None,
        )
        sign_in_link = next(
            (
                item
                for item in links
                if "sign in" in str(item.get("text", "")).lower()
                or "signin" in str(item.get("href", "")).lower()
                or "sign in" in str(item.get("href", "")).lower()
            ),
            None,
        )
        account_link = next(
            (item for item in links if "account" in str(item.get("text", "")).lower() or "account" in str(item.get("href", "")).lower()),
            None,
        )
        deals_link = next(
            (item for item in links if "deal" in str(item.get("text", "")).lower() or "goldbox" in str(item.get("href", "")).lower()),
            None,
        )
        nav_link = next(
            (item for item in links if item.get("id") in {"nav-top", "nav-bb-book"} or str(item.get("text", "")).lower().strip() in {"shop deals", "best sellers"}),
            None,
        )
        product_link = next(
            (item for item in links if "/dp/" in str(item.get("href", "")) or "/gp/product" in str(item.get("href", "")) or "product" in str(item.get("href", ""))),
            None,
        )

        return {
            "search_box": {
                "name": "Search textbox",
                "type": "input",
                "selector": search_input.get("css_selector", "") if search_input else "",
                "xpath": search_input.get("xpath", "") if search_input else "",
                "description": "Used to search products",
            },
            "search_button": {
                "name": "Search button",
                "type": "button",
                "selector": search_button.get("css_selector", "") if search_button else "",
                "xpath": search_button.get("xpath", "") if search_button else "",
                "description": "Submits product search",
            },
            "cart_button": {
                "name": "Cart button",
                "type": "button",
                "selector": cart_link.get("css_selector", "") if cart_link else "",
                "xpath": cart_link.get("xpath", "") if cart_link else "",
                "description": "Opens the shopping cart",
            },
            "sign_in_button": {
                "name": "Sign in button",
                "type": "button",
                "selector": sign_in_link.get("css_selector", "") if sign_in_link else "",
                "xpath": sign_in_link.get("xpath", "") if sign_in_link else "",
                "description": "Starts the sign-in flow",
            },
            "navigation_menu": {
                "name": "Navigation menu",
                "type": "menu",
                "selector": nav_link.get("css_selector", "") if nav_link else "",
                "xpath": nav_link.get("xpath", "") if nav_link else "",
                "description": "Contains primary page navigation links",
            },
            "product_links": {
                "name": "Product links",
                "type": "link",
                "selector": product_link.get("css_selector", "") if product_link else "",
                "xpath": product_link.get("xpath", "") if product_link else "",
                "description": "List of product results or featured products",
            },
        }

    def run(self, scraper_data: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        page_data = self._load_scraper_data(scraper_data)
        prompt = (
            "Analyze this webpage and identify the most important automation elements for testing. "
            "Return ONLY valid JSON with these fields: search_box, search_button, cart_button, sign_in_button, account_button, deals_link, navigation_menu, product_links. "
            "Each field must contain name, type, selector, xpath, and description. "
            f"Data:\n{json.dumps(page_data, indent=2)}"
        )

        try:
            if self.client is None:
                raise RuntimeError("Groq client not configured")
            response = self.client.ask(prompt)
            parsed = self._extract_json(response)
        except Exception:
            parsed = self._fallback_locators(page_data)

        site_context = get_site_context()
        site_slug = site_context["slug"]
        path = self.output_dir / f"{site_slug}_locators.json"
        path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

        # Preserve the legacy amazon_locators.json file for backward compatibility.
        legacy_path = self.output_dir / "amazon_locators.json"
        legacy_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")

        write_site_docs(site_context, locators=parsed, output_dir=Path("."))
        return parsed
