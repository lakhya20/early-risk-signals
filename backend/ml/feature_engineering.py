# backend/ml/feature_engineering.py
from typing import Dict, Any, List
import numpy as np
from sklearn.preprocessing import StandardScaler
from backend.core.logger import logger


def validate_feature_value(value: Any, default: float = 0.0) -> float:
    """Safely convert inputs to float, fallback to default on error."""
    try:
        val = float(value)
        if np.isnan(val) or np.isinf(val):
            logger.warning(f"Feature value invalid (NaN/Inf): {value} -> using default {default}")
            return default
        return val
    except Exception:
        logger.warning(f"Feature value conversion failed: {value} -> using default {default}")
        return default


def prepare_features(features: Dict[str, Any], scaler: StandardScaler) -> List[List[float]]:
    """
    Convert a features dict to a scaled 2D list ready for model.predict_proba().
    
    Accepts features from frontend (flexible naming) and maps to model's expected column names.
    Frontend may send: utilisation_pct, min_due_paid_frequency, recent_spend_change_pct
    Model expects: utilization, min_due_paid_freq, recent_spend_change

    Args:
        features: dict containing feature values (can use frontend or model column names)
        scaler: fitted sklearn StandardScaler instance

    Returns:
        2D list (or numpy array) with shape (1, n_features)
    """
    if scaler is None:
        raise ValueError("Scaler must be provided to prepare_features()")

    # Map from frontend column names to model's expected column names
    # This allows flexibility - frontend can send either naming convention
    FEATURE_MAPPING = {
        # Model's expected names (from train_model.py FEATURE_COLUMNS)
        "credit_limit": ["credit_limit"],
        "utilization": ["utilization", "utilisation_pct"],  # Accept both
        "avg_payment_ratio": ["avg_payment_ratio"],
        "min_due_paid_freq": ["min_due_paid_freq", "min_due_paid_frequency"],  # Accept both
        "merchant_mix_index": ["merchant_mix_index"],
        "cash_withdrawal_pct": ["cash_withdrawal_pct"],
        "recent_spend_change": ["recent_spend_change", "recent_spend_change_pct"],  # Accept both
    }
    
    # Ordered list matching train_model.py FEATURE_COLUMNS
    ordered_keys = [
        "credit_limit",
        "utilization",
        "avg_payment_ratio",
        "min_due_paid_freq",
        "merchant_mix_index",
        "cash_withdrawal_pct",
        "recent_spend_change",
    ]

    try:
        # Extract values in the correct order, using mapping to find the right key
        raw = []
        for model_key in ordered_keys:
            possible_keys = FEATURE_MAPPING[model_key]
            value_found = None
            
            # Try to find value using any of the possible keys
            for key in possible_keys:
                if key in features:
                    value_found = features[key]
                    break
            
            if value_found is None:
                # Try case-insensitive match
                for key in possible_keys:
                    for feat_key in features.keys():
                        if feat_key.lower() == key.lower():
                            value_found = features[feat_key]
                            break
                    if value_found is not None:
                        break
            
            # Use default if not found
            raw.append(validate_feature_value(value_found if value_found is not None else 0.0, default=0.0))
            
    except Exception as e:
        logger.error(f"Error processing features: {e}. Features received: {list(features.keys())}")
        raise ValueError(f"Error reading features: {e}")

    arr = np.array([raw], dtype=float)  # shape (1, n_features)

    try:
        scaled = scaler.transform(arr)
    except Exception as e:
        raise ValueError(f"Scaler transform failed: {e}")

    # Return a numpy array (model.predict_proba accepts numpy arrays)
    return scaled
