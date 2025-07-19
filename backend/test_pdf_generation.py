#!/usr/bin/env python3
"""
Test PDF Report Generation for Autonomous Trading Sessions
"""

import sys
import os
import json
from datetime import datetime, timezone

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from utils.autonomous_report_generator import generate_autonomous_session_report

def test_pdf_generation():
    """Test PDF generation with sample autonomous session data"""
    
    # Sample autonomous trading session data (like what you provided)
    sample_session_data = {
        "session_data": {
            "session_id": "sess_5c823f8e-7f90-4a43-9d8b-3e1f2a9b7c4d",
            "user_id": "test_user_001",
            "status": "active",
            "params": {
                "duration_text": "30 minutes",
                "max_trade_size": 50,
                "risk_level": "moderate",
                "testing_mode": True,
                "enhanced_learning": True,
                "start_time": "2024-01-15T10:00:00Z"
            },
            "trades_executed": [
                {
                    "timestamp": "2024-01-15T10:05:00Z",
                    "from_token": "USDC",
                    "to_token": "ETH", 
                    "amount": 25.0,
                    "success": True,
                    "profit_loss": 0.0012,
                    "pre_trade_portfolio_value": 1000.00,
                    "post_trade_portfolio_value": 1000.0012,
                    "trade_result": {
                        "transaction": {
                            "toAmount": 0.011234,
                            "price": 0.0004496,
                            "tradeAmountUsd": 25.0
                        }
                    }
                },
                {
                    "timestamp": "2024-01-15T10:10:00Z", 
                    "from_token": "USDC",
                    "to_token": "ETH",
                    "amount": 30.0,
                    "success": True,
                    "profit_loss": -0.0008,
                    "pre_trade_portfolio_value": 1000.0012,
                    "post_trade_portfolio_value": 1000.0004,
                    "trade_result": {
                        "transaction": {
                            "toAmount": 0.013456,
                            "price": 0.0004485,
                            "tradeAmountUsd": 30.0
                        }
                    }
                },
                {
                    "timestamp": "2024-01-15T10:15:00Z",
                    "from_token": "USDC", 
                    "to_token": "ETH",
                    "amount": 20.0,
                    "success": False,
                    "profit_loss": -0.0015,
                    "pre_trade_portfolio_value": 1000.0004,
                    "post_trade_portfolio_value": 999.9989,
                    "trade_result": {
                        "error": "Insufficient liquidity"
                    }
                }
            ],
            "reasoning_log": [
                {
                    "cycle": 1,
                    "decision": {
                        "market_data": {
                            "prices": {"ETH": 2234.56, "USDC": 1.00},
                            "sentiment": "neutral",
                            "volatility": "low"
                        },
                        "trading_decision": {
                            "reasoning": [
                                "ETH price shows stability at current levels",
                                "Portfolio allocation favors small ETH accumulation", 
                                "Risk assessment indicates favorable entry point"
                            ],
                            "confidence": 0.73,
                            "strategy_used": "incremental_purchase",
                            "risk_assessment": {
                                "risk_score": 0.234
                            }
                        }
                    }
                },
                {
                    "cycle": 2,
                    "decision": {
                        "market_data": {
                            "prices": {"ETH": 2231.12, "USDC": 1.00},
                            "sentiment": "neutral",
                            "volatility": "low"  
                        },
                        "trading_decision": {
                            "reasoning": [
                                "Slight price decrease presents opportunity",
                                "Maintaining consistent accumulation strategy",
                                "Risk remains within acceptable parameters"
                            ],
                            "confidence": 0.68,
                            "strategy_used": "incremental_purchase", 
                            "risk_assessment": {
                                "risk_score": 0.189
                            }
                        }
                    }
                }
            ],
            "strategies": {
                "incremental_purchase": {"usage_count": 2, "success_rate": 0.667}
            }
        },
        "performance": {
            "total_trades": 3,
            "successful_trades": 2,
            "total_volume": 75.0,
            "total_profit_loss": -0.0011,
            "current_portfolio_value": 999.9989,
            "start_portfolio_value": 1000.0,
            "roi_percentage": -0.0011
        }
    }
    
    print("🧪 Testing Autonomous Trading PDF Report Generation...")
    print(f"📊 Sample session: {sample_session_data['session_data']['session_id'][:8]}...")
    print(f"🔄 Trades: {sample_session_data['performance']['total_trades']}")
    print(f"💰 P&L: ${sample_session_data['performance']['total_profit_loss']:+.4f}")
    
    try:
        # Generate PDF report
        pdf_path = generate_autonomous_session_report(sample_session_data)
        
        print(f"✅ PDF Report Generated Successfully!")
        print(f"📄 File Location: {pdf_path}")
        
        # Check file exists and size
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"📊 File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Show some details about the content
            print(f"🎯 Report Details:")
            print(f"   • Session ID: {sample_session_data['session_data']['session_id']}")
            print(f"   • Total Trades: {sample_session_data['performance']['total_trades']}")
            print(f"   • Success Rate: {(sample_session_data['performance']['successful_trades']/sample_session_data['performance']['total_trades']*100):.1f}%")
            print(f"   • Final P&L: ${sample_session_data['performance']['total_profit_loss']:+.4f}")
            print(f"   • ROI: {sample_session_data['performance']['roi_percentage']:.4f}%")
            
            return pdf_path
        else:
            print("❌ PDF file was not created")
            return None
            
    except ImportError as e:
        print(f"⚠️ Import Error: {e}")
        print("💡 Installing required packages: pip install reportlab matplotlib")
        return None
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_text_report_fallback():
    """Test text report generation as fallback"""
    
    # Simple session data for text report
    sample_data = {
        "session_data": {
            "session_id": "sess_text_test",
            "user_id": "test_user",
            "params": {"duration_text": "Test Duration"},
            "trades_executed": [
                {
                    "from_token": "USDC", "to_token": "ETH",
                    "amount": 25, "success": True, "profit_loss": 0.001
                }
            ]
        },
        "performance": {
            "total_trades": 1, "successful_trades": 1,
            "total_profit_loss": 0.001, "roi_percentage": 0.1,
            "current_portfolio_value": 1000.001
        }
    }
    
    try:
        # Force text report by using different file extension
        from utils.autonomous_report_generator import autonomous_report_generator
        text_path = autonomous_report_generator._generate_text_report(
            sample_data, "/tmp/test_autonomous_report.txt"
        )
        
        print(f"✅ Text Report Generated: {text_path}")
        
        if os.path.exists(text_path):
            with open(text_path, 'r') as f:
                content = f.read()
            print(f"📄 Text Report Preview (first 500 chars):")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
        
        return text_path
        
    except Exception as e:
        print(f"❌ Error generating text report: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Kairos Autonomous Trading PDF Report Test")
    print("=" * 60)
    
    # Test PDF generation
    pdf_result = test_pdf_generation()
    
    print("\n" + "=" * 60)
    
    # Test text fallback
    print("📝 Testing text report fallback...")
    text_result = test_text_report_fallback()
    
    print("\n" + "=" * 60)
    print("🎉 Test Summary:")
    print(f"   PDF Report: {'✅ Success' if pdf_result else '❌ Failed'}")
    print(f"   Text Report: {'✅ Success' if text_result else '❌ Failed'}")
    
    if pdf_result or text_result:
        print("🚀 Report generation system is working!")
        print("💡 The status endpoint will now automatically generate reports")
    else:
        print("⚠️ Both report types failed - check dependencies")
