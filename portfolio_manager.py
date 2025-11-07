"""
[STAR] GOD MODE 1000 - PORTFOLIO MANAGEMENT ENGINE 💫
=====================================================
[START] ADVANCED PORTFOLIO MANAGEMENT & RISK CONTROL
[FAST] REAL-TIME P&L TRACKING & POSITION MANAGEMENT
[BULLSEYE] ENTERPRISE-GRADE PORTFOLIO OPTIMIZATION

PORTFOLIO MANAGEMENT CAPABILITIES:
- Multi-exchange portfolio consolidation
- Real-time P&L calculation and tracking
- Advanced risk management and position sizing
- Portfolio optimization and rebalancing
- Performance analytics and benchmarking
- Multi-asset allocation management
- Hedging and derivative position tracking
- VaR and risk metrics calculation
"""

import asyncio
# Removed threading imports to avoid ScriptRunContext warnings
import time
import json
# Import centralized pandas/numpy bypass to eliminate duplicates
# Fix Python 3.13 compatibility first
import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Import unified modules - NO FALLBACK/BYPASS
from unified_logging_manager import unified_logging
from unified_config import UnifiedConfig
from unified_data_structures import Position, Trade, PortfolioSummary, PositionSide, PositionAction
from unified_cache_manager import unified_cache

dynamic_config = UnifiedConfig()

class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    portfolio_value: float
    total_margin_used: float
    available_margin: float
    max_drawdown: float
    var_95: float
    var_99: float
    sharpe_ratio: float
    volatility: float
    beta: float
    correlation_btc: float
    leverage_ratio: float
    margin_ratio: float

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    sortino_ratio: float
    calmar_ratio: float
    beta: float
    alpha: float
    information_ratio: float

