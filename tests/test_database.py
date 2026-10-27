from __future__ import annotations

import config
import pytest
from database import (
    create_patient,
    delete_patient,
    get_patient_by_id,
    init_db,
    is_duplicate_submission,
    list_patients,
    update_patient,
)


def test_database_crud_round_trip(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "test_health.db"
    monkeypatch.setattr(config, "APP_DATABASE_PATH", str(database_path))
    init_db()

    patient = create_patient(
        {
            "full_name": "Mia Patel",
            "dob": "12/09/1998",
            "email": "mia@example.com",
            "glucose": "95",
            "haemoglobin": "12.5",
            "cholesterol": "200",
            "remarks": "Test remarks",
        }
    )
    assert patient["email"] == "mia@example.com"
    assert len(list_patients()) == 1

    saved = get_patient_by_id(patient["id"])
    assert saved is not None
    assert saved["full_name"] == "Mia Patel"

    updated = update_patient(
        patient["id"],
        {
            "full_name": "Mia Patel",
            "dob": "12/09/1998",
            "email": "gokul@infocare.com",
            "glucose": "96",
            "haemoglobin": "12.6",
            "cholesterol": "210",
            "remarks": "Updated remarks",
        },
    )
    assert updated["email"] == "gokul@infocare.com"

    delete_patient(patient["id"])
    assert get_patient_by_id(patient["id"]) is None


def test_duplicate_submission_detected() -> None:
    payload = {
        "full_name": "Jane Doe",
        "dob": "12.09.1998",
        "email": "jane@example.com",
        "glucose": "95",
        "haemoglobin": "12.5",
        "cholesterol": "200",
    }
    seen = set()
    assert is_duplicate_submission(payload, seen) is False
    seen.add(("jane doe", "12.09.1998", "jane@example.com", "95", "12.5", "200"))
    assert is_duplicate_submission(payload, seen) is True


def test_create_patient_rejects_duplicate_with_case_or_date_format_difference(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "test_health.db"
    monkeypatch.setattr(config, "APP_DATABASE_PATH", str(database_path))
    init_db()
    patient = {
        "full_name": "Jane Doe",
        "dob": "12.09.1998",
        "email": "jane@example.com",
        "glucose": "95",
        "haemoglobin": "12.5",
        "cholesterol": "200",
    }
    create_patient(patient)

    duplicate = {**patient, "full_name": "jane doe", "dob": "12/09/1998", "email": "JANE@example.com"}
    with pytest.raises(ValueError, match="already exist"):
        create_patient(duplicate)


def test_create_patient_rejects_unicode_casefold_name_duplicate(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "test_health.db"
    monkeypatch.setattr(config, "APP_DATABASE_PATH", str(database_path))
    init_db()
    patient = {
        "full_name": "Straße",
        "dob": "12.09.1998",
        "email": "jane@example.com",
        "glucose": "95",
        "haemoglobin": "12.5",
        "cholesterol": "200",
    }
    create_patient(patient)

    duplicate = {**patient, "full_name": "STRASSE"}
    with pytest.raises(ValueError, match="already exist"):
        create_patient(duplicate)


def test_update_patient_rejects_duplicate_record(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "test_health.db"
    monkeypatch.setattr(config, "APP_DATABASE_PATH", str(database_path))
    init_db()
    first = create_patient({
        "full_name": "Jane Doe",
        "dob": "12/09/1998",
        "email": "jane@example.com",
        "glucose": "95",
        "haemoglobin": "12.5",
        "cholesterol": "200",
    })
    second = create_patient({
        "full_name": "John Doe",
        "dob": "12/09/1998",
        "email": "john@example.com",
        "glucose": "96",
        "haemoglobin": "12.6",
        "cholesterol": "210",
    })

    with pytest.raises(ValueError, match="already exist"):
        update_patient(second["id"], {
            "full_name": first["full_name"],
            "dob": first["dob"],
            "email": first["email"],
            "glucose": "96",
            "haemoglobin": "12.6",
            "cholesterol": "210",
        })


def test_database_creates_parent_directories(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "nested" / "directory" / "health.db"
    monkeypatch.setattr(config, "APP_DATABASE_PATH", str(database_path))

    init_db()

    assert database_path.exists()
