import json
import signal
from pathlib import Path
from typing import Any, Dict

from mcp.browser_mcp_server import BrowserMCPServer


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")


class ScraperAgent:
    def __init__(self):
        self.server = BrowserMCPServer()
        self.output_dir = Path("generated")
        self.output_dir.mkdir(exist_ok=True)

    def run(self, url: str) -> Dict[str, Any]:
        try:
            print(f"Opening page: {url}")
            self.server.open_page(url)
            print("Page opened, extracting elements...")
            payload = self.server.extract_elements()
            print(f"Extracted {sum(len(v) for v in payload.values())} elements")
        except Exception as exc:
            print(f"Scraper error: {exc}")
            payload = {
                "inputs": [],
                "buttons": [],
                "links": [],
                "text_elements": [],
                "error": str(exc),
            }

        path = self.output_dir / "page_elements.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
