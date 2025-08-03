"""
Enhanced Valura Financial Planning Agent with Real-time Market Data
Integrates Tavily and yfinance APIs for current market information
"""

import streamlit as st
import os
from datetime import datetime
import sys
import json

# Add src directory to path for imports
sys.path.append('src')

# Import existing modules
from tools.market_data_tool import MarketDataTool
from calculators.step_by_step_calculator import (
    calculate_scenario_step_by_step,
    format_step_by_step_response,
    calculate_withdrawal_longevity_step_by_step,
    format_withdrawal_analysis
)

# Import Google Gemini
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    st.error("Google Gemini not available. Please install: pip install langchain-google-genai")

# Page configuration
st.set_page_config(
    page_title="Valura Financial Planning Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
def apply_chat_styling():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .market-data-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2563eb;
        margin: 1rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2563eb;
    }
    
    .user-message {
        background-color: #eff6ff;
        border-left-color: #3b82f6;
    }
    
    .assistant-message {
        background-color: #f8fafc;
        border-left-color: #2563eb;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .success-message {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #22c55e;
    }
    
    .error-message {
        background-color: #fef2f2;
        color: #dc2626;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #ef4444;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    
    if 'conversation_phase' not in st.session_state:
        st.session_state.conversation_phase = "persona_building"
    
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    if 'calculation_history' not in st.session_state:
        st.session_state.calculation_history = []
    
    if 'market_data_tool' not in st.session_state:
        st.session_state.market_data_tool = MarketDataTool()

def initialize_gemini():
    """Initialize Google Gemini AI"""
    if not GEMINI_AVAILABLE:
        return None
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        st.error("Please set your GOOGLE_API_KEY environment variable")
        return None
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=google_api_key,
            temperature=0.7
        )
        return llm
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        return None

def display_market_data_sidebar():
    """Display real-time market data in sidebar"""
    st.sidebar.markdown("### 📊 Live Market Data")
    
    # Get current savings rates
    with st.sidebar.expander("💰 Current Savings Rates (India)", expanded=False):
        try:
            rates_data = st.session_state.market_data_tool.get_current_savings_rates_india()
            
            if "error" not in rates_data:
                st.success(f"Updated: {rates_data.get('query_date', 'N/A')}")
                
                # Display sources
                for i, source in enumerate(rates_data.get('sources', [])[:3]):
                    with st.container():
                        st.markdown(f"**{source.get('title', 'N/A')[:50]}...**")
                        st.caption(source.get('content_snippet', 'No preview available'))
                        if source.get('url'):
                            st.markdown(f"[Read more]({source['url']})")
                        st.divider()
            else:
                st.error(rates_data.get('message', 'Failed to fetch data'))
                
        except Exception as e:
            st.error(f"Error loading market data: {e}")
    
    # Get Indian market indices
    with st.sidebar.expander("📈 Indian Market Indices", expanded=False):
        try:
            indices_data = st.session_state.market_data_tool.get_indian_market_indices()
            
            for index_name, data in indices_data.get('indices', {}).items():
                if "error" not in data:
                    current_price = data.get('current_price')
                    change_percent = data.get('historical_data', {}).get('price_change_percent', 0)
                    
                    # Color based on performance
                    color = "🟢" if change_percent >= 0 else "🔴"
                    
                    st.metric(
                        label=f"{color} {index_name}",
                        value=f"{current_price:.2f}" if current_price else "N/A",
                        delta=f"{change_percent:.2f}%" if change_percent else None
                    )
                else:
                    st.error(f"{index_name}: Data unavailable")
                    
        except Exception as e:
            st.error(f"Error loading indices: {e}")

def handle_market_data_query(user_input: str) -> str:
    """Handle market data related queries"""
    user_input_lower = user_input.lower()
    
    # Check for savings rate queries
    if any(keyword in user_input_lower for keyword in ['savings rate', 'interest rate', 'bank rate', 'deposit rate']):
        if 'india' in user_input_lower or 'indian' in user_input_lower:
            rates_data = st.session_state.market_data_tool.get_current_savings_rates_india()
            
            if "error" not in rates_data:
                response = "📊 **Current Savings Account Rates in India:**\n\n"
                response += f"*Data updated: {rates_data.get('query_date', 'N/A')}*\n\n"
                
                for source in rates_data.get('sources', [])[:3]:
                    response += f"**{source.get('title', 'Source')}**\n"
                    response += f"{source.get('content_snippet', 'No details available')}\n"
                    if source.get('url'):
                        response += f"[Read full article]({source['url']})\n\n"
                
                response += "\n💡 **For your retirement planning:** These current rates can help you understand the baseline returns on safe investments like savings accounts. Consider this when setting your expected return assumptions."
                
                return response
            else:
                return f"❌ I couldn't fetch the current savings rates: {rates_data.get('message', 'Unknown error')}"
    
    # Check for market/stock queries
    if any(keyword in user_input_lower for keyword in ['market', 'stock', 'nifty', 'sensex', 'share']):
        indices_data = st.session_state.market_data_tool.get_indian_market_indices()
        
        response = "📈 **Current Indian Market Status:**\n\n"
        response += f"*Last updated: {indices_data.get('last_updated', 'N/A')}*\n\n"
        
        for index_name, data in indices_data.get('indices', {}).items():
            if "error" not in data:
                current_price = data.get('current_price', 0)
                change_percent = data.get('historical_data', {}).get('price_change_percent', 0)
                
                trend = "📈" if change_percent >= 0 else "📉"
                response += f"{trend} **{index_name}**: {current_price:.2f} ({change_percent:+.2f}%)\n"
            else:
                response += f"❌ **{index_name}**: Data unavailable\n"
        
        response += "\n💡 **Investment Insight:** Market performance can help inform your expected return assumptions for equity investments in your retirement portfolio."
        
        return response
    
    # Check for investment news queries
    if any(keyword in user_input_lower for keyword in ['news', 'latest', 'current events', 'market news']):
        news_data = st.session_state.market_data_tool.search_financial_news("India financial markets investment")
        
        if "error" not in news_data:
            response = "📰 **Latest Financial News:**\n\n"
            
            for article in news_data.get('articles', [])[:3]:
                response += f"**{article.get('title', 'News Article')}**\n"
                response += f"{article.get('content', 'No summary available')[:200]}...\n"
                if article.get('url'):
                    response += f"[Read full article]({article['url']})\n\n"
            
            return response
        else:
            return f"❌ I couldn't fetch the latest news: {news_data.get('message', 'Unknown error')}"
    
    return None

