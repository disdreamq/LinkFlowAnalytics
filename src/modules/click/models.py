from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id", ondelete="CASCADE"))
    user_agent: Mapped[str]
    user_ip: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    link: Mapped["Link"] = relationship(back_populates="clicks")  # noqa #type: ignore
