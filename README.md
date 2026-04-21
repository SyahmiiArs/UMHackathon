# 🧠 BudgetBrain — GLM-Powered Personal Finance Decision Assistant

> **UMHackathon 2026 · Domain 2: AI for Economic Empowerment & Decision Intelligence**

BudgetBrain uses the Z.AI GLM large language model to turn raw monthly expense numbers into
actionable, personalised financial decisions — telling you **where** to cut, **why**, and
**how much** you will save.

---

## 🚀 Quick Start

```bash
# 1. Clone and enter the repo
git clone https://github.com/SyahmiiArs/UMHackathon.git
cd UMHackathon

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set your GLM API key — app works with a mock if omitted
export GLM_API_KEY="your-key-here"

# 4. Run the app
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```
UMHackathon/
├── app.py               # Streamlit frontend (Member 2)
├── glm_integration.py   # GLM API + mock fallback (Member 1)
├── prompts.py           # Few-shot prompt templates (Member 1)
├── requirements.txt     # Python dependencies
└── tests/
    └── test_glm_integration.py   # Unit tests (Member 3)
```

---

## 🔑 GLM Integration

| Behaviour | Detail |
|-----------|--------|
| Real API | Set `GLM_API_KEY` env var — calls `glm-4` model |
| Mock fallback | Works out-of-the-box with no API key |
| Retry logic | Up to 2 retries, 10-second timeout |
| Error handling | API timeout / invalid response → auto-fallback to mock |
| Token budget | Prompts kept under 1 500 tokens |

### Decision types supported

1. **Where can I cut costs?**
2. **How can I increase savings?**
3. **Is my spending balanced?**
4. **What should I prioritize this month?**

Each prompt uses few-shot examples and enforces a 4-section structured output:
`RECOMMENDATION · REASONING · IMPACT · CONFIDENCE`

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

22 unit tests covering mock responses, prompt building, response parsing, and edge cases.

---

## 👥 Team BudgetBrain

| Member | Role |
|--------|------|
| Syameer (M1) | GLM Integration Lead |
| Daus (M2) | Frontend Developer |
| Adif (M3) | QA & Testing Lead |
| Faiz (M4) | Documentation Lead |
| Syahmi (M5) | Pitch & Video Lead |
