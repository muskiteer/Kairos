# Gemini Trading Agent

An AI-powered crypto trading assistant that uses Google's Gemini AI to provide intelligent trading capabilities through the Recall API.

## Features

🤖 **AI-Powered Trading Assistant**
- Natural language interaction with Gemini AI
- Intelligent function calling for trading operations
- Detailed explanations and trading advice

📊 **Trading Capabilities**
- View portfolio and token balances
- Get real-time token prices
- Execute trades between supported tokens
- View trading history
- Get trading advice and market insights

💰 **Supported Tokens**
- USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH

## Quick Start

### 1. Setup Environment

```bash
# Run setup script
python setup.py

# Or manually install requirements
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file and add your API keys:

```env
# Recall API Configuration
RECALL_API_KEY=your_recall_api_key_here
RECALL_SANDBOX_API_BASE=https://api.sandbox.competitions.recall.network

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run the Agent

```bash
# Start the AI agent
python main.py

# Or run directly
python cli.py

# Or try the demo
python demo.py
```

## Usage Examples

Once running, you can chat with the AI agent:

```
You: What's my portfolio?
🤖 AI Agent: I'll check your portfolio for you!

You: What's the current price of WETH?
🤖 AI Agent: Let me get the current WETH price...

You: Buy 100 USDC worth of WETH
🤖 AI Agent: I'll help you execute that trade. First, let me check your balance and current prices...

You: Show me my trading history
🤖 AI Agent: Here's your complete trading history...
```

## File Structure

```
backend/
├── main.py              # Main entry point
├── cli.py               # CLI interface
├── setup.py             # Setup script
├── demo.py              # Demo script
├── gemini_agent.py      # Advanced Gemini AI agent
├── ai_agent.py          # Simple AI agent
├── utils.py             # Utility functions
├── execute.py           # Trade execution
├── portfolio.py         # Portfolio management
├── token_balance.py     # Token balance queries
├── token_price.py       # Token price queries
├── trades_history.py    # Trading history
└── requirements.txt     # Python dependencies
```

## API Functions

The AI agent has access to these functions:

- `get_portfolio()` - Get complete portfolio
- `get_token_balance(token)` - Get specific token balance
- `get_token_price(symbol)` - Get token price
- `get_trades_history()` - Get trading history
- `execute_trade(from_token, to_token, amount)` - Execute trades
- `get_supported_tokens()` - Get supported tokens list

## Requirements

- Python 3.7+
- Recall API key (from Recall platform)
- Gemini API key (from Google AI Studio)
- Internet connection

## Future Enhancements

- 📰 CoinPanic API integration for crypto news
- 📈 Advanced trading strategies
- 💹 Portfolio optimization suggestions
- 🔔 Price alerts and notifications
- 📊 Technical analysis integration

## Safety Features

- Balance checking before trades
- Confirmation requests for large trades
- Error handling and validation
- Trading advice and risk warnings

## Support

If you encounter issues:
1. Check your API keys in `.env`
2. Ensure internet connectivity
3. Verify supported token symbols
4. Check API rate limits

---

*Happy trading with AI assistance! 🚀*