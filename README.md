# 🏦 Valura Financial Planning Agent

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.43.0%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0%2B-1C3C3C?logo=langchain&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0%2B-FF6B6B?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> 🤖 **AI-Powered Retirement Planning** | Build personalized retirement plans through conversational AI with real-time market data integration

The Valura Financial Planning Agent is an intelligent conversational system that combines **persona building**, **financial calculations**, and **real-time market data** to help users create comprehensive retirement plans. Built with Google Gemini 2.5 Flash, LangChain, and LangGraph for sophisticated memory management.

## ✨ Key Features

| Feature | Description | Technology |
|---------|-------------|------------|
| 🧠 **AI Persona Builder** | Guided conversation flow with 8 structured questions | LangGraph + Gemini 2.5 Flash |
| 🧮 **Financial Engine** | Future Value, Present Value, NPER, Rule of 72 calculations | Pure Python Functions |
| 📊 **Real-Time Market Data** | Live Indian market indices, savings rates, financial news | Tavily API + Yahoo Finance |
| 💬 **Conversational AI** | Natural language Q&A with context-aware responses | Google Gemini 2.5 Flash |
| 🔄 **Memory Management** | Persistent conversation state and calculation history | LangGraph State Management |
| 📱 **Modern UI** | Professional web interface with live market sidebar | Streamlit + Custom CSS |
| 🧪 **Comprehensive Testing** | Unit tests and real API integration tests | pytest + Custom Test Suite |

### 🇮🇳 Indian Market Integration
- **Live Market Indices**: NIFTY 50, BSE SENSEX, NIFTY BANK, NIFTY IT
- **Current Savings Rates**: Real-time rates from major Indian banks (SBI, HDFC, ICICI)
- **Financial News**: Latest market updates and RBI policy changes
- **Smart Recommendations**: Market-aware investment advice

## 🚀 Quick Start

### Prerequisites
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)
![Conda](https://img.shields.io/badge/Conda-Optional-green?style=flat-square)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Valura-FinancialPlanning-Agent

# 2. Create virtual environment (recommended)
conda create -n langgraph python=3.11
conda activate langgraph

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env  # Edit with your API keys
```

### Environment Configuration
Create a `.env` file with your API keys:

```ini
# Required for AI chat functionality
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional for real-time market data
TAVILY_API_KEY=your_tavily_api_key_here
```

### Launch Application

```bash
# Enhanced version with market data
streamlit run enhanced_financial_chat_app.py

# Alternative versions
streamlit run app.py                    # Basic version
streamlit run financial_chat_app.py     # Chat version
python -m streamlit run src/ui/main.py  # Modular version
```

🌐 **Access**: Open your browser to `http://localhost:8501`

### 🧪 Test Integration

```bash
# Test market data APIs
python test_market_integration.py

# Run comprehensive tests
pytest tests/test_agent_functionality.py -v
pytest tests/test_real_api_integration.py -v -s
```

## 💡 Usage Guide

### 🎯 Getting Started
1. **Launch the application** using any of the streamlit commands above
2. **Complete your financial profile** through guided conversation (8 questions)
3. **Get instant retirement calculations** with real-time market context
4. **Explore scenarios** with "What if..." questions
5. **Access live market data** in the sidebar

### 💬 Sample Conversations

```
👤 User: "I'm 35, save $1000 monthly, expect 6% return. When can I retire?"
🤖 Agent: Based on your profile, you can retire at 65 with $1.2M. 
         With current Indian savings rates at 3-4%, consider...

👤 User: "What if I save $200 more per month?"
🤖 Agent: 🔄 Scenario Analysis: +$200/month = $1.45M at retirement
         📈 Additional fund: $250K | Earlier retirement: Age 63

👤 User: "Show me today's market performance"
🤖 Agent: 📊 Current Market Status:
         • NIFTY 50: 24,565 (-0.47%)
         • SENSEX: 80,599 (-0.36%)
         • Current SBI savings rate: 3.0%
```

### 🔧 Advanced Features

| Feature | Command | Description |
|---------|---------|-------------|
| **Scenario Analysis** | "What if I save $X more?" | Compare different savings amounts |
| **Market Insights** | "Current savings rates?" | Real-time Indian bank rates |
| **Calculation Details** | "Explain the math" | Step-by-step formula breakdown |
| **Retirement Timeline** | "When can I retire?" | Personalized retirement age calculation |
| **Withdrawal Planning** | "How long will $X last?" | Money longevity analysis |

## Documentation

Comprehensive documentation is available:

- **[Complete Documentation](docs/DOCUMENTATION.md)** - Full system overview, architecture, and features
- **[User Guide](docs/USER_GUIDE.md)** - Step-by-step guide for end users
- **[Design Architechure](docs\DESIGN_ARCHITECTURE.md)** - Design choices explained

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


## 🏗️ Architecture Overview

The Valura Financial Planning Agent leverages a sophisticated architecture combining **LangChain**, **LangGraph**, and **Google Gemini 2.5 Flash** for intelligent financial planning:

**Core Architecture Decisions:**
• **LangGraph State Management**: Implements conversation phases (`persona_building` → `profile_complete` → `interactive`) with persistent memory across user sessions
• **LangChain + Gemini Integration**: Uses `ChatGoogleGenerativeAI` wrapper for standardized LLM interactions with built-in conversation memory
• **Modular Tool Architecture**: Separate classes (`MarketDataTool`) with specific responsibilities for market data, calculations, and AI responses
• **Multi-API Integration**: Combines Tavily (search), Yahoo Finance (market data), and Google Gemini (conversational AI) with graceful fallbacks

**Key Trade-offs:**
• Streamlit session state vs. LangGraph's sophisticated memory (chose simplicity for MVP)
• Direct API calls vs. LangChain abstraction (chose standardization and flexibility)
• Real-time market data vs. static assumptions (chose enhanced user experience despite API dependencies)

## 📚 Enhanced Documentation

| Document | Description |
|----------|-------------|
| **[📖 Complete Documentation](docs/DOCUMENTATION.md)** | Full system overview, architecture, and features |
| **[👤 User Guide](docs/USER_GUIDE.md)** | Step-by-step guide for end users |
| **[🏗️ Design Architecture](docs/DESIGN_ARCHITECTURE.md)** | Technical architecture decisions and trade-offs |

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

```bash
# Development setup
git clone <repository-url>
cd Valura-FinancialPlanning-Agent
conda create -n langgraph-dev python=3.11
conda activate langgraph-dev
pip install -r requirements-dev.txt  # If available

# Run tests before submitting PR
pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini 2.5 Flash** for conversational AI capabilities
- **LangChain & LangGraph** for memory management and AI orchestration
- **Streamlit** for rapid UI development
- **Yahoo Finance** for reliable market data
- **Tavily** for real-time search capabilities

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

[![GitHub stars](https://img.shields.io/github/stars/username/Valura-FinancialPlanning-Agent?style=social)](https://github.com/username/Valura-FinancialPlanning-Agent/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/username/Valura-FinancialPlanning-Agent?style=social)](https://github.com/username/Valura-FinancialPlanning-Agent/network/members)

</div>