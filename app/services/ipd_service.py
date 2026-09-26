from datetime import datetime
from sqlalchemy import func
from app.models.bed import Bed

from app.models.opd_patient import OpdPatient

from app.models.ipd_admission import (
    IPDAdmission
)
from app.models.ipd_bill_item import IPDBillItem
from app.models.ipd_billing import IPDBill
from app.models.ipd_payment import (
    IPDPayment
)

from app.repositories.hospital_repository import (
    get_hospital_by_id
)

from app.utils.patient_number import (
    generate_uhid
)

# def get_ipd_patients(
#     db,
#     current_user
# ):

#     return (
#         db.query(IPDAdmission)
#         .filter(
#             IPDAdmission.hospital_id == current_user["hospital_id"]
#         )
#         .order_by(IPDAdmission.id.desc())
#         .all()
#     )


def get_ipd_patients(db, current_user):
    admissions = (
        db.query(IPDAdmission)
        .filter(
        IPDAdmission.hospital_id == current_user["hospital_id"],
        IPDAdmission.status != "Deleted",
        )
        .order_by(IPDAdmission.id.desc())
        .all()
    )

    result = []

    for admission in admissions:
        advance_paid = (
            db.query(func.coalesce(func.sum(IPDPayment.amount), 0))
            .filter(
                IPDPayment.admission_id == admission.id,
                IPDPayment.hospital_id == current_user["hospital_id"],
                IPDPayment.payment_type == "Advance"
            )
            .scalar()
            or 0
        )

        admission.advance_paid = float(advance_paid)
        admission.advancePayment = float(advance_paid)
        latest_bill = (
            db.query(IPDBill)
            .filter(
                IPDBill.admission_id == admission.id,
                IPDBill.hospital_id == current_user["hospital_id"]
            )
            .order_by(IPDBill.created_at.desc(), IPDBill.id.desc())
            .first()
        )
        bill_date = None
        if latest_bill and latest_bill.bill_date:
            bill_date = latest_bill.bill_date.isoformat()
        selected_services = []
        if latest_bill:
            bill_items = (
                db.query(IPDBillItem)
                .filter(IPDBillItem.bill_id == latest_bill.id)
                .order_by(IPDBillItem.id.asc())
                .all()
            )

            selected_services = [
                {
                    "id": item.id,
                    "bill_id": latest_bill.id,
                    "name": item.name,
                    "category": item.category,
                    "qty": item.qty,
                    "rate": item.rate,
                    "amount": float(item.amount or 0),
                    "fee": float(item.amount or 0),
                    "discount": float(item.discount or 0),
                    "remarks": item.remarks,
                }
                for item in bill_items
            ]

        due_amount = (
            float(latest_bill.due_amount)
            if latest_bill and latest_bill.due_amount is not None
            else 0.0
        )
        admission.bill_date = bill_date
        admission.billDate = bill_date
        admission.due_amount = due_amount
        admission.due = "No Dues" if due_amount <= 0 else float(due_amount)

        admission.selectedServices = selected_services
        admission.selected_services = selected_services
        admission.selectedServiceIds = [service["id"] for service in selected_services]
        admission.selected_service_ids = [service["id"] for service in selected_services]

        result.append(admission)

    return result

def generate_admission_no(
    db,
    hospital_id
):
    count = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.hospital_id ==
            hospital_id
        )
        .count()
    )

    return f"IPD{hospital_id}{count+1:05d}"

def validate_bed(
    db,
    hospital_id,
    ward,
    room,
    bed_no
):
    bed = (
        db.query(Bed)
        .filter(
            Bed.hospital_id == hospital_id,
            Bed.ward == ward,
            Bed.room == room,
            Bed.bed_no == bed_no
        )
        .first()
    )

    if not bed:
        raise ValueError(
            "Bed not found"
        )

    if bed.status != "Available":
        raise ValueError(
            "Bed already occupied"
        )

    return bed


def admit_new_patient(
    db,
    payload,
    current_user
):

    hospital_id = current_user[
        "hospital_id"
    ]

    hospital = get_hospital_by_id(
        db,
        hospital_id
    )

    patient = OpdPatient(

        hospital_id=hospital_id,

        uhid=generate_uhid(
            db,
            hospital
        ),

        name=payload.name,

        mobile=payload.mobile,

        gender=payload.gender,

        age=payload.age,

        address=payload.address
    )

    db.add(patient)

    db.commit()

    db.refresh(patient)

    return create_ipd_admission(
        db,
        patient.id,
        payload,
        hospital_id,
        "New"
    )


def admit_existing_patient(
    db,
    payload,
    current_user
):

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id ==
            payload.patient_id
        )
        .first()
    )

    if not patient:
        raise ValueError(
            "Patient not found"
        )

    return create_ipd_admission(
        db,
        patient.id,
        payload,
        current_user["hospital_id"],
        "Existing"
    )


