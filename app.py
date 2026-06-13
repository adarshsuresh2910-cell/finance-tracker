import streamlit as st

st.title("Personal Finance Tracker")

income = st.number_input("Enter Income (₹)", min_value=0)

expense = st.number_input("Enter Expense (₹)", min_value=0)

if st.button("Calculate Savings"):
    savings = income - expense
    st.success(f"Your Savings: ₹{savings}")