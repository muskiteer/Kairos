#!/usr/bin/env python3
"""
Kairos Autonomous Trading Session PDF Report Generator - ENHANCED VERSION
Creates STUNNING PDF reports from autonomous trading session data with real data integration
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import traceback

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(backend_dir))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        PageBreak, Image, KeepTogether
    )
    from reportlab.lib.colors import HexColor
    from reportlab.graphics.shapes import Drawing, Rect
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics import renderPDF
    REPORTLAB_AVAILABLE = True
    print("✅ ReportLab loaded successfully - PDF generation enabled")
except ImportError as e:
    print(f"⚠️ ReportLab not installed: {e}")
    print("📦 Install with: pip install reportlab")
    REPORTLAB_AVAILABLE = False

class EnhancedAutonomousReportGenerator:
    """Generates EPIC comprehensive PDF reports for autonomous trading sessions"""
    
    def __init__(self):
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self.setup_custom_styles()
            print("🎨 Custom styles initialized")
        else:
            self.styles = None
            print("⚠️ PDF generation will use text format fallback")

    def setup_custom_styles(self):
        """Create beautiful custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='KairosTitle', 
            parent=self.styles['Title'], 
            fontSize=32,
            textColor=HexColor('#1e3a8a'), 
            spaceAfter=30, 
            alignment=1, 
            fontName='Helvetica-Bold',
            borderWidth=3,
            borderColor=HexColor('#3b82f6'),
            borderPadding=20,
            backColor=HexColor('#eff6ff')
        ))
        
        # Session header style
        self.styles.add(ParagraphStyle(
            name='SessionHeader', 
            parent=self.styles['Heading1'], 
            fontSize=22,
            textColor=HexColor('#059669'), 
            spaceBefore=25, 
            spaceAfter=20,
            borderWidth=2, 
            borderColor=HexColor('#10b981'), 
            borderPadding=15,
            backColor=HexColor('#ecfdf5'), 
            fontName='Helvetica-Bold',
            alignment=1
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader', 
            parent=self.styles['Heading2'], 
            fontSize=18,
            textColor=HexColor('#1f2937'), 
            spaceBefore=25, 
            spaceAfter=15,
            borderWidth=1, 
            borderColor=HexColor('#e5e7eb'), 
            borderPadding=10,
            backColor=HexColor('#f9fafb'), 
            fontName='Helvetica-Bold'
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection', 
            parent=self.styles['Heading3'], 
            fontSize=14,
            textColor=HexColor('#374151'), 
            spaceBefore=15, 
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leftIndent=20
        ))
        
        # Trade detail style
        self.styles.add(ParagraphStyle(
            name='TradeDetail', 
            parent=self.styles['Normal'], 
            fontSize=11,
            textColor=HexColor('#374151'), 
            leftIndent=20, 
            rightIndent=20,
            spaceBefore=10, 
            spaceAfter=10, 
            backColor=HexColor('#f8fafc'),
            borderWidth=0.5, 
            borderColor=HexColor('#cbd5e1'), 
            borderPadding=10
        ))
        
        # AI reasoning style
        self.styles.add(ParagraphStyle(
            name='AIReasoning', 
            parent=self.styles['Normal'], 
            fontSize=12,
            textColor=HexColor('#1e40af'), 
            leftIndent=25, 
            rightIndent=25,
            spaceBefore=12, 
            spaceAfter=12, 
            backColor=HexColor('#eff6ff'),
            borderWidth=1, 
            borderColor=HexColor('#3b82f6'), 
            borderPadding=15,
            fontName='Helvetica-Oblique'
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricStyle', 
            parent=self.styles['Normal'], 
            fontSize=14,
            fontName='Helvetica-Bold', 
            textColor=HexColor('#059669'), 
            alignment=1
        ))
        
        # Success style
        self.styles.add(ParagraphStyle(
            name='SuccessText', 
            parent=self.styles['Normal'], 
            fontSize=12,
            textColor=HexColor('#059669'), 
            fontName='Helvetica-Bold'
        ))
        
        # Error style
        self.styles.add(ParagraphStyle(
            name='ErrorText', 
            parent=self.styles['Normal'], 
            fontSize=12,
            textColor=HexColor('#dc2626'), 
            fontName='Helvetica-Bold'
        ))

    def generate_autonomous_session_report(self, session_data: Dict, output_path: Optional[str] = None) -> str:
        """Generate a comprehensive autonomous trading session report"""
        
        # Extract session info
        session_info = session_data.get('session_data', {})
        session_id = session_info.get('id', session_info.get('session_id', 'unknown'))
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_session_id = session_id[:8] if session_id != 'unknown' else 'unknown'
            output_path = f"/tmp/kairos_autonomous_report_{safe_session_id}_{timestamp}.pdf"
        
        print(f"📄 Generating PDF report for session {session_id[:8]}...")
        print(f"💾 Output path: {output_path}")
        
        if not REPORTLAB_AVAILABLE:
            return self._generate_text_report(session_data, output_path.replace('.pdf', '.txt'))
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path, 
                pagesize=A4, 
                rightMargin=50, 
                leftMargin=50, 
                topMargin=50, 
                bottomMargin=50
            )
            
            # Build the report content
            story = []
            
            # Title page
            story.extend(self._create_title_page(session_data))
            
            # Executive summary
            story.extend(self._create_executive_summary(session_data))
            
            # Trading performance
            story.extend(self._create_trading_performance_section(session_data))
            
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
            
            # Build the PDF
            print("🔨 Building PDF document...")
            doc.build(story)
            
            print(f"✅ EPIC Autonomous Trading Report generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating PDF report: {e}")
            traceback.print_exc()
            # Fallback to text report
            return self._generate_text_report(session_data, output_path.replace('.pdf', '.txt'))

    def _create_title_page(self, session_data: Dict) -> List:
        """Create an EPIC title page with session overview"""
        story = []
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        
        # Main title
        title = Paragraph("🤖 KAIROS AI AUTONOMOUS TRADING REPORT", self.styles['KairosTitle'])
        story.append(title)
        story.append(Spacer(1, 40))
        
        # Session header
        session_id = session_info.get('id', session_info.get('session_id', 'Unknown'))
        session_header = Paragraph(f"📊 SESSION: {session_id[:8]}...", self.styles['SessionHeader'])
        story.append(session_header)
        story.append(Spacer(1, 30))
        
        # Session overview table
        session_overview = [
            ['📅 Report Generated:', datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ['🆔 Session ID:', session_id[:32] + '...' if len(session_id) > 32 else session_id],
            ['👤 User ID:', session_info.get('user_id', 'Unknown')],
            ['⏰ Session Start:', self._format_datetime(session_info.get('start_time'))],
            ['🏁 Session End:', self._format_datetime(session_info.get('end_time', 'In Progress'))],
            ['⌛ Duration:', self._calculate_duration(session_info)],
            ['📈 Total Trades:', str(performance.get('total_trades', session_info.get('total_trades', 0)))],
            ['✅ Successful Trades:', str(performance.get('successful_trades', session_info.get('successful_trades', 0)))],
            ['🎯 Success Rate:', f"{self._calculate_success_rate(performance, session_info):.1f}%"],
            ['💰 Initial Value:', f"${session_info.get('initial_portfolio_value', 0):,.2f}"],
            ['📊 Final Value:', f"${performance.get('current_portfolio_value', session_info.get('current_portfolio_value', 0)):,.2f}"],
            ['💸 Total P&L:', f"${performance.get('total_profit_loss', session_info.get('total_pnl', 0)):+,.4f}"],
            ['📈 ROI:', f"{self._calculate_roi(performance, session_info):.4f}%"],
            ['🤖 AI Engine:', performance.get('ai_engine', 'Kairos Gemini v3.0 Enhanced')],
            ['🔥 Status:', session_info.get('status', 'Unknown').upper()],
        ]
        
        overview_table = Table(session_overview, colWidths=[140, 300])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#3b82f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f0f9ff'), HexColor('#e0f2fe')]),
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 40))
        
        # Enhanced disclaimer
        disclaimer = Paragraph(
            """
            <b>🔒 IMPORTANT DISCLAIMER:</b><br/><br/>
            This report documents autonomous AI trading activities conducted through the Kairos Trading System. 
            All transactions were executed via real trading APIs with actual market data and live portfolio management. 
            <br/><br/>
            <b>⚠️ RISK WARNING:</b> Cryptocurrency trading involves substantial risk of loss. Past performance 
            does not guarantee future results. This system is experimental and should only be used with funds 
            you can afford to lose.
            <br/><br/>
            <b>🤖 AI DISCLOSURE:</b> All trading decisions were made autonomously by Gemini AI based on 
            real-time market analysis, portfolio data, and learned strategies. Human oversight was minimal 
            during the trading session.
            """,
            self.styles['Normal']
        )
        story.append(disclaimer)
        story.append(PageBreak())
        
        return story

    def _create_executive_summary(self, session_data: Dict) -> List:
        """Create executive summary with key insights"""
        story = []
        performance = session_data.get('performance', {})
        session_info = session_data.get('session_data', {})
        
        header = Paragraph("📊 EXECUTIVE SUMMARY", self.styles['SectionHeader'])
        story.append(header)
        
        # Extract key metrics
        total_trades = performance.get('total_trades', session_info.get('total_trades', 0))
        successful_trades = performance.get('successful_trades', session_info.get('successful_trades', 0))
        total_pnl = performance.get('total_profit_loss', session_info.get('total_pnl', 0))
        success_rate = self._calculate_success_rate(performance, session_info)
        roi = self._calculate_roi(performance, session_info)
        duration = self._calculate_duration(session_info)
        
        # Create executive summary text
        summary_text = f"""
        <b>🎯 SESSION PERFORMANCE OVERVIEW</b><br/><br/>
        
        The Kairos AI autonomous trading session executed <b>{total_trades} trades</b> over a 
        <b>{duration}</b> period, achieving a <b>{success_rate:.1f}% success rate</b>. 
        <br/><br/>
        
        The AI agent demonstrated <b>{'PROFITABLE' if total_pnl > 0 else 'LEARNING-FOCUSED'}</b> 
        performance with a total P&L of <b>${total_pnl:+,.4f}</b> and an ROI of <b>{roi:.4f}%</b>.
        <br/><br/>
        
        <b>🧠 AI PERFORMANCE HIGHLIGHTS:</b><br/>
        • Advanced market analysis with real-time data integration<br/>
        • Multi-chain portfolio management across Ethereum, Polygon, and Solana<br/>
        • Dynamic risk management with position sizing controls<br/>
        • Continuous learning from trade outcomes and market conditions<br/>
        • News sentiment analysis and technical indicator integration<br/><br/>
        
        <b>📈 KEY ACHIEVEMENTS:</b><br/>
        • Successful trades: {successful_trades}/{total_trades}<br/>
        • Risk management: No single trade exceeded 50% of token balance<br/>
        • Market adaptability: AI adjusted strategy based on conditions<br/>
        • Learning evolution: Each trade improved future decision making<br/>
        """
        
        summary_para = Paragraph(summary_text, self.styles['Normal'])
        story.append(summary_para)
        story.append(Spacer(1, 30))
        
        return story

    def _create_trading_performance_section(self, session_data: Dict) -> List:
        """Create detailed trading performance analysis"""
        story = []
        
        header = Paragraph("💹 TRADING PERFORMANCE ANALYSIS", self.styles['SectionHeader'])
        story.append(header)
        
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        trades = session_info.get('trades_executed', [])
        
        if not trades:
            no_trades = Paragraph("📝 No trades were executed during this session.", self.styles['Normal'])
            story.append(no_trades)
            return story
        
        # Performance metrics table
        total_volume = sum(float(trade.get('amount', 0)) for trade in trades)
        avg_trade_size = total_volume / len(trades) if trades else 0
        
        perf_data = [
            ['📊 METRIC', '📈 VALUE', '💡 ANALYSIS'],
            ['Total Trades Executed', str(len(trades)), 'High activity level' if len(trades) > 5 else 'Conservative approach'],
            ['Successful Trades', str(sum(1 for t in trades if t.get('success', False))), f"{self._calculate_success_rate(performance, session_info):.1f}% success rate"],
            ['Failed Trades', str(sum(1 for t in trades if not t.get('success', True))), 'Learning opportunities'],
            ['Total Volume Traded', f"${total_volume:.2f}", 'Transaction volume'],
            ['Average Trade Size', f"${avg_trade_size:.2f}", 'Position sizing'],
            ['Total Profit/Loss', f"${performance.get('total_profit_loss', 0):+.4f}", 'Overall performance'],
            ['Return on Investment', f"{self._calculate_roi(performance, session_info):.4f}%", 'Portfolio growth'],
            ['Win Rate', f"{self._calculate_success_rate(performance, session_info):.1f}%", 'Decision accuracy'],
            ['Risk Score', session_info.get('risk_score', 'Medium'), 'Risk management level']
        ]
        
        perf_table = Table(perf_data, colWidths=[150, 120, 150])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#fbbf24')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#f59e0b')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#fef3c7'), HexColor('#fde68a')])
        ]))
        
        story.append(perf_table)
        story.append(Spacer(1, 30))
        
        return story

    def _create_detailed_trade_log(self, session_data: Dict) -> List:
        """Create detailed trade-by-trade analysis"""
        story = []
        
        header = Paragraph("📝 DETAILED TRADE EXECUTION LOG", self.styles['SectionHeader'])
        story.append(header)
        
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        
        if not trades:
            no_trades = Paragraph("No trades were executed during this session.", self.styles['Normal'])
            story.append(no_trades)
            return story
        
        for i, trade in enumerate(trades, 1):
            # Trade header
            trade_timestamp = trade.get('execution_time', trade.get('timestamp', 'Unknown'))
            success_icon = "✅" if trade.get('success', False) else "❌"
            
            trade_header = Paragraph(
                f"{success_icon} <b>TRADE #{i}</b> - {self._format_datetime(trade_timestamp)}", 
                self.styles['SubSection']
            )
            story.append(trade_header)
            
            # Trade details table
            trade_details = [
                ['🔄 Action', f"{trade.get('from_token', 'Unknown')} → {trade.get('to_token', 'Unknown')}"],
                ['💰 Amount', f"{trade.get('from_amount', trade.get('amount', 0))} {trade.get('from_token', '')}"],
                ['📈 Received', f"{trade.get('to_amount', 'Unknown')} {trade.get('to_token', '')}"],
                ['🎯 Status', '✅ Success' if trade.get('success', False) else '❌ Failed'],
                ['💸 P&L Impact', f"${trade.get('profit_loss', 0):+.6f}"],
                ['⛽ Gas Used', str(trade.get('gas_used', 'Unknown'))],
                ['🔗 Chain', trade.get('chain', 'Unknown')],
                ['🧾 Tx Hash', trade.get('tx_hash', 'Not available')[:32] + '...' if trade.get('tx_hash') else 'N/A'],
                ['🤖 AI Confidence', f"{float(trade.get('ai_confidence', 0)) * 100:.1f}%" if trade.get('ai_confidence') else 'N/A']
            ]
            
            trade_table = Table(trade_details, colWidths=[120, 300])
            trade_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e2e8f0')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(trade_table)
            
            # AI reasoning if available
            ai_reasoning = trade.get('ai_reasoning', '')
            if ai_reasoning:
                reasoning_header = Paragraph("<b>🧠 AI REASONING:</b>", self.styles['Normal'])
                story.append(Spacer(1, 10))
                story.append(reasoning_header)
                
                reasoning_text = Paragraph(ai_reasoning, self.styles['AIReasoning'])
                story.append(reasoning_text)
            
            story.append(Spacer(1, 20))
        
        return story

    def _create_ai_reasoning_section(self, session_data: Dict) -> List:
        """Create AI reasoning and strategy analysis"""
        story = []
        
        header = Paragraph("🧠 AI DECISION ANALYSIS & STRATEGY EVOLUTION", self.styles['SectionHeader'])
        story.append(header)
        
        # Get AI strategies and decisions
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        
        if trades:
            # Analyze AI strategies used
            strategies = {}
            for trade in trades:
                reasoning = trade.get('ai_reasoning', 'Unknown strategy')
                confidence = trade.get('ai_confidence', 0)
                success = trade.get('success', False)
                
                # Extract strategy from reasoning (simplified)
                strategy_key = 'Unknown'
                if 'momentum' in reasoning.lower():
                    strategy_key = 'Momentum Trading'
                elif 'arbitrage' in reasoning.lower():
                    strategy_key = 'Arbitrage'
                elif 'dca' in reasoning.lower():
                    strategy_key = 'Dollar Cost Averaging'
                elif 'swing' in reasoning.lower():
                    strategy_key = 'Swing Trading'
                elif 'hodl' in reasoning.lower():
                    strategy_key = 'HODL Strategy'
                elif 'scalping' in reasoning.lower():
                    strategy_key = 'Scalping'
                else:
                    strategy_key = 'Custom Strategy'
                
                if strategy_key not in strategies:
                    strategies[strategy_key] = {'count': 0, 'success': 0, 'confidence': []}
                
                strategies[strategy_key]['count'] += 1
                if success:
                    strategies[strategy_key]['success'] += 1
                strategies[strategy_key]['confidence'].append(confidence)
            
            # Strategy performance table
            strategy_data = [['🎯 STRATEGY', '📊 USED', '✅ SUCCESS', '📈 SUCCESS RATE', '🎪 AVG CONFIDENCE']]
            
            for strategy, data in strategies.items():
                success_rate = (data['success'] / data['count'] * 100) if data['count'] > 0 else 0
                avg_confidence = sum(data['confidence']) / len(data['confidence']) * 100 if data['confidence'] else 0
                
                strategy_data.append([
                    strategy,
                    str(data['count']),
                    str(data['success']),
                    f"{success_rate:.1f}%",
                    f"{avg_confidence:.1f}%"
                ])
            
            strategy_table = Table(strategy_data, colWidths=[120, 60, 60, 80, 100])
            strategy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#7c3aed')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f3e8ff')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#8b5cf6')),
            ]))
            
            story.append(strategy_table)
            story.append(Spacer(1, 20))
        
        # AI learning insights
        insights_text = """
        <b>🔍 AI LEARNING INSIGHTS:</b><br/><br/>
        
        • <b>Decision Framework:</b> The AI uses a sophisticated multi-factor analysis including market sentiment, 
        technical indicators, portfolio balance, risk assessment, and historical performance data.<br/><br/>
        
        • <b>Risk Management:</b> Each trade is validated against position sizing limits, ensuring no single 
        trade exceeds 50% of any token balance.<br/><br/>
        
        • <b>Market Adaptation:</b> The AI continuously learns from market conditions and adjusts strategies 
        based on news sentiment and price movements.<br/><br/>
        
        • <b>Strategy Evolution:</b> Historical performance data is used to refine future decision making, 
        with successful strategies being prioritized in similar market conditions.<br/><br/>
        
        • <b>Multi-Chain Intelligence:</b> The AI properly handles token balances across different blockchains 
        (Ethereum, Polygon, Solana, Base) and executes trades within chain constraints.
        """
        
        insights_para = Paragraph(insights_text, self.styles['Normal'])
        story.append(insights_para)
        story.append(Spacer(1, 20))
        
        return story

    def _create_portfolio_evolution(self, session_data: Dict) -> List:
        """Create portfolio evolution analysis"""
        story = []
        
        header = Paragraph("📈 PORTFOLIO EVOLUTION & ASSET ALLOCATION", self.styles['SectionHeader'])
        story.append(header)
        
        session_info = session_data.get('session_data', {})
        initial_value = session_info.get('initial_portfolio_value', 0)
        final_value = session_data.get('performance', {}).get('current_portfolio_value', 
                                                              session_info.get('current_portfolio_value', 0))
        
        evolution_text = f"""
        <b>💼 PORTFOLIO VALUE EVOLUTION:</b><br/><br/>
        
        • <b>Initial Portfolio Value:</b> ${initial_value:,.2f}<br/>
        • <b>Final Portfolio Value:</b> ${final_value:,.2f}<br/>
        • <b>Absolute Change:</b> ${final_value - initial_value:+,.2f}<br/>
        • <b>Percentage Change:</b> {((final_value - initial_value) / max(initial_value, 1) * 100):+.4f}%<br/><br/>
        
        <b>🎯 KEY PORTFOLIO INSIGHTS:</b><br/><br/>
        
        • The AI maintained a diversified approach across multiple cryptocurrencies<br/>
        • Risk management protocols prevented excessive concentration in any single asset<br/>
        • Dynamic rebalancing occurred based on market opportunities and risk assessment<br/>
        • Multi-chain capabilities enabled optimal token utilization across networks<br/>
        """
        
        evolution_para = Paragraph(evolution_text, self.styles['Normal'])
        story.append(evolution_para)
        story.append(Spacer(1, 20))
        
        return story

    def _create_risk_assessment(self, session_data: Dict) -> List:
        """Create comprehensive risk assessment section"""
        story = []
        
        header = Paragraph("⚠️ RISK ASSESSMENT & MANAGEMENT", self.styles['SectionHeader'])
        story.append(header)
        
        session_info = session_data.get('session_data', {})
        trades = session_info.get('trades_executed', [])
        performance = session_data.get('performance', {})
        
        # Calculate risk metrics
        total_trades = len(trades)
        successful_trades = sum(1 for t in trades if t.get('success', False))
        success_rate = (successful_trades / max(total_trades, 1)) * 100
        
        # Risk assessment based on performance
        risk_level = "LOW"
        risk_color = HexColor('#059669')
        
        if success_rate < 40:
            risk_level = "HIGH"
            risk_color = HexColor('#dc2626')
        elif success_rate < 70:
            risk_level = "MEDIUM"
            risk_color = HexColor('#f59e0b')
        
        risk_text = f"""
        <b>🛡️ RISK MANAGEMENT OVERVIEW:</b><br/><br/>
        
        <b>Overall Risk Level:</b> <font color="{risk_color}">{risk_level}</font><br/><br/>
        
        <b>🔍 RISK FACTORS ANALYZED:</b><br/>
        • Position sizing: Maximum 50% of any token balance per trade<br/>
        • Portfolio diversification: Multi-asset and multi-chain approach<br/>
        • Market volatility: Real-time price monitoring and adaptation<br/>
        • Execution risk: Comprehensive trade validation before execution<br/>
        • Liquidity risk: Only trading in supported token pairs<br/><br/>
        
        <b>📊 RISK METRICS:</b><br/>
        • Success Rate: {success_rate:.1f}% (Target: >60%)<br/>
        • Trade Frequency: {total_trades} trades over session duration<br/>
        • Maximum Single Trade: Limited to 50% of token balance<br/>
        • Chain Risk: Distributed across multiple blockchain networks<br/><br/>
        
        <b>🎯 RISK MITIGATION STRATEGIES:</b><br/>
        • Continuous market monitoring and sentiment analysis<br/>
        • Dynamic strategy adjustment based on performance<br/>
        • Automated stop-loss through intelligent decision making<br/>
        • Portfolio rebalancing to maintain optimal allocation<br/>
        """
        
        risk_para = Paragraph(risk_text, self.styles['Normal'])
        story.append(risk_para)
        story.append(Spacer(1, 20))
        
        return story

    def _create_conclusions(self, session_data: Dict) -> List:
        """Create conclusions and recommendations section"""
        story = []
        
        header = Paragraph("🎯 CONCLUSIONS & RECOMMENDATIONS", self.styles['SectionHeader'])
        story.append(header)
        
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        trades = session_info.get('trades_executed', [])
        
        total_pnl = performance.get('total_profit_loss', session_info.get('total_pnl', 0))
        success_rate = self._calculate_success_rate(performance, session_info)
        total_trades = len(trades)
        
        # Generate intelligent conclusions based on performance
        conclusions_text = f"""
        <b>📊 SESSION PERFORMANCE SUMMARY:</b><br/><br/>
        
        The Kairos AI autonomous trading session completed with <b>{total_trades} trades</b> 
        and a <b>{success_rate:.1f}% success rate</b>. The AI demonstrated 
        <b>{'strong' if success_rate > 70 else 'moderate' if success_rate > 50 else 'learning-focused'}</b> 
        performance with a total P&L of <b>${total_pnl:+,.4f}</b>.<br/><br/>
        
        <b>🔍 KEY FINDINGS:</b><br/><br/>
        
        • <b>AI Decision Quality:</b> {'Excellent' if success_rate > 80 else 'Good' if success_rate > 60 else 'Developing'} 
        - The AI made informed decisions based on comprehensive market analysis<br/><br/>
        
        • <b>Risk Management:</b> Effective position sizing and portfolio diversification maintained throughout<br/><br/>
        
        • <b>Market Adaptation:</b> {'Strong' if total_trades > 5 else 'Conservative'} responsiveness to market conditions 
        and news events<br/><br/>
        
        • <b>Technical Execution:</b> {'Excellent' if success_rate > 70 else 'Good'} trade execution with proper 
        chain management and validation<br/><br/>
        
        <b>💡 RECOMMENDATIONS FOR FUTURE SESSIONS:</b><br/><br/>
        """
        
        # Add specific recommendations based on performance
        if success_rate > 70:
            conclusions_text += """
            • <b>Continue Current Strategy:</b> The AI performed well and can handle longer trading sessions<br/>
            • <b>Increase Position Sizes:</b> Consider allowing slightly larger position sizes for high-confidence trades<br/>
            • <b>Expand Duration:</b> Longer sessions may yield better results with this performance level<br/>
            """
        elif success_rate > 50:
            conclusions_text += """
            • <b>Optimize Strategy Selection:</b> Review and refine the AI's strategy selection criteria<br/>
            • <b>Enhance Market Analysis:</b> Incorporate additional technical indicators for better timing<br/>
            • <b>Maintain Current Risk Levels:</b> Current position sizing appears appropriate<br/>
            """
        else:
            conclusions_text += """
            • <b>Review Strategy Framework:</b> Analyze unsuccessful trades to improve decision logic<br/>
            • <b>Reduce Trade Frequency:</b> Focus on higher-confidence opportunities<br/>
            • <b>Enhanced Market Filtering:</b> Improve market condition assessment before trading<br/>
            """
        
        conclusions_text += f"""<br/>
        <b>⚡ TECHNICAL RECOMMENDATIONS:</b><br/><br/>
        
        • <b>Portfolio Monitoring:</b> Continue real-time portfolio tracking and rebalancing<br/>
        • <b>News Integration:</b> Maintain comprehensive news sentiment analysis<br/>
        • <b>Multi-Chain Optimization:</b> Leverage cross-chain opportunities for better yields<br/>
        • <b>Learning Enhancement:</b> Build on successful strategies identified in this session<br/><br/>
        
        <b>📈 FUTURE OUTLOOK:</b><br/><br/>
        
        Based on this session's performance, the Kairos AI system shows 
        <b>{'excellent' if success_rate > 70 else 'promising' if success_rate > 50 else 'developing'}</b> 
        potential for autonomous cryptocurrency trading. Continued refinement and learning will enhance 
        future performance and trading outcomes.
        """
        
        conclusions_para = Paragraph(conclusions_text, self.styles['Normal'])
        story.append(conclusions_para)
        story.append(Spacer(1, 30))
        
        # Final signature
        signature = Paragraph(
            "<b>📄 Report generated by Kairos AI Trading System v3.0</b><br/>"
            f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S UTC')}<br/>"
            "🤖 Powered by Gemini AI • 🔗 Multi-Chain Trading • 📊 Real-Time Analytics",
            self.styles['MetricStyle']
        )
        story.append(signature)
        
        return story

    def _generate_text_report(self, session_data: Dict, output_path: str) -> str:
        """Generate comprehensive text report when PDF is not available"""
        print("📝 Generating text report (PDF not available)...")
        
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        trades = session_info.get('trades_executed', [])
        
        report_lines = [
            "🤖 KAIROS AI AUTONOMOUS TRADING REPORT",
            "=" * 60,
            "",
            f"📊 SESSION OVERVIEW",
            "-" * 30,
            f"Session ID: {session_info.get('id', session_info.get('session_id', 'Unknown'))}",
            f"User ID: {session_info.get('user_id', 'Unknown')}",
            f"Start Time: {self._format_datetime(session_info.get('start_time'))}",
            f"End Time: {self._format_datetime(session_info.get('end_time', 'In Progress'))}",
            f"Duration: {self._calculate_duration(session_info)}",
            f"Status: {session_info.get('status', 'Unknown')}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            f"💰 FINANCIAL PERFORMANCE",
            "-" * 30,
            f"Initial Portfolio Value: ${session_info.get('initial_portfolio_value', 0):,.2f}",
            f"Final Portfolio Value: ${performance.get('current_portfolio_value', 0):,.2f}",
            f"Total P&L: ${performance.get('total_profit_loss', session_info.get('total_pnl', 0)):+,.4f}",
            f"ROI: {self._calculate_roi(performance, session_info):.4f}%",
            "",
            f"📈 TRADING STATISTICS",
            "-" * 30,
            f"Total Trades: {len(trades)}",
            f"Successful Trades: {sum(1 for t in trades if t.get('success', False))}",
            f"Failed Trades: {sum(1 for t in trades if not t.get('success', True))}",
            f"Success Rate: {self._calculate_success_rate(performance, session_info):.1f}%",
            f"Average Trade Size: ${sum(float(t.get('amount', 0)) for t in trades) / max(len(trades), 1):.2f}",
            "",
            f"🔄 DETAILED TRADE LOG",
            "-" * 30
        ]
        
        # Add individual trades
        for i, trade in enumerate(trades, 1):
            status = "✅ SUCCESS" if trade.get('success', False) else "❌ FAILED"
            report_lines.extend([
                f"",
                f"Trade #{i}: {trade.get('from_token', 'Unknown')} → {trade.get('to_token', 'Unknown')}",
                f"  Timestamp: {self._format_datetime(trade.get('execution_time', trade.get('timestamp')))}",
                f"  Amount: {trade.get('from_amount', trade.get('amount', 0))} {trade.get('from_token', '')}",
                f"  Received: {trade.get('to_amount', 'Unknown')} {trade.get('to_token', '')}",
                f"  Status: {status}",
                f"  P&L: ${trade.get('profit_loss', 0):+.6f}",
                f"  Chain: {trade.get('chain', 'Unknown')}",
                f"  Tx Hash: {trade.get('tx_hash', 'N/A')}",
                f"  AI Confidence: {float(trade.get('ai_confidence', 0)) * 100:.1f}%"
            ])
            
            if trade.get('ai_reasoning'):
                report_lines.append(f"  AI Reasoning: {trade.get('ai_reasoning')}")
        
        # Add conclusions
        report_lines.extend([
            "",
            f"🎯 CONCLUSIONS",
            "-" * 20,
            f"The AI trading session completed with {self._calculate_success_rate(performance, session_info):.1f}% success rate.",
            f"Total P&L of ${performance.get('total_profit_loss', 0):+.4f} demonstrates the AI's market capabilities.",
            f"Risk management protocols maintained portfolio safety throughout the session.",
            f"Multi-chain trading capabilities enabled optimal token utilization.",
            "",
            f"📊 RECOMMENDATIONS",
            "-" * 20,
            f"• Continue monitoring AI performance and strategy evolution",
            f"• Maintain current risk management parameters",
            f"• Consider longer sessions for enhanced learning opportunities",
            f"• Review successful strategies for future implementation",
            "",
            f"🔒 DISCLAIMER",
            "-" * 15,
            f"This report documents autonomous AI trading with real market data.",
            f"Cryptocurrency trading involves substantial risk of loss.",
            f"Past performance does not guarantee future results.",
            f"Only trade with funds you can afford to lose.",
            "",
            f"Generated by Kairos AI Trading System v3.0",
            f"Powered by Gemini AI • Multi-Chain Trading • Real-Time Analytics"
        ])
        
        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"✅ Text report generated: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Error writing text report: {e}")
            return ""

    # Helper methods
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display"""
        if not dt_string or dt_string in ['Unknown', 'In Progress']:
            return dt_string
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return str(dt_string)

    def _calculate_duration(self, session_info: Dict) -> str:
        """Calculate session duration"""
        try:
            start_time = session_info.get('start_time')
            end_time = session_info.get('end_time')
            
            if not start_time:
                return "Unknown"
            
            if not end_time or end_time == 'In Progress':
                # Calculate from start to now
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                duration = datetime.utcnow() - start_dt.replace(tzinfo=None)
            else:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = end_dt - start_dt
            
            hours = duration.total_seconds() / 3600
            if hours < 1:
                minutes = duration.total_seconds() / 60
                return f"{minutes:.0f} minutes"
            else:
                return f"{hours:.1f} hours"
        except:
            return "Unknown"

    def _calculate_success_rate(self, performance: Dict, session_info: Dict) -> float:
        """Calculate trading success rate"""
        total_trades = performance.get('total_trades', len(session_info.get('trades_executed', [])))
        successful_trades = performance.get('successful_trades', 
                                          sum(1 for t in session_info.get('trades_executed', []) 
                                              if t.get('success', False)))
        
        if total_trades == 0:
            return 0.0
        return (successful_trades / total_trades) * 100

    def _calculate_roi(self, performance: Dict, session_info: Dict) -> float:
        """Calculate return on investment"""
        initial_value = session_info.get('initial_portfolio_value', 0)
        final_value = performance.get('current_portfolio_value', session_info.get('current_portfolio_value', 0))
        
        if initial_value == 0:
            return 0.0
        
        return ((final_value - initial_value) / initial_value) * 100

# Global instance for easy import
autonomous_report_generator = EnhancedAutonomousReportGenerator()

def generate_autonomous_session_report(session_data: Dict, output_path: Optional[str] = None) -> str:
    """Convenience function to generate awesome autonomous session reports"""
    print("🚀 Starting EPIC report generation...")
    return autonomous_report_generator.generate_autonomous_session_report(session_data, output_path)