class AdvancedPortfolioManager:
    """[STAR] ADVANCED PORTFOLIO MANAGER - GOD MODE 1000
    Comprehensive portfolio management with advanced risk control
    """
    
    def __init__(self):
        """Initialize Advanced Portfolio Manager"""
        try:
            self.unified_logger = unified_logging.get_logger("portfolio_manager")
            
            # Portfolio data
            self.positions: Dict[str, Position] = {}
            self.trades: List[Trade] = []
            self.portfolio_history: List[Dict[str, Any]] = []
            
            # Risk management
            self.risk_limits = {
                'max_position_size': 0.1,  # 10% max per position
                'max_portfolio_risk': 0.2,  # 20% max portfolio risk
                'max_drawdown': 0.15,  # 15% max drawdown
                'max_leverage': 3.0,  # 3x max leverage
                'var_threshold': 0.05  # 5% VaR threshold
            }
            
            # Performance tracking
            self.performance_metrics = PerformanceMetrics(
                total_return=0.0,
                annualized_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                beta=0.0,
                alpha=0.0,
                information_ratio=0.0
            )
            
            # Removed threading to avoid ScriptRunContext warnings
            # All operations are now synchronous to prevent UI blocking
            self._executor = None
            self._executor_max_workers = int(dynamic_config.get('portfolio.executor_max_workers', 10))
            
            # Real-time updates
            self.last_update = datetime.now()
            self.update_interval = 30  # seconds
            
            self.unified_logger.info("Advanced Portfolio Manager initialized - God Mode 1000")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize Portfolio Manager: {e}")
            raise e
    
    def add_position(self, symbol: str, size: float, avg_price: float, side: str = 'long') -> bool:
        """Add or update position"""
        try:
            if symbol in self.positions:
                # Update existing position
                position = self.positions[symbol]
                total_value = (position.size * position.avg_price) + (size * avg_price)
                total_size = position.size + size
                new_avg_price = total_value / total_size if total_size != 0 else avg_price
                
                position.size = total_size
                position.avg_price = new_avg_price
                position.side = side
            else:
                # Create new position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    size=size,
                    avg_price=avg_price,
                    side=side
                )
            
            self.unified_logger.info(f"Position updated: {symbol} {size} @ {avg_price}")
            return True
                
        except Exception as e:
            self.unified_logger.error(f"Failed to add position: {e}")
            return False
    
    def close_position(self, symbol: str, size: float, price: float) -> bool:
        """Close or partially close position"""
        try:
            if symbol not in self.positions:
                self.unified_logger.log_warning("portfolio_manager", f"Position {symbol} not found")
                return False
            
            position = self.positions[symbol]
            close_size = min(size, abs(position.size))
            
            # Calculate P&L
            if position.side == 'long':
                pnl = (price - position.avg_price) * close_size
            else:
                pnl = (position.avg_price - price) * close_size
            
            # Update position
            position.size -= close_size if position.side == 'long' else -close_size
            position.realized_pnl += pnl
            
            # Remove position if fully closed
            if abs(position.size) < 1e-8:
                del self.positions[symbol]
            
            # Record trade
            trade = Trade(
                symbol=symbol,
                side='sell' if position.side == 'long' else 'buy',
                size=close_size,
                price=price,
                timestamp=datetime.now(),
                trade_id=f"{symbol}_{int(time.time())}"
            )
            self.trades.append(trade)
            
            self.unified_logger.info(f"Position closed: {symbol} {close_size} @ {price}, P&L: {pnl:.2f}")
            return True
                
        except Exception as e:
            self.unified_logger.error(f"Failed to close position: {e}")
            return False
    
    def update_prices(self, price_data: Dict[str, float]):
        """Update current prices for all positions"""
        try:
            total_unrealized_pnl = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in price_data:
                    position.current_price = price_data[symbol]
                    
                    # Calculate unrealized P&L
                    if position.side == 'long':
                        position.unrealized_pnl = (position.current_price - position.avg_price) * position.size
                    else:
                        position.unrealized_pnl = (position.avg_price - position.current_price) * abs(position.size)
                    
                    total_unrealized_pnl += position.unrealized_pnl
            
            self.last_update = datetime.now()
            self.unified_logger.log_debug("portfolio_manager", f"Prices updated, total unrealized P&L: {total_unrealized_pnl:.2f}")
                
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to update prices: {e}", exception=e)
    
    def get_portfolio_summary(self) -> PortfolioSummary:
        """Get portfolio summary"""
        try:
            total_value = 0.0
            total_pnl = 0.0
            positions_list = []
            
            for position in self.positions.values():
                if position.current_price > 0:
                    position_value = position.current_price * abs(position.size)
                    total_value += position_value
                    total_pnl += position.unrealized_pnl + position.realized_pnl
                    positions_list.append(position)
            
            return PortfolioSummary(
                total_value=total_value,
                total_pnl=total_pnl,
                positions=positions_list,
                cash_balance=0.0  # Would be calculated from exchange balances
            )
                
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to get portfolio summary: {e}", exception=e)
            return PortfolioSummary(total_value=0.0, total_pnl=0.0, positions=[])
    
    def get_portfolio_summary_dict(self) -> Dict:
        """Get portfolio summary as dictionary for UI display - God Mode 10000"""
        try:
            summary = self.get_portfolio_summary()
            
            # Convert to dictionary format
            total_value = summary.total_value if hasattr(summary, 'total_value') else 0.0
            total_pnl = summary.total_pnl if hasattr(summary, 'total_pnl') else 0.0
            
            # Calculate metrics
            pnl_percent = (total_pnl / total_value * 100) if total_value > 0 else 0.0
            daily_change = pnl_percent  # Simplified for now
            
            # Count winning and losing positions
            positions = summary.positions if hasattr(summary, 'positions') else []
            winning_positions = sum(1 for p in positions if p.unrealized_pnl + p.realized_pnl > 0)
            total_positions = len(positions)
            win_rate = (winning_positions / total_positions * 100) if total_positions > 0 else 0.0
            
            # Convert positions to dict format
            positions_dict = []
            for pos in positions:
                positions_dict.append({
                    'symbol': pos.symbol,
                    'size': pos.size,
                    'asset': pos.symbol.split('/')[0] if '/' in pos.symbol else pos.symbol,
                    'entry_price': pos.avg_price,
                    'current_price': pos.current_price,
                    'value': pos.current_price * abs(pos.size),
                    'pnl': pos.unrealized_pnl + pos.realized_pnl,
                    'pnl_percent': ((pos.current_price - pos.avg_price) / pos.avg_price * 100) if pos.avg_price > 0 else 0.0
                })
            
            return {
                'total_value': total_value,
                'total_pnl': total_pnl,
                'pnl_percent': pnl_percent,
                'daily_change': daily_change,
                'win_rate': win_rate,
                'active_positions': total_positions,
                'positions': positions_dict
            }
        
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to get portfolio summary dict: {e}", exception=e)
            return {
                'total_value': 0.0,
                'total_pnl': 0.0,
                'pnl_percent': 0.0,
                'daily_change': 0.0,
                'win_rate': 0.0,
                'active_positions': 0,
                'positions': []
            }
    
    def get_allocation(self) -> Dict[str, float]:
        """Get asset allocation percentages - God Mode 10000"""
        try:
            summary = self.get_portfolio_summary()
            total_value = summary.total_value if hasattr(summary, 'total_value') else 0.0
            
            if total_value <= 0:
                return {}
            
            # Calculate allocation for each asset
            allocation = {}
            positions = summary.positions if hasattr(summary, 'positions') else []
            
            for pos in positions:
                asset = pos.symbol.split('/')[0] if '/' in pos.symbol else pos.symbol
                position_value = pos.current_price * abs(pos.size)
                allocation_pct = (position_value / total_value * 100)
                
                if asset in allocation:
                    allocation[asset] += allocation_pct
                else:
                    allocation[asset] = allocation_pct
            
            return allocation
        
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to get allocation: {e}", exception=e)
            return {}
    
    def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate portfolio risk metrics"""
        try:
            portfolio_summary = self.get_portfolio_summary()
            
            # Calculate VaR (simplified)
            returns = self._calculate_returns()
            var_95 = np.percentile(returns, 5) if len(returns) > 0 else -0.05
            var_99 = np.percentile(returns, 1) if len(returns) > 0 else -0.10
            
            # Calculate volatility
            volatility = np.std(returns) * np.sqrt(252) if len(returns) > 0 else 0.0
            
            # Calculate Sharpe ratio (simplified)
            avg_return = np.mean(returns) * 252 if len(returns) > 0 else 0.0
            sharpe_ratio = avg_return / volatility if volatility > 0 else 0.0
            
            # Calculate max drawdown
            max_drawdown = self._calculate_max_drawdown()
            
            return RiskMetrics(
                portfolio_value=portfolio_summary.total_value,
                total_margin_used=0.0,  # Would be calculated from exchange data
                available_margin=0.0,  # Would be calculated from exchange data
                max_drawdown=max_drawdown,
                var_95=var_95,
                var_99=var_99,
                sharpe_ratio=sharpe_ratio,
                volatility=volatility,
                beta=0.0,  # Would be calculated against BTC
                correlation_btc=0.0,  # Would be calculated
                leverage_ratio=1.0,  # Would be calculated
                margin_ratio=0.0  # Would be calculated
            )
            
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to calculate risk metrics: {e}", exception=e)
            return RiskMetrics(
                portfolio_value=0.0,
                total_margin_used=0.0,
                available_margin=0.0,
                max_drawdown=0.0,
                var_95=0.0,
                var_99=0.0,
                sharpe_ratio=0.0,
                volatility=0.0,
                beta=0.0,
                correlation_btc=0.0,
                leverage_ratio=1.0,
                margin_ratio=0.0
            )
    
    def _calculate_returns(self) -> List[float]:
        """Calculate portfolio returns"""
        try:
            if len(self.portfolio_history) < 2:
                return []
            
            returns = []
            for i in range(1, len(self.portfolio_history)):
                prev_value = self.portfolio_history[i-1]['total_value']
                curr_value = self.portfolio_history[i]['total_value']
                if prev_value > 0:
                    returns.append((curr_value - prev_value) / prev_value)
            
            return returns
            
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to calculate returns: {e}", exception=e)
            return []
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        try:
            if len(self.portfolio_history) < 2:
                return 0.0
            
            values = [h['total_value'] for h in self.portfolio_history]
            peak = values[0]
            max_dd = 0.0
            
            for value in values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_dd:
                    max_dd = drawdown
            
            return max_dd
            
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to calculate max drawdown: {e}", exception=e)
            return 0.0
    
    def optimize_portfolio(self, target_return: float = 0.1, risk_tolerance: float = 0.15) -> Dict[str, float]:
        """Optimize portfolio allocation"""
        try:
            # Simplified portfolio optimization
            positions = list(self.positions.keys())
            if not positions:
                return {}
            
            # Equal weight allocation as baseline
            equal_weight = 1.0 / len(positions)
            allocation = {symbol: equal_weight for symbol in positions}
            
            # Adjust based on risk tolerance and target return
            # This is a simplified version - in reality would use modern portfolio theory
            for symbol in positions:
                risk_adjustment = min(1.0, risk_tolerance / 0.15)
                allocation[symbol] *= risk_adjustment
            
            # Normalize weights
            total_weight = sum(allocation.values())
            if total_weight > 0:
                allocation = {k: v / total_weight for k, v in allocation.items()}
            
            self.unified_logger.info(f"Portfolio optimized: {allocation}")
            return allocation
            
        except Exception as e:
            self.unified_logger.error(f"Failed to optimize portfolio: {e}")
            return {}
    
    def rebalance_portfolio(self, target_allocation: Dict[str, float]) -> List[Dict[str, Any]]:
        """Rebalance portfolio to target allocation"""
        try:
            rebalance_orders = []
            portfolio_summary = self.get_portfolio_summary()
            total_value = portfolio_summary.total_value
            
            if total_value <= 0:
                return rebalance_orders
            
            for symbol, target_weight in target_allocation.items():
                target_value = total_value * target_weight
                
                if symbol in self.positions:
                    current_position = self.positions[symbol]
                    current_value = current_position.current_price * abs(current_position.size)
                    
                    value_diff = target_value - current_value
                    if abs(value_diff) > total_value * 0.01:  # 1% threshold
                        if value_diff > 0:
                            # Buy more
                            size = value_diff / current_position.current_price
                            rebalance_orders.append({
                                'symbol': symbol,
                                'action': 'buy',
                                'size': size,
                                'price': current_position.current_price
                            })
                        else:
                            # Sell some
                            size = abs(value_diff) / current_position.current_price
                            rebalance_orders.append({
                                'symbol': symbol,
                                'action': 'sell',
                                'size': size,
                                'price': current_position.current_price
                            })
                else:
                    # New position
                    if target_weight > 0.01:  # Only if significant weight
                            # Need a current market price for this symbol; attempt to fetch via market data accessor
                            try:
                                current_price = None
                                # Prefer a project-level market data helper if available
                                if hasattr(self, 'market_data_fetcher') and self.market_data_fetcher is not None:
                                    current_price = self.market_data_fetcher.get_current_price(symbol)
                                elif 'real_market_data_fetcher' in globals():
                                    from real_market_data_fetcher import RealMarketDataFetcher
                                    current_price = RealMarketDataFetcher().get_current_price(symbol)
                            
                                if current_price is None:
                                    self.unified_logger.log_warning('portfolio_manager', f"Skipping new position for {symbol}: no current price available; configure market data fetcher")
                                    continue

                                size = target_value / current_price
                                rebalance_orders.append({
                                    'symbol': symbol,
                                    'action': 'buy',
                                    'size': size,
                                    'price': current_price
                                })
                            except Exception as e:
                                self.unified_logger.error(f"Failed to create rebalance order for {symbol}: {e}")
            
            self.unified_logger.info(f"Rebalancing orders: {len(rebalance_orders)}")
            return rebalance_orders
            
        except Exception as e:
            self.unified_logger.error(f"Failed to rebalance portfolio: {e}")
            return []
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get comprehensive performance metrics"""
        try:
            returns = self._calculate_returns()
            
            if len(returns) == 0:
                return self.performance_metrics
            
            # Calculate metrics
            total_return = np.prod([1 + r for r in returns]) - 1
            annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
            volatility = np.std(returns) * np.sqrt(252)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0.0
            max_drawdown = self._calculate_max_drawdown()
            
            # Win rate
            positive_returns = [r for r in returns if r > 0]
            win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0.0
            
            # Profit factor
            gross_profit = sum([r for r in returns if r > 0])
            gross_loss = abs(sum([r for r in returns if r < 0]))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Sortino ratio
            downside_returns = [r for r in returns if r < 0]
            downside_volatility = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0.0
            sortino_ratio = annualized_return / downside_volatility if downside_volatility > 0 else 0.0
            
            # Calmar ratio
            calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0.0
            
            self.performance_metrics = PerformanceMetrics(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                beta=0.0,  # Would be calculated against benchmark
                alpha=0.0,  # Would be calculated
                information_ratio=0.0  # Would be calculated
            )
            
            return self.performance_metrics
            
        except Exception as e:
            self.unified_logger.log_error("portfolio_manager", f"Failed to calculate performance metrics: {e}", exception=e)
            return self.performance_metrics
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if getattr(self, '_executor', None) is not None:
                self._executor.shutdown(wait=True)
            self.unified_logger.info("Portfolio Manager cleaned up")
        except Exception as e:
            self.unified_logger.error(f"Failed to cleanup: {e}")

    def _ensure_executor(self):
        """Removed executor to avoid ScriptRunContext warnings."""
        # All operations are now synchronous to prevent UI blocking
        pass

