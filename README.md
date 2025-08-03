# Valura Financial Planning Agent

The Valura Financial Planning Agent is designed to assist users in planning their retirement by collecting relevant information, running financial calculations, and providing actionable insights.

## Features

- **Persona Builder**: Collects user information to build a financial profile.
- **Financial Calculations**: Runs retirement planning formulas using Python.
- **Real-Time Data**: Integrates APIs like Tavily and Yahoo Finance for real-time insights.
- **Streamlit UI**: Provides a modern web interface for interaction.
- **Comprehensive Testing**: Includes both functionality and API integration tests.

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

4. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```
   
   Alternative (if you want to run the modular version):
   ```bash
   python -m streamlit run src/ui/main.py
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

1. Access the Streamlit application through your browser at the provided localhost address.
2. Interact with the Financial Planning Agent by providing your financial details and receive calculations.

## Documentation

Comprehensive documentation is available:

- **[Complete Documentation](docs/DOCUMENTATION.md)** - Full system overview, architecture, and features
- **[User Guide](docs/USER_GUIDE.md)** - Step-by-step guide for end users


## Key Features

- **🤖 AI-Powered Conversations**: Natural language interface using Google Gemini
- **🧠 Enhanced Memory**: LangGraph-powered memory system that remembers conversations
- **📊 Financial Calculations**: Retirement planning with proven formulas
- **🎯 Scenario Analysis**: "What-if" calculations for different savings strategies
- **💡 Detailed Explanations**: Step-by-step breakdown of financial calculations
- **📱 Modern UI**: Professional Streamlit interface with responsive design
- **⚡ Real-time Results**: Instant calculations and analysis
- **🔄 Persistent State**: Conversations and calculations are remembered across interactions