def admit_from_opd(
    db,
    payload,
    current_user
):

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id ==
            payload.patient_id
        )
        .first()
    )

    if not patient:
        raise ValueError(
            "Patient not found"
        )

    return create_ipd_admission(
        db,
        patient.id,
        payload,
        current_user["hospital_id"],
        "OPD"
    )

def create_ipd_admission(
    db,
    patient_id,
    payload,
    hospital_id,
    admission_type
):
    print("STEP 1")
    patient = (
    db.query(OpdPatient)
    .filter(OpdPatient.id == patient_id)
    .first()
    )

    print("STEP 2")
    patient_uhid = patient.uhid

    print("STEP 3", patient_uhid)

    bed = None

    if payload.ward and payload.room and payload.bed_no:
        bed = validate_bed(
            db,
            hospital_id,
            payload.ward,
            payload.room,
            payload.bed_no
        )
        print("STEP 5")

    admission = IPDAdmission(
        hospital_id=hospital_id,
        patient_id=patient_id,
        uhid=patient_uhid,
        name=patient.name,
        doctor_id=payload.doctor_id,
        admission_no=generate_admission_no(db, hospital_id),
        ward=payload.ward,
        room=payload.room,
        bed_no=payload.bed_no,
        diagnosis=payload.diagnosis,
        admission_type=admission_type,
        admission_date=payload.admission_date or datetime.now(),
        status="Admitted",
        
        department=payload.department,
        attendant_name=payload.attendant_name,
        emergency_contact=payload.emergency_contact,
        expected_discharge_date=payload.expected_discharge_date,
        notes=payload.notes,
        package_name=payload.package_name,
        reason=payload.reason,
        referral=payload.referral,
        room_category=payload.room_category,
        insurance_policy=payload.insurance_policy,
        insurer=payload.insurer,
        age_days=payload.age_days,
        age_months=payload.age_months,
  
    )

    db.add(admission)
    print("Before commit")

    if bed is not None:
        bed.status = "Occupied"

    db.commit()
    print("After commit")
    print(admission.id)
    db.refresh(admission)

    if payload.advance_amount is not None and payload.advance_amount > 0:
        payment = IPDPayment(
            hospital_id=hospital_id,
            admission_id=admission.id,
            amount=payload.advance_amount,
            payment_type="Advance",
            payment_mode=payload.payment_mode
        )
        db.add(payment)
        db.commit()

    return admission

def discharge_patient(
    db,
    admission_id,
    hospital_id
):

    admission = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.id == admission_id,
            IPDAdmission.hospital_id == hospital_id
        )
        .first()
    )

    if not admission:
        return None

    bed = (
        db.query(Bed)
        .filter(
            Bed.hospital_id == hospital_id,
            Bed.ward == admission.ward,
            Bed.room == admission.room,
            Bed.bed_no == admission.bed_no
        )
        .first()
    )

    if bed:
        bed.status = "Available"

    admission.status = "Discharged"

    admission.discharge_date = datetime.now()

    db.commit()

    db.refresh(admission)

    return admission


def update_ipd_admission(
    db,
    admission_id,
    payload,
    hospital_id,
):
    admission = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.id == admission_id,
            IPDAdmission.hospital_id == hospital_id,
            IPDAdmission.status != "Deleted",
        )
        .first()
    )

    if not admission:
        return None

    data = payload.model_dump(exclude_unset=True)

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == admission.patient_id,
            OpdPatient.hospital_id == hospital_id,
        )
        .first()
    )

    patient_fields = {
        "name",
        "mobile",
        "gender",
        "age",
        "address",
        "dob",
        

    }

    if patient:
        for field in patient_fields:
            if field in data:
                setattr(patient, field, data[field])

    for field in (
       "doctor_id",
        "ward",
        "room",
        "bed_no",
        "diagnosis",
        "admission_date",
        "department",
        "attendant_name",
        "emergency_contact",
        "expected_discharge_date",
        "notes",
        "package_name",
        "reason",
        "referral",
        "room_category",
        "insurance_policy",
        "insurer",
        "age_days",
        "age_months",
        "status",
    ):
        if field in data:
            setattr(admission, field, data[field])

    if "name" in data:
        admission.name = data["name"]

    old_bed = None
    new_bed = None

    bed_fields = {"ward", "room", "bed_no"}
    if bed_fields.intersection(data):
        target_ward = data.get("ward", admission.ward)
        target_room = data.get("room", admission.room)
        target_bed_no = data.get("bed_no", admission.bed_no)

        bed_changed = (
            target_ward != admission.ward
            or target_room != admission.room
            or target_bed_no != admission.bed_no
        )

        if bed_changed:
            old_bed = (
                db.query(Bed)
                .filter(
                    Bed.hospital_id == hospital_id,
                    Bed.ward == admission.ward,
                    Bed.room == admission.room,
                    Bed.bed_no == admission.bed_no,
                )
                .first()
            )

            if target_ward and target_room and target_bed_no:
                new_bed = validate_bed(
                    db,
                    hospital_id,
                    target_ward,
                    target_room,
                    target_bed_no,
                )

                new_bed.status = "Occupied"

            if old_bed:
                old_bed.status = "Available"

    db.commit()
    db.refresh(admission)

    return admission


