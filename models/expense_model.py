from sqlalchemy import String, Integer, DateTime, Enum, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from utils.database import Base
import enum

class CategoryEnum(enum.Enum):
    Groceries = "Groceries"
    Leisure = "Leisure"
    Electronics = "Electronics"
    Utilities = "Utilities"
    Clothing = "Clothing"
    Health = "Health"
    Others = "Others"

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[CategoryEnum] = mapped_column(Enum(CategoryEnum), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    user:Mapped["User"] = relationship("User", back_populates="expenses")
