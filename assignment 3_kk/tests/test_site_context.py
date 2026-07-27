from pathlib import Path
from unittest.mock import Mock

from pages.home_page import WebsiteHomePage
from utils.site_utils import get_site_context, write_site_docs


def test_flipkart_site_context_is_used_for_output_names():
    context = get_site_context("https://www.flipkart.com")

    assert context["slug"] == "flipkart"
    assert context["display_name"] == "Flipkart"
    assert context["doc_prefix"] == "flipkart-homepage"


def test_write_site_docs_uses_scenarios_for_feature_content(tmp_path: Path):
    site_context = get_site_context("https://www.flipkart.com")
    scenarios = [
        {"name": "Search Product", "description": "Search for products"},
        {"name": "Cart Flow", "description": "Review the shopping cart"},
    ]

    files = write_site_docs(site_context, scenarios=scenarios, output_dir=tmp_path)
    feature_path = files[2]
    feature_content = feature_path.read_text(encoding="utf-8")

    assert "Feature: Flipkart homepage core functionalities" in feature_content
    assert "Scenario: Search Product" in feature_content
    assert "Scenario: Cart Flow" in feature_content


def test_write_site_docs_includes_action_guidance_for_locators(tmp_path: Path):
    site_context = get_site_context("https://www.flipkart.com")
    locators = {
        "search_box": {"name": "Search Input", "type": "input", "selector": "#search", "xpath": "", "description": "Main search field"},
        "search_button": {"name": "Search Button", "type": "button", "selector": "#search-btn", "xpath": "", "description": "Starts the search"},
    }

    files = write_site_docs(site_context, locators=locators, output_dir=tmp_path)
    locators_path = files[0]
    content = locators_path.read_text(encoding="utf-8")

    assert "Type into" in content
    assert "Click" in content


def test_generic_home_page_uses_environment_url(monkeypatch):
    monkeypatch.setenv("WEBSITE_URL", "https://example.com")
    page = Mock()
    page.goto.return_value = None
    page.wait_for_load_state.return_value = None
    page.locator.return_value = Mock(count=Mock(return_value=0), is_visible=Mock(return_value=False))

    home_page = WebsiteHomePage(page)
    home_page.open()

    page.goto.assert_called_once_with("https://example.com", wait_until="domcontentloaded")
