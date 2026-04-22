import os
import json

# ── when API key arrives, uncomment these two lines ──
# from anthropic import Anthropic
# from dotenv import load_dotenv; load_dotenv()

# ─────────────────────────────────────────
# SYSTEM PROMPT — the brain of your assistant
# ─────────────────────────────────────────
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

# ─────────────────────────────────────────
# MAIN FUNCTION — this is what Member 2 imports
# ─────────────────────────────────────────
def get_finance_advice(user_data: dict) -> dict:
    """
    Input:  user_data dict with keys:
              - allowance (float)
              - spending (dict of category: amount)
              - passive_income (float)
              - investment (float)
              - goal (str)
    Output: dict with recommendation, reasoning,
            expected_impact, confidence, reminders
    """

    # -- Validate input --
    required_keys = ["allowance", "spending", "passive_income", "investment", "goal"]
    for key in required_keys:
        if key not in user_data:
            return _error_response(f"Missing field: {key}")

    # -- Format the user message --
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

    # ── MOCK RESPONSE (remove this block once API key arrives) ──
    mock_response = {
        "recommendation": f"Reduce discretionary spending by RM 80/month and redirect it to savings.",
        "reasoning": f"Your total spending is RM {total_spending} against an allowance of RM {user_data['allowance']}. "
                     f"Your goal '{user_data['goal']}' requires a higher savings rate than your current pace.",
        "expected_impact": "You will reach your goal approximately 2 months earlier with an added RM 300 buffer.",
        "confidence": "80%",
        "reminders": [
            "Review your subscriptions this weekend",
            "Set up an auto-transfer on the day you receive your allowance",
            "Log your daily spending for the next 7 days"
        ]
    }
    return mock_response
    # ── END MOCK — real API call goes below when key is ready ──

    # ── REAL API CALL (uncomment when key arrives) ──
    # try:
    #     client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    #     response = client.messages.create(
    #         model="claude-sonnet-4-20250514",
    #         max_tokens=1000,
    #         system=SYSTEM_PROMPT,
    #         messages=[{"role": "user", "content": user_message}]
    #     )
    #     raw = response.content[0].text
    #     return json.loads(raw)
    # except json.JSONDecodeError:
    #     return _error_response("AI returned unreadable response. Please try again.")
    # except Exception as e:
    #     return _error_response(f"API error: {str(e)}")


# ─────────────────────────────────────────
# ERROR HELPER
# ─────────────────────────────────────────
def _error_response(message: str) -> dict:
    return {
        "recommendation": "Unable to generate advice.",
        "reasoning": message,
        "expected_impact": "N/A",
        "confidence": "0%",
        "reminders": ["Please check your inputs and try again."]
    }