import argparse
import getpass
import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph


load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter your Groq API key: ")

assert os.getenv("GROQ_API_KEY"), "Groq API key is missing."
print("Groq API key is configured for this notebook session.")

parser = argparse.ArgumentParser(description="Run a multi-agent QA workflow with agent-specific Groq models")
parser.add_argument(
    "--requirements-model",
    default=os.getenv("GROQ_REQUIREMENTS_ANALYST_MODEL", "openai/gpt-oss-120b"),
    help="Groq model for the requirements analyst agent",
)
parser.add_argument(
    "--test-model",
    default=os.getenv("GROQ_TEST_DESIGNER_MODEL", "openai/gpt-oss-120b"),
    help="Groq model for the test designer agent",
)
parser.add_argument(
    "--review-model",
    default=os.getenv("GROQ_QA_REVIEWER_MODEL", "openai/gpt-oss-120b"),
    help="Groq model for the QA reviewer agent",
)
parser.add_argument(
    "--security-model",
    default=os.getenv("GROQ_SECURITY_REVIEWER_MODEL", "openai/gpt-oss-120b"),
    help="Groq model for the security reviewer agent",
)
parser.add_argument(
    "--auto-select-models",
    action="store_true",
    help="Evaluate candidate models and auto-select the best model for each agent",
)
parser.add_argument(
    "--candidate-models",
    default=None,
    help="Comma-separated candidate Groq models to compare during auto-selection",
)
parser.add_argument(
    "--evaluation-model",
    default=None,
    help="Groq model used to evaluate candidate model outputs when auto-selecting",
)
args = parser.parse_args()

AUTO_MODEL_SELECTION = args.auto_select_models or os.getenv("GROQ_AUTO_MODEL_SELECTION", "0") == "1"
DEFAULT_CANDIDATE_MODELS = "openai/gpt-oss-120b"

if AUTO_MODEL_SELECTION:
    configured_candidates = args.candidate_models or os.getenv("GROQ_CANDIDATE_MODELS")
    if configured_candidates:
        candidate_models_value = configured_candidates
    else:
        prompt_text = (
            "No candidate models found in environment. Enter comma-separated Groq models to compare "
            f"or press Enter for default '{DEFAULT_CANDIDATE_MODELS}': "
        )
        candidate_models_value = input(prompt_text).strip() or DEFAULT_CANDIDATE_MODELS
else:
    candidate_models_value = args.candidate_models or os.getenv("GROQ_CANDIDATE_MODELS") or DEFAULT_CANDIDATE_MODELS

CANDIDATE_MODELS = [m.strip() for m in candidate_models_value.split(",") if m.strip()]
EVALUATION_MODEL = args.evaluation_model or os.getenv("GROQ_EVALUATION_MODEL") or "openai/gpt-oss-120b"
MODEL_SELECTION_REPORTS = {}


class QAAgentState(TypedDict):
    requirement: str
    analysis: str
    test_cases: str
    review: str
    security_review: str


