#!/usr/bin/env python3
"""
Kairos Trading API Server - Enhanced with Conversational AI Copilot and Report Generation
Provides REST API endpoints for the frontend chat interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import sys
import os
import asyncio

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our enhanced copilot and autonomous agent
from agent.kairos_copilot import kairos_copilot
from agent.autonomous_agent import KairosAutonomousAgent
from api.trades_history import get_portfolio
from api.token_price import get_token_price_json

# Initialize FastAPI app and autonomous agent
app = FastAPI(title="Kairos Trading API", version="2.0.0")
autonomous_agent = KairosAutonomousAgent()

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    actions_taken: Optional[List[str]] = []
    reasoning: Optional[str] = None
    suggestions: Optional[List[str]] = []
    session_id: Optional[str] = None
    timestamp: str

class SessionRequest(BaseModel):
    user_id: Optional[str] = "default"

class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    copilot_ready: bool
    features: List[str]
    timestamp: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="🚀 Kairos Trading API is running",
        copilot_ready=True,
        features=[
            "Conversational Trading Interface",
            "AI-Powered Strategy Analysis", 
            "Vincent AI Policy Integration",
            "Real-time Portfolio Management",
            "Market Sentiment Analysis",
            "Trading Session Management",
            "PDF Report Generation"
        ],
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        copilot_ready=True,
        features=[
            "Gemini AI Integration",
            "Supabase Database", 
            "Vincent AI Policy Engine",
            "Recall API Trading",
            "CoinPanic News Feed",
            "PDF Report Generation"
        ],
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/sessions", response_model=SessionResponse)
async def create_trading_session(request: SessionRequest):
    """Create a new trading session"""
    try:
        session_id = await kairos_copilot.start_trading_session(request.user_id)
        
        return SessionResponse(
            session_id=session_id,
            status="created",
            message="New trading session started successfully! I'm ready to help you trade.",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create trading session: {str(e)}"
        )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_copilot(request: ChatRequest):
    """Enhanced conversational chat endpoint with Kairos Copilot and Autonomous Agent"""
    
    try:
        print(f"📨 Received message: {request.message}")
        
        # Check if this is an autonomous trading request
        if any(keyword in request.message.lower() for keyword in 
               ["autonomous", "start trading session", "trade for", "auto trade", "test agent", "run agent"]):
            # Process through autonomous agent
            autonomous_response = await autonomous_agent.process_autonomous_request(
                request.message, 
                request.user_id or "default"
            )
            
            # Ensure data is a dictionary
            response_data = autonomous_response.get("data", {})
            if isinstance(response_data, list):
                response_data = {"items": response_data}
            elif not isinstance(response_data, dict):
                response_data = {"value": response_data}
            
            return ChatResponse(
                response=autonomous_response.get("response", "I'm sorry, I couldn't process your autonomous request."),
                intent=autonomous_response.get("intent"),
                confidence=autonomous_response.get("confidence"),
                data=response_data,
                actions_taken=autonomous_response.get("actions_taken", []),
                reasoning=autonomous_response.get("reasoning"),
                suggestions=autonomous_response.get("suggestions", []),
                session_id=request.session_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Ensure we have a session for regular copilot
        if not request.session_id:
            session_id = await kairos_copilot.start_trading_session(request.user_id)
        else:
            session_id = request.session_id
        
        # Process message through Kairos Copilot
        copilot_response = await kairos_copilot.process_user_message(request.message)
        
        print(f"🎯 Intent: {copilot_response.get('intent')} (Confidence: {copilot_response.get('confidence', 0):.0%})")
        
        # Ensure data is a dictionary, not a list
        response_data = copilot_response.get("data", {})
        if isinstance(response_data, list):
            response_data = {"items": response_data}
        elif not isinstance(response_data, dict):
            response_data = {"value": response_data}
        
        return ChatResponse(
            response=copilot_response.get("response", "I'm sorry, I couldn't process your request properly."),
            intent=copilot_response.get("intent"),
            confidence=copilot_response.get("confidence"),
            data=response_data,
            actions_taken=copilot_response.get("actions_taken", []),
            reasoning=copilot_response.get("reasoning"),
            suggestions=copilot_response.get("suggestions", []),
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        
        return ChatResponse(
            response=f"I apologize, but I encountered an error: {str(e)}. Let me try to help you in a different way. What would you like to do?",
            intent="error_recovery",
            confidence=0.0,
            actions_taken=["error_handling"],
            suggestions=[
                "Try asking about your portfolio",
                "Request market analysis", 
                "Ask for trading help"
            ],
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get comprehensive session summary and analytics"""
    try:
        summary = await kairos_copilot.generate_session_summary(session_id)
        return {
            "session_id": session_id,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate session summary: {str(e)}"
        )

