import streamlit as st
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.calculators.retirement_calculator import (
    calculate_retirement_timeline,
    calculate_savings_longevity,
    calculate_required_monthly_savings
)

# Page configuration
st.set_page_config(
    page_title="AI Financial Planning Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for user inputs
with st.sidebar:
    st.header("👤 Your Profile")
    current_age = st.slider("Current Age", 18, 80, 30)
    retirement_age = st.slider("Target Retirement Age", 50, 80, 65)
    monthly_income = st.number_input("Monthly Income ($)", min_value=0, value=5000)
    current_savings = st.number_input("Current Savings ($)", min_value=0, value=10000)
    monthly_savings = st.number_input("Monthly Savings ($)", min_value=0, value=500)
    expected_return = st.slider("Expected Annual Return (%)", 0.0, 15.0, 6.0)
    risk_tolerance = st.select_slider(
        "Risk Tolerance", 
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate"
    )

# Main interface layout
st.title('🏦 AI Financial Planning Advisor')

# Display calculation results
retirement_timeline = calculate_retirement_timeline(
    current_age=current_age,
    retirement_age=retirement_age,
    monthly_savings=monthly_savings,
    expected_return=expected_return,
    current_savings=current_savings
)

st.subheader("📊 Retirement Summary")

st.metric("Total Retirement Fund", f"${retirement_timeline['total_fund']:,.0f}")
st.metric(
    "Inflation-Adjusted Value", 
    f"${retirement_timeline['real_purchasing_power']:,.0f}",
    f"Over {retirement_timeline['years_to_retirement']} years"
)
