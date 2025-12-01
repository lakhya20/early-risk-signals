from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.core.models import Alert
from backend.core.logger import logger
from backend.api.utils import validate_customer_id, handle_database_error


router = APIRouter()


class AlertPayload(BaseModel):
    """Alert creation payload."""
    customer_id: str = Field(..., description="Customer identifier")
    message: str = Field(..., min_length=1, max_length=500, description="Alert message")
    channel: str = Field(default="email", description="Alert channel (email, sms, push)")


class AlertResponse(BaseModel):
    """Alert response model."""
    id: int
    customer_id: str
    message: str
    channel: str
    status: str
    created_at: str
    sent_at: Optional[str] = None


@router.post("/send", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def send_alert(
    payload: AlertPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Create and queue an alert for a customer.
    
    Args:
        payload: Alert information
        db: Database session
        
    Returns:
        Created alert record
    """
    try:
        customer_id = validate_customer_id(payload.customer_id)
        
        # Validate channel
        valid_channels = ["email", "sms", "push", "webhook"]
        channel = payload.channel.lower()
        if channel not in valid_channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid channel. Must be one of: {', '.join(valid_channels)}"
            )
        
        logger.info(f"Creating alert for customer {customer_id} via {channel}")
        
        # Create alert record
        alert = Alert(
            customer_id=customer_id,
            message=payload.message,
            channel=channel,
            status="queued"
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        logger.info(f"Alert {alert.id} created and queued for customer {customer_id}")
        
        # In production, this would trigger an actual notification service
        # For now, we just log it
        logger.info(
            f"Alert notification: [{channel.upper()}] To: {customer_id}, "
            f"Message: {payload.message[:50]}..."
        )
        
        return AlertResponse(
            id=alert.id,
            customer_id=alert.customer_id,
            message=alert.message,
            channel=alert.channel,
            status=alert.status,
            created_at=alert.created_at.isoformat(),
            sent_at=alert.sent_at.isoformat() if alert.sent_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "alert creation")


@router.get("/{customer_id}", response_model=List[AlertResponse])
async def get_customer_alerts(
    customer_id: str,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all alerts for a customer.
    
    Args:
        customer_id: Customer identifier
        status_filter: Optional status filter (queued, sent, failed)
        db: Database session
        
    Returns:
        List of alert records
    """
    try:
        customer_id = validate_customer_id(customer_id)
        
        logger.info(f"Fetching alerts for customer: {customer_id}")
        
        query = select(Alert).where(Alert.customer_id == customer_id)
        
        if status_filter:
            valid_statuses = ["queued", "sent", "failed"]
            if status_filter.lower() not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"
                )
            query = query.where(Alert.status == status_filter.lower())
        
        query = query.order_by(Alert.created_at.desc())
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        logger.info(f"Found {len(alerts)} alerts for customer {customer_id}")
        
        return [
            AlertResponse(
                id=a.id,
                customer_id=a.customer_id,
                message=a.message,
                channel=a.channel,
                status=a.status,
                created_at=a.created_at.isoformat(),
                sent_at=a.sent_at.isoformat() if a.sent_at else None
            )
            for a in alerts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "alerts fetch")


@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts(
    status_filter: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all alerts with optional filtering.
    
    Args:
        status_filter: Optional status filter
        limit: Maximum number of alerts to return
        db: Database session
        
    Returns:
        List of alert records
    """
    try:
        logger.info(f"Fetching all alerts (limit: {limit})")
        
        query = select(Alert)
        
        if status_filter:
            valid_statuses = ["queued", "sent", "failed"]
            if status_filter.lower() not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"
                )
            query = query.where(Alert.status == status_filter.lower())
        
        query = query.order_by(Alert.created_at.desc()).limit(min(limit, 1000))
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        logger.info(f"Found {len(alerts)} alerts")
        
        return [
            AlertResponse(
                id=a.id,
                customer_id=a.customer_id,
                message=a.message,
                channel=a.channel,
                status=a.status,
                created_at=a.created_at.isoformat(),
                sent_at=a.sent_at.isoformat() if a.sent_at else None
            )
            for a in alerts
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "alerts fetch")
