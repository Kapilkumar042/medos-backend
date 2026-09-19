from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String

from app.db.base import Base


class RadiologyTest(Base):
    __tablename__ = "radiology_tests"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    code = Column(String, nullable=True)
    name = Column(String, nullable=False)
    modality = Column(String)
    body_part = Column(String)
    report_time = Column(String)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    code = Column(String, nullable=True)
    name = Column(String, nullable=False)
    manufacturer = Column(String)
    strength = Column(String)
    form = Column(String)
    hsn = Column(String)
    gst_percent = Column(Float)
    purchase_price = Column(Float)
    mrp = Column(Float, nullable=False)
    stock = Column(Float, default=0)
    batch_no = Column(String)
    expiry = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


class HospitalService(Base):
    __tablename__ = "hospital_services"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    code = Column(String, nullable=True)
    name = Column(String, nullable=False)
    category = Column(String)
    unit = Column(String)
    price = Column(Float, nullable=False)
    hsn = Column(String)
    gst_percent = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    code = Column(String, nullable=True)
    name = Column(String, nullable=False)
    head = Column(String)
    location = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
