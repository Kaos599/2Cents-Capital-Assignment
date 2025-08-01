# Valura Financial Planning Agent - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [Technical Implementation](#technical-implementation)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

## Overview

The Valura Financial Planning Agent is an AI-powered conversational application built with Streamlit that helps users create personalized retirement plans. It combines the power of Google's Gemini AI with proven financial formulas to provide accurate retirement planning calculations and advice.

### Key Capabilities
- **Persona Building**: Collects user financial information through guided conversation
- **Financial Calculations**: Performs retirement timeline, savings longevity, and scenario analysis
- **Interactive Chat**: Natural language interface powered by Google Gemini
- **Real-time Analysis**: Instant calculations with detailed explanations
- **Professional UI**: Modern, responsive Streamlit interface

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                       │
├─────────────────────────────────────────────────────────────┤
│  Chat Interface  │  Sidebar Profile  │  Quick Actions      │
├─────────────────────────────────────────────────────────────┤
│                    Session Management                       │
├─────────────────────────────────────────────────────────────┤
│  Google Gemini AI  │  Financial Calculators  │  Validators │
├─────────────────────────────────────────────────────────────┤
│              Financial Formulas & Tools                     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Frontend**: Streamlit 1.43.0+
- **AI Engine**: Google Gemini 2.5 Flash via LangChain
- **Backend**: Python 3.8+
- **Financial Calculations**: Custom financial formulas
- **State Management**: Streamlit session state
- **Styling**: Custom CSS with gradient themes

## Features

### 1. Persona Building System
The agent collects user information through 8 structured questions:

| Field | Type | Description | Mandatory |
|-------|------|-------------|-----------|
| Age | Number | Current age (18-100) | Yes |
| Retirement Age | Number | Target retirement age (50-80) | Yes |
| Monthly Income | Currency | After-tax monthly income | Yes |
| Current Savings | Currency | Existing retirement savings | Yes |
| Monthly Savings | Currency | Monthly retirement contributions | Yes |
| Expected Return | Percentage | Expected annual investment return (0-20%) | Yes |
| Risk Tolerance | Select | Conservative/Moderate/Aggressive | No |
| Financial Goals | Text | Personal financial objectives | No |

### 2. Financial Calculations

#### Retirement Timeline Calculation
- **Formula**: Future Value of Annuity + Future Value of Lump Sum
- **Inputs**: Age, retirement age, savings, expected return
- **Outputs**: Total fund, inflation-adjusted value, years to retirement

#### Scenario Analysis
- **What-if calculations**: Modify savings amounts or returns
- **Comparison analysis**: Show impact of changes
- **Multiple scenarios**: Test different financial strategies

#### Withdrawal Planning
- **4% Rule application**: Safe withdrawal rate calculation
- **Longevity analysis**: How long money will last
- **Custom withdrawal amounts**: User-specified monthly withdrawals

### 3. Interactive Chat Interface

#### Conversation Phases
1. **Persona Building**: Guided question flow
2. **Profile Complete**: Initial calculation presentation
3. **Interactive**: Open-ended Q&A and analysis

#### Question Classification
The AI automatically classifies user questions into:
- **PERSONA**: Profile updates
- **CALCULATION**: Financial computations
- **SCENARIO**: What-if analysis
- **EXPLANATION**: Detailed breakdowns
- **ADVICE**: General financial guidance
- **GENERAL**: Other inquiries

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google API key for Gemini
- Required Python packages (see requirements.txt)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Valura-FinancialPlanning-Agent
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here  # Optional
   ```

4. **Run the Application**
   ```bash
   streamlit run financial_chat_app.py
   ```

5. **Access the Interface**
   Open your browser to `http://localhost:8501`

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key for AI responses |
| `TAVILY_API_KEY` | No | Tavily API key for web searches (future feature) |

## Usage Guide

### Getting Started

1. **Launch the Application**
   - Run `streamlit run financial_chat_app.py`
   - Navigate to the provided localhost URL

2. **Complete Your Profile**
   - Answer the guided questions about your financial situation
   - Use quick-select buttons for common values
   - Or type custom responses in the chat

3. **Review Your Retirement Plan**
   - View your projected retirement fund
   - See inflation-adjusted purchasing power
   - Understand the calculation breakdown

