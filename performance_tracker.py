"""
GOD MODE 10000 - PERFORMANCE TRACKER
====================================
Real-time Performance Tracking & Feedback Loop for Model Improvement
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from collections import deque
import json
from pathlib import Path

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging

# Use centralized pandas/numpy bypass
# Fix Python 3.13 compatibility first
import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np



@dataclass
class PredictionRecord:
    """Record of a prediction"""
    id: str
    symbol: str
    signal: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    predicted_at: datetime
    sources: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeResult:
    """Result of a trade"""
    prediction_id: str
    symbol: str
    entry_price: float
    exit_price: float
    pnl: float
    pnl_pct: float
    duration_hours: float
    outcome: str  # 'win', 'loss', 'breakeven'
    hit_target: str  # 'tp', 'sl', 'manual'
    executed_at: datetime
    closed_at: datetime


@dataclass
class PerformanceMetrics:
    """Overall performance metrics"""
    total_predictions: int
    total_trades: int
    win_rate: float
    avg_pnl_pct: float
    sharpe_ratio: float
    max_drawdown: float
    prediction_accuracy: float
    avg_confidence: float
    best_timeframe: str
    best_market_regime: str
    roi: float


class PerformanceTracker:
    """Performance Tracker - GOD MODE 10000"""
    
    def __init__(self):
        """Initialize Performance Tracker"""
        self.unified_logger = unified_logging.get_logger("performance_tracker")
        
        # Storage
        self.predictions: Dict[str, PredictionRecord] = {}
        self.trade_results: List[TradeResult] = []
        
        # Recent history for quick access
        self.recent_predictions = deque(maxlen=1000)
        self.recent_trades = deque(maxlen=500)
        
        # Performance cache
        self.metrics_cache = None
        self.cache_timestamp = None
        self.cache_ttl = 300  # 5 minutes
        
        # Data directory
    
    def analyze_performance(self, symbol: str) -> Dict[str, Any]:
        """Analyze performance for prediction - GOD MODE 10000"""
        try:
            # Get recent predictions for this symbol
            recent_preds = [p for p in self.recent_predictions if p.symbol == symbol]
            
            if not recent_preds:
                return {
                    'performance_score': 0.5,
                    'confidence': 0.4,
                    'total_predictions': 0
                }
            
            # Calculate accuracy
            correct = sum(1 for p in recent_preds if p.was_correct)
            total = len(recent_preds)
            accuracy = correct / total if total > 0 else 0.5
            
            # Performance score based on accuracy
            performance_score = accuracy
            
            return {
                'performance_score': performance_score,
                'confidence': min(0.9, 0.5 + (total / 100) * 0.4),  # More predictions = higher confidence
                'total_predictions': total,
                'accuracy': accuracy
            }
            
        except Exception as e:
            self.unified_logger.error(f"Performance analysis error: {e}")
            return {
                'performance_score': 0.5,
                'confidence': 0.3,
                'total_predictions': 0
            }
        self.data_dir = Path("data/performance")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load historical data
        self._load_historical_data()
        
        self.unified_logger.info("✅ Performance Tracker initialized - God Mode 10000")
    
    def record_prediction(self, prediction_data: Dict[str, Any]) -> str:
        """Record a new prediction"""
        try:
            pred_id = f"{prediction_data['symbol']}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            
            record = PredictionRecord(
                id=pred_id,
                symbol=prediction_data['symbol'],
                signal=prediction_data['signal'],
                confidence=prediction_data['confidence'],
                entry_price=prediction_data.get('entry_price', 0),
                stop_loss=prediction_data.get('stop_loss', 0),
                take_profit=prediction_data.get('take_profit', 0),
                predicted_at=datetime.now(timezone.utc),
                sources=[s.get('source_name', 'Unknown') for s in prediction_data.get('sources', [])],
                metadata=prediction_data.get('metadata', {})
            )
            
            self.predictions[pred_id] = record
            self.recent_predictions.append(record)
            
            # Save periodically
            if len(self.predictions) % 10 == 0:
                self._save_predictions()
            
            return pred_id
        
        except Exception as e:
            self.unified_logger.error(f"Record prediction error: {e}")
            return ""
    
    def record_trade_result(self, prediction_id: str, trade_data: Dict[str, Any]) -> bool:
        """Record trade result and calculate performance"""
        try:
            if prediction_id not in self.predictions:
                self.unified_logger.warning(f"Prediction {prediction_id} not found")
                return False
            
            prediction = self.predictions[prediction_id]
            
            # Calculate P&L
            entry = trade_data.get('entry_price', prediction.entry_price)
            exit_price = trade_data['exit_price']
            
            if prediction.signal == 'BUY':
                pnl_pct = ((exit_price - entry) / entry) * 100
            elif prediction.signal == 'SELL':
                pnl_pct = ((entry - exit_price) / entry) * 100
            else:
                pnl_pct = 0
            
            # Determine outcome
            if abs(pnl_pct) < 0.1:
                outcome = 'breakeven'
            elif pnl_pct > 0:
                outcome = 'win'
            else:
                outcome = 'loss'
            
            # Determine what hit
            if exit_price >= prediction.take_profit * 0.95 and prediction.signal == 'BUY':
                hit_target = 'tp'
            elif exit_price <= prediction.stop_loss * 1.05 and prediction.signal == 'BUY':
                hit_target = 'sl'
            elif exit_price <= prediction.take_profit * 1.05 and prediction.signal == 'SELL':
                hit_target = 'tp'
            elif exit_price >= prediction.stop_loss * 0.95 and prediction.signal == 'SELL':
                hit_target = 'sl'
            else:
                hit_target = 'manual'
            
            # Calculate duration
            executed_at = trade_data.get('executed_at', datetime.now(timezone.utc))
            closed_at = trade_data.get('closed_at', datetime.now(timezone.utc))
            duration = (closed_at - executed_at).total_seconds() / 3600
            
            result = TradeResult(
                prediction_id=prediction_id,
                symbol=prediction.symbol,
                entry_price=entry,
                exit_price=exit_price,
                pnl=pnl_pct * entry / 100,
                pnl_pct=pnl_pct,
                duration_hours=duration,
                outcome=outcome,
                hit_target=hit_target,
                executed_at=executed_at,
                closed_at=closed_at
            )
            
            self.trade_results.append(result)
            self.recent_trades.append(result)
            
            # Invalidate cache
            self.metrics_cache = None
            
            # Save
            self._save_trade_results()
            
            self.unified_logger.info(f"Trade result recorded: {outcome} ({pnl_pct:+.2f}%)")
            return True
        
        except Exception as e:
            self.unified_logger.error(f"Record trade result error: {e}")
            return False
    
    def get_performance_metrics(self, days: int = 30) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        try:
            # Check cache
            if self.metrics_cache and self.cache_timestamp:
                age = (datetime.now(timezone.utc) - self.cache_timestamp).total_seconds()
                if age < self.cache_ttl:
                    return self.metrics_cache
            
            # Filter recent trades
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            recent_trades = [t for t in self.trade_results if t.closed_at > cutoff_date]
            
            if not recent_trades:
                return self._empty_metrics()
            
            # Calculate metrics
            total_trades = len(recent_trades)
            wins = [t for t in recent_trades if t.outcome == 'win']
            win_rate = len(wins) / total_trades if total_trades > 0 else 0
            
            pnls = [t.pnl_pct for t in recent_trades]
            avg_pnl_pct = np.mean(pnls)
            
            # Sharpe ratio
            if len(pnls) > 1:
                sharpe = (np.mean(pnls) / (np.std(pnls) + 1e-10)) * np.sqrt(252)
            else:
                sharpe = 0
            
            # Max drawdown
            cumulative = np.cumsum(pnls)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = cumulative - running_max
            max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
            
            # Prediction accuracy (did price move in predicted direction?)
            correct_predictions = sum(1 for t in recent_trades if t.outcome == 'win')
            pred_accuracy = correct_predictions / total_trades if total_trades > 0 else 0
            
            # Get predictions for recent trades
            recent_preds = [self.predictions.get(t.prediction_id) for t in recent_trades if t.prediction_id in self.predictions]
            recent_preds = [p for p in recent_preds if p is not None]
            
            avg_confidence = np.mean([p.confidence for p in recent_preds]) if recent_preds else 0
            
            # Calculate best timeframe/regime from historical data
            timeframe_wins = {}
            regime_wins = {}
            for pred in recent_preds:
                tf = pred.metadata.get('timeframe', '1h')
                regime = pred.metadata.get('regime', 'neutral')
                outcome = pred.metadata.get('outcome', 0)
                
                timeframe_wins[tf] = timeframe_wins.get(tf, 0) + (1 if outcome > 0 else 0)
                regime_wins[regime] = regime_wins.get(regime, 0) + (1 if outcome > 0 else 0)
            
            best_timeframe = max(timeframe_wins.items(), key=lambda x: x[1])[0] if timeframe_wins else "1h"
            best_regime = max(regime_wins.items(), key=lambda x: x[1])[0] if regime_wins else "neutral"
            
            # ROI
            roi = sum(pnls)
            
            metrics = PerformanceMetrics(
                total_predictions=len(self.predictions),
                total_trades=total_trades,
                win_rate=win_rate,
                avg_pnl_pct=avg_pnl_pct,
                sharpe_ratio=sharpe,
                max_drawdown=max_drawdown,
                prediction_accuracy=pred_accuracy,
                avg_confidence=avg_confidence,
                best_timeframe=best_timeframe,
                best_market_regime=best_regime,
                roi=roi
            )
            
            # Cache
            self.metrics_cache = metrics
            self.cache_timestamp = datetime.now(timezone.utc)
            
            return metrics
        
        except Exception as e:
            self.unified_logger.error(f"Performance metrics calculation error: {e}")
            return self._empty_metrics()
    
    def get_model_feedback(self) -> Dict[str, Any]:
        """Get feedback for model improvement"""
        try:
            metrics = self.get_performance_metrics(30)
            
            feedback = {
                'overall_performance': 'good' if metrics.win_rate > 0.6 else 'needs_improvement',
                'win_rate': metrics.win_rate,
                'prediction_accuracy': metrics.prediction_accuracy,
                'avg_confidence': metrics.avg_confidence,
                'confidence_calibration': self._check_confidence_calibration(),
                'recommendations': []
            }
            
            # Generate recommendations
            if metrics.win_rate < 0.5:
                feedback['recommendations'].append("Consider retraining models with more recent data")
            
            if metrics.prediction_accuracy < 0.6:
                feedback['recommendations'].append("Review prediction logic and source weights")
            
            if metrics.avg_confidence > 0.8 and metrics.win_rate < 0.6:
                feedback['recommendations'].append("Models are overconfident - adjust confidence thresholds")
            
            if metrics.sharpe_ratio < 1.0:
                feedback['recommendations'].append("Risk-adjusted returns are low - review risk management")
            
            return feedback
        
        except Exception as e:
            self.unified_logger.error(f"Model feedback error: {e}")
            return {}
    
    def _check_confidence_calibration(self) -> str:
        """Check if model confidence is well-calibrated"""
        try:
            # Get recent predictions with results
            recent_trades = list(self.recent_trades)
            if not recent_trades:
                return "insufficient_data"
            
            # Bucket by confidence
            high_conf_trades = []
            low_conf_trades = []
            
            for trade in recent_trades:
                pred = self.predictions.get(trade.prediction_id)
                if pred:
                    if pred.confidence > 0.7:
                        high_conf_trades.append(trade)
                    elif pred.confidence < 0.6:
                        low_conf_trades.append(trade)
            
            # Check if high confidence trades actually perform better
            if high_conf_trades and low_conf_trades:
                high_conf_wins = sum(1 for t in high_conf_trades if t.outcome == 'win') / len(high_conf_trades)
                low_conf_wins = sum(1 for t in low_conf_trades if t.outcome == 'win') / len(low_conf_trades)
                
                if high_conf_wins > low_conf_wins + 0.1:
                    return "well_calibrated"
                elif high_conf_wins < low_conf_wins:
                    return "inversely_calibrated"
                else:
                    return "poorly_calibrated"
            
            return "insufficient_data"
        
        except Exception as e:
            self.unified_logger.error(f"Confidence calibration check error: {e}")
            return "error"
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics"""
        return PerformanceMetrics(
            total_predictions=0,
            total_trades=0,
            win_rate=0,
            avg_pnl_pct=0,
            sharpe_ratio=0,
            max_drawdown=0,
            prediction_accuracy=0,
            avg_confidence=0,
            best_timeframe="N/A",
            best_market_regime="N/A",
            roi=0
        )
    
    def _save_predictions(self):
        """Save predictions to disk"""
        try:
            file_path = self.data_dir / "predictions.json"
            data = {
                pred_id: {
                    'symbol': pred.symbol,
                    'signal': pred.signal,
                    'confidence': pred.confidence,
                    'entry_price': pred.entry_price,
                    'predicted_at': pred.predicted_at.isoformat()
                }
                for pred_id, pred in list(self.predictions.items())[-1000:]  # Keep last 1000
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.unified_logger.error(f"Save predictions error: {e}")
    
    def _save_trade_results(self):
        """Save trade results to disk"""
        try:
            file_path = self.data_dir / "trade_results.json"
            data = [
                {
                    'prediction_id': t.prediction_id,
                    'symbol': t.symbol,
                    'pnl_pct': t.pnl_pct,
                    'outcome': t.outcome,
                    'closed_at': t.closed_at.isoformat()
                }
                for t in self.trade_results[-500:]  # Keep last 500
            ]
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.unified_logger.error(f"Save trade results error: {e}")
    
    def _load_historical_data(self):
        """Load historical data from disk"""
        try:
            # Load predictions
            pred_file = self.data_dir / "predictions.json"
            if pred_file.exists():
                with open(pred_file, 'r') as f:
                    data = json.load(f)
                    self.unified_logger.info(f"Loaded {len(data)} historical predictions")
            
            # Load trade results
            trade_file = self.data_dir / "trade_results.json"
            if trade_file.exists():
                with open(trade_file, 'r') as f:
                    data = json.load(f)
                    self.unified_logger.info(f"Loaded {len(data)} historical trades")
        except Exception as e:
            self.unified_logger.error(f"Load historical data error: {e}")


# Global instance
performance_tracker = PerformanceTracker()

