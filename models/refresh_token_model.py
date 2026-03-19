from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from utils.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    token:Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at:Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user:Mapped["User"] = relationship("User", back_populates="refresh_tokens")