"""
Complete Copy Trading System - God Mode 10000
Auto-copy signals với risk management
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from .unified_logging_manager import UnifiedLoggingManager


@dataclass
class CopyTradeConfig:
    """Config cho copy trading"""
    trader_id: str
    copy_percentage: float  # % of capital to allocate
    max_position_size: float
    stop_loss_override: Optional[float]
    take_profit_override: Optional[float]
    max_daily_loss: float
    enabled: bool


class CopyTradingSystem:
    """Complete copy trading system"""
    
    def __init__(self):
        self.logger = UnifiedLoggingManager().get_logger("copy_trading_system")
        self.active_copies: Dict[str, CopyTradeConfig] = {}
        self.logger.info("✅ Copy Trading System initialized")
    
    def enable_copy_trading(self, config: CopyTradeConfig) -> bool:
        """Enable copy trading for a trader"""
        try:
            self.active_copies[config.trader_id] = config
            self.logger.info(f"✅ Copy trading enabled for trader {config.trader_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error enabling copy trading: {e}")
            return False
    
    def process_signal(self, trader_id: str, signal: Dict) -> Optional[Dict]:
        """Process a signal from copied trader with risk management"""
        try:
            if trader_id not in self.active_copies:
                return None
            
            config = self.active_copies[trader_id]
            
            if not config.enabled:
                return None
            
            # Apply risk management
            position_size = min(
                signal.get('position_size', 0) * config.copy_percentage,
                config.max_position_size
            )
            
            # Override SL/TP if configured
            stop_loss = config.stop_loss_override or signal.get('stop_loss')
            take_profit = config.take_profit_override or signal.get('take_profit')
            
            adjusted_signal = {
                'symbol': signal['symbol'],
                'side': signal['side'],
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'source': f'copy_{trader_id}'
            }
            
            return adjusted_signal
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}")
            return None


copy_trading_system = CopyTradingSystem()

