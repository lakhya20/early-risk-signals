# backend/api/train_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import pandas as pd
import io
import joblib
from pathlib import Path
from typing import List

from backend.ml.train_model import train_from_dataframe
from backend.core.config import settings
from backend.core.logger import logger
from backend.core.database import get_db
from backend.core.models import ModelTrainingHistory

router = APIRouter()

class TrainResponse(BaseModel):
    model_version: str
    auc: float
    accuracy: float
    precision: float
    recall: float
    f1: float

class TrainHistoryResponse(BaseModel):
    version: str
    auc: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    dataset_rows: int
    dataset_columns: int
    created_at: datetime

@router.post("/", response_model=TrainResponse)
async def train_model_api(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    logger.info(f"Received training file: {file.filename}")

    # read bytes safely (use await file.read() to avoid file pointer issues)
    try:
        content = await file.read()
        if file.filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.lower().endswith((".xls", ".xlsx")):
            # Do not assume sheet name - try default sheet
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .csv or .xlsx")
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    # call training pipeline (train_from_dataframe handles normalization)
    try:
        result = await _run_training_in_thread(df)
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

    # result expected to contain "model_version" and "bundle"
    bundle = result.get("bundle")
    model_version = result.get("model_version") or result.get("version")
    if not bundle or not model_version:
        logger.error("Training result missing bundle or version.")
        raise HTTPException(status_code=500, detail="Training produced incomplete result.")

    # ensure models dir exists and save versioned bundle
    model_dir = Path("backend/ml/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    versioned_path = model_dir / f"{model_version}.pkl"
    joblib.dump(bundle, str(versioned_path))
    logger.info(f"Saved model bundle at {versioned_path}")

    # also save latest pointer (optional)
    latest_path = Path("backend/ml/models/latest.pkl")
    joblib.dump(bundle, str(latest_path))

    # Store training history (non-fatal if DB save fails)
    try:
        history_entry = ModelTrainingHistory(
            version=model_version,
            auc=result.get("auc", 0.0),
            accuracy=result.get("accuracy", 0.0),
            precision=result.get("precision", 0.0),
            recall=result.get("recall", 0.0),
            f1=result.get("f1", 0.0),
            dataset_rows=int(df.shape[0]),
            dataset_columns=int(df.shape[1]),
        )
        db.add(history_entry)
        await db.commit()
        logger.info(f"Training history saved: {model_version}")
    except Exception as e:
        logger.error(f"Failed to save training history: {e}", exc_info=True)

    return TrainResponse(
        model_version=model_version,
        auc=result.get("auc", 0.0),
        accuracy=result.get("accuracy", 0.0),
        precision=result.get("precision", 0.0),
        recall=result.get("recall", 0.0),
        f1=result.get("f1", 0.0),
    )


async def _run_training_in_thread(df):
    """
    Run the CPU-heavy training in a threadpool so it doesn't block the event loop.
    """
    from fastapi.concurrency import run_in_threadpool
    def _train():
        return train_from_dataframe(df)
    return await run_in_threadpool(_train)
