from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from ai_service import generate_ai_remarks
from config import get_database_path
from database import create_patient, delete_patient, get_patient_age_label, get_patient_by_id, init_db, list_patients, update_patient
from validators import validate_patient_record

st.set_page_config(page_title="HealthTrack — Patient Health Insights", layout="wide")


@st.cache_data(show_spinner=False)
def load_demo_fixture():
    fixture_path = Path(__file__).resolve().parent / "data" / "employer_test_data.json"
    with open(fixture_path, "r", encoding="utf-8") as file:
        return json.load(file)


def render_header() -> None:
    st.title("HealthTrack — Patient Health Insights")
    st.caption("A professional healthcare dashboard for patient registration, review, and record management.")
    st.warning(
        "Informational risk insights only. This application is not a medical diagnosis and is not a substitute "
        "for professional medical advice."
    )


def render_registration_form() -> None:
    st.subheader("Patient Registration")
    with st.form("patient_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name")
            dob = st.text_input("Date of Birth (DD/MM/YYYY)")
            email = st.text_input("Email Address")
        with col2:
            glucose = st.text_input("Glucose")
            haemoglobin = st.text_input("Haemoglobin")
            cholesterol = st.text_input("Cholesterol")

        submitted = st.form_submit_button("Save Patient")

    if not submitted:
        return

    payload = {
        "full_name": full_name,
        "dob": dob,
        "email": email,
        "glucose": glucose,
        "haemoglobin": haemoglobin,
        "cholesterol": cholesterol,
    }

    errors = validate_patient_record(payload)
    if errors:
        st.error("Please fix the following validation issues before saving:")
        for key, message in errors.items():
            st.markdown(f"- **{key.replace('_', ' ').title()}:** {message}")
        return

    try:
        remarks = generate_ai_remarks(payload)
        record = create_patient({**payload, "remarks": remarks})
        st.success(f"Patient saved successfully: {record['full_name']}")
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Unexpected error while saving patient: {exc}")


def render_record_table() -> None:
    st.subheader("Search and Manage Records")
    search_query = st.text_input("Search by patient name or email", key="record_search")
    records = list_patients(search_query)

    if not records:
        st.info("No patient records found.")
        return

    st.dataframe(
        [
            {
                "ID": item["id"],
                "Name": item["full_name"],
                "Age": get_patient_age_label(item),
                "Email": item["email"],
                "Glucose": item["glucose"],
                "Haemoglobin": item["haemoglobin"],
                "Cholesterol": item["cholesterol"],
                "Updated": item["updated_at"],
            }
            for item in records
        ],
        use_container_width=True,
        hide_index=True,
    )

    selected_id = st.selectbox("View or edit a record", [item["id"] for item in records], format_func=lambda value: next(item["full_name"] for item in records if item["id"] == value))
    patient = get_patient_by_id(selected_id)
    if patient is None:
        st.warning("The selected patient could not be found.")
        return

    st.subheader("Patient Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Name:** {patient['full_name']}")
        st.write(f"**Date of Birth:** {patient['dob']}")
        st.write(f"**Age:** {get_patient_age_label(patient)}")
    with col2:
        st.write(f"**Email:** {patient['email']}")
        st.write(f"**Glucose:** {patient['glucose']}")
        st.write(f"**Haemoglobin:** {patient['haemoglobin']}")
    with col3:
        st.write(f"**Cholesterol:** {patient['cholesterol']}")
        st.write(f"**Remarks:** {patient['remarks']}")

    st.subheader("Edit Record")
    edit_form = st.form("edit_patient_form")
    with edit_form:
        edit_name = st.text_input("Full Name", value=patient["full_name"])
        edit_dob = st.text_input("Date of Birth (DD/MM/YYYY)", value=patient["dob"])
        edit_email = st.text_input("Email Address", value=patient["email"])
        edit_glucose = st.text_input("Glucose", value=str(patient["glucose"]))
        edit_haemoglobin = st.text_input("Haemoglobin", value=str(patient["haemoglobin"]))
        edit_cholesterol = st.text_input("Cholesterol", value=str(patient["cholesterol"]))
        update_pressed = st.form_submit_button("Update Patient")

    if update_pressed:
        updated_payload = {
            "full_name": edit_name,
            "dob": edit_dob,
            "email": edit_email,
            "glucose": edit_glucose,
            "haemoglobin": edit_haemoglobin,
            "cholesterol": edit_cholesterol,
        }
        errors = validate_patient_record(updated_payload)
        if errors:
            st.error("Please correct the following validation issues before updating:")
            for key, message in errors.items():
                st.markdown(f"- **{key.replace('_', ' ').title()}:** {message}")
            return

        try:
            updated_remarks = patient["remarks"]
            if (
                str(updated_payload["glucose"]) != str(patient["glucose"])
                or str(updated_payload["haemoglobin"]) != str(patient["haemoglobin"])
                or str(updated_payload["cholesterol"]) != str(patient["cholesterol"])
            ):
                updated_remarks = generate_ai_remarks(updated_payload)
            update_patient(selected_id, {**updated_payload, "remarks": updated_remarks})
            st.success("Patient record updated successfully.")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to update patient: {exc}")

    st.subheader("Delete Record")
    confirm_delete = st.checkbox("I confirm I want to delete this patient record.")
    if st.button("Delete Selected Record"):
        if not confirm_delete:
            st.warning("Please confirm deletion before removing the record.")
        else:
            try:
                delete_patient(selected_id)
                st.success("Patient record deleted successfully.")
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to delete patient: {exc}")


def render_demo_section() -> None:
    st.subheader("Employer Test Data Validation")
    st.write("This helper attempts all supplied records, reports which rows pass or fail validation, and preserves the original values for audit.")

    if st.button("Run Employer Record Validation"):
        fixture = load_demo_fixture()
        valid_rows = []
        invalid_rows = []
        for index, row in enumerate(fixture, start=1):
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
                invalid_rows.append({"row_number": index, "record": row, "errors": errors})
            else:
                valid_rows.append({"row_number": index, "record": row})

        st.success(f"Completed validation: {len(valid_rows)} valid rows and {len(invalid_rows)} invalid rows.")

        if valid_rows:
            st.write("#### Valid rows")
            st.dataframe(valid_rows, use_container_width=True)
        if invalid_rows:
            st.write("#### Invalid rows")
            st.dataframe(invalid_rows, use_container_width=True)


def main() -> None:
    init_db()
    render_header()
    render_registration_form()
    render_record_table()
    render_demo_section()
    st.caption(f"Database location: {get_database_path()}")


if __name__ == "__main__":
    main()
