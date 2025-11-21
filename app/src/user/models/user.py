from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import func
from app.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.enums.enums import UserTarifPlan

if TYPE_CHECKING:
    from app.src.link.models.link import Link

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    tarifplan: Mapped[UserTarifPlan] = mapped_column(server_default='base', defaul=UserTarifPlan.Base)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    links: Mapped[list[Link]] = relationship(back_populates='link')