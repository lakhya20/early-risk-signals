from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import pandas as pd
import numpy as np

from backend.core.database import get_db
from backend.core.models import RiskScore
from backend.core.logger import logger
from backend.core.config import settings

from backend.ml.load_model import load_model


router = APIRouter()


class ScoreRequest(BaseModel):
    """Request model for risk scoring endpoint."""
    customer_id: str
    credit_limit: float
    utilization: float
    avg_payment_ratio: float
    min_due_paid_freq: float
    merchant_mix_index: float
    cash_withdrawal_pct: float
    recent_spend_change: float


class ScoreResponse(BaseModel):
    """Response model for risk scoring endpoint."""
    risk_score: float
    risk_level: str
    model_version: str


def calculate_risk_level(score: float) -> str:
    """Calculate risk level based on score."""
    if score >= 0.70:
        return "HIGH"
    elif score >= 0.40:
        return "MEDIUM"
    return "LOW"


@router.post("/predict", response_model=ScoreResponse)
async def predict_risk(payload: ScoreRequest, db: AsyncSession = Depends(get_db)):
    """
    Predict risk score for a customer.
    Endpoint: POST /score/predict
    
    Loads the latest versioned model from backend/ml/models/ automatically.
    """
    logger.info(f"Predicting risk for customer: {payload.customer_id}")

    # Load model bundle (in thread pool to avoid blocking)
    try:
        bundle = await run_in_threadpool(load_model)
        model = bundle["model"]
        scaler = bundle["scaler"]
        version = bundle["version"]  # Version is guaranteed by load_model()
        logger.info(f"✅ Model loaded successfully. Version: {version}")
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")

    # Create DataFrame from input features with training column names
    # Column mapping: client_input → normalized column name (as used during training)
    feature_data = {
        "credit_limit": [payload.credit_limit],
        "utilization": [payload.utilization],
        "avg_payment_ratio": [payload.avg_payment_ratio],
        "min_due_paid_freq": [payload.min_due_paid_freq],
        "merchant_mix_index": [payload.merchant_mix_index],
        "cash_withdrawal_pct": [payload.cash_withdrawal_pct],
        "recent_spend_change": [payload.recent_spend_change],
    }
    
    df = pd.DataFrame(feature_data)
    logger.info(f"📊 Created input DataFrame with columns: {list(df.columns)}")
    logger.info(f"   Input values: {df.iloc[0].to_dict()}")

    # Prepare features for scaling (extract values in correct order)
    # Order must match training: credit_limit, utilization, avg_payment_ratio, 
    # min_due_paid_freq, merchant_mix_index, cash_withdrawal_pct, recent_spend_change
    feature_order = [
        "credit_limit",
        "utilization",
        "avg_payment_ratio",
        "min_due_paid_freq",
        "merchant_mix_index",
        "cash_withdrawal_pct",
        "recent_spend_change",
    ]
    
    X = df[feature_order].values.astype(float)
    logger.info(f"📐 Feature matrix shape: {X.shape}")
    logger.info(f"   Feature values: {X[0].tolist()}")

    # Scale features (in thread pool to avoid blocking)
    try:
        def scale_features():
            X_scaled = scaler.transform(X)
            logger.info(f"🔢 Scaled feature values: {X_scaled[0].tolist()}")
            return X_scaled
        
        X_scaled = await run_in_threadpool(scale_features)
    except Exception as e:
        logger.error(f"❌ Feature scaling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Feature scaling failed: {e}")

    # Predict risk score (in thread pool to avoid blocking)
    try:
        def predict_score():
            proba = model.predict_proba(X_scaled)
            score = float(proba[0][1])  # Probability of class 1 (delinquent)
            logger.info(f"🎯 Raw prediction probability: {score}")
            return score
        
        score = await run_in_threadpool(predict_score)
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        logger.info(f"✅ Final risk score: {score:.4f}")
    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    risk_level = calculate_risk_level(score)
    logger.info(f"⚠️  Risk level: {risk_level}")

    # Save to DB (non-blocking, don't fail request if DB save fails)
    try:
        entry = RiskScore(
            customer_id=payload.customer_id,
            risk_score=score,
            risk_level=risk_level,
            model_version=version,
        )
        db.add(entry)
        await db.commit()
        logger.info(f"💾 Risk score saved to database")
    except Exception as e:
        logger.error(f"⚠️  Failed to save risk score to DB: {e}", exc_info=True)
        # Don't fail the request if DB save fails

    return ScoreResponse(
        risk_score=round(score, 4),
        risk_level=risk_level,
        model_version=version,
    )
