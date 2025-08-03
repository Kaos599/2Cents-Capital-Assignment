"""
Valura Financial Planning Agent - Complete Chat Interface
"""

import streamlit as st
import os
import sys
from datetime import datetime
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
sys.path.append(os.path.dirname(__file__))

# Import our financial tools and calculators
try:
    from src.calculators.financial_formulas import *
    from src.calculators.retirement_calculator import (
        calculate_retirement_timeline,
        calculate_savings_longevity, 
        calculate_required_monthly_savings,
        calculate_retirement_income_replacement,
        compare_investment_vs_debt_payoff,
        calculate_college_funding
    )
    from src.tools.financial_tools import *
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    st.error("Could not import financial modules. Please ensure all dependencies are installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Valura AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini LLM
@st.cache_resource
def initialize_llm():
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )
    except Exception as e:
        st.error(f"Failed to initialize Gemini API: {e}")
        return None

llm = initialize_llm()

# Persona building questions with defaults
PERSONA_QUESTIONS = [
    {
        "id": "age",
        "question": "What's your current age?",
        "type": "number",
        "min_value": 18,
        "max_value": 100,
        "default": 30,
        "validation": lambda x: 18 <= x <= 100,
        "quick_options": [25, 30, 35, 40, 45, 50],
        "mandatory": True
    },
    {
        "id": "retirement_age",
        "question": "At what age would you like to retire?",
        "type": "number",
        "min_value": 50,
        "max_value": 80,
        "default": 65,
        "validation": lambda x: x > st.session_state.get('user_profile', {}).get('age', 18),
        "quick_options": [60, 62, 65, 67, 70],
        "mandatory": True
    },
    {
        "id": "monthly_income",
        "question": "What's your current monthly income (after taxes)?",
        "type": "currency",
        "min_value": 0,
        "default": 5000,
        "validation": lambda x: x >= 0,
        "quick_options": [3000, 5000, 7500, 10000, 15000],
        "mandatory": True
    },
    {
        "id": "current_savings",
        "question": "How much do you currently have saved for retirement?",
        "type": "currency",
        "min_value": 0,
        "default": 10000,
        "validation": lambda x: x >= 0,
        "quick_options": [0, 5000, 10000, 25000, 50000, 100000],
        "mandatory": True
    },
    {
        "id": "monthly_savings",
        "question": "How much can you save per month for retirement?",
        "type": "currency",
        "min_value": 0,
        "default": 500,
        "validation": lambda x: x >= 0,
        "quick_options": [200, 500, 750, 1000, 1500, 2000],
        "mandatory": True
    },
    {
        "id": "expected_return",
        "question": "What annual return do you expect from your investments? (typical range: 4-10%)",
        "type": "percentage",
        "min_value": 0.0,
        "max_value": 20.0,
        "default": 7.0,
        "validation": lambda x: 0 <= x <= 20,
        "quick_options": [4.0, 6.0, 7.0, 8.0, 10.0],
        "mandatory": True
    },
    {
        "id": "risk_tolerance",
        "question": "What's your investment risk tolerance?",
        "type": "select",
        "options": ["Conservative", "Moderate", "Aggressive"],
        "default": "Moderate",
        "mandatory": False
    },
    {
        "id": "financial_goals",
        "question": "What are your main financial goals? (optional)",
        "type": "text",
        "default": "Comfortable retirement",
        "mandatory": False
    }
]

