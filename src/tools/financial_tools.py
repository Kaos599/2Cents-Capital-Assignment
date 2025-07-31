"""
Financial calculation tools for the LangGraph agent
"""

import os
from typing import Dict, Any
from langchain.tools import tool
from tavily import TavilyClient
import yfinance as yf
from datetime import datetime

from ..calculators.retirement_calculator import (
    calculate_retirement_timeline,
    calculate_savings_longevity,
    calculate_required_monthly_savings,
    calculate_retirement_income_replacement,
    compare_investment_vs_debt_payoff,
    calculate_college_funding
)


@tool
def search_financial_info(query: str) -> str:
    """Search for current financial information and market data using Tavily."""
    try:
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = tavily_client.search(
            query, 
            search_depth="advanced",
            max_results=3
        )
        
        results = []
        for result in response.get('results', []):
            results.append(f"Title: {result.get('title', 'N/A')}\n"
                         f"Content: {result.get('content', 'N/A')}\n"
                         f"URL: {result.get('url', 'N/A')}\n")
        
        return "\n".join(results)
    except Exception as e:
        return f"Error searching financial information: {str(e)}"


@tool
def get_market_data(symbol: str) -> Dict:
    """Get current market data and historical information using Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        history = ticker.history(period="1y")
        
        return {
            "symbol": symbol,
            "current_price": info.get("currentPrice", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "beta": info.get("beta", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Error fetching market data for {symbol}: {str(e)}"}


@tool
def retirement_calculator_tool(
    current_age: int,
    retirement_age: int, 
    monthly_savings: float,
    expected_return: float,
    current_savings: float = 0
) -> Dict:
    """Calculate retirement projections using financial formulas."""
    try:
        result = calculate_retirement_timeline(
            current_age=current_age,
            retirement_age=retirement_age,
            monthly_savings=monthly_savings,
            expected_return=expected_return,
            current_savings=current_savings
        )
        
        result["calculation_type"] = "retirement_timeline"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        return {"error": f"Error calculating retirement timeline: {str(e)}"}


@tool
def savings_longevity_tool(
    retirement_fund: float,
    monthly_withdrawal: float,
    expected_return: float
) -> Dict:
    """Calculate how long retirement savings will last with monthly withdrawals."""
    try:
        result = calculate_savings_longevity(
            retirement_fund=retirement_fund,
            monthly_withdrawal=monthly_withdrawal,
            expected_return=expected_return
        )
        
        result["calculation_type"] = "savings_longevity"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        return {"error": f"Error calculating savings longevity: {str(e)}"}


@tool
def required_savings_tool(
    current_age: int,
    retirement_age: int,
    target_amount: float,
    current_savings: float,
    expected_return: float
) -> Dict:
    """Calculate required monthly savings to reach a target retirement amount."""
    try:
        result = calculate_required_monthly_savings(
            current_age=current_age,
            retirement_age=retirement_age,
            target_amount=target_amount,
            current_savings=current_savings,
            expected_return=expected_return
        )
        
        result["calculation_type"] = "required_monthly_savings"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        return {"error": f"Error calculating required savings: {str(e)}"}


@tool
def income_replacement_tool(
    current_annual_income: float,
    desired_replacement_ratio: float,
    retirement_years: int,
    expected_return_retirement: float
) -> Dict:
    """Calculate required retirement fund for income replacement."""
    try:
        result = calculate_retirement_income_replacement(
            current_annual_income=current_annual_income,
            desired_replacement_ratio=desired_replacement_ratio,
            retirement_years=retirement_years,
            expected_return_retirement=expected_return_retirement
        )
        
        result["calculation_type"] = "income_replacement"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        return {"error": f"Error calculating income replacement: {str(e)}"}


@tool
def debt_vs_investment_tool(
    debt_amount: float,
    debt_interest_rate: float,
    investment_return_rate: float,
    time_horizon_years: int,
    monthly_available: float
) -> Dict:
    """Compare paying off debt vs investing the same amount."""
    try:
        result = compare_investment_vs_debt_payoff(
            debt_amount=debt_amount,
            debt_interest_rate=debt_interest_rate,
            investment_return_rate=investment_return_rate,
            time_horizon_years=time_horizon_years,
            monthly_available=monthly_available
        )
        
        result["calculation_type"] = "debt_vs_investment"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        return {"error": f"Error comparing debt vs investment: {str(e)}"}


@tool
def college_funding_tool(
    current_cost: float,
    years_until_needed: int,
    education_inflation_rate: float,
    expected_return: float,
    monthly_savings_capacity: float = None
) -> Dict:
    """Calculate college funding requirements."""
    try:
        result = calculate_college_funding(
            current_cost=current_cost,
            years_until_needed=years_until_needed,
            education_inflation_rate=education_inflation_rate,
            expected_return=expected_return,
            monthly_savings_capacity=monthly_savings_capacity
        )
        
        result["calculation_type"] = "college_funding"
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        return {"error": f"Error calculating college funding: {str(e)}"}


# List of all available tools
FINANCIAL_TOOLS = [
    search_financial_info,
    get_market_data,
    retirement_calculator_tool,
    savings_longevity_tool,
    required_savings_tool,
    income_replacement_tool,
    debt_vs_investment_tool,
    college_funding_tool
]
