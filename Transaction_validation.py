import streamlit as st
import pandas as pd
import joblib


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Transaction Validation — SIDONPAY Fraud Detector",
    page_icon="💳",
    layout="centered"
)


# ============================================================
# LOAD SAVED MODEL, FEATURE LIST, AND TUNED THRESHOLD
# ============================================================

model = joblib.load("fraud_model.pkl")
feature_cols = joblib.load("feature_cols.pkl")
best_threshold = joblib.load("best_threshold.pkl")


# ============================================================
# PAGE HEADER
# ============================================================

st.title("💳 Transaction Validation")

st.caption(
    "Random Forest model trained on PaySim transaction data — SIDONPAY"
)

st.divider()


# ============================================================
# EXPLAIN WHAT THE MODEL LOOKS AT
# ============================================================

with st.expander("ℹ️ What we look at, and why (click to learn more)"):
    st.markdown("""
    Our model was trained on millions of past transactions and learned which patterns are
    most associated with fraud. Here's what it weighs most heavily, from strongest to weakest:

    - **🔴 Very High impact — Sender's balance before the transaction.**
      Accounts that actually have money in them are far more attractive fraud targets than
      empty ones. This alone is our single strongest signal.

    - **🟠 High impact — Transaction amount.**
      Larger transactions carry more risk simply because there's more to lose.

    - **🟠 High impact — Whether the sender's account was completely emptied out.**
      Fraud typically drains an account to exactly zero, rather than taking a partial amount.

    - **🟠 High impact — Whether the recipient's balance stayed the same despite the transfer.**
      When money is supposedly sent but the receiving account's balance never moves, that's
      one of the clearest fraud fingerprints we found — about 7 in 10 transactions with this
      exact pattern turned out to be fraud.

    - **🟡 Medium impact — Recipient's balance after, balance mismatches, transaction type.**
      Transfers carry a higher fraud rate than cash-outs, and any gap between what should
      have arrived and what actually did adds risk.

    - **🟢 Lower impact — Sender's balance after, and time of day.**
      Still useful, but mostly reinforces what the stronger signals above already show.
    """)


st.divider()


# ============================================================
# TRANSACTION DETAILS
# ============================================================

st.subheader("Transaction Details")

col1, col2 = st.columns(2)


with col1:

    txn_type = st.selectbox(
        "Transaction Type",
        ["CASH_OUT", "TRANSFER"]
    )

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=10000.0,
        step=100.0
    )

    hour_of_day = st.slider(
        "Hour of Day (0-23)",
        0,
        23,
        12
    )


with col2:

    old_balance_orig = st.number_input(
        "Sender's Balance Before",
        min_value=0.0,
        value=50000.0,
        step=100.0
    )

    new_balance_orig = st.number_input(
        "Sender's Balance After",
        min_value=0.0,
        value=40000.0,
        step=100.0
    )


# ============================================================
# RECIPIENT DETAILS
# ============================================================

st.subheader("Recipient Details")

col3, col4 = st.columns(2)


with col3:

    old_balance_dest = st.number_input(
        "Recipient's Balance Before",
        min_value=0.0,
        value=0.0,
        step=100.0
    )


with col4:

    new_balance_dest = st.number_input(
        "Recipient's Balance After",
        min_value=0.0,
        value=0.0,
        step=100.0
    )


st.divider()


# ============================================================
# VALIDATE TRANSACTION
# ============================================================