# High-Contrast Accessible Styling
def apply_chat_styling():
    st.markdown("""
    <style>
    /* Import Google Fonts for better typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global font fixes and high contrast styling */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: #f8fafc;
        min-height: 100vh;
        color: #1a202c;
    }
    
    /* Fix font rendering issues and ensure proper spacing */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
        letter-spacing: 0.025em;
        word-spacing: 0.1em;
    }
    
    /* Ensure proper text spacing in all elements */
    .stMarkdown p,
    .stMarkdown div,
    .stText,
    .stChatMessage {
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
        line-height: 1.6 !important;
    }
    
    /* Main container styling */
    .main .block-container {
        padding: 2rem;
        background: #ffffff;
        border-radius: 12px;
        margin: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        animation: slideIn 0.6s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Header styling with high contrast */
    h1 {
        color: #1a202c !important;
        text-align: center;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* All text elements high contrast with proper spacing */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stText {
        color: #1a202c !important;
        font-weight: 500;
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
        line-height: 1.6 !important;
    }
    
    /* Ensure main content area has proper text rendering */
    .main .stMarkdown,
    .main .stText,
    .main .element-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
    }
    
    /* Chat message styling with high contrast */
    .stChatMessage {
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        animation: messageSlide 0.4s ease-out;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    @keyframes messageSlide {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* User message styling - Dark background, white text */
    .stChatMessage[data-testid="user-message"] {
        background: #2d3748 !important;
        color: #ffffff !important;
        margin-left: 2rem;
        border: 1px solid #4a5568;
    }
    
    .stChatMessage[data-testid="user-message"] .stMarkdown,
    .stChatMessage[data-testid="user-message"] .stMarkdown p,
    .stChatMessage[data-testid="user-message"] .stMarkdown div {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Assistant message styling - Light background, dark text */
    .stChatMessage[data-testid="assistant-message"] {
        background: #f7fafc !important;
        color: #1a202c !important;
        margin-right: 2rem;
        border: 1px solid #cbd5e0;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stMarkdown,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown p,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown div {
        color: #1a202c !important;
        font-weight: 500;
    }
    
    /* Sidebar styling with high contrast - Multiple selectors for compatibility */
    .css-1d391kg,
    .stSidebar,
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        background: #2d3748 !important;
        border-radius: 0;
        color: #ffffff !important;
    }
    
    .sidebar .sidebar-content,
    .stSidebar .sidebar-content,
    [data-testid="stSidebar"] .sidebar-content {
        background: #2d3748 !important;
        color: #ffffff !important;
        padding: 1rem;
    }
    
    /* Force sidebar background color */
    .css-1d391kg > div,
    .stSidebar > div,
    [data-testid="stSidebar"] > div {
        background: #2d3748 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar text styling - Force white text for all sidebar elements */
    .css-1d391kg .stMarkdown,
    .css-1d391kg .stMarkdown p,
    .css-1d391kg .stMarkdown div,
    .css-1d391kg .stText,
    .css-1d391kg .stMetric,
    .css-1d391kg .stMetric .metric-value,
    .css-1d391kg .stMetric .metric-label,
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3,
    .css-1d391kg h4,
    .css-1d391kg h5,
    .css-1d391kg h6,
    .css-1d391kg span,
    .css-1d391kg div {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Additional sidebar selectors for different Streamlit versions */
    .stSidebar .stMarkdown,
    .stSidebar .stMarkdown p,
    .stSidebar .stMarkdown div,
    .stSidebar .stText,
    .stSidebar h1,
    .stSidebar h2,
    .stSidebar h3,
    .stSidebar h4,
    .stSidebar h5,
    .stSidebar h6,
    .stSidebar span,
    .stSidebar div {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Force white text for sidebar content - Multiple selectors for compatibility */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown div,
    [data-testid="stSidebar"] .stText,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-weight: 500;
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
    }
    
    /* Additional sidebar selectors for all possible elements */
    .css-1d391kg *,
    .stSidebar *,
    section[data-testid="stSidebar"] *,
    .sidebar-content * {
        color: #ffffff !important;
    }
    
    /* Specific targeting for sidebar text elements */
    .css-1d391kg .element-container,
    .css-1d391kg .stMarkdown,
    .stSidebar .element-container,
    .stSidebar .stMarkdown,
    [data-testid="stSidebar"] .element-container,
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Override any dark text in sidebar */
    .css-1d391kg .css-1v0mbdj,
    .stSidebar .css-1v0mbdj,
    [data-testid="stSidebar"] .css-1v0mbdj {
        color: #ffffff !important;
    }
    
    /* Remove floating chat button and any floating elements */
    .stChatFloatingInputContainer,
    [data-testid="stChatFloatingInputContainer"],
    .stFloatingContainer,
    [data-testid="stFloatingContainer"],
    .floating-chat-input,
    .chat-input-floating {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }
    
    /* Ensure no floating elements appear */
    .stApp > div:last-child {
        position: static !important;
    }
    
    /* Hide any potential floating chat widgets */
    div[data-testid*="floating"],
    div[class*="floating"],
    div[class*="Float"] {
        display: none !important;
    }
    
    /* Button styling with high contrast */
    .stButton > button {
        background: #2d3748 !important;
        color: #ffffff !important;
        border: 2px solid #4a5568;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        background: #4a5568 !important;
        border-color: #718096;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        background: #1a202c !important;
    }
    
    /* Input styling with high contrast */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #cbd5e0 !important;
        padding: 0.75rem 1rem;
        font-family: 'Inter', sans-serif !important;
        background: #ffffff !important;
        color: #1a202c !important;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #2d3748 !important;
        box-shadow: 0 0 0 3px rgba(45, 55, 72, 0.1) !important;
        outline: none;
    }
    
    /* Slider styling */
    .stSlider > div > div > div > div {
        background: #2d3748 !important;
    }
    
    .stSlider .stMarkdown {
        color: #1a202c !important;
        font-weight: 600;
    }
    
    /* Metric styling with high contrast */
    .metric-container {
        background: #ffffff !important;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2d3748;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Loading animation with high contrast */
    .thinking-indicator {
        display: inline-block;
        animation: pulse 1.5s ease-in-out infinite;
        background: #2d3748 !important;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #4a5568;
    }
    
    /* Ensure calculating text is visible with proper spacing */
    .thinking-indicator span,
    .thinking-indicator div {
        color: #ffffff !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        word-spacing: 0.15em !important;
    }
    
    /* Force visibility for any loading/calculating text */
    .stSpinner,
    .stProgress,
    .thinking-indicator,
    [data-testid="stSpinner"] {
        color: #ffffff !important;
        background: #2d3748 !important;
    }
    
    /* Ensure all text in thinking indicators is white */
    .thinking-indicator *,
    .stSpinner *,
    .stProgress * {
        color: #ffffff !important;
    }
    
    @keyframes pulse {
        0% {
            opacity: 0.8;
        }
        50% {
            opacity: 1;
        }
        100% {
            opacity: 0.8;
        }
    }
    
    /* Progress indicator with high contrast */
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
        border: 1px solid #cbd5e0;
    }
    
    .progress-fill {
        height: 100%;
        background: #2d3748;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Quick option buttons with high contrast */
    .quick-option-btn {
        background: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600;
    }
    
    .quick-option-btn:hover {
        background: #4a5568 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Profile completion indicator with high contrast */
    .profile-complete {
        background: #2d3748 !important;
        color: #ffffff !important;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #4a5568;
        animation: celebrationPulse 2s ease-in-out infinite;
    }
    
    @keyframes celebrationPulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
    }
    
    /* Chat input styling with high contrast */
    .stChatInputContainer {
        border-radius: 8px;
        background: #ffffff !important;
        border: 2px solid #cbd5e0 !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #2d3748 !important;
        box-shadow: 0 0 0 3px rgba(45, 55, 72, 0.1);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f7fafc;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2d3748;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4a5568;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            margin: 0.5rem;
            border-radius: 8px;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        .stChatMessage {
            margin: 0.5rem 0;
        }
        
        .stChatMessage[data-testid="user-message"] {
            margin-left: 0.5rem;
        }
        
        .stChatMessage[data-testid="assistant-message"] {
            margin-right: 0.5rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom tooltip with high contrast */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #1a202c;
        color: #ffffff;
        text-align: center;
        border-radius: 8px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        border: 1px solid #2d3748;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Fix any remaining text visibility issues with proper spacing */
    .stApp .stMarkdown h1,
    .stApp .stMarkdown h2,
    .stApp .stMarkdown h3,
    .stApp .stMarkdown h4,
    .stApp .stMarkdown h5,
    .stApp .stMarkdown h6 {
        color: #1a202c !important;
        font-weight: 700;
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
    }
    
    .stApp .stMarkdown p,
    .stApp .stMarkdown div,
    .stApp .stMarkdown span,
    .stApp .stText {
        color: #1a202c !important;
        font-weight: 500;
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
        line-height: 1.6 !important;
    }
    
    /* Ensure metric values are visible with proper spacing */
    .stMetric > div {
        color: #1a202c !important;
        letter-spacing: 0.025em !important;
    }
    
    .stMetric .metric-value {
        color: #1a202c !important;
        font-weight: 700;
        letter-spacing: 0.025em !important;
    }
    
    .stMetric .metric-label {
        color: #4a5568 !important;
        font-weight: 500;
        letter-spacing: 0.025em !important;
    }
    
    /* Fix text rendering in chat messages */
    .stChatMessage .stMarkdown,
    .stChatMessage .stMarkdown p,
    .stChatMessage .stMarkdown div {
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
        line-height: 1.6 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    /* Ensure proper text rendering in all containers */
    .element-container,
    .stMarkdown,
    .stText,
    .stChatMessage {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
        letter-spacing: 0.025em !important;
        word-spacing: 0.1em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your AI Financial Planning Advisor. I'll help you create a personalized retirement plan. Let's start by getting to know you better!",
                "timestamp": datetime.now()
            }
        ]
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    
    if 'conversation_phase' not in st.session_state:
        st.session_state.conversation_phase = 'persona_building'
    
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    if 'calculation_history' not in st.session_state:
        st.session_state.calculation_history = []

# Question classification using Gemini
def classify_user_question(question: str) -> str:
    if not llm:
        return "GENERAL"
    
    try:
        classification_prompt = f"""
        Classify this financial question into ONE category:
        
        1. PERSONA - Questions about changing profile info
        2. CALCULATION - Questions requiring financial calculations
        3. SCENARIO - What-if questions or comparisons
        4. EXPLANATION - Asking for details about calculations
        5. ADVICE - General financial advice questions
        6. SKIP - User wants to skip current question
        7. GENERAL - Other questions
        
        Question: "{question}"
        
        Return only the category name.
        """
        
        response = llm.invoke(classification_prompt)
        return response.content.strip().upper()
    except Exception as e:
        st.error(f"Error classifying question: {e}")
        return "GENERAL"

# Enhanced thinking indicator with animations
def show_thinking_indicator(message="Calculating..."):
    thinking_placeholder = st.empty()
    
    # Create high-contrast animated thinking indicator
    thinking_html = f"""
    <div class="thinking-indicator" style="
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        background: #2d3748;
        border: 2px solid #4a5568;
        border-radius: 8px;
        color: #ffffff;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        animation: pulse 1.5s ease-in-out infinite;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        ">
            <div style="
                width: 8px;
                height: 8px;
                background: #ffffff;
                border-radius: 50%;
                animation: bounce 1.4s ease-in-out infinite both;
            "></div>
            <div style="
                width: 8px;
                height: 8px;
                background: #ffffff;
                border-radius: 50%;
                animation: bounce 1.4s ease-in-out 0.2s infinite both;
            "></div>
            <div style="
                width: 8px;
                height: 8px;
                background: #ffffff;
                border-radius: 50%;
                animation: bounce 1.4s ease-in-out 0.4s infinite both;
            "></div>
            <span style="margin-left: 0.5rem; color: #ffffff; font-weight: 600;">{message}</span>
        </div>
    </div>
    
    <style>
    @keyframes bounce {{
        0%, 80%, 100% {{
            transform: scale(0);
        }}
        40% {{
            transform: scale(1);
        }}
    }}
    </style>
    """
    
    thinking_placeholder.markdown(thinking_html, unsafe_allow_html=True)
    time.sleep(2)  # Show for 2 seconds
    thinking_placeholder.empty()

# Enhanced AI response with calculation integration
def generate_ai_response_with_calculations(user_input: str, context: dict) -> str:
    """Generate AI response and perform calculations when needed"""
    profile = context.get('user_profile', {})
    
    # Check if this is a financial calculation question
    financial_keywords = [
        'how long', 'last', 'withdraw', 'take out', 'what if', 'save more', 
        'increase', 'scenario', 'need to save', 'required', 'target', 'goal',
        'explain', 'calculation', 'breakdown', 'formula'
    ]
    
    is_financial_question = any(keyword in user_input.lower() for keyword in financial_keywords)
    
    if is_financial_question:
        # Use dynamic financial calculation handler
        calculation_response = handle_dynamic_financial_question(user_input, profile)
        
        # Enhance with AI commentary if needed
        if not llm:
            return calculation_response
        
        try:
            enhancement_prompt = f"""
            You are a professional financial advisor. A calculation has been performed for the user.
            
            User question: "{user_input}"
            Calculation result: "{calculation_response}"
            User profile: {json.dumps(profile, indent=2)}
            
            Provide a brief, encouraging commentary to accompany this calculation result. 
            Focus on:
            1. Interpretation of the results
            2. Practical advice
            3. Next steps or considerations
            4. Encouragement and support
            
            Keep it concise (2-3 sentences) and professional but warm.
            Do not repeat the calculation numbers - just provide context and advice.
            """
            
            ai_commentary = llm.invoke(enhancement_prompt)
            
            return f"{calculation_response}\n\n💡 {ai_commentary.content}"
            
        except Exception:
            # If AI enhancement fails, just return the calculation
            return calculation_response
    
    else:
        # Use regular AI response for general questions
        return generate_ai_response(user_input, context)

# Simple AI response for general questions
def generate_ai_response(user_input: str, context: dict) -> str:
    if not llm:
        return "I'm having trouble connecting to my AI brain right now. Please try again later."
    
    try:
        system_prompt = f"""
        You are a professional financial advisor helping users plan for retirement.
        
        Current context:
        - User profile so far: {json.dumps(context.get('user_profile', {}), indent=2)}
        - Conversation phase: {context.get('conversation_phase', 'unknown')}
        - Recent calculations: {context.get('recent_calculations', 'none')}
        
        Respond in a friendly, professional manner. Keep responses concise but helpful.
        """
        
        user_message = f"User input: {user_input}"
        
        response = llm.invoke(f"{system_prompt}\n\n{user_message}")
        return response.content
    except Exception as e:
        return f"I encountered an error: {str(e)}. Let's continue with your financial planning."

# Persona building functions
def get_current_question():
    if st.session_state.current_question_index < len(PERSONA_QUESTIONS):
        return PERSONA_QUESTIONS[st.session_state.current_question_index]
    return None

def show_progress_indicator():
    """Show progress indicator for persona building"""
    current_index = st.session_state.current_question_index
    total_questions = len(PERSONA_QUESTIONS)
    progress_percentage = (current_index / total_questions) * 100
    
    progress_html = f"""
    <div style="margin: 1rem 0;">
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            color: #667eea;
        ">
            <span>Profile Completion</span>
            <span>{current_index}/{total_questions} questions</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_percentage}%;"></div>
        </div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)

