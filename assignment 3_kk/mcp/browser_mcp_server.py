import json
from pathlib import Path
from typing import Any, Dict, List

from playwright.sync_api import TimeoutError, sync_playwright


class BrowserMCPServer:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def open_page(self, url: str) -> Dict[str, Any]:
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        if self.browser is None:
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--disable-web-resources"],
            )
        if self.context is None:
            self.context = self.browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                accept_downloads=False,
            )
        if self.page is None:
            self.page = self.context.new_page()

        strategies = [
            ("domcontentloaded", 30000),
            ("load", 40000),
            ("domcontentloaded", 60000),
        ]

        for wait_until, timeout in strategies:
            try:
                self.page.goto(url, wait_until=wait_until, timeout=timeout)
                try:
                    self.page.wait_for_load_state("networkidle", timeout=5000)
                except TimeoutError:
                    pass
                self.page.wait_for_timeout(1000)
                return {"url": self.page.url, "title": self.page.title()}
            except TimeoutError:
                continue

        return {"url": self.page.url, "title": self.page.title(), "warning": "Page loaded with fallback strategy"}

    def extract_dom(self) -> str:
        if not self.page:
            raise RuntimeError("No page opened")
        return self.page.content()

    def extract_elements(self) -> Dict[str, list[Dict[str, Any]]]:
        if not self.page:
            raise RuntimeError("No page opened")

        try:
            result = self.page.evaluate(
                """
                () => {
                    const makeXPath = (el) => {
                        if (!el || el.nodeType !== 1) return '';
                        if (el.id) return `//*[@id="${el.id}"]`;
                        const parts = [];
                        let current = el;
                        while (current && current.nodeType === 1 && parts.length < 5) {
                            let tag = current.tagName.toLowerCase();
                            let siblingIndex = 1;
                            let sibling = current.previousElementSibling;
                            while (sibling) {
                                if (sibling.tagName.toLowerCase() === tag) siblingIndex++;
                                sibling = sibling.previousElementSibling;
                            }
                            parts.unshift(`${tag}[${siblingIndex}]`);
                            current = current.parentElement;
                        }
                        return parts.length ? `/${parts.join('/')}` : '';
                    };

                    const collect = (selector, kind, extraMapper) => {
                        const elements = [];
                        document.querySelectorAll(selector).forEach((el) => {
                            const classes = (el.className || '').toString().trim().split(/\\s+/).filter(Boolean);
                            const css_selector = el.id ? `#${el.id}` : classes.length ? `${el.tagName.toLowerCase()}.${classes.join('.')}` : el.tagName.toLowerCase();
                            const data = {
                                type: kind,
                                text: (el.textContent || '').trim().slice(0, 120),
                                id: el.id || '',
                                name: el.getAttribute('name') || '',
                                placeholder: el.getAttribute('placeholder') || '',
                                type_attr: el.getAttribute('type') || '',
                                role: el.getAttribute('role') || '',
                                href: el.getAttribute('href') || '',
                                css_selector,
                                xpath: makeXPath(el),
                            };
                            const extra = extraMapper ? extraMapper(el) : {};
                            elements.push({ ...data, ...extra });
                        });
                        return elements;
                    };

                    const inputs = collect('input', 'input', (el) => ({
                        input_type: el.getAttribute('type') || 'text',
                        placeholder: el.getAttribute('placeholder') || '',
                    }));

                    const buttons = collect('button', 'button', (el) => ({
                        text: (el.textContent || '').trim(),
                        role: el.getAttribute('role') || 'button',
                    }));

                    const links = collect('a', 'link', (el) => ({
                        text: (el.textContent || '').trim(),
                        href: el.getAttribute('href') || '',
                    }));

                    return { inputs, buttons, links };
                }
                """,
                timeout=10000,
            )

            payload = {
                "url": self.page.url,
                "title": self.page.title(),
                "inputs": result.get("inputs", []),
                "buttons": result.get("buttons", []),
                "links": result.get("links", []),
            }
        except Exception as exc:
            payload = {
                "url": self.page.url,
                "title": self.page.title(),
                "inputs": [],
                "buttons": [],
                "links": [],
                "error": str(exc),
            }

        return payload

    def capture_screenshot(self, path: str = "reports/screenshot.png") -> str:
        if not self.page:
            raise RuntimeError("No page opened")
        output_path = Path(path)
        output_path.parent.mkdir(exist_ok=True)
        self.page.screenshot(path=str(output_path), full_page=True)
        return str(output_path)

