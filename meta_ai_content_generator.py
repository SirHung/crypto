"""
GOD MODE 10000 - META AI CONTENT GENERATOR
===========================================
AI-Powered Content Generation for Smart Notifications
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging


@dataclass
class ContentTemplate:
    """AI-generated content template"""
    title: str
    body: str
    emoji: str
    tone: str  # professional, urgent, casual, technical
    key_points: List[str]
    call_to_action: str


class MetaAIContentGenerator:
    """Meta AI Content Generator - GOD MODE 10000"""
    
    def __init__(self):
        """Initialize Meta AI Content Generator"""
        self.unified_logger = unified_logging.get_logger("meta_ai_content")
        
        # Content generation rules
        self.tone_styles = {
            'professional': {'emoji': '📊', 'prefix': 'Analysis:', 'style': 'formal'},
            'urgent': {'emoji': '🚨', 'prefix': 'ALERT:', 'style': 'direct'},
            'casual': {'emoji': '💡', 'prefix': 'Insight:', 'style': 'friendly'},
            'technical': {'emoji': '🔬', 'prefix': 'Technical:', 'style': 'detailed'}
        }
        
        self.unified_logger.info("✅ Meta AI Content Generator initialized - God Mode 10000")
    
    def generate_prediction_alert(self, prediction_data: Dict[str, Any], 
                                  shap_explanation: Dict[str, Any] = None) -> ContentTemplate:
        """Generate smart alert for prediction with SHAP explanation"""
        try:
            symbol = prediction_data.get('symbol', 'N/A')
            signal = prediction_data.get('signal', 'NEUTRAL')
            confidence = prediction_data.get('confidence', 0.5)
            entry_price = prediction_data.get('entry_price', 0)
            stop_loss = prediction_data.get('stop_loss', 0)
            take_profit = prediction_data.get('take_profit', 0)
            sources = prediction_data.get('sources', [])
            
            # Determine tone based on signal strength
            if confidence > 0.8:
                tone = 'urgent'
            elif confidence > 0.65:
                tone = 'professional'
            else:
                tone = 'casual'
            
            tone_config = self.tone_styles[tone]
            
            # Generate title
            signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
            title = f"{tone_config['emoji']} {tone_config['prefix']} {symbol} - {signal_emoji} {signal}"
            
            # Generate body with SHAP insights
            body_parts = []
            
            # Opening
            body_parts.append(f"**{symbol} Analysis Complete**")
            body_parts.append(f"Signal: **{signal}** (Confidence: {confidence*100:.1f}%)")
            body_parts.append("")
            
            # Entry points
            body_parts.append(f"📍 **Entry:** ${entry_price:,.2f}")
            body_parts.append(f"🛑 **Stop Loss:** ${stop_loss:,.2f}")
            body_parts.append(f"🎯 **Take Profit:** ${take_profit:,.2f}")
            
            # Risk/Reward
            if entry_price > 0 and stop_loss > 0 and take_profit > 0:
                risk = abs(entry_price - stop_loss)
                reward = abs(take_profit - entry_price)
                rr_ratio = reward / risk if risk > 0 else 0
                body_parts.append(f"⚖️ **Risk:Reward:** 1:{rr_ratio:.2f}")
            body_parts.append("")
            
            # SHAP explanation
            if shap_explanation:
                body_parts.append("**🧠 AI Reasoning (SHAP Analysis):**")
                top_factors = shap_explanation.get('top_factors', [])
                for i, factor in enumerate(top_factors[:3], 1):
                    impact = "↑" if factor.get('impact', 0) > 0 else "↓"
                    body_parts.append(f"{i}. {factor.get('name', 'N/A')} {impact} ({abs(factor.get('impact', 0)):.2%})")
                body_parts.append("")
            
            # Contributing sources
            if sources:
                body_parts.append("**📊 Contributing Sources:**")
                for source in sources[:5]:
                    source_name = source.get('name', 'Unknown')
                    source_conf = source.get('confidence', 0)
                    body_parts.append(f"• {source_name}: {source_conf*100:.0f}%")
                body_parts.append("")
            
            # Key points
            key_points = self._extract_key_points(prediction_data, shap_explanation)
            
            # Call to action
            if signal == "BUY" and confidence > 0.7:
                cta = "✅ Consider LONG position with proper risk management"
            elif signal == "SELL" and confidence > 0.7:
                cta = "⚠️ Consider SHORT position or exit longs"
            else:
                cta = "ℹ️ Monitor closely for better entry opportunity"
            
            body_parts.append(f"**{cta}**")
            
            return ContentTemplate(
                title=title,
                body="\n".join(body_parts),
                emoji=signal_emoji,
                tone=tone,
                key_points=key_points,
                call_to_action=cta
            )
        
        except Exception as e:
            self.unified_logger.error(f"Prediction alert generation error: {e}")
            # NO FALLBACK: Raise error instead of generating fake content
            raise RuntimeError(
                f"❌ CRITICAL: Failed to generate prediction alert content\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Ensure prediction_data contains valid fields\n"
                f"❌ NO FALLBACK: Cannot generate fake/placeholder content"
            )
    
    def generate_whale_alert(self, whale_data: Dict[str, Any]) -> ContentTemplate:
        """Generate alert for whale activity"""
        try:
            symbol = whale_data.get('symbol', 'N/A')
            net_flow = whale_data.get('net_flow', 0)
            volume = whale_data.get('volume', 0)
            tx_count = whale_data.get('tx_count', 0)
            
            # Determine significance
            if abs(net_flow) > 10000000:  # $10M+
                tone = 'urgent'
                significance = "MASSIVE"
            elif abs(net_flow) > 1000000:  # $1M+
                tone = 'professional'
                significance = "SIGNIFICANT"
            else:
                tone = 'casual'
                significance = "Notable"
            
            tone_config = self.tone_styles[tone]
            
            # Direction
            direction = "INFLOW 📈" if net_flow > 0 else "OUTFLOW 📉"
            direction_emoji = "🟢" if net_flow > 0 else "🔴"
            
            title = f"{tone_config['emoji']} WHALE ALERT: {symbol} - {direction_emoji} {significance} {direction}"
            
            body_parts = []
            body_parts.append(f"**🐋 Whale Movement Detected: {symbol}**")
            body_parts.append("")
            body_parts.append(f"💰 **Net Flow:** ${net_flow:,.0f}")
            body_parts.append(f"📊 **Total Volume:** ${volume:,.0f}")
            body_parts.append(f"🔢 **Transactions:** {tx_count}")
            body_parts.append("")
            
            # Interpretation
            if net_flow > 0:
                body_parts.append("**📈 Interpretation:**")
                body_parts.append("• Whales are accumulating")
                body_parts.append("• Potential bullish signal")
                body_parts.append("• Could indicate upcoming price increase")
                cta = "✅ Consider this bullish signal for entry"
            else:
                body_parts.append("**📉 Interpretation:**")
                body_parts.append("• Whales are distributing")
                body_parts.append("• Potential bearish signal")
                body_parts.append("• Could indicate profit-taking or exit")
                cta = "⚠️ Exercise caution or consider taking profits"
            
            body_parts.append("")
            body_parts.append(f"**{cta}**")
            
            return ContentTemplate(
                title=title,
                body="\n".join(body_parts),
                emoji=direction_emoji,
                tone=tone,
                key_points=[
                    f"Net flow: ${net_flow:,.0f}",
                    f"{tx_count} whale transactions",
                    direction
                ],
                call_to_action=cta
            )
        
        except Exception as e:
            self.unified_logger.error(f"Whale alert generation error: {e}")
            # NO FALLBACK: Raise error instead of generating fake content
            raise RuntimeError(
                f"❌ CRITICAL: Failed to generate whale alert content\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Ensure whale_data contains valid fields\n"
                f"❌ NO FALLBACK: Cannot generate fake/placeholder content"
            )
    
    def generate_portfolio_alert(self, portfolio_data: Dict[str, Any]) -> ContentTemplate:
        """Generate portfolio performance alert"""
        try:
            total_value = portfolio_data.get('total_value', 0)
            total_pnl = portfolio_data.get('total_pnl', 0)
            pnl_pct = portfolio_data.get('pnl_pct', 0)
            best_performer = portfolio_data.get('best_performer', 'N/A')
            worst_performer = portfolio_data.get('worst_performer', 'N/A')
            
            # Determine tone
            if pnl_pct > 10:
                tone = 'urgent'
                mood = "Excellent"
                mood_emoji = "🎉"
            elif pnl_pct > 5:
                tone = 'professional'
                mood = "Good"
                mood_emoji = "✅"
            elif pnl_pct > 0:
                tone = 'casual'
                mood = "Positive"
                mood_emoji = "📈"
            else:
                tone = 'urgent'
                mood = "Attention Needed"
                mood_emoji = "⚠️"
            
            tone_config = self.tone_styles[tone]
            
            title = f"{mood_emoji} Portfolio Update: {mood} Performance"
            
            body_parts = []
            body_parts.append(f"**💼 Your Portfolio Summary**")
            body_parts.append("")
            body_parts.append(f"💰 **Total Value:** ${total_value:,.2f}")
            body_parts.append(f"📊 **P&L:** ${total_pnl:,.2f} ({pnl_pct:+.2f}%)")
            body_parts.append("")
            body_parts.append(f"🏆 **Best Performer:** {best_performer}")
            body_parts.append(f"⚠️ **Worst Performer:** {worst_performer}")
            body_parts.append("")
            
            # Recommendations
            if pnl_pct > 10:
                body_parts.append("**💡 Recommendations:**")
                body_parts.append("• Consider taking partial profits")
                body_parts.append("• Rebalance portfolio if needed")
                body_parts.append("• Set trailing stop losses")
                cta = "Great performance! Consider profit-taking strategy"
            elif pnl_pct < -5:
                body_parts.append("**💡 Recommendations:**")
                body_parts.append("• Review losing positions")
                body_parts.append("• Consider cutting losses on worst performers")
                body_parts.append("• Reassess risk management")
                cta = "⚠️ Portfolio needs attention - review positions"
            else:
                body_parts.append("**💡 Status:**")
                body_parts.append("• Portfolio is stable")
                body_parts.append("• Continue monitoring")
                cta = "✅ Portfolio on track - continue monitoring"
            
            body_parts.append("")
            body_parts.append(f"**{cta}**")
            
            return ContentTemplate(
                title=title,
                body="\n".join(body_parts),
                emoji=mood_emoji,
                tone=tone,
                key_points=[
                    f"Value: ${total_value:,.2f}",
                    f"P&L: {pnl_pct:+.2f}%",
                    mood
                ],
                call_to_action=cta
            )
        
        except Exception as e:
            self.unified_logger.error(f"Portfolio alert generation error: {e}")
            # NO FALLBACK: Raise error instead of generating fake content
            raise RuntimeError(
                f"❌ CRITICAL: Failed to generate portfolio alert content\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Ensure portfolio_data contains valid fields\n"
                f"❌ NO FALLBACK: Cannot generate fake/placeholder content"
            )
    
    def _extract_key_points(self, prediction_data: Dict[str, Any], 
                           shap_explanation: Dict[str, Any] = None) -> List[str]:
        """Extract key points from prediction data"""
        key_points = []
        
        try:
            # Add signal
            signal = prediction_data.get('signal', 'NEUTRAL')
            confidence = prediction_data.get('confidence', 0)
            key_points.append(f"{signal} signal ({confidence*100:.0f}% confidence)")
            
            # Add top SHAP factors
            if shap_explanation:
                top_factors = shap_explanation.get('top_factors', [])
                if top_factors:
                    top_factor = top_factors[0]
                    key_points.append(f"Key driver: {top_factor.get('name', 'N/A')}")
            
            # Add source count
            sources = prediction_data.get('sources', [])
            if sources:
                key_points.append(f"{len(sources)} sources agree")
            
            # Add regime
            regime = prediction_data.get('market_regime', '')
            if regime:
                key_points.append(f"Market: {regime}")
        
        except Exception as e:
            self.unified_logger.error(f"Key points extraction error: {e}")
        
        return key_points[:5]  # Limit to 5 key points


# Global instance
meta_ai_content = MetaAIContentGenerator()

