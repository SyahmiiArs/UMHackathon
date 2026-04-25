# ai_tests.py - Test AI outputs
from glm_engine import get_finance_advice

print("=" * 50)
print("AI-01: Student with laptop goal")
print("=" * 50)

test_1 = {
    "allowance": 800,
    "passive_income": 200,
    "investment": 500,
    "spending": {"food": 400, "transport": 150, "entertainment": 200},
    "goal": "Save RM2000 for laptop in 5 months"
}
result_1 = get_finance_advice(test_1)
print(f"Recommendation: {result_1.get('recommendation', 'MISSING')}")
print(f"Reasoning: {result_1.get('reasoning', 'MISSING')}")
print(f"Expected impact: {result_1.get('expected_impact', 'MISSING')}")
print(f"Confidence: {result_1.get('confidence', 'MISSING')}")
print(f"Reminders: {result_1.get('reminders', 'MISSING')}")
print()

print("=" * 50)
print("AI-02: House down payment goal")
print("=" * 50)

test_2 = {
    "allowance": 3000,
    "passive_income": 0,
    "investment": 2000,
    "spending": {"housing": 1500, "food": 800, "transport": 300},
    "goal": "Save RM10000 for house down payment in 12 months"
}
result_2 = get_finance_advice(test_2)
print(f"Recommendation: {result_2.get('recommendation', 'MISSING')}")
print(f"Reasoning: {result_2.get('reasoning', 'MISSING')}")
print(f"Expected impact: {result_2.get('expected_impact', 'MISSING')}")
print(f"Confidence: {result_2.get('confidence', 'MISSING')}")
print(f"Reminders: {result_2.get('reminders', 'MISSING')}")
print()

print("=" * 50)
print("AI-03: Vague goal (should ask clarifying question)")
print("=" * 50)

test_3 = {
    "allowance": 500,
    "passive_income": 0,
    "investment": 0,
    "spending": {"food": 450, "transport": 100, "entertainment": 50},
    "goal": "I want to be rich"
}
result_3 = get_finance_advice(test_3)
print(f"Recommendation: {result_3.get('recommendation', 'MISSING')}")
print(f"Reasoning: {result_3.get('reasoning', 'MISSING')}")
print(f"Expected impact: {result_3.get('expected_impact', 'MISSING')}")
print(f"Confidence: {result_3.get('confidence', 'MISSING')}")
print(f"Reminders: {result_3.get('reminders', 'MISSING')}")
print()