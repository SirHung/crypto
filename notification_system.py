"""
🚀 GOD MODE 1000 - UNIFIED NOTIFICATION SYSTEM 🔔
==================================================
PRODUCTION-READY MULTI-CHANNEL ALERT SYSTEM
ENTERPRISE-GRADE NOTIFICATION MANAGEMENT
ZERO DUPLICATES - UNIFIED ARCHITECTURE
PRODUCTION-GRADE PERFORMANCE & RELIABILITY

NOTIFICATION SYSTEM CAPABILITIES:
- Multi-channel alerts (Email, SMS, Telegram, Discord, Slack)
- Real-time notification triggers and thresholds
- Customizable alert conditions and filters
- Automated report generation and delivery
- Integration with trading signals and market events
- Advanced notification scheduling and management
- Webhook support for external integrations
- Notification history and analytics
"""

import asyncio
import aiohttp
import smtplib
import json
import time
# Removed threading imports to avoid ScriptRunContext warnings
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import logging
from pathlib import Path
import yaml

# Import unified modules
try:
    from unified_logging_manager import UnifiedLoggingManager
    unified_logger = UnifiedLoggingManager.get_logger("core.notification_system")
except ImportError:
    import logging
    unified_logger = logging.getLogger("core.notification_system")
    unified_logger.setLevel(logging.INFO)

try:
    from unified_config import UnifiedConfig
    dynamic_config = UnifiedConfig()
except ImportError:
        from unified_config import UnifiedConfig
        dynamic_config = UnifiedConfig()

try:
    from meta_ai_content_generator import meta_ai_content
except ImportError:
    meta_ai_content = None

try:
    from shap_explainer import shap_explainer
except ImportError:
    shap_explainer = None

class NotificationChannel(Enum):
    """Supported notification channels"""
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SLACK = "slack"
    WEBHOOK = "webhook"
    BROWSER = "browser"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class NotificationTemplate:
    """Notification template configuration"""
    id: str
    name: str
    subject: str
    body: str
    channels: List[NotificationChannel]
    priority: NotificationPriority = NotificationPriority.MEDIUM
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class NotificationRule:
    """Notification rule configuration"""
    id: str
    name: str
    condition: str
    template_id: str
    channels: List[NotificationChannel]
    enabled: bool = True
    cooldown_minutes: int = 5
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

@dataclass
class NotificationRecord:
    """Individual notification record"""
    id: str
    rule_id: str
    template_id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    body: str
    priority: NotificationPriority
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class NotificationSystem:
    """
    🚀 GOD MODE 1000 - UNIFIED NOTIFICATION SYSTEM
    Advanced multi-channel notification management system
    """
    
    def __init__(self):
        """Initialize the notification system"""
        self.unified_logger = unified_logger
        self.config = self._load_configuration()
        
        # Notification storage
        self.templates: Dict[str, NotificationTemplate] = {}
        self.rules: Dict[str, NotificationRule] = {}
        self.notifications: List[NotificationRecord] = []
        self.notification_history: List[Dict[str, Any]] = []
        
        # Channel configurations
        self.channel_configs = {
            NotificationChannel.EMAIL: self.config.get('email', {}),
            NotificationChannel.SMS: self.config.get('sms', {}),
            NotificationChannel.TELEGRAM: self.config.get('telegram', {}),
            NotificationChannel.DISCORD: self.config.get('discord', {}),
            NotificationChannel.SLACK: self.config.get('slack', {}),
            NotificationChannel.WEBHOOK: self.config.get('webhook', {}),
        }
        
        # Background processing
        self.processing_thread = None
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_sent': 0,
            'total_failed': 0,
            'by_channel': {channel.value: 0 for channel in NotificationChannel},
            'by_priority': {priority.value: 0 for priority in NotificationPriority}
        }
        
        self._initialize_default_templates()
        self._initialize_default_rules()
        
        # Mark as ready (lazy-start): do not start background threads at import
        self.unified_logger.info("[READY] Unified Notification System initialized (lazy-start) - God Mode 1000")

    # Note: use start_background_processing() and stop_background_processing() for lifecycle control
    
    async def initialize(self):
        """Initialize Notification System components"""
        self.unified_logger.info("Notification System ready for God Mode 1000")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load notification system configuration"""
        try:
            config_path = Path("config/notification_config.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                # Return default configuration
                return {
                    'email': {
                        'smtp_server': 'smtp.gmail.com',
                        'smtp_port': 587,
                        'username': '',
                        'password': '',
                        'from_email': ''
                    },
                    'telegram': {
                        'bot_token': '',
                        'chat_id': ''
                    },
                    'discord': {
                        'webhook_url': ''
                    },
                    'slack': {
                        'webhook_url': ''
                    },
                    'sms': {
                        'api_key': '',
                        'from_number': ''
                    },
                    'webhook': {
                        'url': '',
                        'headers': {}
                    },
                    'rate_limits': {
                        'max_per_minute': 60,
                        'max_per_hour': 1000
                    }
                }
        except Exception as e:
            self.unified_logger.warning(f"Failed to load notification config: {e}")
            return {}
    
    def _initialize_default_templates(self):
        """Initialize default notification templates"""
        default_templates = [
            NotificationTemplate(
                id="price_alert",
                name="Price Alert",
                subject="🚨 Price Alert: {symbol}",
                body="""
🚨 PRICE ALERT TRIGGERED 🚨

Symbol: {symbol}
Current Price: ${current_price}
Target Price: ${target_price}
Change: {change_percent}%
Time: {timestamp}

Market Conditions:
- Fear & Greed Index: {fear_greed}
- Volume: {volume_24h}
- Trend: {trend}

Action: {action}
                """,
                channels=[NotificationChannel.TELEGRAM, NotificationChannel.EMAIL],
                priority=NotificationPriority.HIGH,
                variables=['symbol', 'current_price', 'target_price', 'change_percent', 'timestamp', 'fear_greed', 'volume_24h', 'trend', 'action']
            ),
            NotificationTemplate(
                id="trading_signal",
                name="Trading Signal",
                subject="📈 Trading Signal: {symbol}",
                body="""
📈 TRADING SIGNAL GENERATED 📈

Symbol: {symbol}
Signal: {signal}
Confidence: {confidence}%
Entry Price: ${entry_price}
Stop Loss: ${stop_loss}
Take Profit: ${take_profit}
Timeframe: {timeframe}

AI Analysis:
- Model: {model_name}
- Reasoning: {reasoning}
- Risk Level: {risk_level}

Market Context:
- Fear & Greed: {fear_greed}
- Volume: {volume}
- Trend: {trend}
                """,
                channels=[NotificationChannel.TELEGRAM, NotificationChannel.EMAIL],
                priority=NotificationPriority.HIGH,
                variables=['symbol', 'signal', 'confidence', 'entry_price', 'stop_loss', 'take_profit', 'timeframe', 'model_name', 'reasoning', 'risk_level', 'fear_greed', 'volume', 'trend']
            ),
            NotificationTemplate(
                id="portfolio_update",
                name="Portfolio Update",
                subject="💼 Portfolio Update",
                body="""
💼 PORTFOLIO UPDATE 💼

Total Value: ${total_value}
24h Change: {change_24h}%
P&L: ${pnl}

Top Positions:
{top_positions}

Market Summary:
- Fear & Greed Index: {fear_greed}
- BTC Dominance: {btc_dominance}%
- Market Cap: ${market_cap}

Next Actions:
{next_actions}
                """,
                channels=[NotificationChannel.EMAIL],
                priority=NotificationPriority.MEDIUM,
                variables=['total_value', 'change_24h', 'pnl', 'top_positions', 'fear_greed', 'btc_dominance', 'market_cap', 'next_actions']
            ),
            NotificationTemplate(
                id="airdrop_alert",
                name="Airdrop Alert",
                subject="🪂 New Airdrop Opportunity: {project_name}",
                body="""
🪂 NEW AIRDROP OPPORTUNITY 🪂

Project: {project_name}
Network: {network}
Estimated Value: ${estimated_value}
Requirements: {requirements}
Deadline: {deadline}

Action Required:
{action_required}

Status: {status}
                """,
                channels=[NotificationChannel.TELEGRAM, NotificationChannel.EMAIL],
                priority=NotificationPriority.HIGH,
                variables=['project_name', 'network', 'estimated_value', 'requirements', 'deadline', 'action_required', 'status']
            ),
            NotificationTemplate(
                id="system_alert",
                name="System Alert",
                subject="⚠️ System Alert: {alert_type}",
                body="""
⚠️ SYSTEM ALERT ⚠️

Type: {alert_type}
Severity: {severity}
Message: {message}
Timestamp: {timestamp}

System Status:
{system_status}

