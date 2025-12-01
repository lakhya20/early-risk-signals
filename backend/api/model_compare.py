from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.core.database import get_db
from backend.core.models import ModelTrainingHistory
from backend.core.logger import logger
import joblib
from pathlib import Path
from backend.core.config import settings
from typing import Optional

router = APIRouter()

@router.get("/", summary="Compare two model versions")
async def compare_models(
    modelA: Optional[str] = Query(None, description="First model version to compare"),
    modelB: Optional[str] = Query(None, description="Second model version to compare"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare two model versions by reading their model files and calculating metric deltas.
    If modelA and modelB are not provided, compares latest with best previous.
    """
    try:
        models_dir = Path("backend/ml/models")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # If versions provided, compare those specific versions
        if modelA and modelB:
            model_a_path = models_dir / f"{modelA}.pkl"
            model_b_path = models_dir / f"{modelB}.pkl"
            
            if not model_a_path.exists():
                raise HTTPException(status_code=404, detail=f"Model version {modelA} not found")
            if not model_b_path.exists():
                raise HTTPException(status_code=404, detail=f"Model version {modelB} not found")
            
            # Load model bundles (in thread pool to avoid blocking)
            bundle_a = await run_in_threadpool(joblib.load, model_a_path)
            bundle_b = await run_in_threadpool(joblib.load, model_b_path)
            
            # Get history entries for metrics
            stmt_a = select(ModelTrainingHistory).where(ModelTrainingHistory.version == modelA)
            result_a = await db.execute(stmt_a)
            entry_a = result_a.scalars().first()
            
            stmt_b = select(ModelTrainingHistory).where(ModelTrainingHistory.version == modelB)
            result_b = await db.execute(stmt_b)
            entry_b = result_b.scalars().first()
            
            if not entry_a or not entry_b:
                raise HTTPException(status_code=404, detail="Model history entries not found")
            
            metrics_a = {
                "version": entry_a.version,
                "auc": entry_a.auc,
                "accuracy": entry_a.accuracy,
                "precision": entry_a.precision,
                "recall": entry_a.recall,
                "f1": entry_a.f1,
                "created_at": entry_a.created_at
            }
            
            metrics_b = {
                "version": entry_b.version,
                "auc": entry_b.auc,
                "accuracy": entry_b.accuracy,
                "precision": entry_b.precision,
                "recall": entry_b.recall,
                "f1": entry_b.f1,
                "created_at": entry_b.created_at
            }
            
            # Calculate deltas
            deltas = {
                "auc": metrics_a["auc"] - metrics_b["auc"],
                "accuracy": metrics_a["accuracy"] - metrics_b["accuracy"],
                "precision": metrics_a["precision"] - metrics_b["precision"],
                "recall": metrics_a["recall"] - metrics_b["recall"],
                "f1": metrics_a["f1"] - metrics_b["f1"]
            }
            
            return {
                "model_a": metrics_a,
                "model_b": metrics_b,
                "deltas": deltas,
                "model_a_better": metrics_a["auc"] > metrics_b["auc"]
            }
        
        # Otherwise, compare latest with best previous (default behavior)
        stmt = select(ModelTrainingHistory).order_by(desc(ModelTrainingHistory.created_at))
        result = await db.execute(stmt)
        logs = result.scalars().all()

        if not logs:
            raise HTTPException(status_code=404, detail="No training runs found")

        latest = logs[0]

        if len(logs) > 1:
            previous_best = max(logs[1:], key=lambda x: x.auc)
        else:
            previous_best = None

        # Load model files (in thread pool to avoid blocking)
        latest_path = models_dir / f"{latest.version}.pkl"
        latest_bundle = None
        if latest_path.exists():
            try:
                latest_bundle = await run_in_threadpool(joblib.load, latest_path)
            except Exception as e:
                logger.warning(f"Could not load latest model file: {e}")

        previous_bundle = None
        if previous_best:
            previous_path = models_dir / f"{previous_best.version}.pkl"
            if previous_path.exists():
                try:
                    previous_bundle = await run_in_threadpool(joblib.load, previous_path)
                except Exception as e:
                    logger.warning(f"Could not load previous model file: {e}")

        # Calculate deltas if both exist
        deltas = None
        if previous_best:
            deltas = {
                "auc": latest.auc - previous_best.auc,
                "accuracy": latest.accuracy - previous_best.accuracy,
                "precision": latest.precision - previous_best.precision,
                "recall": latest.recall - previous_best.recall,
                "f1": latest.f1 - previous_best.f1
            }

        return {
            "latest_model": {
                "version": latest.version,
                "auc": latest.auc,
                "accuracy": latest.accuracy,
                "precision": latest.precision,
                "recall": latest.recall,
                "f1": latest.f1,
                "created_at": latest.created_at,
                "model_file_exists": latest_bundle is not None
            },
            "best_previous_model": (
                {
                    "version": previous_best.version,
                    "auc": previous_best.auc,
                    "accuracy": previous_best.accuracy,
                    "precision": previous_best.precision,
                    "recall": previous_best.recall,
                    "f1": previous_best.f1,
                    "created_at": previous_best.created_at,
                    "model_file_exists": previous_bundle is not None
                }
                if previous_best else None
            ),
            "deltas": deltas,
            "is_latest_better": (
                previous_best is None or latest.auc >= previous_best.auc
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compare models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to compare models: {e}")



