from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_service import generate_ai_remarks
from config import AI_PROVIDER
from database import create_patient, init_db
from validators import validate_patient_record


def load_fixture() -> list[dict]:
    fixture_path = Path(__file__).resolve().parents[1] / "data" / "employer_test_data.json"
    with fixture_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    init_db()
    rows = load_fixture()
    valid_rows = []
    invalid_rows = []
    seen_values = set()

    for index, row in enumerate(rows, start=1):
        record = {
            "full_name": row["full_name"],
            "dob": row["dob"],
            "email": row["email"],
            "glucose": row["glucose"],
            "haemoglobin": row["haemoglobin"],
            "cholesterol": row["cholesterol"],
        }
        errors = validate_patient_record(record)
        if errors:
            invalid_rows.append({"row_number": index, "original": row, "errors": errors})
            print(f"Row {index}: INVALID -> {errors}")
            continue

        try:
            remarks = generate_ai_remarks(record)
            created = create_patient({**record, "remarks": remarks})
            valid_rows.append({"row_number": index, "created_id": created["id"], "original": row})
            seen_values.add((row["full_name"].casefold(), row["dob"], row["email"].casefold(), str(row["glucose"]), str(row["haemoglobin"]), str(row["cholesterol"])))
            print(f"Row {index}: VALID -> inserted as patient id {created['id']}")
        except Exception as exc:
            invalid_rows.append({"row_number": index, "original": row, "errors": {"database": str(exc)}})
            print(f"Row {index}: DB INSERT FAILED -> {exc}")

    print(f"Summary: {len(valid_rows)} valid rows inserted; {len(invalid_rows)} invalid rows reported.")

    if invalid_rows:
        print("Invalid rows: ")
        for item in invalid_rows:
            print(item)


if __name__ == "__main__":
    main()
