"""
Valura Financial Planning Agent - Improved with LangGraph Memory Management
"""

import streamlit as st
import os
import sys
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Annotated
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path for imports
sys.path.append(os.path.dirname(__file__))

# LangGraph imports for memory management
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

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
    from src.calculators.step_by_step_calculator import (
        calculate_scenario_step_by_step,
        format_step_by_step_response,
        calculate_withdrawal_longevity_step_by_step,
        format_withdrawal_analysis
    )
    from src.tools.financial_tools import FINANCIAL_TOOLS
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as e:
    st.error(f"Could not import financial modules: {e}. Please ensure all dependencies are installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Valura AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Design System with Accessibility
def apply_modern_styling():
    st.markdown("""
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* CSS Custom Properties for consistent theming */
    :root {
        /* Primary Colors - Modern Blue Palette */
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-200: #bfdbfe;
        --primary-300: #93c5fd;
        --primary-400: #60a5fa;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-800: #1e40af;
        --primary-900: #1e3a8a;
        
        /* Neutral Colors - Modern Gray Scale */
        --neutral-50: #f8fafc;
        --neutral-100: #f1f5f9;
        --neutral-200: #e2e8f0;
        --neutral-300: #cbd5e1;
        --neutral-400: #94a3b8;
        --neutral-500: #64748b;
        --neutral-600: #475569;
        --neutral-700: #334155;
        --neutral-800: #1e293b;
        --neutral-900: #0f172a;
        
        /* Semantic Colors */
        --success-500: #10b981;
        --success-100: #d1fae5;
        --warning-500: #f59e0b;
        --warning-100: #fef3c7;
        --error-500: #ef4444;
        --error-100: #fee2e2;
        
        /* Typography */
        --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        
        /* Spacing Scale */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-12: 3rem;
        
        /* Border Radius */
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        
        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    
    /* Global Styles */
    .stApp {
        font-family: var(--font-family);
        background: var(--neutral-50);
        color: var(--neutral-900);
        line-height: 1.6;
        letter-spacing: -0.01em;
    }
    
    /* Main Container */
    .main .block-container {
        padding: var(--space-8);
        background: white;
        border-radius: var(--radius-xl);
        margin: var(--space-4);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--neutral-200);
        max-width: 1200px;
        animation: slideIn 0.6s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Typography Hierarchy */
    h1 {
        color: var(--neutral-900) !important;
        font-weight: 700;
        font-size: 2.5rem;
        line-height: 1.2;
        margin-bottom: var(--space-6);
        text-align: center;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-800));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        color: var(--neutral-800) !important;
        font-weight: 600;
        font-size: 1.875rem;
        margin-bottom: var(--space-4);
    }
    
    h3 {
        color: var(--neutral-700) !important;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: var(--space-3);
    }
    
    /* Text Elements */
    .stMarkdown p,
    .stMarkdown div,
    .stText {
        color: var(--neutral-700) !important;
        font-weight: 400;
        line-height: 1.7;
        margin-bottom: var(--space-3);
    }
    
    /* Chat Messages - Enhanced Visibility */
    .stChatMessage {
        border-radius: var(--radius-lg);
        margin: var(--space-4) 0;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--neutral-200);
        animation: messageSlide 0.4s ease-out;
        transition: all 0.3s ease;
        overflow: hidden;
        min-height: 60px;
        padding: var(--space-4);
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* User Messages - Modern Blue Theme with High Contrast */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, var(--primary-600), var(--primary-700)) !important;
        color: white !important;
        margin-left: var(--space-8);
        border: 1px solid var(--primary-500);
    }
    
    .stChatMessage[data-testid="user-message"] *,
    .stChatMessage[data-testid="user-message"] .stMarkdown,
    .stChatMessage[data-testid="user-message"] .stMarkdown p,
    .stChatMessage[data-testid="user-message"] .stMarkdown div,
    .stChatMessage[data-testid="user-message"] .stMarkdown span,
    .stChatMessage[data-testid="user-message"] .stMarkdown strong,
    .stChatMessage[data-testid="user-message"] .stMarkdown em {
        color: white !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    
    /* Assistant Messages - Clean Light Theme with High Contrast */
    .stChatMessage[data-testid="assistant-message"] {
        background: white !important;
        color: var(--neutral-900) !important;
        margin-right: var(--space-8);
        border: 1px solid var(--neutral-300);
    }
    
    .stChatMessage[data-testid="assistant-message"] *,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown p,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown div,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown span,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown strong,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown em,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown li,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown ul,
    .stChatMessage[data-testid="assistant-message"] .stMarkdown ol {
        color: var(--neutral-900) !important;
        font-weight: 500 !important;
        line-height: 1.7 !important;
    }
    
    /* Ensure all text in assistant messages is visible */
    .stChatMessage[data-testid="assistant-message"] h1,
    .stChatMessage[data-testid="assistant-message"] h2,
    .stChatMessage[data-testid="assistant-message"] h3,
    .stChatMessage[data-testid="assistant-message"] h4,
    .stChatMessage[data-testid="assistant-message"] h5,
    .stChatMessage[data-testid="assistant-message"] h6 {
        color: var(--neutral-800) !important;
        font-weight: 600 !important;
        margin: var(--space-3) 0 !important;
    }
    
    /* Code blocks in messages */
    .stChatMessage code {
        background: var(--neutral-100) !important;
        color: var(--neutral-800) !important;
        padding: var(--space-1) var(--space-2) !important;
        border-radius: var(--radius-sm) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.875rem !important;
    }
    
    .stChatMessage pre {
        background: var(--neutral-100) !important;
        color: var(--neutral-800) !important;
        padding: var(--space-3) !important;
        border-radius: var(--radius-md) !important;
        overflow-x: auto !important;
        margin: var(--space-3) 0 !important;
    }
    
    /* Blockquotes in messages */
    .stChatMessage blockquote {
        border-left: 4px solid var(--primary-500) !important;
        padding-left: var(--space-3) !important;
        margin: var(--space-3) 0 !important;
        font-style: italic !important;
        color: var(--neutral-700) !important;
    }
    
    /* Sidebar - Modern Dark Theme */
    .css-1d391kg,
    .stSidebar,
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        background: var(--neutral-900) !important;
        border-right: 1px solid var(--neutral-800);
    }
    
    /* Sidebar Content */
    .css-1d391kg *,
    .stSidebar *,
    [data-testid="stSidebar"] * {
        color: var(--neutral-100) !important;
        font-family: var(--font-family) !important;
    }
    
    /* Fix profile boxes text color to black for better readability */
    .css-1d391kg .metric-value,
    .stSidebar .metric-value,
    [data-testid="stSidebar"] .metric-value,
    .css-1d391kg [data-testid="metric-value"],
    .stSidebar [data-testid="metric-value"],
    [data-testid="stSidebar"] [data-testid="metric-value"],
    .stSidebar .stMetric [data-testid="metric-value"],
    .stSidebar .stMetric .metric-value,
    [data-testid="stSidebar"] .stMetric [data-testid="metric-value"],
    [data-testid="stSidebar"] .stMetric .metric-value {
        color: #000000 !important;
        font-weight: 700 !important;
        background: white !important;
        padding: var(--space-2) var(--space-3) !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--neutral-300) !important;
        margin: var(--space-1) 0 !important;
    }
    
    /* Fix profile boxes label color */
    .css-1d391kg .metric-label,
    .stSidebar .metric-label,
    [data-testid="stSidebar"] .metric-label,
    .css-1d391kg [data-testid="metric-label"],
    .stSidebar [data-testid="metric-label"],
    [data-testid="stSidebar"] [data-testid="metric-label"],
    .stSidebar .stMetric [data-testid="metric-label"],
    .stSidebar .stMetric .metric-label,
    [data-testid="stSidebar"] .stMetric [data-testid="metric-label"],
    [data-testid="stSidebar"] .stMetric .metric-label {
        color: var(--neutral-100) !important;
        font-weight: 600 !important;
        margin-bottom: var(--space-1) !important;
    }
    
    /* Additional comprehensive targeting for all sidebar metric text */
    .stSidebar div[data-testid="metric-container"] div,
    [data-testid="stSidebar"] div[data-testid="metric-container"] div,
    .stSidebar .element-container div,
    [data-testid="stSidebar"] .element-container div {
        color: #000000 !important;
    }
    
    /* Target all text elements in sidebar metrics specifically */
    .stSidebar .stMetric div,
    [data-testid="stSidebar"] .stMetric div,
    .stSidebar [data-testid="metric-container"] div,
    [data-testid="stSidebar"] [data-testid="metric-container"] div {
        color: #000000 !important;
        background: white !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        margin: 2px 0 !important;
    }
    
    /* Fix progress indicator text color */
    .progress-container,
    .progress-container * {
        color: var(--neutral-900) !important;
    }
    
    /* NUCLEAR OPTION: Force ALL sidebar text to be black */
    .stSidebar *,
    [data-testid="stSidebar"] *,
    .css-1d391kg * {
        color: #000000 !important;
    }
    
    /* Override any Streamlit metric styling completely */
    .stSidebar .stMetric *,
    [data-testid="stSidebar"] .stMetric *,
    .stSidebar [class*="metric"] *,
    [data-testid="stSidebar"] [class*="metric"] *,
    .stSidebar [data-testid*="metric"] *,
    [data-testid="stSidebar"] [data-testid*="metric"] * {
        color: #000000 !important;
        background: white !important;
        text-shadow: none !important;
        opacity: 1 !important;
    }
    
    /* Target specific Streamlit internal classes */
    .stSidebar .css-1wivap2,
    .stSidebar .css-1xarl3l,
    .stSidebar .css-1v0mbdj,
    [data-testid="stSidebar"] .css-1wivap2,
    [data-testid="stSidebar"] .css-1xarl3l,
    [data-testid="stSidebar"] .css-1v0mbdj {
        color: #000000 !important;
        background: white !important;
    }
    
    /* Sidebar Headers - Keep these white for contrast */
    .css-1d391kg h1,
    .css-1d391kg h2,
    .css-1d391kg h3,
    .stSidebar h1,
    .stSidebar h2,
    .stSidebar h3,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    .stSidebar .markdown-text-container h1,
    .stSidebar .markdown-text-container h2,
    .stSidebar .markdown-text-container h3,
    [data-testid="stSidebar"] .markdown-text-container h1,
    [data-testid="stSidebar"] .markdown-text-container h2,
    [data-testid="stSidebar"] .markdown-text-container h3 {
        color: white !important;
        font-weight: 600 !important;
        margin-bottom: var(--space-4) !important;
    }
    
    /* Exception: Keep sidebar section headers white but make metric text black */
    .stSidebar h1,
    .stSidebar h2, 
    .stSidebar h3,
    .stSidebar h4,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: white !important;
    }
    
    /* Buttons - Modern Design */
    .stButton > button {
        background: var(--primary-600) !important;
        color: white !important;
        border: 1px solid var(--primary-500);
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-6);
        font-weight: 600;
        font-family: var(--font-family) !important;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        background: var(--primary-700) !important;
        border-color: var(--primary-600);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    /* Secondary Buttons */
    .stButton.secondary > button {
        background: var(--neutral-100) !important;
        color: var(--neutral-700) !important;
        border: 1px solid var(--neutral-300);
    }
    
    .stButton.secondary > button:hover {
        background: var(--neutral-200) !important;
        border-color: var(--neutral-400);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: var(--radius-md);
        border: 1px solid var(--neutral-300) !important;
        padding: var(--space-3) var(--space-4);
        font-family: var(--font-family) !important;
        background: white !important;
        color: var(--neutral-900) !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px var(--primary-100) !important;
        outline: none;
    }
    
    /* Chat Input */
    .stChatInputContainer {
        border-radius: var(--radius-lg);
        background: white !important;
        border: 2px solid var(--neutral-200) !important;
        box-shadow: var(--shadow-md);
        transition: all 0.2s ease;
    }
    
    .stChatInputContainer:focus-within {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px var(--primary-100), var(--shadow-lg);
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        border: 1px solid var(--neutral-200);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .stMetric .metric-value {
        color: var(--primary-600) !important;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    .stMetric .metric-label {
        color: var(--neutral-600) !important;
        font-weight: 500;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Sidebar Metrics - Force black text for all metric components */
    .stSidebar .stMetric,
    [data-testid="stSidebar"] .stMetric {
        background: white !important;
        border: 1px solid var(--neutral-300) !important;
        margin: var(--space-2) 0 !important;
    }
    
    .stSidebar .stMetric .metric-value,
    .stSidebar .stMetric [data-testid="metric-value"],
    [data-testid="stSidebar"] .stMetric .metric-value,
    [data-testid="stSidebar"] .stMetric [data-testid="metric-value"],
    .stSidebar .stMetric div:first-child,
    [data-testid="stSidebar"] .stMetric div:first-child {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }
    
    .stSidebar .stMetric .metric-label,
    .stSidebar .stMetric [data-testid="metric-label"],
    [data-testid="stSidebar"] .stMetric .metric-label,
    [data-testid="stSidebar"] .stMetric [data-testid="metric-label"],
    .stSidebar .stMetric div:last-child,
    [data-testid="stSidebar"] .stMetric div:last-child {
        color: var(--neutral-200) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
    }
    
    /* Progress Bar */
    .progress-container {
        background: var(--neutral-100);
        border-radius: var(--radius-md);
        padding: var(--space-4);
        margin: var(--space-4) 0;
        border: 1px solid var(--neutral-200);
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--neutral-200);
        border-radius: var(--radius-sm);
        overflow: hidden;
        margin: var(--space-2) 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
        border-radius: var(--radius-sm);
        transition: width 0.5s ease;
    }
    
    /* Loading Indicator */
    .thinking-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--space-4);
        background: var(--primary-50);
        border: 1px solid var(--primary-200);
        border-radius: var(--radius-lg);
        color: var(--primary-700);
        margin: var(--space-4) 0;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.8; }
        50% { opacity: 1; }
    }
    
    /* Quick Options */
    .quick-options {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
        margin: var(--space-4) 0;
    }
    
    .quick-option-btn {
        background: var(--neutral-100) !important;
        color: var(--neutral-700) !important;
        border: 1px solid var(--neutral-300);
        border-radius: var(--radius-md);
        padding: var(--space-2) var(--space-4);
        font-family: var(--font-family) !important;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .quick-option-btn:hover {
        background: var(--primary-50) !important;
        color: var(--primary-700) !important;
        border-color: var(--primary-300);
        transform: translateY(-1px);
    }
    
    /* Persona Building Specific Styles */
    .persona-question-container {
        background: white;
        border: 2px solid var(--primary-300);
        border-radius: var(--radius-xl);
        padding: var(--space-8);
        margin: var(--space-6) 0;
        box-shadow: var(--shadow-lg);
        animation: questionSlide 0.5s ease-out;
    }
    
    /* Slider styling for persona questions */
    .stSlider > div > div > div > div {
        background: var(--primary-600) !important;
    }
    
    .stSlider > div > div > div {
        background: var(--primary-100) !important;
    }
    
    /* Number input styling */
    .stNumberInput > div > div > input {
        border: 2px solid var(--neutral-300) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-3) var(--space-4) !important;
        font-family: var(--font-family) !important;
        background: white !important;
        color: var(--neutral-900) !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px var(--primary-100) !important;
        outline: none;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > select {
        border: 2px solid var(--neutral-300) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-3) var(--space-4) !important;
        font-family: var(--font-family) !important;
        background: white !important;
        color: var(--neutral-900) !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px var(--primary-100) !important;
        outline: none;
    }
    
    /* Text input styling for persona questions */
    .stTextInput > div > div > input {
        border: 2px solid var(--neutral-300) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-3) var(--space-4) !important;
        font-family: var(--font-family) !important;
        background: white !important;
        color: var(--neutral-900) !important;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px var(--primary-100) !important;
        outline: none;
    }
    
    /* Submit button styling for persona questions */
    .stButton > button[kind="primary"] {
        background: var(--primary-600) !important;
        color: white !important;
        border: 1px solid var(--primary-500);
        border-radius: var(--radius-md);
        padding: var(--space-3) var(--space-6);
        font-weight: 600;
        font-family: var(--font-family) !important;
        transition: all 0.2s ease;
        box-shadow: var(--shadow-sm);
        width: 100%;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--primary-700) !important;
        border-color: var(--primary-600);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Success States */
    .success-message {
        background: var(--success-100);
        color: var(--success-800);
        border: 1px solid var(--success-200);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-4) 0;
    }
    
    /* Error States */
    .error-message {
        background: var(--error-100);
        color: var(--error-800);
        border: 1px solid var(--error-200);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-4) 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--neutral-100);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--neutral-400);
        border-radius: var(--radius-sm);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--neutral-500);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            margin: var(--space-2);
            padding: var(--space-4);
        }
        
        h1 {
            font-size: 2rem;
        }
        
        .stChatMessage[data-testid="user-message"] {
            margin-left: var(--space-2);
        }
        
        .stChatMessage[data-testid="assistant-message"] {
            margin-right: var(--space-2);
        }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* FINAL OVERRIDE: Force all sidebar metric text to be black with highest specificity */
    .stSidebar .stMetric div[data-testid="metric-value"],
    [data-testid="stSidebar"] .stMetric div[data-testid="metric-value"],
    .stSidebar .stMetric > div > div,
    [data-testid="stSidebar"] .stMetric > div > div,
    .stSidebar .stMetric span,
    [data-testid="stSidebar"] .stMetric span,
    .stSidebar div[data-testid="metric-container"] > div,
    [data-testid="stSidebar"] div[data-testid="metric-container"] > div,
    /* Additional targeting for metric values specifically */
    .stSidebar .stMetric [data-testid="metric-value"] *,
    [data-testid="stSidebar"] .stMetric [data-testid="metric-value"] *,
    .stSidebar .stMetric .metric-value *,
    [data-testid="stSidebar"] .stMetric .metric-value *,
    .stSidebar [data-testid="metric-container"] [data-testid="metric-value"],
    [data-testid="stSidebar"] [data-testid="metric-container"] [data-testid="metric-value"],
    .stSidebar [data-testid="metric-container"] .metric-value,
    [data-testid="stSidebar"] [data-testid="metric-container"] .metric-value,
    /* Target all text nodes in sidebar metrics */
    .stSidebar .stMetric div:not([data-testid="metric-label"]),
    [data-testid="stSidebar"] .stMetric div:not([data-testid="metric-label"]),
    .stSidebar .stMetric > div:last-child,
    [data-testid="stSidebar"] .stMetric > div:last-child,
    .stSidebar .stMetric > div:last-child *,
    [data-testid="stSidebar"] .stMetric > div:last-child * {
        color: #000000 !important;
        background-color: white !important;
        font-weight: 700 !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        border: 1px solid #e2e8f0 !important;
        margin: 4px 0 !important;
        display: block !important;
        text-shadow: none !important;
        opacity: 1 !important;
    }
    
    /* NUCLEAR OPTION: Force ALL text in sidebar metrics to be black */
    .stSidebar .stMetric,
    .stSidebar .stMetric *,
    [data-testid="stSidebar"] .stMetric,
    [data-testid="stSidebar"] .stMetric * {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize LLM
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

# Initialize Memory Store and Checkpointer
@st.cache_resource
def initialize_memory_system():
    """Initialize LangGraph memory system with store and checkpointer"""
    try:
        # Create in-memory store for long-term memories
        store = InMemoryStore()
        
        # Create in-memory checkpointer for conversation state
        checkpointer = InMemorySaver()
        
        return store, checkpointer
    except Exception as e:
        st.error(f"Failed to initialize memory system: {e}")
        return None, None

# Define State for LangGraph
class FinancialChatState(MessagesState):
    """Extended state for financial chat with user profile and calculation history"""
    user_profile: Dict[str, Any] = {}
    conversation_phase: str = "persona_building"
    current_question_index: int = 0
    calculation_history: List[Dict] = []

# Persona Questions Configuration
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

# Persona building functions
def get_current_question():
    if st.session_state.current_question_index < len(PERSONA_QUESTIONS):
        return PERSONA_QUESTIONS[st.session_state.current_question_index]
    return None

def render_question_input(question):
    """Render interactive question input with modern styling"""
    question_id = str(question['id'])
    
    # Initialize session state keys if they don't exist to prevent widget key errors
    slider_key = f"slider_{question_id}"
    manual_key = f"manual_{question_id}"
    
    if slider_key not in st.session_state:
        st.session_state[slider_key] = question['default']
    if manual_key not in st.session_state:
        st.session_state[manual_key] = question['default']
    
    # Create two columns for slider and manual input
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if question['type'] == 'currency':
            slider_value = st.slider(
                f"Use slider for {question['question']}",
                min_value=float(question.get('min_value', 0)),
                max_value=float(question.get('max_value', 200000)),
                value=float(st.session_state[slider_key]),
                step=100.0,
                key=slider_key,
                format="$%.0f"
            )
        elif question['type'] == 'number':
            slider_value = st.slider(
                f"Use slider for {question['question']}",
                min_value=int(question.get('min_value', 0)),
                max_value=int(question.get('max_value', 100)),
                value=int(st.session_state[slider_key]),
                key=slider_key
            )
        elif question['type'] == 'percentage':
            slider_value = st.slider(
                f"Use slider for {question['question']}",
                min_value=float(question.get('min_value', 0.0)),
                max_value=float(question.get('max_value', 20.0)),
                value=float(st.session_state[slider_key]),
                step=0.1,
                key=slider_key,
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
                value=str(st.session_state.get(f"text_{question_id}", question['default'])), 
                key=f"text_{question_id}"
            )
    
    with col2:
        if question['type'] in ['currency', 'number', 'percentage']:
            if question['type'] == 'currency':
                manual_value = st.number_input(
                    "Or enter manually:",
                    min_value=float(question.get('min_value', 0)),
                    max_value=float(question.get('max_value', 1000000)),
                    value=float(st.session_state[manual_key]),
                    step=100.0,
                    key=manual_key,
                    format="%.0f"
                )
            elif question['type'] == 'number':
                manual_value = st.number_input(
                    "Or enter manually:",
                    min_value=int(question.get('min_value', 0)),
                    max_value=int(question.get('max_value', 100)),
                    value=int(st.session_state[manual_key]),
                    key=manual_key
                )
            elif question['type'] == 'percentage':
                manual_value = st.number_input(
                    "Or enter manually:",
                    min_value=float(question.get('min_value', 0.0)),
                    max_value=float(question.get('max_value', 20.0)),
                    value=float(st.session_state[manual_key]),
                    step=0.1,
                    key=manual_key,
                    format="%.1f"
                )
            
            # Use manual value if it's different from slider
            final_value = manual_value
        else:
            final_value = slider_value
    
    # Quick options buttons
    if 'quick_options' in question and question['type'] != 'select':
        st.markdown("**Quick Options:**")
        cols = st.columns(len(question['quick_options']))
        for i, option in enumerate(question['quick_options']):
            with cols[i]:
                if question['type'] == 'currency':
                    button_text = f"${option:,.0f}"
                elif question['type'] == 'percentage':
                    button_text = f"{option}%"
                else:
                    button_text = str(option)
                
                # Use a callback approach to avoid session state modification after widget instantiation
                if st.button(button_text, key=f"quick_{question_id}_{i}", use_container_width=True):
                    # Store the selected option in a temporary variable
                    st.session_state[f"selected_option_{question_id}"] = option
                    st.rerun()
    
    # Check if a quick option was selected and update the values
    if f"selected_option_{question_id}" in st.session_state:
        selected_option = st.session_state[f"selected_option_{question_id}"]
        final_value = selected_option
        # Clear the temporary selection
        del st.session_state[f"selected_option_{question_id}"]
    
    # Submit button
    if st.button("Submit Answer", key=f"submit_{question_id}", type="primary", use_container_width=True):
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
    """Add message to session state"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    }
    if metadata:
        message["metadata"] = metadata
    
    st.session_state.messages.append(message)

def next_question_or_complete():
    """Move to next question or complete persona building"""
    current_q = get_current_question()
    if current_q:
        # Ask next question
        question_text = f"📝 {current_q['question']}"
        if not current_q['mandatory']:
            question_text += " (optional - you can skip this)"
        
        add_message("assistant", question_text)
    else:
        # Profile complete - store original baseline values
        st.session_state.original_baseline = st.session_state.user_profile.copy()
        st.session_state.conversation_phase = 'profile_complete'
        add_message("assistant", "🎉 Great! I have all the information I need. Let me analyze your financial situation and create your retirement plan...")
        
        # Run initial calculation
        run_retirement_calculation()

def run_retirement_calculation():
    """Run initial retirement calculation after profile completion"""
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
        
        response = f"""📊 **Your Retirement Plan Analysis:**

🎯 **Projected Retirement Fund:** ${total_fund:,.0f}
⏰ **Years to Retirement:** {years_to_retirement} years  
💰 **Inflation-Adjusted Value:** ${real_value:,.0f}

**Based on your profile:**
• Monthly savings: ${profile.get('monthly_savings', 0):,}
• Expected return: {profile.get('expected_return', 0)}%
• Current savings: ${profile.get('current_savings', 0):,}

💡 **What would you like to explore next?**
• Ask "What if I save $200 more per month?" for scenarios
• Ask "How long will my money last if I withdraw $3,000/month?" for withdrawal planning  
• Ask "Explain the calculation step by step" for detailed breakdown"""
        
        add_message("assistant", response)
        st.session_state.conversation_phase = 'interactive'
        
    except Exception as e:
        add_message("assistant", f"I had trouble running the calculation. Error: {str(e)}. Let's try again or ask me something else!")

def initialize_session_state():
    """Initialize Streamlit session state with LangGraph integration"""
    if 'initialized' not in st.session_state:
        # Initialize memory system
        store, checkpointer = initialize_memory_system()
        if store is None or checkpointer is None:
            st.error("Failed to initialize memory system")
            return
        
        st.session_state.store = store
        st.session_state.checkpointer = checkpointer
        
        # Initialize conversation state
        st.session_state.messages = []
        st.session_state.user_profile = {}
        st.session_state.original_baseline = {}  # Store original values for scenario calculations
        st.session_state.conversation_phase = 'persona_building'
        st.session_state.current_question_index = 0
        st.session_state.calculation_history = []
        
        # Generate unique thread ID for this session
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.user_id = str(uuid.uuid4())
        
        # Initialize LangGraph
        st.session_state.graph = create_financial_chat_graph()
        
        # Add welcome message and start persona building
        welcome_msg = "👋 Hello! I'm your AI Financial Planning Advisor with enhanced memory. I'll remember our conversation and help you create a personalized retirement plan. Let's start by getting to know you better!"
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_msg,
            "timestamp": datetime.now()
        })
        
        # Start with first question if in persona building phase
        if st.session_state.conversation_phase == 'persona_building':
            first_question = get_current_question()
            if first_question:
                question_msg = f"📝 {first_question['question']}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": question_msg,
                    "timestamp": datetime.now()
                })
        
        st.session_state.initialized = True
    
    # Ensure all required session state variables exist even if already initialized
    # This prevents AttributeError issues
    required_vars = {
        'messages': [],
        'user_profile': {},
        'original_baseline': {},  # Store original values for scenario calculations
        'conversation_phase': 'persona_building',
        'current_question_index': 0,
        'calculation_history': [],
        'thread_id': str(uuid.uuid4()),
        'user_id': str(uuid.uuid4())
    }
    
    for var_name, default_value in required_vars.items():
        if var_name not in st.session_state:
            st.session_state[var_name] = default_value

