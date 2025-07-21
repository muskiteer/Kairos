# Kairos AI Trading System

## Overview

Kairos is a comprehensive autonomous cryptocurrency trading platform powered by advanced AI technology. The system combines Gemini AI's sophisticated decision-making capabilities with real-time market data to provide both autonomous trading and interactive market analysis features.

## System Architecture

```
Kairos AI Trading System
├── Frontend (React/Next.js)     # Web interface and user experience
│   ├── AI Agent Interface       # Autonomous trading and assistant modes
│   ├── Manual Trading          # Direct trading interface
│   └── Portfolio Dashboard     # Real-time portfolio management
├── Backend (Python/FastAPI)    # Core trading engine and AI integration
│   ├── Gemini AI Agent        # Decision-making and market analysis
│   ├── Trading Engine         # Multi-chain trade execution
│   ├── Portfolio Manager      # Real-time balance and asset tracking
│   └── Analytics Engine       # Performance tracking and reporting
└── External Integrations      # Third-party services and APIs
    ├── Recall Trading API     # Real trade execution
    ├── CoinGecko API          # Live price data
    ├── Supabase Database      # Data persistence
    └── TradingView Charts     # Technical analysis
```

## Key Features

### Autonomous Trading
- **AI-Powered Decisions**: Gemini AI analyzes market conditions, news sentiment, and portfolio data
- **Multi-Chain Support**: Trade across Ethereum, Polygon, Solana, and Base networks
- **Risk Management**: Intelligent position sizing and portfolio protection
- **Learning System**: AI improves strategies based on trade outcomes
- **Real-Time Execution**: Automated trade execution with comprehensive validation

### Interactive AI Assistant
- **Market Analysis**: Real-time crypto price data and trend analysis
- **Portfolio Insights**: Comprehensive holdings analysis and recommendations
- **Educational Content**: Crypto concepts and trading strategy explanations
- **News Integration**: Latest cryptocurrency news and sentiment analysis

### Advanced Analytics
- **Performance Tracking**: Real-time P&L, success rates, and trading metrics
- **Strategy Analysis**: AI decision pattern analysis and optimization
- **Professional Reports**: Automated PDF report generation
- **Risk Assessment**: Comprehensive risk scoring and management

### Professional Interface
- **Dual Mode Operation**: Switch between autonomous agent and interactive assistant
- **Real-Time Updates**: Live portfolio and session monitoring
- **Responsive Design**: Mobile-first responsive interface
- **Integration Charts**: TradingView integration for technical analysis

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with Shadcn/UI components
- **State Management**: React hooks with custom state management
- **Charts**: TradingView widget integration
- **Theme**: Dark/light mode with system preference detection

### Backend
- **Framework**: FastAPI with Python 3.8+
- **AI Integration**: Google Gemini 1.5 Pro
- **Database**: Supabase PostgreSQL
- **Trading API**: Recall Network trading infrastructure
- **Market Data**: CoinGecko API integration
- **Reports**: ReportLab PDF generation

### Infrastructure
- **Development**: Local development with hot reloading
- **Production**: Docker containerization ready
- **Database**: Supabase cloud PostgreSQL
- **API Integration**: RESTful APIs with comprehensive error handling
- **Monitoring**: Comprehensive logging and error tracking

## Quick Start

### Prerequisites

- **Node.js 18+** for frontend development
- **Python 3.8+** for backend development
- **API Keys**: Gemini AI, Supabase, Recall Network
- **Package Managers**: npm/yarn for frontend, pip for backend

### Installation

1. **Clone Repository**
```bash
git clone <repository-url>
cd kairos-ai-trading
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

3. **Frontend Setup**
```bash
cd frontend
npm install
# or yarn install

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Start Services**

Backend:
```bash
cd backend
source venv/bin/activate
python api_server.py
# Server starts on http://localhost:8000
```

Frontend:
```bash
cd frontend
npm run dev
# Application starts on http://localhost:3000
```

### Environment Configuration

#### Backend (.env)
```env
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Trading API Configuration
RECALL_API_KEY=your_recall_api_key_here
RECALL_SANDBOX_API_BASE=https://api.sandbox.competitions.recall.network
```

#### Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

## Usage Guide

### Autonomous Trading Mode

1. **Access AI Agent**: Navigate to the AI Agent section
2. **Select Agent Mode**: Choose "Agent" from the mode selector
3. **Configure Session**: Set trading duration (10 minutes to 24 hours)
4. **Start Trading**: Click "Start Trading" to begin autonomous session
5. **Monitor Progress**: View real-time updates and AI decision-making
6. **Download Reports**: Access PDF reports when session completes

### Interactive Assistant Mode

1. **Select Assistant Mode**: Choose "Assistant" from the mode selector
2. **Ask Questions**: Type queries about markets, portfolio, or crypto concepts
3. **Get Analysis**: Receive real-time market analysis and insights
4. **Portfolio Review**: Ask for portfolio optimization suggestions
5. **Market Updates**: Get latest news and price information

### Manual Trading

1. **Navigate to Trading**: Access the Manual Trading section
2. **Select Tokens**: Choose from/to tokens for your trade
3. **Set Amount**: Enter the amount to trade with balance validation
4. **Review Trade**: Check estimated output and fee information
5. **Execute Trade**: Confirm and execute the trade
6. **Track Results**: Monitor trade execution and portfolio updates

## API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portfolio` | GET | Current portfolio data |
| `/api/trade` | POST | Execute manual trade |
| `/api/chat` | POST | Start autonomous trading session |
| `/api/chat/assistant` | POST | Interactive AI assistant |
| `/api/autonomous/status/{id}` | GET | Trading session status |
| `/api/session/report/{id}` | GET | Download session PDF report |

### Real-Time Features

- **Portfolio Updates**: Live balance and value tracking
- **Price Feeds**: Real-time cryptocurrency prices
- **Session Monitoring**: Live autonomous trading progress
- **Trade Notifications**: Instant trade execution updates

## Security & Risk Management

### Trading Security
- **API Key Management**: Secure storage of all API credentials
- **Trade Validation**: Comprehensive pre-trade validation
- **Balance Verification**: Real-time balance checking
- **Position Limits**: Maximum 50% of token balance per trade

### Risk Controls
- **Portfolio Diversification**: Multi-asset allocation management
- **Chain Risk Management**: Distributed across multiple networks
- **AI Confidence Scoring**: Trade execution based on AI confidence levels
- **Stop-Loss Protection**: Intelligent risk management through AI decisions

### Data Security
- **Environment Variables**: Secure credential management
- **Database Security**: Supabase row-level security
- **API Rate Limiting**: Protection against abuse
- **Error Handling**: Secure error messages without sensitive data exposure

## Monitoring & Analytics

### Performance Metrics
- **Trading Success Rate**: Percentage of successful trades
- **Portfolio Performance**: Real-time P&L tracking
- **AI Confidence Trends**: Analysis of AI decision confidence
- **Risk-Adjusted Returns**: Performance relative to risk taken

### Reporting Features
- **Session Reports**: Comprehensive PDF reports for each trading session
- **Strategy Analysis**: AI decision pattern analysis
- **Performance Tracking**: Historical performance trends
- **Risk Assessment**: Detailed risk analysis and recommendations

## Development

### Project Structure

```
kairos-ai-trading/
├── frontend/               # React/Next.js web application
│   ├── src/app/           # Next.js app directory pages
│   ├── src/components/    # Reusable React components
│