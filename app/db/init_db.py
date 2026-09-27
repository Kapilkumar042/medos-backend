from app.db.base import Base
from app.db.session import engine
from sqlalchemy import inspect, text

from app.models.hospital import Hospital
from app.models.user import User
from app.models.doctor_profile import (
    DoctorProfile
)
from app.models.lab_test import LabTest

from app.models.catalog import (
    RadiologyTest,
    Medicine,
    HospitalService,
    Department
)
from app.models.shared_catalog import (
    CatalogTemplate,
    HospitalCatalogOverride,
    LabCatalogTemplate,
    MedicineCatalogTemplate,
    RadiologyCatalogTemplate,
    ServiceCatalogTemplate,
)


def create_tables():
    Base.metadata.create_all(
        bind=engine
    )

    inspector = inspect(engine)
    medicine_columns = {
        "dosage_type": "VARCHAR(255)",
        "pack_size": "VARCHAR(100)",
        "stock": "FLOAT",
        "purchase_rate": "FLOAT",
        "unit_price": "FLOAT",
        "mrp": "FLOAT",
        "expiry_date": "DATE",
    }
    with engine.begin() as connection:
        for table_name in (
            "catalog_templates",
            "hospital_catalog_overrides",
            "global_lab_tests",
            "global_radiology_tests",
            "global_hospital_services",
            "global_medicines",
        ):
            existing_columns = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            for column_name, column_type in medicine_columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    ))

        override_columns = {
            column["name"]
            for column in inspector.get_columns("hospital_catalog_overrides")
        }
        if "overridden_fields" not in override_columns:
            connection.execute(text(
                "ALTER TABLE hospital_catalog_overrides "
                "ADD COLUMN overridden_fields JSON"
            ))

        if engine.dialect.name == "postgresql":
            inspector = inspect(connection)
            foreign_keys = inspector.get_foreign_keys("hospital_catalog_overrides")
            for foreign_key in foreign_keys:
                if (
                    foreign_key.get("referred_table") == "catalog_templates"
                    and foreign_key.get("constrained_columns") == ["template_id"]
                    and foreign_key.get("name")
                ):
                    constraint_name = foreign_key["name"].replace('"', '""')
                    connection.execute(text(
                        "ALTER TABLE hospital_catalog_overrides "
                        f'DROP CONSTRAINT "{constraint_name}"'
                    ))

            unique_constraints = inspector.get_unique_constraints(
                "hospital_catalog_overrides"
            )
            has_scoped_constraint = any(
                constraint.get("column_names") == ["hospital_id", "kind", "template_id"]
                for constraint in unique_constraints
            )
            old_constraints = [
                constraint for constraint in unique_constraints
                if constraint.get("column_names") == ["hospital_id", "template_id"]
                and constraint.get("name")
            ]
            for constraint in old_constraints:
                constraint_name = constraint["name"].replace('"', '""')
                connection.execute(text(
                    "ALTER TABLE hospital_catalog_overrides "
                    f'DROP CONSTRAINT "{constraint_name}"'
                ))

            if not has_scoped_constraint:
                connection.execute(text(
                    "ALTER TABLE hospital_catalog_overrides "
                    "ADD CONSTRAINT uq_hospital_catalog_template "
                    "UNIQUE (hospital_id, kind, template_id)"
                ))

    template_models = {
        "lab": LabCatalogTemplate,
        "radiology": RadiologyCatalogTemplate,
        "service": ServiceCatalogTemplate,
        "medicine": MedicineCatalogTemplate,
    }
    with engine.begin() as connection:
        legacy_rows = connection.execute(text(
            "SELECT * FROM catalog_templates"
        )).mappings()
        for row in legacy_rows:
            model = template_models.get(row["kind"])
            if model is None:
                continue
            target_columns = {column.name for column in model.__table__.columns}
            values = {key: value for key, value in row.items() if key in target_columns}
            exists = connection.execute(
                model.__table__.select().with_only_columns(model.__table__.c.id).where(
                    model.__table__.c.id == values["id"]
                )
            ).first()
            if exists is None:
                connection.execute(model.__table__.insert(), values)
