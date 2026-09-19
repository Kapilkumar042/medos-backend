from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import create_tables

from app.api.users import (
    router as users_router
)
from app.api.doctors import (
    router as doctors_router
)
from fastapi.staticfiles import StaticFiles


from app.api.appointments import router as appointment_router
from app.api.opd_queue import router as opd_queue_router
from app.api.public_appointment import (
    router as public_appointment_router
)
from app.api.catalog import router as catalog_router

# from app.api.doctors import router as doctor_router

from app.api.auth import router as auth_router
from app.api.opd_patients import router as opd_patient_router
from app.api.opd_visit import router as opd_visit_router
from app.api.opd_bills import (
    router as opd_bill_router
)

from app.api.hospital_qr import router as hospital_qr_router


app = FastAPI(
    title="MedOS API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://13.200.215.42"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():

    create_tables()


app.include_router(auth_router)

app.include_router(users_router)
app.include_router(doctors_router)
app.include_router(
    opd_patient_router
)

# app.include_router(
#     doctor_router,
#     prefix="/api"
# )
app.include_router(
    opd_visit_router
)
app.include_router(
    opd_bill_router
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.include_router(
    appointment_router,
    prefix="/api"
)
app.include_router(
    public_appointment_router,

)
app.include_router(
    hospital_qr_router
)
app.include_router(catalog_router)

app.include_router(opd_queue_router)


@app.get("/")
def home():
    return {
        "message": "I love you Meenu too much"
    }
