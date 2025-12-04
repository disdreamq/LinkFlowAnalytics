from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, func
from src.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.enums.enums import UserTarifPlan


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    tarifplan: Mapped[UserTarifPlan] = mapped_column(
        String(50),
        default=UserTarifPlan.Base,
        server_default=UserTarifPlan.Base.value,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    links: Mapped[list["Link"]] = relationship(  # noqa #type: ignore
        back_populates="user", cascade="all, delete-orphan"
    )
