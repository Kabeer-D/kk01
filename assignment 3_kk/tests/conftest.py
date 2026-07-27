import pytest
from playwright.sync_api import sync_playwright
from pages.home_page import HomePage


@pytest.fixture(scope="function")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        yield page
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def home_page(browser_context):
    page = browser_context
    return HomePage(page)

