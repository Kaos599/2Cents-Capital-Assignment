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

# CSS Styling
def apply_chat_styling():
    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 2rem;
    }
    
    .quick-option-btn {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-option-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    .profile-complete {
        background: linear-gradient(45deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
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

# Show thinking indicator
def show_thinking_indicator(message="Calculating..."):
    thinking_placeholder = st.empty()
    for i in range(3):
        thinking_placeholder.markdown(f"🤔 {message} {'.' * (i + 1)}")
        time.sleep(0.5)
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
    
    # Extract percentages
    percent_matches = re.findall(r'([0-9]+(?:\.[0-9]+)?)%', user_input)
    if percent_matches:
        params['percentage'] = float(percent_matches[0])
    
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
        if any(phrase in user_lower for phrase in ['how long', 'last', 'withdraw', 'take out']):
            # Withdrawal longevity question
            retirement_fund = profile.get('current_savings', 100000)
            if st.session_state.calculation_history:
                retirement_fund = st.session_state.calculation_history[-1]['result']['total_fund']
            
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
                years = result['years_lasting']
                months = result['months_lasting']
                duration_text = f"⏰ Duration: {years:.1f} years ({months:.0f} months)"
                explanation = "⚠️ Limited duration - consider reducing withdrawal amount."
            
            four_percent = result['four_percent_rule_monthly']
            
            return f"""📉 Withdrawal Analysis for ${withdrawal_amount:,.0f}/month:

💰 Retirement Fund: ${retirement_fund:,.0f}
📊 Monthly Withdrawal: ${withdrawal_amount:,.0f}
{duration_text}

{explanation}

💡 4% Rule Reference: ${four_percent:,.0f}/month is considered safe
📈 Your withdrawal is {result['withdrawal_vs_four_percent']:.1f}x the 4% rule"""

        elif any(phrase in user_lower for phrase in ['what if', 'save more', 'increase', 'scenario']):
            # Scenario analysis
            current_monthly = profile.get('monthly_savings', 500)
            
            if 'amount' in params:
                new_monthly = params['amount']
            elif 'percentage' in params:
                new_monthly = current_monthly * (1 + params['percentage'] / 100)
            else:
                new_monthly = current_monthly * 1.2  # Default 20% increase
            
            scenario_result = calculate_retirement_timeline(
                current_age=profile.get('age', 30),
                retirement_age=profile.get('retirement_age', 65),
                monthly_savings=new_monthly,
                expected_return=profile.get('expected_return', 7.0),
                current_savings=profile.get('current_savings', 10000)
            )
            
            # Compare with original
            original_fund = 0
            if st.session_state.calculation_history:
                original_fund = st.session_state.calculation_history[-1]['result']['total_fund']
            
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
            
            return f"""🔄 Scenario Analysis: Monthly savings ${current_monthly:,.0f} → ${new_monthly:,.0f}

📈 New Monthly Savings: ${new_monthly:,.0f} (+${new_monthly - current_monthly:,.0f})
💰 New Retirement Fund: ${new_fund:,.0f}
📊 Additional Money: ${difference:,.0f} ({increase_percent:.1f}% increase)

🎯 That's ${difference:,.0f} more for retirement!
💡 Each extra $100/month adds approximately ${difference / ((new_monthly - current_monthly) / 100):,.0f} to your retirement fund."""

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
        return f"I encountered an error with that calculation: {str(e)}. Could you try rephrasing your question?"

# Main app
def main():
    apply_chat_styling()
    initialize_session_state()
    
    # Header
    st.title("🏦 Valura AI Financial Advisor")
    st.markdown("---")
    
    # Sidebar - Profile Status
    with st.sidebar:
        st.header("👤 Your Profile")
        
        profile = st.session_state.user_profile
        if profile:
            for key, value in profile.items():
                if key in ['monthly_income', 'current_savings', 'monthly_savings']:
                    st.metric(key.replace('_', ' ').title(), f"${value:,}")
                elif key == 'expected_return':
                    st.metric(key.replace('_', ' ').title(), f"{value}%")
                else:
                    st.metric(key.replace('_', ' ').title(), str(value))
        else:
            st.info("Complete the chat to see your profile here")
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        if st.button("🔄 Start Over", use_container_width=True):
            for key in ['messages', 'user_profile', 'conversation_phase', 'current_question_index', 'calculation_history']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        if st.button("⏭️ Skip to Calculation", use_container_width=True):
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
            st.markdown("---")
            st.markdown(f"### Current Question: {current_q['question']}")
            render_question_input(current_q)
            
            # Skip option for non-mandatory questions
            if not current_q['mandatory']:
                if st.button("⏭️ Skip this question", use_container_width=True):
                    st.session_state.current_question_index += 1
                    add_message("user", "Skipped")
                    next_question_or_complete()
                    st.rerun()
    
    # Chat input
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

if __name__ == "__main__":
    main()
