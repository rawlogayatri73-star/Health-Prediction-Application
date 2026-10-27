from validators import (
    validate_date_of_birth,
    validate_email,
    validate_numeric_measurement,
    validate_patient_record,
)


def test_valid_and_invalid_emails() -> None:
    assert validate_email("robin@example.com") == ""
    assert "Email address is invalid" in validate_email("hunter@gmail")
    assert "Email address is invalid" in validate_email("Kris.wu.gmail.com")


def test_valid_and_invalid_dates() -> None:
    assert validate_date_of_birth("28/01/1960") == ""
    assert validate_date_of_birth("28.01.1960") == ""
    assert "Date of Birth must use DD/MM/YYYY or DD.MM.YYYY format" in validate_date_of_birth("01-01-2000")
    assert "invalid calendar date" in validate_date_of_birth("31.11.2001") or "Date of Birth must use DD/MM/YYYY or DD.MM.YYYY format" in validate_date_of_birth("31.11.2001")


def test_future_date_of_birth() -> None:
    assert "cannot be in the future" in validate_date_of_birth("19.10.2030")


def test_numeric_measurements_and_limits() -> None:
    assert validate_numeric_measurement("94", "Glucose", min_value=0.0, max_value=500.0) == ""
    assert "must be a numeric value" in validate_numeric_measurement("not-a-number", "Glucose", min_value=0.0, max_value=500.0)
    assert "must be a finite numeric value" in validate_numeric_measurement("nan", "Glucose", min_value=0.0, max_value=500.0)
    assert "cannot be less than 0.0" in validate_numeric_measurement("-1", "Glucose", min_value=0.0, max_value=500.0)


def test_complete_patient_record_validation() -> None:
    payload = {
        "full_name": " Jane Doe ",
        "dob": "12/09/1998",
        "email": "jane@example.com",
        "glucose": "95",
        "haemoglobin": "12.5",
        "cholesterol": "200",
    }
    assert validate_patient_record(payload) == {}

    rejected = {
        "full_name": " ",
        "dob": "31.11.2001",
        "email": "wrong",
        "glucose": "-5",
        "haemoglobin": "abc",
        "cholesterol": "inf",
    }
    errors = validate_patient_record(rejected)
    assert errors["full_name"]
    assert errors["email"]
    assert errors["dob"]
    assert errors["glucose"]
    assert errors["haemoglobin"]
    assert errors["cholesterol"]
