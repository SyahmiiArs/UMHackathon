"""BudgetBrain — GLM-Powered Personal Finance Decision Assistant.

Run with:  streamlit run app.py
"""

import streamlit as st

from glm_integration import GLMIntegration

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="BudgetBrain",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🧠 BudgetBrain")
st.caption("GLM-Powered Financial Decision Intelligence | Domain 2 — AI for Economic Empowerment")
st.divider()

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "decisions_accepted" not in st.session_state:
    st.session_state.decisions_accepted = 0
if "total_savings_committed" not in st.session_state:
    st.session_state.total_savings_committed = 0.0
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_impact_rm" not in st.session_state:
    st.session_state.last_impact_rm = 0.0

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
st.subheader("📊 Your Monthly Finances (RM)")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input("💰 Monthly Income", min_value=0, value=3000, step=50)
    rent = st.number_input("🏠 Rent / Housing", min_value=0, value=1000, step=50)
    food = st.number_input("🍜 Food & Groceries", min_value=0, value=600, step=50)
with col2:
    transport = st.number_input("🚗 Transport", min_value=0, value=200, step=50)
    entertainment = st.number_input("🎬 Entertainment", min_value=0, value=300, step=50)
    others = st.number_input("📦 Others", min_value=0, value=200, step=50)

total_expenses = rent + food + transport + entertainment + others
savings = income - total_expenses

# Live summary strip
col_exp, col_sav = st.columns(2)
col_exp.metric("Total Expenses", f"RM {total_expenses:,.0f}")
savings_delta_label = "surplus" if savings >= 0 else "deficit ⚠️"
col_sav.metric(f"Monthly {savings_delta_label}", f"RM {abs(savings):,.0f}",
               delta=f"RM {savings:,.0f}", delta_color="normal" if savings >= 0 else "inverse")

st.divider()

# Decision type selector
question = st.selectbox(
    "🤔 What decision do you need help with?",
    [
        "Where can I cut costs?",
        "How can I increase savings?",
        "Is my spending balanced?",
        "What should I prioritize this month?",
    ],
)

# ---------------------------------------------------------------------------
# GLM analysis button
# ---------------------------------------------------------------------------
if st.button("🧠 Ask GLM", type="primary", use_container_width=True):
    if income == 0:
        st.error("Please enter your monthly income before asking GLM.")
    else:
        with st.spinner("GLM is analysing your finances…"):
            glm = GLMIntegration()
            result = glm.get_recommendation(
                income, rent, food, transport, entertainment, others, question
            )
        st.session_state.last_result = result

        # Try to extract a numeric impact figure for the savings tracker
        import re
        impact_text = result.get("impact", "")
        amounts = re.findall(r"RM\s*([\d,]+)", impact_text)
        if amounts:
            try:
                st.session_state.last_impact_rm = float(amounts[0].replace(",", ""))
            except ValueError:
                st.session_state.last_impact_rm = 0.0

# ---------------------------------------------------------------------------
# Display recommendation
# ---------------------------------------------------------------------------
if st.session_state.last_result:
    result = st.session_state.last_result
    st.success("✅ GLM has generated your recommendation")

    st.markdown("#### 💡 Recommendation")
    st.info(result.get("recommendation") or result.get("raw", ""))

    if result.get("reasoning"):
        st.markdown("#### 🔍 Reasoning")
        st.write(result["reasoning"])

    if result.get("impact"):
        st.markdown("#### 📈 Expected Impact")
        st.write(result["impact"])

    if result.get("confidence"):
        st.markdown("#### 🎯 Confidence")
        st.write(result["confidence"])

    # Savings meter
    if st.session_state.last_impact_rm > 0:
        max_display = max(st.session_state.last_impact_rm * 2, 1000)
        progress_val = min(st.session_state.last_impact_rm / max_display, 1.0)
        st.markdown("#### 💰 Monthly Savings Potential")
        st.progress(progress_val)
        yearly = st.session_state.last_impact_rm * 12
        st.caption(
            f"RM {st.session_state.last_impact_rm:,.0f}/month  →  "
            f"RM {yearly:,.0f}/year"
        )

    st.divider()

    # Accept / Reject
    col_accept, col_reject = st.columns(2)
    with col_accept:
        if st.button("✅ Accept Recommendation", use_container_width=True):
            st.session_state.decisions_accepted += 1
            st.session_state.total_savings_committed += st.session_state.last_impact_rm
            st.balloons()
            st.success(
                f"Tracked! Committed to saving ~RM {st.session_state.last_impact_rm:,.0f}/month."
            )
    with col_reject:
        if st.button("❌ Reject / Try Again", use_container_width=True):
            st.session_state.last_result = None
            st.rerun()

# ---------------------------------------------------------------------------
# Impact tracker sidebar strip
# ---------------------------------------------------------------------------
if st.session_state.decisions_accepted > 0:
    st.divider()
    st.markdown("### 🏆 Your Progress")
    c1, c2, c3 = st.columns(3)
    c1.metric("Decisions Accepted", st.session_state.decisions_accepted)
    c2.metric("Monthly Savings Committed", f"RM {st.session_state.total_savings_committed:,.0f}")
    c3.metric("Yearly Projection", f"RM {st.session_state.total_savings_committed * 12:,.0f}")

# ---------------------------------------------------------------------------
# Without GLM comparison (critical path evidence for judges)
# ---------------------------------------------------------------------------
st.divider()
with st.expander("🔍 Why GLM is essential — click to see", expanded=False):
    col_without, col_with = st.columns(2)
    with col_without:
        st.markdown("**❌ Without GLM**")
        st.markdown(
            f"""
            - Total expenses: **RM {total_expenses:,.0f}**
            - Monthly savings: **RM {savings:,.0f}**

            *That's all you get — raw numbers, no decision support.*
            """
        )
    with col_with:
        st.markdown("**✅ With GLM**")
        st.markdown(
            """
            - **WHERE** to cut a specific category
            - **WHY** that category, with reasoning
            - **HOW MUCH** you will save (RM/month + RM/year)
            - **Different** answers for different questions
            - **Confidence** score so you can trust the advice
            """
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Team BudgetBrain · UMHackathon 2026 · Domain 2: AI for Economic Empowerment & Decision Intelligence"
)
