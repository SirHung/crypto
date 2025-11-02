"""
GOD MODE 10000 - HIGH-FREQUENCY TRADING (HFT) ENGINE
===================================================
Ultra-low latency trading engine with microsecond execution,
order book imbalance detection, and tick-level pattern recognition.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Deque
from datetime import datetime, timezone
from enum import Enum
from collections import deque
import asyncio
import time

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

class OrderBookSide(Enum):
    BID = "Bid"
    ASK = "Ask"

@dataclass
class OrderBookLevel:
    """Represents a single level in the order book"""
    price: float
    quantity: float
    num_orders: int = 1

@dataclass
class OrderBookSnapshot:
    """Complete order book snapshot"""
    symbol: str
    timestamp: datetime
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    sequence_number: int

@dataclass
class OrderBookImbalance:
    """Order book imbalance metrics"""
    symbol: str
    timestamp: datetime
    bid_volume: float
    ask_volume: float
    imbalance_ratio: float  # bid_volume / (bid_volume + ask_volume)
    spread: float
    mid_price: float
    signal: str  # "BUY", "SELL", "NEUTRAL"
    confidence: float

@dataclass
class TickData:
    """Tick-level market data"""
    symbol: str
    timestamp: datetime
    price: float
    quantity: float
    side: OrderBookSide
    is_buyer_maker: bool

@dataclass
class HFTSignal:
    """High-frequency trading signal"""
    id: str
    symbol: str
    timestamp: datetime
    signal_type: str  # "ORDER_BOOK_IMBALANCE", "MICROSTRUCTURE", "SPREAD_CAPTURE"
    direction: str  # "BUY", "SELL"
    confidence: float
    urgency: float  # 0-1, how urgent is execution
    target_price: float
    expected_edge_bps: float  # Expected edge in basis points
    max_latency_ms: float  # Maximum acceptable latency

class HFTEngine:
    """
    High-Frequency Trading Engine - God Mode 10000
    Ultra-low latency trading with microsecond precision.
    """
    
    def __init__(self):
        self.logger = unified_logging.get_logger("hft_engine")
        self.order_book_cache: Dict[str, OrderBookSnapshot] = {}
        self.tick_history: Dict[str, Deque[TickData]] = {}
        self.max_tick_history = 1000
        self.signal_counter = 0
        self.logger.info("✅ HFT Engine initialized - God Mode 10000")
    
    async def analyze_order_book_imbalance(
        self, 
        order_book: OrderBookSnapshot,
        depth_levels: int = 10
    ) -> Optional[OrderBookImbalance]:
        """
        Analyze order book imbalance to detect short-term price movements
        """
        try:
            # Calculate total volume on each side
            bid_volume = sum(level.quantity for level in order_book.bids[:depth_levels])
            ask_volume = sum(level.quantity for level in order_book.asks[:depth_levels])
            
            total_volume = bid_volume + ask_volume
            if total_volume == 0:
                return None
            
            # Calculate imbalance ratio
            imbalance_ratio = bid_volume / total_volume
            
            # Calculate spread and mid price
            best_bid = order_book.bids[0].price if order_book.bids else 0
            best_ask = order_book.asks[0].price if order_book.asks else 0
            spread = best_ask - best_bid if best_bid and best_ask else 0
            mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
            
            # Generate signal
            if imbalance_ratio > 0.60:  # Strong bid side
                signal = "BUY"
                confidence = (imbalance_ratio - 0.5) * 2  # 0.6 -> 0.2 confidence
            elif imbalance_ratio < 0.40:  # Strong ask side
                signal = "SELL"
                confidence = (0.5 - imbalance_ratio) * 2
            else:
                signal = "NEUTRAL"
                confidence = 0.0
            
            imbalance = OrderBookImbalance(
                symbol=order_book.symbol,
                timestamp=order_book.timestamp,
                bid_volume=bid_volume,
                ask_volume=ask_volume,
                imbalance_ratio=imbalance_ratio,
                spread=spread,
                mid_price=mid_price,
                signal=signal,
                confidence=confidence
            )
            
            if signal != "NEUTRAL":
                self.logger.debug(f"Order book imbalance detected: {signal} @ {confidence:.2%}")
            
            return imbalance
            
        except Exception as e:
            self.logger.error(f"Error analyzing order book imbalance: {e}")
            return None
    
    def detect_aggressive_orders(
        self,
        symbol: str,
        lookback_ticks: int = 50
    ) -> Dict[str, Any]:
        """
        Detect aggressive buy/sell orders (takers) in recent tick data
        """
        try:
            if symbol not in self.tick_history:
                return {'aggressive_buys': 0, 'aggressive_sells': 0, 'signal': 'NEUTRAL'}
            
            recent_ticks = list(self.tick_history[symbol])[-lookback_ticks:]
            
            # Aggressive buy = buyer is taker (crosses spread)
            aggressive_buys = sum(1 for tick in recent_ticks if tick.is_buyer_maker == False)
            aggressive_sells = sum(1 for tick in recent_ticks if tick.is_buyer_maker == True)
            
            total = aggressive_buys + aggressive_sells
            if total == 0:
                return {'aggressive_buys': 0, 'aggressive_sells': 0, 'signal': 'NEUTRAL'}
            
            buy_ratio = aggressive_buys / total
            
            if buy_ratio > 0.65:
                signal = 'BUY'
            elif buy_ratio < 0.35:
                signal = 'SELL'
            else:
                signal = 'NEUTRAL'
            
            return {
                'aggressive_buys': aggressive_buys,
                'aggressive_sells': aggressive_sells,
                'buy_ratio': buy_ratio,
                'signal': signal,
                'confidence': abs(buy_ratio - 0.5) * 2
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting aggressive orders: {e}")
            return {'error': str(e)}
    
    async def generate_hft_signal(
        self,
        symbol: str,
        order_book: OrderBookSnapshot
    ) -> Optional[HFTSignal]:
        """
        Generate a high-frequency trading signal based on microstructure analysis
        """
        try:
            # Analyze order book imbalance
            imbalance = await self.analyze_order_book_imbalance(order_book)
            if not imbalance or imbalance.signal == "NEUTRAL":
                return None
            
            # Analyze recent tick flow
            aggressive_orders = self.detect_aggressive_orders(symbol)
            
            # Combine signals
            ob_signal = imbalance.signal
            tick_signal = aggressive_orders.get('signal', 'NEUTRAL')
            
            # Both signals must agree for high confidence
            if ob_signal != tick_signal:
                return None
            
            # Calculate combined confidence
            ob_confidence = imbalance.confidence
            tick_confidence = aggressive_orders.get('confidence', 0)
            combined_confidence = (ob_confidence + tick_confidence) / 2
            
            if combined_confidence < 0.3:
                return None
            
            # Calculate expected edge
            spread_bps = (imbalance.spread / imbalance.mid_price) * 10000 if imbalance.mid_price > 0 else 0
            expected_edge_bps = spread_bps * 0.3  # Capture 30% of spread
            
            # Generate signal
            self.signal_counter += 1
            signal = HFTSignal(
                id=f"HFT_{self.signal_counter}",
                symbol=symbol,
                timestamp=datetime.now(timezone.utc),
                signal_type="ORDER_BOOK_IMBALANCE",
                direction=ob_signal,
                confidence=combined_confidence,
                urgency=combined_confidence,  # Higher confidence = higher urgency
                target_price=imbalance.mid_price,
                expected_edge_bps=expected_edge_bps,
                max_latency_ms=100.0  # 100ms max latency
            )
            
            self.logger.info(f"🚀 HFT Signal: {signal.direction} {symbol} @ {signal.confidence:.2%}")
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generating HFT signal: {e}")
            return None
    
    def add_tick(self, tick: TickData):
        """Add a tick to history for analysis"""
        if tick.symbol not in self.tick_history:
            self.tick_history[tick.symbol] = deque(maxlen=self.max_tick_history)
        
        self.tick_history[tick.symbol].append(tick)
    
    async def execute_hft_order(
        self,
        signal: HFTSignal,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Execute HFT order with ultra-low latency
        """
        try:
            start_time = time.perf_counter()
            
            self.logger.info(f"Executing HFT order: {signal.direction} {quantity} {signal.symbol}")
            
            # Simulate order execution with minimal latency
            await asyncio.sleep(0.001)  # 1ms simulated execution
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Check if latency is acceptable
            if latency_ms > signal.max_latency_ms:
                self.logger.warning(f"⚠️ Latency exceeded: {latency_ms:.2f}ms > {signal.max_latency_ms}ms")
                return {
                    'success': False,
                    'reason': 'LATENCY_EXCEEDED',
                    'latency_ms': latency_ms
                }
            
            # Simulate fill
            fill_price = signal.target_price
            if signal.direction == "BUY":
                fill_price += signal.target_price * 0.0001  # Small slippage
            else:
                fill_price -= signal.target_price * 0.0001
            
            execution_result = {
                'success': True,
                'signal_id': signal.id,
                'symbol': signal.symbol,
                'side': signal.direction,
                'quantity': quantity,
                'fill_price': fill_price,
                'target_price': signal.target_price,
                'slippage_bps': abs((fill_price - signal.target_price) / signal.target_price) * 10000,
                'latency_ms': latency_ms,
                'timestamp': datetime.now(timezone.utc)
            }
            
            self.logger.info(f"✅ HFT order executed in {latency_ms:.2f}ms")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"HFT order execution error: {e}")
            return {'success': False, 'error': str(e)}

hft_engine = HFTEngine()

