# HealthTrack — Patient Health Insights

A beginner-friendly Python + Streamlit application for managing patient records, validating health data, storing records in SQLite, and generating cautious AI-style remarks using a configurable external API or a safe mock mode for testing.

## Overview

This project demonstrates a complete patient-management workflow with:

- A professional registration form
- Validation for names, email addresses, dates, and numeric health measurements
- SQLite persistence for patient records
- Search, viewing, editing, and deleting records
- A demonstration workflow for employer-supplied validation scenarios
- AI remark generation with safe handling for missing keys or API outages
- Automated tests using pytest

The app is intentionally simple, readable, and designed for learning and interview use.

## Technology stack

- Python 3.11+
- Streamlit
- SQLite3 (built into Python)
- requests
- python-dotenv
- pytest

## Project structure

```text
health-prediction-app/
├── app.py
├── ai_service.py
├── config.py
├── database.py
├── validators.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── INTERVIEW_PREPARATION.md
├── data/
│   └── employer_test_data.json
├── scripts/
│   └── validate_test_data.py
├── tests/
│   ├── test_ai_service.py
│   ├── test_database.py
│   └── test_validators.py
└── health_predictions.db   # created at runtime; ignored by git
```

## Prerequisites

- Python 3.11 or newer
- Windows PowerShell or VS Code terminal
- Internet access for optional live AI API usage

## Installation

1. Open a terminal in the project folder.
2. Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the app

Start the Streamlit dashboard:

```powershell
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## AI API configuration

This application supports a real provider through environment variables.

Create a `.env` file in the project folder based on `.env.example`:

```env
AI_PROVIDER=openrouter
AI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
AI_API_BASE_URL=https://openrouter.ai/api/v1/chat/completions
APP_DATABASE_PATH=health_predictions.db
```

Notes:

- Do not commit `.env` to GitHub.
- The app will not expose secret values in logs or UI output.
- `AI_PROVIDER` defaults to `openrouter`; add your own API key to `.env` to enable live AI-generated risk remarks.
- With `AI_PROVIDER=openrouter` and a valid key, the app requests a brief, screening-level assessment of possible health risk signals from the supplied measurements. The AI output is stored and shown in the Remarks field.
- If `AI_PROVIDER=mock`, no key is configured, or the service is unavailable, the app continues working and labels the result as a fallback; it is not presented as an external AI prediction.
- Only the three blood-test measurements are included in the AI request; name, date of birth, and email are not sent.
- The AI prompt asks the model to explain uncertainty (including missing units and clinical context), avoid diagnosing disease, and recommend professional interpretation.
- These remarks are informational only, not medical advice or a diagnosis.

## Validation behaviour

Validation rules cover:

- Full names cannot be empty after trimming whitespace.
- Emails must look valid, including a domain and valid suffix.
- Dates must use DD/MM/YYYY or DD.MM.YYYY and cannot be in the future.
- Numeric values must be finite, not negative, and within sensible limits.

The app rejects invalid records before writing to the database or calling the AI API.

## SQLite database

The app creates its SQLite database automatically when it starts. The default file is:

```text
health_predictions.db
```

This file is created locally and ignored by Git.

## Test data import and validation

The employer-supplied records are stored in:

```text
data/employer_test_data.json
```

Run the demonstration validator:

```powershell
python scripts/validate_test_data.py
```

This helper attempts all ten supplied rows, shows which records are valid, records validation failures, and preserves each original supplied record for audit. Invalid rows are not inserted as valid patient records.

## Running tests

```powershell
pytest -q
```

The suite covers:

- validator behavior
- database CRUD flows
- duplicate detection
- AI service success/failure cases

## Demonstrating CRUD manually

### Create

- Open the app and complete the registration form.
- Submit the form.
- The app validates data before saving.
- A valid record is inserted into SQLite and the AI remarks are stored.

### Read

- Use the search box to filter by patient name or email.
- The table shows saved records.
- Select a patient to view details.

### Update

- Select a patient.
- Change the email or other valid fields.
- Save changes.
- If measurement values changed, the app regenerates remarks.

### Delete

- Tick the confirmation checkbox.
- Click Delete Selected Record.
- Confirm the record is removed from the list.

## Troubleshooting

### Module import errors

If Python cannot import `validators`, `database`, or `ai_service`, make sure you are running the command from the project root and your virtual environment is active.

### SQLite database errors

Check whether the `health_predictions.db` file is locked by another process. Close the Streamlit app or database viewer and retry.

### AI not available

If no API key is configured, the app automatically falls back to a safe mock/test mode. The UI continues working without exposing secrets.

### Streamlit not found

Install requirements again:

```powershell
python -m pip install -r requirements.txt
```

## Security and quality notes

- No real secrets are stored in source code.
- `.env` is excluded from Git.
- No sensitive patient data is uploaded to GitHub.
- Unsafe HTML rendering is avoided.
- The AI output is cautious and non-diagnostic.

## GitHub safety

Before pushing to GitHub:

1. Review `.gitignore`.
2. Make sure `.env` and the database file are not tracked.
3. Use a clean branch and review changes with `git status`.
4. Commit only relevant files.

Example:

```powershell
git status
git add .
git commit -m "Initial health prediction app"
```

## Limitations

This app provides informational insights only. It does not diagnose disease and does not replace professional medical care. The remarks and validation are educational and intended for demonstration, not medical practice.

## Interview guidance

The code is written to be easy to explain:

- `validators.py` handles safe validation rules.
- `database.py` manages SQLite CRUD operations.
- `ai_service.py` handles the external API request.
- `app.py` connects the interface to the logic.

This makes the architecture clear and beginner-friendly.
