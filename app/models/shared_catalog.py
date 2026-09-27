from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy import JSON

from app.db.base import Base


class CatalogTemplate(Base):
    """Legacy mixed catalog table retained as a migration source."""

    __tablename__ = "catalog_templates"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(30), nullable=False, index=True)
    code = Column(String(100), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    sample_type = Column(String(255), nullable=True)
    price = Column(Float, nullable=True)
    description = Column(String(1000), nullable=True)
    category = Column(String(255), nullable=True)
    modality = Column(String(100), nullable=True)
    body_part = Column(String(255), nullable=True)
    report_time = Column(String(100), nullable=True)
    unit = Column(String(100), nullable=True)
    dosage_type = Column(String(255), nullable=True)
    pack_size = Column(String(100), nullable=True)
    stock = Column(Float, nullable=True)
    purchase_rate = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    mrp = Column(Float, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class _CatalogTemplateFields:
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    sample_type = Column(String(255), nullable=True)
    price = Column(Float, nullable=True)
    description = Column(String(1000), nullable=True)
    category = Column(String(255), nullable=True)
    modality = Column(String(100), nullable=True)
    body_part = Column(String(255), nullable=True)
    report_time = Column(String(100), nullable=True)
    unit = Column(String(100), nullable=True)
    dosage_type = Column(String(255), nullable=True)
    pack_size = Column(String(100), nullable=True)
    stock = Column(Float, nullable=True)
    purchase_rate = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    mrp = Column(Float, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LabCatalogTemplate(_CatalogTemplateFields, Base):
    __tablename__ = "global_lab_tests"


class RadiologyCatalogTemplate(_CatalogTemplateFields, Base):
    __tablename__ = "global_radiology_tests"


class ServiceCatalogTemplate(_CatalogTemplateFields, Base):
    __tablename__ = "global_hospital_services"


class MedicineCatalogTemplate(_CatalogTemplateFields, Base):
    __tablename__ = "global_medicines"


class HospitalCatalogOverride(Base):
    __tablename__ = "hospital_catalog_overrides"
    __table_args__ = (
        UniqueConstraint("hospital_id", "kind", "template_id", name="uq_hospital_catalog_template"),
    )

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    template_id = Column(Integer, nullable=True, index=True)
    kind = Column(String(30), nullable=False, index=True)
    overridden_fields = Column(JSON, nullable=False, default=list)
    code = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    sample_type = Column(String(255), nullable=True)
    price = Column(Float, nullable=True)
    description = Column(String(1000), nullable=True)
    category = Column(String(255), nullable=True)
    modality = Column(String(100), nullable=True)
    body_part = Column(String(255), nullable=True)
    report_time = Column(String(100), nullable=True)
    unit = Column(String(100), nullable=True)
    dosage_type = Column(String(255), nullable=True)
    pack_size = Column(String(100), nullable=True)
    stock = Column(Float, nullable=True)
    purchase_rate = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    mrp = Column(Float, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


