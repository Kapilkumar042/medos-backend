from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime
)
from datetime import datetime

from app.db.base import Base


class LabTest(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        nullable=False
    )

    code = Column(String, unique=True)

    test_name = Column(String)
    category = Column(String)

    price = Column(Float)

    sample_type = Column(String)
    report_time = Column(String)
    method = Column(String)

    status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
