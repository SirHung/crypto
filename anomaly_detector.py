"""
Anomaly Detection System - God Mode 10000
Phát hiện anomalies trong price/volume và manipulation
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from unified_logging_manager import UnifiedLoggingManager

# Use centralized pandas/numpy bypass
# Fix Python 3.13 compatibility first
import python313_compatibility

# Import real libraries - NO BYPASS/FALLBACK
import pandas as pd
import numpy as np

from real_market_data_fetcher import real_market_data_fetcher


@dataclass
class AnomalyAlert:
    """Alert về anomaly"""
    symbol: str
    timestamp: datetime
    anomaly_type: str
    severity: str
    z_score: float
    description: str
    manipulation_suspected: bool


class AnomalyDetector:
    """Detect market anomalies and manipulation"""
    
    def __init__(self):
        self.logger = UnifiedLoggingManager().get_logger("anomaly_detector")
        self.logger.info("✅ Anomaly Detector initialized")
    
    def detect_anomalies(self, symbol: str) -> List[AnomalyAlert]:
        """Detect all types of anomalies"""
        try:
            alerts = []
            
            # Get data
            data = real_market_data_fetcher.get_historical_data(symbol, '1h', 100)
            if not data or len(data) < 50:
                return alerts
            
            closes = [float(d['close']) for d in data]
            volumes = [float(d['volume']) for d in data]
            
            # Price anomaly
            price_mean = np.mean(closes)
            price_std = np.std(closes)
            current_price = closes[-1]
            price_z = abs((current_price - price_mean) / price_std) if price_std > 0 else 0
            
            if price_z > 3:
                alerts.append(AnomalyAlert(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    anomaly_type='PRICE_SPIKE',
                    severity='HIGH' if price_z > 4 else 'MEDIUM',
                    z_score=price_z,
                    description=f"Price spike detected (z-score: {price_z:.2f})",
                    manipulation_suspected=price_z > 5
                ))
            
            # Volume anomaly
            vol_mean = np.mean(volumes)
            vol_std = np.std(volumes)
            current_vol = volumes[-1]
            vol_z = abs((current_vol - vol_mean) / vol_std) if vol_std > 0 else 0
            
            if vol_z > 3:
                alerts.append(AnomalyAlert(
                    symbol=symbol,
                    timestamp=datetime.now(),
                    anomaly_type='VOLUME_SPIKE',
                    severity='HIGH' if vol_z > 4 else 'MEDIUM',
                    z_score=vol_z,
                    description=f"Volume spike detected (z-score: {vol_z:.2f})",
                    manipulation_suspected=vol_z > 5 and price_z < 1
                ))
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return []


anomaly_detector = AnomalyDetector()

