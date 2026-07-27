import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None

load_dotenv()


class GroqClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
        self.client = None
        if not self.api_key or Groq is None:
            return

        try:
            self.client = Groq(api_key=self.api_key)
        except Exception:
            self.client = None

    def ask(self, prompt: str) -> str:
        if not self.client:
            raise RuntimeError("Groq client is not configured. Set GROQ_API_KEY or install groq.")

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1500,
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Groq API request failed: {exc}") from exc

        if not getattr(response, "choices", None):
            raise ValueError("Invalid Groq response: no choices returned")

        message = response.choices[0].message
        content = getattr(message, "content", None)
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Invalid Groq response: empty content")

        return content

    def analyze_page(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "Analyze this webpage data and return JSON with important locator suggestions.\n"
            f"Data:\n{json.dumps(data, indent=2)}"
        )
        result = self.ask(prompt)
        try:
            return json.loads(result)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON response from Groq: {result}") from exc

    def generate_code(self, requirement: str) -> str:
        prompt = (
            "Generate Python pytest Playwright code for the following requirement. "
            "Keep it simple and production-ready.\n"
            f"Requirement:\n{requirement}"
        )
        return self.ask(prompt)