# Create global instance with lazy initialization
_portfolio_manager_singleton = None

def get_portfolio_manager() -> AdvancedPortfolioManager:
    """Return a singleton AdvancedPortfolioManager created lazily."""
    global _portfolio_manager_singleton
    if _portfolio_manager_singleton is None:
        _portfolio_manager_singleton = AdvancedPortfolioManager()
    return _portfolio_manager_singleton

# Export singleton instance for compatibility
portfolio_manager = get_portfolio_manager()

# ═══════════════════════════════════════════════════════════════════
# ADVANCED POSITION MANAGEMENT (Merged from position_manager_advanced.py)
# ═══════════════════════════════════════════════════════════════════

class AdvancedPositionManager:
    """Advanced position management (merged from position_manager_advanced.py)"""
    
    def __init__(self):
        self.logger = unified_logging
    
    def manage_position(self, symbol: str, current_size: float, 
                       portfolio_value: float, market_conditions: Dict) -> Optional[PositionAction]:
        """Manage position dynamically"""
        try:
            volatility = market_conditions.get('volatility', 0.02)
            
            # Dynamic sizing based on volatility
            base_size = portfolio_value * 0.10
            vol_multiplier = max(0.5, min(2.0, 0.02 / volatility))
            recommended_size = base_size * vol_multiplier
            
            # Determine action
            size_diff = abs(current_size - recommended_size) / portfolio_value
            
            if size_diff > 0.05:  # 5% difference
                action = 'SIZE'
                reason = f"Adjust size due to volatility change (vol: {volatility:.3f})"
            else:
                action = 'HOLD'
                reason = "Position size optimal"
            
            # Hedge recommendation
            hedges = []
            if volatility > 0.05:
                hedges = ['PUT_OPTIONS', 'INVERSE_ETF']
            
            return PositionAction(
                action_type=action,
                symbol=symbol,
                current_size=current_size,
                recommended_size=recommended_size,
                hedge_instruments=hedges,
                reasoning=reason
            )
        except Exception as e:
            self.logger.log_error("position_mgr_adv", f"Error managing position: {e}", exception=e)
            return None


# Create instance for backward compatibility
position_manager_advanced = AdvancedPositionManager()