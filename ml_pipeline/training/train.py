import argparse
import joblib
from pathlib import Path
import yaml
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from .utils import load_raw_data, engineer_features

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'model_registry' / 'latest_model.pkl'


def train(config_path):
    config_path = Path(config_path)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    df = load_raw_data(ROOT / 'data' / 'raw' / config['data']['file'])
    df = engineer_features(df)
    target = config['data']['target']
    if target not in df.columns:
        raise ValueError(f"target column {target} missing")
    X = df.drop(columns=[target])
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config['training']['test_size'],
        random_state=42,
    )
    model = XGBClassifier(**config['training']['params'])
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, REGISTRY)
    print(f'Model saved to {REGISTRY}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yaml')
    args = parser.parse_args()
    train(args.config)