4. **Explore Scenarios**
   - Ask "What if I save more?" for scenario analysis
   - Try "How long will my money last?" for withdrawal planning
   - Request "Explain the calculation" for detailed formulas

### Sample Interactions

#### Profile Building
```
Agent: What's your current age?
User: 35
Agent: ✅ Got it! Age: 35

Agent: At what age would you like to retire?
User: 65
Agent: ✅ Perfect! Retirement Age: 65
```

#### Financial Analysis
```
User: What if I save $200 more per month?
Agent: 🔄 Scenario Analysis: Increasing savings by 20%
       📈 New Monthly Savings: $600 (+$100)
       💰 New Retirement Fund: $1,234,567
       📊 Additional Money: $123,456
```

#### Detailed Explanations
```
User: Explain the calculation
Agent: 🧮 Calculation Breakdown:
       Formula Used: Future Value of Annuity + Future Value of Lump Sum
       📈 Your Current Savings Growth: $50,000 → $400,000
       💰 Your Monthly Contributions Growth: $500/month → $800,000
       🎯 Total = $1,200,000
```

### Quick Actions

#### Sidebar Features
- **Profile Display**: Real-time view of collected information
- **Start Over**: Reset the entire conversation
- **Skip to Calculation**: Use default values for quick analysis

#### Chat Features
- **Quick Select Buttons**: Common values for each question
- **Manual Input**: Custom values via sliders and text inputs
- **Skip Options**: Optional questions can be skipped

## Technical Implementation

### Core Functions

#### Session State Management
```python
def initialize_session_state():
    """Initialize all session state variables for conversation tracking"""
    - messages: Chat conversation history
    - user_profile: Collected financial information
    - conversation_phase: Current stage of interaction
    - current_question_index: Progress through persona questions
    - calculation_history: Stored financial calculations
```

#### AI Integration
```python
def generate_ai_response(user_input: str, context: dict) -> str:
    """Generate contextual responses using Google Gemini"""
    - Processes user input with conversation context
    - Maintains professional financial advisor persona
    - Provides relevant, helpful responses
```

#### Financial Calculations
```python
def run_retirement_calculation():
    """Execute retirement timeline calculation"""
    - Uses future value formulas
    - Accounts for inflation
    - Stores results for future reference
```

### Data Structures

#### User Profile Schema
```python
{
    "age": int,                    # Current age
    "retirement_age": int,         # Target retirement age
    "monthly_income": float,       # After-tax monthly income
    "current_savings": float,      # Existing retirement savings
    "monthly_savings": float,      # Monthly contributions
    "expected_return": float,      # Expected annual return (%)
    "risk_tolerance": str,         # Conservative/Moderate/Aggressive
    "financial_goals": str         # Personal objectives
}
```

#### Calculation Result Schema
```python
{
    "type": str,                   # Calculation type
    "result": {
        "total_fund": float,       # Projected retirement fund
        "years_to_retirement": int, # Years until retirement
        "real_purchasing_power": float, # Inflation-adjusted value
        "calculation_details": {
            "fv_current_savings": float,
            "fv_monthly_contributions": float
        }
    },
    "timestamp": datetime          # When calculation was performed
}
```

### Financial Formulas

#### Future Value Calculations
```python
# Future Value of Lump Sum
FV = PV × (1 + r)^n

# Future Value of Annuity
FV = PMT × [(1 + r)^n - 1] / r

# Present Value of Annuity
PV = PMT × [1 - (1 + r)^(-n)] / r
```

Where:
- `PV` = Present Value
- `FV` = Future Value
- `PMT` = Payment (monthly contribution)
- `r` = Interest rate per period
- `n` = Number of periods

### Error Handling

#### Input Validation
- **Age Range**: 18-100 years
- **Retirement Age**: Must be greater than current age
- **Financial Values**: Non-negative numbers only
- **Percentage Values**: 0-20% range for expected returns

#### Exception Management
- **API Failures**: Graceful degradation when Gemini is unavailable
- **Calculation Errors**: User-friendly error messages
- **Input Parsing**: Robust handling of various input formats

## API Reference

### Core Functions

#### `initialize_session_state()`
Initializes all Streamlit session state variables.

