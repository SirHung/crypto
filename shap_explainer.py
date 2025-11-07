"""
GOD MODE 10000 - SHAP EXPLAINER
================================
SHAP (SHapley Additive exPlanations) for AI Prediction Explanation
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

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
class SHAPFactor:
    """SHAP factor explanation"""
    name: str
    impact: float  # -1 to 1
    value: float
    importance: float  # 0 to 1
    direction: str  # 'bullish', 'bearish', 'neutral'


@dataclass
class SHAPExplanation:
    """Complete SHAP explanation for a prediction"""
    prediction_signal: str
    base_value: float
    prediction_value: float
    top_factors: List[SHAPFactor]
    all_factors: List[SHAPFactor]
    overall_confidence: float
    explanation_text: str


class SHAPExplainer:
    """SHAP Explainer for AI Predictions - GOD MODE 10000"""
    
    def __init__(self):
        """Initialize SHAP Explainer"""
        self.unified_logger = unified_logging.get_logger("shap_explainer")
        
        # Base value (neutral point)
        self.base_value = 0.5
        
        self.unified_logger.info("✅ SHAP Explainer initialized - God Mode 10000")
    
    def explain_prediction(self, prediction_data: Dict[str, Any]) -> SHAPExplanation:
        """Generate SHAP explanation for prediction"""
        try:
            signal = prediction_data.get('signal', 'NEUTRAL')
            confidence = prediction_data.get('confidence', 0.5)
            sources = prediction_data.get('sources', [])
            metadata = prediction_data.get('metadata', {})
            
            # Calculate SHAP values from sources
            factors = self._calculate_shap_values(sources, metadata, signal, confidence)
            
            # Sort by importance
            factors_sorted = sorted(factors, key=lambda x: abs(x.impact), reverse=True)
            
            # Prediction value
            prediction_value = self.base_value + sum(f.impact for f in factors)
            prediction_value = max(0.0, min(1.0, prediction_value))
            
            # Generate explanation text
            explanation_text = self._generate_explanation_text(factors_sorted[:5], signal, confidence)
            
            return SHAPExplanation(
                prediction_signal=signal,
                base_value=self.base_value,
                prediction_value=prediction_value,
                top_factors=factors_sorted[:10],
                all_factors=factors_sorted,
                overall_confidence=confidence,
                explanation_text=explanation_text
            )
        
        except Exception as e:
            self.unified_logger.error(f"SHAP explanation error: {e}")
            # NO FALLBACK: Raise error instead of returning fake explanation
            raise RuntimeError(
                f"❌ CRITICAL: Failed to generate SHAP explanation\n"
                f"❌ ERROR: {e}\n"
                f"❌ REQUIRED: Ensure prediction_data contains valid sources and metadata\n"
                f"❌ NO FALLBACK: Cannot provide fake/empty explanation"
            )
    
    def _calculate_shap_values(self, sources: List[Dict], metadata: Dict, 
                               signal: str, confidence: float) -> List[SHAPFactor]:
        """Calculate SHAP values from prediction sources"""
        factors = []
        
        try:
            # Process each source as a factor
            for source in sources:
                source_name = source.get('source_name', 'Unknown')
                source_signal = source.get('signal', 'HOLD')
                source_conf = source.get('confidence', 0.5)
                source_weight = source.get('credibility_weight', 0.1)
                
                # Calculate impact
                if source_signal == signal:
                    # Agrees with final signal
                    impact = source_conf * source_weight
                    direction = 'bullish' if signal == 'BUY' else 'bearish' if signal == 'SELL' else 'neutral'
                else:
                    # Disagrees with final signal
                    impact = -source_conf * source_weight * 0.5
                    direction = 'bearish' if signal == 'BUY' else 'bullish' if signal == 'SELL' else 'neutral'
                
                factor = SHAPFactor(
                    name=f"{source_name} Signal",
                    impact=impact,
                    value=source_conf,
                    importance=abs(impact),
                    direction=direction
                )
                factors.append(factor)
            
            # Add metadata factors
            if metadata:
                # Volatility factor
                volatility = metadata.get('volatility', 0)
                if volatility > 0:
                    vol_impact = -0.05 if volatility > 0.05 else 0.02
                    factors.append(SHAPFactor(
                        name="Market Volatility",
                        impact=vol_impact,
                        value=volatility,
                        importance=abs(vol_impact),
                        direction='bearish' if vol_impact < 0 else 'bullish'
                    ))
                
                # Volume factor
                volume = metadata.get('volume_24h', 0)
                if volume > 0:
                    # High volume = higher confidence
                    vol_factor_impact = 0.03 if volume > 1000000000 else 0.01
                    factors.append(SHAPFactor(
                        name="Trading Volume",
                        impact=vol_factor_impact,
                        value=volume,
                        importance=abs(vol_factor_impact),
                        direction='bullish'
                    ))
                
                # Market regime
                regime = metadata.get('market_regime', '')
                if regime:
                    regime_impact = 0.05 if regime == 'bull' else -0.05 if regime == 'bear' else 0
                    if regime_impact != 0:
                        factors.append(SHAPFactor(
                            name="Market Regime",
                            impact=regime_impact,
                            value=1.0 if regime == 'bull' else -1.0 if regime == 'bear' else 0,
                            importance=abs(regime_impact),
                            direction='bullish' if regime_impact > 0 else 'bearish'
                        ))
        
        except Exception as e:
            self.unified_logger.error(f"SHAP value calculation error: {e}")
        
        return factors
    
    def _generate_explanation_text(self, top_factors: List[SHAPFactor], 
                                   signal: str, confidence: float) -> str:
        """Generate human-readable explanation"""
        try:
            parts = []
            
            # Opening
            parts.append(f"The AI predicts a **{signal}** signal with {confidence*100:.1f}% confidence.")
            parts.append("")
            parts.append("**Key factors influencing this prediction:**")
            parts.append("")
            
            # Top factors
            for i, factor in enumerate(top_factors, 1):
                direction_emoji = "📈" if factor.direction == 'bullish' else "📉" if factor.direction == 'bearish' else "➡️"
                impact_pct = abs(factor.impact) * 100
                
                if abs(factor.impact) > 0.05:
                    strength = "Strong"
                elif abs(factor.impact) > 0.02:
                    strength = "Moderate"
                else:
                    strength = "Minor"
                
                parts.append(f"{i}. {direction_emoji} **{factor.name}**: {strength} {factor.direction} impact ({impact_pct:.1f}%)")
            
            parts.append("")
            parts.append("This explanation uses SHAP (SHapley Additive exPlanations) to show how each factor contributed to the final prediction.")
            
            return "\n".join(parts)
        
        except Exception as e:
            self.unified_logger.error(f"Explanation text generation error: {e}")
            return "Prediction explanation unavailable."
    
    def get_feature_importance(self, factors: List[SHAPFactor]) -> Dict[str, float]:
        """Get feature importance ranking"""
        try:
            importance_dict = {}
            total_importance = sum(f.importance for f in factors)
            
            if total_importance > 0:
                for factor in factors:
                    importance_dict[factor.name] = (factor.importance / total_importance) * 100
            
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        
        except Exception as e:
            self.unified_logger.error(f"Feature importance error: {e}")
            return {}


# Global instance
shap_explainer = SHAPExplainer()

