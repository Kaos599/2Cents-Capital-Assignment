"""
Step-by-step financial calculation explanations
"""

from typing import Dict, Any
import math
from .financial_formulas import future_value, fv_annuity, pv_annuity
from .retirement_calculator import calculate_retirement_timeline, calculate_savings_longevity


def calculate_scenario_step_by_step(
    current_monthly_savings: float,
    additional_monthly_savings: float,
    current_age: int,
    retirement_age: int,
    current_savings: float,
    annual_return: float
) -> Dict[str, Any]:
    """
    Calculate scenario analysis with detailed step-by-step breakdown
    """
    
    # Calculate baseline scenario
    baseline_result = calculate_retirement_timeline(
        current_age=current_age,
        retirement_age=retirement_age,
        monthly_savings=current_monthly_savings,
        expected_return=annual_return * 100,  # Convert to percentage
        current_savings=current_savings
    )
    
    # Calculate improved scenario
    new_monthly_savings = current_monthly_savings + additional_monthly_savings
    improved_result = calculate_retirement_timeline(
        current_age=current_age,
        retirement_age=retirement_age,
        monthly_savings=new_monthly_savings,
        expected_return=annual_return * 100,  # Convert to percentage
        current_savings=current_savings
    )
    
    # Calculate the improvement
    improvement = {
        "additional_retirement_fund": improved_result["total_fund"] - baseline_result["total_fund"],
        "percentage_increase": ((improved_result["total_fund"] - baseline_result["total_fund"]) / baseline_result["total_fund"]) * 100,
        "additional_monthly_savings": additional_monthly_savings,
        "new_monthly_savings": new_monthly_savings
    }
    
    # Step-by-step breakdown
    years_to_retirement = retirement_age - current_age
    monthly_return = annual_return / 12
    months_to_retirement = years_to_retirement * 12
    
    steps = {
        "step_1": {
            "description": "Calculate baseline retirement fund",
            "formula": "FV = Current Savings Growth + Monthly Contributions Growth",
            "calculation": f"${baseline_result['total_fund']:,.0f}",
            "details": {
                "current_savings_growth": baseline_result["calculation_details"]["fv_current_savings"],
                "monthly_contributions_growth": baseline_result["calculation_details"]["fv_monthly_contributions"]
            }
        },
        "step_2": {
            "description": "Calculate improved retirement fund with additional savings",
            "formula": f"New Monthly Savings = ${current_monthly_savings:,.0f} + ${additional_monthly_savings:,.0f} = ${new_monthly_savings:,.0f}",
            "calculation": f"${improved_result['total_fund']:,.0f}",
            "details": {
                "current_savings_growth": improved_result["calculation_details"]["fv_current_savings"],
                "monthly_contributions_growth": improved_result["calculation_details"]["fv_monthly_contributions"]
            }
        },
        "step_3": {
            "description": "Calculate the improvement",
            "formula": "Improvement = New Fund - Baseline Fund",
            "calculation": f"${improvement['additional_retirement_fund']:,.0f}",
            "percentage": f"{improvement['percentage_increase']:.1f}% increase"
        },
        "step_4": {
            "description": "Calculate value per extra dollar saved",
            "formula": "Value per $100/month = Additional Fund / (Additional Monthly × 12 × Years)",
            "calculation": f"Each extra $100/month adds approximately ${(improvement['additional_retirement_fund'] / max(additional_monthly_savings, 1) * 100):,.0f}" if additional_monthly_savings > 0 else "No additional savings to analyze",
            "multiplier": improvement['additional_retirement_fund'] / max(additional_monthly_savings, 1) / 12 / years_to_retirement if additional_monthly_savings > 0 else 0
        }
    }
    
    return {
        "baseline": baseline_result,
        "improved": improved_result,
        "improvement": improvement,
        "steps": steps,
        "results": {
            "baseline_fund": baseline_result["total_fund"],
            "improved_fund": improved_result["total_fund"],
            "improvement": improvement
        }
    }