def extract_financial_parameters(user_input: str, current_profile: Dict) -> Dict[str, Any]:
    """Extract financial parameters from user input"""
    import re
    
    # Extract numbers from input
    numbers = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', user_input.replace(',', ''))
    numbers = [float(n.replace(',', '')) for n in numbers]
    
    # Use original baseline for scenario calculations to prevent compounding errors
    original_baseline = st.session_state.get('original_baseline', current_profile)
    
    # Default parameters from profile (use original baseline for monthly_savings)
    params = {
        'current_monthly_savings': original_baseline.get('monthly_savings', 500),  # Use original baseline!
        'current_age': current_profile.get('age', 35),
        'retirement_age': current_profile.get('retirement_age', 65),
        'current_savings': current_profile.get('current_savings', 25000),
        'annual_return': current_profile.get('expected_return', 7.0) / 100
    }
    
    # Try to extract additional savings amount
    if numbers:
        if 'more' in user_input.lower() or 'additional' in user_input.lower() or 'extra' in user_input.lower():
            params['additional_monthly_savings'] = numbers[0]
        elif 'withdraw' in user_input.lower() or 'take out' in user_input.lower():
            params['monthly_withdrawal'] = numbers[0]
        elif 'save' in user_input.lower() and len(numbers) == 1:
            params['additional_monthly_savings'] = numbers[0] - params['current_monthly_savings']
    
    return params

