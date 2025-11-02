"""
GOD MODE 2000 - SOCIAL TRADING MODULE
=====================================
Copy Trading, Signal Following, Leaderboard, Performance Tracking
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import statistics

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging


class TraderTier(Enum):
    """Trader performance tiers"""
    LEGEND = "legend"      # Top 1%
    MASTER = "master"      # Top 5%
    EXPERT = "expert"      # Top 10%
    ADVANCED = "advanced"  # Top 25%
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"


@dataclass
class TraderProfile:
    """Trader profile for social trading"""
    trader_id: str
    username: str
    tier: TraderTier
    total_followers: int
    win_rate: float
    total_trades: int
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_pnl: float
    monthly_return: float
    risk_score: float  # 0-100
    avg_position_size: float
    avg_holding_time: float  # hours
    specialties: List[str] = field(default_factory=list)
    verified: bool = False
    premium: bool = False


@dataclass
class TradingSignal:
    """Trading signal from a trader"""
    signal_id: str
    trader_id: str
    symbol: str
    action: str  # BUY, SELL, CLOSE
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    confidence: float
    timestamp: datetime
    reasoning: str
    status: str = "ACTIVE"  # ACTIVE, CLOSED, CANCELLED


@dataclass
class CopyTradingConfig:
    """Copy trading configuration"""
    enabled: bool
    trader_id: str
    copy_ratio: float  # 0.1 = 10% of their position size
    max_position_size: float
    max_daily_trades: int
    allowed_symbols: List[str]
    risk_limit: float  # Max loss per trade
    auto_close: bool  # Auto close when trader closes


class SocialTrading:
    """Social Trading & Copy Trading - God Mode 2000"""
    
    def __init__(self):
        """Initialize Social Trading"""
        self.unified_logger = unified_logging.get_logger("social_trading")
        
        # Storage
        self.traders: Dict[str, TraderProfile] = {}
        self.signals: List[TradingSignal] = []
        self.followers: Dict[str, List[str]] = {}  # trader_id -> follower_ids
        self.copy_configs: Dict[str, CopyTradingConfig] = {}  # user_id -> config
        
        # Performance tracking
        self.signal_performance: Dict[str, Dict] = {}
        
        # Initialize demo traders
        self._initialize_demo_traders()
        
        self.unified_logger.info("✅ Social Trading initialized - God Mode 2000")
    
    def _initialize_demo_traders(self):
        """Initialize demo top traders"""
        demo_traders = [
            TraderProfile(
                trader_id="trader_001",
                username="CryptoWizard",
                tier=TraderTier.LEGEND,
                total_followers=15420,
                win_rate=0.78,
                total_trades=1250,
                profit_factor=2.8,
                sharpe_ratio=2.1,
                max_drawdown=0.12,
                total_pnl=458900.0,
                monthly_return=0.18,
                risk_score=35,
                avg_position_size=5000.0,
                avg_holding_time=18.5,
                specialties=["BTC", "ETH", "Swing Trading"],
                verified=True,
                premium=True
            ),
            TraderProfile(
                trader_id="trader_002",
                username="WhaleHunter",
                tier=TraderTier.MASTER,
                total_followers=8920,
                win_rate=0.72,
                total_trades=890,
                profit_factor=2.3,
                sharpe_ratio=1.8,
                max_drawdown=0.15,
                total_pnl=287600.0,
                monthly_return=0.15,
                risk_score=42,
                avg_position_size=8000.0,
                avg_holding_time=24.2,
                specialties=["Altcoins", "Scalping"],
                verified=True,
                premium=True
            ),
            TraderProfile(
                trader_id="trader_003",
                username="AITrader",
                tier=TraderTier.EXPERT,
                total_followers=6540,
                win_rate=0.68,
                total_trades=2100,
                profit_factor=1.9,
                sharpe_ratio=1.6,
                max_drawdown=0.18,
                total_pnl=198400.0,
                monthly_return=0.12,
                risk_score=50,
                avg_position_size=3000.0,
                avg_holding_time=6.8,
                specialties=["Day Trading", "Technical Analysis"],
                verified=True,
                premium=False
            ),
            TraderProfile(
                trader_id="trader_004",
                username="DeFiMaster",
                tier=TraderTier.EXPERT,
                total_followers=5230,
                win_rate=0.65,
                total_trades=670,
                profit_factor=1.7,
                sharpe_ratio=1.4,
                max_drawdown=0.20,
                total_pnl=156800.0,
                monthly_return=0.10,
                risk_score=55,
                avg_position_size=4500.0,
                avg_holding_time=72.0,
                specialties=["DeFi", "Fundamental Analysis"],
                verified=True,
                premium=False
            ),
            TraderProfile(
                trader_id="trader_005",
                username="TrendFollower",
                tier=TraderTier.ADVANCED,
                total_followers=3890,
                win_rate=0.62,
                total_trades=1580,
                profit_factor=1.5,
                sharpe_ratio=1.2,
                max_drawdown=0.22,
                total_pnl=98300.0,
                monthly_return=0.08,
                risk_score=60,
                avg_position_size=2500.0,
                avg_holding_time=12.4,
                specialties=["Trend Following", "Risk Management"],
                verified=False,
                premium=False
            )
        ]
        
        for trader in demo_traders:
            self.traders[trader.trader_id] = trader
    
    def get_leaderboard(self, tier: Optional[str] = None, limit: int = 20) -> List[TraderProfile]:
        """Get trader leaderboard"""
        try:
            traders = list(self.traders.values())
            
            # Filter by tier
            if tier:
                traders = [t for t in traders if t.tier.value == tier]
            
            # Sort by total PnL
            traders.sort(key=lambda x: x.total_pnl, reverse=True)
            
            return traders[:limit]
        
        except Exception as e:
            self.unified_logger.error(f"Leaderboard error: {e}")
            return []
    
    def get_trader_details(self, trader_id: str) -> Optional[TraderProfile]:
        """Get detailed trader profile"""
        return self.traders.get(trader_id)
    
    def follow_trader(self, user_id: str, trader_id: str) -> Tuple[bool, str]:
        """Follow a trader"""
        try:
            if trader_id not in self.traders:
                return False, "Trader not found"
            
            if trader_id not in self.followers:
                self.followers[trader_id] = []
            
            if user_id in self.followers[trader_id]:
                return False, "Already following this trader"
            
            self.followers[trader_id].append(user_id)
            self.traders[trader_id].total_followers += 1
            
            return True, f"Now following {self.traders[trader_id].username}"
        
        except Exception as e:
            self.unified_logger.error(f"Follow trader error: {e}")
            return False, str(e)
    
    def unfollow_trader(self, user_id: str, trader_id: str) -> Tuple[bool, str]:
        """Unfollow a trader"""
        try:
            if trader_id not in self.followers:
                return False, "Not following this trader"
            
            if user_id not in self.followers[trader_id]:
                return False, "Not following this trader"
            
            self.followers[trader_id].remove(user_id)
            self.traders[trader_id].total_followers -= 1
            
            return True, f"Unfollowed {self.traders[trader_id].username}"
        
        except Exception as e:
            self.unified_logger.error(f"Unfollow trader error: {e}")
            return False, str(e)
    
    def enable_copy_trading(self, user_id: str, config: CopyTradingConfig) -> Tuple[bool, str]:
        """Enable copy trading for a user"""
        try:
            if config.trader_id not in self.traders:
                return False, "Trader not found"
            
            # Validate config
            if config.copy_ratio <= 0 or config.copy_ratio > 1:
                return False, "Copy ratio must be between 0 and 1"
            
            self.copy_configs[user_id] = config
            
            return True, f"Copy trading enabled for {self.traders[config.trader_id].username}"
        
        except Exception as e:
            self.unified_logger.error(f"Enable copy trading error: {e}")
            return False, str(e)
    
    def disable_copy_trading(self, user_id: str) -> Tuple[bool, str]:
        """Disable copy trading"""
        try:
            if user_id not in self.copy_configs:
                return False, "Copy trading not enabled"
            
            del self.copy_configs[user_id]
            
            return True, "Copy trading disabled"
        
        except Exception as e:
            self.unified_logger.error(f"Disable copy trading error: {e}")
            return False, str(e)
    
    def get_latest_signals(self, trader_id: Optional[str] = None, limit: int = 50) -> List[TradingSignal]:
        """Get latest trading signals"""
        try:
            signals = self.signals
            
            if trader_id:
                signals = [s for s in signals if s.trader_id == trader_id]
            
            # Sort by timestamp
            signals.sort(key=lambda x: x.timestamp, reverse=True)
            
            return signals[:limit]
        
        except Exception as e:
            self.unified_logger.error(f"Get signals error: {e}")
            return []
    
    def publish_signal(self, signal: TradingSignal) -> Tuple[bool, str]:
        """Publish a trading signal"""
        try:
            if signal.trader_id not in self.traders:
                return False, "Trader not found"
            
            self.signals.append(signal)
            
            # Notify followers (in real app, send notifications)
            follower_count = len(self.followers.get(signal.trader_id, []))
            
            return True, f"Signal published to {follower_count} followers"
        
        except Exception as e:
            self.unified_logger.error(f"Publish signal error: {e}")
            return False, str(e)
    
    def get_signal_performance(self, trader_id: str) -> Dict[str, any]:
        """Get signal performance statistics for a trader"""
        try:
            trader_signals = [s for s in self.signals if s.trader_id == trader_id]
            
            if not trader_signals:
                return {}
            
            total_signals = len(trader_signals)
            active_signals = len([s for s in trader_signals if s.status == "ACTIVE"])
            closed_signals = len([s for s in trader_signals if s.status == "CLOSED"])
            
            # Calculate stats
            avg_confidence = statistics.mean([s.confidence for s in trader_signals])
            
            return {
                'total_signals': total_signals,
                'active_signals': active_signals,
                'closed_signals': closed_signals,
                'avg_confidence': avg_confidence,
                'last_signal_time': trader_signals[0].timestamp if trader_signals else None
            }
        
        except Exception as e:
            self.unified_logger.error(f"Signal performance error: {e}")
            return {}
    
    def search_traders(self, query: str = "", min_win_rate: float = 0.0, 
                      min_followers: int = 0, verified_only: bool = False) -> List[TraderProfile]:
        """Search traders with filters"""
        try:
            traders = list(self.traders.values())
            
            # Filter by query
            if query:
                traders = [t for t in traders if query.lower() in t.username.lower() or 
                          any(query.lower() in s.lower() for s in t.specialties)]
            
            # Filter by win rate
            if min_win_rate > 0:
                traders = [t for t in traders if t.win_rate >= min_win_rate]
            
            # Filter by followers
            if min_followers > 0:
                traders = [t for t in traders if t.total_followers >= min_followers]
            
            # Filter verified
            if verified_only:
                traders = [t for t in traders if t.verified]
            
            # Sort by followers
            traders.sort(key=lambda x: x.total_followers, reverse=True)
            
            return traders
        
        except Exception as e:
            self.unified_logger.error(f"Search traders error: {e}")
            return []


# Global instance
social_trading = SocialTrading()

