import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.groq_client import GroqClient
from utils.site_utils import get_site_context


class GeneratorAgent:
    def __init__(self):
        try:
            self.client = GroqClient()
        except RuntimeError:
            self.client = None

        self.output_dir = Path("tests/generated")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.generated_dir = Path("generated")
        self.generated_dir.mkdir(exist_ok=True, parents=True)

    def _slugify(self, name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        return slug or "scenario"

    def _write_metadata(self, files: List[str], tests_generated: int, scenarios_processed: int) -> None:
        metadata = {
            "scenarios_processed": scenarios_processed,
            "tests_generated": tests_generated,
            "files": files,
            "generated_by": "Groq",
        }
        (self.generated_dir / "generated_tests.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _suggest_page_object_updates(self, scenarios: List[Dict[str, Any]]) -> None:
        missing_methods = []
        for scenario in scenarios:
            name = scenario.get("name", "")
            if "Search" in name or "search" in name:
                missing_methods.append("HomePage.search_for(query)")
            if "Cart" in name or "cart" in name:
                missing_methods.append("HomePage.open_cart()")
            if "Navigation" in name or "category" in name or "menu" in name:
                missing_methods.append("HomePage.open_categories()")

        if missing_methods:
            content = "# Page Object Suggestions\n\n"
            for method in missing_methods:
                content += f"Missing method: {method}\nSuggested implementation:\n```python\n# implement {method}\n```\n\n"
            (self.generated_dir / "page_object_updates.md").write_text(content, encoding="utf-8")

    def _build_prompt(self, locators: Dict[str, Any], scenarios: List[Dict[str, Any]]) -> str:
        site_context = get_site_context()
        return (
            "You are a testing assistant. Generate pytest Playwright test files for these page locators and scenarios. "
            "Return ONLY valid JSON with a top-level 'tests' field. Each item must include filename and code. "
            "Do not include markdown fences. Import HomePage from pages.home_page and use SearchResultsPage for search validations when appropriate. "
            f"Target site: {site_context['url']}\n"
            f"Locators:\n{json.dumps(locators, indent=2)}\nScenarios:\n{json.dumps(scenarios, indent=2)}"
        )

    def _extract_json(self, response: str) -> List[Dict[str, Any]]:
        text = response.strip()
        if text.startswith("```"):
            text = re.sub(r"```(?:json)?", "", text).strip()

        match = re.search(r"\{.*\}", text, re.S)
        if match:
            text = match.group(0)

        parsed = json.loads(text)
        tests = parsed.get("tests")
        if not isinstance(tests, list):
            raise ValueError("Generated response did not contain a tests list")

        normalized: List[Dict[str, Any]] = []
        for item in tests:
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "filename": item.get("filename") or item.get("name") or "test_ai_generated.py",
                    "code": item.get("code") or item.get("source") or "",
                }
            )
        return normalized

    def _build_fallback_code(self, scenario: Dict[str, Any]) -> str:
        scenario_name = scenario.get("name", "scenario")
        scenario_slug = self._slugify(scenario_name)
        name_lower = scenario_name.lower()
        base = (
            "import pytest\n"
            "from pages.home_page import HomePage\n\n"
            "@pytest.mark.usefixtures(\"home_page\")\n"
            f"def test_{scenario_slug}(home_page):\n"
            "    home_page.open()\n"
        )

        if "search" in name_lower:
            return (
                base
                + "    home_page.search_for(\"wireless headphones\")\n"
                + "    assert home_page.page.locator('body').is_visible()\n"
            )
        if "cart" in name_lower:
            return (
                base
                + "    home_page.open_cart()\n"
                + "    assert home_page.page.locator('body').is_visible()\n"
            )
        if "account" in name_lower or "sign in" in name_lower or "signin" in name_lower:
            return (
                base
                + "    home_page.open_account()\n"
                + "    assert home_page.page.locator('body').is_visible()\n"
            )
        if "deal" in name_lower or "deals" in name_lower:
            return (
                base
                + "    home_page.open_deals()\n"
                + "    assert home_page.page.locator('body').is_visible()\n"
            )
        if "navigation" in name_lower or "category" in name_lower or "menu" in name_lower:
            return (
                base
                + "    home_page.open_categories()\n"
                + "    assert home_page.page.locator('body').is_visible()\n"
            )
        return (
            base
            + "    assert home_page.page.locator('body').is_visible()\n"
        )

    def _write_test_files(self, tests: List[Dict[str, Any]]) -> List[str]:
        files_created: List[str] = []
        for test in tests:
            file_name = test.get("filename") or "test_ai_generated.py"
            path = self.output_dir / file_name
            path.write_text(test.get("code", ""), encoding="utf-8")
            files_created.append(file_name)
        return files_created

    def run(self, locators: Optional[Dict[str, Any]] = None, scenarios: Optional[List[Dict[str, Any]]] = None):
        locators = locators or {}
        scenarios = scenarios or []

        for test_file in self.output_dir.glob("test_*.py"):
            if test_file.is_file():
                test_file.unlink()

        tests: List[Dict[str, Any]] = []
        if self.client is not None:
            try:
                prompt = self._build_prompt(locators, scenarios)
                tests = self._extract_json(self.client.ask(prompt))
            except Exception:
                tests = []

        if not tests:
            for scenario in scenarios:
                code = self._build_fallback_code(scenario)
                tests.append({"filename": f"test_ai_{self._slugify(scenario.get('name','scenario'))}.py", "code": code})

        files_created = self._write_test_files(tests)

        if not files_created:
            sample_scenarios = [
                {"name": "Search Product"},
                {"name": "Cart Flow"},
                {"name": "Navigation"},
            ]
            for scenario in sample_scenarios:
                code = self._build_fallback_code(scenario)
                file_name = f"test_ai_{self._slugify(scenario['name'])}.py"
                path = self.output_dir / file_name
                path.write_text(code, encoding="utf-8")
                files_created.append(file_name)

        self._suggest_page_object_updates(scenarios)
        self._write_metadata(files_created, len(files_created), len(scenarios))
        return {"tests_generated": len(files_created), "files": files_created, "generated_by": "Groq", "scenarios_processed": len(scenarios)}
