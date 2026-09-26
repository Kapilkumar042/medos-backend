from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import DateTime
from datetime import datetime

from app.db.base import Base


class IPDPayment(Base):
    __tablename__ = "ipd_payments"

    id = Column(
        Integer,
        primary_key=True
    )

    hospital_id = Column(
        Integer,
        nullable=False
    )

    admission_id = Column(
        Integer,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    payment_type = Column(
        String,
        default="Advance"
    )

    payment_mode = Column(
        String
    )

    remarks = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=datetime.now
    )