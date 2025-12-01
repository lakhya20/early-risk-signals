import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score
from datetime import datetime
import joblib

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("%","pct").replace("-","_") for c in df.columns]
    return df

def train_from_dataframe(df: pd.DataFrame) -> dict:
    df = _normalize_columns(df)
    # possible target names
    target_candidates = ["dpd_bucket_next_month","delinquency_flag","target"]
    target_col = next((c for c in target_candidates if c in df.columns), None)
    if not target_col:
        raise ValueError(f"None of {target_candidates} found in columns: {list(df.columns)}")

    # If target is multi-class (e.g. DPD buckets), convert to binary: 0=no-dpd, 1=dpd (>=1)
    y_raw = df[target_col]
    try:
        y = (y_raw.astype(int) >= 1).astype(int)
    except:
        # fallback: map typical labels
        y = y_raw.map(lambda v: 1 if str(v).strip() not in ("0","no","none","nan","") else 0).fillna(0).astype(int)

    # Select feature columns (exclude ID + target)
    exclude = {target_col, "customer_id", "customer id", "id"}
    feature_cols = [c for c in df.columns if c not in exclude]
    if not feature_cols:
        raise ValueError("No feature columns found after excluding target/id.")

    X = df[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if len(set(y))>1 else None)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:,1] if hasattr(model, "predict_proba") else model.predict(X_test_scaled)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "auc": float(roc_auc_score(y_test, y_proba)) if len(set(y_test))>1 else 0.0,
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    }

    version = datetime.now().strftime("%Y%m%d-%H%M%S")

    bundle = {
        "model": model,
        "scaler": scaler,
        "features": feature_cols,
        "version": version
    }

    return {
        "model_version": version,
        "auc": metrics["auc"],
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1": metrics["f1"],
        "bundle": bundle
    }
