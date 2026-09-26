from fastapi import FastAPI, Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse

from app.db.session import engine

from app.models.user import User
from app.models.hospital import Hospital
from app.models.doctor_profile import DoctorProfile
from app.models.appointment import Appointment
from app.models.lab_test import LabTest
from app.models.opd_patient import OpdPatient
from app.models.opd_visit import OpdVisit
from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem
from app.models.opd_queue import OpdQueue

from app.models.catalog import (
    RadiologyTest,
    Medicine,
    HospitalService,
    Department,
)


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

class AdminAuth(AuthenticationBackend):

    async def login(
        self,
        request: Request
    ) -> bool:

        form = await request.form()

        username = form.get("username")
        password = form.get("password")

        # LOCAL DEVELOPMENT LOGIN
        if (
            username == "admin"
            and password == "admin123"
        ):
            request.session.update({
                "admin_authenticated": True
            })

            return True

        return False

    async def logout(
        self,
        request: Request
    ) -> bool:

        request.session.clear()

        return True

    async def authenticate(
        self,
        request: Request
    ) -> bool:

        return request.session.get(
            "admin_authenticated",
            False
        )


authentication_backend = AdminAuth(
    secret_key="medos-admin-secret-key"
)


# ============================================================
# USER
# ============================================================

class UserAdmin(ModelView, model=User):

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"

    column_list = [
        User.id,
        User.full_name,
        User.email,
        User.phone,
        User.role,
        User.is_active,
        User.hospital_id,
    ]

    column_searchable_list = [
        User.full_name,
        User.email,
        User.phone,
    ]

    column_sortable_list = [
        User.id,
        User.full_name,
        User.email,
        User.role,
    ]

    column_default_sort = [
        (User.id, True)
    ]

    form_excluded_columns = [
        User.password,
    ]


# ============================================================
# HOSPITAL
# ============================================================

class HospitalAdmin(ModelView, model=Hospital):

    name = "Hospital"
    name_plural = "Hospitals"
    icon = "fa-solid fa-hospital"

    column_list = [
        Hospital.id,
        Hospital.hospital_name,
        Hospital.email,
        Hospital.phone,
        Hospital.hospital_code,
        Hospital.is_active,
    ]

    column_searchable_list = [
        Hospital.hospital_name,
        Hospital.email,
        Hospital.phone,
        Hospital.hospital_code,
    ]

    column_sortable_list = [
        Hospital.id,
        Hospital.hospital_name,
        Hospital.email,
    ]

    column_default_sort = [
        (Hospital.id, True)
    ]

    form_excluded_columns = [
        Hospital.password,
    ]


# ============================================================
# DOCTOR
# ============================================================

class DoctorAdmin(ModelView, model=DoctorProfile):

    name = "Doctor"
    name_plural = "Doctors"
    icon = "fa-solid fa-user-doctor"

    column_list = [
        DoctorProfile.id,
        DoctorProfile.doctor_code,
        DoctorProfile.first_name,
        DoctorProfile.last_name,
        DoctorProfile.specialization,
        DoctorProfile.qualification,
        DoctorProfile.phone,
        DoctorProfile.department,
        DoctorProfile.status,
        DoctorProfile.hospital_id,
    ]

    column_searchable_list = [
        DoctorProfile.doctor_code,
        DoctorProfile.first_name,
        DoctorProfile.last_name,
        DoctorProfile.email,
        DoctorProfile.phone,
        DoctorProfile.specialization,
    ]

    column_sortable_list = [
        DoctorProfile.id,
        DoctorProfile.first_name,
        DoctorProfile.specialization,
        DoctorProfile.status,
    ]

    column_default_sort = [
        (DoctorProfile.id, True)
    ]


# ============================================================
# APPOINTMENT
# ============================================================

class AppointmentAdmin(ModelView, model=Appointment):

    name = "Appointment"
    name_plural = "Appointments"
    icon = "fa-solid fa-calendar-check"

    column_list = [
        Appointment.id,
        Appointment.token,
        Appointment.patient_name,
        Appointment.phone,
        Appointment.doctor_id,
        Appointment.department,
        Appointment.appointment_date,
        Appointment.appointment_time,
        Appointment.visit_type,
        Appointment.status,
        Appointment.hospital_id,
    ]

    column_searchable_list = [
        Appointment.patient_name,
        Appointment.phone,
        Appointment.department,
        Appointment.status,
    ]

    column_sortable_list = [
        Appointment.id,
        Appointment.appointment_date,
        Appointment.status,
    ]

    column_default_sort = [
        (Appointment.id, True)
    ]


