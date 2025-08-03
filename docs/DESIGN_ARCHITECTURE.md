# Valura Financial Planning Agent - Architecture Design Document

## Overview

The Valura Financial Planning Agent combines **LangChain**, **LangGraph**, and **Google Gemini 2.5 Flash** to create an intelligent conversational system for retirement planning with real-time market data integration.

## Core Architecture Decisions

### 1. LangChain + LangGraph + Gemini 2.5 Flash Integration

**Decision**: Used Google's Gemini 2.5 Flash via LangChain's `ChatGoogleGenerativeAI` wrapper with LangGraph for sophisticated state management.

**Rationale**: 
• LangChain provides standardized LLM interfaces with built-in conversation memory
• LangGraph enables complex conversation flows with persistent state management across phases
• Gemini 2.5 Flash offers excellent performance-to-cost ratio for conversational AI
• Easy model switching and enhanced memory capabilities

**Trade-offs**: Additional dependency layers vs. direct API calls, but gained standardization and sophisticated memory management.

### 2. Hybrid Memory Management Strategy

**Decision**: Combined Streamlit session state for UI persistence with LangGraph's state management for conversation flow.

**Implementation**: Three-phase state machine (`persona_building` → `profile_complete` → `interactive`) managed by LangGraph, with UI state handled by Streamlit.

**Benefits**: 
• Persistent conversation context across user interactions
• Structured data collection with smooth phase transitions
• LangGraph's graph-based memory for complex conversation flows
• Direct UI integration without additional database requirements

### 3. Multi-API Integration with Graceful Fallbacks

**APIs Integrated**:
• **Tavily API**: Real-time search for savings rates and financial news
• **Yahoo Finance (yfinance)**: Live Indian market indices (NIFTY, SENSEX, NIFTY BANK, NIFTY IT)
• **Google Gemini**: Conversational AI and intelligent question classification

**Architecture**: Modular `MarketDataTool` class with specific responsibilities, implementing graceful degradation when APIs are unavailable.

### 4. Pure Function Financial Engine

**Decision**: Implemented financial formulas as pure Python functions for mathematical accuracy.

**Formulas Implemented**:
• Future Value: `FV = PV × (1 + r)^n`
• Present Value: `PV = FV / (1 + r)^n`
• Future Value of Annuity: `FV = PMT × [(1 + r)^n – 1] / r`
• Present Value of Annuity: `PV = PMT × [1 – (1 + r)^(-n)] / r`

**Benefits**: Easy unit testing, predictable outputs, reusable across contexts, mathematical accuracy verification.

## LangGraph Memory Management

**State Structure**: 
```python
class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_profile: Dict[str, Any]
    calculations: Dict[str, Any]
    current_step: str
    conversation_history: List[Dict[str, str]]
```

**Conversation Flow**: LangGraph manages transitions between persona building, calculation execution, and interactive Q&A phases, maintaining context and enabling complex conversation patterns.

## Key Trade-offs

• **Streamlit vs. React**: Chose Streamlit for rapid Python-native development over React's customization capabilities
• **Session State vs. Database**: Prioritized simplicity for MVP over persistent cross-session storage
• **API Dependencies vs. Static Data**: Enhanced user experience with real-time market data despite increased complexity
• **LangGraph Complexity vs. Simple State**: Chose sophisticated memory management for better conversation flow

## Scalability Considerations

**Current Limitations**: Single-user sessions, no persistent storage, limited concurrent users

**Future Architecture**: Database integration, multi-tenant architecture, microservices separation, enhanced LangGraph workflows, WebSocket real-time updates

## Security & Privacy

• Environment variable API key management
• No persistent storage of financial data
• Session-based memory only
• Graceful API failure handling

## Conclusion

The architecture balances rapid development with sophisticated AI capabilities through LangChain/LangGraph integration. The modular design enables easy enhancement while LangGraph provides the memory management foundation for complex conversational flows. Trade-offs favor functionality and user experience appropriate for an MVP financial planning agent.