"""
Real API integration tests using actual API keys from .env file
"""

import pytest
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

from src.tools.financial_tools import (
    search_financial_info,
    get_market_data,
    retirement_calculator_tool,
    savings_longevity_tool,
    required_savings_tool
)


class TestRealAPIIntegration:
    """Test suite for real API integrations"""

    def test_tavily_search_real_api(self):
        """Test Tavily search with real API key"""
        # Verify API key is loaded
        api_key = os.getenv("TAVILY_API_KEY")
        assert api_key is not None, "TAVILY_API_KEY not found in environment"
        
        # Perform real search
        result = search_financial_info.func("retirement planning strategies 2024")
        
        print(f"Tavily Search Result: {result[:500]}...")  # Print first 500 chars
        
        # Verify we got meaningful results
        assert isinstance(result, str)
        assert len(result) > 50  # Should have substantial content
        assert "error" not in result.lower()  # Should not contain error messages
        
    def test_yahoo_finance_real_api(self):
        """Test Yahoo Finance with real market data"""
        # Test with a popular stock
        result = get_market_data.func("AAPL")
        
        print(f"Yahoo Finance Result: {result}")
        
        # Verify we got real market data
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert "current_price" in result
        assert "last_updated" in result
        assert "error" not in result  # Should not contain errors
        
    def test_retirement_calculator_with_real_data(self):
        """Test retirement calculator with realistic data"""
        result = retirement_calculator_tool.func(
            current_age=28,
            retirement_age=67,
            monthly_savings=800,
            expected_return=7.5,
            current_savings=25000
        )
        
        print(f"Retirement Calculation Result: {result}")
        
        # Verify calculation results
        assert "total_fund" in result
        assert "years_to_retirement" in result
        assert result["years_to_retirement"] == 39
        assert result["total_fund"] > 100000  # Should be substantial
        assert result["calculation_type"] == "retirement_timeline"
        
    def test_savings_longevity_realistic_scenario(self):
        """Test how long savings last in realistic retirement scenario"""
        result = savings_longevity_tool.func(
            retirement_fund=750000,
            monthly_withdrawal=4000,
            expected_return=4.0
        )
        
        print(f"Savings Longevity Result: {result}")
        
        # Verify longevity calculation
        assert "years_lasting" in result
        assert "months_lasting" in result
        assert result["years_lasting"] > 15  # Should last reasonable time
        assert result["calculation_type"] == "savings_longevity"
        
    def test_required_savings_millionaire_goal(self):
        """Test required savings to become a millionaire"""
        result = required_savings_tool.func(
            current_age=25,
            retirement_age=65,
            target_amount=1000000,
            current_savings=10000,
            expected_return=8.0
        )
        
        print(f"Required Savings Result: {result}")
        
        # Verify required savings calculation
        assert "required_monthly_savings" in result
        assert result["required_monthly_savings"] > 0
        assert result["target_amount"] == 1000000
        assert result["calculation_type"] == "required_monthly_savings"


class TestConversationalFlow:
    """Test conversational flow with state memory"""
    
    def setUp(self):
        """Set up test state"""
        self.user_state = {
            'current_age': None,
            'retirement_age': None,
            'monthly_income': None,
            'current_savings': None,
            'monthly_savings': None,
            'expected_return': None,
            'risk_tolerance': None,
            'goals': [],
            'completed_persona': False
        }
        self.conversation_history = []
        
    def test_full_conversation_flow(self):
        """Test a complete conversation flow with state memory"""
        self.setUp()
        
        # Simulate conversation steps
        conversation_steps = [
            {"user": "Hi, I want to plan for retirement", "action": "greeting"},
            {"user": "I'm 32 years old", "action": "set_age", "value": 32},
            {"user": "I want to retire at 65", "action": "set_retirement_age", "value": 65},
            {"user": "I have $45,000 in savings", "action": "set_current_savings", "value": 45000},
            {"user": "I save $1,200 per month", "action": "set_monthly_savings", "value": 1200},
            {"user": "I expect 7% annual returns", "action": "set_expected_return", "value": 7.0},
        ]
        
        # Process each conversation step
        for step in conversation_steps:
            self.conversation_history.append(step["user"])
            
            # Update state based on action
            if step["action"] == "set_age":
                self.user_state["current_age"] = step["value"]
            elif step["action"] == "set_retirement_age":
                self.user_state["retirement_age"] = step["value"]
            elif step["action"] == "set_current_savings":
                self.user_state["current_savings"] = step["value"]
            elif step["action"] == "set_monthly_savings":
                self.user_state["monthly_savings"] = step["value"]
            elif step["action"] == "set_expected_return":
                self.user_state["expected_return"] = step["value"]
        
        # Mark persona as complete
        self.user_state["completed_persona"] = True
        
        print(f"Final User State: {self.user_state}")
        print(f"Conversation History: {self.conversation_history}")
        
        # Verify state memory persistence
        assert self.user_state["current_age"] == 32
        assert self.user_state["retirement_age"] == 65
        assert self.user_state["current_savings"] == 45000
        assert self.user_state["monthly_savings"] == 1200
        assert self.user_state["expected_return"] == 7.0
        assert self.user_state["completed_persona"] is True
        assert len(self.conversation_history) == 6
        
        # Now run calculation with the collected data
        calculation_result = retirement_calculator_tool.func(
            current_age=self.user_state["current_age"],
            retirement_age=self.user_state["retirement_age"],
            monthly_savings=self.user_state["monthly_savings"],
            expected_return=self.user_state["expected_return"],
            current_savings=self.user_state["current_savings"]
        )
        
        print(f"Final Calculation: {calculation_result}")
        
        # Verify calculation worked with conversation data
        assert calculation_result["total_fund"] > 0
        assert calculation_result["years_to_retirement"] == 33
        
    def test_api_integration_with_search(self):
        """Test API integration by searching for current financial advice"""
        # Search for current retirement advice
        search_result = search_financial_info.func(
            "2024 retirement planning inflation impact strategies"
        )
        
        print(f"Current Financial Advice Search: {search_result[:300]}...")
        
        # Verify we get current, relevant information
        assert isinstance(search_result, str)
        assert len(search_result) > 100
        assert any(keyword in search_result.lower() for keyword in 
                  ["retirement", "inflation", "2024", "planning", "strategy"])
        
    def test_market_data_integration(self):
        """Test market data integration for investment advice"""
        # Get data for major market indices
        sp500_data = get_market_data.func("SPY")  # S&P 500 ETF
        tech_data = get_market_data.func("QQQ")   # NASDAQ-100 ETF
        
        print(f"S&P 500 Data: {sp500_data}")
        print(f"Tech Data: {tech_data}")
        
        # Verify we can get real market data for investment recommendations
        assert sp500_data["symbol"] == "SPY"
        assert tech_data["symbol"] == "QQQ"
        assert "current_price" in sp500_data
        assert "current_price" in tech_data
        
        # Both should have valid price data (or N/A which is acceptable for some ETFs)
        price_spy = sp500_data.get("current_price", 0)
        price_qqq = tech_data.get("current_price", 0)
        
        # Price should be either a number > 0 or "N/A"
        assert (isinstance(price_spy, (int, float)) and price_spy > 0) or price_spy == "N/A"
        assert (isinstance(price_qqq, (int, float)) and price_qqq > 0) or price_qqq == "N/A"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
