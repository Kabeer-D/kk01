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

GROQ_MODEL = "openai/gpt-oss-120b"

groq_model = ChatGroq(
    model=GROQ_MODEL,
    temperature=0.2,
    max_tokens=1500,
    reasoning_format="parsed",
    max_retries=2,
)


class QAAgentState(TypedDict):
    requirement: str
    analysis: str
    test_cases: str
    review: str
    security_review: str


def call_specialist(system_prompt, task):
    response = groq_model.invoke(
        [
            ("system", system_prompt),
            ("human", task),
        ]
    )
    return response.content


def requirements_analyst(state: QAAgentState):
    analysis = call_specialist(
        "You are a senior QA requirements analyst. Identify actors, business rules, acceptance criteria, risks, dependencies, and ambiguous requirements. Be concise and do not invent missing facts.",
        f"Analyze this requirement for testing:\n\n{state['requirement']}",
    )
    return {"analysis": analysis}


def test_designer(state: QAAgentState):
    test_cases = call_specialist(
        "You are a senior test designer. Produce a compact Markdown table with ID, scenario, preconditions, steps, expected result, test type, and priority. Cover positive, negative, boundary, security, and failure paths.",
        f"Requirement:\n{state['requirement']}\n\nRequirements analysis:\n{state['analysis']}\n\nDesign executable test cases.",
    )
    return {"test_cases": test_cases}


def qa_reviewer(state: QAAgentState):
    review = call_specialist(
        "You are a critical QA lead. Review the proposed tests for requirement coverage, missing edge cases, duplication, testability, and business risk. Finish with APPROVE or REVISE and a short reason.",
        f"Requirement:\n{state['requirement']}\n\nAnalysis:\n{state['analysis']}\n\nProposed tests:\n{state['test_cases']}",
    )
    return {"review": review}


def security_reviewer(state: QAAgentState):
    security_review = call_specialist(
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
print(f"Four-agent QA chain is ready with {GROQ_MODEL}.")

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