import importlib.util
import os
from pathlib import Path


def load_module():
    os.environ.setdefault("GROQ_API_KEY", "test-key")
    module_path = Path(__file__).with_name("RAG assignment_AI 1.py")
    spec = importlib.util.spec_from_file_location("rag_assignment", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_score_output_rewards_structured_requirements_content():
    module = load_module()
    output = "Actors: customer\nBusiness rules: ...\nAcceptance criteria: ...\nRisks: ..."

    assert module.score_output("requirements_analyst", output) > module.score_output("requirements_analyst", "short and vague")


def test_choose_best_profile_prefers_highest_scoring_profile():
    module = load_module()

    profiles = [
        {"model": "model-a", "temperature": 0.1, "max_tokens": 800},
        {"model": "model-b", "temperature": 0.2, "max_tokens": 1000},
    ]

    def fake_runner(profile, agent_name, prompt):
        if profile["model"] == "model-a":
            return "Actors: user\nAcceptance criteria: login must work\nRisks: none"
        return "short output"

    selected = module.choose_best_profile("requirements_analyst", "Requirement", profiles, runner=fake_runner)

    assert selected["model"] == "model-a"
