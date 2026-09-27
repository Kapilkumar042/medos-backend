from io import BytesIO

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import UploadFile

from app.db.base import Base
from app.models.hospital import Hospital
from app.models.lab_test import LabTest
from app.models.opd_bill import OpdBill
from app.models.opd_bill_item import OpdBillItem
from app.models.shared_catalog import (
    LabCatalogTemplate,
    MedicineCatalogTemplate,
    RadiologyCatalogTemplate,
    ServiceCatalogTemplate,
)
from app.services.lab_test_service import create_lab_test
from app.services.lab_test_service import delete_lab_test
from app.services.shared_catalog_service import (
    delete_catalog_for_hospital,
    import_hospital_catalog,
    list_hospital_catalog,
    update_catalog_for_hospital,
    update_hospital_catalog_template,
)
from app.models.catalog import HospitalService, Medicine, RadiologyTest
from app.schemas.catalog import (
    HospitalServiceUpdate,
    MedicineUpdate,
    RadiologyUpdate,
)
from app.schemas.opd_bill import BillItemRequest, CreateBillRequest, UpdateBillRequest
from app.services.opd_bill_service import create_opd_bill, update_opd_bill
from app.models.shared_catalog import HospitalCatalogOverride


def _excel_upload(rows):
    buffer = BytesIO()
    pd.DataFrame(rows).to_excel(buffer, index=False)
    buffer.seek(0)
    return UploadFile(filename="catalog.xlsx", file=buffer)


