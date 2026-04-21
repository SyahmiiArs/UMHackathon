"""Unit tests for GLMIntegration and prompt building."""

import pytest

from glm_integration import GLMIntegration
from prompts import build_prompt, PROMPT_TEMPLATES


# ---------------------------------------------------------------------------
# GLMIntegration — mock mode
# ---------------------------------------------------------------------------

class TestGLMIntegrationMock:
    """Tests that run entirely against the mock (no real API key needed)."""

    def setup_method(self):
        self.glm = GLMIntegration()  # no API key → mock mode
        assert self.glm.use_mock is True

    def test_get_recommendation_returns_dict(self):
        result = self.glm.get_recommendation(3000, 1000, 600, 200, 300, 200, "Where can I cut costs?")
        assert isinstance(result, dict)

    def test_result_has_required_keys(self):
        result = self.glm.get_recommendation(3000, 1000, 600, 200, 300, 200, "Where can I cut costs?")
        for key in ("recommendation", "reasoning", "impact", "confidence", "raw"):
            assert key in result, f"Missing key: {key}"

    def test_negative_savings_triggers_urgent(self):
        """When expenses > income, the mock should flag URGENT."""
        result = self.glm.get_recommendation(2000, 1200, 500, 200, 200, 300, "Where can I cut costs?")
        combined = (result["recommendation"] + result["raw"]).upper()
        assert "URGENT" in combined

    def test_increase_savings_question(self):
        result = self.glm.get_recommendation(3000, 1000, 600, 200, 300, 200, "How can I increase savings?")
        assert result["recommendation"] or result["raw"]

    def test_balanced_question(self):
        result = self.glm.get_recommendation(3000, 1000, 600, 200, 300, 200, "Is my spending balanced?")
        assert result["recommendation"] or result["raw"]

    def test_prioritize_question(self):
        result = self.glm.get_recommendation(3000, 1000, 600, 200, 300, 200, "What should I prioritize this month?")
        assert result["recommendation"] or result["raw"]

    def test_zero_income_does_not_crash(self):
        result = self.glm.get_recommendation(0, 0, 0, 0, 0, 0, "Where can I cut costs?")
        assert isinstance(result, dict)

    def test_call_glm_returns_choices_structure(self):
        raw = self.glm.call_glm("test prompt")
        assert "choices" in raw
        assert raw["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# GLMIntegration — parse_response
# ---------------------------------------------------------------------------

class TestParseResponse:
    def setup_method(self):
        self.glm = GLMIntegration()

    def _make_response(self, content: str):
        return {"choices": [{"message": {"content": content}}]}

    def test_parses_all_four_sections(self):
        content = (
            "RECOMMENDATION: Cut entertainment.\n"
            "REASONING: It is too high.\n"
            "IMPACT: Save RM150/month.\n"
            "CONFIDENCE: High — it's discretionary."
        )
        result = self.glm._parse_response(self._make_response(content))
        assert result["recommendation"] == "Cut entertainment."
        assert result["reasoning"] == "It is too high."
        assert result["impact"] == "Save RM150/month."
        assert "High" in result["confidence"]

    def test_graceful_on_empty_content(self):
        result = self.glm._parse_response(self._make_response(""))
        assert isinstance(result, dict)

    def test_graceful_on_malformed_response(self):
        result = self.glm._parse_response({})
        assert isinstance(result, dict)

    def test_raw_preserved(self):
        content = "RECOMMENDATION: Do something.\nREASONING: Because.\nIMPACT: RM100.\nCONFIDENCE: High — sure."
        result = self.glm._parse_response(self._make_response(content))
        assert result["raw"] == content


# ---------------------------------------------------------------------------
# validate_response
# ---------------------------------------------------------------------------

class TestValidateResponse:
    def test_valid_response(self):
        assert GLMIntegration._validate_response(
            {"choices": [{"message": {"content": "some text"}}]}
        )

    def test_empty_content_is_invalid(self):
        assert not GLMIntegration._validate_response(
            {"choices": [{"message": {"content": ""}}]}
        )

    def test_missing_choices_is_invalid(self):
        assert not GLMIntegration._validate_response({})

    def test_none_content_is_invalid(self):
        assert not GLMIntegration._validate_response(
            {"choices": [{"message": {"content": None}}]}
        )


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_returns_string(self):
        prompt = build_prompt("Where can I cut costs?", 3000, 1000, 600, 200, 300, 200)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_income_appears_in_prompt(self):
        prompt = build_prompt("Where can I cut costs?", 3000, 1000, 600, 200, 300, 200)
        assert "3000" in prompt

    def test_savings_calculated_correctly(self):
        # income=3000, expenses=1000+600+200+300+200=2300, savings=700
        prompt = build_prompt("Where can I cut costs?", 3000, 1000, 600, 200, 300, 200)
        assert "700" in prompt

    def test_negative_savings_in_prompt(self):
        # income=2000, expenses=2500, savings=-500
        prompt = build_prompt("Where can I cut costs?", 2000, 1200, 500, 200, 300, 300)
        assert "-500" in prompt

    def test_all_decision_types_covered(self):
        for decision_type in PROMPT_TEMPLATES:
            prompt = build_prompt(decision_type, 3000, 1000, 600, 200, 300, 200)
            assert isinstance(prompt, str) and len(prompt) > 100

    def test_unknown_decision_type_uses_default(self):
        prompt = build_prompt("Something unknown", 3000, 1000, 600, 200, 300, 200)
        assert isinstance(prompt, str) and len(prompt) > 0