def handle_financial_calculation(user_input: str, current_profile: Dict, store: BaseStore, user_id: str) -> str:
    """Handle financial calculations with step-by-step breakdown"""
    try:
        user_input_lower = user_input.lower()
        
        # Extract parameters
        params = extract_financial_parameters(user_input, current_profile)
        
        # Scenario analysis (what if I save more)
        if any(phrase in user_input_lower for phrase in ['what if', 'save more', 'additional', 'extra', 'increase']):
            if 'additional_monthly_savings' in params:
                result = calculate_scenario_step_by_step(
                    current_monthly_savings=params['current_monthly_savings'],
                    additional_monthly_savings=params['additional_monthly_savings'],
                    current_age=params['current_age'],
                    retirement_age=params['retirement_age'],
                    current_savings=params['current_savings'],
                    annual_return=params['annual_return']
                )
                
                # Store calculation in memory
                calc_memory = {
                    "data": f"Scenario calculation: +${params['additional_monthly_savings']}/month = +${result['results']['improvement']['additional_retirement_fund']:,.0f} retirement fund",
                    "timestamp": datetime.now().isoformat(),
                    "type": "calculation",
                    "calculation_type": "scenario_analysis",
                    "parameters": params,
                    "results": result['results']
                }
                store.put(("calculations", user_id), str(uuid.uuid4()), calc_memory)
                
                return format_step_by_step_response(result)
        
        # Withdrawal analysis
        elif any(phrase in user_input_lower for phrase in ['how long', 'last', 'withdraw', 'take out']):
            if 'monthly_withdrawal' in params:
                # Use current profile to get retirement fund estimate
                retirement_fund = current_profile.get('projected_retirement_fund', 1000000)  # Default estimate
                
                result = calculate_withdrawal_longevity_step_by_step(
                    retirement_fund=retirement_fund,
                    monthly_withdrawal=params['monthly_withdrawal'],
                    annual_return=0.04  # Conservative withdrawal phase return
                )
                
                # Store calculation in memory
                calc_memory = {
                    "data": f"Withdrawal analysis: ${params['monthly_withdrawal']}/month from ${retirement_fund:,.0f} fund",
                    "timestamp": datetime.now().isoformat(),
                    "type": "calculation",
                    "calculation_type": "withdrawal_analysis",
                    "parameters": params,
                    "results": result['results']
                }
                store.put(("calculations", user_id), str(uuid.uuid4()), calc_memory)
                
                return format_withdrawal_analysis(result)
        
        # Explanation of previous calculation
        elif any(phrase in user_input_lower for phrase in ['explain', 'breakdown', 'calculation', 'how did you']):
            # Search for recent calculations
            calc_memories = store.search(("calculations", user_id), query="calculation", limit=3)
            if calc_memories:
                latest_calc = calc_memories[0]
                calc_data = latest_calc.value
                
                if calc_data.get('calculation_type') == 'scenario_analysis':
                    # Re-run the calculation to get full breakdown
                    params = calc_data['parameters']
                    result = calculate_scenario_step_by_step(
                        current_monthly_savings=params['current_monthly_savings'],
                        additional_monthly_savings=params['additional_monthly_savings'],
                        current_age=params['current_age'],
                        retirement_age=params['retirement_age'],
                        current_savings=params['current_savings'],
                        annual_return=params['annual_return']
                    )
                    return format_step_by_step_response(result)
                
                elif calc_data.get('calculation_type') == 'withdrawal_analysis':
                    params = calc_data['parameters']
                    result = calculate_withdrawal_longevity_step_by_step(
                        retirement_fund=params.get('retirement_fund', 1000000),
                        monthly_withdrawal=params['monthly_withdrawal'],
                        annual_return=0.04
                    )
                    return format_withdrawal_analysis(result)
            
            return "I don't have a recent calculation to explain. Please ask me to perform a specific financial calculation first!"
        
        # Default response for unrecognized financial questions
        return """I can help you with these types of financial calculations:

💰 **Scenario Analysis**: "What if I save $200 more per month?"
📉 **Withdrawal Planning**: "How long will my money last if I withdraw $4,000/month?"
🧮 **Calculation Explanations**: "Explain the calculation" or "Show me the step-by-step breakdown"

Please ask me one of these questions and I'll provide a detailed analysis with step-by-step calculations!"""
        
    except Exception as e:
        return f"I encountered an error with the calculation: {str(e)}. Please try rephrasing your question."

