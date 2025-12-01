from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from backend.core.logger import logger

router = APIRouter()

ACTIVE_MODEL_PATH = Path("backend/ml/active_model.pkl")
MODEL_DIR = Path("backend/ml/models")

class ScoreInput(BaseModel):
    customer_id: Optional[str] = None
    credit_limit: Optional[float] = None
    utilization: Optional[float] = None
    avg_payment_ratio: Optional[float] = None
    min_due_paid_freq: Optional[float] = None
    merchant_mix_index: Optional[float] = None
    cash_withdrawal_pct: Optional[float] = None
    recent_spend_change: Optional[float] = None

def load_bundle() -> Dict[str,Any]:
    """Load model bundle, preferring models with 'features' key."""
    # Try active model first
    if ACTIVE_MODEL_PATH.exists():
        try:
            bundle = joblib.load(ACTIVE_MODEL_PATH)
            if isinstance(bundle, dict) and "model" in bundle and "scaler" in bundle:
                logger.info(f"Loaded active model. Bundle keys: {list(bundle.keys())}")
                return bundle
        except Exception as e:
            logger.warning(f"Failed to load active model: {e}")
    
    # Fallback: find latest model in MODEL_DIR that has features
    if MODEL_DIR.exists():
        models = sorted(MODEL_DIR.glob("*.pkl"), reverse=True)
        logger.info(f"Found {len(models)} model file(s) in {MODEL_DIR}")
        
        # First, try to find one with features
        for model_path in models:
            try:
                bundle = joblib.load(model_path)
                if isinstance(bundle, dict) and "model" in bundle and "scaler" in bundle and "features" in bundle:
                    logger.info(f"Loaded model with features from {model_path.name}")
                    return bundle
            except Exception as e:
                logger.warning(f"Failed to load {model_path.name}: {e}")
                continue
        
        # If no model with features, try any valid bundle
        for model_path in models:
            try:
                bundle = joblib.load(model_path)
                if isinstance(bundle, dict) and "model" in bundle and "scaler" in bundle:
                    logger.warning(f"Loaded model without features from {model_path.name}")
                    return bundle
            except Exception:
                continue
    
    raise FileNotFoundError("No valid model available. Please train a new model using POST /train/")

@router.post("/predict")
async def predict(input: ScoreInput):
    # Validate payload contains either customer_id or the required numeric features
    data = input.dict()
    bundle = None
    try:
        bundle = load_bundle()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No model loaded: {e}")

    # Check bundle structure
    if not isinstance(bundle, dict):
        raise HTTPException(status_code=500, detail=f"Invalid model bundle format. Expected dict, got {type(bundle)}")
    
    if "model" not in bundle:
        raise HTTPException(status_code=500, detail="Model bundle missing 'model' key")
    if "scaler" not in bundle:
        raise HTTPException(status_code=500, detail="Model bundle missing 'scaler' key")

    features = bundle.get("features")
    if not features:
        logger.warning("Model bundle missing 'features' key. Bundle keys: %s", list(bundle.keys()))
        # Fallback: use expected feature order if not in bundle (backward compatibility)
        # This matches the normalized column names from training
        features = [
            "credit_limit",
            "utilization",
            "avg_payment_ratio",
            "min_due_paid_freq",
            "merchant_mix_index",
            "cash_withdrawal_pct",
            "recent_spend_change",
        ]
        logger.warning("Using default feature order. For best results, retrain the model using POST /train/")
        logger.info(f"Using default features: {features}")
    else:
        logger.info(f"Using features from bundle: {features}")

    # Build feature vector based on feature order
    X = []
    for f in features:
        # map expected feature naming variants
        if f in data and data[f] is not None:
            X.append(float(data[f]))
            continue
        # try alternate keys
        alt = f.replace("_pct","_pct").replace("credit_limit","credit_limit").replace("%","pct")
        if alt in data and data[alt] is not None:
            X.append(float(data[alt]))
            continue
        # missing -> 0
        X.append(0.0)

    # scale and predict
    scaler = bundle.get("scaler")
    model = bundle.get("model")
    X_arr = np.array(X).reshape(1,-1)
    if scaler is not None:
        X_arr = scaler.transform(X_arr)
    if hasattr(model, "predict_proba"):
        proba = float(model.predict_proba(X_arr)[:,1][0])
    else:
        proba = float(model.predict(X_arr)[0])

    # Risk level thresholds (matching specification)
    if proba >= 0.70:
        level = "HIGH"
    elif proba >= 0.40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"risk_score": round(proba,4), "risk_level": level, "model_version": bundle.get("version","unknown")}

