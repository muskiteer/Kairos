#!/usr/bin/env python3
"""
Kairos Trading API Server - Enhanced with Conversational AI Copilot and Report Generation
Provides REST API endpoints for the frontend chat interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import sys
import os
import asyncio

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Load environment variables from the backend directory
from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

# Import our enhanced copilot and autonomous agent
from agent.kairos_copilot import KairosTradingCopilot
from agent.autonomous_agent import KairosAutonomousAgent
from api.trades_history import get_portfolio
from api.token_price import get_token_price_json
from api.profile import profile_router

# Initialize FastAPI app and store agent instances per user
app = FastAPI(title="Kairos Trading API", version="2.0.0")
user_agents = {}  # Store user-specific agents

def get_user_copilot(user_id: str = "default") -> KairosTradingCopilot:
    """Get or create a user-specific copilot instance"""
    if user_id not in user_agents:
        user_agents[user_id] = {
            "copilot": KairosTradingCopilot(user_id=user_id),
            "autonomous": KairosAutonomousAgent(user_id=user_id)
        }
    return user_agents[user_id]["copilot"]

def get_user_autonomous_agent(user_id: str = "default") -> KairosAutonomousAgent:
    """Get or create a user-specific autonomous agent instance"""
    if user_id not in user_agents:
        user_agents[user_id] = {
            "copilot": KairosTradingCopilot(user_id=user_id),
            "autonomous": KairosAutonomousAgent(user_id=user_id)
        }
    return user_agents[user_id]["autonomous"]

# Include profile router
app.include_router(profile_router)

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
        user_id = request.user_id or "default"
        
        # Check if this is an autonomous trading request
        if any(keyword in request.message.lower() for keyword in 
               ["autonomous", "start trading session", "trade for", "auto trade", "test agent", "run agent"]):
            # Process through user-specific autonomous agent
            autonomous_agent = get_user_autonomous_agent(user_id)
            autonomous_response = await autonomous_agent.process_autonomous_request(
                request.message, 
                user_id
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
            copilot = get_user_copilot(user_id)
            session_id = await copilot.start_trading_session(user_id)
        else:
            session_id = request.session_id
        
        # Process message through user-specific Kairos Copilot
        copilot = get_user_copilot(user_id)
        copilot_response = await copilot.process_user_message(request.message)
        
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
async def get_session_summary(session_id: str, user_id: str = "default"):
    """Get comprehensive session summary and analytics"""
    try:
        copilot = get_user_copilot(user_id)
        summary = await copilot.generate_session_summary(session_id)
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
async def get_trades_history(user_id: str = "default"):
    """Get trade history from Recall API - ENHANCED WITH DYNAMIC API KEYS"""
    try:
        print(f"📊 Fetching trade history from Recall API for user: {user_id}...")
        start_time = datetime.now()
        
        # Get trades data with user-specific API key
        from api.trades_history import get_portfolio
        recall_data = get_portfolio(user_id)
        
        if not recall_data or isinstance(recall_data, dict) and "error" in recall_data:
            error_msg = recall_data.get('error') if recall_data else 'No data returned'
            print(f"⚠️ API Error: {error_msg}")
            
            # If it's an API key issue, provide helpful message
            if "key" in error_msg.lower() or "authorization" in error_msg.lower():
                return {
                    "trades": [],
                    "stats": {"totalTrades": 0, "totalVolume": 0, "successRate": 0, "totalFees": 0, "avgTradeSize": 0, "mostTradedToken": ""},
                    "message": "Please configure your Recall API key in your profile to view trading data.",
                    "error": error_msg
                }
            
            return {
                "trades": [],
                "stats": {"totalTrades": 0, "totalVolume": 0, "successRate": 0, "totalFees": 0, "avgTradeSize": 0, "mostTradedToken": ""},
                "error": error_msg
            }
        
        # Extract trades from the recall API response
        trades_list = []
        if isinstance(recall_data, dict) and "trades" in recall_data:
            raw_trades = recall_data["trades"]
        else:
            raw_trades = recall_data if isinstance(recall_data, list) else []
        
        print(f"🔍 Processing {len(raw_trades)} trades from Recall API...")
        
        # Process each trade from the actual API structure
        for i, trade_item in enumerate(raw_trades):
            try:
                # Map the real Recall API fields to our frontend format
                trade = {
                    "id": trade_item.get("id", f"trade_{i}"),
                    "timestamp": trade_item.get("timestamp", datetime.now().isoformat()),
                    "fromToken": trade_item.get("fromTokenSymbol", "UNKNOWN"),
                    "toToken": trade_item.get("toTokenSymbol", "UNKNOWN"),
                    "fromAmount": float(trade_item.get("fromAmount", 0)),
                    "toAmount": float(trade_item.get("toAmount", 0)),
                    "fromPrice": float(trade_item.get("price", 0)),  # This is the exchange rate
                    "toPrice": 1.0,  # Calculate inverse if needed
                    "totalValue": float(trade_item.get("tradeAmountUsd", 0)),
                    "chain": trade_item.get("fromSpecificChain", "eth").title(),
                    "txHash": trade_item.get("id", f"0x{i:064x}"),  # Use trade ID as txHash for now
                    "status": "success" if trade_item.get("success", False) else "failed",
                    "gasUsed": 21000,  # Default gas used
                    "gasFee": 0.005,   # Estimated gas fee
                    "slippage": 0.1,   # Default slippage
                    "type": "swap",    # All trades are swaps from the data
                    "source": "manual" # Mark as manual trades from Recall API
                }
                
                # Calculate proper prices if needed
                if trade["fromAmount"] > 0 and trade["toAmount"] > 0:
                    trade["fromPrice"] = trade["totalValue"] / trade["fromAmount"]
                    trade["toPrice"] = trade["totalValue"] / trade["toAmount"]
                
                trades_list.append(trade)
                
            except Exception as e:
                print(f"⚠️ Error processing trade {i}: {e}")
                continue
        
        # Calculate statistics from the processed trades
        total_trades = len(trades_list)
        successful_trades = len([t for t in trades_list if t["status"] == "success"])
        total_volume = sum(trade["totalValue"] for trade in trades_list)
        total_fees = sum(trade["gasFee"] for trade in trades_list)
        
        # Find most traded token
        token_frequency = {}
        for trade in trades_list:
            for token in [trade["fromToken"], trade["toToken"]]:
                if token and token != "UNKNOWN":
                    token_frequency[token] = token_frequency.get(token, 0) + 1
        
        most_traded_token = max(token_frequency.items(), key=lambda x: x[1])[0] if token_frequency else "N/A"
        
        # Sort by timestamp (newest first)
        trades_list.sort(key=lambda x: x["timestamp"], reverse=True)
        
        stats = {
            "totalTrades": total_trades,
            "totalVolume": round(total_volume, 2),
            "successRate": round((successful_trades / max(1, total_trades)) * 100, 1),
            "totalFees": round(total_fees, 6),
            "avgTradeSize": round(total_volume / max(1, total_trades), 2),
            "mostTradedToken": most_traded_token
        }
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        print(f"✅ Processed {total_trades} trades in {processing_time:.2f}s")
        
        return {
            "trades": trades_list,
            "stats": stats,
            "processingTime": f"{processing_time:.2f}s"
        }
        
    except Exception as e:
        print(f"❌ Error fetching trade history: {e}")
        import traceback
        traceback.print_exc()
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
async def get_autonomous_status(session_id: str, user_id: str = "default"):
    """Get real-time status of autonomous trading session and generate PDF report"""
    try:
        print(f"🔍 Status request for session {session_id[:8]}... with user_id {user_id}")
        
        autonomous_agent = get_user_autonomous_agent(user_id)
        print(f"📊 Got agent, checking {len(autonomous_agent.autonomous_sessions)} sessions")
        
        session_data = None
        found_user = user_id
        
        # Check if the session exists in this agent instance
        if session_id in autonomous_agent.autonomous_sessions:
            print(f"✅ Found session in current agent")
            session_data = autonomous_agent.autonomous_sessions[session_id]
        else:
            print(f"🔍 Session not found in current agent, searching other agents...")
            # Check if session might exist in other user agents or globally
            total_sessions = 0
            for uid, agents in user_agents.items():
                try:
                    if "autonomous" in agents and hasattr(agents["autonomous"], "autonomous_sessions"):
                        agent_sessions = agents["autonomous"].autonomous_sessions
                        total_sessions += len(agent_sessions)
                        
                        if session_id in agent_sessions:
                            print(f"✅ Found session in user {uid}")
                            session_data = agent_sessions[session_id]
                            found_user = uid
                            break
                except Exception as agent_error:
                    print(f"⚠️ Error checking agent for user {uid}: {agent_error}")
                    continue
        
        if session_data:
            # Extract performance data to top level for client compatibility
            performance_data = session_data.get("performance", {})
            
            # Generate comprehensive PDF report
            pdf_report_path = None
            try:
                from utils.autonomous_report_generator import generate_autonomous_session_report
                
                # Prepare comprehensive data structure for PDF generation
                comprehensive_session_data = {
                    'session_data': session_data,
                    'performance': performance_data
                }
                
                pdf_report_path = generate_autonomous_session_report(comprehensive_session_data)
                print(f"✅ PDF report generated: {pdf_report_path}")
                
            except ImportError as import_error:
                print(f"⚠️ PDF generator not available: {import_error}")
            except Exception as pdf_error:
                print(f"❌ PDF generation failed: {pdf_error}")
                # Continue without PDF - don't fail the entire request
            
            response_data = {
                "session_found": True,
                "session_data": session_data,
                "performance": performance_data,  # Top-level performance for client
                "found_in_user": found_user,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add PDF information if generated successfully
            if pdf_report_path:
                response_data["pdf_report_path"] = pdf_report_path
                response_data["pdf_report_filename"] = os.path.basename(pdf_report_path)
                response_data["pdf_report_url"] = f"/api/download-report/{os.path.basename(pdf_report_path)}"
                response_data["pdf_generated"] = True
                print(f"📄 PDF report available at: {pdf_report_path}")
            else:
                response_data["pdf_generated"] = False
                response_data["pdf_error"] = "PDF generation failed or unavailable"
            
            return response_data
        else:
            total_sessions = sum(
                len(agents.get("autonomous", {}).get("autonomous_sessions", {})) 
                for agents in user_agents.values() 
                if isinstance(agents, dict) and "autonomous" in agents
            )
            
            print(f"❌ Session not found anywhere. Total sessions: {total_sessions}")
            
            # Session truly not found
            return {
                "session_found": False,
                "message": f"Session {session_id} not found in any active agents",
                "total_active_sessions": total_sessions,
                "searched_users": list(user_agents.keys()),
                "timestamp": datetime.now().isoformat(),
                "pdf_generated": False
            }
            
    except Exception as e:
        print(f"❌ Error in status endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting session status: {str(e)}")

@app.get("/api/download-report/{filename}")
async def download_report(filename: str):
    """Download generated PDF report from /tmp directory"""
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        file_path = f"/tmp/{filename}"
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        # Serve the file for download
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading report: {str(e)}")

@app.get("/api/autonomous/sessions")
async def list_autonomous_sessions(user_id: str = "default"):
    """List all autonomous trading sessions"""
    try:
        autonomous_agent = get_user_autonomous_agent(user_id)
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
async def stop_autonomous_session(session_id: str, user_id: str = "default"):
    """Stop a specific autonomous trading session"""
    try:
        autonomous_agent = get_user_autonomous_agent(user_id)
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

@app.get("/api/price/{token}")
async def get_token_price_endpoint(token: str):
    """Get current price for a specific token"""
    try:
        price_data = get_token_price_json(token.upper())
        
        if isinstance(price_data, dict) and "error" in price_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch price for {token}: {price_data.get('error')}"
            )
        
        # Return the price data directly (not wrapped)
        return price_data
        
    except Exception as e:
        print(f"❌ Error fetching price for {token}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch price for {token}: {str(e)}"
        )

@app.get("/api/balance/{token}")
async def get_token_balance_endpoint(token: str):
    """Get current balance for a specific token"""
    try:
        from api.token_balance import get_token_balance
        
        balance_data = get_token_balance(token.upper())
        
        if isinstance(balance_data, dict) and "error" in balance_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch balance for {token}: {balance_data.get('error')}"
            )
        
        # Return the balance data directly (not wrapped)
        return balance_data
        
    except Exception as e:
        print(f"❌ Error fetching balance for {token}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch balance for {token}: {str(e)}"
        )

@app.get("/api/news")
async def get_crypto_news(limit: int = 10, news_type: str = "trending"):
    """Get cryptocurrency news from CoinPanic API"""
    try:
        from agent.coinpanic_api import get_trending_news, get_bullish_news, get_bearish_news, get_crypto_news
        
        print(f"📰 Fetching {news_type} crypto news (limit: {limit})...")
        
        # Route to appropriate news function based on type
        if news_type == "trending":
            news_data = get_trending_news(limit=limit)
        elif news_type == "bullish":
            news_data = get_bullish_news(limit=limit)
        elif news_type == "bearish":
            news_data = get_bearish_news(limit=limit)
        else:
            news_data = get_crypto_news(limit=limit)
        
        if isinstance(news_data, dict) and "error" in news_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch news: {news_data.get('error')}"
            )
        
        return {
            "news": news_data.get("news", []),
            "count": news_data.get("count", 0),
            "type": news_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error fetching crypto news: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch crypto news: {str(e)}"
        )

@app.get("/api/news/{currency}")
async def get_currency_news_endpoint(currency: str, limit: int = 5):
    """Get news for a specific cryptocurrency"""
    try:
        from agent.coinpanic_api import get_currency_news
        
        print(f"📰 Fetching news for {currency.upper()} (limit: {limit})...")
        
        news_data = get_currency_news(currency.upper(), limit=limit)
        
        if isinstance(news_data, dict) and "error" in news_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch news for {currency}: {news_data.get('error')}"
            )
        
        return {
            "news": news_data.get("news", []),
            "count": news_data.get("count", 0),
            "currency": currency.upper(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error fetching news for {currency}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch news for {currency}: {str(e)}"
        )

@app.get("/api/market/sentiment")
async def get_market_sentiment():
    """Get overall market sentiment from news"""
    try:
        from agent.coinpanic_api import get_bullish_news, get_bearish_news
        
        print("📊 Analyzing market sentiment...")
        
        # Get both bullish and bearish news
        bullish_data = get_bullish_news(limit=5)
        bearish_data = get_bearish_news(limit=5)
        
        bullish_count = bullish_data.get("count", 0) if "error" not in bullish_data else 0
        bearish_count = bearish_data.get("count", 0) if "error" not in bearish_data else 0
        
        total_sentiment_news = bullish_count + bearish_count
        
        if total_sentiment_news > 0:
            bullish_percentage = (bullish_count / total_sentiment_news) * 100
            bearish_percentage = (bearish_count / total_sentiment_news) * 100
            
            if bullish_percentage > 60:
                sentiment = "bullish"
            elif bearish_percentage > 60:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
        else:
            sentiment = "neutral"
            bullish_percentage = 50
            bearish_percentage = 50
        
        return {
            "sentiment": sentiment,
            "bullish_percentage": round(bullish_percentage, 1),
            "bearish_percentage": round(bearish_percentage, 1),
            "bullish_news_count": bullish_count,
            "bearish_news_count": bearish_count,
            "total_news_analyzed": total_sentiment_news,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error analyzing market sentiment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze market sentiment: {str(e)}"
        )

# Trade execution endpoint
class TradeRequest(BaseModel):
    fromToken: str
    toToken: str
    amount: float
    timestamp: Optional[str] = None

@app.post("/api/trade")
async def execute_trade(request: TradeRequest):
    """Execute a trade between two tokens"""
    try:
        print(f"🔄 Trade request: {request.amount} {request.fromToken} → {request.toToken}")
        
        # Import the execute trade functionality
        from api.execute import trade_exec, token_addresses
        from api.token_balance import get_token_balance
        
        # Validate tokens
        from_token = request.fromToken.upper()
        to_token = request.toToken.upper()
        
        if from_token not in token_addresses or to_token not in token_addresses:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported token(s). Supported: {list(token_addresses.keys())}"
            )
        
        # Check balance
        balance_info = get_token_balance(from_token)
        balance = balance_info.get("amount", 0)
        
        if balance < request.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: {balance}, Required: {request.amount}"
            )
        
        # Get token addresses
        from_address = token_addresses[from_token]
        to_address = token_addresses[to_token]
        
        # Execute the trade
        trade_result = trade_exec(from_address, to_address, request.amount)
        
        if trade_result is None:
            raise HTTPException(
                status_code=500,
                detail="Trade execution failed"
            )
        
        return {
            "success": True,
            "trade_result": trade_result,
            "fromToken": request.fromToken,
            "toToken": request.toToken,
            "amount": request.amount,
            "timestamp": datetime.now().isoformat(),
            "message": f"Successfully traded {request.amount} {request.fromToken} for {request.toToken}"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Trade execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute trade: {str(e)}"
        )

# Additional news endpoints that frontend might be calling
@app.get("/api/market/news")
async def get_market_news(limit: int = 10):
    """Alternative endpoint for market news"""
    return await get_crypto_news(limit=limit, news_type="trending")

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
