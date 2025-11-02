"""
GOD MODE 1000 - PORTFOLIO VISUALIZER
====================================
Advanced Portfolio Analytics & Visualization with Real-Time Data
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum

# Fix Python 3.13 compatibility first
from . import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from .real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None

try:
    from .portfolio_manager import portfolio_manager
except ImportError:
    portfolio_manager = None


class AssetType(Enum):
    """Asset type enumeration"""
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"


@dataclass
class PortfolioHolding:
    """Portfolio holding structure"""
    symbol: str
    asset_type: AssetType
    quantity: float
    entry_price: float
    current_price: float
    cost_basis: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    allocation_pct: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: float
    total_cost: float
    total_pnl: float
    total_pnl_pct: float
    day_pnl: float
    day_pnl_pct: float
    week_pnl: float
    week_pnl_pct: float
    month_pnl: float
    month_pnl_pct: float
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None
    portfolio_beta: float = 1.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    positions: List[Dict[str, Any]] = field(default_factory=list)
    asset_allocation: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class PortfolioVisualizer:
    """Advanced Portfolio Visualization & Analytics - God Mode 1000"""
    
    def __init__(self):
        """Initialize Portfolio Visualizer"""
        self.unified_logger = unified_logging.get_logger("portfolio_visualizer")
        self.portfolio_manager = portfolio_manager
        self.market_data_fetcher = real_market_data_fetcher
        
        # Portfolio data
        self.holdings: Dict[str, PortfolioHolding] = {}
        self.historical_values: List[Dict[str, Any]] = []
        self.transactions: List[Dict[str, Any]] = []
        
        # Performance cache
        self.performance_cache = {}
        self.cache_ttl = 30  # 30 seconds
        
        self.unified_logger.info("✅ Portfolio Visualizer initialized - God Mode 1000")
    
    def get_portfolio_summary(self) -> PortfolioMetrics:
        """Get comprehensive portfolio summary with real-time data"""
        try:
            # Update all holdings with current prices
            self._update_holdings_prices()
            
            if not self.holdings:
                return self._create_empty_metrics()
            
            # Calculate total values
            total_value = sum(h.current_value for h in self.holdings.values())
            total_cost = sum(h.cost_basis for h in self.holdings.values())
            total_pnl = sum(h.unrealized_pnl for h in self.holdings.values())
            total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
            
            # Get time-based performance
            day_metrics = self._calculate_period_performance('1d')
            week_metrics = self._calculate_period_performance('7d')
            month_metrics = self._calculate_period_performance('30d')
            
            # Find best and worst performers
            holdings_sorted = sorted(
                self.holdings.values(),
                key=lambda x: x.unrealized_pnl_pct,
                reverse=True
            )
            best_performer = holdings_sorted[0].symbol if holdings_sorted else None
            worst_performer = holdings_sorted[-1].symbol if holdings_sorted else None
            
            # Calculate risk metrics
            portfolio_beta = self._calculate_portfolio_beta()
            sharpe_ratio = self._calculate_sharpe_ratio()
            sortino_ratio = self._calculate_sortino_ratio()
            max_drawdown = self._calculate_max_drawdown()
            
            # Create positions list
            positions = [
                {
                    'symbol': h.symbol,
                    'quantity': h.quantity,
                    'entry_price': h.entry_price,
                    'current_price': h.current_price,
                    'unrealized_pnl': h.unrealized_pnl,
                    'unrealized_pnl_pct': h.unrealized_pnl_pct
                }
                for h in self.holdings.values()
            ]
            
            # Calculate asset allocation
            asset_allocation = {}
            if total_value > 0:
                for h in self.holdings.values():
                    asset_allocation[h.symbol] = (h.current_value / total_value) * 100
            
            return PortfolioMetrics(
                total_value=total_value,
                total_cost=total_cost,
                total_pnl=total_pnl,
                total_pnl_pct=total_pnl_pct,
                day_pnl=day_metrics['pnl'],
                day_pnl_pct=day_metrics['pnl_pct'],
                week_pnl=week_metrics['pnl'],
                week_pnl_pct=week_metrics['pnl_pct'],
                month_pnl=month_metrics['pnl'],
                month_pnl_pct=month_metrics['pnl_pct'],
                best_performer=best_performer,
                worst_performer=worst_performer,
                portfolio_beta=portfolio_beta,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                max_drawdown=max_drawdown,
                positions=positions,
                asset_allocation=asset_allocation
            )
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get portfolio summary: {e}")
            return self._create_empty_metrics()
    
    def get_holdings_breakdown(self) -> List[PortfolioHolding]:
        """Get detailed breakdown of all holdings"""
        try:
            self._update_holdings_prices()
            return list(self.holdings.values())
        except Exception as e:
            self.unified_logger.error(f"Failed to get holdings breakdown: {e}")
            return []
    
    def get_allocation_data(self) -> Dict[str, float]:
        """Get portfolio allocation by symbol for pie chart"""
        try:
            self._update_holdings_prices()
            
            total_value = sum(h.current_value for h in self.holdings.values())
            if total_value == 0:
                return {}
            
            allocation = {}
            for symbol, holding in self.holdings.items():
                allocation[symbol] = (holding.current_value / total_value) * 100
            
            return allocation
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get allocation data: {e}")
            return {}
    
    def get_performance_chart_data(self, days: int = 30) -> Dict[str, List]:
        """Get historical performance data for line chart"""
        try:
            # Get historical portfolio values
            if len(self.historical_values) < 2:
                # Generate from current holdings if no history
                return self._generate_performance_data(days)
            
            # Filter by date range
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            filtered_history = [
                h for h in self.historical_values
                if h['timestamp'] >= cutoff_date
            ]
            
            if not filtered_history:
                return self._generate_performance_data(days)
            
            dates = [h['timestamp'] for h in filtered_history]
            values = [h['total_value'] for h in filtered_history]
            pnl = [h['total_pnl'] for h in filtered_history]
            
            return {
                'dates': dates,
                'values': values,
                'pnl': pnl
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get performance chart data: {e}")
            return {'dates': [], 'values': [], 'pnl': []}
    
    def add_holding(self, symbol: str, quantity: float, entry_price: float,
                    asset_type: AssetType = AssetType.CRYPTO) -> bool:
        """Add new holding to portfolio"""
        try:
            # Get current price
            current_price = self._get_current_price(symbol, asset_type)
            
            cost_basis = quantity * entry_price
            current_value = quantity * current_price
            unrealized_pnl = current_value - cost_basis
            unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            holding = PortfolioHolding(
                symbol=symbol,
                asset_type=asset_type,
                quantity=quantity,
                entry_price=entry_price,
                current_price=current_price,
                cost_basis=cost_basis,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                allocation_pct=0  # Will be calculated in update
            )
            
            self.holdings[symbol] = holding
            
            # Record transaction
            self.transactions.append({
                'type': 'buy',
                'symbol': symbol,
                'quantity': quantity,
                'price': entry_price,
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Update allocations
            self._update_allocations()
            
            self.unified_logger.info(f"✅ Added holding: {symbol} - {quantity} @ ${entry_price}")
            return True
            
        except Exception as e:
            self.unified_logger.error(f"Failed to add holding: {e}")
            return False
    
    def remove_holding(self, symbol: str, quantity: Optional[float] = None) -> bool:
        """Remove holding from portfolio (full or partial)"""
        try:
            if symbol not in self.holdings:
                return False
            
            holding = self.holdings[symbol]
            
            if quantity is None or quantity >= holding.quantity:
                # Remove completely
                del self.holdings[symbol]
                self.unified_logger.info(f"✅ Removed holding: {symbol}")
            else:
                # Partial removal
                holding.quantity -= quantity
                holding.cost_basis = holding.quantity * holding.entry_price
                holding.current_value = holding.quantity * holding.current_price
                holding.unrealized_pnl = holding.current_value - holding.cost_basis
                holding.unrealized_pnl_pct = (holding.unrealized_pnl / holding.cost_basis * 100) if holding.cost_basis > 0 else 0
                self.unified_logger.info(f"✅ Reduced holding: {symbol} by {quantity}")
            
            # Record transaction
            self.transactions.append({
                'type': 'sell',
                'symbol': symbol,
                'quantity': quantity or holding.quantity,
                'price': holding.current_price,
                'timestamp': datetime.now(timezone.utc)
            })
            
            # Update allocations
            self._update_allocations()
            
            return True
            
        except Exception as e:
            self.unified_logger.error(f"Failed to remove holding: {e}")
            return False
    
    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation matrix between holdings"""
        try:
            if len(self.holdings) < 2:
                return {}
            
            symbols = list(self.holdings.keys())
            correlation_matrix = {}
            
            # Get price history for all symbols
            price_histories = {}
            for symbol in symbols:
                try:
                    # Get 30 days of price data
                    history = self._get_price_history(symbol, days=30)
                    if history:
                        price_histories[symbol] = history
                except:
                    continue
            
            # Calculate correlations
            for symbol1 in price_histories:
                correlation_matrix[symbol1] = {}
                for symbol2 in price_histories:
                    if symbol1 == symbol2:
                        correlation_matrix[symbol1][symbol2] = 1.0
                    else:
                        corr = self._calculate_correlation(
                            price_histories[symbol1],
                            price_histories[symbol2]
                        )
                        correlation_matrix[symbol1][symbol2] = corr
            
            return correlation_matrix
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate correlation matrix: {e}")
            return {}
    
    # ==================== PRIVATE METHODS ====================
    
    def _update_holdings_prices(self):
        """Update current prices for all holdings"""
        try:
            for symbol, holding in self.holdings.items():
                current_price = self._get_current_price(symbol, holding.asset_type)
                holding.current_price = current_price
                holding.current_value = holding.quantity * current_price
                holding.unrealized_pnl = holding.current_value - holding.cost_basis
                holding.unrealized_pnl_pct = (holding.unrealized_pnl / holding.cost_basis * 100) if holding.cost_basis > 0 else 0
            
            self._update_allocations()
            
        except Exception as e:
            self.unified_logger.error(f"Failed to update holdings prices: {e}")
    
    def _update_allocations(self):
        """Update allocation percentages for all holdings"""
        try:
            total_value = sum(h.current_value for h in self.holdings.values())
            if total_value > 0:
                for holding in self.holdings.values():
                    holding.allocation_pct = (holding.current_value / total_value) * 100
        except Exception as e:
            self.unified_logger.error(f"Failed to update allocations: {e}")
    
    def _get_current_price(self, symbol: str, asset_type: AssetType) -> float:
        """Get current price for symbol from market data"""
        try:
            if asset_type == AssetType.CRYPTO:
                if self.market_data_fetcher:
                    data = self.market_data_fetcher.get_current_price(symbol)
                    if data and 'price' in data:
                        return data['price']
            # Add forex and stock support later
            return 0.0
        except:
            return 0.0
    
    def _get_price_history(self, symbol: str, days: int = 30) -> List[float]:
        """Get price history for correlation calculation"""
        try:
            from .real_market_data_fetcher import real_market_data_fetcher
            
            historical_data = real_market_data_fetcher.get_ohlcv(
                symbol=symbol,
                timeframe='1d',
                limit=days
            )
            
            if historical_data and len(historical_data) > 0:
                return [d.get('close', 0) for d in historical_data]
            
            return []
        except Exception as e:
            self.logger.error(f"Failed to get price history for {symbol}: {e}")
            return []
    
    def _calculate_correlation(self, prices1: List[float], prices2: List[float]) -> float:
        """Calculate Pearson correlation between two price series"""
        try:
            if len(prices1) != len(prices2) or len(prices1) < 2:
                return 0.0
            
            n = len(prices1)
            sum1 = sum(prices1)
            sum2 = sum(prices2)
            sum1_sq = sum(p ** 2 for p in prices1)
            sum2_sq = sum(p ** 2 for p in prices2)
            sum_prod = sum(p1 * p2 for p1, p2 in zip(prices1, prices2))
            
            numerator = n * sum_prod - sum1 * sum2
            denominator = ((n * sum1_sq - sum1 ** 2) * (n * sum2_sq - sum2 ** 2)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except:
            return 0.0
    
    def _calculate_period_performance(self, period: str) -> Dict[str, float]:
        """Calculate performance for a specific period"""
        try:
            period_map = {'24h': 1, '7d': 7, '30d': 30, '1y': 365}
            days = period_map.get(period, 1)
            
            if len(self.historical_values) < days:
                return {'pnl': 0.0, 'pnl_pct': 0.0}
            
            current_value = self.historical_values[-1]['total_value'] if self.historical_values else 0
            past_value = self.historical_values[max(0, len(self.historical_values)-days)]['total_value'] if self.historical_values else 0
            
            pnl = current_value - past_value
            pnl_pct = (pnl / past_value * 100) if past_value > 0 else 0.0
            
            return {'pnl': pnl, 'pnl_pct': pnl_pct}
        except Exception as e:
            self.logger.error(f"Failed to calculate period performance: {e}")
            return {'pnl': 0.0, 'pnl_pct': 0.0}
    
    def _calculate_portfolio_beta(self) -> float:
        """Calculate portfolio beta vs BTC"""
        try:
            import numpy as np
            
            if len(self.historical_values) < 2:
                return 1.0
            
            # Get BTC price history
            btc_prices = self._get_price_history('BTC/USDT', len(self.historical_values))
            if len(btc_prices) < 2:
                return 1.0
            
            # Calculate returns
            portfolio_values = [h['total_value'] for h in self.historical_values]
            portfolio_returns = np.diff(portfolio_values) / portfolio_values[:-1]
            btc_returns = np.diff(btc_prices) / btc_prices[:-1]
            
            # Calculate beta
            covariance = np.cov(portfolio_returns, btc_returns)[0][1]
            btc_variance = np.var(btc_returns)
            
            beta = covariance / btc_variance if btc_variance > 0 else 1.0
            return float(beta)
        except Exception as e:
            self.logger.error(f"Failed to calculate portfolio beta: {e}")
            return 1.0
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        try:
            import numpy as np
            
            if len(self.historical_values) < 2:
                return 0.0
            
            portfolio_values = [h['total_value'] for h in self.historical_values]
            returns = np.diff(portfolio_values) / portfolio_values[:-1]
            
            # Annualized metrics
            avg_return = np.mean(returns) * 365
            std_return = np.std(returns) * np.sqrt(365)
            risk_free_rate = 0.02  # 2%
            
            sharpe = (avg_return - risk_free_rate) / std_return if std_return > 0 else 0.0
            return float(sharpe)
        except Exception as e:
            self.logger.error(f"Failed to calculate Sharpe ratio: {e}")
            return 0.0
    
    def _calculate_sortino_ratio(self) -> float:
        """Calculate Sortino ratio (downside risk only)"""
        try:
            import numpy as np
            
            if len(self.historical_values) < 2:
                return 0.0
            
            portfolio_values = [h['total_value'] for h in self.historical_values]
            returns = np.diff(portfolio_values) / portfolio_values[:-1]
            
            # Calculate downside deviation
            downside_returns = returns[returns < 0]
            downside_std = np.std(downside_returns) * np.sqrt(365) if len(downside_returns) > 0 else 0.001
            
            avg_return = np.mean(returns) * 365
            risk_free_rate = 0.02
            
            sortino = (avg_return - risk_free_rate) / downside_std if downside_std > 0 else 0.0
            return float(sortino)
        except Exception as e:
            self.logger.error(f"Failed to calculate Sortino ratio: {e}")
            return 0.0
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        try:
            if len(self.historical_values) < 2:
                return 0.0
            
            values = [h['total_value'] for h in self.historical_values]
            peak = values[0]
            max_dd = 0.0
            
            for value in values:
                if value > peak:
                    peak = value
                dd = (peak - value) / peak if peak > 0 else 0
                if dd > max_dd:
                    max_dd = dd
            
            return max_dd * 100  # Return as percentage
            
        except:
            return 0.0
    
    def _generate_performance_data(self, days: int) -> Dict[str, List]:
        """Generate performance data from current holdings"""
        try:
            from datetime import datetime, timedelta
            
            if len(self.historical_values) == 0:
                return {'dates': [], 'values': [], 'pnl': []}
            
            # Use actual historical data
            recent_data = self.historical_values[-days:] if len(self.historical_values) >= days else self.historical_values
            
            dates = [h['timestamp'].strftime('%Y-%m-%d') for h in recent_data]
            values = [h['total_value'] for h in recent_data]
            
            initial_value = values[0] if values else 0
            pnl = [v - initial_value for v in values]
            
            return {'dates': dates, 'values': values, 'pnl': pnl}
        except Exception as e:
            self.logger.error(f"Failed to generate performance data: {e}")
            return {'dates': [], 'values': [], 'pnl': []}
    
    def _create_empty_metrics(self) -> PortfolioMetrics:
        """Create empty metrics when no holdings"""
        return PortfolioMetrics(
            total_value=0.0,
            total_cost=0.0,
            total_pnl=0.0,
            total_pnl_pct=0.0,
            day_pnl=0.0,
            day_pnl_pct=0.0,
            week_pnl=0.0,
            week_pnl_pct=0.0,
            month_pnl=0.0,
            month_pnl_pct=0.0,
            positions=[],
            asset_allocation={}
        )


# Global instance
portfolio_visualizer = PortfolioVisualizer()

