import json
import time
from typing import Any

import requests

from config import AI_API_BASE_URL, AI_API_KEY, AI_PROVIDER, OPENROUTER_API_KEY, OPENROUTER_MODEL


def build_ai_prompt(patient: dict[str, Any]) -> str:
    return (
        "You are a cautious health information assistant. Provide a brief, screening-level assessment "
        "of possible health risk signals from the following measurements: "
        f"glucose={patient.get('glucose')}, haemoglobin={patient.get('haemoglobin')}, "
        f"cholesterol={patient.get('cholesterol')}. "
        "Mention relevant screening risk categories (such as blood-sugar/diabetes risk, anemia-related risk, "
        "or cardiovascular risk) only as possibilities and only when warranted; otherwise say the results "
        "alone do not establish a clear risk. Do not diagnose or claim the person has a disease. Units, "
        "laboratory reference ranges, fasting status, age, and medical history were not provided, so state "
        "these limitations and avoid definitive conclusions. Keep the answer to 2-4 sentences, distinguish "
        "possible risk from diagnosis, and recommend a qualified clinician for interpretation and follow-up."
    )


def generate_ai_remarks(patient: dict[str, Any]) -> str:
    if AI_PROVIDER == "mock":
        return mock_ai_response_for_test(patient, reason="test mode")

    if AI_PROVIDER not in {"openrouter", "openai"}:
        raise ValueError(f"Unsupported AI provider configured: {AI_PROVIDER}")

    api_key = (AI_API_KEY or OPENROUTER_API_KEY or "").strip()
    if not api_key:
        return mock_ai_response_for_test(patient, reason="no API key is configured")

    auth_value = api_key if api_key.lower().startswith("bearer ") else f"Bearer {api_key}"
    headers = {
        "Authorization": auth_value,
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": build_ai_prompt(patient)}],
        "temperature": 0.4,
    }

    for attempt in range(2):
        try:
            response = requests.post(
                AI_API_BASE_URL,
                headers=headers,
                json=payload,
                timeout=20,
            )
            if response.status_code >= 400:
                raise requests.HTTPError(f"HTTP {response.status_code}: {response.text[:200]}")
            parsed = response.json()
            choices = parsed.get("choices")
            if not isinstance(choices, list) or not choices:
                raise ValueError("AI response did not contain a valid choices array.")
            content = choices[0].get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("AI response did not include usable message content.")
            return content.strip()
        except (requests.RequestException, ValueError, json.JSONDecodeError, TimeoutError, OSError):
            if attempt == 0:
                time.sleep(0.5)
                continue
    return mock_ai_response_for_test(patient, reason="the AI service is unavailable")

def mock_ai_response_for_test(patient: dict[str, Any], *, reason: str = "test mode") -> str:
    return (
        f"AI-generated remarks are unavailable ({reason}); this is a general fallback, not a diagnosis. "
        f"The reported values are glucose={patient.get('glucose')}, haemoglobin={patient.get('haemoglobin')}, "
        f"and cholesterol={patient.get('cholesterol')}. Interpretation depends on units, reference ranges, fasting status, age, and medical history. "
        "Please consult a clinical professional for assessment."
    )
