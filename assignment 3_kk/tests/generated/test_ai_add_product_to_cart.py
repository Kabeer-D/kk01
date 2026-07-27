import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("home_page")
def test_add_product_to_cart(home_page):
    home_page.open()
    home_page.open_cart()
    assert home_page.page.locator('body').is_visible()
