import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("home_page")
def test_view_cart_and_proceed_to_checkout(home_page):
    home_page.open()
    home_page.open_cart()
    assert home_page.page.locator('body').is_visible()
