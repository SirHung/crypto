"""
GOD MODE 1000 - SMART ALERT SYSTEM
Intelligent price alerts with multi-condition triggers
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import warnings
warnings.filterwarnings('ignore')

try:
    from unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

try:
    from notification_system import notification_system
except ImportError:
    notification_system = None

try:
    from real_market_data_fetcher import real_market_data_fetcher
except ImportError:
    real_market_data_fetcher = None

class AlertCondition(Enum):
    """Alert trigger conditions"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE_PCT = "price_change_pct"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"

class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class PriceAlert:
    """Smart price alert"""
    alert_id: str
    symbol: str
    condition: AlertCondition
    target_value: float
    current_value: float = 0.0
    triggered: bool = False
    trigger_time: Optional[datetime] = None
    priority: AlertPriority = AlertPriority.MEDIUM
    message: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

class SmartAlertSystem:
    """Intelligent multi-condition alert system"""
    
    def __init__(self):
        """Initialize smart alert system"""
        try:
            self.unified_logger = unified_logging.get_logger("smart_alerts")
            
            self.active_alerts: Dict[str, PriceAlert] = {}
            self.triggered_alerts: List[PriceAlert] = []
            self.monitoring_active = False
            self.check_interval = 10  # Check every 10 seconds
            
            self.unified_logger.info("Smart Alert System initialized")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to initialize alert system: {e}")
            raise
    
    def create_price_alert(self, symbol: str, condition: AlertCondition, 
                          target_value: float, priority: AlertPriority = AlertPriority.MEDIUM) -> str:
        """Create new price alert"""
        try:
            alert_id = f"alert_{symbol}_{int(datetime.now().timestamp())}"
            
            message = self._generate_alert_message(symbol, condition, target_value)
            
            alert = PriceAlert(
                alert_id=alert_id,
                symbol=symbol,
                condition=condition,
                target_value=target_value,
                priority=priority,
                message=message
            )
            
            self.active_alerts[alert_id] = alert
            self.unified_logger.info(f"Created alert: {alert_id}")
            
            return alert_id
            
        except Exception as e:
            self.unified_logger.error(f"Failed to create alert: {e}")
            return ""
    
    def _generate_alert_message(self, symbol: str, condition: AlertCondition, target: float) -> str:
        """Generate alert message"""
        messages = {
            AlertCondition.PRICE_ABOVE: f"{symbol} price above ${target:,.2f}",
            AlertCondition.PRICE_BELOW: f"{symbol} price below ${target:,.2f}",
            AlertCondition.PRICE_CHANGE_PCT: f"{symbol} price changed {target:+.1f}%",
            AlertCondition.VOLUME_SPIKE: f"{symbol} volume spike detected",
            AlertCondition.RSI_OVERBOUGHT: f"{symbol} RSI overbought (>{target})",
            AlertCondition.RSI_OVERSOLD: f"{symbol} RSI oversold (<{target})"
        }
        return messages.get(condition, f"{symbol} alert triggered")
    
    async def check_alerts(self):
        """Check all active alerts"""
        try:
            if not self.active_alerts:
                return
            
            for alert_id, alert in list(self.active_alerts.items()):
                if alert.triggered:
                    continue
                
                # Get current market data
                if real_market_data_fetcher:
                    market_data = real_market_data_fetcher.get_market_data(alert.symbol)
                    if not market_data:
                        continue
                    
                    triggered = False
                    
                    # Check condition
                    if alert.condition == AlertCondition.PRICE_ABOVE:
                        alert.current_value = market_data['price']
                        if market_data['price'] >= alert.target_value:
                            triggered = True
                    
                    elif alert.condition == AlertCondition.PRICE_BELOW:
                        alert.current_value = market_data['price']
                        if market_data['price'] <= alert.target_value:
                            triggered = True
                    
                    elif alert.condition == AlertCondition.PRICE_CHANGE_PCT:
                        alert.current_value = market_data['change_24h']
                        if abs(market_data['change_24h']) >= abs(alert.target_value):
                            triggered = True
                    
                    elif alert.condition == AlertCondition.VOLUME_SPIKE:
                        # Volume spike detection
                        volume_avg = alert.metadata.get('volume_avg', market_data['volume_24h'])
                        if market_data['volume_24h'] > volume_avg * alert.target_value:
                            triggered = True
                    
                    if triggered:
                        await self._trigger_alert(alert)
            
        except Exception as e:
            self.unified_logger.error(f"Failed to check alerts: {e}")
    
    async def _trigger_alert(self, alert: PriceAlert):
        """Trigger alert and send notification"""
        try:
            alert.triggered = True
            alert.trigger_time = datetime.now(timezone.utc)
            
            # Move to triggered list
            self.triggered_alerts.append(alert)
            if alert.alert_id in self.active_alerts:
                del self.active_alerts[alert.alert_id]
            
            # Send notification
            if notification_system:
                notification_system.send_notification(
                    title="🔔 Price Alert Triggered",
                    message=f"{alert.message}\nCurrent: {alert.current_value}",
                    priority=alert.priority.value.upper()
                )
            
            self.unified_logger.info(f"Alert triggered: {alert.alert_id}")
            
        except Exception as e:
            self.unified_logger.error(f"Failed to trigger alert: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of active alerts"""
        try:
            return [
                {
                    'alert_id': alert.alert_id,
                    'symbol': alert.symbol,
                    'condition': alert.condition.value,
                    'target_value': alert.target_value,
                    'current_value': alert.current_value,
                    'priority': alert.priority.value,
                    'message': alert.message,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in self.active_alerts.values()
            ]
        except Exception as e:
            self.unified_logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_triggered_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recently triggered alerts"""
        try:
            recent = self.triggered_alerts[-limit:] if len(self.triggered_alerts) > limit else self.triggered_alerts
            return [
                {
                    'alert_id': alert.alert_id,
                    'symbol': alert.symbol,
                    'condition': alert.condition.value,
                    'target_value': alert.target_value,
                    'trigger_value': alert.current_value,
                    'trigger_time': alert.trigger_time.isoformat() if alert.trigger_time else None,
                    'priority': alert.priority.value,
                    'message': alert.message
                }
                for alert in recent
            ]
        except Exception as e:
            self.unified_logger.error(f"Failed to get triggered alerts: {e}")
            return []
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        try:
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
                self.unified_logger.info(f"Deleted alert: {alert_id}")
                return True
            return False
        except Exception as e:
            self.unified_logger.error(f"Failed to delete alert: {e}")
            return False
    
    def start_monitoring(self):
        """Start alert monitoring"""
        try:
            self.monitoring_active = True
            self.unified_logger.info("Alert monitoring started")
        except Exception as e:
            self.unified_logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop alert monitoring"""
        try:
            self.monitoring_active = False
            self.unified_logger.info("Alert monitoring stopped")
        except Exception as e:
            self.unified_logger.error(f"Failed to stop monitoring: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        try:
            return {
                'active_alerts': len(self.active_alerts),
                'triggered_alerts': len(self.triggered_alerts),
                'monitoring_active': self.monitoring_active,
                'check_interval': self.check_interval,
                'last_update': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.unified_logger.error(f"Failed to get stats: {e}")
            return {}

# Global instance
smart_alert_system = SmartAlertSystem()

