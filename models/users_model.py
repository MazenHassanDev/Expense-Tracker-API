from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from utils.database import Base


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String(100), nullable=False)
    email:Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String(100), nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")