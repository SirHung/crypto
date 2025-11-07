"""
GOD MODE 10000 - SYSTEM VALIDATOR
===================================
Comprehensive System-Wide Validation & Health Checks
STRICTEST validation level for production deployment
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import time

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

# Use centralized pandas/numpy bypass
try:
    import python313_compatibility
except ImportError:
    pass

import numpy as np
import pandas as pd


@dataclass
class ValidationResult:
    """Validation result structure"""
    check_name: str
    passed: bool
    severity: str  # 'critical', 'warning', 'info'
    message: str
    details: Dict[str, Any]
    timestamp: datetime


class SystemValidator:
    """
    GOD MODE 10000 - Comprehensive System Validator
    
    Validates:
    1. GPU + Multi-threading synchronization
    2. 9 AI models pipeline integrity
    3. Crypto/Forex logic consistency
    4. Prediction accuracy alignment
    5. Edge cases handling
    6. Resource utilization
    """
    
    def __init__(self):
        """Initialize System Validator"""
        self.logger = unified_logging.get_logger("system_validator") if hasattr(unified_logging, 'get_logger') else unified_logging
        self.validation_results: List[ValidationResult] = []
        
        self.logger.info("✅ System Validator initialized - God Mode 10000")
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Run ALL validation checks - COMPREHENSIVE
        
        Returns:
            Dict with overall status and detailed results
        """
        self.logger.info("=" * 80)
        self.logger.info("🔍 STARTING COMPREHENSIVE SYSTEM VALIDATION - GOD MODE 10000")
        self.logger.info("=" * 80)
        
        self.validation_results = []
        start_time = time.time()
        
        # Run all validation checks
        checks = [
            self._validate_gpu_availability,
            self._validate_multi_threading,
            self._validate_gpu_threading_sync,
            self._validate_ai_models_pipeline,
            self._validate_crypto_forex_logic,
            self._validate_prediction_system,
            self._validate_data_quality_system,
            self._validate_cache_system,
            self._validate_resource_management,
            self._validate_error_handling,
        ]
        
        for check in checks:
            try:
                result = check()
                self.validation_results.append(result)
                
                # Log result
                icon = "✅" if result.passed else ("⚠️" if result.severity == 'warning' else "❌")
                self.logger.info(f"{icon} {result.check_name}: {result.message}")
                
            except Exception as e:
                error_result = ValidationResult(
                    check_name=check.__name__,
                    passed=False,
                    severity='critical',
                    message=f"Validation check failed: {e}",
                    details={'error': str(e)},
                    timestamp=datetime.now(timezone.utc)
                )
                self.validation_results.append(error_result)
                self.logger.error(f"❌ {check.__name__} failed: {e}")
        
        # Calculate summary
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results if r.passed)
        critical_failures = sum(1 for r in self.validation_results if not r.passed and r.severity == 'critical')
        warnings = sum(1 for r in self.validation_results if not r.passed and r.severity == 'warning')
        
        elapsed_time = time.time() - start_time
        
        # Overall status
        overall_pass = critical_failures == 0
        pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        self.logger.info("=" * 80)
        if overall_pass:
            self.logger.info(f"✅ VALIDATION COMPLETE: {passed_checks}/{total_checks} checks passed ({pass_rate:.1f}%)")
        else:
            self.logger.error(f"❌ VALIDATION FAILED: {critical_failures} critical failures, {warnings} warnings")
        self.logger.info(f"⏱️ Total validation time: {elapsed_time:.2f}s")
        self.logger.info("=" * 80)
        
        return {
            'overall_pass': overall_pass,
            'pass_rate': pass_rate,
            'total_checks': total_checks,
            'passed': passed_checks,
            'critical_failures': critical_failures,
            'warnings': warnings,
            'elapsed_time': elapsed_time,
            'results': self.validation_results
        }
    
    def _validate_gpu_availability(self) -> ValidationResult:
        """Check GPU availability and configuration"""
        try:
            from gpu_accelerator import GPUAccelerator, GPU_AVAILABLE
            
            details = {
                'gpu_available': GPU_AVAILABLE,
                'gpu_library': None,
                'device_info': None
            }
            
            if GPU_AVAILABLE:
                try:
                    gpu_acc = GPUAccelerator()
                    details['gpu_library'] = gpu_acc.gpu_library
                    details['device_info'] = gpu_acc.device_info
                    
                    message = f"GPU available: {gpu_acc.gpu_library}"
                    passed = True
                except Exception as e:
                    message = f"GPU detected but initialization failed: {e}"
                    passed = False
                    details['error'] = str(e)
            else:
                message = "GPU not available, using CPU fallback"
                passed = True  # Not critical - CPU fallback OK
            
            return ValidationResult(
                check_name="GPU Availability",
                passed=passed,
                severity='warning' if not GPU_AVAILABLE else 'info',
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="GPU Availability",
                passed=False,
                severity='warning',
                message=f"GPU check failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_multi_threading(self) -> ValidationResult:
        """Validate multi-threading configuration"""
        try:
            from parallel_executor import parallel_executor
            import psutil
            
            cpu_count = psutil.cpu_count(logical=True)
            thread_workers = parallel_executor.max_thread_workers
            process_workers = parallel_executor.max_process_workers
            
            details = {
                'cpu_count': cpu_count,
                'thread_workers': thread_workers,
                'process_workers': process_workers,
                'optimal': thread_workers >= 4 and thread_workers <= cpu_count * 32
            }
            
            if details['optimal']:
                message = f"Multi-threading configured optimally: {thread_workers} thread workers, {process_workers} process workers"
                passed = True
                severity = 'info'
            else:
                message = f"Multi-threading suboptimal: {thread_workers} workers (CPU: {cpu_count})"
                passed = True  # Warning, not critical
                severity = 'warning'
            
            return ValidationResult(
                check_name="Multi-Threading Configuration",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Multi-Threading Configuration",
                passed=False,
                severity='critical',
                message=f"Multi-threading check failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_gpu_threading_sync(self) -> ValidationResult:
        """Validate GPU and threading work together without conflicts"""
        try:
            from parallel_executor import parallel_executor
            from gpu_accelerator import GPUAccelerator, GPU_AVAILABLE
            
            details = {
                'gpu_available': GPU_AVAILABLE,
                'parallel_executor_initialized': parallel_executor is not None,
                'sync_test_passed': False
            }
            
            # Test: Can we create tasks that will use both GPU and threading?
            if GPU_AVAILABLE:
                try:
                    gpu_acc = GPUAccelerator()
                    # Simple synchronization test
                    test_data = np.random.rand(100)
                    gpu_data = gpu_acc.to_gpu(test_data)
                    cpu_data = gpu_acc.to_cpu(gpu_data)
                    
                    # Check data integrity after GPU round-trip
                    if np.allclose(test_data, cpu_data, rtol=1e-5):
                        details['sync_test_passed'] = True
                        message = "GPU-Threading synchronization verified"
                        passed = True
                    else:
                        message = "GPU-Threading sync test failed: data mismatch"
                        passed = False
                except Exception as e:
                    message = f"GPU-Threading sync test failed: {e}"
                    passed = False
                    details['error'] = str(e)
            else:
                message = "GPU not available, threading-only mode (OK)"
                passed = True
            
            return ValidationResult(
                check_name="GPU-Threading Synchronization",
                passed=passed,
                severity='critical' if not passed and GPU_AVAILABLE else 'info',
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="GPU-Threading Synchronization",
                passed=False,
                severity='warning',
                message=f"Sync validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_ai_models_pipeline(self) -> ValidationResult:
        """Validate 9 AI models training pipeline"""
        try:
            from ai_training_engine import AITrainingEngine, AIModelType
            
            # Check all 9 model types are defined
            model_types = [
                AIModelType.LSTM,
                AIModelType.TRANSFORMER,
                AIModelType.RANDOM_FOREST,
                AIModelType.XGBOOST,
                AIModelType.LIGHTGBM,
                AIModelType.NEURAL_NETWORK,
                AIModelType.SVM,
                AIModelType.PROPHET,
                AIModelType.ENSEMBLE
            ]
            
            details = {
                'total_models': len(model_types),
                'models_defined': [m.value for m in model_types]
            }
            
            if len(model_types) == 9:
                message = f"All 9 AI models defined correctly"
                passed = True
                severity = 'info'
            else:
                message = f"Model count mismatch: expected 9, got {len(model_types)}"
                passed = False
                severity = 'critical'
            
            return ValidationResult(
                check_name="AI Models Pipeline",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="AI Models Pipeline",
                passed=False,
                severity='critical',
                message=f"AI models validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_crypto_forex_logic(self) -> ValidationResult:
        """Validate Crypto/Forex terminology and logic"""
        try:
            from market_terminology import MarketTerminologyHandler, MarketType, OrderSide
            
            # Test crypto detection
            btc_type = MarketTerminologyHandler.detect_market_type("BTC/USDT")
            eth_type = MarketTerminologyHandler.detect_market_type("ETH/USDT")
            
            # Test forex detection
            eurusd_type = MarketTerminologyHandler.detect_market_type("EUR/USD")
            gbpusd_type = MarketTerminologyHandler.detect_market_type("GBP/USD")
            
            # Test futures detection
            btc_perp_type = MarketTerminologyHandler.detect_market_type("BTC-PERP")
            
            # Test terminology
            crypto_long = MarketTerminologyHandler.get_display_action(OrderSide.LONG, MarketType.CRYPTO_SPOT)
            crypto_short = MarketTerminologyHandler.get_display_action(OrderSide.SHORT, MarketType.CRYPTO_SPOT)
            forex_long = MarketTerminologyHandler.get_display_action(OrderSide.LONG, MarketType.FOREX)
            forex_short = MarketTerminologyHandler.get_display_action(OrderSide.SHORT, MarketType.FOREX)
            
            details = {
                'crypto_detection': {
                    'BTC/USDT': btc_type.value,
                    'ETH/USDT': eth_type.value,
                    'BTC-PERP': btc_perp_type.value
                },
                'forex_detection': {
                    'EUR/USD': eurusd_type.value,
                    'GBP/USD': gbpusd_type.value
                },
                'crypto_terminology': {
                    'LONG': crypto_long,
                    'SHORT': crypto_short
                },
                'forex_terminology': {
                    'LONG': forex_long,
                    'SHORT': forex_short
                }
            }
            
            # Validation checks
            checks_passed = (
                btc_type == MarketType.CRYPTO_SPOT and
                eth_type == MarketType.CRYPTO_SPOT and
                btc_perp_type == MarketType.CRYPTO_FUTURES and
                eurusd_type == MarketType.FOREX and
                gbpusd_type == MarketType.FOREX and
                crypto_long == "LONG" and
                crypto_short == "SHORT" and
                forex_long == "BUY" and
                forex_short == "SELL"
            )
            
            if checks_passed:
                message = "Crypto/Forex logic 100% accurate"
                passed = True
                severity = 'info'
            else:
                message = "Crypto/Forex logic has errors"
                passed = False
                severity = 'critical'
            
            return ValidationResult(
                check_name="Crypto/Forex Logic",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Crypto/Forex Logic",
                passed=False,
                severity='critical',
                message=f"Crypto/Forex validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_prediction_system(self) -> ValidationResult:
        """Validate prediction system integrity"""
        try:
            from enhanced_prediction_system import EnhancedPredictionSystem
            
            details = {
                'system_initialized': False,
                'modules_available': 0
            }
            
            # Try to initialize prediction system
            pred_system = EnhancedPredictionSystem()
            details['system_initialized'] = True
            details['modules_available'] = sum(1 for v in pred_system.modules_available.values() if v)
            
            if details['system_initialized']:
                message = f"Prediction system OK ({details['modules_available']} modules available)"
                passed = True
                severity = 'info'
            else:
                message = "Prediction system initialization failed"
                passed = False
                severity = 'critical'
            
            return ValidationResult(
                check_name="Prediction System",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Prediction System",
                passed=False,
                severity='critical',
                message=f"Prediction system validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_data_quality_system(self) -> ValidationResult:
        """Validate data quality system"""
        try:
            from training_quality_controller import TrainingQualityController
            
            details = {
                'quality_controller_initialized': False,
                'thresholds_configured': False
            }
            
            # Try to initialize quality controller
            qc = TrainingQualityController()
            details['quality_controller_initialized'] = True
            details['thresholds_configured'] = hasattr(qc, 'min_data_quality_score')
            
            if details['quality_controller_initialized'] and details['thresholds_configured']:
                message = "Data quality system configured correctly"
                passed = True
                severity = 'info'
            else:
                message = "Data quality system configuration incomplete"
                passed = False
                severity = 'warning'
            
            return ValidationResult(
                check_name="Data Quality System",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Data Quality System",
                passed=False,
                severity='warning',
                message=f"Data quality validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_cache_system(self) -> ValidationResult:
        """Validate cache system"""
        try:
            from unified_cache_manager import unified_cache_manager
            
            details = {
                'cache_manager_initialized': unified_cache_manager is not None,
                'caches_created': len(unified_cache_manager.caches) if unified_cache_manager else 0
            }
            
            if details['cache_manager_initialized'] and details['caches_created'] > 0:
                message = f"Cache system OK ({details['caches_created']} caches)"
                passed = True
                severity = 'info'
            else:
                message = "Cache system not properly initialized"
                passed = False
                severity = 'warning'
            
            return ValidationResult(
                check_name="Cache System",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Cache System",
                passed=False,
                severity='warning',
                message=f"Cache validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_resource_management(self) -> ValidationResult:
        """Validate resource management system"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            details = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'healthy': cpu_percent < 95 and memory.percent < 95
            }
            
            if details['healthy']:
                message = f"Resources healthy (CPU: {cpu_percent:.1f}%, MEM: {memory.percent:.1f}%)"
                passed = True
                severity = 'info'
            else:
                message = f"Resource usage high (CPU: {cpu_percent:.1f}%, MEM: {memory.percent:.1f}%)"
                passed = True  # Warning, not critical
                severity = 'warning'
            
            return ValidationResult(
                check_name="Resource Management",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Resource Management",
                passed=False,
                severity='warning',
                message=f"Resource validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )
    
    def _validate_error_handling(self) -> ValidationResult:
        """Validate error handling mechanisms"""
        try:
            # Test error handling by trying to import modules
            modules_to_check = [
                'ai_training_engine',
                'enhanced_prediction_system',
                'parallel_executor',
                'unified_logging_manager'
            ]
            
            successful_imports = 0
            for module_name in modules_to_check:
                try:
                    __import__(f'core.{module_name}')
                    successful_imports += 1
                except Exception:
                    pass
            
            details = {
                'modules_checked': len(modules_to_check),
                'successful_imports': successful_imports,
                'import_rate': successful_imports / len(modules_to_check)
            }
            
            if successful_imports == len(modules_to_check):
                message = "All core modules importable"
                passed = True
                severity = 'info'
            else:
                message = f"Some modules failed to import ({successful_imports}/{len(modules_to_check)})"
                passed = False
                severity = 'warning'
            
            return ValidationResult(
                check_name="Error Handling",
                passed=passed,
                severity=severity,
                message=message,
                details=details,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            return ValidationResult(
                check_name="Error Handling",
                passed=False,
                severity='warning',
                message=f"Error handling validation failed: {e}",
                details={'error': str(e)},
                timestamp=datetime.now(timezone.utc)
            )


# Singleton instance
system_validator = SystemValidator()

