# Kairos AI Trading Backend

## Overview

The Kairos AI Trading Backend is a powerful FastAPI-based autonomous cryptocurrency trading system powered by Gemini AI. It provides both autonomous trading capabilities and interactive assistant features with real-time portfolio management across multiple blockchain networks.

## Features

### Autonomous Trading Agent
- **Gemini AI Integration**: Advanced decision-making using Google's Gemini 1.5 Pro
- **Multi-Chain Support**: Ethereum, Polygon, Solana, Base networks
- **Real-Time Portfolio Management**: Live balance tracking and optimization
- **Risk Management**: Intelligent position sizing and portfolio protection
- **Strategy Learning**: AI learns from trade outcomes and market conditions

### Interactive AI Assistant
- **Market Analysis**: Real-time crypto price data and trend analysis
- **Portfolio Insights**: Comprehensive holdings analysis and recommendations
- **News Integration**: Latest cryptocurrency news and sentiment analysis
- **Educational Content**: Crypto concepts and trading strategy explanations

### Advanced Analytics
- **Real-Time Metrics**: Live P&L, success rates, and performance tracking
- **PDF Report Generation**: Professional trading session reports
- **Strategy Analytics**: AI decision pattern analysis and optimization
- **Risk Assessment**: Comprehensive risk scoring and management

### API Integration
- **Recall Trading API**: Real trade execution capabilities
- **CoinGecko Integration**: Live price feeds and market data
- **Supabase Database**: Persistent data storage and analytics
- **Multi-Chain Portfolio**: Cross-blockchain asset management

## Architecture

```
backend/
├── api/                    # Core API modules
│   ├── portfolio.py       # Portfolio management
│   ├── execute.py         # Trade execution engine
│   ├── token_price.py     # Price data fetching
│   └── trades_history.py  # Historical trade data
├── agent/                 # AI agents and intelligence
│   ├── gemini_agent.py    # Gemini AI integration
│   ├── kairos_autonomous_agent.py  # Main trading agent
│   └── coinpanic_api.py   # News and sentiment
├── database/              # Data persistence
│   └── supabase_client.py # Database operations
├── reports/               # Report generation
│   └── autonomous_report_generator.py  # PDF reports
├── api_server.py          # Main FastAPI application
└── requirements.txt       # Python dependencies
```

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Virtual Environment** (recommended)
- **API Keys** (Gemini, Supabase, Recall)

### Installation

1. **Clone and Setup Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
Create a `.env` file in the backend directory:
```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Trading API Configuration
RECALL_API_KEY=your_recall_api_key_here
RECALL_SANDBOX_API_BASE=https://api.competitions.recall.network

# Optional: News API
COINPANIC_API_KEY=your_coinpanic_api_key
```

3. **Start the Server**
```bash
python api_server.py
```

The server will start on `http://localhost:8000`

### API Documentation

Once running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check and server status |
| GET | `/health` | Detailed health information |
| GET | `/api/portfolio` | Get current portfolio data |
| GET | `/api/balance/{token}` | Get specific token balance |
| GET | `/api/price/{token}` | Get live token price |

### Trading Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/trade` | Execute manual trade |
| GET | `/api/trades/history` | Get trading history |
| POST | `/api/chat` | Start autonomous trading session |
| GET | `/api/autonomous/status/{session_id}` | Get session status |
| POST | `/api/autonomous/stop/{session_id}` | Stop trading session |

### Assistant Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/assistant` | Interactive AI assistant |
| GET | `/api/session/report/{session_id}` | Download PDF report |

## Configuration

### Supported Tokens

The system supports trading with the following tokens:
- **Stablecoins**: USDC, USDT, DAI, USDbC
- **Major Cryptos**: ETH, WETH, BTC, WBTC
- **DeFi Tokens**: UNI, LINK, AAVE
- **Layer 1s**: SOL, MATIC

### Supported Chains

- **Ethereum**: Primary network for most tokens
- **Polygon**: MATIC and bridged tokens
- **Solana**: SOL ecosystem tokens
- **Base**: USDbC and Base ecosystem

### Risk Management

- **Position Sizing**: Maximum 50% of token balance per trade
- **Portfolio Limits**: Diversification across multiple assets
- **Chain Validation**: Trades only within compatible networks
- **Balance Verification**: Real-time balance checking before execution

## Development

### Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── portfolio.py          # Portfolio management and balance fetching
│   ├── execute.py            # Trade execution via Recall API
│   ├── token_price.py        # Live price data from CoinGecko
│   └── trades_history.py     # Historical trade data retrieval
├── agent/
│   ├── __init__.py
│   ├── gemini_agent.py       # Gemini AI integration and prompts
│   ├── kairos_autonomous_agent.py  # Main autonomous trading logic
│   └── coinpanic_api.py      # News and sentiment analysis
├── database/
│   ├── __init__.py
│   └── supabase_client.py    # Database operations and ORM
├── reports/
│   ├── __init__.py
│   └── autonomous_report_generator.py  # PDF report generation
├── api_server.py             # FastAPI application and routes
├── requirements.txt          # Python dependencies
└── .env.example             # Environment variables template
```

### Key Components

#### API Server (`api_server.py`)
- **FastAPI Application**: Main web server and API routes
- **CORS Configuration**: Cross-origin request handling
- **Background Tasks**: Async autonomous trading execution
- **Error Handling**: Comprehensive error management and logging

#### Gemini Agent (`agent/gemini_agent.py`)
- **AI Decision Engine**: Core trading decision logic
- **Assistant Mode**: Interactive chat capabilities
- **Market Analysis**: Real-time data processing and analysis
- **Strategy Generation**: Dynamic trading strategy creation

#### Autonomous Agent (`agent/kairos_autonomous_agent.py`)
- **Trading Loop**: Main autonomous trading execution
- **Portfolio Management**: Real-time portfolio tracking and optimization
- **Risk Assessment**: Trade validation and risk management
- **Learning System**: Strategy performance tracking and improvement

#### Database Client (`database/supabase_client.py`)
- **Session Management**: Trading session lifecycle
- **Trade Logging**: Comprehensive trade record keeping
- **Strategy Storage**: AI strategy persistence and retrieval
- **Analytics**: Performance metrics and reporting data

### Testing

```bash
# Run basic health check
curl http://localhost:8000/health

# Test portfolio endpoint
curl http://localhost:8000/api/portfolio

# Test price endpoint
curl http://localhost:8000/api/price/BTC

# Start interactive session (requires frontend or API client)
curl -X POST http://localhost:8000/api/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current Bitcoin price?"}'
```

### Debugging

Enable debug logging by setting environment variables:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export DEBUG=true
python api_server.py
```

## Deployment

### Production Setup

1. **Environment Variables**
```bash
# Production environment
export ENVIRONMENT=production
export DEBUG=false
export API_HOST=0.0.0.0
export API_PORT=8000
```

2. **Process Management**
```bash
# Using gunicorn for production
pip install gunicorn
gunicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

3. **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "api_server.py"]
```

### Security Considerations

- **API Keys**: Store securely in environment variables
- **Database Access**: Use read-only keys where possible
- **Rate Limiting**: Implement API rate limiting for production
- **Input Validation**: All inputs are validated before processing
- **Error Handling**: Sensitive information is not exposed in errors

## Troubleshooting

### Common Issues

1. **Server Won't Start**
   - Check that all required environment variables are set
   - Verify Python version (3.8+ required)
   - Ensure all dependencies are installed

2. **Database Connection Issues**
   - Verify Supabase credentials in `.env`
   - Check network connectivity
   - System automatically falls back to mock mode

3. **Trading API Errors**
   - Verify Recall API key and endpoint
   - Check token symbols are supported
   - Ensure sufficient portfolio balance

4. **Gemini AI Issues**
   - Verify GEMINI_API_KEY is valid
   - Check API quota and limits
   - Review request format and parameters

### Logs and Monitoring

The application provides comprehensive logging:
- **Info Level**: Normal operations and status updates
- **Warning Level**: Non-critical issues and fallbacks
- **Error Level**: Critical errors and exceptions
- **Debug Level**: Detailed execution information

## Contributing

1. **Code Style**: Follow PEP 8 Python style guidelines
2. **Documentation**: Update docstrings and README for new features
3. **Testing**: Add tests for new functionality
4. **Error Handling**: Implement comprehensive error management
5. **Logging**: Add appropriate logging for debugging and monitoring

## License

This project is proprietary software. All rights reserved.

## Support

For technical support or questions:
- Review the API documentation at `/docs`
- Check the troubleshooting section above
- Verify environment configuration
- Review application logs for error details