def format_step_by_step_response(calculation_result: Dict[str, Any]) -> str:
    """
    Format the step-by-step calculation into a readable response
    """
    result = calculation_result["results"]
    steps = calculation_result["steps"]
    improvement = result["improvement"]
    
    # Fix the current monthly savings calculation - it should be the original baseline amount
    current_monthly_savings = improvement['new_monthly_savings'] - improvement['additional_monthly_savings']
    
    response = f"""🔄 **Scenario Analysis: Increasing Monthly Savings by ${improvement['additional_monthly_savings']:,.0f}**

📊 **Results Summary:**
• **Current Monthly Savings:** ${current_monthly_savings:,.0f}
• **New Monthly Savings:** ${improvement['new_monthly_savings']:,.0f} (+${improvement['additional_monthly_savings']:,.0f})
• **New Retirement Fund:** ${result['improved_fund']:,.0f}
• **Additional Money:** ${improvement['additional_retirement_fund']:,.0f} (+{improvement['percentage_increase']:.1f}% change)

🧮 **Step-by-Step Calculation:**

**Step 1: Baseline Calculation**
{steps['step_1']['description']}
• Formula: {steps['step_1']['formula']}
• Current savings growth: ${steps['step_1']['details']['current_savings_growth']:,.0f}
• Monthly contributions growth: ${steps['step_1']['details']['monthly_contributions_growth']:,.0f}
• **Total baseline fund: {steps['step_1']['calculation']}**

**Step 2: Improved Scenario**
{steps['step_2']['description']}
• {steps['step_2']['formula']}
• Current savings growth: ${steps['step_2']['details']['current_savings_growth']:,.0f}
• New monthly contributions growth: ${steps['step_2']['details']['monthly_contributions_growth']:,.0f}
• **Total improved fund: {steps['step_2']['calculation']}**

**Step 3: Calculate Improvement**
{steps['step_3']['description']}
• {steps['step_3']['formula']}
• **Improvement: {steps['step_3']['calculation']} ({steps['step_3']['percentage']})**

**Step 4: Value Analysis**
{steps['step_4']['description']}
• **{steps['step_4']['calculation']} to your retirement fund**

💡 **Key Insight:** That's ${improvement['additional_retirement_fund']:,.0f} more for retirement! Each extra ${improvement['additional_monthly_savings']:,.0f} per month adds approximately ${improvement['additional_retirement_fund'] / max(improvement['additional_monthly_savings'], 1):,.0f} to your retirement fund over time.

🎯 **That's fantastic!** Increasing your monthly savings by just ${improvement['additional_monthly_savings']:,.0f} makes a substantial difference, adding hundreds of thousands more to your retirement fund over time. This highlights the incredible power of consistent contributions and smart planning. Keep up the great work – every extra bit truly compounds!"""

    return response


def calculate_withdrawal_longevity_step_by_step(
    retirement_fund: float,
    monthly_withdrawal: float,
    annual_return: float
) -> Dict[str, Any]:
    """
    Calculate withdrawal longevity with step-by-step breakdown
    """
    
    # Use the existing calculator
    result = calculate_savings_longevity(
        retirement_fund=retirement_fund,
        monthly_withdrawal=monthly_withdrawal,
        expected_return=annual_return * 100  # Convert to percentage
    )
    
    # Add step-by-step breakdown
    monthly_return = annual_return / 12
    
    # Calculate 4% rule for comparison
    four_percent_annual = retirement_fund * 0.04
    four_percent_monthly = four_percent_annual / 12
    
    steps = {
        "step_1": {
            "description": "Analyze your retirement fund",
            "calculation": f"Starting retirement fund: ${retirement_fund:,.0f}",
            "details": f"This is your nest egg that will fund your retirement"
        },
        "step_2": {
            "description": "Calculate monthly withdrawal rate",
            "calculation": f"Monthly withdrawal: ${monthly_withdrawal:,.0f}",
            "annual_withdrawal": monthly_withdrawal * 12,
            "withdrawal_rate": (monthly_withdrawal * 12 / retirement_fund) * 100
        },
        "step_3": {
            "description": "Apply investment returns during retirement",
            "calculation": f"Expected annual return: {annual_return * 100:.1f}%",
            "monthly_return": f"Monthly return: {monthly_return * 100:.2f}%",
            "details": "Your money continues to grow even during retirement"
        },
        "step_4": {
            "description": "Calculate how long money will last",
            "formula": "Using present value of annuity formula: PV = PMT × [1 - (1 + r)^(-n)] / r",
            "calculation": f"Your money will last: {result['years_lasting']:.1f} years" if result['years_lasting'] != float('inf') else "Your money will last indefinitely (sustainable withdrawal)",
            "sustainable": result['sustainable']
        },
        "step_5": {
            "description": "Compare to 4% rule",
            "four_percent_monthly": four_percent_monthly,
            "your_withdrawal": monthly_withdrawal,
            "comparison": "above" if monthly_withdrawal > four_percent_monthly else "below",
            "safety_margin": abs(monthly_withdrawal - four_percent_monthly)
        }
    }
    
    return {
        "result": result,
        "steps": steps,
        "results": {
            "years_lasting": result['years_lasting'],
            "months_lasting": result['months_lasting'],
            "sustainable": result['sustainable'],
            "four_percent_comparison": {
                "four_percent_monthly": four_percent_monthly,
                "your_withdrawal": monthly_withdrawal,
                "difference": monthly_withdrawal - four_percent_monthly
            }
        }
    }


