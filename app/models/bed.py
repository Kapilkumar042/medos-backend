from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.db.base import Base


class Bed(Base):
    __tablename__ = "beds"

    id = Column(
        Integer,
        primary_key=True
    )

    hospital_id = Column(
        Integer
    )

    ward = Column(
        String
    )

    room = Column(
        String
    )

    bed_no = Column(
        String
    )

    bed_type = Column(
        String
    )

    status = Column(
        String,
        default="Available"
    )