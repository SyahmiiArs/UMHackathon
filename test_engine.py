# test_engine.py - Unit tests for GLM engine
from glm_engine import get_finance_advice

print("=" * 60)
print("RUNNING UNIT TESTS")
print("=" * 60)

# Test 1: Normal user
print("\n✅ TEST 1: Normal user")
test_user = {
    "allowance": 800,
    "passive_income": 200,
    "investment": 500,
    "spending": {"food": 400, "transport": 150, "entertainment": 200},
    "goal": "Save RM2000 for laptop in 5 months"
}
try:
    result = get_finance_advice(test_user)
    if all(key in result for key in ["recommendation", "reasoning", "expected_impact", "confidence", "reminders"]):
        print("   ✅ PASS - All 5 sections present")
    else:
        print("   ❌ FAIL - Missing sections")
except Exception as e:
    print(f"   ❌ FAIL - Error: {e}")

# Test 2: Missing field
print("\n✅ TEST 2: Missing field (error handling)")
test_missing = {
    "allowance": 1000,
    "spending": {"food": 500}
}
try:
    result = get_finance_advice(test_missing)
    print(f"   ✅ PASS - Handled gracefully: {result.get('recommendation')}")
except Exception as e:
    print(f"   ❌ FAIL - Crash: {e}")

print("\n" + "=" * 60)
print("UNIT TESTS COMPLETE")
print("=" * 60)