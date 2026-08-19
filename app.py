import streamlit as st

st.set_page_config(page_title="SIDONPAY Fraud Detector", page_icon="🟢", layout="centered")

def home():
    st.title("🟢 SIDONPAY Fraud Detection System")
    st.subheader("Welcome 👋")
    st.write(
        "This tool predicts whether a mobile money transaction is likely fraudulent, "
        "based on transaction details and account balance behavior."
    )
    st.write("👉 Go to **Transaction Validation** in the sidebar to assess a transaction.")

# Define each page's exact label, icon, and file location — independent of filenames
home_page = st.Page(home, title="App", icon="🟢", default=True)
validation_page = st.Page("pages/1_Transaction_Validation.py", title="Transaction Validation", icon="💳")
about_page = st.Page("pages/2_About.py", title="About", icon="📘")

# The ORDER in this list is the order shown in the sidebar
pg = st.navigation([home_page, validation_page, about_page])
pg.run()
