"""
GOD MODE 10000 - BALANCED HYPERPARAMETERS
==========================================
Intelligent hyperparameter selection for maximum accuracy with proper generalization

OPTIMIZATION STRATEGY:
- Dynamic adjustment based on data size and market conditions
- GPU-optimized batch sizes and learning rates
- Early stopping with intelligent patience
- Regularization balanced for crypto volatility
"""

from typing import Dict, Any
import psutil

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

class BalancedHyperparameters:
    """
    Intelligent hyperparameter manager for maximum model accuracy
    
    Features:
    - Data-size adaptive parameters
    - GPU-optimized settings
    - Market-volatility aware regularization
    - Memory-efficient configurations
    """
    
    def __init__(self):
        self.logger = unified_logging.get_logger("balanced_hyperparameters") if hasattr(unified_logging, 'get_logger') else unified_logging
        
        # Detect system capabilities
        self.cpu_count = psutil.cpu_count(logical=True)
        self.ram_gb = psutil.virtual_memory().total / (1024**3)
        
        # Check GPU availability
        self.gpu_available = False
        self.gpu_memory_gb = 0
        try:
            import torch
            if torch.cuda.is_available():
                self.gpu_available = True
                self.gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        except Exception:
            pass
        
        self.logger.debug(f"System: CPU={self.cpu_count}, RAM={self.ram_gb:.1f}GB, GPU={self.gpu_available} ({self.gpu_memory_gb:.1f}GB)")
    
    def get_balanced_params(self, model_name: str, data_size: int) -> Dict[str, Any]:
        """
        Get balanced hyperparameters for a specific model
        
        Args:
            model_name: Model type (xgboost, lightgbm, random_forest, etc.)
            data_size: Training data size
            
        Returns:
            Dictionary of optimized hyperparameters
        """
        # Data scale factor: 0.5 for small data, 1.5 for large data
        data_scale = min(1.5, max(0.5, data_size / 5000))
        
        # GPU optimization factor
        gpu_factor = 1.3 if self.gpu_available else 1.0
        
        if model_name in ['xgboost', 'xgboost_model']:
            return self._get_xgboost_params(data_scale, gpu_factor)
        elif model_name in ['lightgbm', 'lightgbm_model']:
            return self._get_lightgbm_params(data_scale, gpu_factor)
        elif model_name in ['random_forest', 'random_forest_model']:
            return self._get_random_forest_params(data_scale)
        elif model_name in ['lstm', 'lstm_model']:
            return self._get_lstm_params(data_scale, gpu_factor)
        elif model_name in ['neural_network', 'neural_network_model']:
            return self._get_neural_network_params(data_scale, gpu_factor)
        elif model_name in ['transformer', 'transformer_model']:
            return self._get_transformer_params(data_scale)
        elif model_name in ['prophet', 'prophet_model']:
            return self._get_prophet_params(data_scale)
        elif model_name in ['ensemble', 'ensemble_model']:
            return self._get_ensemble_params(data_scale)
        elif model_name in ['svm', 'svm_model']:
            return self._get_svm_params(data_scale)
        else:
            self.logger.warning(f"Unknown model: {model_name}, using default params")
            return {}
    
    def _get_xgboost_params(self, data_scale: float, gpu_factor: float) -> Dict[str, Any]:
        """XGBoost: GPU-accelerated gradient boosting with ULTRA-OPTIMIZED capacity for >90% accuracy"""
        base_rounds = int(350 * data_scale * gpu_factor)  # Further increased for better learning
        
        return {
            'max_depth': min(14, max(7, int(9 * data_scale))),  # Further increased depth for better pattern capture
            'eta': max(0.005, 0.015 / data_scale),  # Even lower learning rate for better convergence
            'num_rounds': min(600, max(300, base_rounds)),  # More rounds for thorough learning
            'subsample': 0.85,  # Higher subsample for better generalization
            'colsample_bytree': 0.8,  # Increased from 0.75 to 0.8
            'colsample_bylevel': 0.7,  # Increased from 0.65 to 0.7
            'colsample_bynode': 0.7,  # Increased from 0.65 to 0.7
            'min_child_weight': max(3, int(8 / data_scale)),  # Reduced from 5/10 for more splits
            'gamma': max(0.15, 0.4 / data_scale),  # Slightly reduced from 0.2/0.5
            'lambda': 2.5,  # Reduced from 3.0 for less constraint
            'alpha': 0.3,  # Reduced from 0.5 for less constraint
            'max_delta_step': 3,  # Increased from 2 for faster learning
            'early_stopping_rounds': max(50, int(80 * data_scale)),  # Increased patience
            'eval_metric': 'rmse'
        }
    
    def _get_lightgbm_params(self, data_scale: float, gpu_factor: float) -> Dict[str, Any]:
        """LightGBM: Memory-efficient gradient boosting - ANTI-OVERFITTING configuration"""
        # CRITICAL FIX: Increase regularization to prevent overfitting (40.4% detected)
        # Overfitting occurs when model is too complex → reduce capacity, increase regularization
        base_rounds = int(350 * data_scale * gpu_factor)  # Reduced from 400 to 350
        
        return {
            'num_leaves': min(100, max(50, int(70 * data_scale))),  # Reduced from 80-150 to 50-100 leaves
            'learning_rate': max(0.01, 0.025 / data_scale),  # Slightly increased from 0.008-0.02 to 0.01-0.025
            'num_boost_round': min(500, max(250, base_rounds)),  # Reduced from 300-600 to 250-500 rounds
            'feature_fraction': 0.7,  # Reduced from 0.8 to 0.7 (more regularization)
            'bagging_fraction': 0.7,  # Reduced from 0.8 to 0.7 (more regularization)
            'bagging_freq': 5,  # Increased from 4 to 5 (less frequent bagging)
            'max_depth': min(10, max(5, int(7 * data_scale))),  # Reduced from 8-15 to 5-10 depth
            'min_data_in_leaf': max(15, int(30 / data_scale)),  # Increased from 10-20 to 15-30 (more regularization)
            'lambda_l1': 0.5,  # Increased from 0.2 to 0.5 (more L1 regularization)
            'lambda_l2': 2.0,  # Increased from 1.2 to 2.0 (more L2 regularization)
            'min_gain_to_split': 0.15,  # Increased from 0.08 to 0.15 (harder to split)
            'early_stopping_rounds': max(50, int(80 * data_scale)),  # Increased patience
            'metric': 'rmse',
            'verbosity': -1
        }
    
    def _get_random_forest_params(self, data_scale: float) -> Dict[str, Any]:
        """Random Forest: Ensemble of decision trees - ANTI-UNDERFITTING configuration"""
        # CRITICAL FIX: Reduce regularization to prevent underfitting
        # Underfitting occurs when model is too simple → increase capacity
        return {
            'n_estimators': min(350, max(200, int(250 * data_scale))),  # Increased from 180-300 to 200-350 trees
            'max_depth': min(25, max(15, int(18 * data_scale))),  # Increased from 12-20 to 15-25 depth
            'min_samples_split': max(2, int(4 / data_scale)),  # Reduced from 3-6 to 2-4 (less regularization)
            'min_samples_leaf': max(1, int(2 / data_scale)),  # Reduced from 2-4 to 1-2 (less regularization)
            'max_features': 'sqrt',  # Use sqrt(n_features) features
            'bootstrap': True,  # Bootstrap sampling
            'oob_score': True,  # Out-of-bag score
            'n_jobs': -1,  # Use all CPU cores
            'random_state': 42
        }
    
    def _get_lstm_params(self, data_scale: float, gpu_factor: float) -> Dict[str, Any]:
        """LSTM: Deep learning for time series with OPTIMIZED architecture (using MLPRegressor)"""
        base_epochs = int(250 * data_scale * gpu_factor)  # Increased base from 200 to 250
        
        # GPU-optimized batch size
        if self.gpu_available:
            if self.gpu_memory_gb >= 8:
                batch_size = 128
            elif self.gpu_memory_gb >= 4:
                batch_size = 64
            else:
                batch_size = 32
        else:
            batch_size = 64
        
        return {
            'hidden_layer_sizes': (128, 64, 32),  # 3-layer network optimized for time-series
            'learning_rate_init': 0.001,  # Increased from 0.0005 to 0.001
            'batch_size': batch_size,
            'early_stopping': False,  # CRITICAL: Disabled - use external validation instead
            'alpha': 0.0001,  # Low regularization to prevent underfitting
            'max_iter': min(500, max(250, base_epochs)),  # Increased from 400 to 500
            'tol': 1e-5  # Relaxed from 1e-6 to 1e-5
        }
    
    def _get_neural_network_params(self, data_scale: float, gpu_factor: float) -> Dict[str, Any]:
        """Neural Network: OPTIMIZED Multi-layer perceptron with balanced capacity"""
        base_epochs = int(250 * data_scale * gpu_factor)  # Increased base from 200 to 250
        
        # GPU-optimized batch size
        if self.gpu_available:
            if self.gpu_memory_gb >= 8:
                batch_size = 128
            elif self.gpu_memory_gb >= 4:
                batch_size = 64
            else:
                batch_size = 32
        else:
            batch_size = 64
        
        return {
            'hidden_layer_sizes': (100, 50, 25),  # 3-layer network balanced for small-medium datasets
            'activation': 'relu',
            'solver': 'adam',
            'learning_rate': 'adaptive',
            'learning_rate_init': 0.001,  # Increased from 0.0005 to 0.001
            'alpha': 0.0005,  # Balanced regularization
            'batch_size': batch_size,
            'max_iter': min(500, max(250, base_epochs)),  # Increased from 400 to 500
            'early_stopping': False,  # CRITICAL: Disabled - use external validation instead
            'tol': 1e-5,  # Relaxed from 1e-6 to 1e-5
            'random_state': 42
        }
    
    def _get_transformer_params(self, data_scale: float) -> Dict[str, Any]:
        """Transformer: Attention-based architecture - ANTI-OVERFITTING configuration"""
        # CRITICAL FIX: Increase regularization to prevent overfitting (36.3% detected)
        # Overfitting occurs when model is too complex → reduce capacity, increase regularization
        return {
            'n_estimators': min(200, max(120, int(150 * data_scale))),  # Reduced from 150-250 to 120-200 trees
            'max_depth': min(12, max(6, int(8 * data_scale))),  # Reduced from 10-18 to 6-12 depth
            'min_samples_split': max(5, int(10 / data_scale)),  # Increased from 3-6 to 5-10 (more regularization)
            'min_samples_leaf': max(3, int(6 / data_scale)),  # Increased from 2-4 to 3-6 (more regularization)
            'max_features': 'sqrt',
            'bootstrap': False,  # ExtraTrees doesn't use bootstrap
            'n_jobs': -1,
            'random_state': 42
        }
    
    def _get_prophet_params(self, data_scale: float) -> Dict[str, Any]:
        """Prophet: Time series forecasting - ANTI-UNDERFITTING configuration"""
        # CRITICAL FIX: Reduce regularization to prevent underfitting
        # Underfitting occurs when model is too simple → increase capacity
        return {
            'n_estimators': min(250, max(180, int(220 * data_scale))),  # Increased from 150-200 to 180-250
            'learning_rate': max(0.04, 0.06 / data_scale),  # Increased from 0.03-0.05 to 0.04-0.06
            'max_depth': min(10, max(6, int(8 * data_scale))),  # Increased from 5-8 to 6-10 depth
            'min_samples_split': max(2, int(4 / data_scale)),  # Reduced from 4-6 to 2-4 (less regularization)
            'min_samples_leaf': max(1, int(2 / data_scale)),  # Reduced from 2-3 to 1-2 (less regularization)
            'subsample': 0.85,  # Increased from 0.8 to 0.85 (more data per tree)
            'max_features': 'sqrt',
            'validation_fraction': 0.15,
            'n_iter_no_change': 25,
            'tol': 1e-5,
            'random_state': 42
        }
    
    def _get_ensemble_params(self, data_scale: float) -> Dict[str, Any]:
        """Ensemble: Voting regressor combining multiple models"""
        return {
            'n_estimators': min(150, max(100, int(120 * data_scale))),  # 100-150 estimators
            'max_depth': min(15, max(10, int(12 * data_scale))),  # 10-15 depth
            'min_samples_split': max(3, int(5 / data_scale)),
            'min_samples_leaf': max(2, int(3 / data_scale)),
            'max_features': 'sqrt',
            'bootstrap': True,
            'oob_score': True,
            'n_jobs': -1,
            'random_state': 42
        }
    
    def _get_svm_params(self, data_scale: float) -> Dict[str, Any]:
        """SVM: Support Vector Machine with ULTRA ANTI-OVERFITTING regularization - LINEAR kernel only"""
        # CRITICAL: Always use LINEAR kernel to prevent overfitting
        # Small crypto datasets + RBF kernel = 100% overfitting
        return {
            'C': min(3, max(0.5, 1.5 * data_scale)),  # VERY low C to prevent overfitting (was 5-15)
            'epsilon': max(0.15, 0.25 / data_scale),  # Higher epsilon for wider margin (was 0.1-0.15)
            'max_iter': 5000,
            'tol': 1e-4,
            'cache_size': min(2000, int(1000 * data_scale))
        }
    
    def get_optimal_batch_size(self, model_name: str, data_size: int) -> int:
        """Get optimal batch size based on GPU memory and data size"""
        if not self.gpu_available:
            # CPU batch sizes
            if data_size < 1000:
                return 32
            elif data_size < 5000:
                return 64
            else:
                return 128
        
        # GPU batch sizes - optimized for memory
        if self.gpu_memory_gb >= 12:  # High-end GPU (12GB+)
            base_batch = 256
        elif self.gpu_memory_gb >= 8:  # Mid-range GPU (8GB)
            base_batch = 128
        elif self.gpu_memory_gb >= 6:  # Entry-level dedicated GPU (6GB)
            base_batch = 64
        elif self.gpu_memory_gb >= 4:  # Low-end GPU (4GB)
            base_batch = 32
        else:  # Very low memory
            base_batch = 16
        
        # Adjust based on data size
        if data_size < 500:
            return max(16, base_batch // 4)
        elif data_size < 2000:
            return max(32, base_batch // 2)
        else:
            return base_batch
    
    def get_optimal_workers(self, task_type: str = 'training') -> int:
        """Get optimal number of workers for parallel processing"""
        if task_type == 'training':
            # Training benefits from leaving some CPU for system
            return max(1, int(self.cpu_count * 0.8))
        elif task_type == 'inference':
            # Inference can use all CPUs
            return self.cpu_count
        elif task_type == 'preprocessing':
            # Preprocessing is I/O heavy, use more workers
            return min(self.cpu_count * 2, 32)
        else:
            return max(1, int(self.cpu_count * 0.75))

# Export singleton instance
balanced_hyperparameters = BalancedHyperparameters()

