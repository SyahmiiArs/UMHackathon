"""Prompt templates for GLM financial decision types."""

FEW_SHOT_EXAMPLES = """
Example 1:
User finances: Income=RM3000, Rent=RM1000, Food=RM600, Transport=RM200, Entertainment=RM300, Others=RM200, Savings=RM700
Question: Where can I cut costs?
Response:
RECOMMENDATION: Reduce entertainment spending by RM150/month.
REASONING: Entertainment at RM300 represents 10% of your income, which is above the recommended 5-7%. Cutting it to RM150 is a practical first step without sacrificing quality of life.
IMPACT: Saving RM150/month = RM1,800/year. Your savings rate improves from 23% to 28%.
CONFIDENCE: High — entertainment is the most flexible category in your budget.

Example 2:
User finances: Income=RM2000, Rent=RM1200, Food=RM500, Transport=RM200, Entertainment=RM200, Others=RM300, Savings=-RM400
Question: How can I increase savings?
Response:
RECOMMENDATION: URGENT — Your expenses exceed income by RM400/month. Immediate action needed.
REASONING: You are spending RM2400 on a RM2000 income. Rent alone is 60% of income (healthy max is 30%). Consider a cheaper room or finding a housemate to share rent.
IMPACT: If rent is reduced to RM800, you save RM400 and go from -RM400 to RM0, then build an emergency fund.
CONFIDENCE: High — rent reduction is the single highest-impact action available.
"""

PROMPT_TEMPLATES = {
    "Where can I cut costs?": """You are a personal finance advisor AI powered by GLM. Analyze the user's financial data and recommend the single most impactful cost-cutting action.

{few_shot}

Now analyze this user:
User finances: Income=RM{income}, Rent=RM{rent}, Food=RM{food}, Transport=RM{transport}, Entertainment=RM{entertainment}, Others=RM{others}, Savings=RM{savings}
Question: Where can I cut costs?

Respond EXACTLY in this format (no extra text):
RECOMMENDATION: [specific action]
REASONING: [2-3 sentences explaining why]
IMPACT: [RM amount saved per month and per year]
CONFIDENCE: [High/Medium/Low] — [one sentence reason]""",

    "How can I increase savings?": """You are a personal finance advisor AI powered by GLM. Analyze the user's financial data and recommend the best strategy to increase their monthly savings.

{few_shot}

Now analyze this user:
User finances: Income=RM{income}, Rent=RM{rent}, Food=RM{food}, Transport=RM{transport}, Entertainment=RM{entertainment}, Others=RM{others}, Savings=RM{savings}
Question: How can I increase savings?

Respond EXACTLY in this format (no extra text):
RECOMMENDATION: [specific action]
REASONING: [2-3 sentences explaining why]
IMPACT: [RM amount saved per month and per year]
CONFIDENCE: [High/Medium/Low] — [one sentence reason]""",

    "Is my spending balanced?": """You are a personal finance advisor AI powered by GLM. Evaluate whether the user's spending allocation follows healthy financial ratios and identify the most imbalanced category.

{few_shot}

Now analyze this user:
User finances: Income=RM{income}, Rent=RM{rent}, Food=RM{food}, Transport=RM{transport}, Entertainment=RM{entertainment}, Others=RM{others}, Savings=RM{savings}
Question: Is my spending balanced?

Respond EXACTLY in this format (no extra text):
RECOMMENDATION: [balanced or specific imbalance found]
REASONING: [2-3 sentences comparing to healthy ratios — Rent≤30%, Food≤20%, Transport≤10%, Entertainment≤7%, Savings≥20%]
IMPACT: [what adjusting the most imbalanced category would achieve]
CONFIDENCE: [High/Medium/Low] — [one sentence reason]""",

    "What should I prioritize this month?": """You are a personal finance advisor AI powered by GLM. Based on the user's current finances, recommend their single most important financial priority this month.

{few_shot}

Now analyze this user:
User finances: Income=RM{income}, Rent=RM{rent}, Food=RM{food}, Transport=RM{transport}, Entertainment=RM{entertainment}, Others=RM{others}, Savings=RM{savings}
Question: What should I prioritize this month?

Respond EXACTLY in this format (no extra text):
RECOMMENDATION: [specific priority action]
REASONING: [2-3 sentences explaining why this is the top priority right now]
IMPACT: [expected financial improvement in RM]
CONFIDENCE: [High/Medium/Low] — [one sentence reason]""",
}


def build_prompt(decision_type: str, income: float, rent: float, food: float,
                 transport: float, entertainment: float, others: float) -> str:
    """Build a prompt for the given decision type and financial inputs."""
    savings = income - rent - food - transport - entertainment - others
    template = PROMPT_TEMPLATES.get(decision_type, PROMPT_TEMPLATES["Where can I cut costs?"])
    return template.format(
        few_shot=FEW_SHOT_EXAMPLES,
        income=int(income),
        rent=int(rent),
        food=int(food),
        transport=int(transport),
        entertainment=int(entertainment),
        others=int(others),
        savings=int(savings),
    )
