from __future__ import annotations
from datetime import datetime
from sqlalchemy import ForeignKey, func
from src.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    base_url: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="links")  # noqa #type: ignore
    clicks: Mapped[list['Click']] = relationship(back_populates="link") # noqa #type: ignore
