"""
GOD MODE 10000 - Core Module Exports
====================================
Centralized imports for all core modules
ZERO CIRCULAR IMPORTS - CLEAN ARCHITECTURE
ZERO WRAPPERS/FALLBACKS - REAL DATA ONLY
"""

# CRITICAL: Fix Python 3.13 _pyrepl bug FIRST before any other imports
import python313_compatibility

# Core functionality exports
from unified_logging_manager import unified_logging
from unified_config import unified_config
from market_constants import market_constants

# Authentication & Security
from authentication_manager import authentication_manager, Permission, UserRole, UserStatus

# Market Data
from real_market_data_fetcher import real_market_data_fetcher
from forex_market_data_fetcher import forex_market_data_fetcher

# AI & Prediction - LAZY LOADING to avoid circular imports
# These will be imported when needed, not at module level

# Trading
from advanced_trading_bot import advanced_trading_bot
from portfolio_manager import portfolio_manager
from dca_bot import dca_bot

# Analysis
from advanced_backtesting import advanced_backtesting_engine as backtesting_engine
from onchain_tokenomics_analyzer import onchain_tokenomics_analyzer
from regime_detection import regime_detection_engine as regime_detection
from kol_influence_tracker import kol_influence_tracker
from whale_wallet_monitor import whale_wallet_monitor

# Advanced Features
from portfolio_visualizer import portfolio_visualizer
from funding_rate_tracker import funding_rate_tracker
from order_book_analyzer import order_book_analyzer
from news_aggregator import news_aggregator
from pattern_recognition import pattern_recognition
from multi_timeframe_analyzer import multi_timeframe_analyzer

# System
from smart_alert_system import smart_alert_system
from advanced_search_engine import advanced_search_engine
from airdrop_manager import airdrop_manager
from system_validator import system_validator
# performance_optimizer, system_health_manager, system_warmup merged into intelligent_resource_manager
# batch_processor, distributed_computing merged into parallel_executor
# settings_manager merged into unified_config
# training_progress_tracker merged into ai_training_engine

# God Mode 2000 - Advanced Features (LAZY LOADING to avoid circular imports)
# These modules may contain pandas imports - loaded on-demand
def _lazy_import_god_mode_2000():
    """Lazy import God Mode 2000 features to avoid circular pandas import"""
    global risk_management, RiskMetrics, PositionSize
    global advanced_analytics, CorrelationAnalysis, ClusterResult, MonteCarloResult
    global tax_calculator, TaxReport, TaxMethod, TransactionType
    global social_trading, TraderProfile, TradingSignal, TraderTier
    global mobile_api, APIResponse, WebSocketMessage
    global blockchain_integration, BlockchainNetwork, DeFiPosition
    
    from risk_management import risk_management, RiskMetrics, PositionSize
    from advanced_analytics import advanced_analytics, CorrelationAnalysis, ClusterResult, MonteCarloResult
    from tax_calculator import tax_calculator, TaxReport, TaxMethod, TransactionType
    from social_trading import social_trading, TraderProfile, TradingSignal, TraderTier
    from mobile_api import mobile_api, APIResponse, WebSocketMessage
    from blockchain_integration import blockchain_integration, BlockchainNetwork, DeFiPosition

# God Mode 10000 - Ultra Advanced AI & Trading (LAZY LOADING)
def _lazy_import_god_mode_10000_ai():
    """Lazy import AI modules to avoid circular pandas import"""
    global reinforcement_learning
    global arbitrage_bot, ArbitrageOpportunity, ArbitrageType
    global market_making_bot, MarketMakingOrder
    global advanced_nlp_sentiment, SentimentAnalysis
    global strategy_optimizer, OptimizationResult, ParameterRange
    
    from reinforcement_learning import reinforcement_learning
    from arbitrage_bot import arbitrage_bot, ArbitrageOpportunity, ArbitrageType
    from market_making_bot import market_making_bot, MarketMakingOrder
    from advanced_nlp_sentiment import advanced_nlp_sentiment, SentimentAnalysis
    from strategy_optimizer import strategy_optimizer, OptimizationResult, ParameterRange