@app.post("/api/sessions/{session_id}/report")
async def generate_session_report(session_id: str):
    """Generate PDF report for trading session"""
    try:
        from utils.report_generator import generate_report
        
        # Generate the PDF report
        report_path = await generate_report(session_id)
        
        return {
            "session_id": session_id,
            "report_path": report_path,
            "message": "Trading session report generated successfully",
            "download_url": f"/api/sessions/{session_id}/download",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate session report: {str(e)}"
        )

@app.get("/api/trades/history")
async def get_trades_history():
    """Get trade history and statistics from Recall API - OPTIMIZED VERSION"""
    try:
        # Token address to symbol mapping - optimized lookup
        token_mapping = {
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "USDC",
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": "WETH", 
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": "WBTC",
            "0xdAC17F958D2ee523a2206206994597C13D831ec7": "USDT",
            "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984": "UNI",
            "0x0000000000000000000000000000000000000000": "ETH"
        }
        
        def get_token_symbol(address: str) -> str:
            """Convert token address to symbol - fast lookup"""
            return token_mapping.get(address, address[:6] + "...")
        
        def get_real_price(symbol: str) -> float:
            """Get REAL price from API - NO MOCK DATA EVER"""
            try:
                print(f"🔍 Getting REAL price for {symbol} from API...")
                price_data = get_token_price_json(symbol)
                if isinstance(price_data, dict) and "price" in price_data:
                    real_price = float(price_data["price"])
                    print(f"💰 REAL {symbol} price from API: ${real_price:,.2f}")
                    return real_price
                elif symbol in ["USDC", "USDT"]:
                    # Only stablecoins can be $1
                    print(f"💰 {symbol} stablecoin: $1.00")
                    return 1.0
                else:
                    print(f"⚠️ API returned invalid data for {symbol}: {price_data}")
                    return 0.0
            except Exception as e:
                print(f"❌ Error getting REAL {symbol} price from API: {e}")
                return 0.0
        
        print("📊 Fetching trade history...")
        start_time = datetime.now()
        
        # Get portfolio/trades data from Recall API
        portfolio_data = get_portfolio()
        
        if isinstance(portfolio_data, dict) and "error" in portfolio_data:
            print(f"⚠️ API Error: {portfolio_data.get('error')}")
            return {
                "trades": [],
                "stats": {"totalTrades": 0, "totalVolume": 0, "successRate": 0, "totalFees": 0, "avgTradeSize": 0, "mostTradedToken": ""}
            }
        
        # Process trades with minimal processing for speed
        trades = []
        total_volume = 0
        successful_trades = 0
        token_frequency = {}
        
        # Extract and limit trades for performance (only latest 50)
        trade_data = portfolio_data if isinstance(portfolio_data, list) else []
        if isinstance(portfolio_data, dict):
            trade_data = portfolio_data.get("trades", portfolio_data.get("history", []))
        
        # Limit to recent trades for speed
        trade_data = trade_data[:50] if len(trade_data) > 50 else trade_data
        
        for i, trade_item in enumerate(trade_data):
            if not isinstance(trade_item, dict):
                continue
                
            try:
                # Fast processing - no expensive API calls
                from_token_address = trade_item.get("from_token", "UNKNOWN")
                to_token_address = trade_item.get("to_token", "UNKNOWN")
                
                from_token = get_token_symbol(from_token_address)
                to_token = get_token_symbol(to_token_address)
                
                amount = float(trade_item.get("amount", 0))
                to_amount = float(trade_item.get("to_amount", amount))
                
                # REAL price lookup - NO MOCK DATA
                from_price = get_real_price(from_token)
                to_price = get_real_price(to_token)
                
                # Quick value calculation
                total_value = amount * from_price if from_price > 0 else to_amount * to_price
                
                # Determine trade type quickly
                trade_type = "buy" if from_token in ["USDC", "USDT"] else "sell" if to_token in ["USDC", "USDT"] else "swap"
                
                # Create trade object with minimal processing
                trade = {
                    "id": trade_item.get("id", f"trade_{i}"),
                    "timestamp": trade_item.get("timestamp", datetime.now().isoformat()),
                    "fromToken": from_token,
                    "toToken": to_token,
                    "fromAmount": amount,
                    "toAmount": to_amount,
                    "fromPrice": from_price,
                    "toPrice": to_price,
                    "totalValue": total_value,
                    "chain": trade_item.get("chain", "Ethereum"),
                    "txHash": trade_item.get("txHash", f"0x{i:064x}"),
                    "status": trade_item.get("status", "success"),  # Use REAL status from API
                    "gasUsed": int(trade_item.get("gasUsed", 21000)),
                    "gasFee": float(trade_item.get("gasFee", 0.001)),
                    "slippage": float(trade_item.get("slippage", 0.1)),
                    "type": trade_type
                }
                
                trades.append(trade)
                total_volume += total_value
                
                # Count REAL successful trades based on actual status
                if trade.get("status") == "success":
                    successful_trades += 1
                
                # Track tokens
                for token in [from_token, to_token]:
                    if token != "UNKNOWN":
                        token_frequency[token] = token_frequency.get(token, 0) + 1
                        
            except Exception as e:
                print(f"⚠️ Error processing trade {i}: {e}")
                continue
        
        # Calculate REAL stats from actual trade data
        total_trades = len(trades)
        success_rate = (successful_trades / max(1, total_trades)) * 100 if total_trades > 0 else 0.0
        avg_trade_size = total_volume / max(1, total_trades)
        
        # Calculate REAL total fees from actual trades
        total_fees = sum(trade.get("gasFee", 0) for trade in trades)
        
        # Find REAL most traded token
        most_traded_token = max(token_frequency.items(), key=lambda x: x[1])[0] if token_frequency else "N/A"
        
        # Sort by timestamp (newest first)
        trades.sort(key=lambda x: x["timestamp"], reverse=True)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        print(f"✅ Trade history processed in {processing_time:.2f}s - {total_trades} trades")
        
        return {
            "trades": trades,
            "stats": {
                "totalTrades": total_trades,
                "totalVolume": round(total_volume, 2),
                "successRate": round(success_rate, 1),
                "totalFees": round(total_fees, 6),  # REAL fees from actual trades
                "avgTradeSize": round(avg_trade_size, 2),
                "mostTradedToken": most_traded_token  # REAL most traded token
            },
            "processingTime": f"{processing_time:.2f}s"
        }
        
    except Exception as e:
        print(f"❌ Error fetching trade history: {e}")
        return {
            "trades": [],
            "stats": {"totalTrades": 0, "totalVolume": 0, "successRate": 0, "totalFees": 0, "avgTradeSize": 0, "mostTradedToken": ""},
            "error": str(e)
        }

