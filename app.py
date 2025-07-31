"""
Valura Financial Planning Agent - Standalone Streamlit App
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import math

# Page configuration
st.set_page_config(
    page_title="Valura AI Financial Planning Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Financial calculation functions
def future_value(pv, rate, periods):
    """FV = PV × (1 + r)^n"""
    return pv * (1 + rate) ** periods

def fv_annuity(pmt, rate, periods):
    """FV = PMT × [(1 + r)^n – 1] / r"""
    if rate == 0:
        return pmt * periods
    return pmt * ((1 + rate) ** periods - 1) / rate

def calculate_retirement_timeline(
    current_age, retirement_age, monthly_savings, expected_return, current_savings=0
):
    """Calculate comprehensive retirement projections"""
    years_to_retirement = retirement_age - current_age
    annual_return = expected_return / 100
    monthly_return = annual_return / 12
    months_to_retirement = years_to_retirement * 12
    
    # Future value of current savings
    fv_current = future_value(current_savings, annual_return, years_to_retirement)
    
    # Future value of monthly contributions
    fv_monthly = fv_annuity(monthly_savings, monthly_return, months_to_retirement)
    
    total_retirement_fund = fv_current + fv_monthly
    
    # Adjust for inflation (assuming 3%)
    inflation_rate = 0.03
    real_purchasing_power = total_retirement_fund / ((1 + inflation_rate) ** years_to_retirement)
    
    return {
        "total_fund": total_retirement_fund,
        "real_purchasing_power": real_purchasing_power,
        "years_to_retirement": years_to_retirement,
        "monthly_contributions": monthly_savings,
        "projected_annual_return": expected_return,
        "fv_current_savings": fv_current,
        "fv_monthly_contributions": fv_monthly
    }

def calculate_savings_longevity(retirement_fund, monthly_withdrawal, expected_return):
    """Calculate how long retirement savings will last"""
    annual_return = expected_return / 100
    monthly_return = annual_return / 12
    
    if monthly_return == 0:
        months_lasting = retirement_fund / monthly_withdrawal
    else:
        pv_ratio = (retirement_fund * monthly_return) / monthly_withdrawal
        if pv_ratio >= 1:
            months_lasting = float('inf')
        else:
            months_lasting = -math.log(1 - pv_ratio) / math.log(1 + monthly_return)
    
    years_lasting = months_lasting / 12 if months_lasting != float('inf') else float('inf')
    
    return {
        "months_lasting": months_lasting,
        "years_lasting": years_lasting,
        "sustainable": months_lasting == float('inf')
    }

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stSelectbox > div > div > select {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🏦 Valura AI Financial Planning Advisor</h1>', unsafe_allow_html=True)

# Sidebar for user inputs
with st.sidebar:
    st.header("👤 Your Financial Profile")
    
    # Personal Information
    st.subheader("Personal Details")
    current_age = st.slider("Current Age", 18, 80, 30)
    retirement_age = st.slider("Target Retirement Age", 50, 80, 65)
    
    # Financial Information
    st.subheader("Financial Details")
    monthly_income = st.number_input("Monthly Income ($)", min_value=0, value=5000, step=100)
    current_savings = st.number_input("Current Savings ($)", min_value=0, value=10000, step=1000)
    monthly_savings = st.number_input("Monthly Savings ($)", min_value=0, value=500, step=50)
    
    # Investment Preferences
    st.subheader("Investment Preferences")
    expected_return = st.slider("Expected Annual Return (%)", 0.0, 15.0, 7.0, 0.5)
    risk_tolerance = st.select_slider(
        "Risk Tolerance", 
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate"
    )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Retirement Projection Analysis")
    
    # Calculate retirement projections
    retirement_data = calculate_retirement_timeline(
        current_age=current_age,
        retirement_age=retirement_age,
        monthly_savings=monthly_savings,
        expected_return=expected_return,
        current_savings=current_savings
    )
    
    # Display key metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric(
            "Total Retirement Fund",
            f"${retirement_data['total_fund']:,.0f}",
            f"In {retirement_data['years_to_retirement']} years"
        )
    
    with metrics_col2:
        st.metric(
            "Real Purchasing Power",
            f"${retirement_data['real_purchasing_power']:,.0f}",
            "Inflation Adjusted"
        )
    
    with metrics_col3:
        monthly_rate = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0
        st.metric(
            "Savings Rate",
            f"{monthly_rate:.1f}%",
            "Of Monthly Income"
        )
    
    # Retirement timeline chart
    years = list(range(current_age, retirement_age + 1))
    fund_values = []
    
    for year in years:
        years_elapsed = year - current_age
        if years_elapsed == 0:
            fund_values.append(current_savings)
        else:
            annual_return = expected_return / 100
            monthly_return = annual_return / 12
            months_elapsed = years_elapsed * 12
            
            fv_current = future_value(current_savings, annual_return, years_elapsed)
            fv_monthly = fv_annuity(monthly_savings, monthly_return, months_elapsed)
            fund_values.append(fv_current + fv_monthly)
    
    # Create DataFrame for plotting
    chart_data = pd.DataFrame({
        'Age': years,
        'Fund Value': fund_values
    })
    
    # Plotly chart
    fig = px.line(
        chart_data, 
        x='Age', 
        y='Fund Value',
        title='Retirement Fund Growth Over Time',
        labels={'Fund Value': 'Fund Value ($)'}
    )
    fig.update_layout(
        xaxis_title="Age",
        yaxis_title="Fund Value ($)",
        yaxis_tickformat='$,.0f'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💡 Financial Insights")
    
    # Breakdown of contributions
    st.write("**Fund Composition at Retirement:**")
    
    breakdown_data = {
        'Source': ['Current Savings Growth', 'Monthly Contributions'],
        'Amount': [
            retirement_data['fv_current_savings'],
            retirement_data['fv_monthly_contributions']
        ]
    }
    
    breakdown_df = pd.DataFrame(breakdown_data)
    fig_pie = px.pie(
        breakdown_df,
        values='Amount',
        names='Source',
        title='Retirement Fund Sources'
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Additional insights
    st.write("**Key Insights:**")
    
    # Rule of 72 calculation
    if expected_return > 0:
        doubling_time = 72 / expected_return
        st.write(f"💫 Your money doubles every ~{doubling_time:.1f} years")
    
    # Savings recommendations
    if monthly_rate < 10:
        st.warning("💡 Consider increasing savings rate to at least 10-15%")
    elif monthly_rate >= 20:
        st.success("🎉 Excellent savings rate! You're on track!")
    else:
        st.info("👍 Good savings rate! Consider gradual increases")
    
    # Retirement lifestyle estimate
    monthly_retirement_income = (retirement_data['total_fund'] * 0.04) / 12  # 4% rule
    st.write(f"**Estimated Monthly Retirement Income:**")
    st.write(f"${monthly_retirement_income:,.0f} (using 4% withdrawal rule)")

# Additional tools section
st.subheader("🔧 Additional Planning Tools")

tool_col1, tool_col2 = st.columns(2)

with tool_col1:
    st.write("**Retirement Withdrawal Calculator**")
    withdrawal_fund = st.number_input("Retirement Fund ($)", min_value=0, value=500000, key="withdrawal_fund")
    monthly_withdrawal = st.number_input("Monthly Withdrawal ($)", min_value=0, value=3000, key="monthly_withdrawal")
    withdrawal_return = st.number_input("Expected Return in Retirement (%)", min_value=0.0, value=4.0, key="withdrawal_return")
    
    if st.button("Calculate Longevity"):
        longevity_data = calculate_savings_longevity(withdrawal_fund, monthly_withdrawal, withdrawal_return)
        if longevity_data['sustainable']:
            st.success("🎉 Your withdrawals are sustainable indefinitely!")
        else:
            st.write(f"💰 Your savings will last approximately **{longevity_data['years_lasting']:.1f} years**")

with tool_col2:
    st.write("**What-If Scenarios**")
    scenario = st.selectbox(
        "Select Scenario",
        ["Increase Savings by 10%", "Increase Return by 1%", "Retire 2 Years Earlier", "Retire 2 Years Later"]
    )
    
    if st.button("Run Scenario"):
        if scenario == "Increase Savings by 10%":
            scenario_data = calculate_retirement_timeline(
                current_age, retirement_age, monthly_savings * 1.1, expected_return, current_savings
            )
            difference = scenario_data['total_fund'] - retirement_data['total_fund']
            st.success(f"📈 Additional fund: ${difference:,.0f}")
            
        elif scenario == "Increase Return by 1%":
            scenario_data = calculate_retirement_timeline(
                current_age, retirement_age, monthly_savings, expected_return + 1, current_savings
            )
            difference = scenario_data['total_fund'] - retirement_data['total_fund']
            st.success(f"📈 Additional fund: ${difference:,.0f}")
            
        elif scenario == "Retire 2 Years Earlier":
            scenario_data = calculate_retirement_timeline(
                current_age, retirement_age - 2, monthly_savings, expected_return, current_savings
            )
            difference = retirement_data['total_fund'] - scenario_data['total_fund']
            st.warning(f"📉 Reduced fund: ${difference:,.0f}")
            
        elif scenario == "Retire 2 Years Later":
            scenario_data = calculate_retirement_timeline(
                current_age, retirement_age + 2, monthly_savings, expected_return, current_savings
            )
            difference = scenario_data['total_fund'] - retirement_data['total_fund']
            st.success(f"📈 Additional fund: ${difference:,.0f}")

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This tool provides estimates for educational purposes only. Consult with a qualified financial advisor for personalized advice.")
st.markdown("*Powered by Valura.ai* 🚀")
