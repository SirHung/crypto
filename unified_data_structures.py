"""
[STAR] GOD MODE 1000 - UNIFIED DATA STRUCTURES 💫
==============================================
[START] CENTRALIZED DATA STRUCTURES FOR ALL MODULES
[FAST] ZERO DUPLICATES - UNIFIED ARCHITECTURE
[BULLSEYE] PRODUCTION-GRADE DATA MANAGEMENT

UNIFIED DATA STRUCTURES:
- Centralized data structures to eliminate duplication
- Consistent data models across all modules
- Optimized for performance and memory usage
- Type-safe and well-documented
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings

warnings.filterwarnings('ignore')

# ==================================================================================
#  TRADING ENUMS
# ==================================================================================

class SignalType(Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REBALANCE = "rebalance"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    LONG = "long"
    SHORT = "short"

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FILLED = "partially_filled"

class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"

class PositionSide(Enum):
    """Position side enumeration"""
    LONG = "long"
    SHORT = "short"

class TradingStrategy(Enum):
    """Trading strategy enumeration"""
    TREND_FOLLOWING = "trend_following"
    GRID_TRADING = "grid_trading"
    DCA = "dca"
    OCO = "oco"
    TRAILING_STOP = "trailing_stop"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"
    ARBITRAGE = "arbitrage"

# ==================================================================================
#  CORE DATA STRUCTURES
# ==================================================================================

@dataclass
class TradingSignal:
    """Unified trading signal data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    signal_type: SignalType = SignalType.HOLD
    price: float = 0.0
    quantity: float = 0.0
    confidence: float = 0.0
    source_module: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-5 (5 highest)
    expiry_time: Optional[datetime] = None
    
    # Enhanced fields for advanced trading
    action: str = "HOLD"  # 'BUY', 'SELL', 'HOLD', 'LONG', 'SHORT'
    stop_loss: float = 0.0
    take_profit: float = 0.0
    reason: str = ""
    timeframe: str = "1h"
    ai_model: str = "ensemble"
    risk_level: str = "MEDIUM"  # 'LOW', 'MEDIUM', 'HIGH', 'EXTREME'
    position_size: float = 0.0
    leverage: float = 1.0
    expected_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    meta_ai_explanation: str = ""
    shape_analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Order:
    """Unified order data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    order_type: OrderType = OrderType.MARKET
    side: OrderSide = OrderSide.BUY
    quantity: float = 0.0
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_price: float = 0.0
    fees: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    filled_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Additional fields
    exchange: str = ""
    client_order_id: Optional[str] = None
    time_in_force: str = "GTC"  # GTC, IOC, FOK
    post_only: bool = False
    reduce_only: bool = False

@dataclass
class Position:
    """Unified position data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: PositionSide = PositionSide.LONG
    size: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    leverage: float = 1.0
    margin_used: float = 0.0
    margin_available: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    ai_model: str = "unknown"
    risk_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Additional fields
    exchange: str = ""
    notional_value: float = 0.0
    liquidation_price: Optional[float] = None
    maintenance_margin: float = 0.0

@dataclass
class Trade:
    """Unified trade data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    size: float = 0.0
    price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    fees: float = 0.0
    pnl: float = 0.0
    ai_model: str = "unknown"
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Additional fields
    exchange: str = ""
    order_id: Optional[str] = None
    commission_asset: str = ""
    commission_amount: float = 0.0

@dataclass
class PortfolioMetrics:
    """Unified portfolio metrics data structure"""
    total_value: float = 0.0
    total_pnl: float = 0.0
    total_fees: float = 0.0
    net_pnl: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    var_95: float = 0.0
    var_99: float = 0.0
    beta: float = 0.0
    alpha: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PortfolioSummary:
    """Portfolio summary data structure"""
    total_value: float = 0.0
    total_pnl: float = 0.0
    positions: List['Position'] = field(default_factory=list)
    cash_balance: float = 0.0
    margin_used: float = 0.0
    available_margin: float = 0.0
    equity: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PositionAction:
    """Position management action"""
    action_type: str = ""  # SIZE/HEDGE/REBALANCE/CLOSE
    symbol: str = ""
    current_size: float = 0.0
    recommended_size: float = 0.0
    hedge_instruments: List[str] = field(default_factory=list)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PortfolioRebalance:
    """Portfolio rebalance data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_allocations: Dict[str, float] = field(default_factory=dict)
    current_allocations: Dict[str, float] = field(default_factory=dict)
    rebalance_orders: List[Order] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==================================================================================
#  MARKET DATA STRUCTURES
# ==================================================================================