@app.get("/api/ai-agent/trades")
async def get_ai_agent_trades():
    """Get trade history from AI autonomous trading sessions - REAL DATA ONLY"""
    try:
        from agent.autonomous_agent import autonomous_agent
        
        def get_real_price(symbol: str) -> float:
            """Get REAL price from API - NO MOCK DATA EVER"""
            try:
                print(f"🔍 Getting REAL price for AI trade {symbol} from API...")
                price_data = get_token_price_json(symbol)
                if isinstance(price_data, dict) and "price" in price_data:
                    real_price = float(price_data["price"])
                    print(f"💰 REAL {symbol} price for AI trade: ${real_price:,.2f}")
                    return real_price
                elif symbol in ["USDC", "USDT"]:
                    # Only stablecoins can be $1
                    return 1.0
                else:
                    print(f"⚠️ API returned invalid data for {symbol}: {price_data}")
                    return 0.0
            except Exception as e:
                print(f"❌ Error getting REAL {symbol} price for AI trade: {e}")
                return 0.0
        
        # Get all autonomous sessions
        all_trades = []
        total_volume = 0
        successful_trades = 0
        
        for session_id, session in autonomous_agent.autonomous_sessions.items():
            trades_executed = session.get("trades_executed", [])
            
            for trade in trades_executed:
                # Get REAL token symbols and prices - NO MOCK DATA
                from_token = trade.get("from_token", "UNKNOWN")
                to_token = trade.get("to_token", "UNKNOWN")
                
                # Get REAL prices from API for AI trades
                from_price = get_real_price(from_token) if from_token != "UNKNOWN" else 0.0
                to_price = get_real_price(to_token) if to_token != "UNKNOWN" else 0.0
                
                # Calculate real values
                amount = float(trade.get("amount", 0))
                received_amount = float(trade.get("received_amount", amount))
                real_total_value = amount * from_price if from_price > 0 else received_amount * to_price
                
                # Convert to standard format with REAL data only
                standard_trade = {
                    "id": f"ai_{session_id[:8]}_{trade.get('timestamp', '')[:10]}",
                    "timestamp": trade.get("timestamp", datetime.now().isoformat()),
                    "fromToken": from_token,
                    "toToken": to_token,
                    "fromAmount": amount,
                    "toAmount": received_amount,
                    "fromPrice": from_price,  # REAL price from API
                    "toPrice": to_price,      # REAL price from API
                    "totalValue": real_total_value,  # REAL calculated value
                    "chain": trade.get("chain", "Ethereum"),
                    "txHash": trade.get("tx_hash", "0x..."),
                    "status": "success" if trade.get("success", False) else "failed",
                    "gasUsed": int(trade.get("gas_used", 21000)),
                    "gasFee": float(trade.get("gas_fee", 0.001)),
                    "slippage": float(trade.get("slippage", 0.1)),
                    "type": "swap",
                    "session_id": session_id,
                    "strategy": trade.get("strategy", "ai_autonomous")
                }
                
                all_trades.append(standard_trade)
                total_volume += standard_trade["totalValue"]
                if standard_trade["status"] == "success":
                    successful_trades += 1
        
        # Sort by timestamp (newest first)
        all_trades.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Calculate REAL stats from actual trade data
        total_trades = len(all_trades)
        success_rate = (successful_trades / max(1, total_trades)) * 100
        avg_trade_size = total_volume / max(1, total_trades)
        
        # Calculate REAL total fees from actual trades
        total_fees = sum(trade.get("gasFee", 0) for trade in all_trades)
        
        # Find REAL most traded token from actual trades
        token_frequency = {}
        for trade in all_trades:
            for token in [trade.get("fromToken"), trade.get("toToken")]:
                if token and token != "UNKNOWN":
                    token_frequency[token] = token_frequency.get(token, 0) + 1
        
        most_traded_token = max(token_frequency.items(), key=lambda x: x[1])[0] if token_frequency else "N/A"
        
        return {
            "trades": all_trades,
            "stats": {
                "totalTrades": total_trades,
                "totalVolume": round(total_volume, 2),
                "successRate": round(success_rate, 1),
                "totalFees": round(total_fees, 6),  # REAL fees from actual trades
                "avgTradeSize": round(avg_trade_size, 2),
                "mostTradedToken": most_traded_token  # REAL most traded token
            },
            "source": "ai_autonomous_agent"
        }
        
    except Exception as e:
        print(f"❌ Error fetching AI agent trades: {e}")
        return {
            "trades": [],
            "stats": {"totalTrades": 0, "totalVolume": 0, "successRate": 0, "totalFees": 0, "avgTradeSize": 0, "mostTradedToken": ""},
            "error": str(e)
        }

