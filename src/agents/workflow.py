"""
Financial Planning Agent Workflow using LangGraph
"""

import os
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool

# Import the state and tools
from .state import AgentState, UserProfile, CalculationResult
from ..tools.financial_tools import FINANCIAL_TOOLS

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)


# Define an agent node for collecting user information
async def persona_builder_node(state: AgentState):
    """Collect user information through guided questions."""
    if not state['user_profile']['completed_persona']:
        # Ask questions to build user profile
        # This is a simplified process; normally it would engage interactively
        state['user_profile'].update({
            "current_age": 30,
            "retirement_age": 65,
            "monthly_income": 5000,
            "current_savings": 10000,
            "monthly_savings": 500,
            "expected_return": 0.06,
            "risk_tolerance": "Moderate",
            "goals": [],
            "completed_persona": True
        })


# Define an agent node for performing financial calculations
async def calculation_node(state: AgentState):
    """Perform financial calculations based on user profile."""
    # Example calculation
    tool: Tool = FINANCIAL_TOOLS[2]  # Example tool: retirement_calculator_tool
    state['calculations'] = tool.invoke({
        "current_age": state['user_profile']['current_age'],
        "retirement_age": state['user_profile']['retirement_age'],
        "monthly_savings": state['user_profile']['monthly_savings'],
        "expected_return": state['user_profile']['expected_return'],
        "current_savings": state['user_profile']['current_savings']
    })


# Initialize the workflow
workflow = StateGraph(AgentState)
workflow.add_node("persona_builder", persona_builder_node)
workflow.add_node("calculator", calculation_node)

# Add edges and conditional routing
workflow.add_edge(START, "persona_builder")
workflow.add_edge("persona_builder", "calculator")

# Compile with memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# Example command to start the process
# await app.run_with_initial_state(AgentState(
#    messages=[],
#    user_profile=UserProfile(completed_persona=False),
#    calculations={},
#    search_results=[],
#    current_step='',
#    conversation_history=[],
#    session_id='test-session'
# ))
