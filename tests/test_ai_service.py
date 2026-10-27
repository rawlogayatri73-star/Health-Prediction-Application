from __future__ import annotations

from unittest.mock import patch

from ai_service import build_ai_prompt, generate_ai_remarks


def test_ai_prompt_requests_cautious_risk_assessment() -> None:
    prompt = build_ai_prompt({
        "glucose": 95,
        "haemoglobin": 12.5,
        "cholesterol": 200,
    })

    assert "possible health risk signals" in prompt
    assert "Do not diagnose" in prompt
    assert "Units, laboratory reference ranges, fasting status, age, and medical history" in prompt


def test_generate_ai_remarks_mock_provider() -> None:
    with patch("ai_service.AI_PROVIDER", "mock"):
        result = generate_ai_remarks({
            "glucose": 95,
            "haemoglobin": 12.5,
            "cholesterol": 200,
        })
        assert "test mode" in result.lower()


def test_generate_ai_remarks_missing_key_uses_fallback() -> None:
    with patch("ai_service.AI_PROVIDER", "openrouter"), patch("ai_service.AI_API_KEY", ""), patch("ai_service.OPENROUTER_API_KEY", ""):
        result = generate_ai_remarks({
            "glucose": 95,
            "haemoglobin": 12.5,
            "cholesterol": 200,
        })
        assert "no API key is configured" in result


def test_generate_ai_remarks_timeout_uses_fallback() -> None:
    with patch("ai_service.AI_PROVIDER", "openrouter"), patch("ai_service.AI_API_KEY", "fake-key"), patch("ai_service.requests.post") as mock_post:
        mock_post.side_effect = TimeoutError("timed out")
        result = generate_ai_remarks({
            "glucose": 95,
            "haemoglobin": 12.5,
            "cholesterol": 200,
        })
        assert "AI service is unavailable" in result


def test_generate_ai_remarks_sends_bearer_token() -> None:
    with patch("ai_service.AI_PROVIDER", "openrouter"), patch("ai_service.AI_API_KEY", "fake-key"), patch("ai_service.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "General guidance."}}]
        }
        result = generate_ai_remarks({
            "glucose": 95,
            "haemoglobin": 12.5,
            "cholesterol": 200,
        })
        assert result == "General guidance."
        assert mock_post.call_args.kwargs["headers"]["Authorization"] == "Bearer fake-key"


def test_generate_ai_remarks_malformed_response_uses_fallback() -> None:
    with patch("ai_service.AI_PROVIDER", "openrouter"), patch("ai_service.AI_API_KEY", "fake-key"), patch("ai_service.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": []}
        result = generate_ai_remarks({
            "glucose": 95,
            "haemoglobin": 12.5,
            "cholesterol": 200,
        })
        assert "AI service is unavailable" in result
