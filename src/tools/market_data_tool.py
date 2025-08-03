"""
Market Data Tool - Real-time financial data using Tavily and yfinance APIs
"""
import os
import yfinance as yf
from tavily import TavilyClient
from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketDataTool:
    """Tool for fetching real-time market data and financial information"""
    
    def __init__(self):
        """Initialize the market data tool with API clients"""
        self.tavily_client = None
        self.yf_client = yf
        
        # Initialize Tavily client if API key is available
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            try:
                self.tavily_client = TavilyClient(api_key=tavily_api_key)
                logger.info("Tavily client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily client: {e}")
        else:
            logger.warning("TAVILY_API_KEY not found in environment variables")
    
    def get_current_savings_rates_india(self) -> Dict[str, Any]:
        """Get current savings account interest rates in India"""
        try:
            if not self.tavily_client:
                return {
                    "error": "Tavily API not available",
                    "message": "Please configure TAVILY_API_KEY to get real-time data"
                }
            
            # Search for current savings account rates in India
            query = "current savings account interest rates India 2025 major banks SBI HDFC ICICI"
            
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_raw_content=True
            )
            
            # Extract relevant information
            rates_info = {
                "query_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "search_query": query,
                "sources": [],
                "summary": "Current savings account interest rates in India"
            }
            
            for result in response.get("results", []):
                source_info = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content_snippet": result.get("content", "")[:300] + "..." if result.get("content") else "",
                    "published_date": result.get("published_date", "")
                }
                rates_info["sources"].append(source_info)
            
            return rates_info
            
        except Exception as e:
            logger.error(f"Error fetching savings rates: {e}")
            return {
                "error": str(e),
                "message": "Failed to fetch current savings rates"
            }
    
    def get_market_data(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """Get market data for a specific symbol using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            
            # Get historical data
            hist = ticker.history(period=period)
            
            # Get current price and key metrics
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
            
            market_data = {
                "symbol": symbol,
                "current_price": float(current_price) if current_price else None,
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "company_name": info.get("longName", info.get("shortName")),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add historical performance
            if not hist.empty:
                market_data["historical_data"] = {
                    "period": period,
                    "start_date": hist.index[0].strftime("%Y-%m-%d"),
                    "end_date": hist.index[-1].strftime("%Y-%m-%d"),
                    "price_change": float(hist['Close'].iloc[-1] - hist['Close'].iloc[0]),
                    "price_change_percent": float(((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100),
                    "average_volume": float(hist['Volume'].mean())
                }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return {
                "error": str(e),
                "symbol": symbol,
                "message": f"Failed to fetch market data for {symbol}"
            }
    
    def get_indian_market_indices(self) -> Dict[str, Any]:
        """Get current data for major Indian market indices"""
        indian_indices = {
            "^NSEI": "NIFTY 50",
            "^BSESN": "BSE SENSEX",
            "^NSEBANK": "NIFTY BANK",
            "^NSEIT": "NIFTY IT"
        }
        
        indices_data = {}
        
        for symbol, name in indian_indices.items():
            try:
                data = self.get_market_data(symbol, period="5d")
                indices_data[name] = data
            except Exception as e:
                logger.error(f"Error fetching data for {name}: {e}")
                indices_data[name] = {"error": str(e)}
        
        return {
            "indices": indices_data,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market": "India"
        }
    
    def search_financial_news(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search for financial news using Tavily"""
        try:
            if not self.tavily_client:
                return {
                    "error": "Tavily API not available",
                    "message": "Please configure TAVILY_API_KEY to get real-time news"
                }
            
            response = self.tavily_client.search(
                query=f"{query} financial news",
                search_depth="basic",
                max_results=max_results,
                include_raw_content=False
            )
            
            news_data = {
                "query": query,
                "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "articles": []
            }
            
            for result in response.get("results", []):
                article = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "published_date": result.get("published_date", ""),
                    "score": result.get("score", 0)
                }
                news_data["articles"].append(article)
            
            return news_data
            
        except Exception as e:
            logger.error(f"Error searching financial news: {e}")
            return {
                "error": str(e),
                "message": "Failed to fetch financial news"
            }
    
    def get_investment_insights(self, topic: str) -> Dict[str, Any]:
        """Get investment insights and analysis using Tavily"""
        try:
            if not self.tavily_client:
                return {
                    "error": "Tavily API not available",
                    "message": "Please configure TAVILY_API_KEY to get investment insights"
                }
            
            # Use QnA search for more focused answers
            answer = self.tavily_client.qna_search(
                query=f"What are the current investment insights and recommendations for {topic} in 2025?"
            )
            
            # Also get broader context
            context = self.tavily_client.get_search_context(
                query=f"{topic} investment analysis market trends 2025"
            )
            
            return {
                "topic": topic,
                "direct_answer": answer,
                "detailed_context": context,
                "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error getting investment insights: {e}")
            return {
                "error": str(e),
                "message": f"Failed to get investment insights for {topic}"
            }

# Utility functions for easy integration
def get_current_market_rates():
    """Quick function to get current market rates"""
    tool = MarketDataTool()
    return tool.get_current_savings_rates_india()

def get_indian_markets():
    """Quick function to get Indian market data"""
    tool = MarketDataTool()
    return tool.get_indian_market_indices()

def search_market_news(query: str):
    """Quick function to search market news"""
    tool = MarketDataTool()
    return tool.search_financial_news(query)
    
#Example usage and testing functions
if __name__ == "__main__":
    # Test the market data tool
    tool = MarketDataTool()
    
    print("Testing Market Data Tool...")
    print("=" * 50)
    
    # Test 1: Get current savings rates in India
    print("\n1. Current Savings Rates in India:")
    rates = tool.get_current_savings_rates_india()
    print(f"Query Date: {rates.get('query_date', 'N/A')}")
    print(f"Sources Found: {len(rates.get('sources', []))}")
    
    # Test 2: Get market data for a popular Indian stock
    print("\n2. Market Data for Reliance Industries (RELIANCE.NS):")
    reliance_data = tool.get_market_data("RELIANCE.NS")
    if "error" not in reliance_data:
        print(f"Company: {reliance_data.get('company_name', 'N/A')}")
        print(f"Current Price: ₹{reliance_data.get('current_price', 'N/A')}")
        print(f"Market Cap: {reliance_data.get('market_cap', 'N/A')}")
    else:
        print(f"Error: {reliance_data.get('error', 'Unknown error')}")
    
    # Test 3: Get Indian market indices
    print("\n3. Indian Market Indices:")
    indices = tool.get_indian_market_indices()
    for index_name, data in indices.get('indices', {}).items():
        if "error" not in data:
            print(f"{index_name}: {data.get('current_price', 'N/A')}")
        else:
            print(f"{index_name}: Error - {data.get('error', 'Unknown')}")
    
    # Test 4: Search financial news
    print("\n4. Financial News Search:")
    news = tool.search_financial_news("India interest rates RBI policy")
    print(f"Articles Found: {len(news.get('articles', []))}")
    if news.get('articles'):
        print(f"Latest: {news['articles'][0].get('title', 'N/A')}")