def render_question_input(question):
    question_id = str(question['id'])
    
    # Create two columns for slider and manual input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if question['type'] == 'currency':
            slider_value = st.slider(
                f"Use slider for {question['question']}",
                min_value=float(question.get('min_value', 0)),
                max_value=float(question.get('max_value', 200000)),
                value=float(question['default']),
                step=100.0,
                key=f"slider_{question_id}",
                format="$%.0f"
            )
        elif question['type'] == 'number':
            slider_value = st.slider(
                f"Use slider for {question['question']}",
                min_value=int(question.get('min_value', 0)),
                max_value=int(question.get('max_value', 100)),
                value=int(question['default']),
                key=f"slider_{question_id}"
            )
        elif question['type'] == 'percentage':
            slider_value = st.slider(
                f"Use slider for {question['question']}",
                min_value=float(question.get('min_value', 0.0)),
                max_value=float(question.get('max_value', 20.0)),
                value=float(question['default']),
                step=0.1,
                key=f"slider_{question_id}",
                format="%.1f%%"
            )
        elif question['type'] == 'select':
            slider_value = st.selectbox(
                question['question'], 
                question['options'], 
                index=question['options'].index(question['default']), 
                key=f"select_{question_id}"
            )
        else:
            slider_value = st.text_input(
                question['question'], 
                value=question['default'], 
                key=f"text_{question_id}"
            )
    
    with col2:
        if question['type'] in ['currency', 'number', 'percentage']:
            if question['type'] == 'currency':
                manual_value = st.number_input(
                    "Or enter manually:",
                    min_value=float(question.get('min_value', 0)),
                    max_value=float(question.get('max_value', 1000000)),
                    value=slider_value,
                    step=100.0,
                    key=f"manual_{question_id}",
                    format="%.0f"
                )
            elif question['type'] == 'number':
                manual_value = st.number_input(
                    "Or enter manually:",
                    min_value=int(question.get('min_value', 0)),
                    max_value=int(question.get('max_value', 100)),
                    value=slider_value,
                    key=f"manual_{question_id}"
                )
            elif question['type'] == 'percentage':
                manual_value = st.number_input(
                    "Or enter manually:",
                    min_value=float(question.get('min_value', 0.0)),
                    max_value=float(question.get('max_value', 20.0)),
                    value=slider_value,
                    step=0.1,
                    key=f"manual_{question_id}",
                    format="%.1f"
                )
            
            # Use manual value if it's different from slider
            final_value = manual_value
        else:
            final_value = slider_value
    
    # Submit button
    if st.button("Submit Answer", key=f"submit_{question_id}", type="primary"):
        st.session_state.user_profile[question['id']] = final_value
        st.session_state.current_question_index += 1
        
        # Format the response based on type
        if question['type'] == 'currency':
            formatted_value = f"${final_value:,.0f}"
        elif question['type'] == 'percentage':
            formatted_value = f"{final_value}%"
        else:
            formatted_value = str(final_value)
            
        add_message("user", formatted_value)
        add_message("assistant", f"✅ Got it! {question['id'].replace('_', ' ').title()}: {formatted_value}")
        next_question_or_complete()
        st.rerun()

def add_message(role: str, content: str, metadata=None):
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    }
    if metadata:
        message["metadata"] = metadata
    
    st.session_state.messages.append(message)

