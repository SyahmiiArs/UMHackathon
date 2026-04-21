"""GLM API integration with mock fallback, retry logic, and error handling."""

import os
import time
import re
import requests
from typing import Any, Dict, Optional

from prompts import build_prompt


class GLMIntegration:
    """Wraps the Z.AI GLM API with automatic mock fallback."""

    DEFAULT_TIMEOUT = 10
    MAX_RETRIES = 2

    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GLM_API_KEY")
        self.api_url = api_url or os.environ.get(
            "GLM_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        )
        self.use_mock = not bool(self.api_key)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_recommendation(
        self,
        income: float,
        rent: float,
        food: float,
        transport: float,
        entertainment: float,
        others: float,
        question: str,
    ) -> Dict[str, Any]:
        """Build prompt, call GLM (or mock), and return a parsed result dict."""
        prompt = build_prompt(question, income, rent, food, transport, entertainment, others)
        raw = self.call_glm(prompt)
        return self._parse_response(raw)

    def call_glm(self, prompt: str) -> Dict[str, Any]:
        """Dispatch to mock or real API automatically."""
        if self.use_mock:
            return self._call_mock(prompt)
        return self._call_real_api(prompt)

    # ------------------------------------------------------------------
    # Mock implementation
    # ------------------------------------------------------------------

    def _call_mock(self, prompt: str) -> Dict[str, Any]:
        """Return a deterministic mock response based on keywords in the prompt."""
        # Only inspect the user-specific section (after the few-shot examples block)
        user_section = prompt.split("Now analyze this user:")[-1] if "Now analyze this user:" in prompt else prompt
        prompt_lower = user_section.lower()

        if "savings=rm-" in prompt_lower or re.search(r"savings=rm-\d", prompt_lower):
            # Negative savings — urgent
            content = (
                "RECOMMENDATION: URGENT — Your expenses exceed your income. Immediately reduce rent or find a housemate.\n"
                "REASONING: Spending more than you earn creates debt that compounds rapidly. "
                "Rent is likely your largest controllable expense and the fastest way to restore balance.\n"
                "IMPACT: Reducing rent by RM300/month saves RM3,600/year and eliminates your monthly deficit.\n"
                "CONFIDENCE: High — eliminating a deficit is always the top priority."
            )
        elif "entertainment" in prompt_lower and "where can i cut" in prompt_lower:
            content = (
                "RECOMMENDATION: Reduce entertainment spending by RM150/month.\n"
                "REASONING: Entertainment typically offers the most flexibility. "
                "Cutting it to RM150 keeps leisure activities affordable while freeing up cash.\n"
                "IMPACT: Saving RM150/month = RM1,800/year. Your savings rate improves noticeably.\n"
                "CONFIDENCE: High — entertainment is discretionary and easy to reduce."
            )
        elif "increase savings" in prompt_lower:
            content = (
                "RECOMMENDATION: Apply the 50/30/20 rule — allocate 20% of income to savings automatically.\n"
                "REASONING: Automating savings removes the temptation to spend. "
                "Your current savings rate can be improved by trimming food and entertainment by 10% each.\n"
                "IMPACT: A 20% savings rate on your income adds up significantly over 12 months.\n"
                "CONFIDENCE: Medium — depends on your fixed commitments."
            )
        elif "balanced" in prompt_lower:
            content = (
                "RECOMMENDATION: Your spending is partially balanced, but review rent — it should stay ≤30% of income.\n"
                "REASONING: Healthy ratios are Rent≤30%, Food≤20%, Transport≤10%, Entertainment≤7%, Savings≥20%. "
                "Check each category against these benchmarks.\n"
                "IMPACT: Bringing all categories within healthy ratios could improve monthly savings by RM200-400.\n"
                "CONFIDENCE: High — ratio analysis is objective."
            )
        elif "prioritize" in prompt_lower:
            content = (
                "RECOMMENDATION: Build a 3-month emergency fund as your top priority this month.\n"
                "REASONING: Without an emergency fund, any unexpected expense forces debt. "
                "Set aside even RM100-200 extra this month toward a dedicated savings account.\n"
                "IMPACT: RM200/month × 12 = RM2,400 emergency fund in one year.\n"
                "CONFIDENCE: High — financial security is the foundation of all other goals."
            )
        else:
            content = (
                "RECOMMENDATION: Review your largest expense category and reduce it by 10%.\n"
                "REASONING: A 10% reduction in your biggest spend typically has the highest absolute impact. "
                "Small consistent cuts accumulate into meaningful savings.\n"
                "IMPACT: Estimated RM100-300/month depending on your largest category.\n"
                "CONFIDENCE: Medium — exact savings depend on your specific situation."
            )

        return {"choices": [{"message": {"content": content}}]}

    # ------------------------------------------------------------------
    # Real API implementation
    # ------------------------------------------------------------------

    def _call_real_api(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """Call the GLM API with retry logic and timeout handling."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 512,
        }

        last_error: Optional[Exception] = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()
                if self._validate_response(data):
                    return data
                # Invalid structure — retry with lower temperature
                payload["temperature"] = 0.1
                last_error = ValueError("GLM response missing required fields")
            except requests.Timeout as exc:
                last_error = exc
                if attempt < self.MAX_RETRIES:
                    time.sleep(1)
            except requests.RequestException as exc:
                last_error = exc
                if attempt < self.MAX_RETRIES:
                    time.sleep(1)

        # All retries exhausted — fall back to mock
        return self._call_mock(prompt)

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_response(data: Dict[str, Any]) -> bool:
        """Return True if the response contains the expected structure."""
        try:
            content = data["choices"][0]["message"]["content"]
            return bool(content and isinstance(content, str))
        except (KeyError, IndexError, TypeError):
            return False

    def _parse_response(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Extract RECOMMENDATION / REASONING / IMPACT / CONFIDENCE sections."""
        try:
            content: str = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            content = ""

        result = {
            "recommendation": "",
            "reasoning": "",
            "impact": "",
            "confidence": "",
            "raw": content,
        }

        patterns = {
            "recommendation": r"RECOMMENDATION:\s*(.+?)(?=\nREASONING:|\Z)",
            "reasoning": r"REASONING:\s*(.+?)(?=\nIMPACT:|\Z)",
            "impact": r"IMPACT:\s*(.+?)(?=\nCONFIDENCE:|\Z)",
            "confidence": r"CONFIDENCE:\s*(.+?)(?=\Z)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()

        if not any([result["recommendation"], result["reasoning"]]):
            result["recommendation"] = content.strip() or "Unable to generate a recommendation. Please try again."

        return result
