import pytest
from pages.home_page import AmazonHomePage


@pytest.mark.parametrize(
    "test_name, action",
    [
        ("search", "search"),
        ("categories", "categories"),
        ("account", "account"),
        ("orders", "orders"),
        ("cart", "cart"),
        ("deals", "deals"),
    ],
)
def test_amazon_homepage_core_features(home_page, test_name, action):
    home_page.open()

    if action == "search":
        home_page.search_for("wireless headphones")
        assert "wireless headphones" in home_page.page.url.lower()
    elif action == "categories":
        home_page.open_categories()
        assert home_page.page.locator("body").is_visible()
    elif action == "account":
        home_page.open_account()
        assert home_page.page.url.lower().startswith("https://www.amazon.com")
    elif action == "orders":
        home_page.open_orders()
        assert home_page.page.url.lower().startswith("https://www.amazon.com")
    elif action == "cart":
        home_page.open_cart()
        assert home_page.page.url.lower().startswith("https://www.amazon.com")
    elif action == "deals":
        home_page.open_deals()
        assert home_page.page.url.lower().startswith("https://www.amazon.com")


def test_homepage_navigation_elements_are_visible(home_page):
    home_page.open()
    assert home_page.is_search_box_visible() is True
    assert home_page.is_cart_link_visible() is True
    assert home_page.is_account_link_visible() is True
    assert home_page.is_deals_link_visible() is True
