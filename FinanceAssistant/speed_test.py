# speed_test.py - Test API response time
import time
from glm_engine import get_finance_advice

print("=" * 50)
print("API PERFORMANCE TEST")
print("=" * 50)

test_data = {
    "allowance": 800,
    "passive_income": 200,
    "investment": 500,
    "spending": {"food": 400, "transport": 150, "entertainment": 200},
    "goal": "Save RM2000 for laptop in 5 months"
}

print("📡 Calling GLM API...")
start = time.time()

try:
    result = get_finance_advice(test_data)
    end = time.time()
    response_time = (end - start)
    print(f"✅ Response time: {response_time:.2f} seconds")
    print(f"   ({(response_time * 1000):.0f} ms)")
    
    # Check quality
    if response_time < 8:
        print("✅ Within 8 second target")
    else:
        print(f"⚠️  Exceeds 8 second target")
        
except Exception as e:
    end = time.time()
    print(f"❌ Error after {(end - start):.2f} seconds: {e}")