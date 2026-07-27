import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("home_page")
def test_browse_daily_deals(home_page):
    home_page.open()
    home_page.open_deals()
    assert home_page.page.locator('body').is_visible()
