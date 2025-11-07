"""
GOD MODE 10000 - SIGNAL AGGREGATOR
==================================
Intelligent aggregation of multiple signal sources
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging

# Use centralized pandas/numpy bypass
# Fix Python 3.13 compatibility first
import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np



class SignalStrength(Enum):
    """Signal strength levels"""
    VERY_STRONG = "very_strong"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NEUTRAL = "neutral"


@dataclass
class AggregatedSignal:
    """Aggregated signal result"""
    symbol: str
    direction: str  # 'BUY', 'SELL', 'HOLD'
    strength: SignalStrength
    confidence: float
    sources_count: int
    agreement_ratio: float
    weighted_score: float
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float
    reasoning: str
    contributing_sources: List[str]
    timestamp: datetime


class SignalAggregator:
    """Signal Aggregator - GOD MODE 10000"""
    
    def __init__(self):
        """Initialize Signal Aggregator"""
        self.unified_logger = unified_logging.get_logger("signal_aggregator")
        
        # Signal source weights (dynamically adjusted)
        self.source_weights = {
            'ai_ensemble': 0.25,
            'technical': 0.20,
            'fundamental': 0.15,
            'sentiment': 0.10,
            'order_flow': 0.10,
            'volatility': 0.05,
            'whale': 0.05,
            'kol': 0.05,
            'rl_agent': 0.05
        }
        
        # Signal history for validation
        self.signal_history = []
        
        self.unified_logger.info("✅ Signal Aggregator initialized - God Mode 10000")
    
    def aggregate_signals(self, signals: List[Dict[str, Any]], 
                         market_data: Dict[str, Any]) -> AggregatedSignal:
        """Aggregate multiple signals into one actionable signal"""
        try:
            if not signals:
                return self._create_neutral_signal(market_data.get('symbol', 'N/A'))
            
            # Extract signal directions and confidences
            buy_signals = []
            sell_signals = []
            hold_signals = []
            
            for signal in signals:
                direction = signal.get('signal', 'HOLD').upper()
                confidence = signal.get('confidence', 0)
                source = signal.get('source', 'unknown')
                weight = self.source_weights.get(source, 0.05)
                
                weighted_confidence = confidence * weight
                
                if 'BUY' in direction:
                    buy_signals.append(weighted_confidence)
                elif 'SELL' in direction:
                    sell_signals.append(weighted_confidence)
                else:
                    hold_signals.append(weighted_confidence)
            
            # Calculate scores
            buy_score = sum(buy_signals)
            sell_score = sum(sell_signals)
            hold_score = sum(hold_signals)
            total_score = buy_score + sell_score + hold_score
            
            # Determine final direction
            if buy_score > sell_score and buy_score > hold_score:
                direction = 'BUY'
                weighted_score = buy_score / total_score if total_score > 0 else 0
                agreement_ratio = len(buy_signals) / len(signals)
            elif sell_score > buy_score and sell_score > hold_score:
                direction = 'SELL'
                weighted_score = sell_score / total_score if total_score > 0 else 0
                agreement_ratio = len(sell_signals) / len(signals)
            else:
                direction = 'HOLD'
                weighted_score = hold_score / total_score if total_score > 0 else 0
                agreement_ratio = len(hold_signals) / len(signals)
            
            # Determine strength
            strength = self._determine_strength(weighted_score, agreement_ratio)
            
            # Calculate confidence
            confidence = weighted_score * (0.7 + agreement_ratio * 0.3)
            
            # Get price levels
            entry_price = market_data.get('price', 0)
            stop_loss, take_profit = self._calculate_levels(
                direction, entry_price, market_data, confidence
            )
            
            # Calculate risk/reward
            if direction == 'BUY':
                risk = abs(entry_price - stop_loss)
                reward = abs(take_profit - entry_price)
            elif direction == 'SELL':
                risk = abs(stop_loss - entry_price)
                reward = abs(entry_price - take_profit)
            else:
                risk = reward = 0
            
            risk_reward = reward / risk if risk > 0 else 0
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                direction, signals, agreement_ratio, confidence
            )
            
            # Contributing sources
            contributing = [s.get('source', 'unknown') for s in signals 
                          if s.get('signal', 'HOLD').upper() == direction]
            
            return AggregatedSignal(
                symbol=market_data.get('symbol', 'N/A'),
                direction=direction,
                strength=strength,
                confidence=confidence,
                sources_count=len(signals),
                agreement_ratio=agreement_ratio,
                weighted_score=weighted_score,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward=risk_reward,
                reasoning=reasoning,
                contributing_sources=contributing,
                timestamp=datetime.now(timezone.utc)
            )
        
        except Exception as e:
            self.unified_logger.error(f"Signal aggregation error: {e}")
            return self._create_neutral_signal(market_data.get('symbol', 'N/A'))
    
    def _determine_strength(self, weighted_score: float, 
                           agreement_ratio: float) -> SignalStrength:
        """Determine signal strength"""
        try:
            combined_score = weighted_score * 0.7 + agreement_ratio * 0.3
            
            if combined_score > 0.8:
                return SignalStrength.VERY_STRONG
            elif combined_score > 0.65:
                return SignalStrength.STRONG
            elif combined_score > 0.5:
                return SignalStrength.MODERATE
            elif combined_score > 0.35:
                return SignalStrength.WEAK
            else:
                return SignalStrength.NEUTRAL
        
        except Exception:
            return SignalStrength.NEUTRAL
    
    def _calculate_levels(self, direction: str, entry_price: float,
                         market_data: Dict[str, Any], confidence: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels"""
        try:
            volatility = market_data.get('volatility', 0.02)
            atr = market_data.get('atr', entry_price * 0.02)
            
            # Dynamic multipliers based on confidence
            sl_multiplier = 1.5 if confidence > 0.7 else 2.0
            tp_multiplier = 3.0 if confidence > 0.7 else 2.5
            
            if direction == 'BUY':
                stop_loss = entry_price - (atr * sl_multiplier)
                take_profit = entry_price + (atr * tp_multiplier)
            elif direction == 'SELL':
                stop_loss = entry_price + (atr * sl_multiplier)
                take_profit = entry_price - (atr * tp_multiplier)
            else:  # HOLD
                stop_loss = entry_price * 0.95
                take_profit = entry_price * 1.05
            
            return stop_loss, take_profit
        
        except Exception as e:
            self.unified_logger.error(f"Level calculation error: {e}")
            return entry_price * 0.95, entry_price * 1.05
    
    def _generate_reasoning(self, direction: str, signals: List[Dict],
                           agreement_ratio: float, confidence: float) -> str:
        """Generate reasoning for the signal"""
        try:
            source_names = [s.get('source', 'unknown') for s in signals]
            
            reasoning_parts = []
            reasoning_parts.append(f"{direction} signal with {confidence*100:.0f}% confidence")
            reasoning_parts.append(f"{len(signals)} sources analyzed")
            reasoning_parts.append(f"{agreement_ratio*100:.0f}% agreement")
            reasoning_parts.append(f"Key sources: {', '.join(source_names[:3])}")
            
            return " | ".join(reasoning_parts)
        
        except Exception:
            return f"{direction} signal from {len(signals)} sources"
    
    def _create_neutral_signal(self, symbol: str) -> AggregatedSignal:
        """Create neutral signal"""
        return AggregatedSignal(
            symbol=symbol,
            direction='HOLD',
            strength=SignalStrength.NEUTRAL,
            confidence=0.5,
            sources_count=0,
            agreement_ratio=0,
            weighted_score=0,
            entry_price=0,
            stop_loss=0,
            take_profit=0,
            risk_reward=0,
            reasoning="Insufficient signal data",
            contributing_sources=[],
            timestamp=datetime.now(timezone.utc)
        )
    
    def update_source_weights(self, performance_data: Dict[str, float]):
        """Update source weights based on performance"""
        try:
            total_perf = sum(performance_data.values())
            if total_perf > 0:
                for source, perf in performance_data.items():
                    if source in self.source_weights:
                        self.source_weights[source] = perf / total_perf
                
                self.unified_logger.info(f"Updated source weights based on performance")
        
        except Exception as e:
            self.unified_logger.error(f"Weight update error: {e}")


# Global instance
signal_aggregator = SignalAggregator()

