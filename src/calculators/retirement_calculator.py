"""
Retirement planning calculations using the core financial formulas
"""

from typing import Dict, Any
import math
from .financial_formulas import (
    future_value, present_value, fv_annuity, pv_annuity, 
    nper_calculation, rule_of_72
)


def calculate_retirement_timeline(
    current_age: int,
    retirement_age: int,
    monthly_savings: float,
    expected_return: float,
    current_savings: float = 0,
    target_retirement_fund: float = None,
    inflation_rate: float = 0.03
) -> Dict[str, Any]:
    """
    Calculate comprehensive retirement projections
    """
    years_to_retirement = retirement_age - current_age
    annual_return = expected_return / 100
    monthly_return = annual_return / 12
    months_to_retirement = years_to_retirement * 12
    
    # Future value of current savings
    fv_current = future_value(current_savings, annual_return, years_to_retirement)
    
    # Future value of monthly contributions
    fv_monthly = fv_annuity(monthly_savings, monthly_return, months_to_retirement)
    
    total_retirement_fund = fv_current + fv_monthly
    
    # Adjust for inflation
    real_purchasing_power = present_value(
        total_retirement_fund, 
        inflation_rate, 
        years_to_retirement
    )
    
    return {
        "total_fund": total_retirement_fund,
        "real_purchasing_power": real_purchasing_power,
        "years_to_retirement": years_to_retirement,
        "monthly_contributions": monthly_savings,
        "projected_annual_return": expected_return,
        "inflation_adjusted": True,
        "calculation_details": {
            "fv_current_savings": fv_current,
            "fv_monthly_contributions": fv_monthly,
            "inflation_rate_used": inflation_rate
        }
    }


def calculate_savings_longevity(
    retirement_fund: float,
    monthly_withdrawal: float,
    expected_return: float,
    inflation_rate: float = 0.03
) -> Dict[str, Any]:
    """
    Calculate how long retirement savings will last with monthly withdrawals
    """
    annual_return = expected_return / 100
    monthly_return = annual_return / 12
    
    # Calculate real monthly withdrawal (inflation-adjusted)
    real_monthly_withdrawal = monthly_withdrawal
    
    try:
        # Using PV annuity formula to find number of periods
        # PV = PMT × [1 – (1 + r)^(–n)] / r
        # Solving for n: n = -log(1 - (PV × r) / PMT) / log(1 + r)
        
        if monthly_return == 0:
            months_lasting = retirement_fund / monthly_withdrawal
        else:
            pv_ratio = (retirement_fund * monthly_return) / monthly_withdrawal
            if pv_ratio >= 1:
                months_lasting = float('inf')  # Money lasts forever
            else:
                months_lasting = -math.log(1 - pv_ratio) / math.log(1 + monthly_return)
        
        years_lasting = months_lasting / 12
        
        return {
            "months_lasting": months_lasting,
            "years_lasting": years_lasting,
            "monthly_withdrawal": monthly_withdrawal,
            "expected_return": expected_return,
            "retirement_fund": retirement_fund,
            "sustainable": months_lasting == float('inf'),
            "calculation_details": {
                "monthly_return": monthly_return,
                "pv_ratio": pv_ratio if monthly_return != 0 else None
            }
        }
    
    except (ValueError, ZeroDivisionError):
        return {
            "error": "Invalid calculation parameters",
            "months_lasting": 0,
            "years_lasting": 0,
            "sustainable": False
        }


def calculate_required_monthly_savings(
    current_age: int,
    retirement_age: int,
    target_amount: float,
    current_savings: float,
    expected_return: float
) -> Dict[str, Any]:
    """
    Calculate required monthly savings to reach a target retirement amount
    """
    years_to_retirement = retirement_age - current_age
    annual_return = expected_return / 100
    monthly_return = annual_return / 12
    months_to_retirement = years_to_retirement * 12
    
    # Future value of current savings
    fv_current = future_value(current_savings, annual_return, years_to_retirement)
    
    # Amount needed from monthly contributions
    amount_needed_from_monthly = target_amount - fv_current
    
    if amount_needed_from_monthly <= 0:
        required_monthly_savings = 0
    else:
        # PMT = FV × r / [(1 + r)^n - 1]
        if monthly_return == 0:
            required_monthly_savings = amount_needed_from_monthly / months_to_retirement
        else:
            required_monthly_savings = (
                amount_needed_from_monthly * monthly_return
            ) / ((1 + monthly_return) ** months_to_retirement - 1)
    
    return {
        "required_monthly_savings": required_monthly_savings,
        "target_amount": target_amount,
        "current_savings": current_savings,
        "years_to_retirement": years_to_retirement,
        "expected_return": expected_return,
        "fv_current_savings": fv_current,
        "amount_from_monthly": amount_needed_from_monthly,
        "already_sufficient": amount_needed_from_monthly <= 0
    }