def create_financial_chat_graph():
    """Create LangGraph with proper memory management for financial chat"""
    llm = initialize_llm()
    if not llm:
        return None
    
    def financial_chat_node(
        state: FinancialChatState,
        config: RunnableConfig,
        *,
        store: BaseStore,
    ) -> Dict[str, Any]:
        """Main chat node with enhanced memory integration"""
        try:
            # Get user ID and create namespace for memories
            user_id = config["configurable"].get("user_id", "default")
            namespace = ("financial_profile", user_id)
            calc_namespace = ("calculations", user_id)
            
            # Get the last message
            if not state["messages"]:
                return {"messages": []}
            
            last_message = state["messages"][-1]
            user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Search for relevant memories from both namespaces
            profile_memories = store.search(namespace, query=user_input, limit=5)
            calc_memories = store.search(calc_namespace, query=user_input, limit=3)
            
            # Combine memory contexts
            profile_context = "\n".join([f"- {mem.value.get('data', '')}" for mem in profile_memories])
            calc_context = "\n".join([f"- {mem.value.get('data', '')}" for mem in calc_memories])
            
            # Get current user profile from session state and memories
            current_profile = dict(st.session_state.get('user_profile', {}))
            
            # Update profile from stored memories
            for mem in profile_memories:
                if isinstance(mem.value, dict) and 'profile_data' in mem.value:
                    current_profile.update(mem.value['profile_data'])
            
            # Store updated profile back to session state
            st.session_state.user_profile = current_profile
            
            # Check if this is a financial calculation request
            financial_keywords = [
                'what if', 'save more', 'additional', 'extra', 'increase',
                'how long', 'last', 'withdraw', 'take out',
                'explain', 'breakdown', 'calculation', 'step by step'
            ]
            
            is_financial_calculation = any(keyword in user_input.lower() for keyword in financial_keywords)
            
            if is_financial_calculation:
                # Handle financial calculation with step-by-step breakdown
                calculation_response = handle_financial_calculation(user_input, current_profile, store, user_id)
                
                # Store this calculation interaction in memory
                interaction_memory = {
                    "data": f"User requested calculation: {user_input}. Provided detailed step-by-step analysis.",
                    "timestamp": datetime.now().isoformat(),
                    "type": "calculation_interaction",
                    "user_input": user_input,
                    "response_preview": calculation_response[:200] + "..." if len(calculation_response) > 200 else calculation_response
                }
                store.put(namespace, str(uuid.uuid4()), interaction_memory)
                
                return {"messages": state["messages"] + [AIMessage(content=calculation_response)]}
            
            else:
                # Handle general conversation with AI
                # Include conversation history from state
                conversation_history = ""
                if len(state["messages"]) > 1:
                    recent_messages = state["messages"][-6:]  # Last 6 messages for context
                    for msg in recent_messages[:-1]:  # Exclude the current message
                        role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                        content = msg.content if hasattr(msg, 'content') else str(msg)
                        conversation_history += f"{role}: {content}\n"
                
                system_prompt = f"""
                You are a professional financial advisor with access to the user's conversation history and profile.
                
                User's Financial Profile:
                {json.dumps(current_profile, indent=2) if current_profile else "Profile being built"}
                
                Recent Conversation History:
                {conversation_history if conversation_history else "No previous conversation"}
                
                Relevant Profile Context:
                {profile_context if profile_context else "No stored profile context"}
                
                Previous Calculations Context:
                {calc_context if calc_context else "No previous calculations"}
                
                Current Conversation Phase: {state.get('conversation_phase', 'interactive')}
                
                Instructions:
                1. Remember and reference previous conversations naturally
                2. Provide personalized financial advice based on their profile
                3. If they ask about previous calculations, refer to the stored context
                4. Be encouraging and supportive
                5. Keep responses concise but helpful
                6. If they mention specific numbers or scenarios from before, acknowledge them
                
                If the user is asking about a previous calculation or scenario, use the memory context to provide accurate information.
                """
                
                # Generate response using conversation history
                messages_for_llm = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
                
                response = llm.invoke(messages_for_llm)
                
                # Store this interaction in memory
                interaction_memory = {
                    "data": f"User asked: {user_input}. Assistant responded: {response.content[:200]}...",
                    "timestamp": datetime.now().isoformat(),
                    "type": "conversation",
                    "user_input": user_input,
                    "response_preview": response.content[:200] + "..." if len(response.content) > 200 else response.content
                }
                store.put(namespace, str(uuid.uuid4()), interaction_memory)
                
                # If this looks like profile information, store it
                profile_keywords = ['age', 'income', 'savings', 'retirement', 'monthly', 'years old', 'earn', 'save']
                if any(keyword in user_input.lower() for keyword in profile_keywords):
                    extracted_profile = extract_profile_data_from_input(user_input)
                    if extracted_profile:
                        profile_memory = {
                            "data": f"Profile update: {user_input}",
                            "timestamp": datetime.now().isoformat(),
                            "type": "profile_update",
                            "profile_data": extracted_profile
                        }
                        store.put(namespace, f"profile_{uuid.uuid4()}", profile_memory)
                        
                        # Update session state profile
                        st.session_state.user_profile.update(extracted_profile)
                
                return {"messages": state["messages"] + [AIMessage(content=response.content)]}
            
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Let's continue with your financial planning."
            return {"messages": state["messages"] + [AIMessage(content=error_msg)]}
    
    # Build the graph
    builder = StateGraph(FinancialChatState)
    builder.add_node("financial_chat", financial_chat_node)
    builder.add_edge(START, "financial_chat")
    
    # Compile with memory components
    store, checkpointer = initialize_memory_system()
    graph = builder.compile(
        checkpointer=checkpointer,
        store=store,
    )
    
    return graph

