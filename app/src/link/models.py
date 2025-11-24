from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, func
from app.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from app.src.user.models import User
    from app.src.click.models import Click


class Link(Base):
    __tablename__ = "link"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped['User'] = relationship(back_populates="links")
    clicks: Mapped[list['Click']] = relationship(back_populates='link')
