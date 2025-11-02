"""
[STAR] GOD MODE 1000 - UNIFIED CONFIGURATION SYSTEM 💫
=====================================================
[START] CENTRALIZED CONFIGURATION MANAGEMENT
[FAST] ZERO DUPLICATES - UNIFIED ARCHITECTURE
[BULLSEYE] PRODUCTION-GRADE CONFIGURATION SYSTEM

UNIFIED CONFIGURATION CAPABILITIES:
- Centralized configuration management
- Dynamic configuration updates
- Environment-specific settings
- Performance-optimized configuration access
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
# Removed threading imports to avoid ScriptRunContext warnings
from datetime import datetime, timedelta

@dataclass
class ConfigEntry:
    """Configuration entry structure"""
    key: str
    value: Any
    default: Any
    description: str = ""
    category: str = "general"
    last_updated: datetime = field(default_factory=datetime.now)
    source: str = "default"

class UnifiedConfig:
    """Unified configuration manager for God Mode 1000"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.config: Dict[str, ConfigEntry] = {}
        # Removed threading lock to avoid ScriptRunContext warnings
        
        # Load default configurations
        self._load_default_config()
        self._load_environment_config()
        self._load_user_config()
    
    def _load_default_config(self):
        """Load default configuration values"""
        default_configs = {
            # AI Engine Configuration - Dynamic values based on market conditions
            'ai.target_accuracy': {'value': 0.90, 'default': 0.90, 'description': 'Target accuracy for AI models (dynamic based on market volatility)', 'category': 'ai'},
            'ai.training_steps': {'value': 35, 'default': 35, 'description': 'Number of training steps (adaptive based on data quality)', 'category': 'ai'},
            'ai.models_count': {'value': 9, 'default': 9, 'description': 'Number of AI models (ensemble size)', 'category': 'ai'},
            'ai.pipeline_stages': {'value': 5, 'default': 5, 'description': 'Number of AI pipeline stages (data->features->models->ensemble->prediction)', 'category': 'ai'},
            # AI model selection and availability
            'ai.default_model': {'value': 'gpt-5-mini', 'default': 'gpt-5-mini', 'description': 'Default AI model identifier used for inference and orchestration', 'category': 'ai'},
            'ai.available_models': {'value': ['gpt-5-mini', 'gpt-4o-mini', 'local-llm'], 'default': ['gpt-5-mini', 'gpt-4o-mini', 'local-llm'], 'description': 'List of available AI models supported by the system', 'category': 'ai'},
            'ai.enable_model_for_all_clients': {'value': True, 'default': True, 'description': 'If true, the default AI model will be used for all clients unless overridden', 'category': 'ai'},
            
            # Data Engine Configuration
            'data.update_interval': {'value': 60, 'default': 60, 'description': 'Data update interval in seconds', 'category': 'data'},
            'data.cache_ttl': {'value': 300, 'default': 300, 'description': 'Cache TTL in seconds', 'category': 'data'},
            'data.max_retries': {'value': 3, 'default': 3, 'description': 'Maximum retry attempts', 'category': 'data'},
            
            # Trading Configuration
            'trading.max_positions': {'value': 5, 'default': 5, 'description': 'Maximum concurrent positions', 'category': 'trading'},
            'trading.risk_limit': {'value': 0.05, 'default': 0.05, 'description': 'Risk limit per trade', 'category': 'trading'},
            'trading.stop_loss': {'value': 0.02, 'default': 0.02, 'description': 'Default stop loss percentage', 'category': 'trading'},
            
            # Portfolio Configuration
            'portfolio.rebalance_threshold': {'value': 0.1, 'default': 0.1, 'description': 'Portfolio rebalance threshold', 'category': 'portfolio'},
            'portfolio.max_drawdown': {'value': 0.15, 'default': 0.15, 'description': 'Maximum allowed drawdown', 'category': 'portfolio'},
            
            # Notification Configuration
            'notifications.enabled': {'value': True, 'default': True, 'description': 'Enable notifications', 'category': 'notifications'},
            'notifications.telegram_enabled': {'value': False, 'default': False, 'description': 'Enable Telegram notifications', 'category': 'notifications'},
            'notifications.email_enabled': {'value': False, 'default': False, 'description': 'Enable email notifications', 'category': 'notifications'},
            
            # Performance Configuration
            'performance.max_workers': {'value': 64, 'default': 64, 'description': 'Maximum worker threads', 'category': 'performance'},
            'performance.worker_multiplier': {'value': 8, 'default': 8, 'description': 'CPU core multiplier for worker threads', 'category': 'performance'},
            'performance.cache_size': {'value': 1000, 'default': 1000, 'description': 'Cache size limit', 'category': 'performance'},
            'performance.timeout': {'value': 30, 'default': 30, 'description': 'Default timeout in seconds', 'category': 'performance'},
            'performance.mode': {'value': 'maximum', 'default': 'maximum', 'description': 'Performance mode: maximum, balanced, conservative', 'category': 'performance'},
            'performance.auto_scale_enabled': {'value': True, 'default': True, 'description': 'Enable automatic scaling', 'category': 'performance'},
            'performance.cpu_critical': {'value': 98.0, 'default': 98.0, 'description': 'CPU critical threshold (%)', 'category': 'performance'},
            'performance.cpu_danger': {'value': 95.0, 'default': 95.0, 'description': 'CPU danger threshold (%)', 'category': 'performance'},
            'performance.cpu_warning': {'value': 90.0, 'default': 90.0, 'description': 'CPU warning threshold (%)', 'category': 'performance'},
            'performance.ram_critical': {'value': 97.0, 'default': 97.0, 'description': 'RAM critical threshold (%)', 'category': 'performance'},
            'performance.ram_danger': {'value': 93.0, 'default': 93.0, 'description': 'RAM danger threshold (%)', 'category': 'performance'},
            'performance.ram_warning': {'value': 88.0, 'default': 88.0, 'description': 'RAM warning threshold (%)', 'category': 'performance'},
            'performance.gpu_critical': {'value': 98.0, 'default': 98.0, 'description': 'GPU critical threshold (%)', 'category': 'performance'},
            'performance.gpu_danger': {'value': 95.0, 'default': 95.0, 'description': 'GPU danger threshold (%)', 'category': 'performance'},
            'performance.gpu_warning': {'value': 90.0, 'default': 90.0, 'description': 'GPU warning threshold (%)', 'category': 'performance'},
            # Production strictness guard - when true, modules must not use demo/fallback logic
            'production.strict': {'value': True, 'default': True, 'description': 'When true, disable demo/fallback behavior and require adapters for external systems', 'category': 'general'},
            # When true, enforce adapters for critical data domains and fail startup if missing
            'production.enforce_adapters': {'value': False, 'default': False, 'description': 'When true, require adapters for market/onchain/orderbook/news and fail startup if missing', 'category': 'general'},
            # List of required adapters/domains for production enforcement
            'production.require_adapters': {'value': ['market', 'onchain', 'orderbook', 'news'], 'default': ['market', 'onchain', 'orderbook', 'news'], 'description': 'List of critical adapter domains required in production', 'category': 'general'},
        }
        
        for key, config_data in default_configs.items():
            self.config[key] = ConfigEntry(
                key=key,
                value=config_data['value'],
                default=config_data['default'],
                description=config_data['description'],
                category=config_data['category'],
                source='default'
            )
    
    def _load_environment_config(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'GOD_MODE_AI_ACCURACY': 'ai.target_accuracy',
            'GOD_MODE_MAX_WORKERS': 'performance.max_workers',
            'GOD_MODE_CACHE_SIZE': 'performance.cache_size',
            'GOD_MODE_TELEGRAM_ENABLED': 'notifications.telegram_enabled',
            'GOD_MODE_EMAIL_ENABLED': 'notifications.email_enabled',
            'GOD_MODE_PRODUCTION_STRICT': 'production.strict',
            'GOD_MODE_ENFORCE_ADAPTERS': 'production.enforce_adapters',
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                if config_key in ['ai.target_accuracy', 'trading.risk_limit', 'trading.stop_loss', 'portfolio.rebalance_threshold', 'portfolio.max_drawdown']:
                    value = float(env_value)
                elif config_key in ['ai.training_steps', 'ai.models_count', 'ai.pipeline_stages', 'data.update_interval', 'data.cache_ttl', 'data.max_retries', 'trading.max_positions', 'performance.max_workers', 'performance.cache_size', 'performance.timeout']:
                    value = int(env_value)
                elif config_key in ['notifications.enabled', 'notifications.telegram_enabled', 'notifications.email_enabled', 'production.strict']:
                    value = env_value.lower() in ('true', '1', 'yes', 'on')
                else:
                    value = env_value
                
                if config_key in self.config:
                    self.config[config_key].value = value
                    self.config[config_key].source = 'environment'
                else:
                    self.config[config_key] = ConfigEntry(
                        key=config_key,
                        value=value,
                        default=value,
                        source='environment'
                    )
    
    def _load_user_config(self):
        """Load user configuration from config files"""
        config_files = [
            'config.json',
            'config.yaml',
            'config.yml',
            'god_mode_config.json'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    if config_file.endswith('.json'):
                        with open(config_path, 'r') as f:
                            user_config = json.load(f)
                    elif config_file.endswith(('.yaml', '.yml')):
                        with open(config_path, 'r') as f:
                            user_config = yaml.safe_load(f)
                    else:
                        continue
                    
                    self._update_config_from_dict(user_config, 'user_file')
                    break
                except Exception as e:
                    print(f"Warning: Failed to load config file {config_file}: {e}")
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any], source: str = 'user'):
        """Update configuration from dictionary"""
        def _update_nested_config(d, prefix=''):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    _update_nested_config(value, full_key)
                else:
                    if full_key in self.config:
                        self.config[full_key].value = value
                        self.config[full_key].source = source
                        self.config[full_key].last_updated = datetime.now()
                    else:
                        self.config[full_key] = ConfigEntry(
                            key=full_key,
                            value=value,
                            default=value,
                            source=source
                        )
        
        _update_nested_config(config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if key in self.config:
            return self.config[key].value
        return default
    
    def set(self, key: str, value: Any, description: str = "", category: str = "general"):
        """Set configuration value"""
        if key in self.config:
            self.config[key].value = value
            self.config[key].last_updated = datetime.now()
            if description:
                self.config[key].description = description
            if category:
                self.config[key].category = category
        else:
                self.config[key] = ConfigEntry(
                    key=key,
                    value=value,
                    default=value,
                    description=description,
                    category=category,
                    source='runtime'
                )
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all configuration values for a category"""
        return {
            key: entry.value
            for key, entry in self.config.items()
            if entry.category == category
        }
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return {key: entry.value for key, entry in self.config.items()}
    
    def reset_to_default(self, key: str):
        """Reset configuration value to default"""
        if key in self.config:
                self.config[key].value = self.config[key].default
                self.config[key].last_updated = datetime.now()
    
    def export_config(self, filename: str = "god_mode_config.json"):
        """Export current configuration to file"""
        export_data = {}
        for key, entry in self.config.items():
            export_data[key] = {
                'value': entry.value,
                'default': entry.default,
                'description': entry.description,
                'category': entry.category,
                'source': entry.source
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def get_config_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed configuration information"""
        if key in self.config:
                entry = self.config[key]
                return {
                    'key': entry.key,
                    'value': entry.value,
                    'default': entry.default,
                    'description': entry.description,
                    'category': entry.category,
                    'source': entry.source,
                    'last_updated': entry.last_updated
                }
        return None

# Create singleton instance
unified_config = UnifiedConfig()

# Backward compatibility
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value (backward compatibility)"""
    return unified_config.get(key, default)

def set_config(key: str, value: Any, description: str = "", category: str = "general"):
    """Set configuration value (backward compatibility)"""
    unified_config.set(key, value, description, category)
