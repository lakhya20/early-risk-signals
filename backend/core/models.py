from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer, DateTime, Index

from backend.core.database import Base


class Customer(Base):
    """Customer model with financial risk indicators."""
    
    __tablename__ = "customers"
    
    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    credit_limit: Mapped[float] = mapped_column(Float, nullable=False)
    utilisation_pct: Mapped[float] = mapped_column(Float, nullable=False)
    avg_payment_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    min_due_paid_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    num_late_payments: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_payment_gap: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    __table_args__ = (
        Index('idx_customer_updated', 'updated_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Customer(customer_id='{self.customer_id}', utilisation={self.utilisation_pct:.2f}%)>"


class RiskScore(Base):
    """Risk score predictions and history."""
    
    __tablename__ = "risk_scores"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    model_version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    __table_args__ = (
        Index('idx_risk_customer_created', 'customer_id', 'created_at'),
        Index('idx_risk_level', 'risk_level'),
    )
    
    def __repr__(self) -> str:
        return f"<RiskScore(customer_id='{self.customer_id}', score={self.risk_score:.3f}, level='{self.risk_level}')>"


class Alert(Base):
    """Alert records for risk notifications."""
    
    __tablename__ = "alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="email")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_alert_customer_status', 'customer_id', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<Alert(customer_id='{self.customer_id}', status='{self.status}', channel='{self.channel}')>"


class ModelTrainingHistory(Base):
    """Model training history records."""
    
    __tablename__ = "model_training_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    auc: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    precision: Mapped[float] = mapped_column(Float, nullable=False)
    recall: Mapped[float] = mapped_column(Float, nullable=False)
    f1: Mapped[float] = mapped_column(Float, nullable=False)
    dataset_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    dataset_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    __table_args__ = (
        Index('idx_training_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<ModelTrainingHistory(version='{self.version}', auc={self.auc:.4f}, created_at='{self.created_at}')>"