**Parameters**: None
**Returns**: None
**Side Effects**: Sets up session state for conversation tracking

#### `classify_user_question(question: str) -> str`
Classifies user input using Google Gemini AI.

**Parameters**:
- `question` (str): User's input text

**Returns**: 
- `str`: Classification category (PERSONA, CALCULATION, SCENARIO, etc.)

#### `generate_ai_response(user_input: str, context: dict) -> str`
Generates AI responses using conversation context.

**Parameters**:
- `user_input` (str): User's message
- `context` (dict): Conversation context including profile and history

**Returns**:
- `str`: AI-generated response

#### `run_retirement_calculation()`
Executes retirement timeline calculation using user profile.

**Parameters**: None (uses session state)
**Returns**: None
**Side Effects**: Updates calculation history and conversation

#### `handle_financial_calculation(question_type: str, user_input: str)`
Processes financial calculation requests.

**Parameters**:
- `question_type` (str): Type of calculation requested
- `user_input` (str): User's specific question

**Returns**: None
**Side Effects**: Adds calculation results to conversation

### UI Components

#### `render_quick_options(question)`
Renders quick-select buttons for persona questions.

**Parameters**:
- `question` (dict): Question configuration with options

**Returns**: None
**Side Effects**: Creates interactive UI elements

#### `apply_chat_styling()`
Applies custom CSS styling to the interface.

**Parameters**: None
**Returns**: None
**Side Effects**: Injects CSS into Streamlit app

## Troubleshooting

### Common Issues

#### 1. "Failed to initialize Gemini API"
**Cause**: Missing or invalid Google API key
**Solution**: 
- Verify `GOOGLE_API_KEY` in `.env` file
- Ensure API key has Gemini access enabled
- Check API quota and billing status

#### 2. "Could not import financial modules"
**Cause**: Missing dependencies or incorrect file structure
**Solution**:
- Run `pip install -r requirements.txt`
- Verify `src/` directory structure exists
- Check Python path configuration

#### 3. Button Key Errors
**Cause**: Non-string values in button keys
**Solution**: 
- Ensure all button keys use string conversion
- Update to latest version with fixed key handling

#### 4. Calculation Errors
**Cause**: Invalid input values or missing profile data
**Solution**:
- Validate all numeric inputs
- Use default values for missing profile fields
- Check calculation function parameters

### Performance Optimization

#### Memory Management
- Session state is automatically managed by Streamlit
- Large calculation histories are limited to recent results
- Profile data is lightweight and efficient

#### Response Time
- AI responses typically take 1-3 seconds
- Financial calculations are near-instantaneous
- UI updates use Streamlit's efficient rerun system

### Debugging Tips

#### Enable Debug Mode
```python
# Add to top of financial_chat_app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Session State Inspection
```python
# Add to sidebar for debugging
st.sidebar.json(st.session_state)
```

#### Error Logging
```python
# Enhanced error handling
try:
    # Your code here
    pass
except Exception as e:
    st.error(f"Debug info: {str(e)}")
    logging.exception("Detailed error information")
```

## Contributing

### Development Setup

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt  # If available
   ```
4. **Make Changes**
5. **Test Thoroughly**
6. **Submit Pull Request**

### Code Standards

#### Python Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions with docstrings
- Maintain consistent naming conventions

#### Streamlit Best Practices
- Use `@st.cache_resource` for expensive operations
- Minimize session state usage
- Implement proper error handling
- Ensure mobile responsiveness

### Testing

#### Manual Testing Checklist
- [ ] Complete persona building flow
- [ ] All calculation types work correctly
- [ ] Error handling functions properly
- [ ] UI elements render correctly
- [ ] Session state persists appropriately

#### Automated Testing
```bash
# Run unit tests (if available)
pytest tests/

# Run integration tests
pytest tests/test_integration.py
```

### Feature Requests

When submitting feature requests, please include:
- Clear description of the feature
- Use case and benefits
- Technical implementation suggestions
- Potential impact on existing functionality

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support, please:
1. Check this documentation
2. Review the troubleshooting section
3. Search existing issues on GitHub
4. Create a new issue with detailed information

---

*Last updated: January 2025*
*Version: 1.0.0*