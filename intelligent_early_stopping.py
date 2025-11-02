"""
GOD MODE 10000 - INTELLIGENT EARLY STOPPING
============================================
Advanced early stopping strategy with adaptive patience and performance tracking

FEATURES:
- Adaptive patience based on model convergence
- Loss plateau detection
- Overfitting prevention
- Performance trend analysis
- Multi-metric monitoring
"""

# Fix Python 3.13 compatibility first
from . import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np

from typing import List, Dict, Any, Optional

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

class IntelligentEarlyStopping:
    """
    Intelligent early stopping with adaptive patience and multi-metric monitoring
    
    Features:
    - Monitors multiple metrics (loss, accuracy, overfitting)
    - Adaptive patience based on convergence rate
    - Detects plateaus and overfitting
    - Provides recommendations for hyperparameter adjustment
    """
    
    def __init__(self, base_patience: int = 20, min_delta: float = 1e-4):
        """
        Initialize early stopping monitor
        
        Args:
            base_patience: Base patience value (will be adapted)
            min_delta: Minimum change to qualify as improvement
        """
        self.logger = unified_logging.get_logger("intelligent_early_stopping") if hasattr(unified_logging, 'get_logger') else unified_logging
        
        self.base_patience = base_patience
        self.min_delta = min_delta
        
        # Tracking variables
        self.best_score = None
        self.best_epoch = 0
        self.counter = 0
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': [],
            'learning_rate': []
        }
        self.should_stop = False
        self.stop_reason = None
    
    def update(self, epoch: int, train_metrics: Dict[str, float], 
               val_metrics: Dict[str, float], learning_rate: Optional[float] = None) -> bool:
        """
        Update early stopping state with new metrics
        
        Args:
            epoch: Current epoch number
            train_metrics: Training metrics dict
            val_metrics: Validation metrics dict
            learning_rate: Current learning rate (optional)
            
        Returns:
            True if training should stop, False otherwise
        """
        # Extract metrics
        val_loss = val_metrics.get('loss', float('inf'))
        val_acc = val_metrics.get('accuracy', 0.0)
        train_loss = train_metrics.get('loss', float('inf'))
        train_acc = train_metrics.get('accuracy', 0.0)
        
        # Store history
        self.history['train_loss'].append(train_loss)
        self.history['val_loss'].append(val_loss)
        self.history['train_acc'].append(train_acc)
        self.history['val_acc'].append(val_acc)
        if learning_rate is not None:
            self.history['learning_rate'].append(learning_rate)
        
        # Primary metric for early stopping (validation loss)
        current_score = val_loss
        
        # Initialize best score on first epoch
        if self.best_score is None:
            self.best_score = current_score
            self.best_epoch = epoch
            return False
        
        # Check for improvement
        if current_score < self.best_score - self.min_delta:
            # Improvement found
            self.best_score = current_score
            self.best_epoch = epoch
            self.counter = 0
            return False
        
        # No improvement
        self.counter += 1
        
        # Calculate adaptive patience
        adaptive_patience = self._calculate_adaptive_patience(epoch)
        
        # Check various stopping conditions
        if self.counter >= adaptive_patience:
            self.should_stop = True
            self.stop_reason = f"No improvement for {self.counter} epochs (patience: {adaptive_patience})"
            return True
        
        # Check for overfitting
        if self._detect_overfitting():
            self.should_stop = True
            self.stop_reason = "Overfitting detected"
            return True
        
        # Check for loss explosion
        if self._detect_loss_explosion():
            self.should_stop = True
            self.stop_reason = "Loss explosion detected"
            return True
        
        # Check for plateau
        if epoch >= 20 and self._detect_plateau():
            self.should_stop = True
            self.stop_reason = "Training plateau detected"
            return True
        
        return False
    
    def _calculate_adaptive_patience(self, epoch: int) -> int:
        """Calculate adaptive patience based on training progress"""
        if epoch < 10:
            # Early training: use lower patience
            return max(5, self.base_patience // 2)
        elif epoch < 30:
            # Mid training: use base patience
            return self.base_patience
        else:
            # Late training: increase patience
            # Model might be fine-tuning
            return int(self.base_patience * 1.5)
    
    def _detect_overfitting(self, window: int = 5) -> bool:
        """
        Detect overfitting by comparing train and val metrics
        
        Args:
            window: Window size for moving average
            
        Returns:
            True if overfitting detected
        """
        if len(self.history['train_loss']) < window + 5:
            return False
        
        try:
            # Calculate recent overfitting gap
            recent_train_loss = np.mean(self.history['train_loss'][-window:])
            recent_val_loss = np.mean(self.history['val_loss'][-window:])
            
            # Check if validation loss is significantly higher than training
            overfitting_ratio = recent_val_loss / (recent_train_loss + 1e-10)
            
            # Also check accuracy gap
            recent_train_acc = np.mean(self.history['train_acc'][-window:])
            recent_val_acc = np.mean(self.history['val_acc'][-window:])
            acc_gap = recent_train_acc - recent_val_acc
            
            # Overfitting criteria:
            # 1. Val loss > 1.5x train loss
            # 2. Train-Val accuracy gap > 20%
            # 3. Val loss is increasing while train loss decreasing
            if overfitting_ratio > 1.5 or acc_gap > 0.20:
                return True
            
            # Check if val loss trending up while train loss trending down
            if len(self.history['train_loss']) >= 10:
                train_trend = np.polyfit(range(window), self.history['train_loss'][-window:], 1)[0]
                val_trend = np.polyfit(range(window), self.history['val_loss'][-window:], 1)[0]
                
                if train_trend < -0.01 and val_trend > 0.01:
                    # Train improving but val getting worse
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Overfitting detection error: {e}")
            return False
    
    def _detect_loss_explosion(self) -> bool:
        """Detect if loss is exploding (gradient issues)"""
        if len(self.history['val_loss']) < 5:
            return False
        
        try:
            recent_loss = self.history['val_loss'][-1]
            
            # Check for NaN or Inf
            if not np.isfinite(recent_loss):
                return True
            
            # Check if loss suddenly increased dramatically
            if len(self.history['val_loss']) >= 3:
                avg_prev_loss = np.mean(self.history['val_loss'][-4:-1])
                if recent_loss > avg_prev_loss * 3:  # 3x increase
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _detect_plateau(self, window: int = 10) -> bool:
        """
        Detect if training has plateaued (no progress)
        
        Args:
            window: Window size to check for plateau
            
        Returns:
            True if plateau detected
        """
        if len(self.history['val_loss']) < window + 5:
            return False
        
        try:
            # Get recent losses
            recent_losses = self.history['val_loss'][-window:]
            
            # Calculate variance - low variance = plateau
            loss_variance = np.var(recent_losses)
            loss_mean = np.mean(recent_losses)
            
            # Relative variance
            rel_variance = loss_variance / (loss_mean ** 2 + 1e-10)
            
            # Plateau if variance is very low
            # Also check that we're not making progress
            if rel_variance < 1e-6 and self.counter > self.base_patience // 2:
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_best_epoch(self) -> int:
        """Get epoch with best validation performance"""
        return self.best_epoch
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of training performance"""
        if not self.history['val_loss']:
            return {}
        
        try:
            return {
                'best_epoch': self.best_epoch,
                'best_val_loss': float(self.best_score) if self.best_score is not None else None,
                'final_train_loss': float(self.history['train_loss'][-1]) if self.history['train_loss'] else None,
                'final_val_loss': float(self.history['val_loss'][-1]) if self.history['val_loss'] else None,
                'final_train_acc': float(self.history['train_acc'][-1]) if self.history['train_acc'] else None,
                'final_val_acc': float(self.history['val_acc'][-1]) if self.history['val_acc'] else None,
                'overfitting_gap': float(self.history['train_acc'][-1] - self.history['val_acc'][-1]) if self.history['train_acc'] and self.history['val_acc'] else None,
                'stopped_early': self.should_stop,
                'stop_reason': self.stop_reason,
                'total_epochs': len(self.history['val_loss'])
            }
        except Exception as e:
            self.logger.debug(f"Performance summary error: {e}")
            return {}
    
    def should_reduce_learning_rate(self, plateau_patience: int = 10) -> bool:
        """
        Check if learning rate should be reduced
        
        Args:
            plateau_patience: Patience before suggesting LR reduction
            
        Returns:
            True if LR should be reduced
        """
        if self.counter >= plateau_patience and not self.should_stop:
            return True
        return False
    
    def get_recommendation(self) -> str:
        """Get recommendation for hyperparameter adjustment"""
        if not self.history['val_loss']:
            return "Not enough data for recommendation"
        
        perf = self.get_performance_summary()
        
        if perf.get('overfitting_gap', 0) > 0.15:
            return "High overfitting detected. Recommendation: Increase regularization (higher dropout, L1/L2)"
        
        if len(self.history['val_loss']) < 20 and self.should_stop:
            return "Stopped too early. Recommendation: Increase patience or check learning rate"
        
        if self.stop_reason == "Training plateau detected":
            return "Training plateaued. Recommendation: Try reducing learning rate or adjusting architecture"
        
        if self.stop_reason == "Loss explosion detected":
            return "Loss exploded. Recommendation: Reduce learning rate significantly or check data preprocessing"
        
        return "Training progressing normally"

def create_early_stopping(model_name: str, data_size: int) -> IntelligentEarlyStopping:
    """
    Factory function to create early stopping with appropriate parameters
    
    Args:
        model_name: Name of the model
        data_size: Size of training data
        
    Returns:
        Configured IntelligentEarlyStopping instance
    """
    # Adjust patience based on data size and model type
    if data_size < 500:
        base_patience = 15
    elif data_size < 2000:
        base_patience = 20
    else:
        base_patience = 30
    
    # Some models need more patience
    if model_name in ['lstm', 'transformer', 'neural_network']:
        base_patience = int(base_patience * 1.5)
    
    return IntelligentEarlyStopping(base_patience=base_patience)

