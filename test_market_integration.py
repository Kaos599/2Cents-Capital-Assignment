"""
Test script for market data integration
Run this to verify that the Tavily and yfinance APIs are working correctly
"""

import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append('src')

from tools.market_data_tool import MarketDataTool

def test_market_data_integration():
    """Test the market data tool functionality"""
    print("🧪 Testing Market Data Integration")
    print("=" * 50)
    
    # Initialize the tool
    tool = MarketDataTool()
    
    # Test 1: Check API availability
    print("\n1. 📋 API Status Check:")
    print(f"   Tavily API: {'✅ Available' if tool.tavily_client else '❌ Not configured'}")
    print(f"   yfinance: ✅ Available")
    print(f"   GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    print(f"   TAVILY_API_KEY: {'✅ Set' if os.getenv('TAVILY_API_KEY') else '❌ Not set'}")
    
    # Test 2: yfinance functionality (should always work)
    print("\n2. 📈 Testing yfinance (Yahoo Finance):")
    try:
        # Test with a popular Indian stock
        reliance_data = tool.get_market_data("RELIANCE.NS", period="5d")
        
        if "error" not in reliance_data:
            print(f"   ✅ Successfully fetched data for {reliance_data.get('company_name', 'RELIANCE.NS')}")
            print(f"   💰 Current Price: ₹{reliance_data.get('current_price', 'N/A')}")
            print(f"   📊 Market Cap: {reliance_data.get('market_cap', 'N/A')}")
            print(f"   🏢 Sector: {reliance_data.get('sector', 'N/A')}")
        else:
            print(f"   ❌ Error: {reliance_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 3: Indian market indices
    print("\n3. 🇮🇳 Testing Indian Market Indices:")
    try:
        indices = tool.get_indian_market_indices()
        
        for index_name, data in indices.get('indices', {}).items():
            if "error" not in data:
                current_price = data.get('current_price')
                change_percent = data.get('historical_data', {}).get('price_change_percent', 0)
                status = "📈" if change_percent >= 0 else "📉"
                
                print(f"   {status} {index_name}: {current_price:.2f} ({change_percent:+.2f}%)")
            else:
                print(f"   ❌ {index_name}: {data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4: Tavily functionality (only if API key is available)
    print("\n4. 🔍 Testing Tavily Search:")
    if tool.tavily_client:
        try:
            # Test savings rates search
            rates_data = tool.get_current_savings_rates_india()
            
            if "error" not in rates_data:
                print(f"   ✅ Successfully searched for savings rates")
                print(f"   📅 Query Date: {rates_data.get('query_date', 'N/A')}")
                print(f"   📰 Sources Found: {len(rates_data.get('sources', []))}")
                
                # Show first source title
                if rates_data.get('sources'):
                    first_source = rates_data['sources'][0]
                    print(f"   📄 Sample Source: {first_source.get('title', 'N/A')[:60]}...")
            else:
                print(f"   ❌ Error: {rates_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    else:
        print("   ⚠️  Tavily API not configured - skipping test")
        print("   💡 To enable: Set TAVILY_API_KEY in your .env file")
    
    # Test 5: Financial news search
    print("\n5. 📰 Testing Financial News Search:")
    if tool.tavily_client:
        try:
            news_data = tool.search_financial_news("India RBI interest rates", max_results=3)
            
            if "error" not in news_data:
                print(f"   ✅ Successfully searched for financial news")
                print(f"   📰 Articles Found: {len(news_data.get('articles', []))}")
                
                # Show first article title
                if news_data.get('articles'):
                    first_article = news_data['articles'][0]
                    print(f"   📄 Sample Article: {first_article.get('title', 'N/A')[:60]}...")
            else:
                print(f"   ❌ Error: {news_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    else:
        print("   ⚠️  Tavily API not configured - skipping test")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("   • yfinance (Yahoo Finance): Always available for market data")
    print("   • Tavily API: Provides real-time search capabilities")
    print("   • Google Gemini: Required for AI chat responses")
    print("\n💡 Next Steps:")
    print("   1. Ensure all API keys are set in your .env file")
    print("   2. Run: streamlit run enhanced_financial_chat_app.py")
    print("   3. Ask questions like:")
    print("      - 'What are the current savings rates in India?'")
    print("      - 'Show me the current market status'")
    print("      - 'What's the latest financial news?'")

if __name__ == "__main__":
    test_market_data_integration()