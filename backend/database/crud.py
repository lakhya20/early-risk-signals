from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Customer, RiskScore


class CustomerRepository:

    @staticmethod
    async def get_customer(db: AsyncSession, customer_id: str):
        result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_customers(db: AsyncSession):
        result = await db.execute(select(Customer))
        return result.scalars().all()


class RiskRepository:

    @staticmethod
    async def save_risk_score(db: AsyncSession, entry: RiskScore):
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