# ============================================================
# LAB TEST
# ============================================================

class LabTestAdmin(ModelView, model=LabTest):

    name = "Lab Test"
    name_plural = "Lab Tests"
    icon = "fa-solid fa-flask"

    column_list = [
        LabTest.id,
        LabTest.code,
        LabTest.test_name,
        LabTest.category,
        LabTest.price,
        LabTest.sample_type,
        LabTest.report_time,
        LabTest.status,
        LabTest.hospital_id,
    ]

    column_searchable_list = [
        LabTest.code,
        LabTest.test_name,
        LabTest.category,
    ]

    column_sortable_list = [
        LabTest.id,
        LabTest.test_name,
        LabTest.price,
        LabTest.status,
    ]


# ============================================================
# OPD PATIENT
# ============================================================

class OpdPatientAdmin(ModelView, model=OpdPatient):

    name = "OPD Patient"
    name_plural = "OPD Patients"
    icon = "fa-solid fa-hospital-user"

    column_list = [
        OpdPatient.id,
        OpdPatient.uhid,
        OpdPatient.opd_no,
        OpdPatient.name,
        OpdPatient.gender,
        OpdPatient.age,
        OpdPatient.mobile,
        OpdPatient.patient_type,
        OpdPatient.hospital_id,
        OpdPatient.created_at,
    ]

    column_searchable_list = [
        OpdPatient.uhid,
        OpdPatient.opd_no,
        OpdPatient.name,
        OpdPatient.mobile,
    ]

    column_sortable_list = [
        OpdPatient.id,
        OpdPatient.name,
        OpdPatient.created_at,
    ]

    column_default_sort = [
        (OpdPatient.id, True)
    ]


# ============================================================
# OPD VISIT
# ============================================================

class OpdVisitAdmin(ModelView, model=OpdVisit):

    name = "OPD Visit"
    name_plural = "OPD Visits"
    icon = "fa-solid fa-stethoscope"

    column_list = [
        OpdVisit.id,
        OpdVisit.patient_id,
        OpdVisit.doctor_id,
        OpdVisit.department,
        OpdVisit.visit_date,
        OpdVisit.hospital_id,
    ]

    column_sortable_list = [
        OpdVisit.id,
        OpdVisit.visit_date,
    ]

    column_default_sort = [
        (OpdVisit.id, True)
    ]


# ============================================================
# OPD BILL
# ============================================================

class OpdBillAdmin(ModelView, model=OpdBill):

    name = "OPD Bill"
    name_plural = "OPD Bills"
    icon = "fa-solid fa-file-invoice-dollar"

    column_list = [
        OpdBill.id,
        OpdBill.bill_no,
        OpdBill.patient_id,
        OpdBill.visit_id,
        OpdBill.total_amount,
        OpdBill.total_discount,
        OpdBill.net_amount,
        OpdBill.paid_amount,
        OpdBill.due_amount,
        OpdBill.payment_mode,
        OpdBill.created_at,
        OpdBill.hospital_id,
    ]

    column_searchable_list = [
        OpdBill.bill_no,
        OpdBill.payment_mode,
    ]

    column_sortable_list = [
        OpdBill.id,
        OpdBill.bill_no,
        OpdBill.net_amount,
        OpdBill.paid_amount,
        OpdBill.due_amount,
        OpdBill.created_at,
    ]

    column_default_sort = [
        (OpdBill.id, True)
    ]


# ============================================================
# OPD BILL ITEM
# ============================================================

class OpdBillItemAdmin(ModelView, model=OpdBillItem):

    name = "Bill Item"
    name_plural = "Bill Items"
    icon = "fa-solid fa-list"

    column_list = [
        OpdBillItem.id,
        OpdBillItem.bill_id,
        OpdBillItem.category,
        OpdBillItem.name,
        OpdBillItem.code,
        OpdBillItem.qty,
        OpdBillItem.amount,
        OpdBillItem.discount,
        OpdBillItem.remarks,
    ]

    column_searchable_list = [
        OpdBillItem.name,
        OpdBillItem.code,
        OpdBillItem.category,
    ]

    column_sortable_list = [
        OpdBillItem.id,
        OpdBillItem.amount,
        OpdBillItem.qty,
    ]


# ============================================================
# OPD QUEUE
# ============================================================