if st.button(
    "Validate Transaction",
    type="primary",
    use_container_width=True
):

    # ========================================================
    # FEATURE ENGINEERING
    # Mirrors the notebook exactly
    # ========================================================

    error_balance_dest = (
        old_balance_dest + amount - new_balance_dest
    )

    dest_balance_unchanged = int(
        (old_balance_dest == new_balance_dest)
        and (amount > 0)
    )

    is_high_risk_hour = int(
        3 <= hour_of_day <= 6
    )

    orig_emptied_out = int(
        (old_balance_orig > 0)
        and (new_balance_orig == 0)
    )

    type_transfer = int(
        txn_type == "TRANSFER"
    )


    # ========================================================
    # PREPARE MODEL INPUT
    # ========================================================

    input_row = pd.DataFrame([{
        "amount": amount,
        "oldbalanceOrg": old_balance_orig,
        "newbalanceOrig": new_balance_orig,
        "oldbalanceDest": old_balance_dest,
        "newbalanceDest": new_balance_dest,
        "errorBalanceDest": error_balance_dest,
        "destBalanceUnchanged": dest_balance_unchanged,
        "isHighRiskHour": is_high_risk_hour,
        "origEmptiedOut": orig_emptied_out,
        "type_TRANSFER": type_transfer,
    }])[feature_cols]


    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    fraud_proba = model.predict_proba(input_row)[0][1]

    is_fraud = fraud_proba >= best_threshold


    # ========================================================
    # RESULT
    # ========================================================

    st.divider()

    st.subheader("Validation Result")


    # ========================================================
    # FRAUD RISK SCORE
    # ========================================================

    st.metric(
        "Fraud Risk Score",
        f"{fraud_proba:.1%}"
    )

    st.write(
        f"This score is "
        f"{'above' if is_fraud else 'below'} "
        f"our {best_threshold:.1%} review threshold."
    )


    # ========================================================
    # NON-TECHNICAL VERDICT
    # ========================================================

    if is_fraud:

        st.error(
            "🔴 **High Risk — this transaction looks like fraud**"
        )

        st.write(
            "Several patterns here match what we typically see in fraudulent "
            "transactions. We'd recommend holding this one for review before "
            "it goes through."
        )

    else:

        st.success(
            "🟢 **Low Risk — this transaction looks normal**"
        )

        st.write(
            "This transaction doesn't show the warning signs we typically "
            "associate with fraud."
        )


    # ========================================================
    # CONTRIBUTING FACTORS
    # ========================================================

    st.write(
        "**What we noticed about this specific transaction:**"
    )

    factors = []


    if orig_emptied_out:

        factors.append(
            (
                "⚠️",
                "The sender's account was drained to exactly zero — "
                "a common fraud pattern."
            )
        )


    if dest_balance_unchanged:

        factors.append(
            (
                "⚠️",
                "The recipient's balance didn't change at all, despite "
                "money supposedly arriving — a strong fraud signal."
            )
        )


    if is_high_risk_hour:

        factors.append(
            (
                "⚠️",
                "This happened during the overnight window (roughly "
                "3am-6am), when fraud rates run much higher."
            )
        )


    if type_transfer:

        factors.append(
            (
                "ℹ️",
                "This is a transfer, which historically carries a higher "
                "fraud rate than a cash-out."
            )
        )


    if amount > 200000:

        factors.append(
            (
                "ℹ️",
                "This is a large transaction amount, which adds risk "
                "simply due to the size of potential loss."
            )
        )


    if not factors:

        factors.append(
            (
                "✅",
                "None of our known high-risk patterns were present "
                "in this transaction."
            )
        )


    for icon, text in factors:

        st.write(
            f"{icon} {text}"
        )


    # ========================================================
    # ENGINEERED FEATURE BREAKDOWN
    # ========================================================

    breakdown = input_row.T.rename(
        columns={0: "Value"}
    )

    breakdown.index.name = "Factor"


    breakdown["Detected Risk Pattern"] = [
        "—",
        "—",
        "—",
        "—",
        "—",
        f"{error_balance_dest:,.2f}",
        "Yes" if dest_balance_unchanged else "No",
        "Yes" if is_high_risk_hour else "No",
        "Yes" if orig_emptied_out else "No",
        "Yes" if type_transfer else "No",
    ]


    breakdown["Overall Result"] = (
        "High Risk" if is_fraud else "Low Risk"
    )


    breakdown["Fraud Score"] = (
        f"{fraud_proba:.1%}"
    )


    # ========================================================
    # INTERACTIVE ENGINEERED FEATURES TABLE
    # ========================================================

    with st.expander(
        "🔎 See engineered features used in this validation"
    ):

        st.dataframe(
            breakdown,
            use_container_width=True,
            hide_index=False
        )