from app.db.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    tarifplan: Mapped[]
    links: Mapped[list["Link"]] = relationship(
        back_populates='user', cascade='all'
    )