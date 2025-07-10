#!/usr/bin/env python3
"""
Main entry point for Gemini Trading Agent
"""

from agent.gemini_agent import GeminiTradingAgent

def main():
    """Start the Gemini Trading Agent"""
    print("🚀 Starting Gemini Trading Agent...")
    
    try:
        agent = GeminiTradingAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Please check your API keys in .env file")

if __name__ == "__main__":
    main()

    
