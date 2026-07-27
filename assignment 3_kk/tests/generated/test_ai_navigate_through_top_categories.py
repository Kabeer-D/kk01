import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("home_page")
def test_navigate_through_top_categories(home_page):
    home_page.open()
    assert home_page.page.locator('body').is_visible()
