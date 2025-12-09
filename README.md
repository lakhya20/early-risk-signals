Early Risk Signals – Credit Card Delinquency Prediction System

A full-stack platform that predicts credit card delinquency risk using an interpretable ML model, a FastAPI backend, and a React + Vite dashboard.

🌟 Features

Real-time risk scoring based on customer financial behavior

Model training pipeline with versioned models

Model rollback system for safe reversion to previous ML versions

Customer insights dashboard with alerts, profiles, and risk explanation

Interactive React UI with neon-dark theme and smooth UX

FastAPI backend with ML model serving, monitoring & logs

⚙️ Tech Stack
Backend

FastAPI

Python (scikit-learn, pandas, numpy)

Model versioning (joblib)

Frontend

React + Vite

Pure CSS (Neon UI styling)

ML

Random Forest / XGBoost

Feature engineering pipeline

Scalable training module

🚀 Setup Instructions
Backend Setup
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload

Frontend Setup
cd frontend
npm install
npm run dev

🧠 ML Training Pipeline
cd ml_pipeline/training
# Place dataset in: ./data/raw/credit_risk.csv
# Adjust settings in: config.yaml
python train.py --config config.yaml

🐳 Docker (Optional)
docker-compose up --build

🧱 Repository Structure
backend/         # FastAPI backend
frontend/        # React dashboard
database/        # DB migrations & seed files
ml_pipeline/     # Training pipeline & model artifacts
docs/            # Architecture & API documentation
infrastructure/  # Deployment config