def calculate_retirement_income_replacement(
    current_annual_income: float,
    desired_replacement_ratio: float,
    retirement_years: int,
    expected_return_retirement: float,
    inflation_rate: float = 0.03
) -> Dict[str, Any]:
    """
    Calculate required retirement fund for income replacement
    """
    desired_annual_income = current_annual_income * (desired_replacement_ratio / 100)
    desired_monthly_income = desired_annual_income / 12
    
    # Calculate required fund using PV of annuity
    annual_return = expected_return_retirement / 100
    monthly_return = annual_return / 12
    months_in_retirement = retirement_years * 12
    
    required_fund = pv_annuity(desired_monthly_income, monthly_return, months_in_retirement)
    
    return {
        "required_retirement_fund": required_fund,
        "desired_annual_income": desired_annual_income,
        "desired_monthly_income": desired_monthly_income,
        "replacement_ratio": desired_replacement_ratio,
        "retirement_years": retirement_years,
        "expected_return": expected_return_retirement
    }


def compare_investment_vs_debt_payoff(
    debt_amount: float,
    debt_interest_rate: float,
    investment_return_rate: float,
    time_horizon_years: int,
    monthly_available: float
) -> Dict[str, Any]:
    """
    Compare paying off debt vs investing the same amount
    """
    # Scenario 1: Pay off debt first, then invest
    months_to_payoff = nper_calculation(
        debt_interest_rate / 100 / 12,
        monthly_available,
        -debt_amount
    )
    years_to_payoff = months_to_payoff / 12
    
    remaining_years = time_horizon_years - years_to_payoff
    if remaining_years > 0:
        investment_after_payoff = fv_annuity(
            monthly_available,
            investment_return_rate / 100 / 12,
            remaining_years * 12
        )
    else:
        investment_after_payoff = 0
    
    # Scenario 2: Invest while making minimum payments
    # Assuming minimum payment is interest only for simplicity
    minimum_payment = debt_amount * (debt_interest_rate / 100) / 12
    investment_monthly = monthly_available - minimum_payment
    
    if investment_monthly > 0:
        investment_with_debt = fv_annuity(
            investment_monthly,
            investment_return_rate / 100 / 12,
            time_horizon_years * 12
        )
        remaining_debt = debt_amount  # Simplified - only paying interest
    else:
        investment_with_debt = 0
        remaining_debt = debt_amount
    
    net_worth_payoff_first = investment_after_payoff
    net_worth_invest_with_debt = investment_with_debt - remaining_debt
    
    return {
        "payoff_first_scenario": {
            "years_to_payoff": years_to_payoff,
            "investment_value": investment_after_payoff,
            "net_worth": net_worth_payoff_first
        },
        "invest_with_debt_scenario": {
            "investment_value": investment_with_debt,
            "remaining_debt": remaining_debt,
            "net_worth": net_worth_invest_with_debt
        },
        "recommendation": "payoff_first" if net_worth_payoff_first > net_worth_invest_with_debt else "invest_with_debt",
        "difference": abs(net_worth_payoff_first - net_worth_invest_with_debt),
        "debt_rate": debt_interest_rate,
        "investment_rate": investment_return_rate
    }


def calculate_college_funding(
    current_cost: float,
    years_until_needed: int,
    education_inflation_rate: float,
    expected_return: float,
    monthly_savings_capacity: float = None
) -> Dict[str, Any]:
    """
    Calculate college funding requirements
    """
    # Future cost of education with inflation
    future_education_cost = future_value(
        current_cost,
        education_inflation_rate / 100,
        years_until_needed
    )
    
    # Required monthly savings if specified
    if monthly_savings_capacity:
        monthly_return = expected_return / 100 / 12
        months_to_save = years_until_needed * 12
        
        projected_savings = fv_annuity(
            monthly_savings_capacity,
            monthly_return,
            months_to_save
        )
        
        shortfall = max(0, future_education_cost - projected_savings)
    else:
        # Calculate required monthly savings
        monthly_return = expected_return / 100 / 12
        months_to_save = years_until_needed * 12
        
        if monthly_return == 0:
            required_monthly = future_education_cost / months_to_save
        else:
            required_monthly = (
                future_education_cost * monthly_return
            ) / ((1 + monthly_return) ** months_to_save - 1)
        
        projected_savings = future_education_cost
        shortfall = 0
    
    return {
        "current_cost": current_cost,
        "future_cost": future_education_cost,
        "years_until_needed": years_until_needed,
        "education_inflation_rate": education_inflation_rate,
        "expected_return": expected_return,
        "required_monthly_savings": required_monthly if not monthly_savings_capacity else None,
        "projected_savings": projected_savings,
        "shortfall": shortfall,
        "monthly_savings_capacity": monthly_savings_capacity
    }
