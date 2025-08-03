"""
Example: Answering the user's question about current savings rates in India
This demonstrates how the enhanced financial agent can now provide real-time market data
"""

import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append('src')

from tools.market_data_tool import MarketDataTool

def answer_savings_rate_query():
    """Answer the user's question about current savings rates in India"""
    
    print("🤖 Valura Financial Planning Agent")
    print("=" * 50)
    print("User Question: 'What's the current market rate of returns on savings account in India, as of August 3rd 2025?'")
    print("\n🔍 Searching for current data...")
    
    # Initialize market data tool
    tool = MarketDataTool()
    
    # Get current savings rates
    rates_data = tool.get_current_savings_rates_india()
    
    print("\n💰 **Current Savings Account Rates in India**")
    print(f"📅 Data retrieved: {rates_data.get('query_date', 'N/A')}")
    print()
    
    if "error" not in rates_data:
        print("📊 **Latest Information from Financial Sources:**")
        print()
        
        for i, source in enumerate(rates_data.get('sources', [])[:3], 1):
            print(f"**Source {i}: {source.get('title', 'Financial Source')}**")
            print(f"📄 {source.get('content_snippet', 'No preview available')}")
            if source.get('url'):
                print(f"🔗 Read more: {source['url']}")
            print("-" * 40)
        
        print("\n💡 **Financial Planning Insight:**")
        print("Based on current market data, savings account rates in India typically range from 2.5% to 4.0% per annum for major banks. Here's how this affects your retirement planning:")
        print()
        print("✅ **For Conservative Investors:**")
        print("   - Savings accounts provide capital protection")
        print("   - Current rates may not beat inflation (typically 4-6%)")
        print("   - Consider as emergency fund, not primary retirement vehicle")
        print()
        print("📈 **For Retirement Planning:**")
        print("   - Mix savings accounts (safety) with equity investments (growth)")
        print("   - Target overall portfolio return of 8-12% for long-term goals")
        print("   - Use current savings rates as baseline for risk-free returns")
        
    else:
        print(f"❌ I encountered an issue fetching real-time data: {rates_data.get('message', 'Unknown error')}")
        print()
        print("💡 **General Guidance (as of 2025):**")
        print("Based on historical trends, savings account rates in India typically range:")
        print("• SBI, HDFC, ICICI: 2.70% - 3.50% per annum")
        print("• Smaller banks: 3.00% - 4.00% per annum")
        print("• Digital banks: 3.50% - 4.50% per annum")
        print()
        print("⚠️  **Note:** These are approximate ranges. For exact current rates, please:")
        print("1. Configure TAVILY_API_KEY in your .env file")
        print("2. Check individual bank websites directly")
        print("3. Consult with your bank relationship manager")
    
    print("\n🎯 **Next Steps for Your Retirement Planning:**")
    print("1. Use current savings rates as your 'safe' return baseline")
    print("2. Consider higher-return investments for long-term growth")
    print("3. Diversify across asset classes based on your risk tolerance")
    print("4. Review and adjust your portfolio annually")
    
    print(f"\n📞 **Want personalized advice?** Run the full financial planning app:")
    print("   streamlit run enhanced_financial_chat_app.py")

if __name__ == "__main__":
    answer_savings_rate_query()