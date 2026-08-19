import streamlit as st

st.set_page_config(
    page_title="Transaction Validation — SIDONPAY Fraud Detector",
    page_icon="🟢",
    layout="centered"
)

st.title("🟢 SIDONPAY Fraud Detection System")
st.subheader("Welcome 👋")

st.write(
    "This tool predicts whether a mobile money transaction is likely fraudulent, "
    "based on transaction details and account balance behavior."
)

st.write("👉 Go to **Transaction Validation** in the sidebar to assess a transaction.")