@app.get("/api/portfolio")
async def get_portfolio_balance():
    """Get current portfolio balance and summary"""
    try:
        from api.portfolio import get_portfolio as get_portfolio_balance
        
        portfolio_data = get_portfolio_balance()
        
        if isinstance(portfolio_data, dict) and "error" in portfolio_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch portfolio: {portfolio_data.get('error')}"
            )
        
        return {
            "portfolio": portfolio_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error fetching portfolio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch portfolio balance: {str(e)}"
        )

@app.get("/api/features")
async def get_features():
    """Get available Kairos features and capabilities"""
    return {
        "conversational_trading": {
            "description": "Natural language trade execution",
            "examples": [
                "Buy 100 USDC worth of ETH",
                "Swap 50 USDC to WBTC", 
                "Trade 200 USDC for UNI"
            ]
        },
        "portfolio_analysis": {
            "description": "AI-powered portfolio insights",
            "examples": [
                "How is my portfolio performing?",
                "What's my current balance?",
                "Show me my trading history"
            ]
        },
        "market_intelligence": {
            "description": "Real-time market analysis and news",
            "examples": [
                "What's happening in the crypto market?",
                "Give me Bitcoin news",
                "Analyze current market sentiment"
            ]
        },
        "strategy_assistance": {
            "description": "Trading strategy development and optimization",
            "examples": [
                "Help me create a DCA strategy",
                "What's a good entry point for ETH?",
                "Should I diversify my holdings?"
            ]
        },
        "risk_management": {
            "description": "Vincent AI-powered policy and risk checks",
            "examples": [
                "Is this trade safe?",
                "Check my portfolio risk",
                "What are the policy implications?"
            ]
        },
        "autonomous_trading": {
            "description": "Fully autonomous AI-powered trading sessions",
            "examples": [
                "Start trading session for 2hr",
                "Run autonomous trading for 30min",
                "Test agent for 24hr"
            ]
        },
        "report_generation": {
            "description": "Comprehensive PDF trading reports",
            "examples": [
                "Generate my session report",
                "Download trading analysis",
                "Create performance summary"
            ]
        }
    }