# God Mode 10000 - Accuracy Enhancement (LAZY LOADING)
def _lazy_import_accuracy_modules():
    """Lazy import accuracy modules to avoid circular pandas import"""
    global ensemble_validator, ModelPerformance
    global order_flow_tracker, OrderFlowMetrics
    global volatility_forecaster, VolatilityForecast
    
    from ensemble_validator import ensemble_validator, ModelPerformance
    from order_flow_tracker import order_flow_tracker, OrderFlowMetrics
    from volatility_forecaster import volatility_forecaster, VolatilityForecast

# God Mode 10000 - Complete Features (LAZY LOADING)
def _lazy_import_complete_features():
    """Lazy import complete features to avoid circular pandas import"""
    global meta_ai_content, ContentTemplate
    global shap_explainer, SHAPExplanation, SHAPFactor
    global performance_tracker, PerformanceMetrics, TradeResult
    global data_source_validator, DataSourceStatus
    global training_quality_controller, DataQualityReport, FeatureImportance, TrainingQualityMetrics
    global signal_aggregator, AggregatedSignal, SignalStrength
    
    from meta_ai_content_generator import meta_ai_content, ContentTemplate
    from shap_explainer import shap_explainer, SHAPExplanation, SHAPFactor
    from performance_tracker import performance_tracker, PerformanceMetrics, TradeResult
    from data_source_validator import data_source_validator, DataSourceStatus
    from training_quality_controller import training_quality_controller, DataQualityReport, FeatureImportance, TrainingQualityMetrics
    from signal_aggregator import signal_aggregator, AggregatedSignal, SignalStrength

# God Mode 10000 - Prediction System (LAZY LOADING)
def _lazy_import_prediction_system():
    """Lazy import prediction system to avoid circular pandas import"""
    global market_microstructure, smart_money_tracker, cross_asset_correlation
    global liquidity_cascade_detector, network_effect_indicators
    global regime_predictor_advanced, uncertainty_quantification
    
    from enhanced_prediction_system import (
        market_microstructure, smart_money_tracker, cross_asset_correlation,
        liquidity_cascade_detector, network_effect_indicators, 
        regime_predictor_advanced, uncertainty_quantification
    )

# God Mode 10000 - Remaining Advanced Modules (LAZY LOADING)
def _lazy_import_advanced_modules():
    """Lazy import advanced modules to avoid circular pandas import"""
    global execution_optimizer
    global dynamic_risk_adjuster
    global online_learning_system
    global transaction_cost_analyzer
    global multi_strategy_coordinator
    global alternative_data_integrator
    global position_manager_advanced, PositionAction
    global anomaly_detector
    global feature_store
    global smart_order_manager
    global copy_trading_system
    global real_trading_execution
    global dex_trading_integration
    global market_making_optimizer
    global latency_arbitrage_detector
    global model_ensemble_optimizer
    
    from execution_quality_optimizer import execution_optimizer
    from dynamic_risk_adjuster import dynamic_risk_adjuster
    from online_learning_system import online_learning_system
    from transaction_cost_analyzer import transaction_cost_analyzer
    from multi_strategy_coordinator import multi_strategy_coordinator
    from alternative_data_integrator import alternative_data_integrator
    from portfolio_manager import position_manager_advanced, PositionAction
    from anomaly_detector import anomaly_detector
    from unified_cache_manager import feature_store
    from smart_order_types import smart_order_manager
    from copy_trading_system import copy_trading_system
    from real_trading_execution import real_trading_execution
    from dex_trading_integration import dex_trading_integration
    from market_making_optimizer import market_making_optimizer
    from latency_arbitrage_detector import latency_arbitrage_detector
    from model_ensemble_optimizer import model_ensemble_optimizer

