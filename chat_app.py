"""
Valura Financial Planning Agent with Chat Interface
"""

import streamlit as st
from datetime import datetime

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {
            "role": "assistant",
            "content": "Hi! I'm your AI Financial Planning Advisor. Let's build your retirement plan together!"
        }
    ]

# Chat container
chat_container = st.container()

# Chat message rendering
with chat_container:
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        st.chat_message(role).text(content)

# Chat input
user_input = st.chat_input(
    "Ask me about retirement planning, savings goals, or any financial question...",
    key="chat_input"
)

# Handle chat input
if user_input:
    # Add user input to messages
    st.session_state['messages'].append({
        "role": "user",
        "content": user_input
    })

    # Simulated response logic
    response = f"You asked about: {user_input}. Let's calculate that for you..."
    st.session_state['messages'].append({
        "role": "assistant",
        "content": response
    })
    
    # Refresh the chat container
    st.rerun()

# Display user profile in sidebar
with st.sidebar:
    st.header("👤 Your Profile")
    if 'user_profile' in st.session_state:
        profile = st.session_state['user_profile']
        st.metric("Age", profile.get("age", "Not set"))
        st.metric("Retirement Age", profile.get("retirement_age", "Not set"))
        st.metric("Monthly Savings", f"${profile.get('monthly_savings', 0):,.2f}")
    else:
        st.write("Complete your profile to see details here.")
