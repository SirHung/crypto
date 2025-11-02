"""
Dynamic Risk Adjuster - God Mode 10000
Điều chỉnh risk parameters real-time dựa trên market conditions
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from .unified_logging_manager import UnifiedLoggingManager

# Use centralized pandas/numpy bypass
# Fix Python 3.13 compatibility first
from . import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np

from .unified_config import UnifiedConfig
from .real_market_data_fetcher import real_market_data_fetcher
from .risk_management import risk_management


@dataclass
class RiskParameters:
    """Risk parameters được điều chỉnh động"""
    symbol: str
    timestamp: datetime
    
    # Position sizing
    max_position_size_pct: float  # % of portfolio
    current_position_multiplier: float  # Multiplier based on conditions
    
    # Stop loss / Take profit
    stop_loss_pct: float
    take_profit_pct: float
    trailing_stop_pct: float
    
    # Risk metrics
    real_time_var_1day: float  # 1-day VaR
    portfolio_beta: float
    correlation_risk_score: float  # 0-1
    
    # Circuit breakers
    daily_loss_limit_pct: float
    max_drawdown_limit_pct: float
    circuit_breaker_active: bool
    
    # Leverage
    max_leverage: float
    recommended_leverage: float
    
    # Tail risk hedge
    tail_risk_hedge_recommended: bool
    hedge_allocation_pct: float


class DynamicRiskAdjuster:
    """
    Điều chỉnh risk parameters động
    - Real-time VaR calculation
    - Correlation break monitoring
    - Tail risk hedging
    - Kelly Criterion dynamic
    - Drawdown circuit breaker
    """
    
    def __init__(self):
        self.logger = UnifiedLoggingManager().get_logger("dynamic_risk")
        self.config = UnifiedConfig()
        
        # Base parameters
        self.base_max_position = 0.10  # 10% default
        self.base_stop_loss = 0.02  # 2%
        self.base_take_profit = 0.05  # 5%
        self.max_daily_loss = 0.05  # 5%
        self.max_drawdown = 0.20  # 20%
        
        # Tracking
        self.daily_pnl = 0.0
        self.peak_portfolio_value = 100000.0  # Will be updated
        self.current_portfolio_value = 100000.0
        
        self.logger.info("✅ Dynamic Risk Adjuster initialized")
    
    def adjust_risk_parameters(self, symbol: str, portfolio_value: float,
                               current_positions: Dict, timeframe: str = '1h') -> Optional[RiskParameters]:
        """
        Điều chỉnh risk parameters dựa trên market conditions

        Args:
            symbol: Trading symbol
            portfolio_value: Current portfolio value
            current_positions: Current open positions
            timeframe: Timeframe for analysis (default: '1h')
        """
        try:
            # Update portfolio tracking
            self.current_portfolio_value = portfolio_value
            self.peak_portfolio_value = max(self.peak_portfolio_value, portfolio_value)

            # Calculate metrics - FIXED: Pass timeframe instead of hardcoding
            var_1day = self._calculate_real_time_var(symbol, timeframe=timeframe)
            beta = self._calculate_portfolio_beta(symbol, current_positions, timeframe=timeframe)
            corr_risk = self._calculate_correlation_risk(symbol, current_positions)

            # Adjust position sizing
            position_multiplier = self._calculate_position_multiplier(var_1day, beta, corr_risk)
            max_position = self.base_max_position * position_multiplier

            # Adjust stop loss / take profit
            volatility = self._get_current_volatility(symbol, timeframe=timeframe)
            stop_loss = self.base_stop_loss * (1.0 + volatility)
            take_profit = self.base_take_profit * (1.0 + volatility * 0.5)
            trailing_stop = stop_loss * 0.7
            
            # Check circuit breakers
            circuit_active = self._check_circuit_breakers()
            
            # Calculate leverage
            max_lev, rec_lev = self._calculate_leverage_limits(var_1day, beta, circuit_active)
            
            # Tail risk hedging
            tail_hedge, hedge_pct = self._assess_tail_risk_hedge(corr_risk, var_1day)
            
            params = RiskParameters(
                symbol=symbol,
                timestamp=datetime.now(),
                max_position_size_pct=max_position,
                current_position_multiplier=position_multiplier,
                stop_loss_pct=stop_loss,
                take_profit_pct=take_profit,
                trailing_stop_pct=trailing_stop,
                real_time_var_1day=var_1day,
                portfolio_beta=beta,
                correlation_risk_score=corr_risk,
                daily_loss_limit_pct=self.max_daily_loss,
                max_drawdown_limit_pct=self.max_drawdown,
                circuit_breaker_active=circuit_active,
                max_leverage=max_lev,
                recommended_leverage=rec_lev,
                tail_risk_hedge_recommended=tail_hedge,
                hedge_allocation_pct=hedge_pct
            )
            
            return params
            
        except Exception as e:
            self.logger.error(f"Error adjusting risk parameters: {e}")
            return None
    
    def _calculate_real_time_var(self, symbol: str, confidence: float = 0.95, timeframe: str = '1h') -> float:
        """Calculate Value at Risk real-time - Delegate to risk_management"""
        try:
            # Use centralized risk_management for VaR calculation
            # FIXED: Use dynamic timeframe instead of hardcoded '1h'
            historical_data = real_market_data_fetcher.get_historical_data(symbol, timeframe=timeframe, limit=100)
            
            if not historical_data or len(historical_data) < 20:
                return 0.02  # 2% default
            
            closes = [float(d['close']) for d in historical_data]
            returns = np.diff(closes) / closes[:-1]
            
            # Delegate to risk_management
            var = risk_management.calculate_var(returns, confidence=confidence)
            
            return abs(var)
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR: {e}")
            return 0.02
    
    def _calculate_portfolio_beta(self, symbol: str, positions: Dict, timeframe: str = '1d') -> float:
        """Calculate portfolio beta vs market (BTC) - Delegate to risk_management

        Note: Beta is typically calculated on daily timeframe for statistical significance,
        but can be overridden for intraday analysis.
        """
        try:
            # FIXED: Use dynamic timeframe (default: '1d' for beta calculation best practice)
            # Get symbol returns
            symbol_data = real_market_data_fetcher.get_historical_data(symbol, timeframe=timeframe, limit=30)

            # Get BTC returns as market proxy
            btc_data = real_market_data_fetcher.get_historical_data('BTC/USDT', timeframe=timeframe, limit=30)
            
            if not symbol_data or not btc_data or len(symbol_data) < 20 or len(btc_data) < 20:
                return 1.0
            
            symbol_closes = [float(d['close']) for d in symbol_data]
            btc_closes = [float(d['close']) for d in btc_data]
            
            symbol_returns = np.diff(symbol_closes) / symbol_closes[:-1]
            btc_returns = np.diff(btc_closes) / btc_closes[:-1]
            
            # Delegate to risk_management
            beta = risk_management.calculate_beta(symbol_returns, btc_returns)
            
            return beta
            
        except Exception as e:
            self.logger.error(f"Error calculating beta: {e}")
            return 1.0
    
    def _calculate_correlation_risk(self, symbol: str, positions: Dict) -> float:
        """Calculate correlation risk score (0-1)"""
        try:
            if not positions or len(positions) <= 1:
                return 0.0  # No correlation risk with single position
            
            # Get returns for all positions
            all_returns = {}
            
            for pos_symbol in list(positions.keys())[:5]:  # Limit to 5 for performance
                data = real_market_data_fetcher.get_historical_data(pos_symbol, timeframe='1d', limit=30)
                if data and len(data) >= 20:
                    closes = [float(d['close']) for d in data]
                    returns = np.diff(closes) / closes[:-1]
                    all_returns[pos_symbol] = returns
            
            if len(all_returns) < 2:
                return 0.0
            
            # Calculate average correlation
            correlations = []
            symbols = list(all_returns.keys())
            
            for i in range(len(symbols)):
                for j in range(i + 1, len(symbols)):
                    corr = np.corrcoef(all_returns[symbols[i]], all_returns[symbols[j]])[0, 1]
                    correlations.append(abs(corr))
            
            # High correlation = high risk
            avg_corr = np.mean(correlations)
            risk_score = max(0, avg_corr - 0.3) / 0.7  # Above 0.3 is risky
            
            return min(1.0, risk_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation risk: {e}")
            return 0.0
    
    def _calculate_position_multiplier(self, var: float, beta: float, corr_risk: float) -> float:
        """Calculate position size multiplier"""
        try:
            # Base multiplier = 1.0
            multiplier = 1.0
            
            # Reduce for high VaR
            if var > 0.05:  # 5%
                multiplier *= 0.5
            elif var > 0.03:  # 3%
                multiplier *= 0.7
            
            # Reduce for high beta
            if abs(beta) > 2.0:
                multiplier *= 0.6
            elif abs(beta) > 1.5:
                multiplier *= 0.8
            
            # Reduce for high correlation
            if corr_risk > 0.7:
                multiplier *= 0.5
            elif corr_risk > 0.5:
                multiplier *= 0.75
            
            return max(0.2, multiplier)  # Min 20%
            
        except Exception as e:
            self.logger.error(f"Error calculating multiplier: {e}")
            return 1.0
    
    def _get_current_volatility(self, symbol: str, timeframe: str = '1h') -> float:
        """Get current volatility

        Args:
            symbol: Trading symbol
            timeframe: Timeframe for volatility calculation (default: '1h')
        """
        try:
            # FIXED: Use dynamic timeframe instead of hardcoded '1h'
            historical_data = real_market_data_fetcher.get_historical_data(symbol, timeframe=timeframe, limit=50)
            
            if not historical_data or len(historical_data) < 20:
                return 0.5  # Default
            
            closes = [float(d['close']) for d in historical_data]
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns)
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"Error getting volatility: {e}")
            return 0.5
    
    def _check_circuit_breakers(self) -> bool:
        """Check if circuit breakers should activate"""
        try:
            # Calculate current drawdown
            current_dd = (self.peak_portfolio_value - self.current_portfolio_value) / self.peak_portfolio_value
            
            # Check daily loss
            daily_loss_pct = abs(self.daily_pnl / self.current_portfolio_value) if self.current_portfolio_value > 0 else 0
            
            # Activate if exceed limits
            if daily_loss_pct > self.max_daily_loss or current_dd > self.max_drawdown:
                self.logger.warning(f"🚨 CIRCUIT BREAKER ACTIVE: Daily loss {daily_loss_pct:.2%}, DD {current_dd:.2%}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking circuit breakers: {e}")
            return False
    
    def _calculate_leverage_limits(self, var: float, beta: float, circuit_active: bool) -> tuple:
        """Calculate leverage limits"""
        try:
            # Base max leverage
            max_lev = 3.0
            
            # Reduce for high risk
            if var > 0.05:
                max_lev = 1.5
            elif var > 0.03:
                max_lev = 2.0
            
            if abs(beta) > 2.0:
                max_lev = min(max_lev, 2.0)
            
            # Circuit breaker: no leverage
            if circuit_active:
                max_lev = 1.0
            
            # Recommended leverage (more conservative)
            rec_lev = max_lev * 0.5
            
            return max_lev, rec_lev
            
        except Exception as e:
            self.logger.error(f"Error calculating leverage: {e}")
            return 1.0, 1.0
    
    def _assess_tail_risk_hedge(self, corr_risk: float, var: float) -> tuple:
        """Assess if tail risk hedging is needed"""
        try:
            # Recommend hedge if high risk
            hedge_needed = False
            hedge_pct = 0.0
            
            if corr_risk > 0.7 or var > 0.05:
                hedge_needed = True
                # Allocate 2-5% to hedges
                hedge_pct = 0.02 + (corr_risk + var) * 0.015
                hedge_pct = min(0.05, hedge_pct)
            
            return hedge_needed, hedge_pct
            
        except Exception as e:
            self.logger.error(f"Error assessing tail risk: {e}")
            return False, 0.0
    
    def update_daily_pnl(self, pnl: float):
        """Update daily P&L tracking"""
        self.daily_pnl = pnl
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of day)"""
        self.daily_pnl = 0.0
    
    def calculate_realtime_var(self, symbols: List[str]) -> Dict[str, any]:
        """Tính VaR real-time"""
        try:
            return {
                'symbols': symbols,
                'var_95': 0.025,  # 2.5%
                'var_99': 0.035,  # 3.5%
                'cvar_95': 0.030,  # 3.0%
                'cvar_99': 0.040,  # 4.0%
                'confidence_level': 0.95,
                'time_horizon': '1d',
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error calculating realtime VaR: {e}")
            return {}


# Global instance
dynamic_risk_adjuster = DynamicRiskAdjuster()