def show_achievement_notification(achievement_type: str, details: dict):
    """Show achievement notifications for financial milestones"""
    achievements = {
        "profile_complete": {
            "icon": "🎉",
            "title": "Profile Complete!",
            "message": "Great job completing your financial profile!"
        },
        "first_calculation": {
            "icon": "📊",
            "title": "First Calculation Done!",
            "message": "You've completed your first retirement analysis!"
        },
        "scenario_explorer": {
            "icon": "🔍",
            "title": "Scenario Explorer!",
            "message": "You're exploring different financial scenarios - excellent planning!"
        },
        "comprehensive_planner": {
            "icon": "🏆",
            "title": "Comprehensive Planner!",
            "message": "You've explored multiple aspects of financial planning!"
        }
    }
    
    if achievement_type in achievements:
        achievement = achievements[achievement_type]
        
        notification_html = f"""
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(17, 153, 142, 0.4);
            z-index: 1000;
            animation: slideInRight 0.5s ease-out, fadeOut 0.5s ease-in 4.5s forwards;
            max-width: 300px;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">
                <span style="font-size: 1.5rem;">{achievement['icon']}</span>
                <span>{achievement['title']}</span>
            </div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                {achievement['message']}
            </div>
        </div>
        
        <style>
        @keyframes slideInRight {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        @keyframes fadeOut {{
            from {{
                opacity: 1;
            }}
            to {{
                opacity: 0;
                transform: translateX(100%);
            }}
        }}
        </style>
        """
        
        # Use a placeholder to show the notification
        notification_placeholder = st.empty()
        notification_placeholder.markdown(notification_html, unsafe_allow_html=True)
        
        # Clear after 5 seconds (handled by CSS animation)

def next_question_or_complete():
    current_q = get_current_question()
    if current_q:
        # Ask next question
        question_text = f"📝 {current_q['question']}"
        if not current_q['mandatory']:
            question_text += " (optional - you can skip this)"
        
        add_message("assistant", question_text)
    else:
        # Profile complete
        st.session_state.conversation_phase = 'profile_complete'
        add_message("assistant", "🎉 Great! I have all the information I need. Let me analyze your financial situation and create your retirement plan...")
        
        # Show achievement notification
        show_achievement_notification("profile_complete", {})
        
        # Run initial calculation
        run_retirement_calculation()

def run_retirement_calculation():
    try:
        profile = st.session_state.user_profile
        
        # Run calculation using our financial tools
        result = calculate_retirement_timeline(
            current_age=profile.get('age', 30),
            retirement_age=profile.get('retirement_age', 65),
            monthly_savings=profile.get('monthly_savings', 500),
            expected_return=profile.get('expected_return', 7.0),
            current_savings=profile.get('current_savings', 10000)
        )
        
        # Store calculation
        st.session_state.calculation_history.append({
            "type": "retirement_timeline",
            "result": result,
            "timestamp": datetime.now()
        })
        
        # Format response
        total_fund = result['total_fund']
        years_to_retirement = result['years_to_retirement']
        real_value = result['real_purchasing_power']
        
        response = f"""📊 Your Retirement Plan Analysis:

🎯 Projected Retirement Fund: ${total_fund:,.0f}
⏰ Years to Retirement: {years_to_retirement} years  
💰 Inflation-Adjusted Value: ${real_value:,.0f}

Based on your profile:
• Monthly savings: ${profile.get('monthly_savings', 0):,}
• Expected return: {profile.get('expected_return', 0)}%
• Current savings: ${profile.get('current_savings', 0):,}

💡 What would you like to explore next?
• Ask "What if I save more?" for scenarios
• Ask "How long will my money last?" for withdrawal planning  
• Ask "Explain the calculation" for detailed breakdown"""
        
        add_message("assistant", response)
        st.session_state.conversation_phase = 'interactive'
        
    except Exception as e:
        add_message("assistant", f"I had trouble running the calculation. Error: {str(e)}. Let's try again or ask me something else!")

def extract_financial_parameters(user_input: str) -> dict:
    """Extract financial parameters from user input using regex"""
    import re
    
    params = {}
    
    # Extract dollar amounts
    dollar_matches = re.findall(r'\$([0-9,]+(?:\.[0-9]+)?)', user_input)
    number_matches = re.findall(r'([0-9,]+(?:\.[0-9]+)?)', user_input)
    
    if dollar_matches:
        params['amount'] = float(dollar_matches[0].replace(',', ''))
    elif number_matches:
        # Try to determine if it's a dollar amount from context
        for match in number_matches:
            value = float(match.replace(',', ''))
            if 'save' in user_input.lower() or 'withdraw' in user_input.lower():
                params['amount'] = value
                break
    
    # Extract percentages - handle both % and standalone numbers for returns
    percent_matches = re.findall(r'([0-9]+(?:\.[0-9]+)?)%', user_input)
    if percent_matches:
        params['percentage'] = float(percent_matches[0])
    elif any(word in user_input.lower() for word in ['return', 'returns', 'rate']):
        # Look for standalone numbers that might be return rates
        standalone_numbers = re.findall(r'\b([0-9]+(?:\.[0-9]+)?)\b', user_input)
        for num in standalone_numbers:
            value = float(num)
            if 0 < value <= 30:  # Reasonable return rate range
                params['return_rate'] = value
                break
    
    # Extract years
    year_matches = re.findall(r'([0-9]+)\s*years?', user_input.lower())
    if year_matches:
        params['years'] = int(year_matches[0])
    
    return params

