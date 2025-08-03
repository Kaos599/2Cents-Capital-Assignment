# Valura Financial Planning Agent - Architecture Design Document

## Overview

The Valura Financial Planning Agent is built as a conversational AI system that combines persona building, financial calculations, and real-time market data integration. This document outlines key architectural decisions and trade-offs made during development.

## Core Architecture Decisions

### 1. LangChain + Gemini 2.5 Flash Integration

**Decision**: Used Google's Gemini 2.5 Flash via LangChain's `ChatGoogleGenerativeAI` wrapper rather than direct API calls.

**Rationale**: 
- LangChain provides standardized interfaces for LLM interactions
- Gemini 2.5 Flash offers excellent performance-to-cost ratio for conversational AI
- Built-in conversation memory and context management
- Easy model switching if needed

**Trade-offs**: 
- Additional dependency layer vs direct API calls
- LangChain abstraction may limit access to model-specific features
- Slightly higher latency than direct integration

### 2. Streamlit Session State for Memory Management

**Decision**: Implemented conversation memory using Streamlit's session state rather than LangGraph's more sophisticated memory systems.

**Rationale**:
- Streamlit session state provides persistent storage across user interactions
- Simpler implementation for MVP requirements
- Direct integration with UI components
- No additional database or storage requirements

**Trade-offs**:
- Memory doesn't persist across browser sessions
- Limited to single-user sessions
- Less sophisticated than LangGraph's graph-based memory
- Potential memory leaks with long conversations

### 3. Modular Tool Architecture

**Decision**: Created separate tool classes (`MarketDataTool`) with specific responsibilities rather than monolithic functions.

**Implementation**:
```python
class MarketDataTool:
    def get_current_savings_rates_india()
    def get_indian_market_indices()
    def search_financial_news()
```

**Rationale**:
- Clear separation of concerns
- Easy testing and mocking
- Extensible for additional data sources
- Follows single responsibility principle

### 4. Multi-API Integration Strategy

**Decision**: Integrated multiple external APIs (Tavily for search, Yahoo Finance for market data) with graceful fallbacks.

**APIs Used**:
- **Tavily API**: Real-time search for savings rates and financial news
- **Yahoo Finance (yfinance)**: Live market data for Indian indices
- **Google Gemini**: Conversational AI and question classification

**Trade-offs**:
- Increased complexity and potential failure points
- API rate limits and costs
- Network dependency for core features
- Enhanced user experience with real-time data

## Persona Building Architecture

### Conversation Phase Management

**Decision**: Implemented a state machine approach with three phases:
1. `persona_building` - Guided question flow
2. `profile_complete` - Initial calculation presentation  
3. `interactive` - Open-ended Q&A

**Implementation**:
```python
if 'conversation_phase' not in st.session_state:
    st.session_state.conversation_phase = "persona_building"
```

**Benefits**:
- Clear user journey progression
- Contextual AI responses based on phase
- Structured data collection
- Smooth transition between modes

### Question Classification System

**Decision**: Used Gemini AI to classify user questions into categories (PERSONA, CALCULATION, SCENARIO, EXPLANATION, ADVICE).

**Rationale**:
- Dynamic response routing based on intent
- Natural language understanding
- Flexible handling of user inputs
- Reduces rigid conversation flows

## Financial Calculation Engine

### Pure Function Design

**Decision**: Implemented financial formulas as pure Python functions in separate modules.

**Example**:
```python
def calculate_retirement_timeline(current_age, retirement_age, monthly_savings, expected_return, current_savings=0):
    # Pure function with no side effects
    return calculation_results
```

**Benefits**:
- Easy unit testing
- Predictable outputs
- Reusable across different contexts
- Mathematical accuracy verification

### Real-time Market Data Integration

**Decision**: Integrated live market data into financial advice rather than using static assumptions.

**Implementation**:
- Current Indian savings account rates via Tavily search
- Live market indices (NIFTY, SENSEX) via Yahoo Finance
- Real-time context for investment recommendations

**Trade-offs**:
- API dependencies and potential failures
- Increased complexity
- More accurate and relevant advice
- Better user engagement

## UI/UX Architecture Decisions

### Streamlit Framework Choice

**Decision**: Used Streamlit over React or plain HTML for the frontend.

**Rationale**:
- Rapid prototyping and development
- Python-native (no context switching)
- Built-in state management
- Easy deployment and sharing

**Trade-offs**:
- Limited customization compared to React
- Python-only development team requirement
- Less control over UI behavior
- Excellent for MVP and data applications

### Sidebar Information Display

**Decision**: Used Streamlit sidebar for profile display and market data rather than inline cards.

**Benefits**:
- Persistent information visibility
- Clean main chat interface
- Easy access to user profile
- Real-time market data always visible

## Error Handling and Resilience

### Graceful API Degradation

**Decision**: Implemented fallback mechanisms when external APIs fail.

**Implementation**:
```python
if not self.tavily_client:
    return {
        "error": "Tavily API not available",
        "message": "Please configure TAVILY_API_KEY to get real-time data"
    }
```

**Benefits**:
- Application continues functioning with reduced features
- Clear user communication about limitations
- Prevents complete system failures

## Scalability Considerations

### Current Limitations
- Single-user sessions only
- Memory doesn't persist across browser sessions
- No user authentication or data persistence
- Limited to Streamlit's concurrent user capacity

### Future Architecture Path
- Database integration for user profiles
- Multi-tenant architecture
- Microservices for different components
- Enhanced memory systems with LangGraph
- WebSocket connections for real-time updates

## Security and Privacy

### API Key Management
- Environment variable configuration
- No hardcoded credentials
- Graceful handling of missing keys

### Data Privacy
- No persistent storage of user financial data
- Session-based memory only
- No external data transmission beyond API calls

## Conclusion

The architecture prioritizes rapid development and user experience while maintaining code quality and extensibility. The modular design allows for easy enhancement and scaling as requirements evolve. Key trade-offs favor simplicity and functionality over complex enterprise patterns, appropriate for an MVP financial planning agent.