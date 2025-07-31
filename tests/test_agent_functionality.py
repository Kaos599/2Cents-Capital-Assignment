"""
Comprehensive tests for Financial Planning Agent functionality
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# Import agent components
from src.agents.state import AgentState, UserProfile
from src.tools.financial_tools import (
    retirement_calculator_tool,
    savings_longevity_tool,
    required_savings_tool,
    search_financial_info,
    get_market_data
)
from src.calculators.retirement_calculator import (
    calculate_retirement_timeline,
    calculate_savings_longevity,
    calculate_required_monthly_savings
)


class TestAgentFunctionality:
    """Test suite for agent functionality"""

    def test_retirement_calculator_tool(self):
        """Test retirement calculator tool with valid inputs"""
        result = retirement_calculator_tool.func(
            current_age=30,
            retirement_age=65,
            monthly_savings=500,
            expected_return=6.0,
            current_savings=10000
        )
        
        assert "total_fund" in result
        assert "years_to_retirement" in result
        assert result["years_to_retirement"] == 35
        assert result["calculation_type"] == "retirement_timeline"
        assert "timestamp" in result
        assert result["total_fund"] > 0

    def test_savings_longevity_tool(self):
        """Test savings longevity tool"""
        result = savings_longevity_tool.func(
            retirement_fund=400000,
            monthly_withdrawal=3000,
            expected_return=5.0
        )
        
        assert "years_lasting" in result
        assert "months_lasting" in result
        assert result["calculation_type"] == "savings_longevity"
        assert "timestamp" in result
        assert result["years_lasting"] > 0

    def test_required_savings_tool(self):
        """Test required savings calculation tool"""
        result = required_savings_tool.func(
            current_age=25,
            retirement_age=65,
            target_amount=1000000,
            current_savings=5000,
            expected_return=7.0
        )
        
        assert "required_monthly_savings" in result
        assert result["calculation_type"] == "required_monthly_savings"
        assert "timestamp" in result
        assert result["required_monthly_savings"] > 0

    @patch('src.tools.financial_tools.TavilyClient')
    def test_search_financial_info_tool(self, mock_tavily):
        """Test Tavily search integration"""
        # Mock Tavily response
        mock_client = Mock()
        mock_tavily.return_value = mock_client
        mock_client.search.return_value = {
            'results': [
                {
                    'title': 'Test Financial Article',
                    'content': 'This is test financial content',
                    'url': 'https://example.com/finance'
                }
            ]
        }
        
        with patch.dict(os.environ, {'TAVILY_API_KEY': 'test-key'}):
            result = search_financial_info.func("retirement planning tips")
            
            assert "Test Financial Article" in result
            assert "This is test financial content" in result
            mock_client.search.assert_called_once()

    @patch('src.tools.financial_tools.yf.Ticker')
    def test_get_market_data_tool(self, mock_ticker):
        """Test Yahoo Finance integration"""
        # Mock Yahoo Finance response
        mock_ticker_instance = Mock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.info = {
            'currentPrice': 150.0,
            'marketCap': 1000000000,
            'trailingPE': 25.0,
            'sector': 'Technology'
        }
        mock_ticker_instance.history.return_value = Mock()
        
        result = get_market_data.func("AAPL")
        
        assert result["symbol"] == "AAPL"
        assert result["current_price"] == 150.0
        assert result["sector"] == "Technology"
        assert "last_updated" in result

    def test_agent_state_structure(self):
        """Test agent state structure and initialization"""
        state = {
            'messages': [],
            'user_profile': {
                'current_age': None,
                'retirement_age': None,
                'monthly_income': None,
                'current_savings': None,
                'monthly_savings': None,
                'expected_return': None,
                'risk_tolerance': None,
                'goals': [],
                'completed_persona': False
            },
            'calculations': {},
            'search_results': [],
            'current_step': '',
            'conversation_history': [],
            'session_id': 'test-session'
        }
        
        # Verify state structure
        assert 'user_profile' in state
        assert 'calculations' in state
        assert 'messages' in state
        assert state['user_profile']['completed_persona'] is False

    def test_calculation_accuracy(self):
        """Test calculation accuracy against known values"""
        # Test retirement timeline calculation
        result = calculate_retirement_timeline(
            current_age=30,
            retirement_age=65,
            monthly_savings=1000,
            expected_return=7.0,
            current_savings=20000
        )
        
        # Verify calculation components
        assert result['total_fund'] > result['calculation_details']['fv_current_savings']
        assert result['total_fund'] > result['calculation_details']['fv_monthly_contributions']
        assert result['real_purchasing_power'] < result['total_fund']  # Due to inflation

    def test_error_handling(self):
        """Test error handling in tools"""
        # Test with invalid inputs
        result = retirement_calculator_tool.func(
            current_age=-5,  # Invalid age
            retirement_age=65,
            monthly_savings=500,
            expected_return=6.0,
            current_savings=10000
        )
        
        # Should handle gracefully or return error
        assert isinstance(result, dict)

    def test_multiple_calculations_consistency(self):
        """Test consistency across multiple calculations"""
        # Run same calculation multiple times
        results = []
        for _ in range(3):
            result = retirement_calculator_tool.func(
                current_age=30,
                retirement_age=65,
                monthly_savings=500,
                expected_return=6.0,
                current_savings=10000
            )
            results.append(result['total_fund'])
        
        # All results should be identical
        assert all(r == results[0] for r in results)

    def test_tool_input_validation(self):
        """Test tool input validation"""
        # Test with missing required parameters
        with pytest.raises(TypeError):
            retirement_calculator_tool.func(
                current_age=30,
                # Missing required parameters
            )

    def test_calculation_edge_cases(self):
        """Test edge cases in calculations"""
        # Test with zero savings
        result = retirement_calculator_tool.func(
            current_age=30,
            retirement_age=65,
            monthly_savings=0,
            expected_return=6.0,
            current_savings=0
        )
        assert result['total_fund'] == 0

        # Test with zero return rate
        result = retirement_calculator_tool.func(
            current_age=30,
            retirement_age=65,
            monthly_savings=500,
            expected_return=0.0,
            current_savings=10000
        )
        assert result['total_fund'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
