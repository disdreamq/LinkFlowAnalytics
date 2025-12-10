from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    base_url: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    click_counter: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="links")  # noqa #type: ignore
    clicks: Mapped[list["Click"]] = relationship(  # noqa #type: ignore
        back_populates="link"
    )
