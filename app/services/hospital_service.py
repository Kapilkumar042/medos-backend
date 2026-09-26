from app.models.hospital import Hospital
from app.models.user import User
import os
import qrcode
import json
import os
import shutil
import uuid

from fastapi import UploadFile
from app.repositories.hospital_repository import get_hospital_by_id
from app.auth.hash import hash_password
from app.auth.hash import verify_password
from app.auth.jwt import create_access_token
from app.utils.qr_generator import (
    generate_hospital_qr
)


from app.repositories.user_repository import (
    create_user,
    get_user_by_email
)

from app.core.roles import (
    HOSPITAL_ADMIN
)
from app.repositories.hospital_repository import (
    create_hospital,
    get_hospital_by_email,
    get_hospital_by_phone
)


def register_hospital(
    db,
    payload
):

    if get_hospital_by_email(
        db,
        payload.hospital_email
    ):
        raise ValueError(
            "Hospital email already exists"
        )

    if get_hospital_by_phone(
        db,
        payload.phone
    ):
        raise ValueError(
            "Hospital phone already exists"
        )

    existing_user = get_user_by_email(
        db,
        payload.hospital_email
    )

    if existing_user:
        raise ValueError(
            "Admin email already exists"
        )

    hospital = Hospital(
        hospital_name=payload.hospital_name,
        email=payload.hospital_email,
        phone=payload.phone,
        address=payload.address,
        password="TEMP",
        modules=",".join(payload.modules)
    )

    db.add(hospital)

    db.commit()

    db.refresh(hospital)

    admin_user = User(

        hospital_id=hospital.id,

        full_name=payload.hospital_name,

        email=payload.hospital_email,

        phone=payload.phone,

        password=hash_password(
            payload.password
        ),

        role=HOSPITAL_ADMIN
    )

    create_user(
        db,
        admin_user
    )

    return hospital


def login_hospital(
    db,
    payload
):

    user = get_user_by_email(
        db,
        payload.email
    )

    if not user:
        raise ValueError(
            "Invalid email or password"
        )

    valid = verify_password(
        payload.password,
        user.password
    )

    if not valid:
        raise ValueError(
            "Invalid email or password"
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "hospital_id": user.hospital_id,
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",

        "user_id": user.id,

        "hospital_id": user.hospital_id,

        "role": user.role,

        "full_name": user.full_name
    }


def create_hospital_qr(db, hospital_id):
    print("QR REQUEST HOSPITAL ID:", hospital_id)

    hospitals = db.query(Hospital).all()
    print(
        "AVAILABLE HOSPITALS:",
        [(h.id, h.hospital_name) for h in hospitals]
    )

    hospital = (
        db.query(Hospital)
        .filter(Hospital.id == hospital_id)
        .first()
    )
    print("FOUND HOSPITAL:", hospital)
    print("QR HOSPITAL RESULT:", hospital)

    if not hospital:
        return None

    if not hospital.hospital_code:
        hospital.hospital_code = f"HOSP{hospital.id}"

    # Frontend appointment booking page
    qr_url = (
        f"http://13.200.215.42/book-appointment"
        f"?hospital_id={hospital.id}"
    )
    print("GENERATED QR URL:", qr_url)
    os.makedirs(
        "uploads/qr",
        exist_ok=True
    )

    file_name = f"{hospital.id}.png"

    file_path = os.path.join(
        "uploads",
        "qr",
        file_name
    )

    qr = qrcode.make(qr_url)

    qr.save(file_path)

    # Store URL path in DB
    hospital.qr_image = f"/uploads/qr/{file_name}"

    db.commit()
    db.refresh(hospital)

    return {
        "hospital_id": hospital.id,
        "hospital_code": hospital.hospital_code,
        "qr_image": hospital.qr_image,
        "url": qr_url
    }

def get_hospital_profile(db, hospital_id):
    hospital = get_hospital_by_id(db, hospital_id)

    if not hospital:
        return None

    return {
        "id": hospital.id,
        "hospital_name": hospital.hospital_name,
        "email": hospital.email,
        "phone": hospital.phone,
        "address": hospital.address,
        "logo_image": hospital.logo_image,
        "modules": (
            hospital.modules.split(",")
            if hospital.modules
            else []
        ),
        "is_active": hospital.is_active,
        "hospital_code": hospital.hospital_code,
    }


def update_hospital_profile(
    db,
    hospital_id,
    hospital_name=None,
    phone=None,
    address=None,
    modules=None,
    logo: UploadFile | None = None,
):
    hospital = get_hospital_by_id(db, hospital_id)

    if not hospital:
        return None

    if hospital_name is not None:
        hospital.hospital_name = hospital_name

    if phone is not None:
        hospital.phone = phone

    if address is not None:
        hospital.address = address

    if modules is not None:
        try:
            parsed_modules = json.loads(modules)
            if not isinstance(parsed_modules, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            parsed_modules = [
                item.strip()
                for item in modules.split(",")
                if item.strip()
            ]

        hospital.modules = ",".join(parsed_modules)

    if logo and logo.filename:
        os.makedirs("uploads/hospitals", exist_ok=True)

        extension = os.path.splitext(logo.filename)[1].lower()
        filename = f"{hospital.id}-{uuid.uuid4().hex}{extension}"
        file_path = os.path.join("uploads", "hospitals", filename)

        with open(file_path, "wb") as output:
            shutil.copyfileobj(logo.file, output)

        hospital.logo_image = f"/uploads/hospitals/{filename}"

    db.commit()
    db.refresh(hospital)

    return get_hospital_profile(db, hospital_id)