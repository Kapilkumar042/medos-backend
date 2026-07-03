from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    DateTime
)

from sqlalchemy.sql import func

from app.db.base import Base


class OpdBill(Base):

    __tablename__ = "opd_bills"

    id = Column(Integer, primary_key=True)

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        nullable=False
    )

    patient_id = Column(
        Integer,
        ForeignKey("opd_patients.id"),
        nullable=False
    )

    visit_id = Column(
        Integer,
        ForeignKey("opd_visits.id"),
        nullable=True
    )

    bill_no = Column(
        String,
        unique=True,
        nullable=False
    )

    total_amount = Column(
        Numeric(10, 2),
        default=0
    )

    total_discount = Column(
        Numeric(10, 2),
        default=0
    )

    net_amount = Column(
        Numeric(10, 2),
        default=0
    )

    paid_amount = Column(
        Numeric(10, 2),
        default=0
    )

    due_amount = Column(
        Numeric(10, 2),
        default=0
    )

    payment_mode = Column(
        String
    )

    remark = Column(
        String
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
