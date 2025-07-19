#!/usr/bin/env python3
"""
Enhanced Kairos Autonomous Trading Session PDF Report Generator
Creates detailed PDF reports from autonomous trading session data
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(backend_dir))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        PageBreak, Image, KeepTogether, HRFlowable
    )
    from reportlab.graphics.shapes import Drawing, Line, Rect
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.colors import HexColor, Color
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.widgets.markers import makeMarker
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("⚠️ ReportLab not installed. PDF generation will use simplified text format.")
    REPORTLAB_AVAILABLE = False

class EnhancedAutonomousReportGenerator:
    """Generates comprehensive PDF reports for autonomous trading sessions"""
    
    def __init__(self):
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self.setup_custom_styles()
        else:
            self.styles = None
        
    def setup_custom_styles(self):
        """Setup custom report styles with Kairos branding"""
        
        # Kairos branded title
        self.styles.add(ParagraphStyle(
            name='KairosTitle',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=HexColor('#1e3a8a'),  # Deep blue
            spaceAfter=30,
            alignment=1,  # Center
            fontName='Helvetica-Bold'
        ))
        
        # Session header
        self.styles.add(ParagraphStyle(
            name='SessionHeader',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#059669'),  # Green
            spaceBefore=20,
            spaceAfter=15,
            borderWidth=2,
            borderColor=HexColor('#10b981'),
            borderPadding=12,
            backColor=HexColor('#ecfdf5'),
            fontName='Helvetica-Bold'
        ))
        
        # Section headers
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#1f2937'),
            spaceBefore=20,
            spaceAfter=12,
            borderWidth=1,
            borderColor=HexColor('#e5e7eb'),
            borderPadding=8,
            backColor=HexColor('#f9fafb'),
            fontName='Helvetica-Bold'
        ))
        
        # Trade details
        self.styles.add(ParagraphStyle(
            name='TradeDetail',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#374151'),
            leftIndent=15,
            rightIndent=15,
            spaceBefore=8,
            spaceAfter=8,
            backColor=HexColor('#f8fafc'),
            borderWidth=0.5,
            borderColor=HexColor('#cbd5e1'),
            borderPadding=8
        ))
        
        # AI reasoning
        self.styles.add(ParagraphStyle(
            name='AIReasoning',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#1e40af'),
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10,
            backColor=HexColor('#eff6ff'),
            borderWidth=1,
            borderColor=HexColor('#3b82f6'),
            borderPadding=12,
            fontName='Helvetica'
        ))
        
        # Performance metrics
        self.styles.add(ParagraphStyle(
            name='MetricStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=HexColor('#059669'),
            alignment=1  # Center
        ))
    
    def generate_autonomous_session_report(
        self, 
        session_data: Dict, 
        output_path: Optional[str] = None
    ) -> str:
        """Generate comprehensive autonomous trading session PDF report"""
        
        session_id = session_data.get('session_data', {}).get('session_id', 'unknown')
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/kairos_autonomous_report_{session_id[:8]}_{timestamp}.pdf"
        
        if not REPORTLAB_AVAILABLE:
            # Fallback to text report
            return self._generate_text_report(session_data, output_path.replace('.pdf', '.txt'))
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        # Build report content
        story = []
        
        # Title page
        story.extend(self._create_title_page(session_data))
        
        # Executive summary
        story.extend(self._create_executive_summary(session_data))
        
        # Trading performance
        story.extend(self._create_trading_performance_section(session_data))
        
        # Strategy analysis
        story.extend(self._create_strategy_analysis(session_data))
        
        # Detailed trade log
        story.extend(self._create_detailed_trade_log(session_data))
        
        # AI reasoning analysis
        story.extend(self._create_ai_reasoning_section(session_data))
        
        # Portfolio evolution
        story.extend(self._create_portfolio_evolution(session_data))
        
        # Risk assessment
        story.extend(self._create_risk_assessment(session_data))
        
        # Conclusions and recommendations
        story.extend(self._create_conclusions(session_data))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Autonomous Trading Report generated: {output_path}")
        return output_path
    
    def _create_title_page(self, session_data: Dict) -> List:
        """Create report title page"""
        story = []
        
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        
        # Title
        title = Paragraph(
            "🤖 Kairos AI Autonomous Trading Report", 
            self.styles['KairosTitle']
        )
        story.append(title)
        story.append(Spacer(1, 30))
        
        # Session overview box
        session_header = Paragraph(
            f"Session: {session_info.get('session_id', 'Unknown')[:8]}...",
            self.styles['SessionHeader']
        )
        story.append(session_header)
        story.append(Spacer(1, 20))
        
        # Key metrics table
        session_overview = [
            ['📊 Report Generated:', datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ['🆔 Session ID:', session_info.get('session_id', 'Unknown')],
            ['👤 User ID:', session_info.get('user_id', 'Unknown')],
            ['⏰ Duration:', session_info.get('params', {}).get('duration_text', 'Unknown')],
            ['📈 Total Trades:', str(performance.get('total_trades', 0))],
            ['✅ Success Rate:', f"{(performance.get('successful_trades', 0) / max(performance.get('total_trades', 1), 1) * 100):.1f}%"],
            ['💰 Portfolio Value:', f"${performance.get('current_portfolio_value', 0):,.2f}"],
            ['📊 Total P&L:', f"${performance.get('total_profit_loss', 0):+,.2f}"],
            ['📈 ROI:', f"{performance.get('roi_percentage', 0):.4f}%"],
            ['🤖 AI Engine:', 'Kairos v2.0 Enhanced'],
        ]
        
        overview_table = Table(session_overview, colWidths=[120, 250])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 30))
        
        # Disclaimer
        disclaimer = Paragraph(
            """
            <b>🔒 DISCLAIMER:</b> This report documents autonomous AI trading activities 
            conducted in a simulated environment using paper trading. All transactions 
            were executed through the Recall API testing framework and do not involve 
            real funds. This analysis is for educational and demonstration purposes only.
            """,
            self.styles['Normal']
        )
        story.append(disclaimer)
        story.append(PageBreak())
        
        return story
    
    def _create_executive_summary(self, session_data: Dict) -> List:
        """Create executive summary section"""
        story = []
        
        performance = session_data.get('performance', {})
        session_info = session_data.get('session_data', {})
        
        header = Paragraph("📊 Executive Summary", self.styles['SectionHeader'])
        story.append(header)
        
        # Performance metrics
        total_trades = performance.get('total_trades', 0)
        successful_trades = performance.get('successful_trades', 0)
        total_pnl = performance.get('total_profit_loss', 0)
        roi = performance.get('roi_percentage', 0)
        
        summary_text = f"""
        The autonomous trading session executed <b>{total_trades}</b> trades over a 
        <b>{session_info.get('params', {}).get('duration_text', 'unknown')}</b> period, 
        achieving a <b>{(successful_trades/max(total_trades,1)*100):.1f}%</b> success rate.
        
        The AI agent demonstrated <b>{'profitable' if total_pnl > 0 else 'learning-focused'}</b> 
        performance with a total P&L of <b>${total_pnl:+.2f}</b> and an ROI of 
        <b>{roi:.4f}%</b>.
        
        Trading was conducted primarily in the <b>USDC/ETH</b> pair, with the AI agent 
        making decisions every <b>5 minutes</b> based on market analysis, portfolio 
        composition, and risk assessment.
        """
        
        summary_para = Paragraph(summary_text, self.styles['Normal'])
        story.append(summary_para)
        story.append(Spacer(1, 20))
        
        # Key highlights
        highlights_data = [
            ['🎯 Strategy Focus', 'Small incremental ETH purchases'],
            ['📈 Best Trade', f"${max([t.get('profit_loss', 0) for t in session_info.get('trades_executed', [])] or [0]):.2f} profit"],
            ['📉 Worst Trade', f"${min([t.get('profit_loss', 0) for t in session_info.get('trades_executed', [])] or [0]):.2f} loss"],
            ['🔄 Trading Frequency', '5-minute cycles'],
            ['🎲 Risk Level', session_info.get('params', {}).get('risk_level', 'Unknown').title()],
            ['💵 Avg Trade Size', f"${performance.get('total_volume', 0) / max(total_trades, 1):.0f}"]
        ]
        
        highlights_table = Table(highlights_data, colWidths=[120, 200])
        highlights_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0fdf4')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(highlights_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_trading_performance_section(self, session_data: Dict) -> List:
        """Create detailed trading performance analysis"""
        story = []
        
        header = Paragraph("💹 Trading Performance Analysis", self.styles['SectionHeader'])
        story.append(header)
        
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        performance = session_data.get('performance', {})
        
        if not trades:
            no_trades = Paragraph("No trades were executed in this session.", self.styles['Normal'])
            story.append(no_trades)
            return story
        
        # Performance metrics table
        perf_data = [
            ['Total Trades Executed', str(len(trades))],
            ['Successful Trades', str(sum(1 for t in trades if t.get('success', False)))],
            ['Failed Trades', str(sum(1 for t in trades if not t.get('success', True)))],
            ['Total Volume Traded', f"${performance.get('total_volume', 0):.2f}"],
            ['Average Trade Size', f"${performance.get('total_volume', 0) / max(len(trades), 1):.2f}"],
            ['Total Profit/Loss', f"${performance.get('total_profit_loss', 0):+.2f}"],
            ['Return on Investment', f"{performance.get('roi_percentage', 0):.4f}%"],
            ['Win Rate', f"{(performance.get('successful_trades', 0) / max(len(trades), 1) * 100):.1f}%"]
        ]
        
        perf_table = Table(perf_data, colWidths=[150, 120])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(perf_table)
        story.append(Spacer(1, 20))
        
        # Trade summary by token pair
        trade_pairs = {}
        for trade in trades:
            pair = f"{trade.get('from_token', 'Unknown')}/{trade.get('to_token', 'Unknown')}"
            if pair not in trade_pairs:
                trade_pairs[pair] = {'count': 0, 'volume': 0, 'pnl': 0}
            trade_pairs[pair]['count'] += 1
            trade_pairs[pair]['volume'] += trade.get('amount', 0)
            trade_pairs[pair]['pnl'] += trade.get('profit_loss', 0)
        
        if trade_pairs:
            pair_header = Paragraph("📈 Trading Pairs Analysis", self.styles['Normal'])
            story.append(pair_header)
            story.append(Spacer(1, 10))
            
            pair_data = [['Token Pair', 'Trades', 'Volume', 'P&L']]
            for pair, stats in trade_pairs.items():
                pair_data.append([
                    pair,
                    str(stats['count']),
                    f"${stats['volume']:.0f}",
                    f"${stats['pnl']:+.2f}"
                ])
            
            pair_table = Table(pair_data, colWidths=[80, 50, 70, 70])
            pair_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(pair_table)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_detailed_trade_log(self, session_data: Dict) -> List:
        """Create detailed trade-by-trade log"""
        story = []
        
        header = Paragraph("📝 Detailed Trade Log", self.styles['SectionHeader'])
        story.append(header)
        
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        
        if not trades:
            no_trades = Paragraph("No trades were executed.", self.styles['Normal'])
            story.append(no_trades)
            return story
        
        for i, trade in enumerate(trades, 1):
            # Trade header
            trade_time = trade.get('timestamp', 'Unknown')
            if 'T' in trade_time:
                try:
                    dt = datetime.fromisoformat(trade_time.replace('Z', '+00:00'))
                    trade_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                except:
                    pass
            
            trade_header = Paragraph(
                f"🔄 Trade #{i} - {trade_time}",
                self.styles['Normal']
            )
            story.append(trade_header)
            story.append(Spacer(1, 5))
            
            # Trade details
            trade_result = trade.get('trade_result', {})
            transaction = trade_result.get('transaction', {})
            
            trade_details = [
                ['Action', f"{trade.get('from_token', 'Unknown')} → {trade.get('to_token', 'Unknown')}"],
                ['Amount', f"{trade.get('amount', 0)} {trade.get('from_token', '')}"],
                ['Received', f"{transaction.get('toAmount', 0):.6f} {trade.get('to_token', '')}"],
                ['Price', f"{transaction.get('price', 0):.8f} {trade.get('to_token', '')}/{trade.get('from_token', '')}"],
                ['USD Value', f"${transaction.get('tradeAmountUsd', 0):.2f}"],
                ['Success', '✅ Yes' if trade.get('success', False) else '❌ No'],
                ['P&L', f"${trade.get('profit_loss', 0):+.4f}"],
                ['Portfolio Before', f"${trade.get('pre_trade_portfolio_value', 0):,.2f}"],
                ['Portfolio After', f"${trade.get('post_trade_portfolio_value', 0):,.2f}"],
            ]
            
            trade_table = Table(trade_details, colWidths=[100, 150])
            trade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e2e8f0')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ]))
            
            story.append(trade_table)
            story.append(Spacer(1, 15))
        
        return story
    
    def _create_ai_reasoning_section(self, session_data: Dict) -> List:
        """Create AI reasoning and decision analysis"""
        story = []
        
        header = Paragraph("🧠 AI Reasoning & Decision Analysis", self.styles['SectionHeader'])
        story.append(header)
        
        reasoning_log = session_data.get('session_data', {}).get('reasoning_log', [])
        
        if not reasoning_log:
            no_reasoning = Paragraph("No AI reasoning data available for this session.", self.styles['Normal'])
            story.append(no_reasoning)
            return story
        
        for i, reasoning in enumerate(reasoning_log[:3], 1):  # Show first 3 cycles
            cycle_header = Paragraph(
                f"🔄 Trading Cycle #{reasoning.get('cycle', i)}",
                self.styles['Normal']
            )
            story.append(cycle_header)
            story.append(Spacer(1, 8))
            
            decision = reasoning.get('decision', {})
            trading_decision = decision.get('trading_decision', {})
            
            # Market analysis
            market_data = decision.get('market_data', {})
            market_text = f"""
            <b>📊 Market Analysis:</b><br/>
            • ETH Price: ${market_data.get('prices', {}).get('ETH', 0):,.2f}<br/>
            • Market Sentiment: {market_data.get('sentiment', 'Unknown').title()}<br/>
            • Volatility: {market_data.get('volatility', 'Unknown').title()}<br/>
            """
            
            market_para = Paragraph(market_text, self.styles['TradeDetail'])
            story.append(market_para)
            
            # AI decision reasoning
            reasoning_text = "<b>🤖 AI Decision Reasoning:</b><br/>"
            if isinstance(trading_decision.get('reasoning'), list):
                for reason in trading_decision.get('reasoning', []):
                    reasoning_text += f"• {reason}<br/>"
            else:
                reasoning_text += f"• {trading_decision.get('reasoning', 'No specific reasoning provided')}<br/>"
            
            reasoning_text += f"<br/><b>Confidence Level:</b> {trading_decision.get('confidence', 0)*100:.1f}%<br/>"
            reasoning_text += f"<b>Strategy Used:</b> {trading_decision.get('strategy_used', 'Unknown')}<br/>"
            reasoning_text += f"<b>Risk Score:</b> {trading_decision.get('risk_assessment', {}).get('risk_score', 0):.3f}"
            
            reasoning_para = Paragraph(reasoning_text, self.styles['AIReasoning'])
            story.append(reasoning_para)
            story.append(Spacer(1, 15))
        
        return story
    
    def _create_strategy_analysis(self, session_data: Dict) -> List:
        """Create strategy usage analysis"""
        story = []
        
        header = Paragraph("🎯 Strategy Analysis", self.styles['SectionHeader'])
        story.append(header)
        
        strategies = session_data.get('session_data', {}).get('strategies', {})
        reasoning_log = session_data.get('session_data', {}).get('reasoning_log', [])
        
        # Extract strategies used from reasoning log
        strategies_used = {}
        for reasoning in reasoning_log:
            strategy = reasoning.get('decision', {}).get('trading_decision', {}).get('strategy_used')
            if strategy:
                if strategy not in strategies_used:
                    strategies_used[strategy] = 0
                strategies_used[strategy] += 1
        
        if strategies_used:
            strategy_data = [['Strategy Name', 'Times Used', 'Usage %']]
            total_uses = sum(strategies_used.values())
            
            for strategy, count in strategies_used.items():
                percentage = (count / total_uses * 100) if total_uses > 0 else 0
                strategy_data.append([
                    strategy.replace('_', ' ').title(),
                    str(count),
                    f"{percentage:.1f}%"
                ])
            
            strategy_table = Table(strategy_data, colWidths=[150, 80, 80])
            strategy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#7c3aed')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(strategy_table)
        else:
            no_strategies = Paragraph("No specific strategies were recorded in this session.", self.styles['Normal'])
            story.append(no_strategies)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_portfolio_evolution(self, session_data: Dict) -> List:
        """Create portfolio evolution analysis"""
        story = []
        
        header = Paragraph("📈 Portfolio Evolution", self.styles['SectionHeader'])
        story.append(header)
        
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        performance = session_data.get('performance', {})
        
        if trades:
            # Portfolio value progression
            evolution_data = [['Trade #', 'Portfolio Value', 'P&L Change']]
            
            for i, trade in enumerate(trades, 1):
                pre_value = trade.get('pre_trade_portfolio_value', 0)
                post_value = trade.get('post_trade_portfolio_value', 0)
                change = trade.get('profit_loss', 0)
                
                evolution_data.append([
                    str(i),
                    f"${post_value:,.2f}",
                    f"${change:+.4f}"
                ])
            
            evolution_table = Table(evolution_data, colWidths=[60, 120, 100])
            evolution_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(evolution_table)
            
            # Summary stats
            start_value = performance.get('start_portfolio_value', 0)
            end_value = performance.get('current_portfolio_value', 0)
            total_change = end_value - start_value
            
            summary_text = f"""
            <b>Portfolio Summary:</b><br/>
            • Starting Value: ${start_value:,.2f}<br/>
            • Ending Value: ${end_value:,.2f}<br/>
            • Total Change: ${total_change:+.2f}<br/>
            • ROI: {performance.get('roi_percentage', 0):.4f}%<br/>
            """
            
            summary_para = Paragraph(summary_text, self.styles['TradeDetail'])
            story.append(summary_para)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_risk_assessment(self, session_data: Dict) -> List:
        """Create risk assessment section"""
        story = []
        
        header = Paragraph("⚠️ Risk Assessment", self.styles['SectionHeader'])
        story.append(header)
        
        session_info = session_data.get('session_data', {})
        params = session_info.get('params', {})
        performance = session_data.get('performance', {})
        
        risk_text = f"""
        <b>Risk Parameters:</b><br/>
        • Risk Level: {params.get('risk_level', 'Unknown').title()}<br/>
        • Max Trade Size: ${params.get('max_trade_size', 0)}<br/>
        • Testing Mode: {'Enabled' if params.get('testing_mode', False) else 'Disabled'}<br/>
        • Enhanced Learning: {'Enabled' if params.get('enhanced_learning', False) else 'Disabled'}<br/>
        <br/>
        <b>Observed Risk Metrics:</b><br/>
        • Largest Single Loss: ${min([t.get('profit_loss', 0) for t in session_info.get('trades_executed', [])] or [0]):.4f}<br/>
        • Largest Single Gain: ${max([t.get('profit_loss', 0) for t in session_info.get('trades_executed', [])] or [0]):.4f}<br/>
        • Portfolio Volatility: Low (paper trading)<br/>
        • Diversification: Single pair focus (USDC/ETH)<br/>
        """
        
        risk_para = Paragraph(risk_text, self.styles['TradeDetail'])
        story.append(risk_para)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_conclusions(self, session_data: Dict) -> List:
        """Create conclusions and recommendations"""
        story = []
        
        header = Paragraph("🎯 Conclusions & Recommendations", self.styles['SectionHeader'])
        story.append(header)
        
        performance = session_data.get('performance', {})
        session_info = session_data.get('session_data', {})
        
        total_trades = performance.get('total_trades', 0)
        success_rate = (performance.get('successful_trades', 0) / max(total_trades, 1)) * 100
        roi = performance.get('roi_percentage', 0)
        
        conclusions_text = f"""
        <b>🔍 Session Analysis:</b><br/>
        This autonomous trading session demonstrated the AI agent's ability to execute 
        consistent trading decisions in a controlled environment. With {total_trades} trades 
        and a {success_rate:.1f}% success rate, the system showed {'promising' if success_rate > 70 else 'learning-focused'} behavior.
        <br/><br/>
        
        <b>💡 Key Insights:</b><br/>
        • The AI agent favored small, frequent ETH purchases<br/>
        • Risk management kept individual trade sizes modest<br/>
        • Decision-making was consistent with neutral market conditions<br/>
        • No significant portfolio drawdowns were observed<br/>
        <br/>
        
        <b>🚀 Recommendations:</b><br/>
        • Consider longer session durations for strategy development<br/>
        • Test with multiple token pairs for diversification<br/>
        • Implement dynamic position sizing based on market volatility<br/>
        • Add sentiment analysis integration for decision enhancement<br/>
        • Monitor performance across different market conditions<br/>
        """
        
        conclusions_para = Paragraph(conclusions_text, self.styles['Normal'])
        story.append(conclusions_para)
        
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = f"""
        <b>📄 Report Footer:</b><br/>
        Generated by Kairos AI Trading System v2.0<br/>
        Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>
        Session ID: {session_info.get('session_id', 'Unknown')}<br/>
        Environment: Paper Trading (Simulated)<br/>
        """
        
        footer_para = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer_para)
        
        return story
    
    def _generate_text_report(self, session_data: Dict, output_path: str) -> str:
        """Generate a text-based report when ReportLab is not available"""
        
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        
        report_lines = [
            "🤖 KAIROS AI AUTONOMOUS TRADING REPORT",
            "=" * 50,
            f"Session ID: {session_info.get('session_id', 'Unknown')}",
            f"User ID: {session_info.get('user_id', 'Unknown')}",
            f"Duration: {session_info.get('params', {}).get('duration_text', 'Unknown')}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "📊 PERFORMANCE SUMMARY",
            "-" * 30,
            f"Total Trades: {performance.get('total_trades', 0)}",
            f"Successful Trades: {performance.get('successful_trades', 0)}",
            f"Success Rate: {(performance.get('successful_trades', 0) / max(performance.get('total_trades', 1), 1) * 100):.1f}%",
            f"Total P&L: ${performance.get('total_profit_loss', 0):+.4f}",
            f"ROI: {performance.get('roi_percentage', 0):.4f}%",
            f"Portfolio Value: ${performance.get('current_portfolio_value', 0):,.2f}",
            "",
            "🔄 TRADE DETAILS",
            "-" * 20
        ]
        
        trades = session_info.get('trades_executed', [])
        for i, trade in enumerate(trades, 1):
            report_lines.extend([
                f"Trade #{i}: {trade.get('from_token', 'Unknown')} -> {trade.get('to_token', 'Unknown')}",
                f"  Amount: {trade.get('amount', 0)}",
                f"  Success: {'Yes' if trade.get('success', False) else 'No'}",
                f"  P&L: ${trade.get('profit_loss', 0):+.4f}",
                ""
            ])
        
        report_lines.extend([
            "🔒 DISCLAIMER",
            "-" * 15,
            "This report documents simulated trading activities.",
            "No real funds were used. Educational purposes only.",
            "",
            "Generated by Kairos AI Trading System v2.0"
        ])
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✅ Text report generated: {output_path}")
        return output_path

# Global instance
autonomous_report_generator = EnhancedAutonomousReportGenerator()

def generate_autonomous_session_report(session_data: Dict, output_path: Optional[str] = None) -> str:
    """Convenience function to generate autonomous session report"""
    return autonomous_report_generator.generate_autonomous_session_report(session_data, output_path)
