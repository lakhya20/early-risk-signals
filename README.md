# Early Risk Signals - Credit Card Delinquency Prediction System

Early Risk Signals is an end-to-end platform that surfaces leading indicators of credit card delinquency via an interpretable ML model, a FastAPI backend, and a Vite React frontend.

## Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (optional but recommended)

## Backend Setup
1. `cd backend`
2. `python -m venv .venv && source .venv/bin/activate` (or Windows equivalent)
3. `pip install -r requirements.txt`
4. `uvicorn api.main:app --reload`

## Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev` (default Vite port 5173)

## ML Training Pipeline
1. `cd ml_pipeline/training`
2. Place raw CSV in `../data/raw/credit_risk.csv`
3. Adjust parameters in `config.yaml`
4. `python train.py --config config.yaml`

## Docker Compose
```
docker-compose up --build
```
This spins up the FastAPI backend, Vite frontend, and Postgres database.

## Repository Layout
See `docs/architecture.md` for component interactions and data flows.