AGENT_MODEL_CONFIG = {
    "requirements_analyst": {
        "model": args.requirements_model,
        "temperature": float(os.getenv("GROQ_REQUIREMENTS_ANALYST_TEMPERATURE", "0.1")),
        "max_tokens": int(os.getenv("GROQ_REQUIREMENTS_ANALYST_MAX_TOKENS", "1400")),
        "reasoning_format": os.getenv("GROQ_REQUIREMENTS_ANALYST_REASONING_FORMAT", "parsed"),
        "max_retries": int(os.getenv("GROQ_MAX_RETRIES", "2")),
    },
    "test_designer": {
        "model": args.test_model,
        "temperature": float(os.getenv("GROQ_TEST_DESIGNER_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("GROQ_TEST_DESIGNER_MAX_TOKENS", "1800")),
        "reasoning_format": os.getenv("GROQ_TEST_DESIGNER_REASONING_FORMAT", "parsed"),
        "max_retries": int(os.getenv("GROQ_MAX_RETRIES", "2")),
    },
    "qa_reviewer": {
        "model": args.review_model,
        "temperature": float(os.getenv("GROQ_QA_REVIEWER_TEMPERATURE", "0.0")),
        "max_tokens": int(os.getenv("GROQ_QA_REVIEWER_MAX_TOKENS", "1200")),
        "reasoning_format": os.getenv("GROQ_QA_REVIEWER_REASONING_FORMAT", "parsed"),
        "max_retries": int(os.getenv("GROQ_MAX_RETRIES", "2")),
    },
    "security_reviewer": {
        "model": args.security_model,
        "temperature": float(os.getenv("GROQ_SECURITY_REVIEWER_TEMPERATURE", "0.0")),
        "max_tokens": int(os.getenv("GROQ_SECURITY_REVIEWER_MAX_TOKENS", "1400")),
        "reasoning_format": os.getenv("GROQ_SECURITY_REVIEWER_REASONING_FORMAT", "parsed"),
        "max_retries": int(os.getenv("GROQ_MAX_RETRIES", "2")),
    },
}

agent_clients = {}


def get_agent_client(agent_name: str) -> ChatGroq:
    if agent_name not in agent_clients:
        config = AGENT_MODEL_CONFIG[agent_name]
        client_kwargs = {
            "model": config["model"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "max_retries": config["max_retries"],
        }
        if config.get("reasoning_format"):
            client_kwargs["reasoning_format"] = config["reasoning_format"]
        agent_clients[agent_name] = ChatGroq(**client_kwargs)
    return agent_clients[agent_name]


def parse_best_model_choice(evaluation_text: str, candidates: list[str]) -> str:
    normalized = evaluation_text.lower()
    for model in candidates:
        if model.lower() in normalized:
            return model
    for line in evaluation_text.splitlines():
        if "best" in line.lower() or "choose" in line.lower():
            for model in candidates:
                if model.lower() in line.lower():
                    return model
    return candidates[0]


def build_evaluation_prompt(agent_name: str, system_prompt: str, task: str, candidate_outputs: dict[str, str]) -> str:
    criteria = {
        "requirements_analyst": "accuracy, completeness, ambiguity detection, business risk and acceptance criteria clarity",
        "test_designer": "coverage, testability, edge cases, negative scenarios, and format quality",
        "qa_reviewer": "requirement coverage, missing edge cases, duplication, clarity, and business risk",
        "security_reviewer": "security threat coverage, authorization/authentication gaps, data exposure, and input validation",
    }
    prompt_lines = [
        f"You are a QA model selection analyst for the {agent_name} role.",
        "Compare these candidate outputs and choose the best model for the job.",
        f"Use the following evaluation criteria: {criteria.get(agent_name, 'clarity, correctness, and completeness')}",
        "Prefer the lower-cost model when the quality is comparable, and avoid choosing a larger model unless it clearly improves the result.",
        "Respond with the best model name and a short justification.",
        "",
        "TASK:",
        task,
        "",
        "CANDIDATE OUTPUTS:",
    ]
    for model, output in candidate_outputs.items():
        prompt_lines.extend([
            f"Model: {model}",
            "Output:",
            output.strip(),
            "---",
        ])
    return "\n".join(prompt_lines)


def evaluate_candidate_models(agent_name: str, system_prompt: str, task: str) -> tuple[str, dict[str, str], str]:
    candidate_outputs: dict[str, str] = {}
    failed_models: dict[str, str] = {}

    for model in CANDIDATE_MODELS:
        if not model:
            continue
        try:
            client = ChatGroq(model=model, temperature=0.0, max_tokens=2000, max_retries=2)
            response = client.invoke(
                [
                    ("system", system_prompt),
                    ("human", task),
                ]
            )
            candidate_outputs[model] = response.content
        except Exception as exc:
            failed_models[model] = str(exc)
            print(f"[AUTO SELECT] skipping model '{model}' due to error: {exc}")

    if not candidate_outputs:
        fallback_model = AGENT_MODEL_CONFIG[agent_name]["model"]
        print(f"[AUTO SELECT] no valid candidate models available; falling back to configured model {fallback_model}")
        fallback_response = get_agent_client(agent_name).invoke(
            [
                ("system", system_prompt),
                ("human", task),
            ]
        )
        fallback_content = fallback_response.content
        candidate_outputs = {fallback_model: fallback_content}
        report_lines = [
            "No candidate models could be used during auto-selection.",
            "Fallback used:",
            fallback_model,
            "Errors:",
        ]
        for failed_model, error_text in failed_models.items():
            report_lines.append(f"- {failed_model}: {error_text}")
        return fallback_model, candidate_outputs, "\n".join(report_lines)

    if len(candidate_outputs) == 1:
        selected_model = list(candidate_outputs.keys())[0]
        report = "Only one candidate model succeeded during auto-selection."
        if failed_models:
            report += "\nSkipped models:\n"
            report += "\n".join(f"- {m}: {e}" for m, e in failed_models.items())
        return selected_model, candidate_outputs, report

    evaluation_client = ChatGroq(model=EVALUATION_MODEL, temperature=0.0, max_tokens=1200, max_retries=2)
    evaluation_prompt = build_evaluation_prompt(agent_name, system_prompt, task, candidate_outputs)
    evaluation_result = evaluation_client.invoke(
        [
            ("system", "You are a model comparison analyst. Choose the best model for the task from the candidates provided."),
            ("human", evaluation_prompt),
        ]
    )
    selected_model = parse_best_model_choice(evaluation_result.content, list(candidate_outputs.keys()))
    report = evaluation_result.content.strip()
    if failed_models:
        report += "\n\nSkipped models:\n"
        report += "\n".join(f"- {m}: {e}" for m, e in failed_models.items())
    return selected_model, candidate_outputs, report


def call_specialist(agent_name: str, system_prompt: str, task: str) -> str:
    if AUTO_MODEL_SELECTION:
        selected_model, candidate_outputs, report = evaluate_candidate_models(agent_name, system_prompt, task)
        MODEL_SELECTION_REPORTS[agent_name] = {
            "selected_model": selected_model,
            "candidate_outputs": candidate_outputs,
            "report": report,
        }
        print(f"[AUTO SELECT] {agent_name} selected {selected_model}")
        return candidate_outputs[selected_model]

    response = get_agent_client(agent_name).invoke(
        [
            ("system", system_prompt),
            ("human", task),
        ]
    )
    return response.content


print("Agent-to-model assignment:")
for agent_name, config in AGENT_MODEL_CONFIG.items():
    print(
        f"- {agent_name}: model={config['model']}, temperature={config['temperature']}, "
        f"max_tokens={config['max_tokens']}"
    )

if AUTO_MODEL_SELECTION:
    print("\nAuto-selection is enabled.")
    print(f"Candidate models: {', '.join(CANDIDATE_MODELS)}")
    print(f"Evaluation model: {EVALUATION_MODEL}\n")


def requirements_analyst(state: QAAgentState):
    analysis = call_specialist(
        "requirements_analyst",
        "You are a senior QA requirements analyst. Identify actors, business rules, acceptance criteria, risks, dependencies, and ambiguous requirements. Be concise and do not invent missing facts.",
        f"Analyze this requirement for testing:\n\n{state['requirement']}",
    )
    return {"analysis": analysis}


def test_designer(state: QAAgentState):
    test_cases = call_specialist(
        "test_designer",
        "You are a senior test designer. Produce a compact Markdown table with ID, scenario, preconditions, steps, expected result, test type, and priority. Cover positive, negative, boundary, security, and failure paths.",
        f"Requirement:\n{state['requirement']}\n\nRequirements analysis:\n{state['analysis']}\n\nDesign executable test cases.",
    )
    return {"test_cases": test_cases}


def qa_reviewer(state: QAAgentState):
    review = call_specialist(
        "qa_reviewer",
        "You are a critical QA lead. Review the proposed tests for requirement coverage, missing edge cases, duplication, testability, and business risk. Finish with APPROVE or REVISE and a short reason.",
        f"Requirement:\n{state['requirement']}\n\nAnalysis:\n{state['analysis']}\n\nProposed tests:\n{state['test_cases']}",
    )
    return {"review": review}


def security_reviewer(state: QAAgentState):
    security_review = call_specialist(
        "security_reviewer",
        "You are a senior security reviewer. Review the requirement and tests for authentication issues, authorization issues, data exposure, input validation gaps, and common security threats. Keep it concise.",
        f"Requirement:\n{state['requirement']}\n\nAnalysis:\n{state['analysis']}\n\nProposed tests:\n{state['test_cases']}\n\nReview from QA lead:\n{state['review']}",
    )
    return {"security_review": security_review}


builder = StateGraph(QAAgentState)
builder.add_node("requirements_analyst", requirements_analyst)
builder.add_node("test_designer", test_designer)
builder.add_node("qa_reviewer", qa_reviewer)
builder.add_node("security_reviewer", security_reviewer)
builder.add_edge(START, "requirements_analyst")
builder.add_edge("requirements_analyst", "test_designer")
builder.add_edge("test_designer", "qa_reviewer")
builder.add_edge("qa_reviewer", "security_reviewer")
builder.add_edge("security_reviewer", END)

qa_agent_chain = builder.compile()
print("Four-agent QA chain is ready with agent-specific Groq model routing.")

REQUIREMENTS_FILE = Path(__file__).with_name("requirements_doc.md")


def load_requirement_text() -> str:
    if REQUIREMENTS_FILE.exists():
        return REQUIREMENTS_FILE.read_text(encoding="utf-8").strip()

    return """
As a registered customer, I want to reset my password using a time-limited email link.
The link must expire after 15 minutes and must not work after it has been used once.
"""


requirement_text = load_requirement_text()
print(f"Loaded requirement text from: {REQUIREMENTS_FILE}")
print("\nRequirement input:\n")
print(requirement_text)

result = qa_agent_chain.invoke({
    "requirement": requirement_text,
    "analysis": "",
    "test_cases": "",
    "review": "",
    "security_review": "",
})

for heading, key in [
    ("REQUIREMENTS ANALYST", "analysis"),
    ("TEST DESIGNER", "test_cases"),
    ("QA REVIEWER", "review"),
    ("SECURITY REVIEWER", "security_review"),
]:
    print(f"\n{'=' * 20} {heading} {'=' * 20}\n")
    print(result[key])

if AUTO_MODEL_SELECTION:
    print("\n" + "=" * 20 + " MODEL SELECTION REPORT " + "=" * 20 + "\n")
    for agent_name, report_data in MODEL_SELECTION_REPORTS.items():
        print(f"\nAgent: {agent_name}")
        print(f"Selected Model: {report_data['selected_model']}")
        print("Evaluation summary:")
        print(report_data['report'])
        print("Candidate models:")
        for model in report_data['candidate_outputs'].keys():
            print(f"- {model}")
