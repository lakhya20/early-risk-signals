from fastapi import APIRouter, HTTPException
from pathlib import Path
import joblib
from typing import List, Dict

router = APIRouter()

MODEL_DIR = Path("backend/ml/models")

@router.get("/versions")
async def list_versions():
    if not MODEL_DIR.exists():
        return []
    files = sorted([p.name for p in MODEL_DIR.glob("*.pkl")], reverse=True)
    versions = []
    for f in files:
        versions.append(f.replace(".pkl",""))
    return versions

@router.post("/rollback/{version}")
async def rollback(version: str):
    # Activate version: copy to active model path (settings.MODEL_PATH) or set symlink
    active_path = Path("backend/ml/active_model.pkl")
    candidate = MODEL_DIR / f"{version}.pkl"
    if not candidate.exists():
        raise HTTPException(status_code=404, detail="Version not found")
    joblib.dump(joblib.load(candidate), active_path)
    return {"status":"ok","message":f"Rolled back to {version}"}





