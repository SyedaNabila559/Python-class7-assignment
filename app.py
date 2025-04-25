import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# --- Constants ---
PASSWORD = "1234"  # Change this to something secure

# --- OOP Classes ---
class Transaction:
    def __init__(self, amount, category, t_type, date, description=""):
        self.amount = amount
        self.category = category
        self.t_type = t_type
        self.date = date
        self.description = description

    def to_dict(self):
        return {
            "Amount": self.amount,
            "Category": self.category,
            "Type": self.t_type,
            "Date": self.date,
            "Description": self.description
        }

class FinanceTracker:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def get_dataframe(self):
        return pd.DataFrame([t.to_dict() for t in self.transactions])

    def get_summary(self):
        df = self.get_dataframe()
        if df.empty:
            return 0, 0, 0
        income = df[df["Type"] == "Income"]["Amount"].sum()
        expense = df[df["Type"] == "Expense"]["Amount"].sum()
        return income, expense, income - expense

    def get_expense_by_category(self):
        df = self.get_dataframe()
        if df.empty:
            return pd.Series()
        df = df[df["Type"] == "Expense"]
        return df.groupby("Category")["Amount"].sum()

class FinanceApp:
    def __init__(self):
        self.tracker = FinanceTracker()

    def run(self):
        st.set_page_config(page_title="💸 Finance Tracker", layout="centered")

        # 👋 Welcome message BEFORE password prompt
        st.markdown("## 👋 Welcome to your Personal Finance Tracker!")
        st.markdown("💼 Keep track of your income 💵 and expenses 💸 with ease. Let’s get started! 🚀")

        # --- Password/Login ---
        password = st.text_input("🔒 Enter Password", type="password")
        if password != PASSWORD:
            st.warning("🔐 Please enter the correct password to access the app.")
            st.stop()

        # --- Main App UI ---
        st.title("💰 Personal Finance Tracker")
        st.caption("Track your income 💵 and expenses 💸 easily!")

        self.add_transaction_ui()
        self.display_summary()
        self.display_charts()
        self.budget_checker()
        self.export_csv()

    def add_transaction_ui(self):
        st.header("➕ Add a New Transaction")
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("💲 Amount", min_value=0.01, format="%.2f")
            category = st.text_input("📂 Category")
        with col2:
            t_type = st.selectbox("🔁 Type", ["Income", "Expense"])
            date = st.date_input("📅 Date", value=datetime.today())
        description = st.text_input("📝 Description (optional)")

        if st.button("✅ Add Transaction"):
            tx = Transaction(amount, category, t_type, date.strftime("%Y-%m-%d"), description)
            self.tracker.add_transaction(tx)
            st.success("🎉 Transaction added successfully!")

    def display_summary(self):
        st.header("📊 Summary")
        income, expense, balance = self.tracker.get_summary()
        col1, col2, col3 = st.columns(3)
        col1.metric("💚 Total Income", f"${income:.2f}")
        col2.metric("❤️ Total Expenses", f"${expense:.2f}")
        col3.metric("🟡 Balance", f"${balance:.2f}")

        st.subheader("🧾 Transaction History")
        df = self.tracker.get_dataframe()
        if not df.empty:
            st.dataframe(df.sort_values("Date", ascending=False))
        else:
            st.info("🔎 No transactions added yet.")

    def display_charts(self):
        st.header("📈 Visual Insights")
        df = self.tracker.get_dataframe()
        if df.empty:
            st.info("📭 Add transactions to generate insights.")
            return

        expense_by_cat = self.tracker.get_expense_by_category()
        if not expense_by_cat.empty:
            fig, ax = plt.subplots()
            expense_by_cat.plot(kind='pie', autopct='%1.1f%%', ax=ax, ylabel="")
            ax.set_title("🧩 Expenses by Category")
            st.pyplot(fig)

    def budget_checker(self):
        st.header("🎯 Monthly Budget Monitor")
        budget = st.number_input("📌 Set Your Monthly Budget", min_value=0.0, value=1000.0, format="%.2f")

        df = self.tracker.get_dataframe()
        if df.empty:
            return

        df['Date'] = pd.to_datetime(df['Date'])
        this_month = df[df['Date'].dt.month == datetime.today().month]
        monthly_expense = this_month[this_month['Type'] == "Expense"]['Amount'].sum()

        if monthly_expense > budget:
            st.error(f"🚨 Budget Exceeded! You've spent ${monthly_expense:.2f} out of ${budget:.2f}")
        else:
            st.success(f"✅ Good! You've spent ${monthly_expense:.2f} out of ${budget:.2f}")

    def export_csv(self):
        st.header("📁 Export Data to CSV")
        df = self.tracker.get_dataframe()
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name="finance_data.csv",
                mime='text/csv',
            )
        else:
            st.info("🛑 No data available to export.")

# --- Run App ---
if __name__ == "__main__":
    app = FinanceApp()
    app.run()
