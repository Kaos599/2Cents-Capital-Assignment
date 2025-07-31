"""
Agent state definition for the Financial Planning Agent
"""

from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State structure for the Financial Planning Agent."""
    messages: List[BaseMessage]
    user_profile: Dict[str, Any]
    calculations: Dict[str, Any]
    search_results: List[Dict]
    current_step: str
    conversation_history: List[Dict[str, str]]
    session_id: str


class UserProfile(TypedDict):
    """User financial profile structure."""
    current_age: Optional[int]
    retirement_age: Optional[int]
    monthly_income: Optional[float]
    current_savings: Optional[float]
    monthly_savings: Optional[float]
    expected_return: Optional[float]
    risk_tolerance: Optional[str]
    goals: List[str]
    completed_persona: bool


class CalculationResult(TypedDict):
    """Structure for calculation results."""
    calculation_type: str
    inputs: Dict[str, Any]
    results: Dict[str, Any]
    explanation: str
    timestamp: str
