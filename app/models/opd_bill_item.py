from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric
)

from app.db.base import Base


class OpdBillItem(Base):

    __tablename__ = "opd_bill_items"

    id = Column(
        Integer,
        primary_key=True
    )

    bill_id = Column(
        Integer,
        ForeignKey("opd_bills.id"),
        nullable=False
    )

    category = Column(String)

    name = Column(String)

    code = Column(String)

    qty = Column(Integer)

    amount = Column(
        Numeric(10, 2)
    )

    discount = Column(
        Numeric(10, 2),
        default=0
    )

    remarks = Column(String)
