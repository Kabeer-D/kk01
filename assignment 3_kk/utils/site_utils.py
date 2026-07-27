import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse


def get_site_context(url: Optional[str] = None) -> Dict[str, str]:
    target_url = (url or os.getenv("WEBSITE_URL") or "").strip()
    parsed = urlparse(target_url) if target_url else None
    hostname = (parsed.netloc if parsed else "").lower().replace("www.", "") or "site"
    host_parts = [part for part in hostname.split(".") if part]
    brand = host_parts[0].capitalize() if host_parts else "Site"
    slug = re.sub(r"[^a-z0-9]+", "_", host_parts[0] if host_parts else "site").strip("_") or "site"
    return {
        "url": target_url,
        "hostname": hostname,
        "slug": slug,
        "display_name": brand,
        "doc_prefix": f"{slug}-homepage",
    }


def get_default_site_selectors(url: Optional[str] = None) -> Dict[str, str]:
    target_url = (url or os.getenv("WEBSITE_URL") or "").strip()
    parsed = urlparse(target_url) if target_url else None
    hostname = (parsed.netloc if parsed else "").lower().replace("www.", "")

    defaults = {
        "search_input": "input[type='search'], input[name*='search' i], input[placeholder*='search' i]",
        "search_button": "button[type='submit'], input[type='submit'], button:has-text('Search')",
        "categories_menu": "nav button, button, a[href*='category' i]",
        "account_link": "a[href*='account' i], button:has-text('account')",
        "orders_link": "a[href*='order' i], button:has-text('orders')",
        "cart_link": "a[href*='cart' i], button:has-text('cart')",
        "deals_link": "a[href*='deal' i], a[href*='goldbox'], button:has-text('deals')",
    }

    if "amazon.com" in hostname:
        defaults.update({
            "search_input": "#twotabsearchtextbox",
            "search_button": "#nav-search-submit-button",
            "categories_menu": "#nav-hamburger-menu",
            "account_link": "#nav-link-accountList",
            "orders_link": "a#nav-orders",
            "cart_link": "a#nav-cart",
            "deals_link": "a[href*='/gp/goldbox']",
        })
    elif "flipkart.com" in hostname:
        defaults.update({
            "search_input": "input[name='q'], input[title*='Search' i]",
            "search_button": "button[type='submit'], button:has-text('Search')",
            "categories_menu": "button[aria-label='Open Menu'], div._331-kn",
            "account_link": "a[title='My Account'], div._2aUbKa",
            "orders_link": "a[href*='orders']",
            "cart_link": "a[href*='viewcart'], button:has-text('Cart')",
            "deals_link": "a[href*='offer'], a[href*='deals']",
        })
    elif "github.com" in hostname:
        defaults.update({
            "search_input": "input.header-search-input, input[name='q']",
            "search_button": "button[type='submit'], button:has-text('Search')",
            "categories_menu": "summary[aria-label='Open user menu']",
            "account_link": "summary[aria-label='View profile and more']",
            "orders_link": "",
            "cart_link": "",
            "deals_link": "",
        })
    elif "wikipedia.org" in hostname:
        defaults.update({
            "search_input": "input#searchInput",
            "search_button": "input[type='submit']",
            "categories_menu": "a[title='Contents']",
            "account_link": "a#pt-userpage, a[title='View your user page']",
            "orders_link": "",
            "cart_link": "",
            "deals_link": "",
        })

    return defaults


def _summarize_locator(key: str, value: Optional[Dict[str, Any]]) -> str:
    if not isinstance(value, dict):
        return f"- {key}: {key.replace('_', ' ').title()}"

    label = value.get("name") or key.replace("_", " ").title()
    description = (value.get("description") or "").strip()
    locator_type = (value.get("type") or "element").lower()
    key_name = key.lower()

    if locator_type in {"button", "link"} or "button" in key_name or "link" in key_name:
        action = "Click"
        detail = description or "start the related action"
        return f"- {key}: {label} - {action} this {locator_type} to {detail.lower()}"
    if "search" in key_name or locator_type == "input":
        action = "Type into"
        detail = description or "the search field"
        return f"- {key}: {label} - {action} this input field to {detail.lower()}"
    if locator_type == "menu":
        action = "Open"
        detail = description or "access the menu options"
        return f"- {key}: {label} - {action} this menu to {detail.lower()}"
    detail = description or "interact with the element"
    return f"- {key}: {label} - Use this element to {detail.lower()}"


def write_site_docs(site_context: Dict[str, str], locators: Optional[Dict[str, Any]] = None, scenarios: Optional[list[Dict[str, Any]]] = None, output_dir: Optional[Path] = None) -> list[Path]:
    output_root = output_dir or Path(".")
    output_root.mkdir(exist_ok=True, parents=True)

    prefix = site_context.get("doc_prefix") or "site-homepage"
    files_written: list[Path] = []

    locators_content = [f"# {site_context.get('display_name', 'Site')} Homepage Locators", "", f"This file lists the important locators discovered for {site_context.get('url') or 'the current site'}.", ""]
    if locators:
        for key, value in locators.items():
            locators_content.append(_summarize_locator(key, value))
    locators_path = output_root / f"{prefix}-locators.md"
    locators_path.write_text("\n".join(locators_content) + "\n", encoding="utf-8")
    files_written.append(locators_path)

    functionalities_content = [f"# {site_context.get('display_name', 'Site')} Homepage Functionalities", "", f"This file lists the important user flows identified for {site_context.get('url') or 'the current site'}.", ""]
    if scenarios:
        for scenario in scenarios:
            functionalities_content.append(f"- {scenario.get('name', 'Scenario')}: {scenario.get('description', '')}")
    functionalities_path = output_root / f"{prefix}-functionalities.md"
    functionalities_path.write_text("\n".join(functionalities_content) + "\n", encoding="utf-8")
    files_written.append(functionalities_path)

    display_name = site_context.get("display_name", "Site")
    feature_content = [f"Feature: {display_name} homepage core functionalities", "", "  As a user", f"  I want to use the main features available on the {display_name} homepage", "  So that I can complete common tasks successfully"]
    if scenarios:
        for scenario in scenarios:
            name = scenario.get("name") or "Homepage scenario"
            description = scenario.get("description") or "they interact with the homepage"
            feature_content.extend(["", f"  Scenario: {name}", f"    Given the user is on the {display_name} homepage", f"    When {description}", "    Then the primary experience should be available"])
    else:
        feature_content.extend(["", "  Scenario: Open homepage", "    Given the user is on the homepage", "    When they view the main page", "    Then they should see the primary navigation and search entry points"])

    feature_path = output_root / f"{prefix}.feature"
    feature_path.write_text("\n".join(feature_content) + "\n", encoding="utf-8")
    files_written.append(feature_path)

    generic_locators_path = output_root / "homepage-locators.md"
    generic_locators_path.write_text("\n".join(locators_content) + "\n", encoding="utf-8")
    files_written.append(generic_locators_path)

    generic_functionalities_path = output_root / "homepage-functionalities.md"
    generic_functionalities_path.write_text("\n".join(functionalities_content) + "\n", encoding="utf-8")
    files_written.append(generic_functionalities_path)

    generic_feature_path = output_root / "homepage.feature"
    generic_feature_path.write_text("\n".join(feature_content) + "\n", encoding="utf-8")
    files_written.append(generic_feature_path)

    return files_written
