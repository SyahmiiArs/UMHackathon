from glm_engine import get_finance_advice

# Test case 1 — normal user
user1 = {
    "allowance": 1200,
    "spending": {"food": 400, "transport": 150, "entertainment": 200, "others": 200},
    "passive_income": 100,
    "investment": 50,
    "goal": "Save RM 5,000 for a laptop in 8 months"
}

# Test case 2 — overspending user
user2 = {
    "allowance": 800,
    "spending": {"food": 500, "transport": 200, "entertainment": 300, "others": 100},
    "passive_income": 0,
    "investment": 0,
    "goal": "Save RM 2,000 for emergency fund in 6 months"
}

# Test case 3 — high income user
user3 = {
    "allowance": 3000,
    "spending": {"food": 600, "transport": 200, "entertainment": 100, "others": 150},
    "passive_income": 500,
    "investment": 300,
    "goal": "Save RM 20,000 for a car in 24 months"
}

# Test case 4 — missing field (error handling test)
user4 = {
    "allowance": 1000,
    "spending": {"food": 300},
    # missing passive_income, investment, goal on purpose
}

print("=== TEST 1 — Normal user ===")
print(get_finance_advice(user1))
print()

print("=== TEST 2 — Overspending user ===")
print(get_finance_advice(user2))
print()

print("=== TEST 3 — High income user ===")
print(get_finance_advice(user3))
print()

print("=== TEST 4 — Missing fields (error test) ===")
print(get_finance_advice(user4))