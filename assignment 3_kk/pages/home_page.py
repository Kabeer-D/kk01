import os

from pages.base_page import BasePage
from utils.site_utils import get_default_site_selectors


class WebsiteHomePage(BasePage):
    URL = os.getenv("WEBSITE_URL", "https://www.example.com")

    def __init__(self, page):
        super().__init__(page)
        self.URL = os.getenv("WEBSITE_URL", self.URL)
        self.defaults = get_default_site_selectors(self.URL)
        self.env_selectors = {
            "search_input": os.getenv("SITE_SEARCH_INPUT", ""),
            "search_button": os.getenv("SITE_SEARCH_BUTTON", ""),
            "categories_menu": os.getenv("SITE_CATEGORIES_MENU", ""),
            "account_link": os.getenv("SITE_ACCOUNT_LINK", ""),
            "orders_link": os.getenv("SITE_ORDERS_LINK", ""),
            "cart_link": os.getenv("SITE_CART_LINK", ""),
            "deals_link": os.getenv("SITE_DEALS_LINK", ""),
        }

    def _selector(self, key: str, fallbacks: list[str]) -> str:
        candidate = self.env_selectors.get(key) or self.defaults.get(key, "")
        if candidate:
            return candidate
        for selector in fallbacks:
            if selector:
                return selector
        return ""

    def _locator_for(self, selectors: list[str]):
        for selector in selectors:
            if not selector:
                continue
            locator = self.page.locator(selector)
            try:
                if locator.count() > 0:
                    return locator
            except Exception:
                continue
        return None

    def _locator_key(self, key: str, fallbacks: list[str]):
        primary = self._selector(key, fallbacks)
        return self._locator_for([primary] + fallbacks)

    def open(self):
        self.page.goto(self.URL, wait_until="domcontentloaded")
        self.wait_for_page_ready()
        return self

    def search_for(self, query: str):
        locator = self._locator_key(
            "search_input",
            [
                "input[type='search']",
                "input[name*='search' i]",
                "input[placeholder*='search' i]",
            ],
        )
        if locator is not None and locator.count() > 0:
            locator.first.fill(query)
            submit = self._locator_key(
                "search_button",
                [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:has-text('Search')",
                ],
            )
            if not self.click_first(submit):
                self.page.keyboard.press("Enter")
        self.wait_for_page_ready()
        return self

    def open_categories(self):
        locator = self._locator_key(
            "categories_menu",
            [
                "nav button",
                "button:has-text('menu')",
                "button",
                "a[href*='category' i]",
            ],
        )
        self.click_first(locator)
        self.wait_for_page_ready()
        return self

    def open_account(self):
        locator = self._locator_key(
            "account_link",
            [
                "a[href*='account' i]",
                "button:has-text('account')",
                "a:has-text('Account')",
            ],
        )
        self.click_first(locator)
        self.wait_for_page_ready()
        return self

    def open_orders(self):
        locator = self._locator_key(
            "orders_link",
            [
                "a[href*='order' i]",
                "button:has-text('orders')",
                "a:has-text('Orders')",
            ],
        )
        self.click_first(locator)
        self.wait_for_page_ready()
        return self

    def open_cart(self):
        locator = self._locator_key(
            "cart_link",
            [
                "a[href*='cart' i]",
                "button:has-text('cart')",
                "a:has-text('Cart')",
            ],
        )
        self.click_first(locator)
        self.wait_for_page_ready()
        return self

    def _deals_link(self):
        locator = self._locator_key(
            "deals_link",
            [
                "a[href*='deal' i]",
                "button:has-text('deals')",
            ],
        )
        return locator

    def open_deals(self):
        locator = self._locator_key(
            "deals_link",
            [
                "a[href*='deal' i]",
                "button:has-text('deals')",
            ],
        )
        self.click_first(locator)
        self.wait_for_page_ready()
        return self

    def is_search_box_visible(self) -> bool:
        return self.is_visible(
            self._locator_key(
                "search_input",
                [
                    "input[type='search']",
                    "input[name*='search' i]",
                    "input[placeholder*='search' i]",
                ],
            )
        )

    def is_cart_link_visible(self) -> bool:
        return self.is_visible(
            self._locator_key(
                "cart_link",
                [
                    "a[href*='cart' i]",
                    "button:has-text('cart')",
                ],
            )
        )

    def is_account_link_visible(self) -> bool:
        return self.is_visible(
            self._locator_key(
                "account_link",
                [
                    "a[href*='account' i]",
                    "button:has-text('account')",
                ],
            )
        )

    def is_deals_link_visible(self) -> bool:
        return self.is_visible(self._deals_link())


HomePage = WebsiteHomePage
AmazonHomePage = WebsiteHomePage
