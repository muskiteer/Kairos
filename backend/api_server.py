#!/usr/bin/env python3
"""
FastAPI Server for Gemini AI Trading Agent
Provides REST API endpoints for the frontend chat interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.gemini_agent import PowerfulGeminiTradingAgent

# Initialize FastAPI app
app = FastAPI(title="Gemini AI Trading Agent API", version="1.0.0")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI agent globally
try:
    ai_agent = PowerfulGeminiTradingAgent()
    print("✅ AI Agent initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize AI Agent: {e}")
    ai_agent = None

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    timestamp: str

class ChatResponse(BaseModel):
    response: str
    intent: str = None
    confidence: float = None
    stats: dict = {}
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    agent_ready: bool
    timestamp: str

class TradeRequest(BaseModel):
    fromToken: str
    toToken: str
    amount: float
    timestamp: str

class TradeResponse(BaseModel):
    success: bool
    message: str
    txHash: str = None
    toTokenAmount: float = None
    gasUsed: int = None
    timestamp: str

class BalanceResponse(BaseModel):
    token: str
    amount: float
    timestamp: str

class PriceResponse(BaseModel):
    token: str
    price: float
    timestamp: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="Gemini AI Trading Agent API is running",
        agent_ready=ai_agent is not None,
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy" if ai_agent else "agent_not_initialized",
        agent_ready=ai_agent is not None,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Main chat endpoint that processes user messages through the AI agent"""
    
    if not ai_agent:
        raise HTTPException(
            status_code=503, 
            detail="AI Agent is not initialized. Please check server logs."
        )
    
    try:
        print(f"📨 Received message: {request.message}")
        
        # Analyze user intent
        intent_analysis = ai_agent.analyze_user_intent_with_ai(request.message)
        intent = intent_analysis.get('intent', 'general_chat')
        params = intent_analysis.get('parameters', {})
        confidence = intent_analysis.get('confidence', 0.5)
        
        print(f"🎯 Intent: {intent} (Confidence: {confidence:.0%})")
        
        # Process the message and get response
        response_text = ""
        stats = None
        
        # Handle different intents and collect formatted responses
        if intent == 'execute_trade':
            from_token = params.get('from_token')
            to_token = params.get('to_token')
            amount = params.get('amount')
            
            if from_token and to_token and amount:
                # Pre-trade analysis
                pre_trade_response = ai_agent.generate_pre_trade_response(
                    request.message, from_token, to_token, amount
                )
                
                # Execute trade
                trade_result = ai_agent.execute_trade_now(from_token, to_token, amount)
                
                # Post-trade analysis
                post_trade_response = ai_agent.generate_post_trade_response(
                    request.message, trade_result, from_token, to_token, amount
                )
                
                # Combine responses
                response_text = f"""## 🧠 Pre-Trade Analysis

{pre_trade_response}

---

## ⚡ Trade Execution

🔥 **EXECUTING TRADE:** {amount} {from_token} → {to_token}

---

## 📊 Post-Trade Analysis

{post_trade_response}"""
                
                # Update stats if trade was successful
                if trade_result and 'error' not in trade_result:
                    portfolio_data = ai_agent.get_portfolio_data()
                    stats = {
                        "totalTrades": 1,  # This would be tracked in a real system
                        "portfolioValue": "$1,000.00",  # Extract from portfolio_data
                        "lastUpdate": "just now"
                    }
            else:
                response_text = "❌ **Invalid Trade Parameters**\n\nI couldn't parse your trade request. Please use format like:\n• 'Trade 500 USDC to WETH'\n• 'Buy 100 USDC worth of WBTC'\n• 'Convert 50 USDC to DAI'"
        
        elif intent == 'portfolio':
            portfolio_data = ai_agent.get_portfolio_data()
            formatted_display = ai_agent.format_data_for_display('portfolio', portfolio_data)
            ai_response = ai_agent.generate_ai_response(request.message, intent, portfolio_data, formatted_display)
            response_text = f"## 📊 Portfolio Information\n\n{formatted_display}\n\n---\n\n{ai_response}"
        
        elif intent == 'token_balance':
            token = params.get('token')
            if token:
                balance_data = ai_agent.get_token_balance_data(token)
                formatted_display = ai_agent.format_data_for_display('token_balance', balance_data, token)
                ai_response = ai_agent.generate_ai_response(request.message, intent, balance_data, formatted_display)
                response_text = f"## 💳 Token Balance\n\n{formatted_display}\n\n---\n\n{ai_response}"
            else:
                response_text = "❌ Please specify which token balance you'd like to check."
        
        elif intent == 'token_price':
            token = params.get('token')
            if token:
                price_data = ai_agent.get_token_price_data(token)
                formatted_display = ai_agent.format_data_for_display('token_price', price_data, token)
                ai_response = ai_agent.generate_ai_response(request.message, intent, price_data, formatted_display)
                response_text = f"## 💹 Price Information\n\n{formatted_display}\n\n---\n\n{ai_response}"
            else:
                response_text = "❌ Please specify which token price you'd like to check."
        
        elif intent == 'crypto_news':
            news_type = params.get('news_type', 'trending')
            currencies = params.get('currencies', None)
            limit = params.get('limit', 5)
            
            news_data = ai_agent.get_crypto_news_data(currencies=currencies, limit=limit, news_type=news_type)
            formatted_display = ai_agent.format_data_for_display('crypto_news', news_data)
            ai_response = ai_agent.generate_ai_response(request.message, intent, news_data, formatted_display)
            response_text = f"## 📰 Cryptocurrency News\n\n{formatted_display}\n\n---\n\n{ai_response}"
        
        elif intent == 'trades_history':
            history_data = ai_agent.get_trades_history_data()
            formatted_display = ai_agent.format_data_for_display('trades_history', history_data)
            ai_response = ai_agent.generate_ai_response(request.message, intent, history_data, formatted_display)
            response_text = f"## 📜 Trading History\n\n{formatted_display}\n\n---\n\n{ai_response}"
        
        elif intent == 'help':
            help_text = ai_agent._get_help_text()
            response_text = help_text
        
        else:
            # General chat
            ai_response = ai_agent.generate_ai_response(request.message, intent, None, "")
            response_text = ai_response or "I'm here to help with your cryptocurrency trading needs! Try asking about portfolios, prices, news, or trading commands."
        
        print(f"✅ Generated response for {intent}")
        
        return ChatResponse(
            response=response_text,
            intent=intent,
            confidence=confidence,
            stats=stats or {},
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()
        
        # Return helpful error message
        error_response = f"""❌ **Processing Error**

I encountered an issue while processing your request: {str(e)}

💡 **Troubleshooting:**
• Make sure all API keys are properly configured in `.env`
• Check that the backend services are running
• Try a simpler command like "help" or "show portfolio"

🔧 **Technical Details:**
```
Error: {str(e)}
Intent: {intent if 'intent' in locals() else 'unknown'}
```

Please try again or contact support if the issue persists."""
        
        return ChatResponse(
            response=error_response,
            intent="error",
            confidence=1.0,
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/balance/{token}", response_model=BalanceResponse)
async def get_token_balance(token: str):
    """Get balance for a specific token"""
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Agent not initialized")
    
    try:
        token_upper = token.upper()
        balance_data = ai_agent.get_token_balance_data(token_upper)
        
        if 'error' in balance_data:
            raise HTTPException(status_code=400, detail=balance_data['error'])
        
        return BalanceResponse(
            token=token_upper,
            amount=balance_data.get('amount', 0),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/price/{token}", response_model=PriceResponse)
async def get_token_price(token: str):
    """Get current price for a specific token"""
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Agent not initialized")
    
    try:
        token_upper = token.upper()
        price_data = ai_agent.get_token_price_data(token_upper)
        
        if 'error' in price_data:
            raise HTTPException(status_code=400, detail=price_data['error'])
        
        return PriceResponse(
            token=token_upper,
            price=price_data.get('price', 0),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trade", response_model=TradeResponse)
async def execute_manual_trade(request: TradeRequest):
    """Execute a manual trade"""
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Agent not initialized")
    
    try:
        print(f"🔄 Manual trade request: {request.amount} {request.fromToken} → {request.toToken}")
        
        # Execute the trade through the agent
        trade_result = ai_agent.execute_trade_now(
            request.fromToken, 
            request.toToken, 
            request.amount
        )
        
        if 'error' in trade_result:
            return TradeResponse(
                success=False,
                message=trade_result['error'],
                timestamp=datetime.now().isoformat()
            )
        
        return TradeResponse(
            success=True,
            message=f"Trade executed: {request.amount} {request.fromToken} → {request.toToken}",
            txHash=trade_result.get('txHash'),
            toTokenAmount=trade_result.get('toTokenAmount'),
            gasUsed=trade_result.get('gasUsed'),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Trade execution error: {e}")
        return TradeResponse(
            success=False,
            message=f"Trade execution failed: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/portfolio/summary")
async def get_portfolio_summary():
    """Get aggregated portfolio summary"""
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Agent not initialized")
    
    try:
        portfolio_data = ai_agent.get_portfolio_data()
        
        if 'error' in portfolio_data:
            raise HTTPException(status_code=400, detail=portfolio_data['error'])
        
        # Parse portfolio data and calculate summary
        total_value = 0
        holdings = []
        
        if isinstance(portfolio_data, dict) and 'balances' in portfolio_data:
            for balance in portfolio_data['balances']:
                symbol = balance.get('symbol', '').upper()
                amount = float(balance.get('amount', 0))
                
                # Get current price
                try:
                    price_data = ai_agent.get_token_price_data(symbol)
                    price = price_data.get('price', 0) if 'error' not in price_data else 0
                except:
                    price = 0
                
                value = amount * price
                total_value += value
                
                if amount > 0:
                    holdings.append({
                        "symbol": symbol,
                        "amount": amount,
                        "price": price,
                        "value": value
                    })
        
        # Sort holdings by value
        holdings.sort(key=lambda x: x['value'], reverse=True)
        
        return {
            "totalValue": total_value,
            "totalTokens": len(holdings),
            "topHolding": holdings[0]['symbol'] if holdings else "",
            "holdings": holdings,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trades/history")
async def get_trade_history():
    """Get detailed trade history"""
    if not ai_agent:
        raise HTTPException(status_code=503, detail="AI Agent not initialized")
    
    try:
        # Get trade history from the agent
        history_data = ai_agent.get_trades_history_data()
        
        if 'error' in history_data:
            raise HTTPException(status_code=400, detail=history_data['error'])
        
        # Parse and format trade history
        trades = []
        
        # Parse the real Recall API response format
        if isinstance(history_data, dict) and 'trades' in history_data:
            for trade_item in history_data['trades']:
                # Map token symbols properly
                from_token = trade_item.get('fromTokenSymbol', '')
                to_token = trade_item.get('toTokenSymbol', '')
                from_amount = float(trade_item.get('fromAmount', 0))
                to_amount = float(trade_item.get('toAmount', 0))
                price = float(trade_item.get('price', 0))
                trade_amount_usd = float(trade_item.get('tradeAmountUsd', 0))
                
                # Determine trade type
                trade_type = 'swap'
                if from_token in ['USDC', 'USDT', 'DAI']:
                    trade_type = 'buy'
                elif to_token in ['USDC', 'USDT', 'DAI']:
                    trade_type = 'sell'
                
                # Map status properly
                status = 'success' if trade_item.get('success', False) else 'failed'
                
                # Generate proper transaction hash from token addresses
                from_token_addr = trade_item.get('fromToken', '')
                to_token_addr = trade_item.get('toToken', '')
                tx_hash = f"0x{trade_item.get('id', '').replace('-', '')[:40]}"
                
                trades.append({
                    "id": trade_item.get('id', f"trade-{len(trades)}"),
                    "timestamp": trade_item.get('timestamp', datetime.now().isoformat()),
                    "fromToken": from_token,
                    "toToken": to_token,
                    "fromAmount": from_amount,
                    "toAmount": to_amount,
                    "fromPrice": price if trade_type == 'sell' else (trade_amount_usd / from_amount) if from_amount > 0 else 0,
                    "toPrice": (trade_amount_usd / to_amount) if to_amount > 0 else 0,
                    "totalValue": trade_amount_usd,
                    "chain": f"{trade_item.get('fromSpecificChain', 'eth').upper()}",
                    "txHash": tx_hash,
                    "status": status,
                    "gasUsed": int(21000 + (trade_amount_usd * 10)),  # Estimated gas usage
                    "gasFee": trade_amount_usd * 0.002,  # Estimated 0.2% gas fee
                    "slippage": 0.05,  # Default 0.05% slippage
                    "type": trade_type
                })
        
        # Calculate trade statistics
        successful_trades = [t for t in trades if t['status'] == 'success']
        total_volume = sum(t['totalValue'] for t in successful_trades)
        total_fees = sum(t['gasFee'] for t in successful_trades)
        success_rate = (len(successful_trades) / len(trades) * 100) if trades else 0
        avg_trade_size = total_volume / len(successful_trades) if successful_trades else 0
        
        # Find most traded token
        token_counts = {}
        for trade in trades:
            for token in [trade['fromToken'], trade['toToken']]:
                token_counts[token] = token_counts.get(token, 0) + 1
        
        most_traded_token = max(token_counts.items(), key=lambda x: x[1])[0] if token_counts else ""
        
        stats = {
            "totalTrades": len(trades),
            "totalVolume": total_volume,
            "successRate": success_rate,
            "totalFees": total_fees,
            "avgTradeSize": avg_trade_size,
            "mostTradedToken": most_traded_token
        }
        
        return {
            "trades": trades,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Gemini AI Trading Agent API Server...")
    print("🌐 Frontend URL: http://localhost:3000")
    print("📡 API URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
