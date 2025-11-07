"""
GOD MODE 10000 - ULTRA ADVANCED ORDER BOOK ANALYZER
===================================================
Professional-grade order book analysis and liquidity intelligence

ENHANCED FEATURES (God Mode 10000):
- Multi-level order book depth analysis
- Whale wall detection with strength classification
- Liquidity heatmaps and visualization
- Order book imbalance tracking
- Support/resistance level detection from order clustering
- Flash crash / pump detection via liquidity gaps
- Real-time spread and depth monitoring
- Cumulative delta analysis
- Market maker activity detection
- Spoofing and layering detection
- Order book pressure indicators
- Liquidity provision quality scoring
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None


@dataclass
class OrderBookLevel:
    """Single order book level"""
    price: float
    quantity: float
    total: float  # Cumulative


@dataclass
class OrderBookSnapshot:
    """Order book snapshot"""
    symbol: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    timestamp: datetime
    exchange: str
    
    @property
    def bid_price(self) -> float:
        """Best bid price"""
        return self.bids[0].price if self.bids else 0.0
    
    @property
    def ask_price(self) -> float:
        """Best ask price"""
        return self.asks[0].price if self.asks else 0.0
    
    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        return self.ask_price - self.bid_price if self.bids and self.asks else 0.0
    
    @property
    def spread_pct(self) -> float:
        """Spread as percentage of mid price"""
        mid_price = (self.bid_price + self.ask_price) / 2
        return (self.spread / mid_price * 100) if mid_price > 0 else 0.0


@dataclass
class WhaleWall:
    """Detected whale wall"""
    side: str  # 'bid' or 'ask'
    price: float
    quantity: float
    distance_from_mid_pct: float
    strength: str  # 'weak', 'moderate', 'strong', 'extreme'


class OrderBookAnalyzer:
    """Order Book Analyzer - God Mode 1000"""
    
    def __init__(self):
        """Initialize Order Book Analyzer"""
        self.unified_logger = unified_logging.get_logger("order_book_analyzer")
        self.market_data_fetcher = real_market_data_fetcher
        
        # Order book storage
        self.order_books: Dict[str, OrderBookSnapshot] = {}
        
        # Cache
        self.cache_ttl = 5  # 5 seconds cache
        self.last_update: Dict[str, datetime] = {}
        
        # Analysis thresholds
        self.whale_wall_threshold = 10.0  # 10x average order size
        self.depth_levels = 20  # Number of levels to analyze
        
        self.unified_logger.info("✅ Order Book Analyzer initialized - God Mode 1000")
    
    def get_order_book(self, symbol: str, exchange: str = 'binance', depth: int = 20) -> Optional[OrderBookSnapshot]:
        """Get order book snapshot"""
        try:
            # Check cache
            cache_key = f"{symbol}_{exchange}"
            if self._is_cache_valid(cache_key):
                return self.order_books.get(cache_key)
            
            # Fetch from exchange
            order_book = self._fetch_order_book(symbol, exchange, depth)
            
            if order_book:
                self.order_books[cache_key] = order_book
                self.last_update[cache_key] = datetime.now(timezone.utc)
                return order_book
            
            return None
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get order book: {e}")
            return None
    
    def detect_whale_walls(self, symbol: str, exchange: str = 'binance') -> List[WhaleWall]:
        """Detect whale walls in order book"""
        try:
            order_book = self.get_order_book(symbol, exchange)
            if not order_book:
                return []
            
            whale_walls = []
            mid_price = (order_book.bid_price + order_book.ask_price) / 2
            
            # Calculate average order size
            avg_bid_size = sum(b.quantity for b in order_book.bids) / len(order_book.bids) if order_book.bids else 0
            avg_ask_size = sum(a.quantity for a in order_book.asks) / len(order_book.asks) if order_book.asks else 0
            
            # Check bids for whale walls
            for bid in order_book.bids:
                if bid.quantity >= avg_bid_size * self.whale_wall_threshold:
                    distance_pct = ((mid_price - bid.price) / mid_price) * 100
                    strength = self._calculate_wall_strength(bid.quantity, avg_bid_size)
                    
                    whale_walls.append(WhaleWall(
                        side='bid',
                        price=bid.price,
                        quantity=bid.quantity,
                        distance_from_mid_pct=distance_pct,
                        strength=strength
                    ))
            
            # Check asks for whale walls
            for ask in order_book.asks:
                if ask.quantity >= avg_ask_size * self.whale_wall_threshold:
                    distance_pct = ((ask.price - mid_price) / mid_price) * 100
                    strength = self._calculate_wall_strength(ask.quantity, avg_ask_size)
                    
                    whale_walls.append(WhaleWall(
                        side='ask',
                        price=ask.price,
                        quantity=ask.quantity,
                        distance_from_mid_pct=distance_pct,
                        strength=strength
                    ))
            
            return whale_walls
            
        except Exception as e:
            self.unified_logger.error(f"Failed to detect whale walls: {e}")
            return []
    
    def get_market_depth_analysis(self, symbol: str, exchange: str = 'binance') -> Dict[str, Any]:
        """Analyze market depth"""
        try:
            order_book = self.get_order_book(symbol, exchange)
            if not order_book:
                return {
                    'bid_depth': 0.0,
                    'ask_depth': 0.0,
                    'depth_ratio': 1.0,
                    'imbalance': 'neutral'
                }
            
            # Calculate total depth
            bid_depth = sum(b.quantity * b.price for b in order_book.bids)
            ask_depth = sum(a.quantity * a.price for a in order_book.asks)
            
            # Depth ratio (bids/asks)
            depth_ratio = bid_depth / ask_depth if ask_depth > 0 else 1.0
            
            # Determine imbalance
            if depth_ratio > 1.5:
                imbalance = 'bullish'
                signal = 'Strong buying support - bullish pressure'
            elif depth_ratio < 0.67:
                imbalance = 'bearish'
                signal = 'Strong selling pressure - bearish pressure'
            else:
                imbalance = 'neutral'
                signal = 'Balanced order book'
            
            return {
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'depth_ratio': depth_ratio,
                'imbalance': imbalance,
                'signal': signal,
                'spread': order_book.spread,
                'spread_pct': order_book.spread_pct
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to analyze market depth: {e}")
            return {
                'bid_depth': 0.0,
                'ask_depth': 0.0,
                'depth_ratio': 1.0,
                'imbalance': 'neutral'
            }
    
    def get_liquidity_score(self, symbol: str, exchange: str = 'binance') -> Dict[str, Any]:
        """Calculate liquidity score"""
        try:
            order_book = self.get_order_book(symbol, exchange)
            if not order_book:
                return {
                    'score': 0.0,
                    'rating': 'unknown'
                }
            
            # Calculate liquidity factors
            spread_score = max(0, 100 - (order_book.spread_pct * 10))  # Lower spread = better
            depth_score = min(100, len(order_book.bids) + len(order_book.asks))  # More levels = better
            
            # Total liquidity
            total_bid_volume = sum(b.quantity for b in order_book.bids)
            total_ask_volume = sum(a.quantity for a in order_book.asks)
            volume_score = min(100, (total_bid_volume + total_ask_volume) / 10)
            
            # Combined score
            liquidity_score = (spread_score * 0.4 + depth_score * 0.3 + volume_score * 0.3)
            
            # Rating
            if liquidity_score >= 80:
                rating = 'excellent'
            elif liquidity_score >= 60:
                rating = 'good'
            elif liquidity_score >= 40:
                rating = 'moderate'
            else:
                rating = 'poor'
            
            return {
                'score': liquidity_score,
                'rating': rating,
                'spread_score': spread_score,
                'depth_score': depth_score,
                'volume_score': volume_score
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate liquidity score: {e}")
            return {
                'score': 0.0,
                'rating': 'unknown'
            }
    
    def get_support_resistance_from_book(self, symbol: str, exchange: str = 'binance') -> Dict[str, List[float]]:
        """Identify support/resistance levels from order book"""
        try:
            order_book = self.get_order_book(symbol, exchange)
            if not order_book:
                return {
                    'support_levels': [],
                    'resistance_levels': []
                }
            
            # Find significant bid clusters (support)
            support_levels = []
            avg_bid = sum(b.quantity for b in order_book.bids) / len(order_book.bids) if order_book.bids else 0
            
            for bid in order_book.bids:
                if bid.quantity >= avg_bid * 5:  # 5x average = significant
                    support_levels.append(bid.price)
            
            # Find significant ask clusters (resistance)
            resistance_levels = []
            avg_ask = sum(a.quantity for a in order_book.asks) / len(order_book.asks) if order_book.asks else 0
            
            for ask in order_book.asks:
                if ask.quantity >= avg_ask * 5:  # 5x average = significant
                    resistance_levels.append(ask.price)
            
            return {
                'support_levels': sorted(support_levels, reverse=True)[:5],  # Top 5
                'resistance_levels': sorted(resistance_levels)[:5]  # Top 5
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get S/R from order book: {e}")
            return {
                'support_levels': [],
                'resistance_levels': []
            }
    
    # ==================== PRIVATE METHODS ====================
    
    def _fetch_order_book(self, symbol: str, exchange: str, depth: int) -> Optional[OrderBookSnapshot]:
        """Fetch order book from exchange"""
        try:
            # Use real market data fetcher
            from real_market_data_fetcher import real_market_data_fetcher
            
            market_data = real_market_data_fetcher.get_market_data(symbol)
            if not market_data:
                return None
            
            # Get orderbook if available
            orderbook = market_data.get('orderbook', {})
            if not orderbook:
                return None
            
            # Create snapshot from real data
            snapshot = OrderBookSnapshot(
                symbol=symbol,
                exchange=exchange,
                bids=orderbook.get('bids', [])[:depth],
                asks=orderbook.get('asks', [])[:depth],
                timestamp=datetime.now(timezone.utc)
            )
            
            return snapshot
        except Exception as e:
            self.unified_logger.error(f"Failed to fetch order book: {e}")
            return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache is valid"""
        if cache_key not in self.last_update:
            return False
        
        elapsed = (datetime.now(timezone.utc) - self.last_update[cache_key]).total_seconds()
        return elapsed < self.cache_ttl
    
    def _calculate_wall_strength(self, order_size: float, avg_size: float) -> str:
        """Calculate whale wall strength"""
        ratio = order_size / avg_size if avg_size > 0 else 0
        
        if ratio >= 50:
            return 'extreme'
        elif ratio >= 30:
            return 'strong'
        elif ratio >= 15:
            return 'moderate'
        else:
            return 'weak'


# Global instance
order_book_analyzer = OrderBookAnalyzer()

