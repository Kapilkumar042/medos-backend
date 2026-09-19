from datetime import date

from pydantic import BaseModel


class RadiologyCreate(BaseModel):
    code: str | None = None
    name: str
    modality: str | None = None
    body_part: str | None = None
    report_time: str | None = None
    price: float


class RadiologyUpdate(RadiologyCreate):
    pass


class MedicineCreate(BaseModel):
    code: str | None = None
    name: str
    manufacturer: str | None = None
    strength: str | None = None
    form: str | None = None
    hsn: str | None = None
    gst_percent: float | None = None
    purchase_price: float | None = None
    mrp: float
    stock: float | None = 0
    batch_no: str | None = None
    expiry: date | None = None


class MedicineUpdate(MedicineCreate):
    pass


class HospitalServiceCreate(BaseModel):
    code: str | None = None
    name: str
    category: str | None = None
    unit: str | None = None
    price: float
    hsn: str | None = None
    gst_percent: float | None = None


class HospitalServiceUpdate(HospitalServiceCreate):
    pass


class DepartmentCreate(BaseModel):
    code: str | None = None
    name: str
    head: str | None = None
    location: str | None = None
    phone: str | None = None


class DepartmentUpdate(DepartmentCreate):
    pass
