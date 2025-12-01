from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.core.database import get_db
from backend.core.models import Customer
from backend.core.logger import logger
from backend.api.utils import validate_customer_id, paginate, handle_database_error


router = APIRouter()


class CustomerCreate(BaseModel):
    """Customer creation payload."""
    customer_id: str
    credit_limit: float
    utilisation_pct: float
    avg_payment_ratio: float
    min_due_paid_frequency: float
    num_late_payments: int = 0
    last_payment_gap: int = 0


class CustomerResponse(BaseModel):
    """Customer response model."""
    customer_id: str
    credit_limit: float
    utilisation_pct: float
    avg_payment_ratio: float
    min_due_paid_frequency: float
    num_late_payments: int
    last_payment_gap: int
    updated_at: str


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new customer record.
    
    Args:
        customer_data: Customer information
        db: Database session
        
    Returns:
        Created customer record
    """
    try:
        customer_id = validate_customer_id(customer_data.customer_id)
        
        logger.info(f"Creating customer: {customer_id}")
        
        # Check if customer already exists
        existing = await db.execute(
            select(Customer).where(Customer.customer_id == customer_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Customer {customer_id} already exists"
            )
        
        # Create new customer
        customer = Customer(
            customer_id=customer_id,
            credit_limit=customer_data.credit_limit,
            utilisation_pct=customer_data.utilisation_pct,
            avg_payment_ratio=customer_data.avg_payment_ratio,
            min_due_paid_frequency=customer_data.min_due_paid_frequency,
            num_late_payments=customer_data.num_late_payments,
            last_payment_gap=customer_data.last_payment_gap,
        )
        
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        
        logger.info(f"Customer {customer_id} created successfully")
        
        return CustomerResponse(
            customer_id=customer.customer_id,
            credit_limit=customer.credit_limit,
            utilisation_pct=customer.utilisation_pct,
            avg_payment_ratio=customer.avg_payment_ratio,
            min_due_paid_frequency=customer.min_due_paid_frequency,
            num_late_payments=customer.num_late_payments,
            last_payment_gap=customer.last_payment_gap,
            updated_at=customer.updated_at.isoformat(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "customer creation")


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get customer by ID.
    
    Args:
        customer_id: Customer identifier
        db: Database session
        
    Returns:
        Customer record
    """
    try:
        customer_id = validate_customer_id(customer_id)
        
        logger.info(f"Fetching customer: {customer_id}")
        
        result = await db.execute(
            select(Customer).where(Customer.customer_id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found"
            )
        
        return CustomerResponse(
            customer_id=customer.customer_id,
            credit_limit=customer.credit_limit,
            utilisation_pct=customer.utilisation_pct,
            avg_payment_ratio=customer.avg_payment_ratio,
            min_due_paid_frequency=customer.min_due_paid_frequency,
            num_late_payments=customer.num_late_payments,
            last_payment_gap=customer.last_payment_gap,
            updated_at=customer.updated_at.isoformat(),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "customer fetch")


@router.get("/", response_model=List[CustomerResponse])
async def get_all_customers(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all customers with pagination.
    
    Args:
        page: Page number
        size: Items per page
        db: Database session
        
    Returns:
        List of customer records
    """
    try:
        logger.info(f"Fetching customers - page {page}, size {size}")
        
        result = await db.execute(select(Customer))
        all_customers = result.scalars().all()
        
        # Convert to response format
        customers_list = [
            CustomerResponse(
                customer_id=c.customer_id,
                credit_limit=c.credit_limit,
                utilisation_pct=c.utilisation_pct,
                avg_payment_ratio=c.avg_payment_ratio,
                min_due_paid_frequency=c.min_due_paid_frequency,
                num_late_payments=c.num_late_payments,
                last_payment_gap=c.last_payment_gap,
                updated_at=c.updated_at.isoformat(),
            )
            for c in all_customers
        ]
        
        # Apply pagination
        paginated = paginate(customers_list, page=page, size=size)
        
        logger.info(f"Returning {len(paginated['items'])} customers")
        
        return paginated["items"]
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_database_error(e, "customers fetch")
