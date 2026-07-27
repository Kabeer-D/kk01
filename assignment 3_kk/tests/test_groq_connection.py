import os

import pytest
from dotenv import load_dotenv

from utils.groq_client import GroqClient

load_dotenv()


def test_groq_connection_smoke():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY is not configured")

    client = GroqClient(api_key=api_key)
    prompt = "Explain what a search textbox is"
    response = client.ask(prompt)
    print("\nGroq response:\n")
    print(response)
    assert isinstance(response, str) and len(response.strip()) > 0
