from contextlib import closing
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import get_database_path
from validators import calculate_age_from_dob, parse_date_value, validate_patient_record


def connect_db() -> sqlite3.Connection:
    database_path = Path(get_database_path())
    database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(connect_db()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                email TEXT NOT NULL,
                glucose REAL NOT NULL,
                haemoglobin REAL NOT NULL,
                cholesterol REAL NOT NULL,
                remarks TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _patient_record_to_db(payload: dict[str, Any]) -> dict[str, Any]:
    data = {
        "full_name": str(payload.get("full_name", "")).strip(),
        "dob": str(payload.get("dob", "")).strip(),
        "email": str(payload.get("email", "")).strip(),
        "glucose": payload.get("glucose"),
        "haemoglobin": payload.get("haemoglobin"),
        "cholesterol": payload.get("cholesterol"),
        "remarks": str(payload.get("remarks", "")).strip(),
    }
    return data


def create_patient(payload: dict[str, Any]) -> dict[str, Any]:
    record = _patient_record_to_db(payload)
    errors = validate_patient_record(record)
    if errors:
        raise ValueError(f"Validation failed: {errors}")

    with closing(connect_db()) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            """
            SELECT id, full_name, dob FROM patients
            WHERE lower(trim(email)) = lower(?)
            """,
            (record["email"],),
        ).fetchall()
        normalized_dob = parse_date_value(record["dob"])
        if any(
            row["full_name"].strip().casefold() == record["full_name"].casefold()
            and parse_date_value(row["dob"]) == normalized_dob
            for row in existing
        ):
            raise ValueError("This patient appears to already exist in the database.")

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.execute(
            """
            INSERT INTO patients (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["full_name"],
                record["dob"],
                record["email"],
                float(record["glucose"]),
                float(record["haemoglobin"]),
                float(record["cholesterol"]),
                record["remarks"],
                now,
                now,
            ),
        )
        record_id = cursor.lastrowid
        conn.commit()
        created = get_patient_by_id(record_id)
        return created


def list_patients(search_query: str = "") -> list[dict[str, Any]]:
    query = """
        SELECT * FROM patients
        WHERE (? = '' OR full_name LIKE '%' || ? || '%' OR email LIKE '%' || ? || '%')
        ORDER BY created_at DESC
    """
    with closing(connect_db()) as conn, conn:
        rows = conn.execute(query, (search_query, search_query, search_query)).fetchall()
    return [dict(row) for row in rows]


def get_patient_by_id(patient_id: int) -> dict[str, Any] | None:
    with closing(connect_db()) as conn, conn:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    return dict(row) if row is not None else None


def update_patient(patient_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    record = _patient_record_to_db(payload)
    errors = validate_patient_record(record)
    if errors:
        raise ValueError(f"Validation failed: {errors}")

    with closing(connect_db()) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        if existing is None:
            raise ValueError("The selected patient record does not exist.")

        possible_duplicates = conn.execute(
            """
            SELECT id, full_name, dob FROM patients
            WHERE id != ? AND lower(trim(email)) = lower(?)
            """,
            (patient_id, record["email"]),
        ).fetchall()
        normalized_dob = parse_date_value(record["dob"])
        if any(
            row["full_name"].strip().casefold() == record["full_name"].casefold()
            and parse_date_value(row["dob"]) == normalized_dob
            for row in possible_duplicates
        ):
            raise ValueError("This patient appears to already exist in the database.")

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            UPDATE patients
            SET full_name = ?, dob = ?, email = ?, glucose = ?, haemoglobin = ?, cholesterol = ?, remarks = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                record["full_name"],
                record["dob"],
                record["email"],
                float(record["glucose"]),
                float(record["haemoglobin"]),
                float(record["cholesterol"]),
                record["remarks"],
                now,
                patient_id,
            ),
        )
        conn.commit()
        updated = get_patient_by_id(patient_id)
        return updated


def delete_patient(patient_id: int) -> None:
    with closing(connect_db()) as conn, conn:
        result = conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,)).rowcount
    if result == 0:
        raise ValueError("Unable to delete the selected patient because the record no longer exists.")


def get_patient_age_label(patient: dict[str, Any]) -> str:
    try:
        return str(calculate_age_from_dob(patient.get("dob", "")))
    except (TypeError, ValueError):
        return "Unknown"


def is_duplicate_submission(payload: dict[str, Any], seen: set[tuple[str, str, str, str, str, str]]) -> bool:
    key = (
        str(payload.get("full_name", "")).strip().casefold(),
        str(payload.get("dob", "")).strip(),
        str(payload.get("email", "")).strip().casefold(),
        str(payload.get("glucose", "")).strip(),
        str(payload.get("haemoglobin", "")).strip(),
        str(payload.get("cholesterol", "")).strip(),
    )
    return key in seen


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
