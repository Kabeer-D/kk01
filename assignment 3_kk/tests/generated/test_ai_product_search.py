import pytest
from pages.home_page import HomePage

@pytest.mark.usefixtures("home_page")
def test_product_search(home_page):
    home_page.open()
    home_page.search_for("wireless headphones")
    assert home_page.page.locator('body').is_visible()