def test_hospital_catalog_import_only_changes_that_hospital():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        first_hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        second_hospital = Hospital(
            hospital_name="Second", email="second@example.com", phone="222", password="test"
        )
        db.add_all([first_hospital, second_hospital])
        db.flush()
        template = LabCatalogTemplate(
            code="PATH001",
            name="Complete Blood Count (CBC)",
            department="Hematology",
            sample_type="EDTA Blood",
            price=300,
            description="Standard CBC",
        )
        db.add(template)
        db.commit()

        result = import_hospital_catalog(
            db,
            first_hospital.id,
            "lab",
            _excel_upload([{
                "Test Name": "Complete Blood Count (CBC)",
                "Price (INR)": 350,
            }]),
        )

        first_catalog = list_hospital_catalog(db, first_hospital.id, "lab")
        second_catalog = list_hospital_catalog(db, second_hospital.id, "lab")
        assert result["count"] == 1
        assert first_catalog[0]["price"] == 350
        assert second_catalog[0]["price"] == 300
        assert first_catalog[0]["department"] == "Hematology"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_hospital_medicine_import_maps_requested_columns_locally():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        db.add(hospital)
        db.flush()
        template = MedicineCatalogTemplate(
            name="Paracetamol",
            dosage_type="Tablet",
            pack_size="10 tablets",
            stock=10,
            purchase_rate=5,
            unit_price=1,
            mrp=8,
        )
        db.add(template)
        db.commit()

        import_hospital_catalog(
            db,
            hospital.id,
            "medicine",
            _excel_upload([{
                "Medicine Name": "Paracetamol",
                "Dosage/type": "Tablet",
                "Pack Size": "15 tablets",
                "Stock": 20,
                "Purchase Rate": 6,
                "Price/Tablet/PC": 1.2,
                "MRP": 9,
                "Expiry Date": "2028-12-31",
                "Ignored Column": "must not be imported",
            }]),
        )

        hospital_catalog = list_hospital_catalog(db, hospital.id, "medicine")
        assert hospital_catalog[0]["pack_size"] == "15 tablets"
        assert hospital_catalog[0]["purchase_rate"] == 6
        assert hospital_catalog[0]["unit_price"] == 1.2
        assert str(hospital_catalog[0]["expiry_date"]) == "2028-12-31"
        assert hospital_catalog[0]["description"] is None
        assert template.pack_size == "10 tablets"
        assert template.mrp == 8
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_global_changes_flow_through_unoverridden_hospital_fields():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        first_hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        second_hospital = Hospital(
            hospital_name="Second", email="second@example.com", phone="222", password="test"
        )
        db.add_all([first_hospital, second_hospital])
        db.flush()
        template = LabCatalogTemplate(
            code="PATH001", name="CBC", department="Hematology", price=300
        )
        db.add(template)
        db.commit()

        update_hospital_catalog_template(
            db, first_hospital.id, "lab", template.id, {"price": 350}
        )
        template.department = "Pathology"
        db.commit()

        first_catalog = list_hospital_catalog(db, first_hospital.id, "lab")
        second_catalog = list_hospital_catalog(db, second_hospital.id, "lab")
        assert first_catalog[0]["price"] == 350
        assert first_catalog[0]["department"] == "Pathology"
        assert second_catalog[0]["price"] == 300
        assert second_catalog[0]["department"] == "Pathology"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_saving_global_lab_test_creates_local_override_not_duplicate_row():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        first_hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        second_hospital = Hospital(
            hospital_name="Second", email="second@example.com", phone="222", password="test"
        )
        db.add_all([first_hospital, second_hospital])
        db.flush()
        template = LabCatalogTemplate(
            code="PATH001", name="CBC", department="Hematology", price=300
        )
        db.add(template)
        db.commit()

        saved = create_lab_test(
            db,
            type("LabPayload", (), {"model_dump": lambda self: {
                "code": "PATH001",
                "test_name": "CBC",
                "category": "Hematology",
                "price": 400,
                "status": "Active",
            }})(),
            {"hospital_id": first_hospital.id},
        )

        first_catalog = list_hospital_catalog(db, first_hospital.id, "lab")
        second_catalog = list_hospital_catalog(db, second_hospital.id, "lab")
        assert saved["price"] == 400
        assert db.query(LabTest).count() == 0
        assert first_catalog[0]["price"] == 400
        assert second_catalog[0]["price"] == 300
        assert template.price == 300
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_deleting_global_lab_test_hides_it_only_for_that_hospital():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        first_hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        second_hospital = Hospital(
            hospital_name="Second", email="second@example.com", phone="222", password="test"
        )
        db.add_all([first_hospital, second_hospital])
        db.flush()
        template = LabCatalogTemplate(
            code="PATH001", name="CBC", department="Hematology", price=300
        )
        db.add(template)
        db.commit()

        removed = delete_lab_test(db, template.id, first_hospital.id)

        assert removed is not None
        assert list_hospital_catalog(db, first_hospital.id, "lab") == []
        assert list_hospital_catalog(db, second_hospital.id, "lab")[0]["name"] == "CBC"
        assert template.status == "Active"
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_global_radiology_service_medicine_updates_and_deletes_are_local():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        first_hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        second_hospital = Hospital(
            hospital_name="Second", email="second@example.com", phone="222", password="test"
        )
        db.add_all([first_hospital, second_hospital])
        db.flush()
        templates = [
            ("radiology", RadiologyCatalogTemplate(code="RAD1", name="Chest X-Ray", price=500)),
            ("service", ServiceCatalogTemplate(code="SRV1", name="Consultation", price=200)),
            ("medicine", MedicineCatalogTemplate(name="Drug A", mrp=30, purchase_rate=20)),
        ]
        db.add_all([template for _, template in templates])
        db.commit()

        for kind, template in templates:
            payload = {
                "radiology": RadiologyUpdate(code="RAD1", name="Chest X-Ray", price=600),
                "service": HospitalServiceUpdate(code="SRV1", name="Consultation", price=250),
                "medicine": MedicineUpdate(name="Drug A", mrp=35),
            }[kind]
            legacy_model = {
                "radiology": RadiologyTest,
                "service": HospitalService,
                "medicine": Medicine,
            }[kind]
            update_catalog_for_hospital(
                db, legacy_model, kind, template.id, payload, first_hospital.id
            )
            update_catalog_for_hospital(
                db, legacy_model, kind, template.id, payload, first_hospital.id
            )
            assert list_hospital_catalog(db, first_hospital.id, kind)[0]["id"] == template.id
            assert list_hospital_catalog(db, second_hospital.id, kind)[0]["id"] == template.id
            assert delete_catalog_for_hospital(
                db, legacy_model, kind, template.id, first_hospital.id
            ) is not None
            assert list_hospital_catalog(db, first_hospital.id, kind) == []
            assert len(list_hospital_catalog(db, second_hospital.id, kind)) == 1
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_opd_medicine_sale_decrements_only_selling_hospital_stock():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        first_hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        second_hospital = Hospital(
            hospital_name="Second", email="second@example.com", phone="222", password="test"
        )
        db.add_all([first_hospital, second_hospital])
        db.flush()
        from app.models.opd_patient import OpdPatient

        patient = OpdPatient(
            hospital_id=first_hospital.id,
            uhid="UH-1",
            opd_no="OPD-1",
            name="Patient One",
            gender="Other",
            age=30,
            mobile="9999999999",
        )
        db.add(patient)
        medicine = MedicineCatalogTemplate(
            name="Drug A", code="DRUG-A", mrp=25, stock=10
        )
        db.add(medicine)
        db.commit()

        payload = CreateBillRequest(
            patient_id=patient.id,
            total_amount=25,
            total_discount=0,
            net_amount=25,
            paid_amount=25,
            payment_mode="Cash",
            items=[BillItemRequest(
                category="Medicine",
                name="Drug A",
                code="DRUG-A",
                qty=2,
                amount=25,
            )],
        )
        create_opd_bill(db, payload, {"hospital_id": first_hospital.id})

        first_inventory = list_hospital_catalog(db, first_hospital.id, "medicine")
        second_inventory = list_hospital_catalog(db, second_hospital.id, "medicine")
        assert first_inventory[0]["stock"] == 8
        assert second_inventory[0]["stock"] == 10
        assert medicine.stock == 10
        assert db.query(OpdBill).count() == 1
        assert db.query(OpdBillItem).count() == 1

        bill = db.query(OpdBill).one()
        update_opd_bill(
            db,
            bill.id,
            UpdateBillRequest(
                items=[BillItemRequest(
                    category="Medicine",
                    name="Drug A",
                    code="DRUG-A",
                    qty=1,
                    amount=25,
                )],
            ),
            {"hospital_id": first_hospital.id},
        )
        assert list_hospital_catalog(db, first_hospital.id, "medicine")[0]["stock"] == 9
        assert list_hospital_catalog(db, second_hospital.id, "medicine")[0]["stock"] == 10
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_opd_sale_finds_custom_hospital_medicine_by_name():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    try:
        hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        db.add(hospital)
        db.flush()
        from app.models.opd_patient import OpdPatient

        patient = OpdPatient(
            hospital_id=hospital.id,
            uhid="UH-ADAP-1",
            opd_no="OPD-ADAP-1",
            name="Patient One",
        )
        custom_medicine = HospitalCatalogOverride(
            hospital_id=hospital.id,
            kind="medicine",
            template_id=None,
            name="Adapalene",
            code="ADAP-001",
            stock=5,
            status="Active",
        )
        db.add_all([patient, custom_medicine])
        db.commit()

        payload = CreateBillRequest(
            patient_id=patient.id,
            total_amount=12,
            total_discount=0,
            net_amount=12,
            paid_amount=12,
            payment_mode="Cash",
            items=[BillItemRequest(
                category="Medicine",
                name="Adapalene",
                code="ADAP-001",
                qty=1,
                amount=12,
            )],
        )
        create_opd_bill(db, payload, {"hospital_id": hospital.id})

        assert custom_medicine.stock == 4
        assert db.query(OpdBill).count() == 1
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_opd_bill_update_falls_back_to_medicine_name_for_stale_code():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    try:
        hospital = Hospital(
            hospital_name="First", email="first@example.com", phone="111", password="test"
        )
        db.add(hospital)
        db.flush()
        from app.models.opd_patient import OpdPatient

        patient = OpdPatient(
            hospital_id=hospital.id,
            uhid="UH-ALB-1",
            opd_no="OPD-ALB-1",
            name="Patient One",
        )
        inventory = HospitalCatalogOverride(
            hospital_id=hospital.id,
            kind="medicine",
            name="Albendazole",
            code="ALB-NEW",
            stock=8,
            status="Active",
            overridden_fields=["stock"],
        )
        db.add_all([patient, inventory])
        db.commit()

        bill = create_opd_bill(
            db,
            CreateBillRequest(
                patient_id=patient.id,
                total_amount=20,
                total_discount=0,
                net_amount=20,
                paid_amount=20,
                payment_mode="Cash",
                items=[BillItemRequest(
                    category="Medicine", name="Albendazole", code="ALB-OLD", qty=2, amount=20
                )],
            ),
            {"hospital_id": hospital.id},
        )
        assert inventory.stock == 6

        update_opd_bill(
            db,
            bill.id,
            UpdateBillRequest(items=[BillItemRequest(
                category="Medicine", name="Albendazole", code="ALB-NEW", qty=1, amount=10
            )]),
            {"hospital_id": hospital.id},
        )
        assert inventory.stock == 7
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()