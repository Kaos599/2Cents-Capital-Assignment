# Valura Financial Planning Agent

The Valura Financial Planning Agent is designed to assist users in planning their retirement by collecting relevant information, running financial calculations, and providing actionable insights.

## Features

- **Persona Builder**: Collects user information to build a financial profile.
- **Financial Calculations**: Runs retirement planning formulas using Python.
- **Real-Time Market Data**: 
  - Current savings account interest rates in India via Tavily API
  - Live Indian market indices (NIFTY, SENSEX, NIFTY BANK, NIFTY IT)
  - Latest financial news and market insights
  - Real-time stock data via Yahoo Finance (yfinance)
- **AI-Powered Chat**: Google Gemini integration for intelligent financial advice
- **Streamlit UI**: Provides a modern web interface with live market data sidebar
- **Comprehensive Testing**: Includes both functionality and API integration tests

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Valura-FinancialPlanning-Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** (if not already present) and configure your API keys:
   ```ini
   GOOGLE_API_KEY=your_google_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

4. **Run the Enhanced Streamlit application**:
   ```bash
   streamlit run main.py
   ```
   

5. **Test the market data integration**:
   ```bash
   python test_market_integration.py
   ```

## Running Tests

- **Functionality and Workflow Tests**:
  ```bash
  pytest tests/test_agent_functionality.py -v
  ```

- **Real API Integration Tests**:
  ```bash
  pytest tests/test_real_api_integration.py -v -s
  ```

## Usage

### Enhanced Financial Planning Agent

1. **Launch the Enhanced Application**:
   ```bash
   streamlit run enhanced_financial_chat_app.py
   ```

2. **Access Real-Time Market Data**:
   - View live Indian market indices in the sidebar
   - Get current savings account interest rates
   - Access latest financial news and insights

3. **Ask Market-Related Questions**:
   - "What are the current savings rates in India?"
   - "Show me today's market performance"
   - "What's the latest financial news?"
   - "How do current rates affect my retirement planning?"

4. **Interactive Financial Planning**:
   - Build your financial profile through guided conversation
   - Get personalized retirement calculations
   - Explore different savings scenarios
   - Receive AI-powered financial advice with current market context

### Market Data Features

- **📊 Live Data Sources**:
  - Tavily API for real-time search and current rates
  - Yahoo Finance (yfinance) for market data and stock prices
  - Google Gemini for intelligent financial advice

- **🇮🇳 Indian Market Coverage**:
  - NIFTY 50, BSE SENSEX, NIFTY BANK, NIFTY IT indices
  - Major Indian bank savings account rates
  - RBI policy updates and financial news

- **💡 Smart Integration**:
  - Market data automatically incorporated into financial advice
  - Current rates used for realistic return assumptions
  - Real-time context for investment recommendations

## Documentation

Comprehensive documentation is available:

- **[Complete Documentation](docs/DOCUMENTATION.md)** - Full system overview, architecture, and features
- **[User Guide](docs/USER_GUIDE.md)** - Step-by-step guide for end users


## Key Features

- **🤖 AI-Powered Conversations**: Natural language interface using Google Gemini
- **📊 Real-Time Market Data**: Live savings rates, market indices, and financial news
- **🇮🇳 Indian Market Focus**: NIFTY, SENSEX, and major Indian bank rates
- **💰 Current Interest Rates**: Real-time savings account rates from major Indian banks
- **� Livae Market Tracking**: Current prices and performance of major indices
- **� Financ ial News Integration**: Latest market news and investment insights
- **🧮 Financial Calculations**: Retirement planning with proven formulas
- **🎯 Scenario Analysis**: "What-if" calculations for different savings strategies
- **💡 Detailed Explanations**: Step-by-step breakdown of financial calculations
- **📱 Modern UI**: Professional Streamlit interface with live market data sidebar
- **⚡ Real-time Results**: Instant calculations and analysis with current market context
- **🔄 Persistent State**: Conversations and calculations are remembered across interactions

