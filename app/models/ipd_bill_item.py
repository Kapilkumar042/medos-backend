from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import ForeignKey

from app.db.base import Base


class IPDBillItem(Base):
    __tablename__ = "ipd_bill_items"

    id = Column(
        Integer,
        primary_key=True
    )

    bill_id = Column(
        Integer,
        ForeignKey("ipd_bills.id")
    )

    category = Column(
        String
    )

    name = Column(
        String
    )

    qty = Column(
        Float
    )

    rate = Column(
        Float
    )

    amount = Column(
        Float
    )

    discount = Column(
        Float,
        default=0
    )

    remarks = Column(
        String
    )