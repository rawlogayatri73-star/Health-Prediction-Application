import math
import re
from datetime import date, datetime
from typing import Any

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}$"
)

BLOOD_VALUE_LIMITS = {
    "glucose": {"min": 0.0, "max": 500.0},
    "haemoglobin": {"min": 0.0, "max": 30.0},
    "cholesterol": {"min": 0.0, "max": 500.0},
}


def validate_full_name(value: Any) -> str:
    if value is None or isinstance(value, bool):
        return "Full Name is required."
    name = str(value).strip()
    if not name:
        return "Full Name is required."
    return ""


def validate_email(value: Any) -> str:
    if value is None:
        return "Email address is required."
    email = str(value).strip()
    if not email:
        return "Email address is required."
    if not EMAIL_PATTERN.fullmatch(email):
        return (
            "Email address is invalid. Please include a valid username and domain, "
            "for example name@example.com."
        )
    return ""


def parse_date_value(value: Any) -> date:
    if value is None:
        raise ValueError("Date of Birth is required.")
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    for fmt in ("%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError("Date of Birth must use DD/MM/YYYY or DD.MM.YYYY format.")


def validate_date_of_birth(value: Any) -> str:
    if value is None or isinstance(value, bool):
        return "Date of Birth is required."
    if isinstance(value, datetime):
        dob = value.date()
    elif isinstance(value, date):
        dob = value
    else:
        raw = str(value).strip()
        if raw == "":
            return "Date of Birth is required."
        for fmt in ("%d/%m/%Y", "%d.%m.%Y"):
            try:
                dob = datetime.strptime(raw, fmt).date()
                break
            except ValueError:
                dob = None
        else:
            return "Date of Birth must use DD/MM/YYYY or DD.MM.YYYY format."
    today = date.today()
    if dob > today:
        return "Date of Birth cannot be in the future."
    return ""


def calculate_age_from_dob(value: Any) -> int:
    dob = parse_date_value(value)
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age


def validate_numeric_measurement(value: Any, field_name: str, *, min_value: float, max_value: float) -> str:
    if value is None or isinstance(value, bool) or str(value).strip() == "":
        return f"{field_name} is required."
    try:
        number = float(value)
    except (TypeError, ValueError):
        return f"{field_name} must be a numeric value."
    if math.isnan(number) or math.isinf(number):
        return f"{field_name} must be a finite numeric value."
    if number < min_value:
        return f"{field_name} cannot be less than {min_value}."
    if number > max_value:
        return f"{field_name} exceeds the configured validation limit of {max_value}."
    return ""


def validate_patient_record(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}

    full_name_error = validate_full_name(data.get("full_name"))
    if full_name_error:
        errors["full_name"] = full_name_error

    email_error = validate_email(data.get("email"))
    if email_error:
        errors["email"] = email_error

    dob_error = validate_date_of_birth(data.get("dob"))
    if dob_error:
        errors["dob"] = dob_error

    for field_name, config in BLOOD_VALUE_LIMITS.items():
        raw_value = data.get(field_name)
        error = validate_numeric_measurement(
            raw_value,
            field_name.replace("_", " ").title(),
            min_value=config["min"],
            max_value=config["max"],
        )
        if error:
            errors[field_name] = error

    return errors


def validate_seed_row(row: dict[str, Any]) -> dict[str, Any]:
    """Validate a test row using the same logic as the app, while preserving the original supplied values."""
    errors = validate_patient_record(row)
    result = {
        "full_name": row.get("full_name"),
        "dob": row.get("dob"),
        "email": row.get("email"),
        "glucose": row.get("glucose"),
        "haemoglobin": row.get("haemoglobin"),
        "cholesterol": row.get("cholesterol"),
        "status": "valid" if not errors else "invalid",
        "errors": errors,
    }
    return result
