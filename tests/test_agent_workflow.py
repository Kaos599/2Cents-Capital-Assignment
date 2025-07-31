"""
Test script to verify full workflow execution and state memory using real APIs
"""

import pytest
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Import agent workflow and state
from src.agents.workflow import app, persona_builder_node, calculation_node
from src.agents.state import AgentState, UserProfile


@pytest.mark.asyncio
async def test_real_api_workflow():
    """Test the full agent workflow with real API calls."""
    
    # 1. Initial State
    initial_state = AgentState(
        messages=[],
        user_profile=UserProfile(
            current_age=None, retirement_age=None, monthly_income=None,
            current_savings=None, monthly_savings=None, expected_return=None,
            risk_tolerance=None, goals=[], completed_persona=False
        ),
        calculations={},
        search_results=[],
        current_step='',
        conversation_history=[],
        session_id='real-test-session'
    )
    
    # 2. Run Persona Builder Node
    # This node is simplified, so we manually update the state for the test
    await persona_builder_node(initial_state)
    
    print("--- Persona Builder State ---")
    print(initial_state['user_profile'])
    
    assert initial_state['user_profile']['completed_persona'] is True
    assert initial_state['user_profile']['current_age'] == 30

    # 3. Run Calculation Node
    await calculation_node(initial_state)

    print("--- Calculation Node State ---")
    print(initial_state['calculations'])

    assert 'total_fund' in initial_state['calculations']
    assert initial_state['calculations']['total_fund'] > 0
    assert initial_state['calculations']['calculation_type'] == "retirement_timeline"

    # 4. Verify the entire app compilation and structure
    config = {"configurable": {"thread_id": "real-test-session"}}
    # We invoke with the already-processed state to check final output
    final_result = await app.ainvoke(initial_state, config=config)

    print("--- Final Workflow Result ---")
    print(final_result)

    # Final assertions on the output state
    assert 'user_profile' in final_result
    assert 'calculations' in final_result
    assert final_result['user_profile']['completed_persona'] is True
    assert final_result['calculations']['total_fund'] > 0

# To run this test: pytest tests/test_agent_workflow.py -v

