import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Ledgerly", layout="wide", page_icon="💰")

st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        border: 1px solid #2e2e3e;
    }
    .stDataFrame { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Ledgerly — Personal Finance Tracker")

if "transactions" not in st.session_state:
    st.session_state.transactions = []

# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.header("Add Transaction")

amount = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=1.0, format="%.2f")

description = st.sidebar.text_input("Description", placeholder="e.g. Swiggy order")

category = st.sidebar.selectbox(
    "Category",
    [
        "Food & Dining",
        "Housing / Rent",
        "Transport",
        "Shopping",
        "Bills & Utilities",
        "Entertainment",
        "Education",
        "Healthcare",
        "Savings / Investment",
        "Salary",
        "Freelance / Business",
        "Other",
    ],
)

transaction_type = st.sidebar.radio("Type", ["Income", "Expense"])

txn_date = st.sidebar.date_input("Date", value=date.today())

if st.sidebar.button("➕ Add Transaction", use_container_width=True):
    if amount <= 0:
        st.sidebar.error("Amount must be greater than 0.")
    else:
        st.session_state.transactions.append(
            {
                "Date": str(txn_date),
                "Description": description or category,
                "Category": category,
                "Type": transaction_type,
                "Amount": amount,
            }
        )
        st.sidebar.success("Transaction added!")

# ── Main area ────────────────────────────────────────────────────────────────

df = pd.DataFrame(st.session_state.transactions)

if df.empty:
    st.info("Add transactions from the sidebar to begin.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date", ascending=False).reset_index(drop=True)

# Month filter
months = ["All"] + sorted(
    df["Date"].dt.to_period("M").astype(str).unique().tolist(), reverse=True
)
selected_month = st.selectbox("Filter by month", months, label_visibility="collapsed")

if selected_month != "All":
    view_df = df[df["Date"].dt.to_period("M").astype(str) == selected_month]
else:
    view_df = df

# ── Summary metrics ───────────────────────────────────────────────────────────

total_income  = view_df[view_df["Type"] == "Income"]["Amount"].sum()
total_expense = view_df[view_df["Type"] == "Expense"]["Amount"].sum()
savings       = total_income - total_expense
savings_rate  = (savings / total_income * 100) if total_income > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income",   f"₹{total_income:,.0f}")
col2.metric("Total Expenses", f"₹{total_expense:,.0f}")
col3.metric("Net Balance",    f"₹{savings:,.0f}", delta=f"{'+'if savings>=0 else ''}{savings:,.0f}")
col4.metric("Savings Rate",   f"{savings_rate:.1f}%")

st.divider()

# ── Insights banner ───────────────────────────────────────────────────────────

if total_expense > total_income:
    st.error("⚠️ You're spending more than you earn this period.")
elif savings > 0:
    st.success(f"✅ Great! You're saving ₹{savings:,.0f} ({savings_rate:.1f}%) this period.")

# ── Charts ────────────────────────────────────────────────────────────────────

expense_df = view_df[view_df["Type"] == "Expense"]

chart_col, list_col = st.columns([1, 1], gap="large")

with chart_col:
    st.subheader("Spending by Category")
    if expense_df.empty:
        st.info("No expenses to show.")
    else:
        cat_summary = (
            expense_df.groupby("Category")["Amount"]
            .sum()
            .reset_index()
            .sort_values("Amount", ascending=True)
        )
        fig = px.bar(
            cat_summary,
            x="Amount",
            y="Category",
            orientation="h",
            text_auto=",.0f",
            color="Amount",
            color_continuous_scale="Reds",
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="",
            yaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)

        top_cat = cat_summary.sort_values("Amount", ascending=False).iloc[0]
        st.info(f"📌 Highest spend: **{top_cat['Category']}** — ₹{top_cat['Amount']:,.0f}")

with list_col:
    st.subheader("Transaction History")

    # Delete widget
    if not view_df.empty:
        del_idx = st.selectbox(
            "Select row to delete (by #)",
            options=["—"] + list(range(len(view_df))),
            format_func=lambda i: "—" if i == "—" else
                f"#{i}  {view_df.iloc[i]['Description']}  ₹{view_df.iloc[i]['Amount']:,.0f}"
        )
        if st.button("🗑️ Delete selected", disabled=(del_idx == "—")):
            # Map back to original df index
            original_idx = view_df.iloc[del_idx].name
            st.session_state.transactions.pop(original_idx)
            st.rerun()

    display_df = view_df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%d %b %Y")
    display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹{x:,.2f}")
    st.dataframe(
        display_df[["Date", "Description", "Category", "Type", "Amount"]],
        use_container_width=True,
        hide_index=True,
    )

# ── Income vs Expense trend ───────────────────────────────────────────────────

st.divider()
st.subheader("Income vs Expense Over Time")

trend_df = (
    view_df.groupby([view_df["Date"].dt.to_period("M").astype(str), "Type"])["Amount"]
    .sum()
    .reset_index()
)
trend_df.columns = ["Month", "Type", "Amount"]

if len(trend_df["Month"].unique()) > 1:
    fig2 = px.bar(
        trend_df,
        x="Month",
        y="Amount",
        color="Type",
        barmode="group",
        color_discrete_map={"Income": "#22c55e", "Expense": "#ef4444"},
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title="",
        yaxis_title="",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Add transactions across multiple months to see the trend.")

# ── Export ────────────────────────────────────────────────────────────────────

st.divider()
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download Full Report (CSV)",
    csv,
    "ledgerly_report.csv",
    "text/csv",
)