"""
GOD MODE 10000 - ORDER FLOW TRACKER
====================================
Real-time Order Flow Analysis, Bid/Ask Pressure, Tape Reading
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from collections import deque

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



@dataclass
class OrderFlowMetrics:
    """Order flow metrics"""
    bid_volume: float
    ask_volume: float
    bid_ask_ratio: float
    buy_pressure: float
    sell_pressure: float
    delta: float  # Cumulative delta
    cvd: float  # Cumulative volume delta
    vwap: float  # Volume-weighted average price
    imbalance_score: float
    timestamp: datetime


class OrderFlowTracker:
    """Order Flow Tracker - GOD MODE 10000"""
    
    def __init__(self):
        """Initialize Order Flow Tracker"""
        self.unified_logger = unified_logging.get_logger("order_flow_tracker")
        
        # Order flow data
        self.order_flow_history: Dict[str, deque] = {}
        self.max_history = 1000
        
        # Metrics
        self.current_metrics: Dict[str, OrderFlowMetrics] = {}
        
        self.unified_logger.info("✅ Order Flow Tracker initialized - God Mode 10000")
    
    def process_trade(self, symbol: str, price: float, volume: float, 
                     side: str, timestamp: datetime = None):
        """Process individual trade"""
        try:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            
            # Initialize history
            if symbol not in self.order_flow_history:
                self.order_flow_history[symbol] = deque(maxlen=self.max_history)
            
            # Store trade
            trade = {
                'price': price,
                'volume': volume,
                'side': side,
                'timestamp': timestamp
            }
            self.order_flow_history[symbol].append(trade)
            
            # Update metrics
            self._update_metrics(symbol)
        
        except Exception as e:
            self.unified_logger.error(f"Trade processing error: {e}")
    
    def _update_metrics(self, symbol: str):
        """Update order flow metrics"""
        try:
            history = list(self.order_flow_history[symbol])
            if not history:
                return
            
            # Calculate bid/ask volumes
            bid_volume = sum(t['volume'] for t in history if t['side'] == 'buy')
            ask_volume = sum(t['volume'] for t in history if t['side'] == 'sell')
            
            # Bid/ask ratio
            bid_ask_ratio = bid_volume / (ask_volume + 1e-10)
            
            # Buy/sell pressure (normalized)
            total_volume = bid_volume + ask_volume
            buy_pressure = bid_volume / (total_volume + 1e-10)
            sell_pressure = ask_volume / (total_volume + 1e-10)
            
            # Delta (difference between buy and sell volume)
            delta = bid_volume - ask_volume
            
            # Cumulative volume delta
            cvd = sum(t['volume'] if t['side'] == 'buy' else -t['volume'] for t in history)
            
            # VWAP
            total_pv = sum(t['price'] * t['volume'] for t in history)
            vwap = total_pv / (total_volume + 1e-10)
            
            # Imbalance score (-1 to 1, negative = sell pressure, positive = buy pressure)
            imbalance_score = (buy_pressure - sell_pressure)
            
            # Create metrics
            metrics = OrderFlowMetrics(
                bid_volume=bid_volume,
                ask_volume=ask_volume,
                bid_ask_ratio=bid_ask_ratio,
                buy_pressure=buy_pressure,
                sell_pressure=sell_pressure,
                delta=delta,
                cvd=cvd,
                vwap=vwap,
                imbalance_score=imbalance_score,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.current_metrics[symbol] = metrics
        
        except Exception as e:
            self.unified_logger.error(f"Metrics update error: {e}")
    
    def get_order_flow_signal(self, symbol: str) -> Tuple[str, float]:
        """Get trading signal from order flow"""
        try:
            if symbol not in self.current_metrics:
                return 'NEUTRAL', 0.5
            
            metrics = self.current_metrics[symbol]
            
            # Signal logic
            signal = 'NEUTRAL'
            confidence = 0.5
            
            # Strong buy pressure
            if metrics.imbalance_score > 0.3 and metrics.cvd > 0:
                signal = 'BUY'
                confidence = 0.5 + (metrics.imbalance_score * 0.5)
            
            # Strong sell pressure
            elif metrics.imbalance_score < -0.3 and metrics.cvd < 0:
                signal = 'SELL'
                confidence = 0.5 + (abs(metrics.imbalance_score) * 0.5)
            
            # Moderate buy pressure
            elif metrics.imbalance_score > 0.1:
                signal = 'BUY'
                confidence = 0.5 + (metrics.imbalance_score * 0.3)
            
            # Moderate sell pressure
            elif metrics.imbalance_score < -0.1:
                signal = 'SELL'
                confidence = 0.5 + (abs(metrics.imbalance_score) * 0.3)
            
            return signal, min(confidence, 0.95)
        
        except Exception as e:
            self.unified_logger.error(f"Order flow signal error: {e}")
            return 'NEUTRAL', 0.5
    
    def get_metrics(self, symbol: str) -> Optional[OrderFlowMetrics]:
        """Get current metrics for symbol"""
        return self.current_metrics.get(symbol)
    
    def analyze_tape(self, symbol: str, last_n: int = 100) -> Dict[str, any]:
        """Analyze recent tape (last N trades)"""
        try:
            if symbol not in self.order_flow_history:
                return {}
            
            history = list(self.order_flow_history[symbol])[-last_n:]
            
            if not history:
                return {}
            
            # Analyze patterns
            large_trades = [t for t in history if t['volume'] > np.median([t['volume'] for t in history]) * 2]
            aggressive_buys = [t for t in history if t['side'] == 'buy' and t['volume'] > np.mean([t['volume'] for t in history])]
            aggressive_sells = [t for t in history if t['side'] == 'sell' and t['volume'] > np.mean([t['volume'] for t in history])]
            
            return {
                'total_trades': len(history),
                'large_trades': len(large_trades),
                'aggressive_buys': len(aggressive_buys),
                'aggressive_sells': len(aggressive_sells),
                'avg_trade_size': np.mean([t['volume'] for t in history]),
                'price_range': max(t['price'] for t in history) - min(t['price'] for t in history),
                'dominant_side': 'buy' if sum(1 for t in history if t['side'] == 'buy') > len(history) / 2 else 'sell'
            }
        
        except Exception as e:
            self.unified_logger.error(f"Tape analysis error: {e}")
            return {}


# Global instance
order_flow_tracker = OrderFlowTracker()

