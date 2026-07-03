from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean

from app.db.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    hospital_name = Column(
        String(255),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    phone = Column(
        String(20),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    modules = Column(
        String(500)
    )

    is_active = Column(
        Boolean,
        default=True
    )
    