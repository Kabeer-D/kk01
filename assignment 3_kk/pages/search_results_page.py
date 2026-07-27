from pages.base_page import BasePage


class SearchResultsPage(BasePage):
    RESULTS_CONTAINER = "div.s-search-results"
    SEARCH_BOX = "input#twotabsearchtextbox"

    def _result_locators(self):
        return [
            self.page.locator(self.RESULTS_CONTAINER),
            self.page.locator("div[data-component-type='s-search-result']"),
            self.page.locator("div[role='listitem']"),
            self.page.locator("a[href*='/dp/' i]"),
        ]

    def is_results_visible(self) -> bool:
        if any(self.is_visible(locator) for locator in self._result_locators()):
            return True
        if "search" in self.page.url.lower() or "query" in self.page.url.lower():
            return True
        try:
            body = self.page.locator("body")
            if body.count() > 0:
                text = body.first.inner_text(timeout=2000)
                return bool(text and text.strip())
        except Exception:
            return False
        return False

    def is_search_box_visible(self) -> bool:
        return self.is_visible(self.page.locator(self.SEARCH_BOX))