@dataclass
class MarketData:
    """Unified market data structure"""
    symbol: str = ""
    price: float = 0.0
    volume: float = 0.0
    change_24h: float = 0.0
    change_percent_24h: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0
    exchange: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OHLCV:
    """OHLCV data structure"""
    timestamp: datetime = field(default_factory=datetime.now)
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IndicatorResult:
    """Unified indicator result structure"""
    name: str = ""
    value: float = 0.0
    signal: str = "HOLD"  # 'BUY', 'SELL', 'HOLD'
    strength: float = 0.0  # 0-1
    category: str = ""  # 'trend', 'momentum', 'volatility', 'volume', 'pattern'
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==================================================================================
#  AI AND ANALYSIS STRUCTURES
# ==================================================================================

@dataclass
class Prediction:
    """Unified prediction data structure"""
    symbol: str = ""
    prediction: str = "HOLD"  # 'BUY', 'SELL', 'HOLD'
    confidence: float = 0.0
    price_target: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    reason: str = ""
    model_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SentimentData:
    """Sentiment analysis data structure"""
    symbol: str = ""
    sentiment_score: float = 0.0  # -1 to 1
    sentiment_label: str = "NEUTRAL"  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationPreview:
    """Enhanced notification preview data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    message: str = ""
    priority: str = "MEDIUM"  # 'HIGH', 'MEDIUM', 'LOW', 'CRITICAL'
    category: str = "SYSTEM"  # 'TRADE', 'ALERT', 'SYSTEM', 'AI', 'AIRDROP', 'RISK'
    timestamp: datetime = field(default_factory=datetime.now)
    symbol: Optional[str] = None
    action: Optional[str] = None
    price: Optional[float] = None
    change_percent: Optional[float] = None
    meta_ai_summary: Optional[str] = None
    shape_insights: Optional[Dict[str, Any]] = None
    action_required: bool = False
    urgency_level: int = 1  # 1-5 scale
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==================================================================================
#  SYSTEM STRUCTURES
# ==================================================================================

# SystemHealth class moved to meta_ai_coordinator.py to avoid duplication

@dataclass
class ModuleStatus:
    """Module status tracking structure"""
    module_name: str = ""
    status: str = "inactive"  # 'active', 'inactive', 'error', 'initializing'
    last_update: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==================================================================================
#  UTILITY FUNCTIONS
# ==================================================================================

def create_trading_signal(
    symbol: str,
    signal_type: SignalType,
    price: float,
    confidence: float,
    source_module: str = "",
    **kwargs
) -> TradingSignal:
    """Create a trading signal with default values"""
    return TradingSignal(
        symbol=symbol,
        signal_type=signal_type,
        price=price,
        confidence=confidence,
        source_module=source_module,
        **kwargs
    )

def create_order(
    symbol: str,
    order_type: OrderType,
    side: OrderSide,
    quantity: float,
    price: Optional[float] = None,
    **kwargs
) -> Order:
    """Create an order with default values"""
    return Order(
        symbol=symbol,
        order_type=order_type,
        side=side,
        quantity=quantity,
        price=price,
        **kwargs
    )

def create_position(
    symbol: str,
    side: PositionSide,
    size: float,
    entry_price: float,
    **kwargs
) -> Position:
    """Create a position with default values"""
    return Position(
        symbol=symbol,
        side=side,
        size=size,
        entry_price=entry_price,
        current_price=entry_price,
        **kwargs
    )

def create_market_data(
    symbol: str,
    price: float,
    volume: float,
    **kwargs
) -> MarketData:
    """Create market data with default values"""
    return MarketData(
        symbol=symbol,
        price=price,
        volume=volume,
        **kwargs
    )

def create_prediction(
    symbol: str,
    prediction: str,
    confidence: float,
    model_name: str = "",
    **kwargs
) -> Prediction:
    """Create a prediction with default values"""
    return Prediction(
        symbol=symbol,
        prediction=prediction,
        confidence=confidence,
        model_name=model_name,
        **kwargs
    )

def create_trade(
    symbol: str,
    side: OrderSide,
    quantity: float,
    price: float,
    order_type: OrderType = OrderType.MARKET,
    **kwargs
) -> Trade:
    """Create a trade with default values"""
    return Trade(
        trade_id=str(uuid.uuid4()),
        symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        order_type=order_type,
        timestamp=datetime.now(),
        **kwargs
    )

def create_notification_preview(
    title: str,
    message: str,
    priority: str = "MEDIUM",
    category: str = "SYSTEM",
    **kwargs
) -> NotificationPreview:
    """Create a notification preview with default values"""
    return NotificationPreview(
        title=title,
        message=message,
        priority=priority,
        category=category,
        **kwargs
    )

