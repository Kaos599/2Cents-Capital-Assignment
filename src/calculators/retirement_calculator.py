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
    
    # Validate inputs
    if retirement_fund <= 0 or monthly_withdrawal <= 0:
        return {
            "error": "Invalid input: fund and withdrawal must be positive",
            "months_lasting": 0,
            "years_lasting": 0,
            "sustainable": False
        }
    
    try:
        # Using PV annuity formula to find number of periods
        # PV = PMT × [1 – (1 + r)^(–n)] / r
        # Solving for n: n = -log(1 - (PV × r) / PMT) / log(1 + r)
        
        if monthly_return == 0:
            # No growth case
            months_lasting = retirement_fund / monthly_withdrawal
            sustainable = False
        else:
            pv_ratio = (retirement_fund * monthly_return) / monthly_withdrawal
            if pv_ratio >= 1:
                months_lasting = float('inf')  # Money lasts forever
                sustainable = True
            else:
                months_lasting = -math.log(1 - pv_ratio) / math.log(1 + monthly_return)
                sustainable = False
        
        years_lasting = months_lasting / 12 if months_lasting != float('inf') else float('inf')
        
        # Calculate 4% rule comparison
        four_percent_monthly = (retirement_fund * 0.04) / 12
        
        return {
            "months_lasting": months_lasting,
            "years_lasting": years_lasting,
            "monthly_withdrawal": monthly_withdrawal,
            "expected_return": expected_return,
            "retirement_fund": retirement_fund,
            "sustainable": sustainable,
            "four_percent_rule_monthly": four_percent_monthly,
            "withdrawal_vs_four_percent": monthly_withdrawal / four_percent_monthly if four_percent_monthly > 0 else 0,
            "calculation_details": {
                "monthly_return": monthly_return,
                "pv_ratio": pv_ratio if monthly_return != 0 else None,
                "annual_return": annual_return
            }
        }
    
    except (ValueError, ZeroDivisionError, OverflowError) as e:
        return {
            "error": f"Calculation error: {str(e)}",
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
        required_monthly = None
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
        "required_monthly_savings": required_monthly,
        "projected_savings": projected_savings,
        "shortfall": shortfall,
        "monthly_savings_capacity": monthly_savings_capacity
    }


def calculate_emergency_fund(
    monthly_expenses: float,
    target_months: int = 6,
    current_emergency_fund: float = 0,
    monthly_savings_capacity: float = None,
    expected_return: float = 2.0
) -> Dict[str, Any]:
    """
    Calculate emergency fund requirements and timeline
    """
    target_amount = monthly_expenses * target_months
    shortfall = max(0, target_amount - current_emergency_fund)
    
    if monthly_savings_capacity and shortfall > 0:
        # Calculate time to reach target
        monthly_return = expected_return / 100 / 12
        
        if monthly_return == 0:
            months_to_target = shortfall / monthly_savings_capacity
        else:
            # Using FV annuity formula to find periods
            try:
                months_to_target = math.log(1 + (shortfall * monthly_return) / monthly_savings_capacity) / math.log(1 + monthly_return)
            except (ValueError, ZeroDivisionError):
                months_to_target = shortfall / monthly_savings_capacity
    else:
        months_to_target = None
    
    return {
        "target_amount": target_amount,
        "current_amount": current_emergency_fund,
        "shortfall": shortfall,
        "monthly_expenses": monthly_expenses,
        "target_months": target_months,
        "monthly_savings_capacity": monthly_savings_capacity,
        "months_to_target": months_to_target,
        "years_to_target": months_to_target / 12 if months_to_target else None,
        "already_sufficient": shortfall == 0
    }


def calculate_mortgage_vs_rent(
    home_price: float,
    down_payment_percent: float,
    mortgage_rate: float,
    mortgage_years: int,
    monthly_rent: float,
    property_tax_annual: float,
    insurance_annual: float,
    maintenance_percent: float = 1.0,
    home_appreciation_rate: float = 3.0,
    investment_return_rate: float = 7.0
) -> Dict[str, Any]:
    """
    Compare buying vs renting over time
    """
    down_payment = home_price * (down_payment_percent / 100)
    loan_amount = home_price - down_payment
    
    # Calculate monthly mortgage payment
    monthly_rate = mortgage_rate / 100 / 12
    num_payments = mortgage_years * 12
    
    if monthly_rate == 0:
        monthly_mortgage = loan_amount / num_payments
    else:
        monthly_mortgage = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    # Monthly ownership costs
    monthly_property_tax = property_tax_annual / 12
    monthly_insurance = insurance_annual / 12
    monthly_maintenance = home_price * (maintenance_percent / 100) / 12
    
    total_monthly_ownership = monthly_mortgage + monthly_property_tax + monthly_insurance + monthly_maintenance
    
    # Calculate net worth after mortgage term
    # Home value after appreciation
    future_home_value = future_value(home_price, home_appreciation_rate / 100, mortgage_years)
    
    # Remaining mortgage balance (should be 0 after full term)
    remaining_balance = 0
    
    # Net home equity
    home_equity = future_home_value - remaining_balance
    
    # Renting scenario - invest the difference
    monthly_difference = total_monthly_ownership - monthly_rent
    if monthly_difference > 0:
        # If buying costs more, invest the difference
        investment_value = fv_annuity(monthly_difference, investment_return_rate / 100 / 12, mortgage_years * 12)
        # Also invest the down payment
        down_payment_growth = future_value(down_payment, investment_return_rate / 100, mortgage_years)
        total_investment_value = investment_value + down_payment_growth
    else:
        # If renting costs more, just invest the down payment
        total_investment_value = future_value(down_payment, investment_return_rate / 100, mortgage_years)
    
    return {
        "home_price": home_price,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "monthly_mortgage": monthly_mortgage,
        "total_monthly_ownership": total_monthly_ownership,
        "monthly_rent": monthly_rent,
        "monthly_difference": monthly_difference,
        "future_home_value": future_home_value,
        "home_equity": home_equity,
        "investment_value": total_investment_value,
        "net_worth_buying": home_equity,
        "net_worth_renting": total_investment_value,
        "recommendation": "buy" if home_equity > total_investment_value else "rent",
        "difference": abs(home_equity - total_investment_value),
        "mortgage_years": mortgage_years
    }
