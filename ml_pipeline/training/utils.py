from pathlib import Path
import pandas as pd


def load_raw_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'balance' in df.columns and 'credit_limit' in df.columns:
        df['utilization'] = df['balance'] / df['credit_limit'].replace(0, 1)
    df = df.fillna(0)
    return df