def delete_ipd_admission(
    db,
    admission_id,
    hospital_id,
):
    admission = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.id == admission_id,
            IPDAdmission.hospital_id == hospital_id,
            IPDAdmission.status != "Deleted",
        )
        .first()
    )

    if not admission:
        return None

    bed = (
        db.query(Bed)
        .filter(
            Bed.hospital_id == hospital_id,
            Bed.ward == admission.ward,
            Bed.room == admission.room,
            Bed.bed_no == admission.bed_no,
        )
        .first()
    )

    if bed:
        bed.status = "Available"

    admission.status = "Deleted"
    admission.discharge_date = datetime.now()

    db.commit()
    db.refresh(admission)

    return admission


def get_ipd_patient_by_id(db, admission_id, current_user):
    hospital_id = current_user["hospital_id"]

    admission = (
        db.query(IPDAdmission)
        .filter(
            IPDAdmission.id == admission_id,
            IPDAdmission.hospital_id == hospital_id,
            IPDAdmission.status != "Deleted",
        )
        .first()
    )

    if not admission:
        return None

    patient = (
        db.query(OpdPatient)
        .filter(
            OpdPatient.id == admission.patient_id,
            OpdPatient.hospital_id == hospital_id,
        )
        .first()
    )

    advance_paid = (
        db.query(func.coalesce(func.sum(IPDPayment.amount), 0))
        .filter(
            IPDPayment.admission_id == admission.id,
            IPDPayment.hospital_id == hospital_id,
            IPDPayment.payment_type == "Advance",
        )
        .scalar()
        or 0
    )

    latest_bill = (
        db.query(IPDBill)
        .filter(
            IPDBill.admission_id == admission.id,
            IPDBill.hospital_id == hospital_id,
        )
        .order_by(IPDBill.created_at.desc(), IPDBill.id.desc())
        .first()
    )

    selected_services = []

    if latest_bill:
        bill_items = (
            db.query(IPDBillItem)
            .filter(IPDBillItem.bill_id == latest_bill.id)
            .order_by(IPDBillItem.id.asc())
            .all()
        )

        selected_services = [
            {
                "id": item.id,
                "bill_id": latest_bill.id,
                "name": item.name,
                "category": item.category,
                "qty": item.qty,
                "rate": item.rate,
                "amount": float(item.amount or 0),
                "fee": float(item.rate or 0),
                "discount": float(item.discount or 0),
                "remarks": item.remarks,
            }
            for item in bill_items
        ]

    return {
        "id": admission.id,
        "admission_id": admission.id,
        "patient_id": admission.patient_id,
        "uhid": admission.uhid,
        "admission_no": admission.admission_no,
        "name": patient.name if patient else admission.name,
        "mobile": patient.mobile if patient else None,
        "gender": patient.gender if patient else None,
        "age": patient.age if patient else None,
        "dob": patient.dob if patient else None,
        "address": patient.address if patient else None,
        "doctor_id": admission.doctor_id,
        "ward": admission.ward,
        "room": admission.room,
        "bed_no": admission.bed_no,
        "diagnosis": admission.diagnosis,
        "admission_type": admission.admission_type,
        "status": admission.status,
        "admission_date": admission.admission_date,
        "discharge_date": admission.discharge_date,
        "department": admission.department,
        "attendant_name": admission.attendant_name,
        "emergency_contact": admission.emergency_contact,
        "expected_discharge_date": admission.expected_discharge_date,
        "insurance_policy": admission.insurance_policy,
        "insurer": admission.insurer,
        "notes": admission.notes,
        "package_name": admission.package_name,
        "reason": admission.reason,
        "referral": admission.referral,
        "room_category": admission.room_category,
        "age_days": admission.age_days or 0,
        "age_months": admission.age_months or 0,
        "department": admission.department,
        "attendant_name": admission.attendant_name,
        "room_category": admission.room_category,
        "advance_paid": float(advance_paid),
        "advancePayment": float(advance_paid),
        "bill_date": (
            latest_bill.bill_date.isoformat()
            if latest_bill and latest_bill.bill_date
            else None
        ),
        "due_amount": (
            float(latest_bill.due_amount or 0)
            if latest_bill
            else 0
        ),
        "selected_services": selected_services,
        "selectedServiceIds": [
            service["id"] for service in selected_services
        ],
    }