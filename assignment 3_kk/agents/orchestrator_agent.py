from agents.executor_agent import ExecutorAgent
from agents.functionality_agent import FunctionalityAgent
from agents.generator_agent import GeneratorAgent
from agents.healing_agent import HealingAgent
from agents.locator_agent import LocatorAgent
from agents.scraper_agent import ScraperAgent


class OrchestratorAgent:
    def __init__(self):
        self.scraper = ScraperAgent()
        self.locator = LocatorAgent()
        self.functionality = FunctionalityAgent()
        self.generator = GeneratorAgent()
        self.executor = ExecutorAgent()
        self.healing = HealingAgent()

    def _log(self, message: str) -> None:
        print(message)

    def run(self, url: str):
        self._log("================================")
        self._log("AI Automation Workflow Started")
        self._log("================================")

        try:
            self._log("[1/5] Scraper Agent")
            scraper_data = self.scraper.run(url)

            self._log("[2/5] Locator Agent")
            locators = self.locator.run(scraper_data)

            self._log("[3/5] Functionality Agent")
            scenarios = self.functionality.run(scraper_data, locators)

            self._log("[4/5] Generator Agent")
            generated = self.generator.run(locators, scenarios)

            self._log("[5/5] Executor Agent")
            execution = self.executor.run()
        except Exception as exc:
            self._log(f"Workflow failed: {exc}")
            healing_data = self.healing.run(str(exc), {})
            return {
                "website": url,
                "agents_completed": [],
                "tests_generated": 0,
                "tests_executed": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "test_details": [],
                "status": "FAILED",
                "error": str(exc),
                "healing": healing_data,
            }

        if execution.get("failed", 0) > 0:
            self._log("[6/6] Healing Agent")
            self.healing.run(execution.get("stderr", ""), {})

        self._log("================================")
        self._log("Workflow Completed")
        self._log("================================")

        return {
            "website": url,
            "agents_completed": ["scraper", "locator", "functionality", "generator", "executor"],
            "tests_generated": generated.get("tests_generated", 0),
            "tests_executed": execution.get("total_tests", 0),
            "tests_passed": execution.get("passed", 0),
            "tests_failed": execution.get("failed", 0),
            "test_details": execution.get("test_details", []),
            "status": "SUCCESS" if execution.get("failed", 0) == 0 else "FAILED",
        }
