from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.core.models import ModelTrainingHistory
from backend.core.logger import logger
from backend.core.config import settings
import joblib
from pathlib import Path

router = APIRouter()


@router.post("/{version}")
async def rollback_model(
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Rollback to a specific model version.
    Endpoint: POST /train/rollback/{version}
    
    Copies the selected model version file into settings.MODEL_PATH (active model).
    """
    
    # Verify version exists in database
    stmt = select(ModelTrainingHistory).where(ModelTrainingHistory.version == version)
    result = await db.execute(stmt)
    entry = result.scalars().first()
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Model version {version} not found in training history"
        )
    
    # Ensure models directory exists (versioned models are stored here)
    models_dir = Path("backend/ml/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if versioned file exists
    version_path = models_dir / f"{version}.pkl"
    
    if not version_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Model version {version} not found at {version_path}"
        )

    try:
        # Load the versioned model (in thread pool to avoid blocking)
        bundle = await run_in_threadpool(joblib.load, version_path)
    except Exception as e:
        logger.error(f"Failed to load model version {version}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to load model file: {e}"
        )

    try:
        # Overwrite active model (in thread pool to avoid blocking)
        active_path = Path(settings.MODEL_PATH)
        active_path.parent.mkdir(parents=True, exist_ok=True)
        await run_in_threadpool(joblib.dump, bundle, active_path)
        logger.info(f"Rolled back active model to version {version}")
    except Exception as e:
        logger.error(f"Failed to save active model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to restore model file: {e}"
        )

    return {
        "status": "success",
        "restored_version": version
    }
