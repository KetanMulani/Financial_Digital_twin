from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TwinProfile(Base):
    __tablename__ = "twin_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    monthly_income: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    monthly_expenses: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    cash_savings: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    investments: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    monthly_investment: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    existing_debt: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    debt_interest_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    monthly_debt_payment: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )

    financial_goal: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )