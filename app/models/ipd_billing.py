from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from datetime import datetime

from app.db.base import Base


class IPDBill(Base):
    __tablename__ = "ipd_bills"

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
        ForeignKey("ipd_admissions.id")
    )

    patient_id = Column(
        Integer,
        ForeignKey("opd_patients.id")
    )

    bill_no = Column(
        String,
        unique=True
    )

    total_amount = Column(
        Float,
        default=0
    )

    discount_amount = Column(
        Float,
        default=0
    )

    net_amount = Column(
        Float,
        default=0
    )

    advance_paid = Column(
    Float,
    default=0
   )

    paid_amount = Column(
        Float,
        default=0
    )

    due_amount = Column(
        Float,
        default=0
    )

    payment_mode = Column(
        String
    )

    remark = Column(
        String
    )
    bill_date = Column(
    DateTime,
    nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )