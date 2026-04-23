import json
import os
import threading
import customtkinter as ctk
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("ILMU_API_KEY")
BASE_URL = os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/v1")
MODEL    = "ilmu-glm-5.1"

SAVE_FILE = os.path.join(os.path.expanduser("~"), "finance_advisor_data.json")

SYSTEM_PROMPT = """
You are a personal finance advisor AI for Malaysian users (currency: RM).
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
    required_keys = ["allowance", "spending", "passive_income", "investment", "goal"]
    for key in required_keys:
        if key not in user_data:
            return _error_response(f"Missing field: {key}")

    total_spending = sum(user_data["spending"].values())
    total_income   = user_data["allowance"] + user_data["passive_income"]
    net            = total_income - total_spending
    savings_rate   = (net / total_income * 100) if total_income > 0 else 0
    breakdown      = ", ".join(
        f"{cat} RM {amt}" for cat, amt in user_data["spending"].items() if amt > 0
    ) or "none entered"

    user_message = f"""Monthly Allowance: RM {user_data['allowance']}
Passive Income: RM {user_data['passive_income']}
Current Investment Value: RM {user_data['investment']}
Monthly Spending: RM {total_spending} ({breakdown})
Net Monthly Cash Flow: RM {net:.2f}
Savings Rate: {savings_rate:.1f}%
Financial Goal: {user_data['goal']}"""

    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message}
            ]
        )
        raw   = response.choices[0].message.content
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)

    except json.JSONDecodeError:
        return _error_response("AI returned an unreadable response. Please try again.")
    except Exception as e:
        return _error_response(f"API error: {str(e)}")


def _error_response(message: str) -> dict:
    return {
        "recommendation": "Unable to generate advice.",
        "reasoning":       message,
        "expected_impact": "N/A",
        "confidence":      "0%",
        "reminders":       ["Please check your inputs and try again."]
    }


# ─────────────────────────────────────────
# Save / Load helpers
# ─────────────────────────────────────────
def load_saved_data() -> dict:
    """Load saved income and expense data from JSON file."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_data(data: dict):
    """Persist income and expense data to JSON file."""
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Save error: {e}")


# ─────────────────────────────────────────
# App appearance
# ─────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FinanceAdvisorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance AI — Powered by ilmu.ai")
        self.geometry("1200x820")
        self.minsize(1000, 700)
        self._saved_data = load_saved_data()
        self._build_layout()
        # Restore saved values after UI is built
        self._restore_saved_values()

    # ── Layout ──────────────────────────────
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.left_panel.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="nsew")

        self.right_panel = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.right_panel.grid(row=0, column=1, padx=(6, 12), pady=12, sticky="nsew")

        self._build_inputs()
        self._build_outputs()

    # ── Left panel: inputs ───────────────────
    def _build_inputs(self):
        p = self.left_panel

        ctk.CTkLabel(p, text="💰 Financial Input",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 4))
        ctk.CTkLabel(p, text=f"Powered by ilmu.ai {MODEL} · RM currency",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 16))

        # ── Income Section ───────────────────
        self._section(p, "Income Details")
        income_f = ctk.CTkFrame(p)
        income_f.pack(fill="x", padx=8, pady=4)

        self.allowance   = self._field(income_f, "Monthly Active Income (RM)")
        self.passive     = self._field(income_f, "Monthly Passive Income (RM)")
        self.investments = self._field(income_f, "Current Investment Value (RM)")

        # Income status label
        self.income_status = ctk.CTkLabel(income_f, text="",
                                          font=ctk.CTkFont(size=11), text_color="gray")
        self.income_status.pack(anchor="w", padx=10, pady=(0, 2))

        # Income Update button (grey)
        ctk.CTkButton(
            income_f,
            text="💾  Update Income",
            fg_color="gray40",
            hover_color="gray30",
            font=ctk.CTkFont(size=13),
            command=self._update_income
        ).pack(fill="x", padx=10, pady=(4, 12))

        # ── Expenses Section ─────────────────
        self._section(p, "Monthly Expenses")
        exp_f = ctk.CTkFrame(p)
        exp_f.pack(fill="x", padx=8, pady=4)

        self.expense_entries = {}
        categories = [
            ("Housing / Rent",   "housing"),
            ("Food & Groceries", "food"),
            ("Transport",        "transport"),
            ("Utilities",        "utilities"),
            ("Entertainment",    "entertainment"),
            ("Shopping",         "shopping"),
            ("Healthcare",       "healthcare"),
            ("Education",        "education"),
            ("Other",            "other"),
        ]
        for i in range(0, len(categories), 2):
            row = ctk.CTkFrame(exp_f, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)
            row.columnconfigure(0, weight=1)
            row.columnconfigure(1, weight=1)

            left_label, left_key = categories[i]
            left_cell = ctk.CTkFrame(row, fg_color="transparent")
            left_cell.grid(row=0, column=0, sticky="ew", padx=(0, 6))
            ctk.CTkLabel(left_cell, text=left_label, anchor="w",
                         font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 2))
            e_left = ctk.CTkEntry(left_cell, placeholder_text="0",
                                  font=ctk.CTkFont(size=12))
            e_left.pack(fill="x")
            self.expense_entries[left_key] = e_left

            if i + 1 < len(categories):
                right_label, right_key = categories[i + 1]
                right_cell = ctk.CTkFrame(row, fg_color="transparent")
                right_cell.grid(row=0, column=1, sticky="ew", padx=(6, 0))
                ctk.CTkLabel(right_cell, text=right_label, anchor="w",
                             font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 2))
                e_right = ctk.CTkEntry(right_cell, placeholder_text="0",
                                       font=ctk.CTkFont(size=12))
                e_right.pack(fill="x")
                self.expense_entries[right_key] = e_right

        # Expenses status label
        self.expenses_status = ctk.CTkLabel(exp_f, text="",
                                            font=ctk.CTkFont(size=11), text_color="gray")
        self.expenses_status.pack(anchor="w", padx=16, pady=(4, 2))

        # Expenses Update button (grey)
        ctk.CTkButton(
            exp_f,
            text="💾  Update Expenses",
            fg_color="gray40",
            hover_color="gray30",
            font=ctk.CTkFont(size=13),
            command=self._update_expenses
        ).pack(fill="x", padx=10, pady=(4, 12))

        # ── Goal Section ─────────────────────
        self._section(p, "Financial Goal")
        goal_f = ctk.CTkFrame(p)
        goal_f.pack(fill="x", padx=8, pady=4)

        self.goal_amount  = self._field(goal_f, "Target Savings (RM)")
        self.goal_months  = self._field(goal_f, "Timeline (months)")
        ctk.CTkLabel(goal_f, text="Goal Purpose",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(4, 0))
        self.goal_purpose = ctk.CTkComboBox(
            goal_f,
            values=["Emergency Fund", "Home Down Payment", "Car Purchase",
                    "Vacation", "Education", "Retirement", "Investment", "Other"],
            font=ctk.CTkFont(size=12)
        )
        self.goal_purpose.pack(fill="x", padx=10, pady=(4, 12))

        # ── Action Buttons ───────────────────
        btn_f = ctk.CTkFrame(p, fg_color="transparent")
        btn_f.pack(fill="x", padx=8, pady=12)
        self.analyze_btn = ctk.CTkButton(
            btn_f,
            text="🔍  Analyse & Get Recommendations",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            command=self._start_analysis
        )
        self.analyze_btn.pack(fill="x", pady=(0, 6))
        ctk.CTkButton(
            btn_f, text="🗑️  Clear All",
            fg_color="gray40", hover_color="gray30",
            font=ctk.CTkFont(size=13),
            command=self._clear_all
        ).pack(fill="x")

        self.status_label = ctk.CTkLabel(p, text="", font=ctk.CTkFont(size=12),
                                         text_color="gray")
        self.status_label.pack(pady=6)

    # ── Right panel: outputs ─────────────────
    def _build_outputs(self):
        p = self.right_panel

        ctk.CTkLabel(p, text="📊 Analysis & Recommendations",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 4))
        ctk.CTkLabel(p, text="AI-powered advice based on your data",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 16))

        self._section(p, "Financial Summary")
        self.summary_box = self._textbox(p, height=130)

        self._section(p, "💡 Recommendation")
        self.rec_box = self._textbox(p, height=100)

        self._section(p, "🧠 Reasoning (Why)")
        self.reason_box = self._textbox(p, height=120)

        self._section(p, "📈 Expected Impact")
        self.impact_box = self._textbox(p, height=90)

        self._section(p, "📊 AI Confidence")
        conf_f = ctk.CTkFrame(p)
        conf_f.pack(fill="x", padx=8, pady=4)
        self.conf_bar = ctk.CTkProgressBar(conf_f)
        self.conf_bar.pack(fill="x", padx=12, pady=(10, 4))
        self.conf_bar.set(0)
        self.conf_label = ctk.CTkLabel(conf_f, text="Confidence: —",
                                       font=ctk.CTkFont(size=13))
        self.conf_label.pack(padx=12, pady=(0, 10))

        self._section(p, "⏰ Reminders")
        self.reminder_box = self._textbox(p, height=90)

    # ── Helpers ──────────────────────────────
    def _section(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
                         anchor="w", padx=10, pady=(12, 2))

    def _field(self, parent, label):
        ctk.CTkLabel(parent, text=label,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(6, 0))
        e = ctk.CTkEntry(parent, font=ctk.CTkFont(size=13))
        e.pack(fill="x", padx=10, pady=(2, 4))
        return e

    def _textbox(self, parent, height=100):
        box = ctk.CTkTextbox(parent, height=height, font=ctk.CTkFont(size=13))
        box.pack(fill="x", padx=8, pady=4)
        return box

    def _get_float(self, widget, default=0.0):
        try:
            return float(widget.get()) if widget.get().strip() else default
        except ValueError:
            return default

    def _write(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def _set_entry(self, entry, value):
        """Set an entry field to a value, clearing it first."""
        entry.delete(0, "end")
        if value:
            entry.insert(0, str(value))

    # ── Save / Load logic ────────────────────
    def _restore_saved_values(self):
        """Populate fields from saved data on startup."""
        income = self._saved_data.get("income", {})
        if income:
            self._set_entry(self.allowance,   income.get("allowance", ""))
            self._set_entry(self.passive,     income.get("passive", ""))
            self._set_entry(self.investments, income.get("investments", ""))
            self.income_status.configure(
                text=f"✅ Income loaded from saved data", text_color="green")

        expenses = self._saved_data.get("expenses", {})
        if expenses:
            for key, entry in self.expense_entries.items():
                self._set_entry(entry, expenses.get(key, ""))
            self.expenses_status.configure(
                text=f"✅ Expenses loaded from saved data", text_color="green")

    def _update_income(self):
        """Save current income fields to disk."""
        income_data = {
            "allowance":    self.allowance.get().strip(),
            "passive":      self.passive.get().strip(),
            "investments":  self.investments.get().strip(),
        }
        self._saved_data["income"] = income_data
        save_data(self._saved_data)

        # Show confirmation with totals
        allowance   = self._get_float(self.allowance)
        passive     = self._get_float(self.passive)
        investments = self._get_float(self.investments)
        total       = allowance + passive

        self.income_status.configure(
            text=f"✅ Saved — Total Income: RM {total:,.2f} | Portfolio: RM {investments:,.2f}",
            text_color="green"
        )
        # Fade back to neutral after 4 seconds
        self.after(4000, lambda: self.income_status.configure(
            text="💾 Income data saved", text_color="gray"))

    def _update_expenses(self):
        """Save current expense fields to disk."""
        expenses_data = {
            key: entry.get().strip()
            for key, entry in self.expense_entries.items()
        }
        self._saved_data["expenses"] = expenses_data
        save_data(self._saved_data)

        # Show confirmation with total
        total_exp = sum(self._get_float(e) for e in self.expense_entries.values())

        self.expenses_status.configure(
            text=f"✅ Saved — Total Expenses: RM {total_exp:,.2f}",
            text_color="green"
        )
        self.after(4000, lambda: self.expenses_status.configure(
            text="💾 Expenses data saved", text_color="gray"))

    # ── Analysis ─────────────────────────────
    def _start_analysis(self):
        allowance = self._get_float(self.allowance)
        if allowance <= 0:
            self.status_label.configure(
                text="⚠️  Please enter a monthly allowance.", text_color="orange")
            return

        self.analyze_btn.configure(state="disabled", text="⏳  Analysing...")
        self.status_label.configure(text=f"Calling ilmu.ai {MODEL}…", text_color="gray")
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _run_analysis(self):
        spending = {
            key: self._get_float(entry)
            for key, entry in self.expense_entries.items()
        }
        user_data = {
            "allowance":      self._get_float(self.allowance),
            "passive_income": self._get_float(self.passive),
            "investment":     self._get_float(self.investments),
            "spending":       spending,
            "goal": (
                f"Save RM {self._get_float(self.goal_amount):.0f} "
                f"in {int(self._get_float(self.goal_months, 12))} months "
                f"for: {self.goal_purpose.get()}"
            )
        }
        result = get_finance_advice(user_data)
        self.after(0, lambda: self._display_results(result, user_data))

    def _display_results(self, result: dict, user_data: dict):
        total_income = user_data["allowance"] + user_data["passive_income"]
        total_exp    = sum(user_data["spending"].values())
        net          = total_income - total_exp
        rate         = (net / total_income * 100) if total_income > 0 else 0

        self._write(self.summary_box,
            f"Total Monthly Income:    RM {total_income:,.2f}\n"
            f"Total Monthly Expenses:  RM {total_exp:,.2f}\n"
            f"Net Monthly Cash Flow:   RM {net:,.2f}\n"
            f"Current Savings Rate:    {rate:.1f}%\n"
            f"Investment Portfolio:    RM {user_data['investment']:,.2f}"
        )
        self._write(self.rec_box,    result.get("recommendation", "—"))
        self._write(self.reason_box, result.get("reasoning",       "—"))
        self._write(self.impact_box, result.get("expected_impact", "—"))

        conf_str = result.get("confidence", "0%")
        try:
            conf_val = int(conf_str.replace("%", "").strip()) / 100
        except ValueError:
            conf_val = 0
        self.conf_bar.set(min(conf_val, 1.0))
        self.conf_label.configure(text=f"Confidence: {conf_str}")

        reminders = result.get("reminders", [])
        self._write(self.reminder_box, "\n".join(f"→  {r}" for r in reminders))

        self.analyze_btn.configure(state="normal",
                                   text="🔍  Analyse & Get Recommendations")
        self.status_label.configure(text="✅  Analysis complete.", text_color="green")

    def _clear_all(self):
        for w in [self.allowance, self.passive, self.investments,
                  self.goal_amount, self.goal_months]:
            w.delete(0, "end")
        for e in self.expense_entries.values():
            e.delete(0, "end")
        for box in [self.summary_box, self.rec_box, self.reason_box,
                    self.impact_box, self.reminder_box]:
            box.configure(state="normal")
            box.delete("1.0", "end")
            box.configure(state="disabled")
        self.conf_bar.set(0)
        self.conf_label.configure(text="Confidence: —")
        self.status_label.configure(text="")
        self.income_status.configure(text="")
        self.expenses_status.configure(text="")


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = FinanceAdvisorApp()
    app.mainloop()
