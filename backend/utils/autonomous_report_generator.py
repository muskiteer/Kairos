#!/usr/bin/env python3
"""
Kairos Autonomous Trading Session PDF Report Generator
Creates detailed PDF reports from autonomous trading session data
Compatible with new agent, backend, and session schema
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(backend_dir))

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )
    from reportlab.lib.colors import HexColor
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
        self.styles.add(ParagraphStyle(
            name='KairosTitle', parent=self.styles['Title'], fontSize=28,
            textColor=HexColor('#1e3a8a'), spaceAfter=30, alignment=1, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(
            name='SessionHeader', parent=self.styles['Heading1'], fontSize=20,
            textColor=HexColor('#059669'), spaceBefore=20, spaceAfter=15,
            borderWidth=2, borderColor=HexColor('#10b981'), borderPadding=12,
            backColor=HexColor('#ecfdf5'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(
            name='SectionHeader', parent=self.styles['Heading2'], fontSize=16,
            textColor=HexColor('#1f2937'), spaceBefore=20, spaceAfter=12,
            borderWidth=1, borderColor=HexColor('#e5e7eb'), borderPadding=8,
            backColor=HexColor('#f9fafb'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(
            name='TradeDetail', parent=self.styles['Normal'], fontSize=10,
            textColor=HexColor('#374151'), leftIndent=15, rightIndent=15,
            spaceBefore=8, spaceAfter=8, backColor=HexColor('#f8fafc'),
            borderWidth=0.5, borderColor=HexColor('#cbd5e1'), borderPadding=8))
        self.styles.add(ParagraphStyle(
            name='AIReasoning', parent=self.styles['Normal'], fontSize=11,
            textColor=HexColor('#1e40af'), leftIndent=20, rightIndent=20,
            spaceBefore=10, spaceAfter=10, backColor=HexColor('#eff6ff'),
            borderWidth=1, borderColor=HexColor('#3b82f6'), borderPadding=12,
            fontName='Helvetica'))
        self.styles.add(ParagraphStyle(
            name='MetricStyle', parent=self.styles['Normal'], fontSize=12,
            fontName='Helvetica-Bold', textColor=HexColor('#059669'), alignment=1))

    def generate_autonomous_session_report(self, session_data: Dict, output_path: Optional[str] = None) -> str:
        session_id = session_data.get('session_data', {}).get('session_id', 'unknown')
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/kairos_autonomous_report_{session_id[:8]}_{timestamp}.pdf"
        if not REPORTLAB_AVAILABLE:
            return self._generate_text_report(session_data, output_path.replace('.pdf', '.txt'))
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        story.extend(self._create_title_page(session_data))
        story.extend(self._create_executive_summary(session_data))
        story.extend(self._create_trading_performance_section(session_data))
        story.extend(self._create_strategy_analysis(session_data))
        story.extend(self._create_detailed_trade_log(session_data))
        story.extend(self._create_ai_reasoning_section(session_data))
        story.extend(self._create_portfolio_evolution(session_data))
        story.extend(self._create_risk_assessment(session_data))
        story.extend(self._create_conclusions(session_data))
        doc.build(story)
        print(f"✅ Autonomous Trading Report generated: {output_path}")
        return output_path

    def _create_title_page(self, session_data: Dict) -> List:
        story = []
        session_info = session_data.get('session_data', {})
        performance = session_data.get('performance', {})
        title = Paragraph("🤖 Kairos AI Autonomous Trading Report", self.styles['KairosTitle'])
        story.append(title)
        story.append(Spacer(1, 30))
        session_header = Paragraph(f"Session: {session_info.get('session_id', 'Unknown')[:8]}...", self.styles['SessionHeader'])
        story.append(session_header)
        story.append(Spacer(1, 20))
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
            ['🤖 AI Engine:', performance.get('ai_engine', 'Kairos v2.0 Enhanced')],
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
        story = []
        performance = session_data.get('performance', {})
        session_info = session_data.get('session_data', {})
        header = Paragraph("📊 Executive Summary", self.styles['SectionHeader'])
        story.append(header)
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
        """
        summary_para = Paragraph(summary_text, self.styles['Normal'])
        story.append(summary_para)
        story.append(Spacer(1, 20))
        return story

    def _create_trading_performance_section(self, session_data: Dict) -> List:
        story = []
        header = Paragraph("💹 Trading Performance Analysis", self.styles['SectionHeader'])
        story.append(header)
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        performance = session_data.get('performance', {})
        if not trades:
            no_trades = Paragraph("No trades were executed in this session.", self.styles['Normal'])
            story.append(no_trades)
            return story
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
        return story

    def _create_strategy_analysis(self, session_data: Dict) -> List:
        story = []
        header = Paragraph("🎯 Strategy Analysis", self.styles['SectionHeader'])
        story.append(header)
        # ...existing code...
        return story

    def _create_detailed_trade_log(self, session_data: Dict) -> List:
        story = []
        header = Paragraph("📝 Detailed Trade Log", self.styles['SectionHeader'])
        story.append(header)
        trades = session_data.get('session_data', {}).get('trades_executed', [])
        if not trades:
            no_trades = Paragraph("No trades were executed.", self.styles['Normal'])
            story.append(no_trades)
            return story
        for i, trade in enumerate(trades, 1):
            trade_header = Paragraph(f"🔄 Trade #{i} - {trade.get('timestamp', 'Unknown')}", self.styles['Normal'])
            story.append(trade_header)
            story.append(Spacer(1, 5))
            trade_details = [
                ['Action', f"{trade.get('from_token', 'Unknown')} → {trade.get('to_token', 'Unknown')}"],
                ['Amount', f"{trade.get('amount', 0)} {trade.get('from_token', '')}"],
                ['Success', '✅ Yes' if trade.get('success', False) else '❌ No'],
                ['P&L', f"${trade.get('profit_loss', 0):+.4f}"],
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
        story = []
        header = Paragraph("🧠 AI Reasoning & Decision Analysis", self.styles['SectionHeader'])
        story.append(header)
        # ...existing code...
        return story

    def _create_portfolio_evolution(self, session_data: Dict) -> List:
        story = []
        header = Paragraph("📈 Portfolio Evolution", self.styles['SectionHeader'])
        story.append(header)
        # ...existing code...
        return story

    def _create_risk_assessment(self, session_data: Dict) -> List:
        story = []
        header = Paragraph("⚠️ Risk Assessment", self.styles['SectionHeader'])
        story.append(header)
        # ...existing code...
        return story

    def _create_conclusions(self, session_data: Dict) -> List:
        story = []
        header = Paragraph("🎯 Conclusions & Recommendations", self.styles['SectionHeader'])
        story.append(header)
        # ...existing code...
        return story

    def _generate_text_report(self, session_data: Dict, output_path: str) -> str:
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
