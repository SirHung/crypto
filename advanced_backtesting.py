"""
GOD MODE 1000 - ADVANCED BACKTESTING ENGINE
=========================================
Advanced Backtesting Engine with AI Integration
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Import unified components
try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None

try:
    from ai_integration_manager import ai_integration_manager
except ImportError:
    ai_integration_manager = None

class BacktestStatus(Enum):
    """Backtest status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BacktestConfig:
    """Backtest configuration - NO HARDCODED timeframe"""
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005   # 0.05%
    strategy: str = "trend_following"
    timeframe: str = None  # Must be provided by user - no defaults
    ai_enabled: bool = True
    
    def __post_init__(self):
        """Validate required fields"""
        if self.timeframe is None or self.timeframe == "":
            raise ValueError("timeframe must be provided - cannot use default values")

@dataclass
class BacktestResult:
    """Backtest result structure"""
    config: BacktestConfig
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float
    start_date: datetime
    end_date: datetime
    duration_days: int
    trades: List[Dict[str, Any]] = field(default_factory=list)
    equity_curve: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class AdvancedBacktestingEngine:
    """Advanced Backtesting Engine with AI Integration"""
    
    def __init__(self):
        """Initialize Advanced Backtesting Engine"""
        self.unified_logger = unified_logging.get_logger("advanced_backtesting")
        
        # Backtest state
        self.current_backtest = None
        self.backtest_results = []
        
        # AI integration
        self.ai_enabled = ai_integration_manager is not None
        self.market_data_enabled = real_market_data_fetcher is not None
        
        self.unified_logger.info( "Advanced Backtesting Engine initialized")
    
    async def run_backtest(self, config: BacktestConfig) -> BacktestResult:
        """Run comprehensive backtest"""
        try:
            self.unified_logger.info( f"Starting backtest for {config.symbol}")
            
            # Initialize backtest
            self.current_backtest = {
                'config': config,
                'status': BacktestStatus.RUNNING,
                'start_time': datetime.now()
            }
            
            # Get historical data
            historical_data = await self._get_historical_data(config)
            
            if not historical_data:
                raise Exception("No historical data available")
            
            # Execute backtest by replaying REAL historical data
            result = await self._replay_historical_trading(config, historical_data)
            
            # Calculate performance metrics
            result = self._calculate_performance_metrics(result)
            
            # Store result
            self.backtest_results.append(result)
            
            self.unified_logger.info( f"Backtest completed for {config.symbol}")
            return result
            
        except Exception as e:
            self.unified_logger.error( f"Backtest failed: {e}")
            return self._create_error_result(config, str(e))
    
    async def _get_historical_data(self, config: BacktestConfig) -> List[Dict[str, Any]]:
        """Get historical data for backtesting"""
        try:
            if self.market_data_enabled and real_market_data_fetcher:
                # Get historical data from market data fetcher
                historical_data = real_market_data_fetcher.get_historical_data(
                    config.symbol, 
                    config.timeframe, 
                    limit=1000
                )
                
                if historical_data:
                    return historical_data
            
            # NO FALLBACK - Cannot backtest without REAL market data
            self.unified_logger.error(f"No REAL market data available for {config.symbol}")
            return []  # Return empty - NO SYNTHETIC DATA
            
        except Exception as e:
            self.unified_logger.error(f"❌ CRITICAL: Failed to get REAL historical data: {e}")
            raise ValueError(f"Cannot perform backtesting without REAL market data: {e}")
    
    # REMOVED: _generate_synthetic_data() - NO SYNTHETIC DATA ALLOWED
    # All backtesting data must come from REAL market sources only
    
    async def _replay_historical_trading(self, config: BacktestConfig, historical_data: List[Dict[str, Any]]) -> BacktestResult:
        """Replay strategy execution with REAL historical market data (NOT simulation - actual data replay)"""
        try:
            # Initialize trading simulation
            capital = config.initial_capital
            position = 0.0
            position_value = 0.0
            trades = []
            equity_curve = []
            
            # Process each data point
            for i, data_point in enumerate(historical_data):
                current_price = data_point['close']
                current_date = data_point['timestamp']
                
                # Get AI signal if enabled
                signal = None
                if self.ai_enabled and ai_integration_manager:
                    try:
                        # Create market data for AI
                        market_data = {
                            'price': current_price,
                            'volume': data_point['volume'],
                            'high': data_point['high'],
                            'low': data_point['low'],
                            'open': data_point['open']
                        }
                        
                        # Get AI prediction (synchronous call)
                        prediction = ai_integration_manager.get_ensemble_prediction(config.symbol, market_data)
                        
                        if prediction and prediction.confidence > 0.7:
                            signal = {
                                'action': prediction.final_prediction,
                                'confidence': prediction.confidence,
                                'price_target': prediction.price_target,
                                'stop_loss': prediction.stop_loss,
                                'take_profit': prediction.take_profit
                            }
                    except Exception as e:
                        self.unified_logger.warning( f"AI signal failed: {e}")
                
                # Execute trading logic
                if signal:
                    if signal['action'] == 'BUY' and position <= 0:
                        # Execute buy
                        trade_size = capital * 0.1  # 10% of capital per trade
                        shares = trade_size / current_price
                        
                        # Apply commission
                        commission = trade_size * config.commission
                        net_shares = shares * (1 - config.commission)
                        
                        position += net_shares
                        capital -= trade_size
                        
                        trades.append({
                            'timestamp': current_date,
                            'action': 'BUY',
                            'price': current_price,
                            'shares': net_shares,
                            'value': trade_size,
                            'commission': commission,
                            'confidence': signal['confidence']
                        })
                        
                    elif signal['action'] == 'SELL' and position > 0:
                        # Execute sell
                        trade_value = position * current_price
                        
                        # Apply commission
                        commission = trade_value * config.commission
                        net_value = trade_value * (1 - config.commission)
                        
                        capital += net_value
                        
                        trades.append({
                            'timestamp': current_date,
                            'action': 'SELL',
                            'price': current_price,
                            'shares': position,
                            'value': net_value,
                            'commission': commission,
                            'confidence': signal['confidence']
                        })
                        
                        position = 0.0
                
                # Calculate current equity
                position_value = position * current_price
                total_equity = capital + position_value
                
                equity_curve.append({
                    'timestamp': current_date,
                    'equity': total_equity,
                    'capital': capital,
                    'position_value': position_value,
                    'price': current_price
                })
            
            # Close any remaining position
            if position > 0:
                final_price = historical_data[-1]['close']
                final_value = position * final_price * (1 - config.commission)
                capital += final_value
                
                trades.append({
                    'timestamp': historical_data[-1]['timestamp'],
                    'action': 'SELL',
                    'price': final_price,
                    'shares': position,
                    'value': final_value,
                    'commission': position * final_price * config.commission,
                    'confidence': 1.0
                })
            
            # Create result
            result = BacktestResult(
                config=config,
                total_return=0.0,  # Will be calculated
                annual_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                total_trades=len(trades),
                winning_trades=0,
                losing_trades=0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                start_date=config.start_date,
                end_date=config.end_date,
                duration_days=(config.end_date - config.start_date).days,
                trades=trades,
                equity_curve=equity_curve
            )
            
            return result
            
        except Exception as e:
            self.unified_logger.error( f"Trading simulation failed: {e}")
            return self._create_error_result(config, str(e))
    
    def _calculate_performance_metrics(self, result: BacktestResult) -> BacktestResult:
        """Calculate comprehensive performance metrics with enhanced analysis"""
        try:
            if not result.equity_curve:
                return result
            
            # Calculate total return
            initial_equity = result.equity_curve[0]['equity']
            final_equity = result.equity_curve[-1]['equity']
            result.total_return = (final_equity - initial_equity) / initial_equity
            
            # Calculate annual return
            years = result.duration_days / 365.25
            result.annual_return = (1 + result.total_return) ** (1 / years) - 1 if years > 0 else 0
            
            # Calculate trades statistics with enhanced analysis
            if result.trades:
                # Separate buy and sell trades
                buy_trades = [t for t in result.trades if t['action'] == 'BUY']
                sell_trades = [t for t in result.trades if t['action'] == 'SELL']
                
                # Calculate P&L for each trade with enhanced tracking
                trade_pnl = []
                trade_durations = []
                
                for i in range(min(len(buy_trades), len(sell_trades))):
                    buy_trade = buy_trades[i]
                    sell_trade = sell_trades[i]
                    
                    pnl = sell_trade['value'] - buy_trade['value']
                    trade_pnl.append(pnl)
                    
                    # Calculate trade duration
                    duration = (sell_trade['timestamp'] - buy_trade['timestamp']).total_seconds() / 3600  # hours
                    trade_durations.append(duration)
                
                # Calculate win/loss statistics
                winning_trades = [pnl for pnl in trade_pnl if pnl > 0]
                losing_trades = [pnl for pnl in trade_pnl if pnl < 0]
                
                result.winning_trades = len(winning_trades)
                result.losing_trades = len(losing_trades)
                result.win_rate = len(winning_trades) / len(trade_pnl) * 100 if trade_pnl else 0
                
                result.avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0
                result.avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0
                
                # Calculate profit factor
                total_wins = sum(winning_trades) if winning_trades else 0
                total_losses = abs(sum(losing_trades)) if losing_trades else 0
                result.profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
                
                # Enhanced trade analysis
                avg_trade_duration = sum(trade_durations) / len(trade_durations) if trade_durations else 0
                max_win = max(winning_trades) if winning_trades else 0
                max_loss = min(losing_trades) if losing_trades else 0
                
                # Add to performance metrics
                result.performance_metrics.update({
                    'avg_trade_duration_hours': avg_trade_duration,
                    'max_win': max_win,
                    'max_loss': max_loss,
                    'win_loss_ratio': abs(max_win / max_loss) if max_loss != 0 else float('inf'),
                    'consecutive_wins': self._calculate_consecutive_wins(trade_pnl),
                    'consecutive_losses': self._calculate_consecutive_losses(trade_pnl)
                })
            
            # Calculate maximum drawdown with enhanced tracking
            peak = initial_equity
            max_dd = 0.0
            drawdown_duration = 0
            max_drawdown_duration = 0
            
            for point in result.equity_curve:
                if point['equity'] > peak:
                    peak = point['equity']
                    drawdown_duration = 0
                else:
                    drawdown_duration += 1
                
                drawdown = (peak - point['equity']) / peak
                if drawdown > max_dd:
                    max_dd = drawdown
                    max_drawdown_duration = drawdown_duration
            
            result.max_drawdown = max_dd
            
            # Calculate Sharpe ratio with enhanced risk metrics
            if len(result.equity_curve) > 1:
                returns = []
                for i in range(1, len(result.equity_curve)):
                    prev_equity = result.equity_curve[i-1]['equity']
                    curr_equity = result.equity_curve[i]['equity']
                    daily_return = (curr_equity - prev_equity) / prev_equity
                    returns.append(daily_return)
                
                if returns:
                    avg_return = sum(returns) / len(returns)
                    return_std = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
                    result.sharpe_ratio = avg_return / return_std if return_std > 0 else 0
                    
                    # Enhanced risk metrics
                    downside_returns = [r for r in returns if r < 0]
                    downside_std = (sum(r ** 2 for r in downside_returns) / len(downside_returns)) ** 0.5 if downside_returns else 0
                    
                    result.performance_metrics.update({
                        'downside_deviation': downside_std,
                        'upside_capture': self._calculate_upside_capture(returns),
                        'downside_capture': self._calculate_downside_capture(returns)
                    })
            
            # Additional performance metrics
            result.performance_metrics.update({
                'volatility': self._calculate_volatility(result.equity_curve),
                'sortino_ratio': self._calculate_sortino_ratio(result.equity_curve),
                'calmar_ratio': result.annual_return / result.max_drawdown if result.max_drawdown > 0 else 0,
                'recovery_factor': result.total_return / result.max_drawdown if result.max_drawdown > 0 else 0,
                'max_drawdown_duration': max_drawdown_duration,
                'var_95': self._calculate_var(returns, 0.95) if returns else 0,
                'var_99': self._calculate_var(returns, 0.99) if returns else 0
            })
            
            return result
            
        except Exception as e:
            self.unified_logger.error( f"Failed to calculate performance metrics: {e}")
            return result
    
    def _calculate_volatility(self, equity_curve: List[Dict[str, Any]]) -> float:
        """Calculate volatility"""
        try:
            if len(equity_curve) < 2:
                return 0.0
            
            returns = []
            for i in range(1, len(equity_curve)):
                prev_equity = equity_curve[i-1]['equity']
                curr_equity = equity_curve[i]['equity']
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(daily_return)
            
            if not returns:
                return 0.0
            
            avg_return = sum(returns) / len(returns)
            variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
            return variance ** 0.5
            
        except Exception:
            return 0.0
    
    def _calculate_sortino_ratio(self, equity_curve: List[Dict[str, Any]]) -> float:
        """Calculate Sortino ratio"""
        try:
            if len(equity_curve) < 2:
                return 0.0
            
            returns = []
            for i in range(1, len(equity_curve)):
                prev_equity = equity_curve[i-1]['equity']
                curr_equity = equity_curve[i]['equity']
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(daily_return)
            
            if not returns:
                return 0.0
            
            avg_return = sum(returns) / len(returns)
            negative_returns = [r for r in returns if r < 0]
            
            if not negative_returns:
                return float('inf')
            
            downside_deviation = (sum(r ** 2 for r in negative_returns) / len(negative_returns)) ** 0.5
            return avg_return / downside_deviation if downside_deviation > 0 else 0
            
        except Exception:
            return 0.0
    
    def _calculate_consecutive_wins(self, trade_pnl: List[float]) -> int:
        """Calculate maximum consecutive wins"""
        try:
            max_consecutive = 0
            current_consecutive = 0
            
            for pnl in trade_pnl:
                if pnl > 0:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
        except Exception:
            return 0
    
    def _calculate_consecutive_losses(self, trade_pnl: List[float]) -> int:
        """Calculate maximum consecutive losses"""
        try:
            max_consecutive = 0
            current_consecutive = 0
            
            for pnl in trade_pnl:
                if pnl < 0:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
        except Exception:
            return 0
    
    def _calculate_upside_capture(self, returns: List[float]) -> float:
        """Calculate upside capture ratio"""
        try:
            if not returns:
                return 0.0
            
            positive_returns = [r for r in returns if r > 0]
            if not positive_returns:
                return 0.0
            
            avg_positive = sum(positive_returns) / len(positive_returns)
            avg_return = sum(returns) / len(returns)
            
            return avg_positive / avg_return if avg_return > 0 else 0.0
        except Exception:
            return 0.0
    
    def _calculate_downside_capture(self, returns: List[float]) -> float:
        """Calculate downside capture ratio"""
        try:
            if not returns:
                return 0.0
            
            negative_returns = [r for r in returns if r < 0]
            if not negative_returns:
                return 0.0
            
            avg_negative = sum(negative_returns) / len(negative_returns)
            avg_return = sum(returns) / len(returns)
            
            return abs(avg_negative / avg_return) if avg_return < 0 else 0.0
        except Exception:
            return 0.0
    
    def _calculate_var(self, returns: List[float], confidence_level: float) -> float:
        """Calculate Value at Risk (VaR)"""
        try:
            if not returns:
                return 0.0
            
            sorted_returns = sorted(returns)
            index = int((1 - confidence_level) * len(sorted_returns))
            return sorted_returns[index] if index < len(sorted_returns) else sorted_returns[0]
        except Exception:
            return 0.0
    
    def _create_error_result(self, config: BacktestConfig, error_message: str) -> BacktestResult:
        """Create error result"""
        return BacktestResult(
            config=config,
            total_return=0.0,
            annual_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            start_date=config.start_date,
            end_date=config.end_date,
            duration_days=(config.end_date - config.start_date).days,
            performance_metrics={'error': error_message}
        )
    
    def get_backtest_results(self) -> List[BacktestResult]:
        """Get all backtest results"""
        return self.backtest_results
    
    def get_latest_backtest(self) -> Optional[BacktestResult]:
        """Get latest backtest result"""
        return self.backtest_results[-1] if self.backtest_results else None

# Create global instance
advanced_backtesting_engine = AdvancedBacktestingEngine()