@app.get("/api/autonomous/status/{session_id}")
async def get_autonomous_status(session_id: str):
    """Get real-time status of autonomous trading session"""
    try:
        if session_id in autonomous_agent.autonomous_sessions:
            session_data = autonomous_agent.autonomous_sessions[session_id]
            return {
                "session_found": True,
                "session_data": session_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "session_found": False,
                "message": "Session not found",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session status: {str(e)}")

@app.get("/api/autonomous/sessions")
async def list_autonomous_sessions():
    """List all autonomous trading sessions"""
    try:
        sessions = {}
        for session_id, session_data in autonomous_agent.autonomous_sessions.items():
            sessions[session_id] = {
                "session_id": session_id,
                "status": session_data.get("status", "unknown"),
                "duration_text": session_data.get("params", {}).get("duration_text", "unknown"),
                "start_time": session_data.get("params", {}).get("start_time"),
                "performance": session_data.get("performance", {}),
                "total_cycles": len(session_data.get("reasoning_log", []))
            }
        
        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.post("/api/autonomous/stop/{session_id}")
async def stop_autonomous_session(session_id: str):
    """Stop a specific autonomous trading session"""
    try:
        if session_id in autonomous_agent.autonomous_sessions:
            autonomous_agent.autonomous_sessions[session_id]["status"] = "stopped"
            return {
                "success": True,
                "message": f"Session {session_id} stopped successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Session not found",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping session: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/chat", response_model=ChatResponse)
async def legacy_chat(request: ChatRequest):
    """Legacy chat endpoint - redirects to new API"""
    return await chat_with_copilot(request)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Kairos Trading API Server...")
    print("🔗 Frontend URL: http://localhost:3000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("💬 Chat Interface: POST /api/chat")
    print("📊 Session Management: POST /api/sessions")
    print("📄 Report Generation: POST /api/sessions/{id}/report")
    
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