def extract_profile_data_from_input(user_input: str) -> Dict[str, Any]:
    """Extract profile data from user input"""
    import re
    
    profile_data = {}
    user_input_lower = user_input.lower()
    
    # Extract age
    age_match = re.search(r'(\d+)\s*years?\s*old|age\s*(?:is\s*)?(\d+)|i\'?m\s*(\d+)', user_input_lower)
    if age_match:
        age = int(age_match.group(1) or age_match.group(2) or age_match.group(3))
        if 18 <= age <= 100:
            profile_data['age'] = age
    
    # Extract monetary amounts
    money_matches = re.findall(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', user_input.replace(',', ''))
    if money_matches:
        amounts = [float(m.replace(',', '')) for m in money_matches]
        
        if 'income' in user_input_lower or 'earn' in user_input_lower:
            profile_data['monthly_income'] = amounts[0]
        elif 'save' in user_input_lower and 'month' in user_input_lower:
            profile_data['monthly_savings'] = amounts[0]
        elif 'current' in user_input_lower and 'savings' in user_input_lower:
            profile_data['current_savings'] = amounts[0]
    
    return profile_data

def show_thinking_indicator(message="Thinking..."):
    """Show modern thinking indicator"""
    thinking_placeholder = st.empty()
    
    thinking_html = f"""
    <div class="thinking-indicator">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 8px; height: 8px; background: var(--primary-600); border-radius: 50%; animation: bounce 1.4s ease-in-out infinite both;"></div>
            <div style="width: 8px; height: 8px; background: var(--primary-600); border-radius: 50%; animation: bounce 1.4s ease-in-out 0.2s infinite both;"></div>
            <div style="width: 8px; height: 8px; background: var(--primary-600); border-radius: 50%; animation: bounce 1.4s ease-in-out 0.4s infinite both;"></div>
            <span style="margin-left: 0.5rem; font-weight: 600;">{message}</span>
        </div>
    </div>
    
    <style>
    @keyframes bounce {{
        0%, 80%, 100% {{ transform: scale(0); }}
        40% {{ transform: scale(1); }}
    }}
    </style>
    """
    
    thinking_placeholder.markdown(thinking_html, unsafe_allow_html=True)
    return thinking_placeholder

def process_user_message(user_input: str):
    """Process user message through LangGraph with proper memory persistence"""
    if not st.session_state.graph:
        st.error("Chat system not initialized properly")
        return
    
    # Show thinking indicator
    thinking_placeholder = show_thinking_indicator("Processing your message...")
    
    try:
        # Prepare config for LangGraph
        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id,
                "user_id": st.session_state.user_id,
            }
        }
        
        # Convert session messages to LangGraph format
        langgraph_messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                langgraph_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langgraph_messages.append(AIMessage(content=msg["content"]))
        
        # Add the new user message
        langgraph_messages.append(HumanMessage(content=user_input))
        
        # Create state with conversation history
        state = {
            "messages": langgraph_messages,
            "user_profile": st.session_state.get('user_profile', {}),
            "conversation_phase": st.session_state.get('conversation_phase', 'interactive'),
            "current_question_index": st.session_state.get('current_question_index', 0),
            "calculation_history": st.session_state.get('calculation_history', [])
        }
        
        # Stream response from graph
        response_content = ""
        final_state = None
        
        for chunk in st.session_state.graph.stream(
            state,
            config,
            stream_mode="values",
        ):
            if chunk.get("messages"):
                final_state = chunk
                # Get the latest assistant message
                for msg in reversed(chunk["messages"]):
                    if isinstance(msg, AIMessage):
                        response_content = msg.content
                        break
        
        # Clear thinking indicator
        thinking_placeholder.empty()
        
        # Update session state with new messages
        if response_content:
            # Add user message to session state
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # Add assistant response to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now()
            })
            
            # Update other state variables if they changed
            if final_state:
                if 'user_profile' in final_state:
                    st.session_state.user_profile.update(final_state['user_profile'])
                if 'conversation_phase' in final_state:
                    st.session_state.conversation_phase = final_state['conversation_phase']
                if 'calculation_history' in final_state:
                    st.session_state.calculation_history = final_state['calculation_history']
        
    except Exception as e:
        thinking_placeholder.empty()
        error_msg = f"I encountered an error processing your message: {str(e)}. Please try again."
        
        # Add user message even if there was an error
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg,
            "timestamp": datetime.now()
        })