def format_withdrawal_analysis(calculation_result: Dict[str, Any]) -> str:
    """
    Format the withdrawal analysis into a readable response
    """
    result = calculation_result["results"]
    steps = calculation_result["steps"]
    
    # Determine sustainability message
    if result["sustainable"]:
        sustainability_msg = "✅ **Sustainable Withdrawal** - Your money will last indefinitely!"
        duration_msg = "Your withdrawal rate is conservative enough that your fund will continue to grow."
    else:
        years = result["years_lasting"]
        sustainability_msg = f"⚠️ **Limited Duration** - Your money will last approximately {years:.1f} years"
        duration_msg = f"After {years:.1f} years, your retirement fund would be depleted at this withdrawal rate."
    
    # 4% rule comparison
    four_percent_data = result["four_percent_comparison"]
    if four_percent_data["difference"] > 0:
        four_percent_msg = f"📈 Your withdrawal (${four_percent_data['your_withdrawal']:,.0f}/month) is **${four_percent_data['difference']:,.0f} above** the 4% rule (${four_percent_data['four_percent_monthly']:,.0f}/month)"
        four_percent_advice = "Consider reducing your withdrawal rate for better long-term sustainability."
    else:
        four_percent_msg = f"📉 Your withdrawal (${four_percent_data['your_withdrawal']:,.0f}/month) is **${abs(four_percent_data['difference']):,.0f} below** the 4% rule (${four_percent_data['four_percent_monthly']:,.0f}/month)"
        four_percent_advice = "Your withdrawal rate is conservative and should be sustainable long-term."
    
    response = f"""💰 **Withdrawal Longevity Analysis**

{sustainability_msg}

🧮 **Step-by-Step Analysis:**

**Step 1: Starting Position**
• {steps['step_1']['calculation']}
• {steps['step_1']['details']}

**Step 2: Withdrawal Rate Analysis**
• {steps['step_2']['calculation']}
• Annual withdrawal: ${steps['step_2']['annual_withdrawal']:,.0f}
• Withdrawal rate: {steps['step_2']['withdrawal_rate']:.2f}% of your fund annually

**Step 3: Investment Growth During Retirement**
• {steps['step_3']['calculation']}
• {steps['step_3']['monthly_return']}
• {steps['step_3']['details']}

**Step 4: Longevity Calculation**
• {steps['step_4']['calculation']}
• Formula used: {steps['step_4']['formula']}

**Step 5: 4% Rule Comparison**
• {four_percent_msg}
• **Recommendation:** {four_percent_advice}

📊 **Summary:**
{duration_msg}

💡 **Key Insights:**
• The 4% rule suggests withdrawing no more than 4% of your retirement fund annually
• Your current withdrawal rate factors in continued investment growth
• {"Sustainable withdrawals help ensure your money lasts throughout retirement" if result["sustainable"] else "Consider adjusting your withdrawal rate or retirement timeline for better sustainability"}

🎯 **Next Steps:** {"You're in great shape! Your withdrawal plan appears sustainable." if result["sustainable"] else "Consider reducing monthly withdrawals or exploring ways to increase your retirement fund."}"""

    return response