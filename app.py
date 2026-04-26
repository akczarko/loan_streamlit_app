# -*- coding: utf-8 -*-
import streamlit as st
import pickle
import pandas as pd

# -------------------------
# Load Model
# -------------------------
with open("app_model.pkl", "rb") as file:
    model = pickle.load(file)

# -------------------------
# Title
# -------------------------
st.markdown(
    "<h1 style='text-align: center; background-color: #d6eaff; padding: 10px; color: #003366;'><b>Loan Approval & Lender Optimization</b></h1>",
    unsafe_allow_html=True
)

st.header("Enter Applicant Information")

# -------------------------
# Numeric Inputs
# -------------------------
Requested_Loan_Amount = st.number_input("Requested Loan Amount", value=10000)
FICO_score = st.number_input("FICO Score", value=700)
Monthly_Gross_Income = st.number_input("Monthly Gross Income", value=5000)
Monthly_Housing_Payment = st.number_input("Monthly Housing Payment", value=1500)

# -------------------------
# Bankruptcy
# -------------------------
bankrupt = st.selectbox(
    "Have you ever filed bankruptcy or foreclosure?",
    ["No", "Yes"]
)
Ever_Bankrupt_or_Foreclose = 1 if bankrupt == "Yes" else 0

# -------------------------
# Loan Reason
# -------------------------
reason = st.selectbox(
    "Loan Reason",
    [
        "credit_card_refinancing",
        "debt_consolidation",   # ✅ FIXED spelling
        "home_improvement",
        "major_purchase",
        "other"
    ]
)

Reason_credit_card_refinancing = 1 if reason == "credit_card_refinancing" else 0
Reason_debt_consolidation = 1 if reason == "debt_consolidation" else 0
Reason_home_improvement = 1 if reason == "home_improvement" else 0
Reason_major_purchase = 1 if reason == "major_purchase" else 0
Reason_other = 1 if reason == "other" else 0

# -------------------------
# Employment Status
# -------------------------
employment_status = st.selectbox(
    "Employment Status",
    ["full_time", "part_time", "unemployed"]
)

Employment_Status_part_time = 1 if employment_status == "part_time" else 0
Employment_Status_unemployed = 1 if employment_status == "unemployed" else 0

# -------------------------
# Employment Sector
# -------------------------
sector = st.selectbox(
    "Employment Sector",
    [
        "communication_services",
        "consumer_discretionary",
        "consumer_staples",
        "energy",
        "financials",
        "health_care",
        "industrials",
        "information_technology",
        "materials",
        "real_estate",
        "utilities"
    ]
)

Employment_Sector_communication_services = 1 if sector == "communication_services" else 0
Employment_Sector_consumer_discretionary = 1 if sector == "consumer_discretionary" else 0
Employment_Sector_consumer_staples = 1 if sector == "consumer_staples" else 0
Employment_Sector_energy = 1 if sector == "energy" else 0
Employment_Sector_financials = 1 if sector == "financials" else 0
Employment_Sector_health_care = 1 if sector == "health_care" else 0
Employment_Sector_industrials = 1 if sector == "industrials" else 0
Employment_Sector_information_technology = 1 if sector == "information_technology" else 0
Employment_Sector_materials = 1 if sector == "materials" else 0
Employment_Sector_real_estate = 1 if sector == "real_estate" else 0
Employment_Sector_utilities = 1 if sector == "utilities" else 0

# -------------------------
# Evaluate Button
# -------------------------
if st.button("Evaluate Loan"):

    # Base input (no lender yet)
    base_input = {
        "Requested_Loan_Amount": Requested_Loan_Amount,
        "FICO_score": FICO_score,
        "Monthly_Gross_Income": Monthly_Gross_Income,
        "Monthly_Housing_Payment": Monthly_Housing_Payment,
        "Ever_Bankrupt_or_Foreclose": Ever_Bankrupt_or_Foreclose,

        "Reason_credit_card_refinancing": Reason_credit_card_refinancing,
        "Reason_debt_consolidation": Reason_debt_consolidation,
        "Reason_home_improvement": Reason_home_improvement,
        "Reason_major_purchase": Reason_major_purchase,
        "Reason_other": Reason_other,

        "Employment_Status_part_time": Employment_Status_part_time,
        "Employment_Status_unemployed": Employment_Status_unemployed,

        "Employment_Sector_communication_services": Employment_Sector_communication_services,
        "Employment_Sector_consumer_discretionary": Employment_Sector_consumer_discretionary,
        "Employment_Sector_consumer_staples": Employment_Sector_consumer_staples,
        "Employment_Sector_energy": Employment_Sector_energy,
        "Employment_Sector_financials": Employment_Sector_financials,
        "Employment_Sector_health_care": Employment_Sector_health_care,
        "Employment_Sector_industrials": Employment_Sector_industrials,
        "Employment_Sector_information_technology": Employment_Sector_information_technology,
        "Employment_Sector_materials": Employment_Sector_materials,
        "Employment_Sector_real_estate": Employment_Sector_real_estate,
        "Employment_Sector_utilities": Employment_Sector_utilities,
    }

    # Lender scenarios + payouts
    lenders = {
        "A": {"Lender_B": 0, "Lender_C": 0, "payout": 250},
        "B": {"Lender_B": 1, "Lender_C": 0, "payout": 350},
        "C": {"Lender_B": 0, "Lender_C": 1, "payout": 150}
    }

    results = []

    for lender_name, lender_values in lenders.items():

        input_data = base_input.copy()
        input_data["Lender_B"] = lender_values["Lender_B"]
        input_data["Lender_C"] = lender_values["Lender_C"]

        df = pd.DataFrame([input_data])

        # 🔥 CRITICAL FIX (prevents your error)
        df = df.reindex(columns=model.feature_names_in_, fill_value=0)

        prob = model.predict_proba(df)[0][1]
        prediction = model.predict(df)[0]

        payout = lender_values["payout"]
        expected_revenue = prob * payout

        results.append({
            "Lender": lender_name,
            "Approval_Probability": prob,
            "Prediction": "Approved" if prediction == 1 else "Denied",
            "Payout": payout,
            "Expected_Revenue": expected_revenue
        })

    results_df = pd.DataFrame(results)

    best_option = results_df.loc[results_df["Expected_Revenue"].idxmax()]

    # -------------------------
    # Display
    # -------------------------
    st.subheader("Results by Lender")
    st.dataframe(results_df)

    st.subheader("Recommended Lender")

    st.success(
        f"Best Lender: {best_option['Lender']} \n\n"
        f"Approval Probability: {best_option['Approval_Probability']:.2f} \n\n"
        f"Expected Revenue: ${best_option['Expected_Revenue']:.2f}"
    )

    st.info("Recommendation is based on maximizing expected revenue (probability × lender payout).")