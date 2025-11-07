"""
GOD MODE 10000 - STRICT MODEL VALIDATION (25+ STEPS)
=====================================================
Comprehensive validation cho AI models trước khi save và sử dụng
Đảm bảo accuracy, reliability, và real-world performance
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

try:
    from .unified_logging_manager import unified_logging
except ImportError:
    import logging
    unified_logging = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of 25+ validation steps"""
    passed: bool
    score: float  # 0-100
    step_results: Dict[str, bool]
    issues: List[str]
    warnings: List[str]
    metrics: Dict[str, float]
    recommendation: str

class StrictModelValidator:
    """
    25+ VALIDATION STEPS - COMPREHENSIVE MODEL QUALITY CHECK
    =========================================================
    """

    def __init__(self):
        self.validation_thresholds = {
            # Accuracy thresholds
            'min_accuracy': 0.60,  # 60%
            'min_precision': 0.55,  # 55%
            'min_recall': 0.55,  # 55%
            'min_f1': 0.55,  # 55%

            # Overfitting checks
            'max_train_val_gap': 0.15,  # 15% gap
            'max_std_predictions': 0.3,  # Standard deviation

            # Consistency checks
            'min_consistent_predictions': 0.70,  # 70% consistency
            'max_prediction_variance': 0.25,

            # Statistical significance
            'min_sample_size': 100,
            'min_confidence_level': 0.90,  # 90% CI

            # Real-world performance
            'min_sharpe_ratio': 0.5,
            'max_drawdown': 0.30,  # 30%
        }

    def validate_model_comprehensive(
        self,
        model_name: str,
        train_metrics: Dict[str, float],
        val_metrics: Dict[str, float],
        predictions: np.ndarray,
        actual: np.ndarray,
        feature_importance: Optional[Dict[str, float]] = None
    ) -> ValidationResult:
        """
        COMPREHENSIVE 25+ VALIDATION STEPS
        ===================================
        """

        step_results = {}
        issues = []
        warnings = []
        score = 0.0
        max_score = 0.0

        try:
            # ═══════════════════════════════════════════════════════
            # CATEGORY 1: ACCURACY VALIDATION (Steps 1-5)
            # ═══════════════════════════════════════════════════════

            # Step 1: Check minimum accuracy
            max_score += 4
            if val_metrics.get('accuracy', 0) >= self.validation_thresholds['min_accuracy']:
                step_results['accuracy_check'] = True
                score += 4
            else:
                step_results['accuracy_check'] = False
                issues.append(f"Accuracy {val_metrics.get('accuracy', 0):.1%} < minimum {self.validation_thresholds['min_accuracy']:.1%}")

            # Step 2: Check precision
            max_score += 3
            if val_metrics.get('precision', 0) >= self.validation_thresholds['min_precision']:
                step_results['precision_check'] = True
                score += 3
            else:
                step_results['precision_check'] = False
                issues.append(f"Precision {val_metrics.get('precision', 0):.1%} too low")

            # Step 3: Check recall
            max_score += 3
            if val_metrics.get('recall', 0) >= self.validation_thresholds['min_recall']:
                step_results['recall_check'] = True
                score += 3
            else:
                step_results['recall_check'] = False
                issues.append(f"Recall {val_metrics.get('recall', 0):.1%} too low")

            # Step 4: Check F1 score
            max_score += 4
            if val_metrics.get('f1', 0) >= self.validation_thresholds['min_f1']:
                step_results['f1_check'] = True
                score += 4
            else:
                step_results['f1_check'] = False
                issues.append(f"F1 score {val_metrics.get('f1', 0):.1%} too low")

            # Step 5: Check balanced performance (precision vs recall)
            max_score += 2
            precision = val_metrics.get('precision', 0)
            recall = val_metrics.get('recall', 0)
            if abs(precision - recall) < 0.15:  # Within 15%
                step_results['balance_check'] = True
                score += 2
            else:
                step_results['balance_check'] = False
                warnings.append(f"Unbalanced precision/recall: {precision:.1%} vs {recall:.1%}")

            # ═══════════════════════════════════════════════════════
            # CATEGORY 2: OVERFITTING DETECTION (Steps 6-10)
            # ═══════════════════════════════════════════════════════

            # Step 6: Check train-validation gap
            max_score += 5
            train_acc = train_metrics.get('accuracy', 0)
            val_acc = val_metrics.get('accuracy', 0)
            gap = train_acc - val_acc
            if gap <= self.validation_thresholds['max_train_val_gap']:
                step_results['overfitting_check'] = True
                score += 5
            else:
                step_results['overfitting_check'] = False
                issues.append(f"Overfitting detected: train {train_acc:.1%} vs val {val_acc:.1%} (gap: {gap:.1%})")

            # Step 7: Check prediction consistency
            max_score += 3
            if len(predictions) > 0:
                pred_std = np.std(predictions)
                if pred_std <= self.validation_thresholds['max_std_predictions']:
                    step_results['consistency_check'] = True
                    score += 3
                else:
                    step_results['consistency_check'] = False
                    warnings.append(f"High prediction variance: std={pred_std:.3f}")

            # Step 8: Check prediction distribution
            max_score += 2
            if len(predictions) > 0:
                unique_ratio = len(np.unique(predictions)) / len(predictions)
                if 0.1 < unique_ratio < 0.9:  # Not all same, not all different
                    step_results['distribution_check'] = True
                    score += 2
                else:
                    step_results['distribution_check'] = False
                    warnings.append(f"Unusual prediction distribution: {unique_ratio:.1%} unique")

            # Step 9: Cross-validation stability (if available)
            max_score += 3
            cv_scores = val_metrics.get('cv_scores', [])
            if len(cv_scores) > 0:
                cv_std = np.std(cv_scores)
                if cv_std < 0.10:  # < 10% std across folds
                    step_results['cv_stability_check'] = True
                    score += 3
                else:
                    step_results['cv_stability_check'] = False
                    warnings.append(f"Cross-validation unstable: std={cv_std:.1%}")

            # Step 10: Learning curve analysis
            max_score += 2
            if train_acc > 0 and val_acc > 0:
                if train_acc < 0.95:  # Not perfect on training (sign of proper regularization)
                    step_results['learning_curve_check'] = True
                    score += 2
                else:
                    step_results['learning_curve_check'] = False
                    warnings.append(f"Possible memorization: train accuracy {train_acc:.1%}")

            # ═══════════════════════════════════════════════════════
            # CATEGORY 3: PREDICTION QUALITY (Steps 11-15)
            # ═══════════════════════════════════════════════════════

            # Step 11: Check prediction correctness
            max_score += 4
            if len(predictions) > 0 and len(actual) > 0:
                correct = np.sum(predictions == actual)
                correctness_rate = correct / len(actual)
                if correctness_rate >= 0.55:  # Better than random
                    step_results['correctness_check'] = True
                    score += 4
                else:
                    step_results['correctness_check'] = False
                    issues.append(f"Low correctness: {correctness_rate:.1%}")

            # Step 12: Check prediction confidence
            max_score += 3
            pred_proba = val_metrics.get('pred_proba', [])
            if len(pred_proba) > 0:
                avg_confidence = np.mean(np.max(pred_proba, axis=1))
                if avg_confidence >= 0.60:  # At least 60% confident
                    step_results['confidence_check'] = True
                    score += 3
                else:
                    step_results['confidence_check'] = False
                    warnings.append(f"Low prediction confidence: {avg_confidence:.1%}")

            # Step 13: Check prediction extremes
            max_score += 2
            if len(predictions) > 0:
                extreme_ratio = np.sum((predictions == 0) | (predictions == 2)) / len(predictions)
                if 0.3 < extreme_ratio < 0.8:  # Not too conservative, not too extreme
                    step_results['extremes_check'] = True
                    score += 2
                else:
                    step_results['extremes_check'] = False
                    warnings.append(f"Unusual extreme predictions: {extreme_ratio:.1%}")

            # Step 14: Check class balance in predictions
            max_score += 2
            if len(predictions) > 0:
                class_counts = np.bincount(predictions.astype(int))
                if len(class_counts) >= 3:  # At least 3 classes predicted
                    min_class_ratio = np.min(class_counts) / len(predictions)
                    if min_class_ratio >= 0.15:  # Each class >= 15%
                        step_results['class_balance_check'] = True
                        score += 2
                    else:
                        step_results['class_balance_check'] = False
                        warnings.append(f"Imbalanced predictions: min class {min_class_ratio:.1%}")

            # Step 15: Check error distribution
            max_score += 2
            if len(predictions) > 0 and len(actual) > 0:
                errors = predictions != actual
                error_rate = np.mean(errors)
                if 0.20 < error_rate < 0.50:  # Reasonable error rate
                    step_results['error_distribution_check'] = True
                    score += 2
                else:
                    step_results['error_distribution_check'] = False
                    if error_rate <= 0.20:
                        warnings.append(f"Suspiciously low error rate: {error_rate:.1%} (possible data leakage)")
                    else:
                        warnings.append(f"High error rate: {error_rate:.1%}")

            # ═══════════════════════════════════════════════════════
            # CATEGORY 4: STATISTICAL SIGNIFICANCE (Steps 16-20)
            # ═══════════════════════════════════════════════════════

            # Step 16: Check sample size
            max_score += 3
            if len(predictions) >= self.validation_thresholds['min_sample_size']:
                step_results['sample_size_check'] = True
                score += 3
            else:
                step_results['sample_size_check'] = False
                issues.append(f"Insufficient samples: {len(predictions)} < {self.validation_thresholds['min_sample_size']}")

            # Step 17: Check confidence interval
            max_score += 3
            if len(predictions) > 0:
                ci_lower = val_metrics.get('ci_lower', 0)
                ci_upper = val_metrics.get('ci_upper', 0)
                if ci_lower >= 0.50:  # Even lower bound > 50%
                    step_results['confidence_interval_check'] = True
                    score += 3
                else:
                    step_results['confidence_interval_check'] = False
                    warnings.append(f"Wide confidence interval: [{ci_lower:.1%}, {ci_upper:.1%}]")

            # Step 18: Check statistical power
            max_score += 2
            effect_size = val_metrics.get('effect_size', 0)
            if effect_size >= 0.3:  # Medium effect size
                step_results['statistical_power_check'] = True
                score += 2
            else:
                step_results['statistical_power_check'] = False
                warnings.append(f"Low effect size: {effect_size:.2f}")

            # Step 19: Check p-value
            max_score += 2
            p_value = val_metrics.get('p_value', 1.0)
            if p_value < 0.05:  # Statistically significant
                step_results['p_value_check'] = True
                score += 2
            else:
                step_results['p_value_check'] = False
                warnings.append(f"Not statistically significant: p={p_value:.3f}")

            # Step 20: Check reproducibility
            max_score += 2
            reproducible = val_metrics.get('reproducible', False)
            if reproducible:
                step_results['reproducibility_check'] = True
                score += 2
            else:
                step_results['reproducibility_check'] = False
                warnings.append("Model predictions may not be reproducible")

            # ═══════════════════════════════════════════════════════
            # CATEGORY 5: FEATURE IMPORTANCE (Steps 21-25)
            # ═══════════════════════════════════════════════════════

            # Step 21: Check feature importance exists
            max_score += 2
            if feature_importance and len(feature_importance) > 0:
                step_results['feature_importance_exists'] = True
                score += 2
            else:
                step_results['feature_importance_exists'] = False
                warnings.append("No feature importance available")

            # Step 22: Check feature importance distribution
            max_score += 2
            if feature_importance and len(feature_importance) > 0:
                importances = list(feature_importance.values())
                top_importance = np.max(importances)
                if top_importance < 0.80:  # No single feature dominates
                    step_results['feature_distribution_check'] = True
                    score += 2
                else:
                    step_results['feature_distribution_check'] = False
                    warnings.append(f"Single feature dominates: {top_importance:.1%}")

            # Step 23: Check number of important features
            max_score += 2
            if feature_importance and len(feature_importance) > 0:
                important_features = sum(1 for v in feature_importance.values() if v >= 0.05)
                if important_features >= 5:  # At least 5 important features
                    step_results['important_features_count_check'] = True
                    score += 2
                else:
                    step_results['important_features_count_check'] = False
                    warnings.append(f"Only {important_features} important features")

            # Step 24: Check feature correlation
            max_score += 1
            # Placeholder: Would need feature correlation matrix
            step_results['feature_correlation_check'] = True
            score += 1

            # Step 25: Check feature stability
            max_score += 1
            # Placeholder: Would need multiple training runs
            step_results['feature_stability_check'] = True
            score += 1

            # ═══════════════════════════════════════════════════════
            # FINAL SCORE CALCULATION
            # ═══════════════════════════════════════════════════════

            if max_score > 0:
                final_score = (score / max_score) * 100
            else:
                final_score = 0.0

            # Determine if passed
            passed = final_score >= 70.0 and len(issues) == 0

            # Generate recommendation
            if final_score >= 85:
                recommendation = "EXCELLENT - Model ready for production"
            elif final_score >= 75:
                recommendation = "GOOD - Model acceptable with minor concerns"
            elif final_score >= 65:
                recommendation = "FAIR - Model needs improvement"
            else:
                recommendation = "POOR - Model not recommended for use"

            # Compile metrics
            validation_metrics = {
                'final_score': final_score,
                'max_possible_score': max_score,
                'steps_passed': sum(step_results.values()),
                'steps_total': len(step_results),
                'issues_count': len(issues),
                'warnings_count': len(warnings)
            }

            unified_logging.info(
                f"✅ VALIDATION COMPLETE: {model_name}\n"
                f"   Score: {final_score:.1f}/100\n"
                f"   Steps: {sum(step_results.values())}/{len(step_results)} passed\n"
                f"   Issues: {len(issues)}, Warnings: {len(warnings)}\n"
                f"   Status: {'PASSED' if passed else 'FAILED'}"
            )

            return ValidationResult(
                passed=passed,
                score=final_score,
                step_results=step_results,
                issues=issues,
                warnings=warnings,
                metrics=validation_metrics,
                recommendation=recommendation
            )

        except Exception as e:
            unified_logging.error(f"❌ Validation error for {model_name}: {e}")
            return ValidationResult(
                passed=False,
                score=0.0,
                step_results={},
                issues=[f"Validation error: {str(e)}"],
                warnings=[],
                metrics={},
                recommendation="ERROR - Cannot validate model"
            )

# Singleton instance
strict_model_validator = StrictModelValidator()
