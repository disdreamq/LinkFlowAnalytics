from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, func
from app.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from app.src.link.models import Link


class Click(Base):
    __tablename__ = "click"

    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey('link.id', ondelete='CASCADE'))
    user_agent: Mapped[str]
    region: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    link: Mapped['Link'] = relationship(back_populates="clicks")