# Initialize lazy imports on first access
_lazy_loaded = {
    'god_mode_2000': False,
    'god_mode_10000_ai': False,
    'accuracy_modules': False,
    'complete_features': False,
    'prediction_system': False,
    'advanced_modules': False
}

def __getattr__(name):
    """Lazy load modules on first access to avoid circular imports"""
    # God Mode 2000
    if name in ['risk_management', 'RiskMetrics', 'PositionSize', 'advanced_analytics', 
                'CorrelationAnalysis', 'ClusterResult', 'MonteCarloResult', 'tax_calculator',
                'TaxReport', 'TaxMethod', 'TransactionType', 'social_trading', 'TraderProfile',
                'TradingSignal', 'TraderTier', 'mobile_api', 'APIResponse', 'WebSocketMessage',
                'blockchain_integration', 'BlockchainNetwork', 'DeFiPosition']:
        if not _lazy_loaded['god_mode_2000']:
            _lazy_import_god_mode_2000()
            _lazy_loaded['god_mode_2000'] = True
        return globals()[name]
    
    # God Mode 10000 AI
    if name in ['reinforcement_learning', 'arbitrage_bot', 'ArbitrageOpportunity', 'ArbitrageType',
                'market_making_bot', 'MarketMakingOrder', 'advanced_nlp_sentiment', 'SentimentAnalysis',
                'strategy_optimizer', 'OptimizationResult', 'ParameterRange']:
        if not _lazy_loaded['god_mode_10000_ai']:
            _lazy_import_god_mode_10000_ai()
            _lazy_loaded['god_mode_10000_ai'] = True
        return globals()[name]
    
    # Accuracy modules
    if name in ['ensemble_validator', 'ModelPerformance', 'order_flow_tracker', 'OrderFlowMetrics',
                'volatility_forecaster', 'VolatilityForecast']:
        if not _lazy_loaded['accuracy_modules']:
            _lazy_import_accuracy_modules()
            _lazy_loaded['accuracy_modules'] = True
        return globals()[name]
    
    # Complete features
    if name in ['meta_ai_content', 'ContentTemplate', 'shap_explainer', 'SHAPExplanation', 'SHAPFactor',
                'performance_tracker', 'PerformanceMetrics', 'TradeResult', 'data_source_validator',
                'DataSourceStatus', 'training_quality_controller', 'DataQualityReport', 'FeatureImportance',
                'TrainingQualityMetrics', 'signal_aggregator', 'AggregatedSignal', 'SignalStrength']:
        if not _lazy_loaded['complete_features']:
            _lazy_import_complete_features()
            _lazy_loaded['complete_features'] = True
        return globals()[name]
    
    # Prediction system
    if name in ['market_microstructure', 'smart_money_tracker', 'cross_asset_correlation',
                'liquidity_cascade_detector', 'network_effect_indicators', 'regime_predictor_advanced',
                'uncertainty_quantification']:
        if not _lazy_loaded['prediction_system']:
            _lazy_import_prediction_system()
            _lazy_loaded['prediction_system'] = True
        return globals()[name]
    
    # Advanced modules
    if name in ['execution_optimizer', 'dynamic_risk_adjuster', 'online_learning_system',
                'transaction_cost_analyzer', 'multi_strategy_coordinator', 'alternative_data_integrator',
                'position_manager_advanced', 'PositionAction', 'anomaly_detector', 'feature_store',
                'smart_order_manager', 'copy_trading_system', 'real_trading_execution',
                'dex_trading_integration', 'market_making_optimizer', 'latency_arbitrage_detector',
                'model_ensemble_optimizer']:
        if not _lazy_loaded['advanced_modules']:
            _lazy_import_advanced_modules()
            _lazy_loaded['advanced_modules'] = True
        return globals()[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    # Core
    'unified_logging',
    'unified_config',
    'market_constants',
    
    # Authentication
    'authentication_manager',
    'Permission',
    'UserRole',
    'UserStatus',
    
    # Market Data
    'real_market_data_fetcher',
    'forex_market_data_fetcher',
    
    # AI & Prediction
    'ai_integration_manager',
    'ai_training_engine',
    'ai_self_correction',
    'enhanced_prediction_system',
    
    # Trading
    'advanced_trading_bot',
    'portfolio_manager',
    'dca_bot',
    
    # Analysis
    'backtesting_engine',
    'onchain_tokenomics_analyzer',
    'regime_detection',
    'kol_influence_tracker',
    'whale_wallet_monitor',
    
    # Advanced Features
    'portfolio_visualizer',
    'funding_rate_tracker',
    'order_book_analyzer',
    'news_aggregator',
    'pattern_recognition',
    'multi_timeframe_analyzer',
    
    # System
    'smart_alert_system',
    'advanced_search_engine',
    'airdrop_manager',
    # 'performance_optimizer', 'system_health_manager', 'system_warmup' - merged into intelligent_resource_manager
    # 'batch_processor', 'distributed_computing' - merged into parallel_executor  
    # 'settings_manager' - merged into unified_config
    # 'training_progress_tracker' - merged into ai_training_engine
    
    # God Mode 2000
    'risk_management',
    'RiskMetrics',
    'PositionSize',
    'advanced_analytics',
    'CorrelationAnalysis',
    'ClusterResult',
    'MonteCarloResult',
    'tax_calculator',
    'TaxReport',
    'TaxMethod',
    'TransactionType',
    'social_trading',
    'TraderProfile',
    'TradingSignal',
    'TraderTier',
    'mobile_api',
    'APIResponse',
    'WebSocketMessage',
    'blockchain_integration',
    'BlockchainNetwork',
    'DeFiPosition',
    
    # God Mode 10000
    'reinforcement_learning',
    'arbitrage_bot',
    'ArbitrageOpportunity',
    'ArbitrageType',
    'market_making_bot',
    'MarketMakingOrder',
    'advanced_nlp_sentiment',
    'SentimentAnalysis',
    'strategy_optimizer',
    'OptimizationResult',
    'ParameterRange',
    
    # God Mode 10000 - Accuracy Enhancement
    'ensemble_validator',
    'ModelPerformance',
    'order_flow_tracker',
    'OrderFlowMetrics',
    'volatility_forecaster',
    'VolatilityForecast',
    
    # God Mode 10000 - Complete Features
    'meta_ai_content',
    'ContentTemplate',
    'shap_explainer',
    'SHAPExplanation',
    'SHAPFactor',
    'performance_tracker',
    'PerformanceMetrics',
    'TradeResult',
    'data_source_validator',
    'DataSourceStatus',
    'training_quality_controller',
    'DataQualityReport',
    'FeatureImportance',
    'TrainingQualityMetrics',
    # 'adaptive_learning_engine' removed - merged into online_learning_system
    'signal_aggregator',
    'AggregatedSignal',
    'SignalStrength',
    
    # God Mode 10000 - NEW Advanced Modules
    'market_microstructure',
    'smart_money_tracker',
    'execution_optimizer',
    'dynamic_risk_adjuster',
    'uncertainty_quantification',
    'cross_asset_correlation',
    'liquidity_cascade_detector',
    'online_learning_system',
    'transaction_cost_analyzer',
    'network_effect_indicators',
    'regime_predictor_advanced',
    'multi_strategy_coordinator',
    'alternative_data_integrator',
    'position_manager_advanced',
    'anomaly_detector',
    'feature_store',
    'smart_order_manager',
    'copy_trading_system',
    'real_trading_execution',
    'dex_trading_integration',
    
    # God Mode 10000 - Additional Advanced Features
    'market_making_optimizer',
    'latency_arbitrage_detector',
    'model_ensemble_optimizer'
]
