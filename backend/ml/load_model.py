import joblib
from pathlib import Path
from backend.core.config import settings
from backend.core.logger import logger
from datetime import datetime

_model_cache = None
_model_version_cache = None


def find_latest_model_version():
    """
    Find the latest versioned model file from backend/ml/models/.
    Returns (model_path, version_string) tuple.
    Models are named as {YYYYMMDD-HHMMSS}.pkl
    """
    models_dir = Path("backend/ml/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all .pkl files matching version pattern
    model_files = list(models_dir.glob("*.pkl"))
    
    if not model_files:
        raise FileNotFoundError(f"No model files found in {models_dir}")
    
    # Parse version from filename (format: YYYYMMDD-HHMMSS.pkl)
    def extract_version(path: Path) -> tuple:
        try:
            version_str = path.stem  # filename without extension
            # Validate format: YYYYMMDD-HHMMSS
            if len(version_str) == 15 and version_str[8] == '-':
                datetime.strptime(version_str, "%Y%m%d-%H%M%S")
                return (path, version_str)
            return None
        except ValueError:
            return None
    
    # Extract versions and filter valid ones
    valid_models = []
    for model_file in model_files:
        parsed = extract_version(model_file)
        if parsed:
            valid_models.append(parsed)
    
    if not valid_models:
        raise FileNotFoundError(f"No valid versioned model files found in {models_dir}")
    
    # Sort by version string (lexicographically, which works for timestamp format)
    valid_models.sort(key=lambda x: x[1], reverse=True)
    
    latest_path, latest_version = valid_models[0]
    logger.info(f"Found {len(valid_models)} versioned model(s). Latest: {latest_version}")
    
    return latest_path, latest_version


def load_model():
    """
    Loads the latest saved model bundle from backend/ml/models/.
    Automatically detects the newest versioned model by timestamp.
    
    Returns:
    {
        "model": XGBClassifier(),
        "scaler": StandardScaler(),
        "version": "20251129-151424"
    }
    """
    global _model_cache, _model_version_cache

    try:
        # Find latest versioned model
        model_path, version = find_latest_model_version()
        
        # Check cache (invalidate if version changed)
        if _model_cache is not None and _model_version_cache == version:
            logger.info(f"Using cached model version: {version}")
            return _model_cache
        
        logger.info(f"📦 Loading model from {model_path} (version: {version})")
        bundle = joblib.load(model_path)

        # Sanity checks
        if not isinstance(bundle, dict):
            raise ValueError("Loaded model bundle is not a dictionary")

        if "model" not in bundle or "scaler" not in bundle:
            raise ValueError(f"Model bundle missing required keys. Found: {list(bundle.keys())}")

        model = bundle["model"]
        scaler = bundle["scaler"]

        # Verify model supports predict_proba
        if not hasattr(model, "predict_proba"):
            raise ValueError("Loaded model does not have predict_proba()")

        # Add version to bundle if not present
        bundle["version"] = version
        
        # Update cache
        _model_cache = bundle
        _model_version_cache = version
        
        logger.info(f"✅ Model loaded successfully. Version: {version}")
        logger.info(f"   Model type: {type(model).__name__}")
        logger.info(f"   Scaler type: {type(scaler).__name__}")

        return bundle

    except FileNotFoundError as e:
        logger.error(f"❌ Model file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}", exc_info=True)
        raise RuntimeError(f"Model loading failed: {e}")