def show_progress_indicator():
    """Show modern progress indicator for persona building"""
    current_index = st.session_state.current_question_index
    total_questions = len(PERSONA_QUESTIONS)
    progress_percentage = (current_index / total_questions) * 100
    
    progress_html = f"""
    <div class="progress-container">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2);">
            <span style="font-weight: 600; color: var(--neutral-700);">Profile Completion</span>
            <span style="font-weight: 500; color: var(--neutral-600);">{current_index}/{total_questions} questions</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_percentage}%;"></div>
        </div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)

def display_user_profile():
    """Display user profile in sidebar with modern styling"""
    if st.session_state.user_profile:
        st.sidebar.markdown("### 📊 Your Financial Profile")
        
        profile = st.session_state.user_profile
        
        # Create profile metrics using native st.metric with border for better visibility
        if 'age' in profile:
            st.sidebar.metric("Age", f"{profile['age']} years", border=True)
        
        if 'retirement_age' in profile:
            st.sidebar.metric("Target Retirement", f"{profile['retirement_age']} years", border=True)
        
        if 'monthly_income' in profile:
            st.sidebar.metric("Monthly Income", f"${profile['monthly_income']:,.0f}", border=True)
        
        if 'current_savings' in profile:
            st.sidebar.metric("Current Savings", f"${profile['current_savings']:,.0f}", border=True)
        
        if 'monthly_savings' in profile:
            st.sidebar.metric("Monthly Savings", f"${profile['monthly_savings']:,.0f}", border=True)
        
        if 'expected_return' in profile:
            st.sidebar.metric("Expected Return", f"{profile['expected_return']:.1f}%", border=True)

def main():
    """Main application function"""
    # Apply modern styling
    apply_modern_styling()
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="fade-in-up">
        <h1>💰 Valura AI Financial Advisor</h1>
        <p style="text-align: center; color: var(--neutral-600); font-size: 1.125rem; margin-bottom: 2rem;">
            Your intelligent financial planning companion with enhanced memory
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("🔄 Start Over", key="start_over"):
            # Clear session state
            for key in list(st.session_state.keys()):
                if key != 'initialized':
                    del st.session_state[key]
            st.rerun()
        
        if st.button("⏭️ Skip to Analysis", key="skip_to_analysis"):
            # Use default values and skip to calculation
            default_profile = {
                'age': 35,
                'retirement_age': 65,
                'monthly_income': 5000,
                'current_savings': 25000,
                'monthly_savings': 500,
                'expected_return': 7.0
            }
            st.session_state.conversation_phase = 'interactive'
            st.session_state.user_profile = default_profile
            st.session_state.original_baseline = default_profile.copy()  # Store original baseline
            st.rerun()
        
        # Show progress if in persona building phase
        if st.session_state.conversation_phase == 'persona_building':
            show_progress_indicator()
            
            # Show current question info
            current_q = get_current_question()
            if current_q:
                st.markdown(f"""
                <div style="
                    background: var(--primary-50);
                    border: 1px solid var(--primary-200);
                    border-radius: var(--radius-md);
                    padding: var(--space-4);
                    margin: var(--space-4) 0;
                    color: var(--primary-800);
                ">
                    <div style="font-weight: 600; margin-bottom: var(--space-2);">
                        Current Question:
                    </div>
                    <div style="font-size: 0.875rem;">
                        {current_q['question'][:50]}{'...' if len(current_q['question']) > 50 else ''}
                    </div>
                    <div style="font-size: 0.75rem; margin-top: var(--space-2); opacity: 0.8;">
                        {'Required' if current_q['mandatory'] else 'Optional'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display user profile
        display_user_profile()
        
        # Memory status
        st.markdown("### 🧠 Memory Status")
        st.success("✅ Enhanced memory active")
        st.info(f"Thread ID: {st.session_state.thread_id[:8]}...")
        
        # Quick calculation examples - only show in interactive phase
        if st.session_state.conversation_phase == 'interactive':
            st.markdown("### 💡 Try These Examples")
            
            example_buttons = [
                ("What if I save $200 more per month?", "scenario_example"),
                ("How long will my money last if I withdraw $3,000/month?", "withdrawal_example"),
                ("Explain the calculation step by step", "explain_example")
            ]
            
            for example_text, key in example_buttons:
                if st.button(example_text, key=key, help="Click to try this example", use_container_width=True):
                    # Add the example to chat
                    st.session_state.messages.append({
                        "role": "user",
                        "content": example_text,
                        "timestamp": datetime.now()
                    })
                    process_user_message(example_text)
                    st.rerun()
    
    # Chat Interface
    st.markdown("### 💬 Chat with Your Financial Advisor")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Show current question options if in persona building phase
    if st.session_state.conversation_phase == 'persona_building':
        current_q = get_current_question()
        if current_q:
            # Enhanced question display with modern styling
            question_html = f"""
            <div style="
                background: white;
                border: 2px solid var(--primary-300);
                border-radius: var(--radius-xl);
                padding: var(--space-8);
                margin: var(--space-6) 0;
                box-shadow: var(--shadow-lg);
                animation: questionSlide 0.5s ease-out;
            ">
                <div style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--primary-700);
                    margin-bottom: var(--space-4);
                    text-align: center;
                ">
                    📝 {current_q['question']}
                </div>
                <div style="
                    font-size: 0.875rem;
                    color: var(--neutral-600);
                    text-align: center;
                    margin-bottom: var(--space-4);
                    font-weight: 500;
                ">
                    Question {st.session_state.current_question_index + 1} of {len(PERSONA_QUESTIONS)}
                    {' (Optional)' if not current_q['mandatory'] else ' (Required)'}
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
            
            # Render the question input
            render_question_input(current_q)
            
            # Skip option for non-mandatory questions
            if not current_q['mandatory']:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("⏭️ Skip this question", use_container_width=True, key="skip_question"):
                        st.session_state.current_question_index += 1
                        add_message("user", "Skipped")
                        add_message("assistant", "⏭️ Skipped - no problem!")
                        next_question_or_complete()
                        st.rerun()
    
    # Show helpful suggestions in interactive phase
    elif st.session_state.conversation_phase == 'interactive':
        st.markdown("""
        <div style="
            background: var(--primary-50);
            border: 2px solid var(--primary-200);
            border-radius: var(--radius-lg);
            padding: var(--space-6);
            margin: var(--space-4) 0;
            box-shadow: var(--shadow-md);
        ">
            <div style="
                font-size: 1.125rem;
                font-weight: 600;
                color: var(--primary-800);
                margin-bottom: var(--space-4);
                text-align: center;
            ">💡 Try asking me about:</div>
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: var(--space-2);
                font-size: 0.875rem;
            ">
                <div style="color: var(--primary-700); font-weight: 500;">• "What if I save $200 more per month?"</div>
                <div style="color: var(--primary-700); font-weight: 500;">• "How long will my money last if I withdraw $3,000/month?"</div>
                <div style="color: var(--primary-700); font-weight: 500;">• "Explain the calculation step by step"</div>
                <div style="color: var(--primary-700); font-weight: 500;">• "What if I get 8% returns instead?"</div>
                <div style="color: var(--primary-700); font-weight: 500;">• "How much do I need for $1 million?"</div>
                <div style="color: var(--primary-700); font-weight: 500;">• "Should I pay off debt or invest?"</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input - only show if not in persona building or if persona building is complete
    if st.session_state.conversation_phase != 'persona_building' or get_current_question() is None:
        if prompt := st.chat_input("Ask me about your financial planning..."):
            # Process the message (this will update session state)
            process_user_message(prompt)
            
            # Rerun to display the new messages
            st.rerun()
    
    # Handle text input during persona building
    elif st.session_state.conversation_phase == 'persona_building':
        if prompt := st.chat_input("Type your answer or use the controls above..."):
            current_q = get_current_question()
            if current_q:
                try:
                    # Parse and validate input based on question type
                    if current_q['type'] == 'number':
                        value = float(prompt.replace('$', '').replace(',', '').replace('%', ''))
                        if current_q['validation'](value):
                            st.session_state.user_profile[current_q['id']] = int(value)
                            st.session_state.current_question_index += 1
                            add_message("user", prompt)
                            add_message("assistant", f"✅ Got it! {current_q['id'].replace('_', ' ').title()}: {value}")
                            next_question_or_complete()
                        else:
                            add_message("user", prompt)
                            add_message("assistant", "❌ That value seems out of range. Please use the controls above or try again.")
                    
                    elif current_q['type'] == 'currency':
                        value = float(prompt.replace('$', '').replace(',', ''))
                        if current_q['validation'](value):
                            st.session_state.user_profile[current_q['id']] = value
                            st.session_state.current_question_index += 1
                            add_message("user", prompt)
                            add_message("assistant", f"✅ Perfect! {current_q['id'].replace('_', ' ').title()}: ${value:,}")
                            next_question_or_complete()
                        else:
                            add_message("user", prompt)
                            add_message("assistant", "❌ Please enter a valid amount (e.g., 5000 or $5,000) or use the controls above.")
                    
                    elif current_q['type'] == 'percentage':
                        value = float(prompt.replace('%', ''))
                        if current_q['validation'](value):
                            st.session_state.user_profile[current_q['id']] = value
                            st.session_state.current_question_index += 1
                            add_message("user", prompt)
                            add_message("assistant", f"✅ Great! Expected return: {value}%")
                            next_question_or_complete()
                        else:
                            add_message("user", prompt)
                            add_message("assistant", "❌ Please enter a percentage between 0 and 20 or use the controls above.")
                    
                    elif current_q['type'] == 'select':
                        if prompt.title() in current_q['options']:
                            st.session_state.user_profile[current_q['id']] = prompt.title()
                            st.session_state.current_question_index += 1
                            add_message("user", prompt)
                            add_message("assistant", f"✅ Noted! Risk tolerance: {prompt.title()}")
                            next_question_or_complete()
                        else:
                            add_message("user", prompt)
                            add_message("assistant", f"❌ Please choose from: {', '.join(current_q['options'])} or use the dropdown above.")
                    
                    elif current_q['type'] == 'text':
                        st.session_state.user_profile[current_q['id']] = prompt
                        st.session_state.current_question_index += 1
                        add_message("user", prompt)
                        add_message("assistant", f"✅ Thanks for sharing: {prompt}")
                        next_question_or_complete()
                    
                except ValueError:
                    add_message("user", prompt)
                    add_message("assistant", "❌ I couldn't understand that format. Please use the controls above or try again with a number.")
                
                st.rerun()
    
    # Footer
    st.markdown("""
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--neutral-200); text-align: center; color: var(--neutral-500);">
        <p>Powered by LangGraph Memory Management & Google Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()