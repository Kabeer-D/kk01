from playwright.sync_api import Page, TimeoutError


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def wait_for_page_ready(self, timeout: int = 10000) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except TimeoutError:
            pass

    def is_visible(self, locator) -> bool:
        if locator is None:
            return False
        try:
            if locator.count() <= 0:
                return False
            return locator.first.is_visible(timeout=5000)
        except Exception:
            return False

    def click_first(self, locator) -> bool:
        if locator is None:
            return False
        try:
            if locator.count() <= 0:
                return False
            locator.first.click(force=True, timeout=5000)
            return True
        except Exception:
            return False
