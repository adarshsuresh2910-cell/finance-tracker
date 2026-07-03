import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ledgerly", layout="wide")

st.title("💰 Ledgerly - Personal Finance Tracker")

if "transactions" not in st.session_state:
    st.session_state.transactions = []

st.sidebar.header("Add Transaction")
# ---------------- Budget Settings ----------------
st.sidebar.markdown("---")
st.sidebar.header("💰 Monthly Budgets")

categories = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Education",
    "Healthcare",
    "Other"
]

if "budgets" not in st.session_state:
    st.session_state.budgets = {cat: 0 for cat in categories}

for cat in categories:
    st.session_state.budgets[cat] = st.sidebar.number_input(
        f"{cat} Budget (₹)",
        min_value=0,
        value=st.session_state.budgets[cat],
        step=500,
        key=f"budget_{cat}"
    )

amount = st.sidebar.number_input(
    "Amount (₹)",
    min_value=0.0,
    step=1.0
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Education",
        "Healthcare",
        "Other"
    ]
)

transaction_type = st.sidebar.radio(
    "Type",
    ["Income", "Expense"]
)

if st.sidebar.button("Add Transaction"):
    st.session_state.transactions.append({
        "Type": transaction_type,
        "Category": category,
        "Amount": amount
    })

df = pd.DataFrame(st.session_state.transactions)

if not df.empty:

    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    savings = total_income - total_expense

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Income", f"₹{total_income:,.0f}")
    col2.metric("Total Expense", f"₹{total_expense:,.0f}")
    col3.metric("Savings", f"₹{savings:,.0f}")

    st.subheader("Transaction History")
    st.dataframe(df, use_container_width=True)

    st.subheader("Category Wise Spending")
# ---------------- Budget Tracker ----------------
st.subheader("📊 Budget Tracker")

if not expense_df.empty:

    budget_df = expense_df.groupby("Category")["Amount"].sum().reset_index()

    for cat in categories:

        spent = budget_df.loc[
            budget_df["Category"] == cat,
            "Amount"
        ].sum()

        budget = st.session_state.budgets.get(cat, 0)

        if budget > 0:

            percent = min(spent / budget, 1.0)

            st.write(f"### {cat}")

            col1, col2 = st.columns([4,1])

            with col1:
                st.progress(percent)

            with col2:
                st.write(f"₹{spent:.0f} / ₹{budget:.0f}")

            if spent > budget:
                st.error(
                    f"⚠️ Budget exceeded by ₹{spent-budget:.0f}"
                )
            elif spent > budget * 0.8:
                st.warning(
                    "⚠️ You have used more than 80% of your budget."
                )
            else:
                st.success(
                    "✅ Budget is under control."
                )

    expense_df = df[df["Type"] == "Expense"]

    if not expense_df.empty:
        category_summary = (
            expense_df.groupby("Category")["Amount"]
            .sum()
            .reset_index()
        )

        st.bar_chart(
            category_summary.set_index("Category")
        )

    st.subheader("Spending Insights")

    if total_expense > total_income:
        st.error("⚠️ You are spending more than you earn.")
    elif savings > 0:
        st.success("✅ Great! You are saving money.")

    if not expense_df.empty:
        top_category = (
            expense_df.groupby("Category")["Amount"]
            .sum()
            .idxmax()
        )

        st.info(
            f"📌 Highest spending category: {top_category}"
        )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Report",
        csv,
        "ledgerly_report.csv",
        "text/csv"
    )

else:
    st.info("Add transactions from the sidebar to begin.")