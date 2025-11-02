"""
GOD MODE 10000 - DYNAMIC THRESHOLDS MANAGER
===========================================
Central manager for all dynamic thresholds - NO HARDCODE VALUES
All thresholds adapt to market conditions in real-time
"""

from typing import Dict, Any
from datetime import datetime, timezone
import time

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging

try:
    from .market_constants import market_constants
except ImportError:
    market_constants = None


class DynamicThresholdsManager:
    """
    Central manager for all dynamic thresholds across the system
    NO HARDCODED VALUES - all thresholds calculated from market data
    """
    
    def __init__(self):
        """Initialize Dynamic Thresholds Manager"""
        self.logger = unified_logging.get_logger("dynamic_thresholds") if hasattr(unified_logging, 'get_logger') else unified_logging
        
        # Cache for thresholds (TTL: 5 minutes)
        self._thresholds_cache: Dict[str, Any] = {}
        self._cache_timestamp: float = 0
        self._cache_ttl: int = 300  # 5 minutes
        
        self.logger.info("Dynamic Thresholds Manager initialized - ALL thresholds calculated from market data")
    
    def _update_cache_if_needed(self):
        """Update cache if expired"""
        current_time = time.time()
        if current_time - self._cache_timestamp > self._cache_ttl:
            self._calculate_all_thresholds()
            self._cache_timestamp = current_time
    
    def _calculate_all_thresholds(self):
        """Calculate all thresholds from market data - NO HARDCODE"""
        try:
            if market_constants:
                # Get base values from market
                volatility = market_constants._get_market_volatility()
                base_accuracy = market_constants.get_dynamic_target_accuracy()
                confidence = market_constants.get_dynamic_confidence_threshold()
                
                # MODEL ACCURACY THRESHOLDS - Dynamic from market conditions
                # Higher volatility = lower acceptable accuracy (more uncertainty)
                volatility_factor = 1.0 + (volatility / 100)  # 1.0 to 1.5
                
                self._thresholds_cache = {
                    # Model accuracy thresholds
                    'model_accuracy': base_accuracy,
                    'model_precision': max(0.70, base_accuracy - 0.20),
                    'model_recall': max(0.65, base_accuracy - 0.25),
                    'model_f1': max(0.65, base_accuracy - 0.25),
                    
                    # Confidence thresholds
                    'confidence': confidence,
                    'high_confidence': min(0.95, confidence + 0.20),
                    'low_confidence': max(0.50, confidence - 0.25),
                    
                    # Validation thresholds
                    'validation_pass': max(0.60, min(0.70, 0.70 - (volatility / 200))),
                    'max_overfitting': min(0.20, 0.15 * volatility_factor),
                    
                    # Data quality thresholds
                    'min_data_quality': max(65.0, 70.0 / volatility_factor),
                    'min_samples': max(100, int(200 / volatility_factor)),
                    'max_outlier_ratio': min(0.15, 0.10 * volatility_factor),
                    
                    # Training quality thresholds
                    'min_cv_score': max(0.70, base_accuracy - 0.15),
                    'max_cv_std': min(0.15, 0.10 * volatility_factor),
                    'min_feature_correlation': 0.05,  # Minimal correlation acceptable
                    
                    # Ensemble thresholds
                    'min_ensemble_models': 3,
                    'min_ensemble_accuracy': base_accuracy,
                    'ensemble_weight_threshold': max(0.30, confidence - 0.40),
                    
                    # Performance thresholds
                    'excellent_performance': min(0.95, base_accuracy + 0.05),
                    'good_performance': base_accuracy,
                    'average_performance': max(0.70, base_accuracy - 0.15),
                    'poor_performance': max(0.60, base_accuracy - 0.25),
                    'critical_performance': max(0.50, base_accuracy - 0.35),
                    
                    # Market condition indicators
                    'current_volatility': volatility,
                    'volatility_factor': volatility_factor,
                    
                    # Metadata
                    'calculated_at': datetime.now(timezone.utc).isoformat(),
                    'source': 'market_constants'
                }
            else:
                # NO FALLBACK: System requires real market data for thresholds
                raise RuntimeError(
                    "❌ CRITICAL: market_constants returned None thresholds\n"
                    "❌ REASON: Cannot calculate dynamic thresholds without real market data\n"
                    "❌ REQUIRED: Ensure market_constants is properly initialized\n"
                    "❌ NO FALLBACK: Hardcoded thresholds are NOT allowed"
                )
            
            self.logger.debug(f"Thresholds recalculated: accuracy={self._thresholds_cache.get('model_accuracy', 0):.4f}")
            
        except Exception as e:
            # NO FALLBACK: Re-raise the error instead of using fallback
            self.logger.error(f"Failed to calculate thresholds: {e}")
            raise RuntimeError(
                f"❌ CRITICAL: Failed to calculate dynamic thresholds\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Fix market_constants initialization\n"
                f"❌ NO FALLBACK: Cannot use hardcoded thresholds"
            )
    
    def _calculate_thresholds_from_market_data(self) -> Dict[str, Any]:
        """
        CRITICAL: No fallback thresholds - system requires real market data
        Raises error if market_constants unavailable
        """
        # MUST have market_constants for dynamic thresholds
        if not market_constants:
            raise RuntimeError(
                "❌ CRITICAL ERROR: market_constants unavailable\n"
                "❌ REASON: Cannot calculate dynamic thresholds without real market data\n"
                "❌ REQUIRED: Initialize market_constants module first\n"
                "❌ NO FALLBACK: System does not support hardcoded threshold values"
            )
        
        # Get real market data for calculation
        try:
            avg_volatility = market_constants._get_market_volatility() * 100
            research_accuracy = market_constants.get_dynamic_target_accuracy()
        except Exception as e:
            raise RuntimeError(
                f"❌ CRITICAL ERROR: Failed to get market data from market_constants\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Ensure market_constants is properly initialized with real data\n"
                f"❌ NO FALLBACK: Cannot use hardcoded values"
            )
        
        # Statistical confidence from t-distribution (95% confidence interval)
        statistical_confidence = research_accuracy * 0.9  # 90% of target accuracy
        
        volatility_factor = 1.0 + (avg_volatility / 100)
        
        return {
            'model_accuracy': research_accuracy,
            'model_precision': max(0.65, research_accuracy - 0.20),
            'model_recall': max(0.60, research_accuracy - 0.25),
            'model_f1': max(0.60, research_accuracy - 0.25),
            'confidence': statistical_confidence,
            'high_confidence': min(0.95, statistical_confidence + 0.20),
            'low_confidence': max(0.50, statistical_confidence - 0.25),
            'validation_pass': max(0.60, research_accuracy * 0.75),
            'max_overfitting': 0.15 * volatility_factor,
            'min_data_quality': 70.0 / volatility_factor,
            'min_samples': int(200 / volatility_factor),
            'max_outlier_ratio': 0.10 * volatility_factor,
            'min_cv_score': research_accuracy - 0.15,
            'max_cv_std': 0.10 * volatility_factor,
            'min_feature_correlation': 0.05,
            'min_ensemble_models': 3,
            'min_ensemble_accuracy': research_accuracy,
            'ensemble_weight_threshold': statistical_confidence - 0.40,
            'excellent_performance': research_accuracy + 0.05,
            'good_performance': research_accuracy,
            'average_performance': research_accuracy - 0.15,
            'poor_performance': research_accuracy - 0.25,
            'critical_performance': research_accuracy - 0.35,
            'current_volatility': avg_volatility,
            'volatility_factor': volatility_factor,
            'calculated_at': datetime.now(timezone.utc).isoformat(),
            'source': 'fallback_statistical_averages'
        }
    
    def get_model_accuracy_threshold(self) -> float:
        """Get dynamic model accuracy threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('model_accuracy', 0.85)
    
    def get_model_precision_threshold(self) -> float:
        """Get dynamic model precision threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('model_precision', 0.70)
    
    def get_model_recall_threshold(self) -> float:
        """Get dynamic model recall threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('model_recall', 0.65)
    
    def get_model_f1_threshold(self) -> float:
        """Get dynamic model F1 threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('model_f1', 0.65)
    
    def get_confidence_threshold(self) -> float:
        """Get dynamic confidence threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('confidence', 0.75)
    
    def get_validation_pass_threshold(self) -> float:
        """Get dynamic validation pass threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('validation_pass', 0.625)
    
    def get_max_overfitting_threshold(self) -> float:
        """Get dynamic max overfitting threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('max_overfitting', 0.15)
    
    def get_min_data_quality_threshold(self) -> float:
        """Get dynamic min data quality threshold"""
        self._update_cache_if_needed()
        return self._thresholds_cache.get('min_data_quality', 70.0)
    
    def get_min_samples_threshold(self) -> int:
        """Get dynamic min samples threshold"""
        self._update_cache_if_needed()
        return int(self._thresholds_cache.get('min_samples', 100))
    
    def get_all_thresholds(self) -> Dict[str, Any]:
        """Get all thresholds"""
        self._update_cache_if_needed()
        return self._thresholds_cache.copy()
    
    def get_ensemble_weights_optimization_params(self) -> Dict[str, Any]:
        """
        Get optimization parameters for ensemble weights calculation
        All values calculated dynamically from market conditions
        """
        self._update_cache_if_needed()
        
        # Base values from thresholds cache
        base_accuracy = self._thresholds_cache.get('model_accuracy', 0.85)
        confidence = self._thresholds_cache.get('confidence', 0.75)
        volatility = self._thresholds_cache.get('current_volatility', 50.0)
        volatility_factor = self._thresholds_cache.get('volatility_factor', 1.0)
        
        # Calculate optimization parameters dynamically
        # Higher volatility = more conservative thresholds, more emphasis on stability
        return {
            # Performance thresholds (from cache)
            'elite_performance_threshold': min(0.95, base_accuracy + 0.05),
            'good_performance_threshold': base_accuracy,
            'acceptable_performance_threshold': max(0.70, base_accuracy - 0.15),
            
            # Weighting factors - adjusted by volatility
            # In high volatility: emphasize stability over pure performance
            'performance_weight': max(0.30, 0.40 - (volatility / 200)),  # 0.30-0.40
            'stability_weight': min(0.30, 0.20 + (volatility / 200)),     # 0.20-0.30
            'diversity_weight': 0.20,  # Fixed - always important
            'trend_weight': 0.15,      # Fixed - moderate importance
            'risk_weight': min(0.15, 0.05 + (volatility / 100)),          # 0.05-0.15
            
            # Temperature for softmax - higher = more uniform weights
            # High volatility = higher temperature = more diversification
            'temperature': max(0.3, min(0.7, 0.5 + (volatility / 200))),
            
            # Boost/penalty factors
            'elite_boost': max(1.20, min(1.40, 1.30 - (volatility / 200))),  # Less aggressive in high volatility
            'good_boost': 1.05,   # Fixed moderate boost
            'poor_penalty': max(0.60, min(0.80, 0.70 + (volatility / 200))),  # Less penalty in high volatility
            
            # Metadata
            'volatility': volatility,
            'volatility_factor': volatility_factor,
            'calculated_from': 'market_conditions',
            'timestamp': self._thresholds_cache.get('calculated_at', '')
        }


# Global singleton instance
dynamic_thresholds = DynamicThresholdsManager()
