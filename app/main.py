from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.init_db import create_tables

from app.api.users import (
    router as users_router
)
from app.api.doctors import (
    router as doctors_router
)

from app.api.doctors import router as doctor_router

from app.api.auth import router as auth_router
from app.api.opd_patients import router as opd_patient_router
from app.api.opd_visit import router as opd_visit_router
from app.api.opd_bills import (
    router as opd_bill_router
)


app = FastAPI(
    title="MedOS API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

app.include_router(
    doctor_router,
    prefix="/api"
)
app.include_router(
    opd_visit_router
)
app.include_router(
    opd_bill_router
)


@app.get("/")
def home():
    return {
        "message": "I love you Meenu too much"
    }