class OpdQueueAdmin(ModelView, model=OpdQueue):

    name = "OPD Queue"
    name_plural = "OPD Queue"
    icon = "fa-solid fa-list-ol"

    column_list = [
        OpdQueue.id,
        OpdQueue.token_no,
        OpdQueue.opd_patient_id,
        OpdQueue.doctor_id,
        OpdQueue.queue_date,
        OpdQueue.status,
        OpdQueue.checkin_time,
        OpdQueue.called_time,
        OpdQueue.completed_time,
        OpdQueue.hospital_id,
    ]

    column_searchable_list = [
        OpdQueue.status,
    ]

    column_sortable_list = [
        OpdQueue.id,
        OpdQueue.token_no,
        OpdQueue.queue_date,
        OpdQueue.status,
    ]

    column_default_sort = [
        (OpdQueue.id, True)
    ]


# ============================================================
# RADIOLOGY TEST
# ============================================================

class RadiologyTestAdmin(ModelView, model=RadiologyTest):

    name = "Radiology Test"
    name_plural = "Radiology Tests"
    icon = "fa-solid fa-x-ray"

    column_list = [
        RadiologyTest.id,
        RadiologyTest.code,
        RadiologyTest.name,
        RadiologyTest.modality,
        RadiologyTest.body_part,
        RadiologyTest.report_time,
        RadiologyTest.price,
        RadiologyTest.hospital_id,
    ]

    column_searchable_list = [
        RadiologyTest.code,
        RadiologyTest.name,
        RadiologyTest.modality,
    ]


# ============================================================
# MEDICINE
# ============================================================

class MedicineAdmin(ModelView, model=Medicine):

    name = "Medicine"
    name_plural = "Medicines"
    icon = "fa-solid fa-pills"

    column_list = [
        Medicine.id,
        Medicine.code,
        Medicine.name,
        Medicine.manufacturer,
        Medicine.strength,
        Medicine.form,
        Medicine.mrp,
        Medicine.stock,
        Medicine.batch_no,
        Medicine.expiry,
        Medicine.hospital_id,
    ]

    column_searchable_list = [
        Medicine.code,
        Medicine.name,
        Medicine.manufacturer,
        Medicine.batch_no,
    ]

    column_sortable_list = [
        Medicine.id,
        Medicine.name,
        Medicine.mrp,
        Medicine.stock,
        Medicine.expiry,
    ]

    column_default_sort = [
        (Medicine.id, True)
    ]


# ============================================================
# HOSPITAL SERVICE
# ============================================================

class HospitalServiceAdmin(ModelView, model=HospitalService):

    name = "Hospital Service"
    name_plural = "Hospital Services"
    icon = "fa-solid fa-hand-holding-medical"

    column_list = [
        HospitalService.id,
        HospitalService.code,
        HospitalService.name,
        HospitalService.category,
        HospitalService.unit,
        HospitalService.price,
        HospitalService.hsn,
        HospitalService.gst_percent,
        HospitalService.hospital_id,
    ]

    column_searchable_list = [
        HospitalService.code,
        HospitalService.name,
        HospitalService.category,
    ]

    column_sortable_list = [
        HospitalService.id,
        HospitalService.name,
        HospitalService.price,
    ]


# ============================================================
# DEPARTMENT
# ============================================================

class DepartmentAdmin(ModelView, model=Department):

    name = "Department"
    name_plural = "Departments"
    icon = "fa-solid fa-building"

    column_list = [
        Department.id,
        Department.code,
        Department.name,
        Department.head,
        Department.location,
        Department.phone,
        Department.hospital_id,
    ]

    column_searchable_list = [
        Department.code,
        Department.name,
        Department.head,
        Department.location,
    ]

    column_sortable_list = [
        Department.id,
        Department.name,
    ]


# ============================================================
# SETUP ADMIN
# ============================================================

def setup_admin(app: FastAPI):

    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        title="Ncuresoft Admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(HospitalAdmin)
    admin.add_view(DoctorAdmin)
    admin.add_view(AppointmentAdmin)
    admin.add_view(LabTestAdmin)
    admin.add_view(OpdPatientAdmin)
    admin.add_view(OpdVisitAdmin)
    admin.add_view(OpdBillAdmin)
    admin.add_view(OpdBillItemAdmin)
    admin.add_view(OpdQueueAdmin)
    admin.add_view(RadiologyTestAdmin)
    admin.add_view(MedicineAdmin)
    admin.add_view(HospitalServiceAdmin)
    admin.add_view(DepartmentAdmin)

    return admin