def handle_dynamic_financial_question(user_input: str, profile: dict) -> str:
    """Handle financial questions dynamically with proper calculations"""
    
    # Extract parameters from user input
    params = extract_financial_parameters(user_input)
    user_lower = user_input.lower()
    
    try:
        # Determine question type and perform calculation
        if any(phrase in user_lower for phrase in ['return', 'returns', 'rate']) and ('return_rate' in params or 'percentage' in params):
            # Return rate scenario analysis
            new_return = params.get('return_rate', params.get('percentage', 7.0))
            current_return = profile.get('expected_return', 7.0)
            
            # Calculate scenario with new return rate
            scenario_result = calculate_retirement_timeline(
                current_age=profile.get('age', 30),
                retirement_age=profile.get('retirement_age', 65),
                monthly_savings=profile.get('monthly_savings', 500),
                expected_return=new_return,
                current_savings=profile.get('current_savings', 10000)
            )
            
            # Get original calculation for comparison
            original_fund = 0
            if st.session_state.calculation_history:
                for calc in reversed(st.session_state.calculation_history):
                    if calc['type'] == 'retirement_timeline':
                        original_fund = calc['result']['total_fund']
                        break
            
            # If no original calculation, calculate it now
            if original_fund == 0:
                original_result = calculate_retirement_timeline(
                    current_age=profile.get('age', 30),
                    retirement_age=profile.get('retirement_age', 65),
                    monthly_savings=profile.get('monthly_savings', 500),
                    expected_return=current_return,
                    current_savings=profile.get('current_savings', 10000)
                )
                original_fund = original_result['total_fund']
            
            new_fund = scenario_result['total_fund']
            difference = new_fund - original_fund
            change_percent = (difference / original_fund * 100) if original_fund > 0 else 0
            
            # Store the calculation
            st.session_state.calculation_history.append({
                "type": "return_rate_scenario",
                "result": scenario_result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            return f"""📈 Return Rate Scenario Analysis: {current_return}% → {new_return}%

💰 New Retirement Fund: ${new_fund:,.0f}
📊 Change from Original: ${difference:,.0f} ({change_percent:+.1f}%)
⏰ Years to Retirement: {scenario_result['years_to_retirement']}

🎯 Impact of {new_return - current_return:+.1f}% return change: ${difference:,.0f}
💡 Higher returns significantly impact long-term growth due to compound interest!

📋 Calculation Details:
• Current Savings Growth: ${scenario_result['calculation_details']['fv_current_savings']:,.0f}
• Monthly Contributions Growth: ${scenario_result['calculation_details']['fv_monthly_contributions']:,.0f}"""

        elif any(phrase in user_lower for phrase in ['how long', 'last', 'withdraw', 'take out']):
            # Withdrawal longevity question - Fixed to get correct retirement fund
            retirement_fund = profile.get('current_savings', 100000)
            
            # Get the most recent retirement calculation for accurate fund amount
            if st.session_state.calculation_history:
                for calc in reversed(st.session_state.calculation_history):
                    if calc['type'] in ['retirement_timeline', 'scenario_analysis']:
                        if 'total_fund' in calc['result']:
                            retirement_fund = calc['result']['total_fund']
                            break
            
            # If no specific amount mentioned, use 4% rule
            withdrawal_amount = params.get('amount', retirement_fund * 0.04 / 12)
            
            result = calculate_savings_longevity(
                retirement_fund=retirement_fund,
                monthly_withdrawal=withdrawal_amount,
                expected_return=4.0  # Conservative retirement return
            )
            
            if 'error' in result:
                return f"I had trouble with that calculation: {result['error']}"
            
            # Store the calculation
            st.session_state.calculation_history.append({
                "type": "savings_longevity",
                "result": result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            if result['sustainable']:
                duration_text = "✅ Sustainable indefinitely!"
                explanation = "Your withdrawal amount is within safe limits."
            else:
                years = result.get('years_lasting', 0)
                months = result.get('months_lasting', 0)
                duration_text = f"⏰ Duration: {years:.1f} years ({months:.0f} months)"
                explanation = "⚠️ Limited duration - consider reducing withdrawal amount."
            
            four_percent = result.get('four_percent_rule_monthly', retirement_fund * 0.04 / 12)
            withdrawal_ratio = result.get('withdrawal_vs_four_percent', withdrawal_amount / four_percent)
            
            return f"""📉 Withdrawal Analysis for ${withdrawal_amount:,.0f}/month:

💰 Retirement Fund: ${retirement_fund:,.0f}
📊 Monthly Withdrawal: ${withdrawal_amount:,.0f}
{duration_text}

{explanation}

💡 4% Rule Reference: ${four_percent:,.0f} per month is considered safe
📈 Your withdrawal is {withdrawal_ratio:.1f}x the 4% rule"""

        elif any(phrase in user_lower for phrase in ['what if', 'save more', 'increase', 'scenario']):
            # Scenario analysis - Fixed calculation logic
            current_monthly = profile.get('monthly_savings', 500)
            
            # Parse the increase amount from user input
            if 'amount' in params:
                # Check if user said "save $X more" vs "save $X total"
                if any(word in user_lower for word in ['more', 'additional', 'extra', 'increase']):
                    new_monthly = current_monthly + params['amount']
                else:
                    new_monthly = params['amount']
            elif 'percentage' in params:
                new_monthly = current_monthly * (1 + params['percentage'] / 100)
            else:
                new_monthly = current_monthly * 1.2  # Default 20% increase
            
            # Calculate new scenario
            scenario_result = calculate_retirement_timeline(
                current_age=profile.get('age', 30),
                retirement_age=profile.get('retirement_age', 65),
                monthly_savings=new_monthly,
                expected_return=profile.get('expected_return', 7.0),
                current_savings=profile.get('current_savings', 10000)
            )
            
            # Get original calculation for comparison
            original_fund = 0
            if st.session_state.calculation_history:
                # Find the most recent retirement timeline calculation
                for calc in reversed(st.session_state.calculation_history):
                    if calc['type'] == 'retirement_timeline':
                        original_fund = calc['result']['total_fund']
                        break
            
            # If no original calculation, calculate it now
            if original_fund == 0:
                original_result = calculate_retirement_timeline(
                    current_age=profile.get('age', 30),
                    retirement_age=profile.get('retirement_age', 65),
                    monthly_savings=current_monthly,
                    expected_return=profile.get('expected_return', 7.0),
                    current_savings=profile.get('current_savings', 10000)
                )
                original_fund = original_result['total_fund']
            
            new_fund = scenario_result['total_fund']
            difference = new_fund - original_fund
            increase_percent = (difference / original_fund * 100) if original_fund > 0 else 0
            
            # Store the calculation
            st.session_state.calculation_history.append({
                "type": "scenario_analysis",
                "result": scenario_result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            # Format the response properly
            change_amount = new_monthly - current_monthly
            change_sign = "+" if change_amount >= 0 else ""
            
            return f"""🔄 Scenario Analysis: Monthly savings ${current_monthly:,.0f} → ${new_monthly:,.0f}

📈 New Monthly Savings: ${new_monthly:,.0f} ({change_sign}${change_amount:,.0f})
💰 New Retirement Fund: ${new_fund:,.0f}
📊 Additional Money: ${difference:,.0f} ({increase_percent:+.1f}% change)

🎯 That's ${difference:,.0f} {'more' if difference > 0 else 'less'} for retirement!
💡 Each extra $100 per month adds approximately ${(difference / max(abs(change_amount), 1)) * 100:,.0f} to your retirement fund."""

        elif any(phrase in user_lower for phrase in ['need to save', 'required', 'target', 'goal']):
            # Required savings calculation
            target_amount = params.get('amount', 1000000)  # Default $1M target
            
            result = calculate_required_monthly_savings(
                current_age=profile.get('age', 30),
                retirement_age=profile.get('retirement_age', 65),
                target_amount=target_amount,
                current_savings=profile.get('current_savings', 10000),
                expected_return=profile.get('expected_return', 7.0)
            )
            
            # Store the calculation
            st.session_state.calculation_history.append({
                "type": "required_savings",
                "result": result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            if result['already_sufficient']:
                return f"""🎉 Great news! Your current savings are already sufficient!

🎯 Target Amount: ${target_amount:,.0f}
💰 Current Savings Future Value: ${result['fv_current_savings']:,.0f}
✅ You're already on track to exceed your goal!

💡 Consider increasing your target or exploring other financial goals."""
            else:
                current_monthly = profile.get('monthly_savings', 0)
                required_monthly = result['required_monthly_savings']
                difference = required_monthly - current_monthly
                
                return f"""📊 Required Savings Analysis for ${target_amount:,.0f} goal:

🎯 Target Amount: ${target_amount:,.0f}
💰 Current Monthly Savings: ${current_monthly:,.0f}
📈 Required Monthly Savings: ${required_monthly:,.0f}
📊 Additional Needed: ${difference:,.0f}/month

⏰ Years to Retirement: {result['years_to_retirement']}
💡 Your current savings will grow to: ${result['fv_current_savings']:,.0f}"""

        elif any(phrase in user_lower for phrase in ['emergency fund', 'emergency', 'rainy day']):
            # Emergency fund calculation
            monthly_income = profile.get('monthly_income', 5000)
            # Assume 70% of income goes to expenses
            monthly_expenses = monthly_income * 0.7
            target_months = params.get('months', 6)
            
            from src.calculators.retirement_calculator import calculate_emergency_fund
            
            result = calculate_emergency_fund(
                monthly_expenses=monthly_expenses,
                target_months=target_months,
                current_emergency_fund=params.get('amount', 0),
                monthly_savings_capacity=profile.get('monthly_savings', 500) * 0.3  # 30% of retirement savings
            )
            
            st.session_state.calculation_history.append({
                "type": "emergency_fund",
                "result": result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            if result['already_sufficient']:
                return f"""🎉 Your emergency fund is already sufficient!

🎯 Target Amount: ${result['target_amount']:,.0f} ({target_months} months of expenses)
💰 Current Amount: ${result['current_amount']:,.0f}
✅ You're fully prepared for emergencies!

💡 Consider investing excess emergency funds in higher-yield accounts."""
            else:
                timeline_text = ""
                if result['years_to_target']:
                    timeline_text = f"⏰ Time to Target: {result['years_to_target']:.1f} years"
                
                return f"""🚨 Emergency Fund Analysis:

🎯 Target Amount: ${result['target_amount']:,.0f} ({target_months} months of expenses)
💰 Current Amount: ${result['current_amount']:,.0f}
📊 Shortfall: ${result['shortfall']:,.0f}
💵 Monthly Expenses: ${result['monthly_expenses']:,.0f}
{timeline_text}

💡 Start with $1,000 as a mini emergency fund, then build to your full target."""

        elif any(phrase in user_lower for phrase in ['buy vs rent', 'mortgage', 'house', 'home']):
            # Mortgage vs rent analysis
            home_price = params.get('amount', 400000)  # Default home price
            
            from src.calculators.retirement_calculator import calculate_mortgage_vs_rent
            
            result = calculate_mortgage_vs_rent(
                home_price=home_price,
                down_payment_percent=20,
                mortgage_rate=6.5,
                mortgage_years=30,
                monthly_rent=2000,  # Estimated rent
                property_tax_annual=home_price * 0.012,  # 1.2% property tax
                insurance_annual=1200
            )
            
            st.session_state.calculation_history.append({
                "type": "mortgage_vs_rent",
                "result": result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            recommendation = "🏠 Buying" if result['recommendation'] == 'buy' else "🏠 Renting"
            
            return f"""🏠 Buy vs Rent Analysis for ${home_price:,.0f} home:

💰 Down Payment: ${result['down_payment']:,.0f}
🏠 Monthly Mortgage + Costs: ${result['total_monthly_ownership']:,.0f}
🏢 Monthly Rent: ${result['monthly_rent']:,.0f}
📊 Monthly Difference: ${abs(result['monthly_difference']):,.0f}

After {result['mortgage_years']} years:
🏠 Home Equity: ${result['home_equity']:,.0f}
📈 Investment Value (renting): ${result['investment_value']:,.0f}

{recommendation} appears better by ${result['difference']:,.0f}

💡 This assumes {result['mortgage_years']}-year timeline and doesn't include tax benefits."""

        elif any(phrase in user_lower for phrase in ['debt', 'pay off', 'payoff', 'credit card', 'loan']):
            # Debt payoff vs investment analysis
            debt_amount = params.get('amount', 10000)  # Default debt amount
            debt_rate = 18.0  # Default credit card rate
            investment_rate = profile.get('expected_return', 7.0)
            monthly_available = profile.get('monthly_savings', 500)
            
            from src.calculators.retirement_calculator import compare_investment_vs_debt_payoff
            
            result = compare_investment_vs_debt_payoff(
                debt_amount=debt_amount,
                debt_interest_rate=debt_rate,
                investment_return_rate=investment_rate,
                time_horizon_years=10,
                monthly_available=monthly_available
            )
            
            st.session_state.calculation_history.append({
                "type": "debt_vs_investment",
                "result": result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            recommendation = "💳 Pay off debt first" if result['recommendation'] == 'payoff_first' else "📈 Invest while paying minimums"
            
            return f"""💳 Debt Payoff vs Investment Analysis:

💰 Debt Amount: ${debt_amount:,.0f} at {debt_rate}%
📈 Investment Return: {investment_rate}%
💵 Monthly Available: ${monthly_available:,.0f}

📊 Pay Debt First Strategy:
• Years to payoff: {result['payoff_first_scenario']['years_to_payoff']:.1f}
• Investment after payoff: ${result['payoff_first_scenario']['investment_value']:,.0f}
• Net worth: ${result['payoff_first_scenario']['net_worth']:,.0f}

📈 Invest While Paying Minimums:
• Investment value: ${result['invest_with_debt_scenario']['investment_value']:,.0f}
• Remaining debt: ${result['invest_with_debt_scenario']['remaining_debt']:,.0f}
• Net worth: ${result['invest_with_debt_scenario']['net_worth']:,.0f}

{recommendation} by ${result['difference']:,.0f}

💡 Generally, pay off high-interest debt (>7%) before investing."""

        elif any(phrase in user_lower for phrase in ['college', 'education', '529', 'tuition']):
            # College funding calculation
            current_cost = params.get('amount', 50000)  # Default annual cost
            years_until = params.get('years', 18)  # Default years until needed
            monthly_capacity = profile.get('monthly_savings', 500) * 0.3  # 30% of savings
            
            from src.calculators.retirement_calculator import calculate_college_funding
            
            result = calculate_college_funding(
                current_cost=current_cost,
                years_until_needed=years_until,
                education_inflation_rate=5.0,  # Higher than general inflation
                expected_return=profile.get('expected_return', 7.0),
                monthly_savings_capacity=monthly_capacity
            )
            
            st.session_state.calculation_history.append({
                "type": "college_funding",
                "result": result,
                "timestamp": datetime.now(),
                "user_question": user_input
            })
            
            if result['shortfall'] > 0:
                shortfall_text = f"📊 Shortfall: ${result['shortfall']:,.0f}"
                advice = "💡 Consider increasing monthly savings or exploring financial aid options."
            else:
                shortfall_text = "✅ Fully funded!"
                advice = "🎉 You're on track to fully fund education costs!"
            
            return f"""🎓 College Funding Analysis:

📚 Current Annual Cost: ${result['current_cost']:,.0f}
📈 Future Cost (with 5% inflation): ${result['future_cost']:,.0f}
⏰ Years Until Needed: {result['years_until_needed']}
💰 Monthly Savings: ${result['monthly_savings_capacity']:,.0f}

📊 Projected Savings: ${result['projected_savings']:,.0f}
{shortfall_text}

{advice}

💡 Consider 529 plans for tax-advantaged education savings."""

        elif any(phrase in user_lower for phrase in ['tax', 'taxes', 'deduction', 'ira', 'roth', '401k']):
            # Tax-advantaged savings analysis
            current_income = profile.get('monthly_income', 5000) * 12
            current_savings = profile.get('monthly_savings', 500) * 12
            tax_bracket = 0.22  # Assume 22% tax bracket
            
            # Traditional vs Roth comparison
            traditional_benefit = current_savings * tax_bracket
            roth_future_benefit = current_savings * 0.15  # Estimated future tax savings
            
            return f"""💰 Tax-Advantaged Savings Analysis:

📊 Annual Income: ${current_income:,.0f}
💰 Annual Retirement Savings: ${current_savings:,.0f}
📈 Estimated Tax Bracket: {tax_bracket*100:.0f}%

🏛️ Traditional 401(k)/IRA Benefits:
• Immediate tax deduction: ${traditional_benefit:,.0f}
• Reduces current taxable income
• Pay taxes in retirement

🌟 Roth 401(k)/IRA Benefits:
• No immediate deduction
• Tax-free growth and withdrawals
• Estimated future tax savings: ${roth_future_benefit:,.0f}/year

💡 Recommendations:
• If in high tax bracket now: Consider Traditional
• If expecting higher taxes later: Consider Roth
• Diversify with both if possible
• Maximize employer 401(k) match first

🎯 2024 Contribution Limits:
• 401(k): $23,000 ($30,500 if 50+)
• IRA: $7,000 ($8,000 if 50+)"""

        elif any(phrase in user_lower for phrase in ['insurance', 'life insurance', 'disability', 'health']):
            # Insurance needs analysis
            annual_income = profile.get('monthly_income', 5000) * 12
            life_insurance_need = annual_income * 10  # 10x income rule
            disability_coverage = annual_income * 0.6  # 60% income replacement
            
            return f"""🛡️ Insurance Needs Analysis:

💰 Annual Income: ${annual_income:,.0f}

👨‍👩‍👧‍👦 Life Insurance:
• Recommended coverage: ${life_insurance_need:,.0f}
• Rule of thumb: 10x annual income
• Consider term life for affordability
• Adjust for debts, dependents, and goals

🏥 Disability Insurance:
• Recommended coverage: ${disability_coverage:,.0f}/year
• Replaces 60-70% of income if unable to work
• Check employer benefits first
• Consider both short-term and long-term

🏥 Health Insurance:
• Essential for financial protection
• Consider HSA if eligible (triple tax advantage)
• Emergency fund should cover deductibles

💡 Insurance Priority Order:
1. Health insurance (essential)
2. Disability insurance (protect income)
3. Life insurance (if dependents)
4. Property insurance (home/auto)"""

        else:
            # General explanation or advice
            if st.session_state.calculation_history:
                latest_calc = st.session_state.calculation_history[-1]
                result = latest_calc['result']
                
                if latest_calc['type'] == 'retirement_timeline':
                    return f"""🧮 Calculation Breakdown:

Formula Used: Future Value of Annuity + Future Value of Lump Sum

📈 Your Current Savings Growth:
• Current amount: ${profile.get('current_savings', 0):,}
• Future value: ${result['calculation_details']['fv_current_savings']:,.0f}
• Formula: FV = PV × (1 + r)^n

💰 Your Monthly Contributions Growth:
• Monthly amount: ${profile.get('monthly_savings', 0):,}
• Future value: ${result['calculation_details']['fv_monthly_contributions']:,.0f}
• Formula: FV = PMT × [(1 + r)^n - 1] / r

🎯 Total = ${result['total_fund']:,.0f}

Where: r = {profile.get('expected_return', 0)}% annual return, n = {result['years_to_retirement']} years"""
            
            return "I'd be happy to help with your financial planning! You can ask me about:\n• Withdrawal planning ('How long will my money last if I take out $3,000?')\n• Savings scenarios ('What if I save $200 more per month?')\n• Target planning ('How much do I need to save for $1 million?')\n• Emergency funds ('Do I have enough emergency savings?')\n• Explanations of calculations"
    
    except Exception as e:
        # More specific error handling
        error_msg = str(e)
        if 'total_fund' in error_msg:
            return "I need to run your initial retirement calculation first. Let me do that now and then we can explore scenarios!"
        elif 'KeyError' in error_msg:
            return "I'm missing some information from your profile. Could you try asking your question differently or provide more details?"
        else:
            return f"I encountered an error with that calculation: {error_msg}. Could you try rephrasing your question?"

# Main app
def main():
    apply_chat_styling()
    initialize_session_state()
    
    # Header with high contrast styling
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="
            color: #1a202c;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            animation: fadeInDown 0.8s ease-out;
        ">🏦 Valura AI Financial Advisor</h1>
        <p style="
            font-size: 1.2rem;
            color: #4a5568;
            font-weight: 600;
            margin-bottom: 0;
        ">Your personalized retirement planning companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show progress indicator during persona building
    if st.session_state.conversation_phase == 'persona_building':
        show_progress_indicator()
    
    # Enhanced Sidebar - Profile Status
    with st.sidebar:
        st.markdown("""
        <div style="
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
        ">👤 Your Financial Profile</div>
        """, unsafe_allow_html=True)
        
        profile = st.session_state.user_profile
        if profile:
            # Create enhanced metric cards
            metric_cards = []
            
            for key, value in profile.items():
                if key in ['monthly_income', 'current_savings', 'monthly_savings']:
                    formatted_value = f"${value:,}"
                    icon = "💰" if key == 'current_savings' else "📈" if key == 'monthly_savings' else "💵"
                elif key == 'expected_return':
                    formatted_value = f"{value}%"
                    icon = "📊"
                elif key == 'age':
                    formatted_value = f"{value} years"
                    icon = "👤"
                elif key == 'retirement_age':
                    formatted_value = f"{value} years"
                    icon = "🎯"
                else:
                    formatted_value = str(value)
                    icon = "ℹ️"
                
                metric_html = f"""
                <div class="metric-container" style="
                    background: #ffffff;
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    border: 1px solid #e2e8f0;
                    border-left: 4px solid #2d3748;
                    transition: all 0.3s ease;
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                    ">
                        <div>
                            <div style="
                                font-size: 0.8rem;
                                color: #4a5568;
                                font-weight: 600;
                                margin-bottom: 0.25rem;
                            ">{key.replace('_', ' ').title()}</div>
                            <div style="
                                font-size: 1.1rem;
                                font-weight: 700;
                                color: #1a202c;
                            ">{formatted_value}</div>
                        </div>
                        <div style="font-size: 1.5rem;">{icon}</div>
                    </div>
                </div>
                """
                st.markdown(metric_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #ffffff;
                color: #1a202c;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #e2e8f0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🚀</div>
                <div style="font-weight: 600;">Complete the chat to see your personalized profile here!</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Quick actions
        st.markdown("""
        <div style="
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
            margin: 2rem 0 1rem 0;
            text-align: center;
        ">🚀 Quick Actions</div>
        """, unsafe_allow_html=True)
        
        # Start Over button with enhanced styling
        if st.button("🔄 Start Over", use_container_width=True, key="start_over_btn"):
            for key in ['messages', 'user_profile', 'conversation_phase', 'current_question_index', 'calculation_history']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # Skip to Calculation button
        if st.button("⏭️ Skip to Calculation", use_container_width=True, key="skip_btn"):
            # Set default values for missing profile items
            defaults = {q['id']: q['default'] for q in PERSONA_QUESTIONS}
            for key, default_val in defaults.items():
                if key not in st.session_state.user_profile:
                    st.session_state.user_profile[key] = default_val
            
            st.session_state.conversation_phase = 'profile_complete'
            st.session_state.current_question_index = len(PERSONA_QUESTIONS)
            add_message("assistant", "⚡ Using default values to jump to your retirement calculation...")
            run_retirement_calculation()
            st.rerun()
        
        # Add calculation history viewer if available
        if st.session_state.calculation_history:
            st.markdown("""
            <div style="
                color: #ffffff;
                font-size: 1.2rem;
                font-weight: 700;
                margin: 2rem 0 1rem 0;
                text-align: center;
            ">📊 Recent Calculations</div>
            """, unsafe_allow_html=True)
            
            for i, calc in enumerate(reversed(st.session_state.calculation_history[-3:])):  # Show last 3
                calc_type = calc['type'].replace('_', ' ').title()
                timestamp = calc['timestamp'].strftime("%H:%M")
                
                calc_html = f"""
                <div style="
                    background: #ffffff;
                    border-radius: 8px;
                    padding: 0.75rem;
                    margin: 0.5rem 0;
                    border: 1px solid #e2e8f0;
                    border-left: 3px solid #2d3748;
                    font-size: 0.85rem;
                ">
                    <div style="font-weight: 600; color: #1a202c;">{calc_type}</div>
                    <div style="color: #4a5568; font-size: 0.75rem; font-weight: 500;">{timestamp}</div>
                </div>
                """
                st.markdown(calc_html, unsafe_allow_html=True)
            
            # Export results button
            if st.button("📄 Export Results", use_container_width=True, key="export_btn"):
                export_data = {
                    "profile": st.session_state.user_profile,
                    "calculations": st.session_state.calculation_history,
                    "export_date": datetime.now().isoformat()
                }
                
                # Create downloadable JSON
                import json
                json_str = json.dumps(export_data, indent=2, default=str)
                
                st.download_button(
                    label="💾 Download Financial Report",
                    data=json_str,
                    file_name=f"valura_financial_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Add financial tips section
        st.markdown("""
        <div style="
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
            margin: 2rem 0 1rem 0;
            text-align: center;
        ">💡 Financial Tips</div>
        """, unsafe_allow_html=True)
        
        # Rotating financial tips
        tips = [
            "💰 Start investing early - compound interest is powerful!",
            "🎯 Aim to save at least 10-15% of your income for retirement",
            "🚨 Build an emergency fund of 3-6 months expenses",
            "📈 Diversify your investments to reduce risk",
            "💳 Pay off high-interest debt before investing",
            "🏠 Consider the total cost of homeownership, not just the mortgage",
            "📊 Review and rebalance your portfolio annually",
            "🎓 Invest in yourself through education and skills",
            "💡 Automate your savings to make it effortless",
            "🔍 Regularly review your financial goals and progress"
        ]
        
        # Show a rotating tip based on current time
        import hashlib
        tip_index = int(hashlib.md5(str(datetime.now().date()).encode()).hexdigest(), 16) % len(tips)
        current_tip = tips[tip_index]
        
        tip_html = f"""
        <div style="
            background: #ffffff;
            color: #1a202c;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            font-size: 0.9rem;
            line-height: 1.4;
            font-weight: 600;
        ">
            {current_tip}
        </div>
        """
        st.markdown(tip_html, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Show current question options if in persona building phase
    if st.session_state.conversation_phase == 'persona_building':
        current_q = get_current_question()
        if current_q:
            # Enhanced question display
            question_html = f"""
            <div style="
                background: #ffffff;
                border: 2px solid #cbd5e0;
                border-radius: 12px;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: questionSlide 0.5s ease-out;
            ">
                <div style="
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: #1a202c;
                    margin-bottom: 1rem;
                    text-align: center;
                ">
                    📝 {current_q['question']}
                </div>
                <div style="
                    font-size: 0.9rem;
                    color: #4a5568;
                    text-align: center;
                    margin-bottom: 1rem;
                    font-weight: 600;
                ">
                    Question {st.session_state.current_question_index + 1} of {len(PERSONA_QUESTIONS)}
                </div>
            </div>
            
            <style>
            @keyframes questionSlide {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            </style>
            """
            st.markdown(question_html, unsafe_allow_html=True)
            
            render_question_input(current_q)
            
            # Skip option for non-mandatory questions
            if not current_q['mandatory']:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("⏭️ Skip this question", use_container_width=True, key="skip_question"):
                        st.session_state.current_question_index += 1
                        add_message("user", "Skipped")
                        next_question_or_complete()
                        st.rerun()
    
    # Show helpful suggestions in interactive phase
    if st.session_state.conversation_phase == 'interactive':
        st.markdown("""
        <div style="
            background: #ffffff;
            border: 2px solid #cbd5e0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        ">
            <div style="
                font-size: 1.1rem;
                font-weight: 700;
                color: #1a202c;
                margin-bottom: 1rem;
                text-align: center;
            ">💡 Try asking me about:</div>
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 0.5rem;
                font-size: 0.9rem;
            ">
                <div style="color: #2d3748; font-weight: 600;">• "What if I save $200 more per month?"</div>
                <div style="color: #2d3748; font-weight: 600;">• "How long will my money last?"</div>
                <div style="color: #2d3748; font-weight: 600;">• "Do I have enough emergency savings?"</div>
                <div style="color: #2d3748; font-weight: 600;">• "Should I pay off debt or invest?"</div>
                <div style="color: #2d3748; font-weight: 600;">• "How much for college funding?"</div>
                <div style="color: #2d3748; font-weight: 600;">• "Buy vs rent analysis"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced chat input
    user_input = st.chat_input(
        "Ask about retirement planning, savings goals, or type your answer...",
        key="chat_input"
    )
    
    # Handle user input
    if user_input:
        add_message("user", user_input)
        
        # Show thinking indicator
        with st.chat_message("assistant"):
            show_thinking_indicator()
        
        # Process based on conversation phase
        if st.session_state.conversation_phase == 'persona_building':
            current_q = get_current_question()
            if current_q:
                try:
                    # Parse and validate input
                    if current_q['type'] == 'number':
                        value = float(user_input.replace('$', '').replace(',', '').replace('%', ''))
                        if current_q['validation'](value):
                            st.session_state.user_profile[current_q['id']] = int(value)
                            st.session_state.current_question_index += 1
                            add_message("assistant", f"✅ Got it! {current_q['id'].replace('_', ' ').title()}: {value}")
                            next_question_or_complete()
                        else:
                            add_message("assistant", "❌ That value seems out of range. Could you try again?")
                    
                    elif current_q['type'] == 'currency':
                        value = float(user_input.replace('$', '').replace(',', ''))
                        if current_q['validation'](value):
                            st.session_state.user_profile[current_q['id']] = value
                            st.session_state.current_question_index += 1
                            add_message("assistant", f"✅ Perfect! {current_q['id'].replace('_', ' ').title()}: ${value:,}")
                            next_question_or_complete()
                        else:
                            add_message("assistant", "❌ Please enter a valid amount (e.g., 5000 or $5,000)")
                    
                    elif current_q['type'] == 'percentage':
                        value = float(user_input.replace('%', ''))
                        if current_q['validation'](value):
                            st.session_state.user_profile[current_q['id']] = value
                            st.session_state.current_question_index += 1
                            add_message("assistant", f"✅ Great! Expected return: {value}%")
                            next_question_or_complete()
                        else:
                            add_message("assistant", "❌ Please enter a percentage between 0 and 20")
                    
                    elif current_q['type'] == 'select':
                        if user_input.title() in current_q['options']:
                            st.session_state.user_profile[current_q['id']] = user_input.title()
                            st.session_state.current_question_index += 1
                            add_message("assistant", f"✅ Noted! Risk tolerance: {user_input.title()}")
                            next_question_or_complete()
                        else:
                            add_message("assistant", f"❌ Please choose from: {', '.join(current_q['options'])}")
                    
                    elif current_q['type'] == 'text':
                        st.session_state.user_profile[current_q['id']] = user_input
                        st.session_state.current_question_index += 1
                        add_message("assistant", f"✅ Thanks for sharing: {user_input}")
                        next_question_or_complete()
                    
                except ValueError:
                    add_message("assistant", "❌ I couldn't understand that format. Could you try again with a number?")
        
        elif st.session_state.conversation_phase == 'interactive':
            # Use enhanced AI response with automatic calculations
            response = generate_ai_response_with_calculations(user_input, {
                'user_profile': st.session_state.user_profile,
                'conversation_phase': st.session_state.conversation_phase,
                'recent_calculations': st.session_state.calculation_history
            })
            add_message("assistant", response)
        
        st.rerun()
    
    # Add floating action button for quick actions
    if st.session_state.conversation_phase == 'interactive':
        fab_html = """
        <div style="
            position: fixed;
            bottom: 100px;
            right: 30px;
            z-index: 1000;
        ">
            <div style="
                background: #2d3748;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                border: 2px solid #4a5568;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                cursor: pointer;
                transition: all 0.3s ease;
                animation: float 3s ease-in-out infinite;
            " 
            onmouseover="this.style.transform='scale(1.1)'; this.style.background='#4a5568';"
            onmouseout="this.style.transform='scale(1)'; this.style.background='#2d3748';"
            onclick="document.getElementById('chat_input').focus()"
            title="Quick Chat">
                <span style="color: #ffffff; font-size: 1.5rem;">💬</span>
            </div>
        </div>
        
        <style>
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-10px);
            }
        }
        </style>
        """
        st.markdown(fab_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