def generate_ai_response(user_input: str, context: dict) -> str:
    """Generate AI response using Gemini with market data integration"""
    llm = initialize_gemini()
    if not llm:
        return "I'm sorry, but I'm currently unable to process your request. Please check the AI configuration."
    
    # First check if this is a market data query
    market_response = handle_market_data_query(user_input)
    if market_response:
        return market_response
    
    # Build context for AI
    system_prompt = f"""
    You are Valura, an expert financial planning assistant with access to real-time market data.
    
    Current conversation context:
    - User profile: {context.get('user_profile', {})}
    - Conversation phase: {context.get('conversation_phase', 'unknown')}
    - Previous calculations: {len(context.get('calculation_history', []))} calculations performed
    
    You have access to:
    1. Real-time savings account interest rates in India
    2. Current Indian market indices (NIFTY, SENSEX, etc.)
    3. Latest financial news and market insights
    4. Advanced financial calculators for retirement planning
    
    Guidelines:
    - Provide practical, actionable financial advice
    - Use real market data when relevant to the user's questions
    - Be encouraging and supportive about retirement planning
    - Explain financial concepts clearly
    - When discussing returns, reference current market conditions
    
    Current date: {datetime.now().strftime('%B %d, %Y')}
    """
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        return f"I apologize, but I encountered an error processing your request: {str(e)}"

def main():
    """Main application function"""
    apply_chat_styling()
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💰 Valura Financial Planning Agent</h1>
        <p>Your AI-powered retirement planning assistant with real-time market data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.markdown("### 💬 Chat with Your Financial Advisor")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about retirement planning, current market rates, or financial advice..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your question and fetching latest market data..."):
                    context = {
                        'user_profile': st.session_state.user_profile,
                        'conversation_phase': st.session_state.conversation_phase,
                        'calculation_history': st.session_state.calculation_history
                    }
                    
                    response = generate_ai_response(prompt, context)
                    st.markdown(response)
                    
                    # Add assistant message
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    with col2:
        # Sidebar with market data
        display_market_data_sidebar()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("📊 Get Current Savings Rates", use_container_width=True):
            rates_response = handle_market_data_query("current savings rates in India")
            st.session_state.messages.append({"role": "assistant", "content": rates_response})
            st.rerun()
        
        if st.button("📈 Check Market Status", use_container_width=True):
            market_response = handle_market_data_query("current Indian market indices")
            st.session_state.messages.append({"role": "assistant", "content": market_response})
            st.rerun()
        
        if st.button("📰 Latest Financial News", use_container_width=True):
            news_response = handle_market_data_query("latest financial news India")
            st.session_state.messages.append({"role": "assistant", "content": news_response})
            st.rerun()
        
        # API Status
        st.markdown("### 🔧 API Status")
        
        # Check Tavily API
        tavily_status = "✅ Connected" if st.session_state.market_data_tool.tavily_client else "❌ Not configured"
        st.markdown(f"**Tavily API:** {tavily_status}")
        
        # Check yfinance
        st.markdown("**Yahoo Finance:** ✅ Available")
        
        # Check Gemini
        gemini_status = "✅ Connected" if os.getenv('GOOGLE_API_KEY') else "❌ Not configured"
        st.markdown(f"**Google Gemini:** {gemini_status}")
        
        # Configuration help
        with st.expander("🔧 Configuration Help"):
            st.markdown("""
            **Required Environment Variables:**
            
            1. `GOOGLE_API_KEY` - For AI responses
            2. `TAVILY_API_KEY` - For real-time market data (optional)
            
            **Setup Instructions:**
            1. Create a `.env` file in your project root
            2. Add your API keys:
               ```
               GOOGLE_API_KEY=your_google_api_key_here
               TAVILY_API_KEY=your_tavily_api_key_here
               ```
            3. Restart the application
            """)

if __name__ == "__main__":
    main()