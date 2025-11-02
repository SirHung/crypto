"""
GOD MODE 1000 - DCA BOT
=======================
Dollar Cost Averaging Bot with Smart Entry & Real Market Data
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum

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
    from .portfolio_visualizer import portfolio_visualizer, AssetType
except ImportError:
    portfolio_visualizer = None
    AssetType = None


class DCAFrequency(Enum):
    """DCA frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class DCAStrategy(Enum):
    """DCA strategy types"""
    FIXED = "fixed"  # Fixed amount regardless of price
    SMART = "smart"  # Buy more when price drops
    TREND = "trend"  # Follow trend (buy dips in uptrend)


@dataclass
class DCAConfig:
    """DCA configuration"""
    symbol: str
    amount_per_order: float
    frequency: DCAFrequency
    strategy: DCAStrategy
    max_total_investment: float
    min_price_drop_pct: float = 0.0  # For smart DCA
    stop_on_profit_pct: float = 0.0  # Stop if profit reaches X%
    active: bool = True
    asset_type: str = "crypto"


@dataclass
class DCAOrder:
    """DCA order record"""
    symbol: str
    price: float
    quantity: float
    amount: float
    timestamp: datetime
    strategy_used: str
    reason: str


class DCABot:
    """Dollar Cost Averaging Bot - God Mode 1000"""
    
    def __init__(self):
        """Initialize DCA Bot"""
        self.unified_logger = unified_logging.get_logger("dca_bot")
        self.market_data_fetcher = real_market_data_fetcher
        self.portfolio_visualizer = portfolio_visualizer
        
        # DCA configurations
        self.dca_configs: Dict[str, DCAConfig] = {}
        self.dca_history: List[DCAOrder] = []
        self.next_execution_times: Dict[str, datetime] = {}
        
        # Bot state
        self.is_running = False
        self.last_check_time = datetime.now(timezone.utc)
        
        self.unified_logger.info("✅ DCA Bot initialized - God Mode 1000")
    
    def add_dca_plan(self, config: DCAConfig) -> bool:
        """Add new DCA plan"""
        try:
            self.dca_configs[config.symbol] = config
            self._schedule_next_execution(config.symbol)
            self.unified_logger.info(f"✅ Added DCA plan for {config.symbol}: ${config.amount_per_order} {config.frequency.value}")
            return True
        except Exception as e:
            self.unified_logger.error(f"Failed to add DCA plan: {e}")
            return False
    
    def remove_dca_plan(self, symbol: str) -> bool:
        """Remove DCA plan"""
        try:
            if symbol in self.dca_configs:
                del self.dca_configs[symbol]
                if symbol in self.next_execution_times:
                    del self.next_execution_times[symbol]
                self.unified_logger.info(f"✅ Removed DCA plan for {symbol}")
                return True
            return False
        except Exception as e:
            self.unified_logger.error(f"Failed to remove DCA plan: {e}")
            return False
    
    def start_bot(self) -> bool:
        """Start DCA bot"""
        try:
            self.is_running = True
            self.unified_logger.info("✅ DCA Bot started")
            return True
        except Exception as e:
            self.unified_logger.error(f"Failed to start DCA bot: {e}")
            return False
    
    def stop_bot(self) -> bool:
        """Stop DCA bot"""
        try:
            self.is_running = False
            self.unified_logger.info("⏹️ DCA Bot stopped")
            return True
        except Exception as e:
            self.unified_logger.error(f"Failed to stop DCA bot: {e}")
            return False
    
    def check_and_execute(self) -> List[DCAOrder]:
        """Check all DCA plans and execute if needed"""
        executed_orders = []
        
        if not self.is_running:
            return executed_orders
        
        try:
            current_time = datetime.now(timezone.utc)
            
            for symbol, config in self.dca_configs.items():
                if not config.active:
                    continue
                
                # Check if it's time to execute
                if symbol not in self.next_execution_times:
                    self._schedule_next_execution(symbol)
                    continue
                
                next_time = self.next_execution_times[symbol]
                if current_time >= next_time:
                    # Execute DCA order
                    order = self._execute_dca_order(config)
                    if order:
                        executed_orders.append(order)
                        self.dca_history.append(order)
                    
                    # Schedule next execution
                    self._schedule_next_execution(symbol)
            
            self.last_check_time = current_time
            
        except Exception as e:
            self.unified_logger.error(f"Error in DCA execution check: {e}")
        
        return executed_orders
    
    def get_dca_summary(self) -> Dict[str, Any]:
        """Get DCA bot summary"""
        try:
            total_invested = sum(order.amount for order in self.dca_history)
            total_orders = len(self.dca_history)
            active_plans = sum(1 for c in self.dca_configs.values() if c.active)
            
            # Calculate P&L per symbol
            pnl_by_symbol = {}
            for symbol in self.dca_configs.keys():
                symbol_orders = [o for o in self.dca_history if o.symbol == symbol]
                if symbol_orders:
                    total_cost = sum(o.amount for o in symbol_orders)
                    total_quantity = sum(o.quantity for o in symbol_orders)
                    avg_price = total_cost / total_quantity if total_quantity > 0 else 0
                    
                    # Get current price
                    current_price = self._get_current_price(symbol)
                    current_value = total_quantity * current_price
                    pnl = current_value - total_cost
                    pnl_pct = (pnl / total_cost * 100) if total_cost > 0 else 0
                    
                    pnl_by_symbol[symbol] = {
                        'total_cost': total_cost,
                        'total_quantity': total_quantity,
                        'avg_price': avg_price,
                        'current_price': current_price,
                        'current_value': current_value,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'orders_count': len(symbol_orders)
                    }
            
            return {
                'is_running': self.is_running,
                'active_plans': active_plans,
                'total_plans': len(self.dca_configs),
                'total_invested': total_invested,
                'total_orders': total_orders,
                'pnl_by_symbol': pnl_by_symbol,
                'last_check': self.last_check_time
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to get DCA summary: {e}")
            return {
                'is_running': self.is_running,
                'active_plans': 0,
                'total_plans': 0,
                'total_invested': 0,
                'total_orders': 0,
                'pnl_by_symbol': {},
                'last_check': datetime.now(timezone.utc)
            }
    
    def get_next_executions(self) -> Dict[str, datetime]:
        """Get next execution times for all plans"""
        return self.next_execution_times.copy()
    
    def get_order_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[DCAOrder]:
        """Get DCA order history"""
        try:
            history = self.dca_history
            if symbol:
                history = [o for o in history if o.symbol == symbol]
            
            # Return most recent first
            return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
        except Exception as e:
            self.unified_logger.error(f"Failed to get order history: {e}")
            return []
    
    # ==================== PRIVATE METHODS ====================
    
    def _execute_dca_order(self, config: DCAConfig) -> Optional[DCAOrder]:
        """Execute a DCA order"""
        try:
            # Get current price
            current_price = self._get_current_price(config.symbol)
            if current_price == 0:
                self.unified_logger.warning(f"Cannot execute DCA for {config.symbol}: price unavailable")
                return None
            
            # Determine order amount based on strategy
            order_amount = self._calculate_order_amount(config, current_price)
            
            if order_amount == 0:
                self.unified_logger.info(f"Skipping DCA for {config.symbol}: conditions not met")
                return None
            
            # Calculate quantity
            quantity = order_amount / current_price
            
            # Create order record
            order = DCAOrder(
                symbol=config.symbol,
                price=current_price,
                quantity=quantity,
                amount=order_amount,
                timestamp=datetime.now(timezone.utc),
                strategy_used=config.strategy.value,
                reason=self._get_execution_reason(config, current_price)
            )
            
            # Add to portfolio if portfolio visualizer available
            if self.portfolio_visualizer:
                asset_type = AssetType.CRYPTO if config.asset_type == "crypto" else AssetType.FOREX
                self.portfolio_visualizer.add_holding(
                    config.symbol,
                    quantity,
                    current_price,
                    asset_type
                )
            
            self.unified_logger.info(f"✅ Executed DCA order: {config.symbol} {quantity:.8f} @ ${current_price:.2f}")
            return order
            
        except Exception as e:
            self.unified_logger.error(f"Failed to execute DCA order: {e}")
            return None
    
    def _calculate_order_amount(self, config: DCAConfig, current_price: float) -> float:
        """Calculate order amount based on strategy"""
        try:
            if config.strategy == DCAStrategy.FIXED:
                return config.amount_per_order
            
            elif config.strategy == DCAStrategy.SMART:
                # Smart DCA: Buy more when price drops
                avg_price = self._get_average_entry_price(config.symbol)
                if avg_price == 0:
                    return config.amount_per_order
                
                price_drop_pct = ((avg_price - current_price) / avg_price) * 100
                
                if price_drop_pct >= config.min_price_drop_pct:
                    # Price dropped enough, buy more
                    multiplier = 1 + (price_drop_pct / 100)  # 5% drop = 1.05x
                    return config.amount_per_order * min(multiplier, 3.0)  # Max 3x
                else:
                    # Price hasn't dropped enough, regular amount
                    return config.amount_per_order
            
            elif config.strategy == DCAStrategy.TREND:
                # Trend DCA: Buy dips in uptrend - use real trend analysis
                try:
                    # Get market data to determine trend
                    from .real_market_data_fetcher import real_market_data_fetcher
                    market_data = real_market_data_fetcher.get_market_data(config.symbol)
                    
                    if market_data:
                        # Calculate trend from price change
                        price_change = market_data.get('change_24h', 0)
                        
                        # Uptrend: increase buy amount on dips
                        if price_change > 0:
                            # Buy more on dips in uptrend
                            avg_price = sum(order.price for order in self.dca_orders[:10]) / min(len(self.dca_orders), 10) if self.dca_orders else current_price
                            if current_price < avg_price * 0.98:  # 2% below average
                                return config.amount_per_order * 1.5
                        # Downtrend: reduce buy amount
                        elif price_change < -5:
                            return config.amount_per_order * 0.5
                except Exception:
                    pass
                
                return config.amount_per_order
            
            return config.amount_per_order
            
        except Exception as e:
            self.unified_logger.error(f"Failed to calculate order amount: {e}")
            return config.amount_per_order
    
    def _get_execution_reason(self, config: DCAConfig, current_price: float) -> str:
        """Get reason for execution"""
        try:
            if config.strategy == DCAStrategy.FIXED:
                return f"Fixed schedule: {config.frequency.value}"
            elif config.strategy == DCAStrategy.SMART:
                avg_price = self._get_average_entry_price(config.symbol)
                if avg_price > 0:
                    price_drop = ((avg_price - current_price) / avg_price) * 100
                    return f"Smart DCA: {price_drop:.2f}% below average"
                return "Smart DCA: Initial order"
            return f"Scheduled {config.frequency.value} order"
        except:
            return "Scheduled order"
    
    def _schedule_next_execution(self, symbol: str):
        """Schedule next execution time"""
        try:
            if symbol not in self.dca_configs:
                return
            
            config = self.dca_configs[symbol]
            current_time = datetime.now(timezone.utc)
            
            # Calculate next execution time based on frequency
            if config.frequency == DCAFrequency.HOURLY:
                next_time = current_time + timedelta(hours=1)
            elif config.frequency == DCAFrequency.DAILY:
                next_time = current_time + timedelta(days=1)
            elif config.frequency == DCAFrequency.WEEKLY:
                next_time = current_time + timedelta(weeks=1)
            elif config.frequency == DCAFrequency.BIWEEKLY:
                next_time = current_time + timedelta(weeks=2)
            elif config.frequency == DCAFrequency.MONTHLY:
                next_time = current_time + timedelta(days=30)
            else:
                next_time = current_time + timedelta(days=1)
            
            self.next_execution_times[symbol] = next_time
            
        except Exception as e:
            self.unified_logger.error(f"Failed to schedule next execution: {e}")
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price from market data"""
        try:
            if self.market_data_fetcher:
                data = self.market_data_fetcher.get_current_price(symbol)
                if data and 'price' in data:
                    return data['price']
            return 0.0
        except:
            return 0.0
    
    def _get_average_entry_price(self, symbol: str) -> float:
        """Get average entry price for symbol"""
        try:
            symbol_orders = [o for o in self.dca_history if o.symbol == symbol]
            if not symbol_orders:
                return 0.0
            
            total_cost = sum(o.amount for o in symbol_orders)
            total_quantity = sum(o.quantity for o in symbol_orders)
            
            return total_cost / total_quantity if total_quantity > 0 else 0.0
        except:
            return 0.0


# Global instance
dca_bot = DCABot()

