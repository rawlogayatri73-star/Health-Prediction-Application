# Interview Preparation — HealthTrack

## Application architecture

The project is intentionally structured into small modules so each responsibility is easy to explain:

- `app.py`: Streamlit interface and user flows
- `validators.py`: reusable validation logic
- `database.py`: SQLite database connection and CRUD operations
- `ai_service.py`: AI request creation and safe response handling
- `config.py`: environment configuration and database path logic

This separation keeps the project beginner-friendly while still showing professional engineering habits.

## End-to-end flow

When a user submits a form:

1. The input values are collected by Streamlit.
2. `validate_patient_record()` checks the full name, email, date of birth, and blood values.
3. If validation fails, the form stops and the user sees specific field-level errors.
4. If validation passes, the app calls the AI service to generate a cautious remark.
5. The patient record and the remark are saved in SQLite.
6. The list refreshes and the patient can be searched or viewed.

## SQLite persistence

The application uses SQLite through Python's standard `sqlite3` library.

- The database file is created automatically at runtime.
- The `patients` table stores patient demographics, measurement values, remarks, and timestamps.
- Parameterized queries are used to avoid SQL injection risks.
- Records are searched using a name/email filter and then retrieved by ID.

## CRUD operations

### Create

The app validates the form first, then inserts the patient only if the record passes validation. This avoids saving invalid data.

### Read

The `list_patients()` function fetches the records and supports search by name or email. `get_patient_by_id()` retrieves one selected patient record for details.

### Update

An existing record is selected, preloaded into the form, edited, and then revalidated before saving. Numeric value changes trigger a new AI remark if needed.

### Delete

The delete action requires user confirmation before removing the record.

## API handling

The AI service uses a real documented API interface if a valid key is available. It:

- Reads the API configuration from environment variables
- Builds a cautious prompt
- Sends a request with a timeout
- Validates the response
- Surfaces clear error messages if the API is unavailable
- Keeps the app usable even when the API is missing

If the configuration is missing or the provider is unavailable, the app shows a clear warning and does not misrepresent the result as a real AI assessment.

## Important functions and modules

- `validate_full_name()`: checks empty and whitespace-only names
- `validate_email()`: verifies email format and domain structure
- `validate_date_of_birth()`: handles DD/MM/YYYY and DD.MM.YYYY, rejects future dates
- `validate_numeric_measurement()`: checks numeric and finite values
- `create_patient()`: validates and saves a patient record
- `update_patient()`: updates an existing record safely
- `delete_patient()`: deletes by ID
- `generate_ai_remarks()`: calls the configured AI service or enters mock mode

## Likely interview questions and answers

1. What problem does the project solve?
   - It helps store patient records and provide cautious informational insights in a clean dashboard.

2. Why use SQLite?
   - It is lightweight, built into Python, and perfectly suitable for local demonstration and testing.

3. How do you avoid SQL injection?
   - By using parameterized queries with placeholders instead of string concatenation.

4. Why are validation checks important?
   - They prevent invalid dates, malformed emails, and bad measurements from being inserted.

5. What happens if the AI key is missing?
   - The app keeps working in mock mode and shows that no live AI result was generated.

6. What is the purpose of the `.env` file?
   - To store environment variables like the API key without committing secrets to source control.

7. Why are tests important here?
   - They confirm validation logic, CRUD operations, and error handling continue to work.

8. What does the app do if a patient record is invalid?
   - It blocks the save and shows clear validation messages next to the relevant fields.

9. How do you handle future dates?
   - The app rejects them clearly because a date of birth cannot be in the future.

10. Why keep AI remarks separate from database logic?
   - It makes the project easier to maintain and test.

11. What is a mock mode and why is it useful?
   - It allows automated tests and local development without real API access.

12. How is duplicate detection handled?
   - The application checks full name + email + DOB as a unique pattern before inserting a record.

13. How do you ensure old records are not silently changed?
   - The app validates the incoming values explicitly and does not guess a corrected date or value.

14. Why is the AI prompt designed to be cautious?
   - Because health data should never be treated as diagnosis without proper clinical context.

15. Why is the disclaimer important?
   - It sets clear expectations and protects the app from being misrepresented as medical advice.

16. How do you defend the use of a non-diagnostic remark?
   - The app explains that interpretation depends on units, fasting status, age, and medical history and recommends professional assessment.

17. What is the difference between validation and AI interpretation?
   - Validation ensures the data is acceptable; AI interpretation is only a cautious informational remark, not a diagnosis.

18. How would you explain the invalid employer records?
   - Each invalid row is intentionally included to demonstrate a specific validation rule.

## Explaining the supplied invalid records

- Row 2: `hunter@gmail` is invalid because the email is missing a valid domain suffix.
- Row 4: `31.11.2001` is invalid because November has only 30 days.
- Row 8: `Kris.wu.gmail.com` is invalid because it is missing the `@` symbol and therefore is not a valid email.
- The future-date row uses a DOB beyond today and is rejected.
- Duplicate rows are retained for audit but are not automatically dropped from the original dataset.

## Demonstration ideas for a 5–10 minute interview

1. Start by explaining the app purpose and architecture.
2. Show the registration form and describe each validation rule.
3. Demonstrate the employer validation helper.
4. Show a valid record being created and saved.
5. Search for a patient and open the details panel.
6. Update an email and save the change.
7. Delete a record and show the list refresh.
8. Explain the AI service and fallback behavior.
9. Close with a short explanation of why this is safe and beginner-friendly.

## Final interview message

The project is designed to show that you understand how to build a small but complete data-driven application: validation, persistence, user interaction, error handling, tests, and safe AI integration.
