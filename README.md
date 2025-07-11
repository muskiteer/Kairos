# 🚀 Kairos - Powerful Cryptocurrency Trading Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-13+-black.svg)](https://nextjs.org/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-green.svg)](https://ai.google.dev/)

> **A sophisticated AI-powered cryptocurrency trading platform with real-time portfolio management, intelligent trade execution, and comprehensive market analysis.**

## ✨ Features

### 🤖 **AI-Powered Trading Assistant**
- **Gemini AI Integration** - Advanced natural language processing for trading commands
- **Intelligent Trade Analysis** - AI-driven market insights and trading recommendations
- **Natural Language Trading** - Execute trades using conversational commands
- **Real-time Reasoning** - See the AI's thought process for every action

### 🔗 **Complete API Integration**
- **Recall API** - Real portfolio management and trade execution
- **CoinPanic News API** - Live cryptocurrency news and market sentiment
- **Real-time Price Data** - Up-to-the-minute token prices and market data
- **Trading History** - Complete transaction records and analytics

### 🎨 **Modern Web Interface**
- **Professional UI** - Built with Next.js 13+ and shadcn/ui components
- **Real-time Chat** - Interactive AI assistant with expandable response details
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- **Dark/Light Mode** - Customizable theme preferences

### 💰 **Trading Capabilities**
- **Real Trade Execution** - Actual cryptocurrency trades via Recall API
- **Portfolio Management** - View balances, track performance, analyze holdings
- **Multi-Token Support** - USDC, WETH, WBTC, DAI, USDT, UNI, LINK, ETH
- **Risk Management** - Built-in safety checks and balance verification

## 🏗️ Architecture

```
├── frontend/                 # Next.js React Application
│   ├── src/
│   │   ├── app/             # App Router (Next.js 13+)
│   │   ├── components/      # Reusable UI Components
│   │   └── lib/             # Utilities and Helpers
│   └── package.json
├── backend/                 # Python API Server
│   ├── api_server.py        # Flask API Server
│   ├── gemini_agent.py      # AI Trading Agent
│   ├── portfolio.py         # Portfolio Management
│   ├── token_price.py       # Price Data Integration
│   ├── execute.py           # Trade Execution
│   ├── coinpanic_api.py     # News Integration
│   └── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm/yarn
- **API Keys** (see [Configuration](#-configuration))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Kairos.git
cd Kairos
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install flask flask-cors

# Set up environment variables (see Configuration section)
cp .env.example .env
# Edit .env with your API keys

# Start the API server
python3 api_server.py
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **AI Trading Interface**: http://localhost:3000/ai-agent
- **API Server**: http://localhost:5000

## ⚙️ Configuration

Create a `.env` file in the `backend/` directory:

```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Trading API Configuration
RECALL_API_KEY=your_recall_api_key_here
RECALL_SANDBOX_API_BASE=https://api.sandbox.competitions.recall.network

# News API Configuration
COINPANIC_API_KEY=your_coinpanic_api_key_here

# Optional: Additional Configuration
DEBUG=True
```

### 🔑 Getting API Keys

1. **Gemini AI**: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Recall API**: [Recall Platform](https://recall.network/)
3. **CoinPanic API**: [CoinPanic](https://cryptopanic.com/developers/)

## 💬 Usage Examples

### Trading Commands
```
"Buy 500 USDC worth of WETH"
"Trade 100 USDC to WBTC"
"Swap 50 USDC for DAI"
"Convert 25 WETH to USDC"
```

### Portfolio Management
```
"Show my portfolio"
"How much USDC do I have?"
"What's my WETH balance?"
"Check all my token balances"
```

### Market Analysis
```
"What's the price of WETH?"
"Show me ETH price trends"
"Get current market prices"
"Price analysis for WBTC"
```

### News & Sentiment
```
"Show me trending crypto news"
"Get bullish market news"
"Show bearish sentiment"
"Bitcoin news updates"
```

### Trading History
```
"Show my trading history"
"Recent transaction records"
"My trade performance"
```

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run in development mode
python3 api_server.py

# Run tests
python3 -m pytest tests/

# Format code
black .
```

### Frontend Development

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

### API Endpoints

- `POST /api/chat` - Send message to AI agent
- `GET /api/portfolio` - Get portfolio data
- `GET /api/price/<symbol>` - Get token price
- `GET /api/news` - Get cryptocurrency news
- `GET /api/health` - Health check

## 📊 Supported Tokens

| Symbol | Name | Network |
|--------|------|---------|
| USDC | USD Coin | Ethereum |
| WETH | Wrapped Ethereum | Ethereum |
| WBTC | Wrapped Bitcoin | Ethereum |
| DAI | Dai Stablecoin | Ethereum |
| USDT | Tether | Ethereum |
| UNI | Uniswap | Ethereum |
| LINK | Chainlink | Ethereum |
| ETH | Ethereum | Ethereum |

## 🔒 Security Features

- **API Key Management** - Secure environment variable storage
- **Input Validation** - Comprehensive request validation
- **Error Handling** - Graceful error management and user feedback
- **Rate Limiting** - Built-in protection against API abuse
- **Balance Verification** - Pre-trade balance checks

## 🎯 Advanced Features

### AI Capabilities
- **Intent Recognition** - Understands complex trading instructions
- **Context Awareness** - Maintains conversation context
- **Risk Assessment** - Evaluates trade risks and market conditions
- **Educational Mode** - Explains trading concepts and strategies

### Technical Features
- **Real-time Updates** - Live price feeds and portfolio updates
- **Expandable Responses** - Detailed reasoning and API response viewing
- **Connection Monitoring** - Backend health checks and retry mechanisms
- **Responsive Design** - Optimized for all device sizes

## 🧪 Testing

```bash
# Backend tests
cd backend
python3 -m pytest

# Frontend tests
cd frontend
npm test

# Integration tests
npm run test:integration
```

## 📈 Performance

- **Fast Response Times** - Optimized API calls and caching
- **Efficient UI** - React optimization and lazy loading
- **Scalable Architecture** - Modular design for easy expansion
- **Memory Management** - Efficient resource utilization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced language processing
- **Recall Network** for cryptocurrency trading infrastructure
- **CoinPanic** for real-time news and market sentiment
- **shadcn/ui** for beautiful UI components
- **Next.js** for the modern React framework

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/Kairos/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Kairos/issues)
- **Discord**: [Community Server](https://discord.gg/Kairos)

---

<div align="center">

**Made with ❤️ by the Kairos Team**

[Website](https://Kairos.com) • [Documentation](https://docs.Kairos.com) • [Discord](https://discord.gg/Kairos)

</div>