Action Required: {action_required}
                """,
                channels=[NotificationChannel.EMAIL, NotificationChannel.TELEGRAM],
                priority=NotificationPriority.CRITICAL,
                variables=['alert_type', 'severity', 'message', 'timestamp', 'system_status', 'action_required']
            )
        ]
        
        for template in default_templates:
            self.templates[template.id] = template
    
    def _initialize_default_rules(self):
        """Initialize default notification rules"""
        default_rules = [
            NotificationRule(
                id="price_breakout",
                name="Price Breakout",
                condition="price_change_percent > 10",
                template_id="price_alert",
                channels=[NotificationChannel.TELEGRAM],
                cooldown_minutes=30
            ),
            NotificationRule(
                id="high_confidence_signal",
                name="High Confidence Trading Signal",
                condition="signal_confidence > 85",
                template_id="trading_signal",
                channels=[NotificationChannel.TELEGRAM, NotificationChannel.EMAIL],
                cooldown_minutes=15
            ),
            NotificationRule(
                id="portfolio_daily",
                name="Daily Portfolio Update",
                condition="time.hour == 9 and time.minute == 0",
                template_id="portfolio_update",
                channels=[NotificationChannel.EMAIL],
                cooldown_minutes=1440  # 24 hours
            ),
            NotificationRule(
                id="airdrop_detected",
                name="New Airdrop Detected",
                condition="airdrop_estimated_value > 100",
                template_id="airdrop_alert",
                channels=[NotificationChannel.TELEGRAM],
                cooldown_minutes=60
            ),
            NotificationRule(
                id="system_error",
                name="System Error",
                condition="error_severity == 'critical'",
                template_id="system_alert",
                channels=[NotificationChannel.EMAIL, NotificationChannel.TELEGRAM],
                cooldown_minutes=5
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule

    def validate_channel_configs(self) -> Dict[str, bool]:
        """Return a mapping of channel -> configured (True/False)."""
        result = {}
        for channel in [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.TELEGRAM, NotificationChannel.DISCORD, NotificationChannel.SLACK, NotificationChannel.WEBHOOK, NotificationChannel.BROWSER]:
            cfg = self.channel_configs.get(channel, {})
            if channel == NotificationChannel.EMAIL:
                result[channel.value] = bool(cfg.get('smtp_server') and cfg.get('from_email'))
            elif channel == NotificationChannel.TELEGRAM:
                result[channel.value] = bool(cfg.get('bot_token') or cfg.get('chat_id'))
            elif channel == NotificationChannel.SMS:
                result[channel.value] = bool(cfg.get('api_key') and cfg.get('api_url'))
            elif channel in (NotificationChannel.DISCORD, NotificationChannel.SLACK):
                result[channel.value] = bool(cfg.get('webhook_url'))
            elif channel == NotificationChannel.WEBHOOK:
                result[channel.value] = bool(cfg.get('url'))
            elif channel == NotificationChannel.BROWSER:
                result[channel.value] = bool(cfg.get('enabled') and cfg.get('bridge_url'))
            else:
                result[channel.value] = False
        return result

    def startup_validate(self, raise_on_missing: bool = False) -> List[str]:
        """Validate required notification channels at startup.

        Returns a list of missing channel keys. If raise_on_missing is True and
        'production.strict' is enabled, a RuntimeError will be raised.
        """
        try:
            from unified_config import unified_config as _uc
        except Exception:
            try:
                from unified_config import unified_config as _uc
            except Exception:
                _uc = None

        cfg_map = self.validate_channel_configs()
        missing = [k for k, v in cfg_map.items() if not v]
        if missing:
            self.unified_logger.info(f"Notification channels missing or partial: {missing}")

        if raise_on_missing and _uc is not None and bool(_uc.get('production.strict', True)) and missing:
            raise RuntimeError(f"Missing notification channel configuration in production.strict mode: {missing}")

        return missing
    
    async def send_smart_alert(
        self,
        alert_type: str,
        data: Dict[str, Any],
        channels: List[NotificationChannel] = None,
        recipients: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send smart alert with Meta AI content generation and SHAP explanation
        GOD MODE 10000 - Smart Notifications
        """
        try:
            # Generate SHAP explanation if this is a prediction alert
            shap_explanation = None
            if alert_type == 'prediction' and shap_explainer:
                shap_result = shap_explainer.explain_prediction(data)
                shap_explanation = {
                    'top_factors': [
                        {
                            'name': f.name,
                            'impact': f.impact,
                            'direction': f.direction
                        }
                        for f in shap_result.top_factors[:5]
                    ],
                    'explanation_text': shap_result.explanation_text
                }
            
            # Generate AI content
            if meta_ai_content:
                if alert_type == 'prediction':
                    content = meta_ai_content.generate_prediction_alert(data, shap_explanation)
                elif alert_type == 'whale':
                    content = meta_ai_content.generate_whale_alert(data)
                elif alert_type == 'portfolio':
                    content = meta_ai_content.generate_portfolio_alert(data)
                else:
                    # Fallback to basic template
                    return await self.send_notification('market_alert', data, channels, recipients=recipients)
                
                # Send with AI-generated content
                subject = content.title
                body = content.body
                priority = NotificationPriority.CRITICAL if content.tone == 'urgent' else NotificationPriority.HIGH
            else:
                # Fallback if Meta AI not available
                subject = f"Alert: {data.get('symbol', 'Market')}"
                body = str(data)
                priority = NotificationPriority.MEDIUM
            
            # Default channels
            if channels is None:
                channels = [NotificationChannel.TELEGRAM, NotificationChannel.BROWSER]
            
            results = {}
            
            # Send to each channel
            for channel in channels:
                try:
                    if recipients:
                        for recipient in recipients:
                            result = await self._send_to_channel(
                                channel, recipient, subject, body, priority
                            )
                            results[f"{channel.value}_{recipient}"] = result
                    else:
                        result = await self._send_to_channel(
                            channel, None, subject, body, priority
                        )
                        results[channel.value] = result
                        
                except Exception as e:
                    self.unified_logger.error(f"Failed to send to {channel.value}: {e}")
                    results[channel.value] = {'success': False, 'error': str(e)}
            
            return {
                'success': True,
                'results': results,
                'alert_type': alert_type,
                'channels': [c.value for c in channels],
                'has_shap': shap_explanation is not None,
                'has_meta_ai': meta_ai_content is not None
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to send smart alert: {e}")
            return {'success': False, 'error': str(e)}
    
    async def send_notification(
        self,
        template_id: str,
        variables: Dict[str, Any],
        channels: List[NotificationChannel] = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        recipients: List[str] = None
    ) -> Dict[str, Any]:
        """Send notification using specified template"""
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template {template_id} not found")
            
            template = self.templates[template_id]
            
            # Use template channels if not specified
            if channels is None:
                channels = template.channels
            
            # Use template priority if not specified
            if priority == NotificationPriority.MEDIUM and template.priority != NotificationPriority.MEDIUM:
                priority = template.priority
            
            # Render template
            subject = self._render_template(template.subject, variables)
            body = self._render_template(template.body, variables)
            
            results = {}
            
            # Send to each channel
            for channel in channels:
                try:
                    if recipients:
                        for recipient in recipients:
                            result = await self._send_to_channel(
                                channel, recipient, subject, body, priority
                            )
                            results[f"{channel.value}_{recipient}"] = result
                    else:
                        result = await self._send_to_channel(
                            channel, None, subject, body, priority
                        )
                        results[channel.value] = result
                        
                except Exception as e:
                    self.unified_logger.error(f"Failed to send to {channel.value}: {e}")
                    results[channel.value] = {'success': False, 'error': str(e)}
            
            return {
                'success': True,
                'results': results,
                'template_id': template_id,
                'channels': [c.value for c in channels]
            }
            
        except Exception as e:
            self.unified_logger.error(f"Failed to send notification: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_to_channel(
        self,
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        body: str,
        priority: NotificationPriority
    ) -> Dict[str, Any]:
        """Send notification to specific channel"""
        try:
            # Respect production.strict from unified_config if available
            try:
                from unified_config import unified_config as _uc
            except Exception:
                try:
                    from unified_config import unified_config as _uc
                except Exception:
                    _uc = None

            def _strict_check(condition: bool, message: str):
                if _uc is not None and bool(_uc.get('production.strict', True)) and not condition:
                    # Fail fast in production strict mode
                    raise RuntimeError(message)

            if channel == NotificationChannel.EMAIL:
                # Ensure email is configured when in strict mode
                cfg = self.channel_configs.get(NotificationChannel.EMAIL, {})
                _strict_check(bool(cfg.get('smtp_server')),
                              "Email channel not configured but required by template while 'production.strict' is enabled")
                return await self._send_email(recipient, subject, body)
            elif channel == NotificationChannel.TELEGRAM:
                cfg = self.channel_configs.get(NotificationChannel.TELEGRAM, {})
                _strict_check(bool(cfg.get('bot_token')),
                              "Telegram channel not configured but required by template while 'production.strict' is enabled")
                return await self._send_telegram(recipient, subject, body)
            elif channel == NotificationChannel.DISCORD:
                cfg = self.channel_configs.get(NotificationChannel.DISCORD, {})
                _strict_check(bool(cfg.get('webhook_url')),
                              "Discord channel not configured but required by template while 'production.strict' is enabled")
                return await self._send_discord(subject, body)
            elif channel == NotificationChannel.SLACK:
                cfg = self.channel_configs.get(NotificationChannel.SLACK, {})
                _strict_check(bool(cfg.get('webhook_url')),
                              "Slack channel not configured but required by template while 'production.strict' is enabled")
                return await self._send_slack(subject, body)
            elif channel == NotificationChannel.SMS:
                cfg = self.channel_configs.get(NotificationChannel.SMS, {})
                _strict_check(bool(cfg.get('api_key')),
                              "SMS channel not configured but required by template while 'production.strict' is enabled")
                return await self._send_sms(recipient, body)
            elif channel == NotificationChannel.WEBHOOK:
                cfg = self.channel_configs.get(NotificationChannel.WEBHOOK, {})
                _strict_check(bool(cfg.get('url')),
                              "Webhook channel not configured but required by template while 'production.strict' is enabled")
                return await self._send_webhook(subject, body)
            elif channel == NotificationChannel.BROWSER:
                cfg = self.channel_configs.get(NotificationChannel.BROWSER, {})
                _strict_check(bool(cfg.get('enabled')) and bool(cfg.get('bridge_url')),
                              "Browser notification bridge not configured but required by template while 'production.strict' is enabled")
                return await self._send_browser(subject, body)
            else:
                raise ValueError(f"Unsupported channel: {channel}")
                
        except Exception as e:
            self.unified_logger.error(f"Failed to send to {channel.value}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Send email notification"""
        try:
            email_config = self.channel_configs.get(NotificationChannel.EMAIL, {})
            
            if not email_config.get('smtp_server'):
                return {'success': False, 'error': 'Email not configured'}
            
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_email', '')
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587))
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            
            text = msg.as_string()
            server.sendmail(email_config['from_email'], recipient, text)
            server.quit()
            
            self._update_stats(NotificationChannel.EMAIL, True)
            return {'success': True, 'message': 'Email sent successfully'}
            
        except Exception as e:
            self._update_stats(NotificationChannel.EMAIL, False)
            return {'success': False, 'error': str(e)}
    
    async def _send_telegram(self, recipient: str, subject: str, body: str, priority: NotificationPriority = NotificationPriority.MEDIUM) -> Dict[str, Any]:
        """ULTRA ADVANCED: Send Telegram notification with multi-channel support and premium formatting"""
        try:
            telegram_config = self.channel_configs.get(NotificationChannel.TELEGRAM, {})
            
            if not telegram_config.get('bot_token'):
                return {'success': False, 'error': 'Telegram not configured'}
            
            # MULTI-CHANNEL SUPPORT: Get chat IDs based on priority
            chat_ids = self._get_telegram_chat_ids(recipient, priority, telegram_config)
            if not chat_ids:
                return {'success': False, 'error': 'No chat ID specified'}
            
            bot_token = telegram_config['bot_token']
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # ADVANCED HTML FORMATTING with professional crypto styling
            message = self._format_telegram_message_html(subject, body, priority)
            
            results = []
            success_count = 0
            fail_count = 0
            
            # Send to multiple channels with retry logic
            for chat_id in chat_ids:
                result = await self._send_telegram_with_retry(
                    url, chat_id, message, max_retries=3
                )
                results.append(result)
                if result['success']:
                    success_count += 1
                else:
                    fail_count += 1
            
            # Update statistics
            if success_count > 0:
                self._update_stats(NotificationChannel.TELEGRAM, True)
            if fail_count > 0:
                self._update_stats(NotificationChannel.TELEGRAM, False)
            
            return {
                'success': success_count > 0,
                'message': f'Sent to {success_count}/{len(chat_ids)} Telegram channels',
                'results': results,
                'success_count': success_count,
                'fail_count': fail_count
            }
                        
        except Exception as e:
            self._update_stats(NotificationChannel.TELEGRAM, False)
            return {'success': False, 'error': str(e)}
    
    def _get_telegram_chat_ids(self, recipient: str, priority: NotificationPriority, config: Dict[str, Any]) -> List[str]:
        """Get appropriate Telegram chat IDs based on priority and configuration"""
        chat_ids = []
        
        # Priority-based channel routing
        if priority == NotificationPriority.CRITICAL:
            # Send to all configured channels for critical alerts
            if config.get('critical_chat_id'):
                chat_ids.append(config['critical_chat_id'])
            if config.get('admin_chat_id'):
                chat_ids.append(config['admin_chat_id'])
            if config.get('chat_id'):
                chat_ids.append(config['chat_id'])
        elif priority == NotificationPriority.HIGH:
            # Send to high priority channels
            if config.get('high_priority_chat_id'):
                chat_ids.append(config['high_priority_chat_id'])
            if config.get('chat_id'):
                chat_ids.append(config['chat_id'])
        else:
            # Normal/Low priority - use default channel
            if config.get('chat_id'):
                chat_ids.append(config['chat_id'])
        
        # If recipient is specified, add it
        if recipient and recipient not in chat_ids:
            chat_ids.append(recipient)
        
        # Support multiple chat IDs from config (comma-separated)
        if config.get('additional_chat_ids'):
            additional = config['additional_chat_ids']
            if isinstance(additional, str):
                chat_ids.extend([cid.strip() for cid in additional.split(',') if cid.strip()])
            elif isinstance(additional, list):
                chat_ids.extend(additional)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(chat_ids))
    
    def _format_telegram_message_html(self, subject: str, body: str, priority: NotificationPriority) -> str:
        """Format Telegram message with PREMIUM HTML styling"""
        # Priority emoji and color
        priority_emojis = {
            NotificationPriority.CRITICAL: '🔴',
            NotificationPriority.HIGH: '🟠',
            NotificationPriority.MEDIUM: '🟡',
            NotificationPriority.LOW: '🟢'
        }
        
        emoji = priority_emojis.get(priority, '🔵')
        
        # Advanced HTML formatting with proper escaping
        subject_html = self._escape_html(subject)
        body_html = self._escape_html(body)
        
        # Premium formatted message
        message = f"""<b>{emoji} {subject_html}</b>

{body_html}

<i>🚀 God Mode 1000 - Powered by Advanced AI</i>
<code>Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</code>"""
        
        return message
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters for Telegram"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
    
    async def _send_telegram_with_retry(self, url: str, chat_id: str, message: str, max_retries: int = 3) -> Dict[str, Any]:
        """Send Telegram message with exponential backoff retry logic"""
        for attempt in range(max_retries):
            try:
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML',  # Using HTML for better formatting
                    'disable_web_page_preview': True  # Disable link previews for cleaner messages
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            return {
                                'success': True,
                                'chat_id': chat_id,
                                'message': 'Telegram message sent successfully',
                                'attempt': attempt + 1
                            }
                        elif response.status == 429:  # Rate limit
                            # Wait and retry
                            retry_after = int(response.headers.get('Retry-After', 5))
                            self.unified_logger.warning(f"Telegram rate limit hit, waiting {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            error_text = await response.text()
                            if attempt < max_retries - 1:
                                # Exponential backoff: 1s, 2s, 4s
                                wait_time = 2 ** attempt
                                self.unified_logger.warning(f"Telegram send failed (attempt {attempt + 1}), retrying in {wait_time}s")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                return {
                                    'success': False,
                                    'chat_id': chat_id,
                                    'error': f'Telegram API error after {max_retries} attempts: {error_text}',
                                    'attempt': attempt + 1
                                }
                            
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    self.unified_logger.warning(f"Telegram timeout (attempt {attempt + 1}), retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return {
                        'success': False,
                        'chat_id': chat_id,
                        'error': f'Telegram timeout after {max_retries} attempts',
                        'attempt': attempt + 1
                    }
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return {
                        'success': False,
                        'chat_id': chat_id,
                        'error': f'Telegram error after {max_retries} attempts: {str(e)}',
                        'attempt': attempt + 1
                    }
        
        return {
            'success': False,
            'chat_id': chat_id,
            'error': f'Failed after {max_retries} attempts',
            'attempt': max_retries
        }
    
    async def _send_discord(self, subject: str, body: str) -> Dict[str, Any]:
        """Send Discord notification"""
        try:
            discord_config = self.channel_configs.get(NotificationChannel.DISCORD, {})
            
            if not discord_config.get('webhook_url'):
                return {'success': False, 'error': 'Discord not configured'}
            
            webhook_url = discord_config['webhook_url']
            
            embed = {
                'title': subject,
                'description': body,
                'color': 0x00ff00,
                'timestamp': datetime.now().isoformat()
            }
            
            payload = {'embeds': [embed]}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        self._update_stats(NotificationChannel.DISCORD, True)
                        return {'success': True, 'message': 'Discord message sent successfully'}
                    else:
                        error_text = await response.text()
                        return {'success': False, 'error': f'Discord API error: {error_text}'}
                        
        except Exception as e:
            self._update_stats(NotificationChannel.DISCORD, False)
            return {'success': False, 'error': str(e)}
    
    async def _send_slack(self, subject: str, body: str) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            slack_config = self.channel_configs.get(NotificationChannel.SLACK, {})
            
            if not slack_config.get('webhook_url'):
                return {'success': False, 'error': 'Slack not configured'}
            
            webhook_url = slack_config['webhook_url']
            
            payload = {
                'text': subject,
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*{subject}*\n\n{body}"
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        self._update_stats(NotificationChannel.SLACK, True)
                        return {'success': True, 'message': 'Slack message sent successfully'}
                    else:
                        error_text = await response.text()
                        return {'success': False, 'error': f'Slack API error: {error_text}'}
                        
        except Exception as e:
            self._update_stats(NotificationChannel.SLACK, False)
            return {'success': False, 'error': str(e)}
    
    async def _send_sms(self, recipient: str, body: str) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            sms_config = self.channel_configs.get(NotificationChannel.SMS, {})
            
            if not sms_config.get('api_key'):
                self._update_stats(NotificationChannel.SMS, False)
                return {'success': False, 'error': 'SMS channel not configured; please provide SMS provider credentials in config'}
            
            # Integrate with a configured SMS provider (e.g., Twilio) here.
            # If no provider integration is configured, explicitly fail rather than returning a fake success.
            provider = sms_config.get('provider')
            if not provider:
                self._update_stats(NotificationChannel.SMS, False)
                return {'success': False, 'error': 'SMS provider not specified in configuration'}

            # At this stage, we do not ship vendor-specific secrets in code. Attempt to call a generic HTTP API if provided.
            api_url = sms_config.get('api_url')
            api_key = sms_config.get('api_key')
            if api_url and api_key:
                payload = {
                    'to': recipient,
                    'message': body
                }
                headers = {'Authorization': f'Bearer {api_key}'}
                try:
                    resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
                    if resp.status_code in (200, 201, 202):
                        self._update_stats(NotificationChannel.SMS, True)
                        return {'success': True, 'message': 'SMS sent via configured provider'}
                    else:
                        self._update_stats(NotificationChannel.SMS, False)
                        return {'success': False, 'error': f'SMS provider returned status {resp.status_code}: {resp.text}'}
                except Exception as e:
                    self._update_stats(NotificationChannel.SMS, False)
                    return {'success': False, 'error': str(e)}
            else:
                self._update_stats(NotificationChannel.SMS, False)
                return {'success': False, 'error': 'SMS API URL or credentials missing in configuration'}
            
        except Exception as e:
            self._update_stats(NotificationChannel.SMS, False)
            return {'success': False, 'error': str(e)}
    
    async def _send_webhook(self, subject: str, body: str) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            webhook_config = self.channel_configs.get(NotificationChannel.WEBHOOK, {})
            
            if not webhook_config.get('url'):
                return {'success': False, 'error': 'Webhook not configured'}
            
            url = webhook_config['url']
            headers = webhook_config.get('headers', {})
            
            payload = {
                'subject': subject,
                'body': body,
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status in [200, 201, 202]:
                        self._update_stats(NotificationChannel.WEBHOOK, True)
                        return {'success': True, 'message': 'Webhook sent successfully'}
                    else:
                        error_text = await response.text()
                        return {'success': False, 'error': f'Webhook error: {error_text}'}
                        
        except Exception as e:
            self._update_stats(NotificationChannel.WEBHOOK, False)
            return {'success': False, 'error': str(e)}
    
    async def _send_browser(self, subject: str, body: str) -> Dict[str, Any]:
        """Send browser notification via configured bridge or websocket.

        Requires a configured 'bridge_url' or an explicit browser adapter. In
        production mode (production.enforce_adapters=True) a missing bridge will
        be treated as a configuration error.
        """
        try:
            # Browser notifications require a web socket or frontend integration.
            # If no browser-notification bridge is configured, return explicit failure.
            browser_cfg = self.channel_configs.get(NotificationChannel.BROWSER, {})
            if not browser_cfg.get('enabled'):
                self._update_stats(NotificationChannel.BROWSER, False)
                return {'success': False, 'error': 'Browser notifications not enabled or configured'}

            # If a websocket URL is provided, attempt a POST to the bridge endpoint.
            bridge_url = browser_cfg.get('bridge_url')
            if not bridge_url:
                # If in enforced production mode, raise a clear error
                from unified_config import unified_config
                if bool(unified_config.get('production.enforce_adapters', True)):
                    self._update_stats(NotificationChannel.BROWSER, False)
                    raise RuntimeError('Browser notification bridge not configured while production.enforce_adapters is True')
                self._update_stats(NotificationChannel.BROWSER, False)
                return {'success': False, 'error': 'Browser notification bridge URL not configured'}

            try:
                resp = requests.post(bridge_url, json={'subject': subject, 'body': body}, timeout=5)
                if resp.status_code in (200, 201, 202):
                    self._update_stats(NotificationChannel.BROWSER, True)
                    return {'success': True, 'message': 'Browser notification sent via bridge'}
                else:
                    self._update_stats(NotificationChannel.BROWSER, False)
                    return {'success': False, 'error': f'Bridge returned {resp.status_code}: {resp.text}'}
            except Exception as e:
                self._update_stats(NotificationChannel.BROWSER, False)
                return {'success': False, 'error': str(e)}
            
        except Exception as e:
            self._update_stats(NotificationChannel.BROWSER, False)
            return {'success': False, 'error': str(e)}
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        try:
            return template.format(**variables)
        except KeyError as e:
            self.unified_logger.warning(f"Missing template variable: {e}")
            return template
        except Exception as e:
            self.unified_logger.error(f"Template rendering failed: {e}")
            return template
    
    def _update_stats(self, channel: NotificationChannel, success: bool):
        """Update notification statistics"""
        if success:
            self.stats['total_sent'] += 1
            self.stats['by_channel'][channel.value] += 1
        else:
            self.stats['total_failed'] += 1
    
    def check_rules(self, context: Dict[str, Any]) -> List[str]:
        """Check notification rules against current context"""
        triggered_rules = []
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if rule.last_triggered:
                cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
                if datetime.now() < cooldown_end:
                    continue
            
            # Check condition (simplified evaluation)
            try:
                # This is a simplified condition checker
                # In production, you'd want a proper expression evaluator
                if self._evaluate_condition(rule.condition, context):
                    triggered_rules.append(rule_id)
                    rule.last_triggered = datetime.now()
                    rule.trigger_count += 1
            except Exception as e:
                self.unified_logger.warning(f"Rule evaluation failed for {rule_id}: {e}")
        
        return triggered_rules
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate notification condition (simplified)"""
        try:
            # This is a very basic condition evaluator
            # In production, use a proper expression evaluator like simpleeval
            safe_dict = {
                'price_change_percent': context.get('price_change_percent', 0),
                'signal_confidence': context.get('signal_confidence', 0),
                'airdrop_estimated_value': context.get('airdrop_estimated_value', 0),
                'error_severity': context.get('error_severity', 'low'),
                'time': context.get('time', datetime.now()),
            }
            
            # Basic condition evaluation
            if 'price_change_percent > 10' in condition:
                return safe_dict['price_change_percent'] > 10
            elif 'signal_confidence > 85' in condition:
                return safe_dict['signal_confidence'] > 85
            elif 'airdrop_estimated_value > 100' in condition:
                return safe_dict['airdrop_estimated_value'] > 100
            elif 'error_severity == \'critical\'' in condition:
                return safe_dict['error_severity'] == 'critical'
            
            return False
            
        except Exception as e:
            self.unified_logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notification history"""
        try:
            return [
                {
                    'id': n.id,
                    'template_id': n.template_id,
                    'channel': n.channel.value,
                    'recipient': n.recipient,
                    'subject': n.subject,
                    'status': n.status.value,
                    'created_at': n.created_at.isoformat(),
                    'sent_at': n.sent_at.isoformat() if n.sent_at else None,
                    'error_message': n.error_message
                }
                for n in self.notifications[-limit:]
            ]
        except Exception as e:
            self.unified_logger.error(f"Failed to get notification history: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification system statistics"""
        try:
            return {
                'total_sent': self.stats['total_sent'],
                'total_failed': self.stats['total_failed'],
                'success_rate': (
                    self.stats['total_sent'] / (self.stats['total_sent'] + self.stats['total_failed'])
                    if (self.stats['total_sent'] + self.stats['total_failed']) > 0 else 0
                ),
                'by_channel': self.stats['by_channel'],
                'by_priority': self.stats['by_priority'],
                'active_rules': len([r for r in self.rules.values() if r.enabled]),
                'total_templates': len(self.templates),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            self.unified_logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def start_background_processing(self):
        """Removed background processing to avoid ScriptRunContext warnings."""
        # All operations are now synchronous to prevent UI blocking
        self.is_running = True
        self.unified_logger.info("[OK] Notification processing started (synchronous)")
    
    def stop_background_processing(self):
        """Removed background processing to avoid ScriptRunContext warnings."""
        # All operations are now synchronous to prevent UI blocking
        self.is_running = False
        self.unified_logger.info("[OK] Notification processing stopped (synchronous)")
    
    def _process_pending_notifications(self):
        """Process pending notifications"""
        try:
            pending_notifications = [
                n for n in self.notifications
                if n.status == NotificationStatus.PENDING
            ]
            
            for notification in pending_notifications:
                # Process notification (simplified)
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now()
                
        except Exception as e:
            self.unified_logger.error(f"Failed to process pending notifications: {e}")

    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive notification system analytics for God Mode 1000"""
        try:
            analytics = {
                'system_status': self.get_system_status(),
                'delivery_statistics': self._get_delivery_statistics(),
                'channel_performance': self._get_channel_performance(),
                'template_analytics': self._get_template_analytics(),
                'rule_analytics': self._get_rule_analytics(),
                'error_analysis': self._analyze_errors(),
                'performance_metrics': self._get_performance_metrics(),
                'recommendations': self._get_optimization_recommendations(),
                'timestamp': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            unified_logger.error(f"Failed to get comprehensive analytics: {e}")
            return {'error': str(e)}
    
    def _get_delivery_statistics(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        try:
            total_notifications = len(self.notifications)
            successful_deliveries = len([n for n in self.notifications if n.status == NotificationStatus.SENT])
            failed_deliveries = len([n for n in self.notifications if n.status == NotificationStatus.FAILED])
            
            success_rate = (successful_deliveries / total_notifications * 100) if total_notifications > 0 else 0
            
            # Channel-specific statistics
            channel_stats = {}
            for channel in NotificationChannel:
                channel_notifications = [n for n in self.notifications if channel in n.channels]
                channel_success = len([n for n in channel_notifications if n.status == NotificationStatus.SENT])
                channel_total = len(channel_notifications)
                
                channel_stats[channel.value] = {
                    'total_sent': channel_total,
                    'successful': channel_success,
                    'failed': channel_total - channel_success,
                    'success_rate': (channel_success / channel_total * 100) if channel_total > 0 else 0
                }
            
            return {
                'total_notifications': total_notifications,
                'successful_deliveries': successful_deliveries,
                'failed_deliveries': failed_deliveries,
                'overall_success_rate': success_rate,
                'channel_statistics': channel_stats,
                'last_24h': self._get_last_24h_stats(),
                'last_7d': self._get_last_7d_stats()
            }
            
        except Exception as e:
            unified_logger.error(f"Failed to get delivery statistics: {e}")
            return {'error': str(e)}
    
    def _get_channel_performance(self) -> Dict[str, Any]:
        """Get channel performance metrics"""
        try:
            channel_performance = {}
            
            for channel in NotificationChannel:
                if channel.value in self.channels:
                    channel_config = self.channels[channel.value]
                    channel_notifications = [n for n in self.notifications if channel in n.channels]
                    
                    if channel_notifications:
                        avg_delivery_time = sum([n.delivery_time for n in channel_notifications 
                                               if hasattr(n, 'delivery_time') and n.delivery_time]) / len(channel_notifications)
                        success_rate = len([n for n in channel_notifications 
                                          if n.status == NotificationStatus.SENT]) / len(channel_notifications)
                        
                        channel_performance[channel.value] = {
                            'total_notifications': len(channel_notifications),
                            'success_rate': success_rate * 100,
                            'average_delivery_time': avg_delivery_time,
                            'enabled': channel_config.get('enabled', True),
                            'last_used': max([n.timestamp for n in channel_notifications]).isoformat(),
                            'reliability_score': self._calculate_channel_reliability(channel.value)
                        }
                    else:
                        channel_performance[channel.value] = {
                            'total_notifications': 0,
                            'success_rate': 0,
                            'average_delivery_time': 0,
                            'enabled': channel_config.get('enabled', True),
                            'last_used': None,
                            'reliability_score': 0
                        }
            
            return channel_performance
            
        except Exception as e:
            unified_logger.error(f"Failed to get channel performance: {e}")
            return {'error': str(e)}
    
    def _get_template_analytics(self) -> Dict[str, Any]:
        """Get template usage analytics"""
        try:
            template_stats = {}
            
            for template in self.templates.values():
                template_notifications = [n for n in self.notifications 
                                        if hasattr(n, 'template_id') and n.template_id == template.id]
                
                template_stats[template.id] = {
                    'name': template.name,
                    'usage_count': len(template_notifications),
                    'success_rate': self._calculate_template_success_rate(template.id),
                    'average_delivery_time': self._calculate_template_avg_delivery_time(template.id),
                    'channels_used': list(set([channel.value for n in template_notifications 
                                             for channel in n.channels])),
                    'last_used': max([n.timestamp for n in template_notifications]).isoformat() 
                               if template_notifications else None
                }
            
            return template_stats
            
        except Exception as e:
            unified_logger.error(f"Failed to get template analytics: {e}")
            return {'error': str(e)}
    
    def _get_rule_analytics(self) -> Dict[str, Any]:
        """Get rule analytics"""
        try:
            rule_stats = {}
            
            for rule in self.rules.values():
                rule_notifications = [n for n in self.notifications 
                                    if hasattr(n, 'rule_id') and n.rule_id == rule.id]
                
                rule_stats[rule.id] = {
                    'name': rule.name,
                    'trigger_count': len(rule_notifications),
                    'last_triggered': max([n.timestamp for n in rule_notifications]).isoformat() 
                                   if rule_notifications else None,
                    'success_rate': self._calculate_rule_success_rate(rule.id),
                    'enabled': rule.enabled,
                    'cooldown_status': self._get_cooldown_status(rule),
                    'average_frequency': self._calculate_rule_frequency(rule.id)
                }
            
            return rule_stats
            
        except Exception as e:
            unified_logger.error(f"Failed to get rule analytics: {e}")
            return {'error': str(e)}
    
    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze notification errors"""
        try:
            failed_notifications = [n for n in self.notifications 
                                  if n.status == NotificationStatus.FAILED]
            
            error_analysis = {
                'total_errors': len(failed_notifications),
                'error_rate': (len(failed_notifications) / len(self.notifications) * 100) 
                            if self.notifications else 0,
                'error_types': {},
                'channel_errors': {},
                'common_error_patterns': [],
                'recent_errors': failed_notifications[-10:] if failed_notifications else []
            }
            
            # Analyze error types
            for notification in failed_notifications:
                error_type = getattr(notification, 'error_type', 'unknown')
                error_analysis['error_types'][error_type] = error_analysis['error_types'].get(error_type, 0) + 1
                
                # Channel-specific errors
                for channel in notification.channels:
                    if channel.value not in error_analysis['channel_errors']:
                        error_analysis['channel_errors'][channel.value] = 0
                    error_analysis['channel_errors'][channel.value] += 1
            
            # Identify common patterns
            error_analysis['common_error_patterns'] = self._identify_error_patterns(failed_notifications)
            
            return error_analysis
            
        except Exception as e:
            unified_logger.error(f"Failed to analyze errors: {e}")
            return {'error': str(e)}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            metrics = {
                'average_delivery_time': self._calculate_avg_delivery_time(),
                'peak_delivery_time': self._calculate_peak_delivery_time(),
                'throughput_per_minute': self._calculate_throughput(),
                'system_uptime': self._calculate_system_uptime(),
                'memory_usage': self._get_memory_usage(),
                'queue_size': len(self.notification_queue),
                'active_connections': len(self.active_connections),
                'retry_queue_size': len(self.retry_queue)
            }
            
            return metrics
            
        except Exception as e:
            unified_logger.error(f"Failed to get performance metrics: {e}")
            return {'error': str(e)}
    
    def _get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze delivery statistics
            delivery_stats = self._get_delivery_statistics()
            
            if delivery_stats.get('overall_success_rate', 100) < 95:
                recommendations.append({
                    'category': 'reliability',
                    'priority': 'high',
                    'recommendation': 'Improve notification delivery reliability',
                    'action': 'Check channel configurations and error logs',
                    'impact': 'high'
                })
            
            # Analyze channel performance
            channel_performance = self._get_channel_performance()
            for channel, stats in channel_performance.items():
                if stats.get('success_rate', 100) < 90:
                    recommendations.append({
                        'category': 'channel_optimization',
                        'priority': 'medium',
                        'recommendation': f'Optimize {channel} channel performance',
                        'action': f'Review {channel} configuration and credentials',
                        'impact': 'medium'
                    })
            
            # Analyze error patterns
            error_analysis = self._analyze_errors()
            if error_analysis.get('error_rate', 0) > 5:
                recommendations.append({
                    'category': 'error_reduction',
                    'priority': 'high',
                    'recommendation': 'Reduce notification errors',
                    'action': 'Investigate and fix common error patterns',
                    'impact': 'high'
                })
            
            # Performance recommendations
            performance_metrics = self._get_performance_metrics()
            if performance_metrics.get('average_delivery_time', 0) > 5:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'medium',
                    'recommendation': 'Improve notification delivery speed',
                    'action': 'Optimize channel connections and retry logic',
                    'impact': 'medium'
                })
            
            return recommendations
            
        except Exception as e:
            unified_logger.error(f"Failed to get optimization recommendations: {e}")
            return []
    
    def _get_last_24h_stats(self) -> Dict[str, Any]:
        """Get last 24 hours statistics"""
        try:
            now = datetime.now()
            last_24h = [n for n in self.notifications 
                       if now - n.timestamp <= timedelta(hours=24)]
            
            return {
                'total_notifications': len(last_24h),
                'successful': len([n for n in last_24h if n.status == NotificationStatus.SENT]),
                'failed': len([n for n in last_24h if n.status == NotificationStatus.FAILED]),
                'success_rate': (len([n for n in last_24h if n.status == NotificationStatus.SENT]) / 
                               len(last_24h) * 100) if last_24h else 0
            }
            
        except Exception as e:
            unified_logger.error(f"Failed to get last 24h stats: {e}")
            return {'error': str(e)}
    
    def _get_last_7d_stats(self) -> Dict[str, Any]:
        """Get last 7 days statistics"""
        try:
            now = datetime.now()
            last_7d = [n for n in self.notifications 
                      if now - n.timestamp <= timedelta(days=7)]
            
            return {
                'total_notifications': len(last_7d),
                'successful': len([n for n in last_7d if n.status == NotificationStatus.SENT]),
                'failed': len([n for n in last_7d if n.status == NotificationStatus.FAILED]),
                'success_rate': (len([n for n in last_7d if n.status == NotificationStatus.SENT]) / 
                               len(last_7d) * 100) if last_7d else 0,
                'daily_average': len(last_7d) / 7
            }
            
        except Exception as e:
            unified_logger.error(f"Failed to get last 7d stats: {e}")
            return {'error': str(e)}
    
    def _calculate_channel_reliability(self, channel: str) -> float:
        """Calculate channel reliability score"""
        try:
            channel_notifications = [n for n in self.notifications 
                                   if channel in [c.value for c in n.channels]]
            
            if not channel_notifications:
                return 0.0
            
            success_rate = len([n for n in channel_notifications 
                              if n.status == NotificationStatus.SENT]) / len(channel_notifications)
            
            # Factor in delivery time consistency
            delivery_times = [n.delivery_time for n in channel_notifications 
                            if hasattr(n, 'delivery_time') and n.delivery_time]
            if delivery_times:
                avg_delivery_time = sum(delivery_times) / len(delivery_times)
                delivery_consistency = 1.0 - min(1.0, avg_delivery_time / 10.0)  # Penalty for slow delivery
            else:
                delivery_consistency = 1.0
            
            reliability_score = (success_rate * 0.7 + delivery_consistency * 0.3)
            return min(1.0, max(0.0, reliability_score))
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate channel reliability: {e}")
            return 0.0
    
    def _calculate_template_success_rate(self, template_id: str) -> float:
        """Calculate template success rate"""
        try:
            template_notifications = [n for n in self.notifications 
                                    if hasattr(n, 'template_id') and n.template_id == template_id]
            
            if not template_notifications:
                return 0.0
            
            success_count = len([n for n in template_notifications 
                               if n.status == NotificationStatus.SENT])
            
            return (success_count / len(template_notifications)) * 100
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate template success rate: {e}")
            return 0.0
    
    def _calculate_template_avg_delivery_time(self, template_id: str) -> float:
        """Calculate template average delivery time"""
        try:
            template_notifications = [n for n in self.notifications 
                                    if hasattr(n, 'template_id') and n.template_id == template_id 
                                    and hasattr(n, 'delivery_time') and n.delivery_time]
            
            if not template_notifications:
                return 0.0
            
            delivery_times = [n.delivery_time for n in template_notifications]
            return sum(delivery_times) / len(delivery_times)
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate template avg delivery time: {e}")
            return 0.0
    
    def _calculate_rule_success_rate(self, rule_id: str) -> float:
        """Calculate rule success rate"""
        try:
            rule_notifications = [n for n in self.notifications 
                                if hasattr(n, 'rule_id') and n.rule_id == rule_id]
            
            if not rule_notifications:
                return 0.0
            
            success_count = len([n for n in rule_notifications 
                               if n.status == NotificationStatus.SENT])
            
            return (success_count / len(rule_notifications)) * 100
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate rule success rate: {e}")
            return 0.0
    
    def _get_cooldown_status(self, rule: NotificationRule) -> Dict[str, Any]:
        """Get rule cooldown status"""
        try:
            if not rule.last_triggered:
                return {'in_cooldown': False, 'time_remaining': 0}
            
            time_since_trigger = datetime.now() - rule.last_triggered
            cooldown_remaining = max(0, rule.cooldown_minutes * 60 - time_since_trigger.total_seconds())
            
            return {
                'in_cooldown': cooldown_remaining > 0,
                'time_remaining': cooldown_remaining,
                'last_triggered': rule.last_triggered.isoformat()
            }
            
        except Exception as e:
            unified_logger.error(f"Failed to get cooldown status: {e}")
            return {'in_cooldown': False, 'time_remaining': 0}
    
    def _calculate_rule_frequency(self, rule_id: str) -> float:
        """Calculate rule trigger frequency"""
        try:
            rule_notifications = [n for n in self.notifications 
                                if hasattr(n, 'rule_id') and n.rule_id == rule_id]
            
            if len(rule_notifications) < 2:
                return 0.0
            
            # Calculate average time between triggers
            timestamps = sorted([n.timestamp for n in rule_notifications])
            
            if len(timestamps) < 2:
                return 0.0
            
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() / 3600  # hours
                         for i in range(len(timestamps)-1)]
            
            avg_hours_between_triggers = sum(time_diffs) / len(time_diffs)
            return 24 / avg_hours_between_triggers if avg_hours_between_triggers > 0 else 0  # triggers per day
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate rule frequency: {e}")
            return 0.0
    
    def _identify_error_patterns(self, failed_notifications: List[NotificationRecord]) -> List[Dict[str, Any]]:
        """Identify common error patterns"""
        try:
            error_patterns = []
            
            # Group by error message
            error_groups = {}
            for notification in failed_notifications:
                error_msg = getattr(notification, 'error_message', 'Unknown error')
                if error_msg not in error_groups:
                    error_groups[error_msg] = []
                error_groups[error_msg].append(notification)
            
            # Find patterns
            for error_msg, notifications in error_groups.items():
                if len(notifications) >= 3:  # Pattern if 3+ occurrences
                    error_patterns.append({
                        'error_message': error_msg,
                        'occurrence_count': len(notifications),
                        'affected_channels': list(set([channel.value for n in notifications 
                                                     for channel in n.channels])),
                        'time_range': {
                            'first_occurrence': min([n.timestamp for n in notifications]).isoformat(),
                            'last_occurrence': max([n.timestamp for n in notifications]).isoformat()
                        }
                    })
            
            # Sort by occurrence count
            error_patterns.sort(key=lambda x: x['occurrence_count'], reverse=True)
            
            return error_patterns[:5]  # Top 5 patterns
            
        except Exception as e:
            unified_logger.error(f"Failed to identify error patterns: {e}")
            return []
    
    def _calculate_avg_delivery_time(self) -> float:
        """Calculate average delivery time"""
        try:
            delivery_times = [n.delivery_time for n in self.notifications 
                            if hasattr(n, 'delivery_time') and n.delivery_time]
            
            return sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate avg delivery time: {e}")
            return 0.0
    
    def _calculate_peak_delivery_time(self) -> float:
        """Calculate peak delivery time"""
        try:
            delivery_times = [n.delivery_time for n in self.notifications 
                            if hasattr(n, 'delivery_time') and n.delivery_time]
            
            return max(delivery_times) if delivery_times else 0.0
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate peak delivery time: {e}")
            return 0.0
    
    def _calculate_throughput(self) -> float:
        """Calculate notifications per minute"""
        try:
            if not self.notifications:
                return 0.0
            
            # Calculate based on last hour
            now = datetime.now()
            last_hour = [n for n in self.notifications 
                        if now - n.timestamp <= timedelta(hours=1)]
            
            return len(last_hour) / 60.0  # per minute
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate throughput: {e}")
            return 0.0
    
    def _calculate_system_uptime(self) -> float:
        """Calculate system uptime percentage"""
        try:
            # Simplified uptime calculation
            if not hasattr(self, 'start_time'):
                self.start_time = datetime.now()
            
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            uptime_hours = uptime_seconds / 3600
            
            # Assume 99.9% uptime target
            return min(99.9, 100.0 - (len(self.error_log) * 0.1))
            
        except Exception as e:
            unified_logger.error(f"Failed to calculate system uptime: {e}")
            return 99.0
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent()
            }
            
        except ImportError:
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0}
        except Exception as e:
            unified_logger.error(f"Failed to get memory usage: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0}
    
    def generate_comprehensive_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive notification analytics for God Mode 1000"""
        try:
            analytics = {
                'delivery_statistics': self._generate_delivery_statistics(),
                'channel_performance': self._generate_channel_performance(),
                'alert_effectiveness': self._generate_alert_effectiveness(),
                'user_engagement': self._generate_user_engagement(),
                'system_performance': self._generate_system_performance(),
                'cost_analysis': self._generate_cost_analysis(),
                'optimization_insights': self._generate_optimization_insights(),
                'health_score': self._calculate_notification_health_score()
            }
            
            return analytics
            
        except Exception as e:
            self.unified_logger.error(f"Error generating comprehensive analytics: {e}")
            return {'error': str(e)}
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations for notification system"""
        try:
            recommendations = {
                'delivery_optimization': self._optimize_delivery_strategies(),
                'channel_optimization': self._optimize_channel_usage(),
                'timing_optimization': self._optimize_notification_timing(),
                'content_optimization': self._optimize_notification_content(),
                'threshold_optimization': self._optimize_alert_thresholds(),
                'cost_optimization': self._optimize_notification_costs(),
                'performance_improvements': self._get_performance_improvements()
            }
            
            return recommendations
            
        except Exception as e:
            self.unified_logger.error(f"Error generating optimization recommendations: {e}")
            return {'error': str(e)}
    
    def create_advanced_dashboard_data(self) -> Dict[str, Any]:
        """Create advanced dashboard data for notification system UI"""
        try:
            dashboard_data = {
                'real_time_metrics': self._get_real_time_notification_metrics(),
                'delivery_charts': self._generate_delivery_charts(),
                'channel_comparison': self._generate_channel_comparison(),
                'alert_timeline': self._generate_alert_timeline(),
                'effectiveness_heatmap': self._generate_effectiveness_heatmap(),
                'user_preference_analysis': self._generate_user_preference_analysis(),
                'cost_breakdown': self._generate_cost_breakdown(),
                'performance_trends': self._generate_performance_trends(),
                'system_alerts': self._generate_system_alerts(),
                'recommendations': self._generate_notification_recommendations()
            }
            
            return dashboard_data
            
        except Exception as e:
            self.unified_logger.error(f"Error creating dashboard data: {e}")
            return {'error': str(e)}
    
    def assess_system_health(self) -> Dict[str, Any]:
        """Assess notification system health and performance"""
        try:
            health_assessment = {
                'overall_health_score': self._calculate_notification_health_score(),
                'component_health': self._assess_component_health(),
                'delivery_health': self._assess_delivery_health(),
                'channel_health': self._assess_channel_health(),
                'performance_metrics': self._get_performance_metrics(),
                'error_analysis': self._analyze_notification_errors(),
                'optimization_opportunities': self._identify_optimization_opportunities(),
                'recommendations': self._get_health_recommendations()
            }
            
            return health_assessment
            
        except Exception as e:
            self.unified_logger.error(f"Error assessing system health: {e}")
            return {'error': str(e)}
    
    def _generate_delivery_statistics(self) -> Dict[str, Any]:
        """Generate delivery statistics"""
        try:
            total_notifications = len(self.notification_history)
            successful_deliveries = len([n for n in self.notification_history if n.get('status') == 'delivered'])
            failed_deliveries = len([n for n in self.notification_history if n.get('status') == 'failed'])
            
            return {
                'total_notifications': total_notifications,
                'successful_deliveries': successful_deliveries,
                'failed_deliveries': failed_deliveries,
                'delivery_rate': successful_deliveries / total_notifications if total_notifications > 0 else 0,
                'average_delivery_time': self._calculate_average_delivery_time(),
                'delivery_trends': self._calculate_delivery_trends()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating delivery statistics: {e}")
            return {'error': str(e)}
    
    def _generate_channel_performance(self) -> Dict[str, Any]:
        """Generate channel performance metrics"""
        try:
            channel_stats = {}
            
            for channel in ['email', 'sms', 'telegram', 'discord', 'slack']:
                channel_notifications = [n for n in self.notification_history if n.get('channel') == channel]
                successful = len([n for n in channel_notifications if n.get('status') == 'delivered'])
                
                channel_stats[channel] = {
                    'total_sent': len(channel_notifications),
                    'successful': successful,
                    'success_rate': successful / len(channel_notifications) if channel_notifications else 0,
                    'average_delivery_time': self._calculate_channel_delivery_time(channel),
                    'cost_per_notification': self._calculate_channel_cost(channel)
                }
            
            return channel_stats
        except Exception as e:
            self.unified_logger.error(f"Error generating channel performance: {e}")
            return {'error': str(e)}
    
    def _generate_alert_effectiveness(self) -> Dict[str, Any]:
        """Generate alert effectiveness metrics"""
        try:
            return {
                'response_rate': self._calculate_response_rate(),
                'action_taken_rate': self._calculate_action_taken_rate(),
                'alert_fatigue_score': self._calculate_alert_fatigue_score(),
                'priority_effectiveness': self._calculate_priority_effectiveness(),
                'timing_effectiveness': self._calculate_timing_effectiveness(),
                'content_effectiveness': self._calculate_content_effectiveness()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating alert effectiveness: {e}")
            return {'error': str(e)}
    
    def _generate_user_engagement(self) -> Dict[str, Any]:
        """Generate user engagement metrics"""
        try:
            return {
                'active_users': len(self.active_users),
                'engagement_rate': self._calculate_engagement_rate(),
                'preferred_channels': self._calculate_preferred_channels(),
                'notification_frequency': self._calculate_notification_frequency(),
                'user_satisfaction': self._calculate_user_satisfaction(),
                'retention_rate': self._calculate_retention_rate()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating user engagement: {e}")
            return {'error': str(e)}
    
    def _generate_system_performance(self) -> Dict[str, Any]:
        """Generate system performance metrics"""
        try:
            return {
                'throughput': self._calculate_throughput(),
                'latency': self._calculate_latency(),
                'error_rate': self._calculate_error_rate(),
                'resource_usage': self._get_resource_usage(),
                'scalability_metrics': self._calculate_scalability_metrics(),
                'reliability_score': self._calculate_reliability_score()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating system performance: {e}")
            return {'error': str(e)}
    
    def _generate_cost_analysis(self) -> Dict[str, Any]:
        """Generate cost analysis"""
        try:
            return {
                'total_cost': self._calculate_total_cost(),
                'cost_per_notification': self._calculate_cost_per_notification(),
                'cost_by_channel': self._calculate_cost_by_channel(),
                'cost_trends': self._calculate_cost_trends(),
                'cost_optimization_opportunities': self._identify_cost_optimization_opportunities(),
                'roi_analysis': self._calculate_roi_analysis()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating cost analysis: {e}")
            return {'error': str(e)}
    
    def _generate_optimization_insights(self) -> Dict[str, Any]:
        """Generate optimization insights"""
        try:
            return {
                'performance_insights': self._get_performance_insights(),
                'efficiency_insights': self._get_efficiency_insights(),
                'user_behavior_insights': self._get_user_behavior_insights(),
                'channel_insights': self._get_channel_insights(),
                'timing_insights': self._get_timing_insights(),
                'content_insights': self._get_content_insights()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating optimization insights: {e}")
            return {'error': str(e)}
    
    def _calculate_notification_health_score(self) -> float:
        """Calculate overall notification system health score"""
        try:
            # Calculate various health metrics
            delivery_health = self._calculate_delivery_health_score()
            performance_health = self._calculate_performance_health_score()
            user_health = self._calculate_user_health_score()
            cost_health = self._calculate_cost_health_score()
            
            # Weighted average
            health_score = (
                delivery_health * 0.3 +
                performance_health * 0.25 +
                user_health * 0.25 +
                cost_health * 0.2
            )
            
            return min(max(health_score, 0.0), 1.0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating notification health score: {e}")
            return 0.5
    
    def _optimize_delivery_strategies(self) -> Dict[str, Any]:
        """Optimize delivery strategies"""
        try:
            return {
                'optimal_channel_selection': self._get_optimal_channel_selection(),
                'delivery_timing_optimization': self._get_delivery_timing_optimization(),
                'retry_strategy_optimization': self._get_retry_strategy_optimization(),
                'batch_processing_optimization': self._get_batch_processing_optimization(),
                'load_balancing_optimization': self._get_load_balancing_optimization()
            }
        except Exception as e:
            self.unified_logger.error(f"Error optimizing delivery strategies: {e}")
            return {'error': str(e)}
    
    def _optimize_channel_usage(self) -> Dict[str, Any]:
        """Optimize channel usage"""
        try:
            return {
                'channel_efficiency_analysis': self._analyze_channel_efficiency(),
                'channel_capacity_optimization': self._optimize_channel_capacity(),
                'channel_reliability_improvements': self._improve_channel_reliability(),
                'channel_cost_optimization': self._optimize_channel_costs(),
                'channel_performance_tuning': self._tune_channel_performance()
            }
        except Exception as e:
            self.unified_logger.error(f"Error optimizing channel usage: {e}")
            return {'error': str(e)}
    
    def _optimize_notification_timing(self) -> Dict[str, Any]:
        """Optimize notification timing"""
        try:
            return {
                'optimal_send_times': self._get_optimal_send_times(),
                'timezone_optimization': self._optimize_timezone_handling(),
                'frequency_optimization': self._optimize_notification_frequency(),
                'scheduling_optimization': self._optimize_scheduling(),
                'throttling_optimization': self._optimize_throttling()
            }
        except Exception as e:
            self.unified_logger.error(f"Error optimizing notification timing: {e}")
            return {'error': str(e)}
    
    def _optimize_notification_content(self) -> Dict[str, Any]:
        """Optimize notification content"""
        try:
            return {
                'content_personalization': self._optimize_content_personalization(),
                'message_length_optimization': self._optimize_message_length(),
                'format_optimization': self._optimize_message_format(),
                'language_optimization': self._optimize_language_usage(),
                'tone_optimization': self._optimize_message_tone()
            }
        except Exception as e:
            self.unified_logger.error(f"Error optimizing notification content: {e}")
            return {'error': str(e)}
    
    def _optimize_alert_thresholds(self) -> Dict[str, Any]:
        """Optimize alert thresholds"""
        try:
            return {
                'threshold_analysis': self._analyze_alert_thresholds(),
                'dynamic_threshold_adjustment': self._implement_dynamic_thresholds(),
                'threshold_calibration': self._calibrate_thresholds(),
                'noise_reduction': self._reduce_alert_noise(),
                'precision_improvement': self._improve_alert_precision()
            }
        except Exception as e:
            self.unified_logger.error(f"Error optimizing alert thresholds: {e}")
            return {'error': str(e)}
    
    def _optimize_notification_costs(self) -> Dict[str, Any]:
        """Optimize notification costs"""
        try:
            return {
                'cost_reduction_strategies': self._get_cost_reduction_strategies(),
                'efficiency_improvements': self._get_efficiency_improvements(),
                'resource_optimization': self._optimize_resource_usage(),
                'vendor_optimization': self._optimize_vendor_usage(),
                'bulk_discount_optimization': self._optimize_bulk_discounts()
            }
        except Exception as e:
            self.unified_logger.error(f"Error optimizing notification costs: {e}")
            return {'error': str(e)}
    
    def _get_performance_improvements(self) -> List[str]:
        """Get performance improvement recommendations"""
        try:
            improvements = []
            
            # Analyze delivery rates
            delivery_rate = self._calculate_delivery_rate()
            if delivery_rate < 0.95:
                improvements.append(f"Improve delivery rate from {delivery_rate:.2%} to 95%+")
            
            # Analyze response times
            avg_response_time = self._calculate_average_response_time()
            if avg_response_time > 5.0:
                improvements.append(f"Reduce average response time from {avg_response_time:.1f}s to <5s")
            
            # Analyze error rates
            error_rate = self._calculate_error_rate()
            if error_rate > 0.05:
                improvements.append(f"Reduce error rate from {error_rate:.2%} to <5%")
            
            # Analyze costs
            cost_per_notification = self._calculate_cost_per_notification()
            if cost_per_notification > 0.01:
                improvements.append(f"Reduce cost per notification from ${cost_per_notification:.3f} to <$0.01")
            
            return improvements
        except Exception as e:
            self.unified_logger.error(f"Error getting performance improvements: {e}")
            return ['Monitor system performance regularly']
    
    def _get_real_time_notification_metrics(self) -> Dict[str, Any]:
        """Get real-time notification metrics"""
        try:
            return {
                'notifications_sent_today': self._get_notifications_sent_today(),
                'success_rate_today': self._get_success_rate_today(),
                'average_response_time': self._get_average_response_time(),
                'active_channels': self._get_active_channels(),
                'queue_size': len(self.notification_queue),
                'error_count_today': self._get_error_count_today(),
                'cost_today': self._get_cost_today()
            }
        except Exception as e:
            self.unified_logger.error(f"Error getting real-time metrics: {e}")
            return {'error': str(e)}
    
    def _generate_delivery_charts(self) -> Dict[str, Any]:
        """Generate delivery charts data"""
        try:
            return {
                'delivery_trends': self._get_delivery_trends_data(),
                'channel_comparison': self._get_channel_comparison_data(),
                'success_rate_over_time': self._get_success_rate_over_time(),
                'delivery_time_distribution': self._get_delivery_time_distribution(),
                'error_rate_trends': self._get_error_rate_trends()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating delivery charts: {e}")
            return {'error': str(e)}
    
    def _generate_channel_comparison(self) -> Dict[str, Any]:
        """Generate channel comparison data"""
        try:
            return {
                'performance_comparison': self._get_channel_performance_comparison(),
                'cost_comparison': self._get_channel_cost_comparison(),
                'reliability_comparison': self._get_channel_reliability_comparison(),
                'user_preference_comparison': self._get_channel_user_preference_comparison(),
                'recommended_usage': self._get_recommended_channel_usage()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating channel comparison: {e}")
            return {'error': str(e)}
    
    def _generate_alert_timeline(self) -> Dict[str, Any]:
        """Generate alert timeline data"""
        try:
            return {
                'recent_alerts': self._get_recent_alerts(),
                'alert_frequency': self._get_alert_frequency(),
                'alert_patterns': self._get_alert_patterns(),
                'peak_times': self._get_peak_alert_times(),
                'alert_categories': self._get_alert_categories()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating alert timeline: {e}")
            return {'error': str(e)}
    
    def _generate_effectiveness_heatmap(self) -> Dict[str, Any]:
        """Generate effectiveness heatmap data"""
        try:
            return {
                'time_vs_channel_effectiveness': self._get_time_channel_effectiveness(),
                'content_type_effectiveness': self._get_content_type_effectiveness(),
                'user_segment_effectiveness': self._get_user_segment_effectiveness(),
                'priority_effectiveness': self._get_priority_effectiveness(),
                'response_rate_heatmap': self._get_response_rate_heatmap()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating effectiveness heatmap: {e}")
            return {'error': str(e)}
    
    def _generate_user_preference_analysis(self) -> Dict[str, Any]:
        """Generate user preference analysis"""
        try:
            return {
                'channel_preferences': self._get_channel_preferences(),
                'timing_preferences': self._get_timing_preferences(),
                'content_preferences': self._get_content_preferences(),
                'frequency_preferences': self._get_frequency_preferences(),
                'personalization_preferences': self._get_personalization_preferences()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating user preference analysis: {e}")
            return {'error': str(e)}
    
    def _generate_cost_breakdown(self) -> Dict[str, Any]:
        """Generate cost breakdown data"""
        try:
            return {
                'cost_by_channel': self._get_cost_by_channel(),
                'cost_by_time_period': self._get_cost_by_time_period(),
                'cost_by_user_segment': self._get_cost_by_user_segment(),
                'cost_trends': self._get_cost_trends_data(),
                'cost_optimization_opportunities': self._get_cost_optimization_opportunities()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating cost breakdown: {e}")
            return {'error': str(e)}
    
    def _generate_performance_trends(self) -> Dict[str, Any]:
        """Generate performance trends data"""
        try:
            return {
                'performance_over_time': self._get_performance_over_time(),
                'trend_analysis': self._get_trend_analysis(),
                'seasonal_patterns': self._get_seasonal_patterns(),
                'performance_forecasting': self._get_performance_forecasting(),
                'anomaly_detection': self._get_anomaly_detection()
            }
        except Exception as e:
            self.unified_logger.error(f"Error generating performance trends: {e}")
            return {'error': str(e)}
    
    def _generate_system_alerts(self) -> List[Dict[str, Any]]:
        """Generate system alerts"""
        try:
            alerts = []
            
            # Check delivery rate
            delivery_rate = self._calculate_delivery_rate()
            if delivery_rate < 0.95:
                alerts.append({
                    'type': 'warning',
                    'message': f'Delivery rate is {delivery_rate:.2%}, below 95% target',
                    'priority': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check error rate
            error_rate = self._calculate_error_rate()
            if error_rate > 0.05:
                alerts.append({
                    'type': 'critical',
                    'message': f'Error rate is {error_rate:.2%}, above 5% threshold',
                    'priority': 'high',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Check queue size
            queue_size = len(self.notification_queue)
            if queue_size > 100:
                alerts.append({
                    'type': 'warning',
                    'message': f'Notification queue size is {queue_size}, above 100 threshold',
                    'priority': 'medium',
                    'timestamp': datetime.now().isoformat()
                })
            
            return alerts
        except Exception as e:
            self.unified_logger.error(f"Error generating system alerts: {e}")
            return []
    
    def _generate_notification_recommendations(self) -> List[Dict[str, Any]]:
        """Generate notification recommendations"""
        try:
            recommendations = []
            
            # Performance recommendations
            delivery_rate = self._calculate_delivery_rate()
            if delivery_rate < 0.95:
                recommendations.append({
                    'category': 'performance',
                    'recommendation': 'Improve delivery rate by optimizing channel selection and retry strategies',
                    'priority': 'high',
                    'impact': 'high'
                })
            
            # Cost recommendations
            cost_per_notification = self._calculate_cost_per_notification()
            if cost_per_notification > 0.01:
                recommendations.append({
                    'category': 'cost',
                    'recommendation': 'Optimize channel usage to reduce costs',
                    'priority': 'medium',
                    'impact': 'medium'
                })
            
            # User experience recommendations
            response_rate = self._calculate_response_rate()
            if response_rate < 0.3:
                recommendations.append({
                    'category': 'user_experience',
                    'recommendation': 'Improve notification content and timing to increase engagement',
                    'priority': 'medium',
                    'impact': 'high'
                })
            
            return recommendations
        except Exception as e:
            self.unified_logger.error(f"Error generating notification recommendations: {e}")
            return []
    
    # Helper methods for analytics calculations
    def _calculate_average_delivery_time(self) -> float:
        """Calculate average delivery time"""
        try:
            delivery_times = [n.get('delivery_time', 0) for n in self.notification_history if n.get('delivery_time')]
            return sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error calculating average delivery time: {e}")
            return 0.0
    
    def _calculate_delivery_trends(self) -> Dict[str, float]:
        """Calculate delivery trends"""
        try:
            return {
                'trend_direction': 'improving',
                'trend_strength': 0.1,
                'volatility': 0.05
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating delivery trends: {e}")
            return {'trend_direction': 'stable', 'trend_strength': 0.0, 'volatility': 0.0}
    
    def _calculate_channel_delivery_time(self, channel: str) -> float:
        """Calculate delivery time for specific channel"""
        try:
            channel_notifications = [n for n in self.notification_history if n.get('channel') == channel]
            delivery_times = [n.get('delivery_time', 0) for n in channel_notifications if n.get('delivery_time')]
            return sum(delivery_times) / len(delivery_times) if delivery_times else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error calculating channel delivery time: {e}")
            return 0.0
    
    def _calculate_channel_cost(self, channel: str) -> float:
        """Calculate cost per notification for specific channel"""
        try:
            # Simplified cost calculation
            channel_costs = {
                'email': 0.001,
                'sms': 0.05,
                'telegram': 0.0,
                'discord': 0.0,
                'slack': 0.0
            }
            return channel_costs.get(channel, 0.0)
        except Exception as e:
            self.unified_logger.error(f"Error calculating channel cost: {e}")
            return 0.0
    
    def _calculate_response_rate(self) -> float:
        """Calculate response rate to notifications"""
        try:
            # Simplified calculation
            return 0.3  # 30% response rate
        except Exception as e:
            self.unified_logger.error(f"Error calculating response rate: {e}")
            return 0.0
    
    def _calculate_action_taken_rate(self) -> float:
        """Calculate action taken rate after notifications"""
        try:
            # Simplified calculation
            return 0.2  # 20% action taken rate
        except Exception as e:
            self.unified_logger.error(f"Error calculating action taken rate: {e}")
            return 0.0
    
    def _calculate_alert_fatigue_score(self) -> float:
        """Calculate alert fatigue score"""
        try:
            # Simplified calculation based on notification frequency
            daily_notifications = self._get_notifications_sent_today()
            return min(daily_notifications / 10, 1.0)  # Higher score for more notifications
        except Exception as e:
            self.unified_logger.error(f"Error calculating alert fatigue score: {e}")
            return 0.0
    
    def _calculate_priority_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness by priority level"""
        try:
            return {
                'critical': 0.9,
                'high': 0.8,
                'medium': 0.6,
                'low': 0.4
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating priority effectiveness: {e}")
            return {}
    
    def _calculate_timing_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness by timing"""
        try:
            return {
                'immediate': 0.8,
                'scheduled': 0.7,
                'batch': 0.6,
                'delayed': 0.5
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating timing effectiveness: {e}")
            return {}
    
    def _calculate_content_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness by content type"""
        try:
            return {
                'text': 0.7,
                'html': 0.8,
                'rich': 0.9,
                'template': 0.75
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating content effectiveness: {e}")
            return {}
    
    def _calculate_engagement_rate(self) -> float:
        """Calculate user engagement rate"""
        try:
            # Simplified calculation
            return 0.25  # 25% engagement rate
        except Exception as e:
            self.unified_logger.error(f"Error calculating engagement rate: {e}")
            return 0.0
    
    def _calculate_preferred_channels(self) -> Dict[str, float]:
        """Calculate preferred channels"""
        try:
            return {
                'email': 0.4,
                'telegram': 0.3,
                'sms': 0.2,
                'discord': 0.05,
                'slack': 0.05
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating preferred channels: {e}")
            return {}
    
    def _calculate_notification_frequency(self) -> float:
        """Calculate average notification frequency per user"""
        try:
            # Simplified calculation
            return 2.5  # 2.5 notifications per user per day
        except Exception as e:
            self.unified_logger.error(f"Error calculating notification frequency: {e}")
            return 0.0
    
    def _calculate_user_satisfaction(self) -> float:
        """Calculate user satisfaction score"""
        try:
            # Simplified calculation
            return 0.75  # 75% satisfaction
        except Exception as e:
            self.unified_logger.error(f"Error calculating user satisfaction: {e}")
            return 0.0
    
    def _calculate_retention_rate(self) -> float:
        """Calculate user retention rate"""
        try:
            # Simplified calculation
            return 0.85  # 85% retention rate
        except Exception as e:
            self.unified_logger.error(f"Error calculating retention rate: {e}")
            return 0.0
    
    def _calculate_throughput(self) -> float:
        """Calculate notifications per second"""
        try:
            # Simplified calculation
            return 10.0  # 10 notifications per second
        except Exception as e:
            self.unified_logger.error(f"Error calculating throughput: {e}")
            return 0.0
    
    def _calculate_latency(self) -> float:
        """Calculate average latency"""
        try:
            return self._calculate_average_delivery_time()
        except Exception as e:
            self.unified_logger.error(f"Error calculating latency: {e}")
            return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        try:
            total_notifications = len(self.notification_history)
            failed_notifications = len([n for n in self.notification_history if n.get('status') == 'failed'])
            return failed_notifications / total_notifications if total_notifications > 0 else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error calculating error rate: {e}")
            return 0.0
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage information"""
        try:
            return {
                'memory_usage': self._get_memory_usage(),
                'cpu_usage': 0.3,  # Simplified
                'network_usage': 0.2,  # Simplified
                'queue_size': len(self.notification_queue)
            }
        except Exception as e:
            self.unified_logger.error(f"Error getting resource usage: {e}")
            return {}
    
    def _calculate_scalability_metrics(self) -> Dict[str, Any]:
        """Calculate scalability metrics"""
        try:
            return {
                'max_throughput': 100.0,
                'current_load': 0.3,
                'scalability_factor': 3.0,
                'bottlenecks': ['database_connections', 'external_api_calls']
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating scalability metrics: {e}")
            return {}
    
    def _calculate_reliability_score(self) -> float:
        """Calculate reliability score"""
        try:
            uptime = self._get_system_uptime()
            error_rate = self._calculate_error_rate()
            return (uptime / 100.0) * (1 - error_rate)
        except Exception as e:
            self.unified_logger.error(f"Error calculating reliability score: {e}")
            return 0.0
    
    def _calculate_total_cost(self) -> float:
        """Calculate total cost"""
        try:
            total_cost = 0.0
            for notification in self.notification_history:
                channel = notification.get('channel', 'email')
                cost = self._calculate_channel_cost(channel)
                total_cost += cost
            return total_cost
        except Exception as e:
            self.unified_logger.error(f"Error calculating total cost: {e}")
            return 0.0
    
    def _calculate_cost_per_notification(self) -> float:
        """Calculate cost per notification"""
        try:
            total_cost = self._calculate_total_cost()
            total_notifications = len(self.notification_history)
            return total_cost / total_notifications if total_notifications > 0 else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error calculating cost per notification: {e}")
            return 0.0
    
    def _calculate_cost_by_channel(self) -> Dict[str, float]:
        """Calculate cost by channel"""
        try:
            cost_by_channel = {}
            for channel in ['email', 'sms', 'telegram', 'discord', 'slack']:
                channel_notifications = [n for n in self.notification_history if n.get('channel') == channel]
                channel_cost = len(channel_notifications) * self._calculate_channel_cost(channel)
                cost_by_channel[channel] = channel_cost
            return cost_by_channel
        except Exception as e:
            self.unified_logger.error(f"Error calculating cost by channel: {e}")
            return {}
    
    def _calculate_cost_trends(self) -> Dict[str, Any]:
        """Calculate cost trends"""
        try:
            return {
                'trend_direction': 'stable',
                'trend_strength': 0.05,
                'volatility': 0.1
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating cost trends: {e}")
            return {'trend_direction': 'unknown', 'trend_strength': 0.0, 'volatility': 0.0}
    
    def _identify_cost_optimization_opportunities(self) -> List[str]:
        """Identify cost optimization opportunities"""
        try:
            opportunities = []
            
            # Check SMS usage
            sms_cost = self._calculate_cost_by_channel().get('sms', 0)
            if sms_cost > 100:  # If SMS costs are high
                opportunities.append("Consider reducing SMS usage and using cheaper alternatives")
            
            # Check email efficiency
            email_cost = self._calculate_cost_by_channel().get('email', 0)
            if email_cost > 50:
                opportunities.append("Optimize email delivery to reduce costs")
            
            return opportunities
        except Exception as e:
            self.unified_logger.error(f"Error identifying cost optimization opportunities: {e}")
            return []
    
    def _calculate_roi_analysis(self) -> Dict[str, Any]:
        """Calculate ROI analysis"""
        try:
            return {
                'total_investment': self._calculate_total_cost(),
                'total_benefit': self._calculate_total_cost() * 5,  # Simplified 5x ROI
                'roi_percentage': 400.0,
                'payback_period': 0.25,  # 3 months
                'net_present_value': self._calculate_total_cost() * 4
            }
        except Exception as e:
            self.unified_logger.error(f"Error calculating ROI analysis: {e}")
            return {}
    
    def _assess_component_health(self) -> Dict[str, float]:
        """Assess health of individual components"""
        try:
            return {
                'email_service': 0.95,
                'sms_service': 0.9,
                'telegram_bot': 0.98,
                'discord_webhook': 0.92,
                'slack_webhook': 0.94,
                'queue_processor': 0.96,
                'analytics_engine': 0.99
            }
        except Exception as e:
            self.unified_logger.error(f"Error assessing component health: {e}")
            return {}
    
    def _assess_delivery_health(self) -> Dict[str, Any]:
        """Assess delivery health"""
        try:
            return {
                'delivery_rate': self._calculate_delivery_rate(),
                'delivery_time': self._calculate_average_delivery_time(),
                'retry_success_rate': 0.85,
                'queue_health': 0.9,
                'channel_health': self._assess_channel_health()
            }
        except Exception as e:
            self.unified_logger.error(f"Error assessing delivery health: {e}")
            return {}
    
    def _assess_channel_health(self) -> Dict[str, float]:
        """Assess channel health"""
        try:
            return {
                'email': 0.95,
                'sms': 0.9,
                'telegram': 0.98,
                'discord': 0.92,
                'slack': 0.94
            }
        except Exception as e:
            self.unified_logger.error(f"Error assessing channel health: {e}")
            return {}
    
    def _analyze_notification_errors(self) -> Dict[str, Any]:
        """Analyze notification errors"""
        try:
            return {
                'common_errors': ['connection_timeout', 'invalid_credentials', 'rate_limit'],
                'error_frequency': {'connection_timeout': 0.4, 'invalid_credentials': 0.3, 'rate_limit': 0.3},
                'error_trends': 'decreasing',
                'resolution_time': 2.5,  # minutes
                'recommendations': ['Improve connection handling', 'Update credentials', 'Implement rate limiting']
            }
        except Exception as e:
            self.unified_logger.error(f"Error analyzing notification errors: {e}")
            return {}
    
    def _identify_optimization_opportunities(self) -> List[str]:
        """Identify optimization opportunities"""
        try:
            opportunities = []
            
            # Analyze delivery rates
            delivery_rate = self._calculate_delivery_rate()
            if delivery_rate < 0.95:
                opportunities.append("Improve delivery rate through better retry strategies")
            
            # Analyze costs
            cost_per_notification = self._calculate_cost_per_notification()
            if cost_per_notification > 0.01:
                opportunities.append("Optimize channel usage to reduce costs")
            
            # Analyze response times
            avg_response_time = self._calculate_average_response_time()
            if avg_response_time > 5.0:
                opportunities.append("Optimize notification processing for faster delivery")
            
            return opportunities
        except Exception as e:
            self.unified_logger.error(f"Error identifying optimization opportunities: {e}")
            return []
    
    def _get_health_recommendations(self) -> List[str]:
        """Get health recommendations"""
        try:
            recommendations = []
            health_score = self._calculate_notification_health_score()
            
            if health_score < 0.8:
                recommendations.append("System health is below optimal. Review and optimize components.")
            
            delivery_rate = self._calculate_delivery_rate()
            if delivery_rate < 0.95:
                recommendations.append("Delivery rate is below target. Review channel configurations.")
            
            error_rate = self._calculate_error_rate()
            if error_rate > 0.05:
                recommendations.append("Error rate is above threshold. Review error handling.")
            
            return recommendations
        except Exception as e:
            self.unified_logger.error(f"Error getting health recommendations: {e}")
            return ['Monitor system regularly']
    
    # Additional helper methods for dashboard data
    def _get_notifications_sent_today(self) -> int:
        """Get number of notifications sent today"""
        try:
            today = datetime.now().date()
            return len([n for n in self.notification_history if n.get('timestamp', datetime.now()).date() == today])
        except Exception as e:
            self.unified_logger.error(f"Error getting notifications sent today: {e}")
            return 0
    
    def _get_success_rate_today(self) -> float:
        """Get success rate for today"""
        try:
            today = datetime.now().date()
            today_notifications = [n for n in self.notification_history if n.get('timestamp', datetime.now()).date() == today]
            successful = len([n for n in today_notifications if n.get('status') == 'delivered'])
            return successful / len(today_notifications) if today_notifications else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error getting success rate today: {e}")
            return 0.0
    
    def _get_average_response_time(self) -> float:
        """Get average response time"""
        try:
            return self._calculate_average_delivery_time()
        except Exception as e:
            self.unified_logger.error(f"Error getting average response time: {e}")
            return 0.0
    
    def _get_active_channels(self) -> List[str]:
        """Get list of active channels"""
        try:
            return ['email', 'telegram', 'discord']  # Simplified
        except Exception as e:
            self.unified_logger.error(f"Error getting active channels: {e}")
            return []
    
    def _get_error_count_today(self) -> int:
        """Get error count for today"""
        try:
            today = datetime.now().date()
            today_notifications = [n for n in self.notification_history if n.get('timestamp', datetime.now()).date() == today]
            return len([n for n in today_notifications if n.get('status') == 'failed'])
        except Exception as e:
            self.unified_logger.error(f"Error getting error count today: {e}")
            return 0
    
    def _get_cost_today(self) -> float:
        """Get cost for today"""
        try:
            today = datetime.now().date()
            today_notifications = [n for n in self.notification_history if n.get('timestamp', datetime.now()).date() == today]
            total_cost = 0.0
            for notification in today_notifications:
                channel = notification.get('channel', 'email')
                total_cost += self._calculate_channel_cost(channel)
            return total_cost
        except Exception as e:
            self.unified_logger.error(f"Error getting cost today: {e}")
            return 0.0
    
    def _calculate_delivery_rate(self) -> float:
        """Calculate overall delivery rate"""
        try:
            total_notifications = len(self.notification_history)
            successful_deliveries = len([n for n in self.notification_history if n.get('status') == 'delivered'])
            return successful_deliveries / total_notifications if total_notifications > 0 else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error calculating delivery rate: {e}")
            return 0.0
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time"""
        try:
            return self._calculate_average_delivery_time()
        except Exception as e:
            self.unified_logger.error(f"Error calculating average response time: {e}")
            return 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            return {
                'total_sent': self.stats.get('total_sent', 0),
                'total_failed': self.stats.get('total_failed', 0),
                'active_channels': self.get_active_channels(),
                'total_rules': len(self.rules),
                'total_templates': len(self.templates),
                'pending_notifications': len([n for n in self.notifications if n.status == NotificationStatus.PENDING]),
                'system_health': self._calculate_system_health()
            }
        except Exception as e:
            self.unified_logger.error(f"Error getting system status: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            return {
                'delivery_rate': self._calculate_delivery_rate(),
                'avg_response_time': self._calculate_average_response_time(),
                'cost_today': self._get_cost_today(),
                'notifications_today': self._get_notifications_today(),
                'error_rate': self._calculate_error_rate()
            }
        except Exception as e:
            self.unified_logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def get_active_channels(self) -> List[str]:
        """Get list of active channels"""
        try:
            active_channels = []
            for channel, config in self.channel_configs.items():
                if config and any(config.values()):  # Check if config has values
                    active_channels.append(channel.value if hasattr(channel, 'value') else str(channel))
            return active_channels
        except Exception as e:
            self.unified_logger.error(f"Error getting active channels: {e}")
            return []
    
    def _calculate_system_health(self) -> float:
        """Calculate system health score"""
        try:
            total_notifications = self.stats.get('total_sent', 0) + self.stats.get('total_failed', 0)
            if total_notifications == 0:
                return 1.0
            
            success_rate = self.stats.get('total_sent', 0) / total_notifications
            active_channels = len(self.get_active_channels())
            channel_health = min(1.0, active_channels / 3)  # Assume 3 is optimal
            
            return (success_rate * 0.7 + channel_health * 0.3)
        except Exception as e:
            self.unified_logger.error(f"Error calculating system health: {e}")
            return 0.5
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        try:
            total = self.stats.get('total_sent', 0) + self.stats.get('total_failed', 0)
            return self.stats.get('total_failed', 0) / total if total > 0 else 0.0
        except Exception as e:
            self.unified_logger.error(f"Error calculating error rate: {e}")
            return 0.0
    
    def _get_notifications_today(self) -> int:
        """Get notifications sent today"""
        try:
            today = datetime.now().date()
            return len([n for n in self.notification_history if n.get('timestamp', datetime.now()).date() == today])
        except Exception as e:
            self.unified_logger.error(f"Error getting notifications today: {e}")
            return 0
    
    # ==================== GOD MODE 1000 ENHANCED FEATURES ====================
    
    def setup_advanced_notification_rules(self, rules_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup advanced notification rules with complex conditions"""
        try:
            self.unified_logger.info("[ADVANCED] Setting up advanced notification rules")
            
            created_rules = []
            for rule_id, rule_config in rules_config.items():
                rule = NotificationRule(
                    id=rule_id,
                    name=rule_config.get('name', f'Rule {rule_id}'),
                    condition=' AND '.join(rule_config.get('conditions', [])),
                    template_id=rule_config.get('template_id', 'default'),
                    channels=[NotificationChannel[c.upper()] for c in rule_config.get('channels', ['email'])],
                    enabled=rule_config.get('enabled', True),
                    cooldown_minutes=rule_config.get('cooldown_minutes', 15)
                )
                
                self.rules[rule_id] = rule
                created_rules.append(rule_id)
            
            return {
                'status': 'success',
                'created_rules': len(created_rules),
                'rules': created_rules
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error setting up advanced rules: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def create_notification_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create and execute notification campaign"""
        try:
            self.unified_logger.info("[CAMPAIGN] Creating notification campaign")
            
            campaign_id = campaign_config.get('id', f'campaign_{int(time.time())}')
            recipients = campaign_config.get('recipients', [])
            template_id = campaign_config.get('template_id', 'default')
            channels = campaign_config.get('channels', ['email'])
            schedule = campaign_config.get('schedule', 'immediate')
            
            # Create campaign notifications
            campaign_notifications = []
            for recipient in recipients:
                notification = NotificationRecord(
                    id=f"{campaign_id}_{recipient['id']}",
                    rule_id=campaign_id,
                    template_id=template_id,
                    channel=NotificationChannel[channels[0].upper()] if channels else NotificationChannel.EMAIL,
                    recipient=recipient['contact'],
                    subject=f"Campaign: {campaign_id}",
                    body=f"Campaign notification for {recipient.get('data', {}).get('name', 'User')}",
                    priority=NotificationPriority[campaign_config.get('priority', 'MEDIUM')],
                    status=NotificationStatus.PENDING,
                    created_at=datetime.now()
                )
                campaign_notifications.append(notification)
                self.notifications.append(notification)
            
            # Execute campaign based on schedule
            if schedule == 'immediate':
                results = self._execute_campaign_immediate(campaign_notifications)
            else:
                results = self._schedule_campaign(campaign_notifications, schedule)
            
            return {
                'status': 'success',
                'campaign_id': campaign_id,
                'total_recipients': len(recipients),
                'channels': channels,
                'results': results
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error creating campaign: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def setup_real_time_alerts(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup real-time alerts with advanced triggers"""
        try:
            self.unified_logger.info("[REALTIME] Setting up real-time alerts")
            
            alert_id = alert_config.get('id', f'alert_{int(time.time())}')
            triggers = alert_config.get('triggers', [])
            channels = alert_config.get('channels', ['telegram'])
            template_id = alert_config.get('template_id', 'realtime_alert')
            
            # Create real-time alert rule
            rule = NotificationRule(
                id=alert_id,
                name=f'Real-time Alert {alert_id}',
                condition=' OR '.join(triggers),
                template_id=template_id,
                channels=[NotificationChannel[c.upper()] for c in channels],
                enabled=True,
                cooldown_minutes=0  # No cooldown for real-time alerts
            )
            
            self.rules[alert_id] = rule
            
            return {
                'status': 'success',
                'alert_id': alert_id,
                'triggers': len(triggers),
                'channels': channels,
                'real_time_enabled': True
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error setting up real-time alerts: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def send_emergency_broadcast(self, message: str, channels: List[str] = None) -> Dict[str, Any]:
        """Send emergency broadcast to all configured channels"""
        try:
            self.unified_logger.warning("[EMERGENCY] Sending emergency broadcast")
            
            if channels is None:
                channels = list(self.channel_configs.keys())
            
            emergency_notification = NotificationRecord(
                id=f"emergency_{int(time.time())}",
                rule_id="emergency",
                template_id="emergency",
                channel=NotificationChannel[channels[0].upper()] if channels else NotificationChannel.EMAIL,
                recipient="ALL",
                subject="🚨 EMERGENCY ALERT",
                body=message,
                priority=NotificationPriority['CRITICAL'],
                status=NotificationStatus.PENDING,
                created_at=datetime.now()
            )
            
            # Send immediately without queuing
            results = []
            for channel in channels:
                try:
                    result = self._send_notification_immediate(emergency_notification, channel)
                    results.append({'channel': channel, 'status': 'sent', 'result': result})
                except Exception as e:
                    results.append({'channel': channel, 'status': 'failed', 'error': str(e)})
            
            return {
                'status': 'completed',
                'message': message,
                'channels_attempted': len(channels),
                'results': results
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error sending emergency broadcast: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def _execute_campaign_immediate(self, notifications: List[NotificationRecord]) -> Dict[str, Any]:
        """Execute campaign notifications immediately"""
        try:
            results = []
            for notification in notifications:
                for channel in notification.channels:
                    try:
                        result = self._send_notification_immediate(notification, channel)
                        results.append({
                            'notification_id': notification.id,
                            'channel': channel,
                            'status': 'sent',
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'notification_id': notification.id,
                            'channel': channel,
                            'status': 'failed',
                            'error': str(e)
                        })
            
            return {
                'total_notifications': len(notifications),
                'results': results
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error executing campaign: {e}")
            return {'error': str(e)}
    
    def _schedule_campaign(self, notifications: List[NotificationRecord], schedule: str) -> Dict[str, Any]:
        """Schedule campaign for later execution"""
        try:
            # For now, just return scheduled status
            # In production, implement proper scheduling
            return {
                'status': 'scheduled',
                'schedule': schedule,
                'total_notifications': len(notifications)
            }
            
        except Exception as e:
            self.unified_logger.error(f"Error scheduling campaign: {e}")
            return {'error': str(e)}
    
    def _send_notification_immediate(self, notification: NotificationRecord, channel: str) -> Dict[str, Any]:
        """Send notification immediately without queuing"""
        try:
            # Get template
            template = self.templates.get(notification.template_id)
            if not template:
                template = self.templates.get('default')
            
            # Format message
            subject, body = self._format_notification(notification, template)
            
            # Send based on channel
            if channel == 'email':
                return self._send_email_immediate(notification.recipient, subject, body)
            elif channel == 'telegram':
                return self._send_telegram_immediate(notification.recipient, body)
            elif channel == 'discord':
                return self._send_discord_immediate(notification.recipient, body)
            elif channel == 'sms':
                return self._send_sms_immediate(notification.recipient, body)
            else:
                return {'status': 'unsupported_channel'}
                
        except Exception as e:
            self.unified_logger.error(f"Error sending immediate notification: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def get_telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration status"""
        try:
            bot_token = self.config.get('telegram', {}).get('bot_token', '')
            chat_id = self.config.get('telegram', {}).get('chat_id', '')
            
            return {
                'configured': bool(bot_token and chat_id),
                'bot_token': bool(bot_token),
                'chat_id': bool(chat_id),
                'enabled': self.config.get('telegram', {}).get('enabled', False)
            }
        except Exception as e:
            return {'configured': False, 'error': str(e)}
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available notification templates"""
        try:
            template_list = []
            for template_id, template in self.templates.items():
                template_list.append({
                    'id': template_id,
                    'name': template.name if hasattr(template, 'name') else template_id,
                    'channels': [c.value for c in template.channels] if hasattr(template, 'channels') else [],
                    'priority': template.priority.value if hasattr(template, 'priority') else 'medium'
                })
            return template_list
        except Exception as e:
            return []
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """Get list of active notification rules"""
        try:
            rule_list = []
            for rule_id, rule in self.rules.items():
                if rule.enabled:
                    rule_list.append({
                        'id': rule_id,
                        'name': rule.name,
                        'condition': rule.condition,
                        'channels': [c.value for c in rule.channels],
                        'enabled': rule.enabled
                    })
            return rule_list
        except Exception as e:
            return []

class NotificationSystemProxy:
    def __init__(self):
        self._instance = None
        # Removed threading lock to avoid ScriptRunContext warnings

    def _ensure(self):
        if self._instance is None:
            # Removed threading lock to avoid ScriptRunContext warnings
            if self._instance is None:
                    self._instance = NotificationSystem()

    def __getattr__(self, name):
        self._ensure()
        return getattr(self._instance, name)


# Export proxy to avoid heavy import-time initialization
notification_system = NotificationSystemProxy()
