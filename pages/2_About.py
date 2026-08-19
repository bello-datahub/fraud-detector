import streamlit as st

st.set_page_config(
    page_title="About — SIDONPAY Fraud Detector",
    page_icon="🟢",
    layout="centered"
)

st.title("📘 About This Project")

st.subheader("Overview")

st.write(
    "An ML-based fraud detection system trained on the PaySim mobile money "
    "transaction dataset, built for SIDONPAY's Data Analyst internship task."
)

st.subheader("Features Used")

st.markdown("""
- Transaction details *(amount, type)*
- Sender balance behavior *(before/after the transaction)*
- Recipient balance behavior *(before/after the transaction)*
- Engineered risk signals *(e.g. recipient balance unchanged, high-risk hour, account emptied out)*
""")

st.subheader("Tools")

st.write(
    "Python | Streamlit | Scikit-learn (Random Forest)"
)
