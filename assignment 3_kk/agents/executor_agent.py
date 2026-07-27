import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from playwright.sync_api import sync_playwright

from utils.site_utils import get_site_context


class ExecutorAgent:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.screenshots_dir = self.reports_dir / "screenshots"
        self.test_results_dir = Path("test-results")
        self.reports_dir.mkdir(exist_ok=True)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)

    def _discover_tests(self) -> List[str]:
        tests_dir = Path("tests/generated")
        if not tests_dir.exists():
            return []
        discovered = sorted([p.name for p in tests_dir.glob("test_*.py") if p.is_file()])
        print("Discovered tests:")
        for test_file in discovered:
            print(f"- {test_file}")
        return discovered

    def _parse_pytest_results(self, output: str) -> Dict[str, Any]:
        tests: List[Dict[str, str]] = []
        passed = 0
        failed = 0
        skipped = 0
        total_tests = 0

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            result_match = re.search(r"(tests/generated/[^\s:]+::[^\s]+)\s+(PASSED|FAILED|SKIPPED|XFAIL|XPASS)", line)
            if result_match:
                test_name = result_match.group(1)
                status = result_match.group(2)
                tests.append({"test": test_name, "status": status})
                if status == "PASSED":
                    passed += 1
                elif status == "FAILED":
                    failed += 1
                elif status == "SKIPPED":
                    skipped += 1
                continue

            collected_match = re.search(r"collected\s+(\d+)\s+items", line, re.I)
            if collected_match:
                total_tests = int(collected_match.group(1))
                continue

            passed_match = re.search(r"(\d+)\s+passed", line)
            failed_match = re.search(r"(\d+)\s+failed", line)
            skipped_match = re.search(r"(\d+)\s+skipped", line)
            if passed_match:
                passed = int(passed_match.group(1))
            if failed_match:
                failed = int(failed_match.group(1))
            if skipped_match:
                skipped = int(skipped_match.group(1))

        if total_tests == 0:
            total_tests = len(tests)

        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "tests": tests,
        }

    def _capture_screenshot(self, test_name: str, output: str) -> None:
        if "FAILURES" not in output and "FAILED" not in output:
            return

        target_url = os.getenv("WEBSITE_URL") or get_site_context()["url"]
        if not target_url:
            return

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(target_url, wait_until="domcontentloaded")
                screenshot_path = self.screenshots_dir / f"{test_name}_failure.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                browser.close()
        except Exception:
            return

    def _write_html_report(self, summary: Dict[str, Any], duration: str, stdout: str, stderr: str) -> None:
        tests_html = "\n".join(
            f"      <li>{test['test']}: {test['status']}</li>" for test in summary.get("test_details", [])
        )
        html = f"""<!DOCTYPE html>
<html>
  <head><meta charset='utf-8'><title>Execution Report</title></head>
  <body>
    <h1>Execution Report</h1>
    <p>Status: {summary['status']}</p>
    <p>Total Tests: {summary['total_tests']}</p>
    <p>Passed: {summary['passed']}</p>
    <p>Failed: {summary['failed']}</p>
    <p>Skipped: {summary['skipped']}</p>
    <p>Duration: {duration}</p>
    <h2>Test Details</h2>
    <ul>
{tests_html}
    </ul>
    <h2>Output</h2>
    <pre>{stdout}</pre>
    <pre>{stderr}</pre>
  </body>
</html>"""
        (self.reports_dir / "execution_report.html").write_text(html, encoding="utf-8")

    def run(self) -> Dict[str, Any]:
        discovered_tests = self._discover_tests()
        start = time.time()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/generated", "-vv", "--junitxml", str(self.test_results_dir / "results.xml")],
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1],
        )
        duration_seconds = int(time.time() - start)
        duration = f"{duration_seconds}s"

        summary = self._parse_pytest_results(result.stdout + "\n" + result.stderr)
        summary["duration"] = duration
        summary["status"] = "SUCCESS" if result.returncode == 0 else "FAILED"
        summary["stdout"] = result.stdout
        summary["stderr"] = result.stderr
        summary["discovered_tests"] = discovered_tests
        summary["test_details"] = summary.pop("tests")

        if summary["failed"] > 0:
            self._capture_screenshot("test_execution_failure", result.stdout + result.stderr)

        self._write_html_report(summary, duration, result.stdout, result.stderr)
        (self.reports_dir / "execution_report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return summary
