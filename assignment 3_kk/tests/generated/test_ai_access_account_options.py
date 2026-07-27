import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("home_page")
def test_access_account_options(home_page):
    home_page.open()
    home_page.open_account()
    assert home_page.page.locator('body').is_visible()
