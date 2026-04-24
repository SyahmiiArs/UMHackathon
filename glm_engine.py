import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a personal finance advisor AI.
The user will provide their monthly financial data.
You must always respond in valid JSON with exactly these fields:
- recommendation (string)
- reasoning (string)
- expected_impact (string)
- confidence (string, e.g. "82%")
- reminders (list of 2-3 short strings)

Be specific, practical, and encouraging.
Use the exact numbers the user provides in your reasoning.
Never respond with anything outside the JSON structure.
"""

def get_finance_advice(user_data: dict) -> dict:
    # Validate input
    required_keys = ["allowance", "spending", "passive_income", "investment", "goal"]
    for key in required_keys:
        if key not in user_data:
            return _error_response(f"Missing field: {key}")

    # Format user message
    total_spending = sum(user_data["spending"].values())
    spending_breakdown = ", ".join(
        f"{cat} RM {amt}" for cat, amt in user_data["spending"].items()
    )

    user_message = f"""
    Monthly Allowance: RM {user_data['allowance']}
    Monthly Spending: RM {total_spending} ({spending_breakdown})
    Passive Income: RM {user_data['passive_income']}
    Monthly Investment: RM {user_data['investment']}
    Future Goal: {user_data['goal']}
    """

    try:
        client = Anthropic(
    api_key=os.getenv("ILMU_API_KEY"),
    base_url=os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/anthropic")
)
        response = client.messages.create(
            model="ilmu-glm-5.1",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        raw = response.content[0].text
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)

    except json.JSONDecodeError:
        return _error_response("AI returned unreadable response. Please try again.")
    except Exception as e:
        return _error_response(f"API error: {str(e)}")


def _error_response(message: str) -> dict:
    return {
        "recommendation": "Unable to generate advice.",
        "reasoning": message,
        "expected_impact": "N/A",
        "confidence": "0%",
        "reminders": ["Please check your inputs and try again."]
    }