import json
from pathlib import Path

from agents.executor_agent import ExecutorAgent


def test_executor_agent_creates_execution_report():
    workspace_root = Path(__file__).resolve().parents[1]
    agent = ExecutorAgent()
    result = agent.run()

    assert isinstance(result, dict)
    assert (workspace_root / "reports" / "execution_report.json").exists()
    assert (workspace_root / "reports" / "execution_report.html").exists()
    assert "total_tests" in result
    assert "passed" in result
    assert "failed" in result
