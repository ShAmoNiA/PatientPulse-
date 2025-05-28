# PatientPulse

PatientPulse is a FastAPI-based application designed to manage patient health data, specifically focusing on biometrics like glucose levels, blood pressure, and weight. It provides an API for data ingestion, retrieval, and analytics, allowing for the tracking and analysis of patient health metrics over time. The system includes an ETL process for initial data loading and scheduled jobs for hourly analytics computation.

---
## Features

* **Patient Management**: Basic listing of patients.
* **Biometric Data Tracking**: Record, retrieve, update, and delete biometric readings (glucose, systolic/diastolic blood pressure, weight).
* **Data Validation**: Input data for patients and biometrics is validated using Pydantic.
* **ETL Process**: Initial data loading for patients (from JSON) and biometric readings (from CSV).
* **Hourly Analytics**:
    * Scheduled computation of min, max, and average for biometric types on an hourly basis.
    * Two versions of analytics computation are available, selectable via configuration.
* **API Endpoints**: Secure and versioned API endpoints for interacting with patient, biometric, and analytics data.
* **Database**: Uses PostgreSQL for persistent data storage.
* **Task Scheduling**: Uses APScheduler for running background analytics tasks.

---
## Technology Stack

* **Backend**: Python, FastAPI
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Data Validation**: Pydantic
* **Dependency Management**: Pipenv
* **Task Scheduling**: APScheduler
* **Testing**: Pytest, TestClient

---
## Architecture Decisions
* **Backend** Framework**: FastAPI is a modern, high-performance Python web framework, a good choice for building APIs.
* **Database**: PostgreSQL is a robust and feature-rich relational database, suitable for this type of application.
* **ORM**: SQLAlchemy provides a powerful ORM layer, abstracting database interactions.
* **Task Scheduling**: APScheduler is used for running background tasks, specifically the hourly analytics computation.
* **Containerization**: Docker is used for containerization, with a docker-compose.yml file provided to set up the API and database services, facilitating easier deployment and development environment consistency.
* **Two-Stage Analytics**: The design incorporates two versions of analytics. Version 2, using a biometrics_hourly buffer table, suggests a design decision to handle potentially high-frequency biometric updates more efficiently by batching them for analytics processing. This can reduce the load on the main biometrics table during analytics runs.
---
## Setup and Installation (Local)

**Prerequisites:**

* Python (3.8 or newer recommended)
* Pipenv (Python packaging tool)
* PostgreSQL (local installation)

**Steps:**

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/ShAmoNiA/PatientPulse-
    cd PatientPulse
    ```

2.  **Install Pipenv:**
    If you don't have Pipenv installed, you can install it using pip:
    ```bash
    pip install pipenv
    ```

3.  **Install Dependencies using Pipenv:**
    Pipenv manages dependencies using a `Pipfile`. If you don't have one, `pipenv install` will create it.
    Install the necessary packages:
    ```bash
    pipenv install fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic pydantic-settings apscheduler
    ```
    For development and testing:
    ```bash
    pipenv install --dev pytest httpx
    ```
    This will create/update `Pipfile` and `Pipfile.lock`.

4.  **Set up PostgreSQL Database:**
    * Ensure your local PostgreSQL server is running.
    * Create a database and a user for the application. For example, using `psql`:
        ```sql
        CREATE DATABASE health;
        CREATE USER healthapi WITH PASSWORD 'supersecret';
        GRANT ALL PRIVILEGES ON DATABASE health TO healthapi;
        ```
        *(Adjust user, password, and database name as needed.)*

5.  **Configure Environment Variables:**
    The application uses environment variables for configuration, primarily for the database connection. You can set these in your shell, or use a `.env` file (which `pydantic-settings` can automatically load from the project root).
    Create a `.env` file in the project root:
    ```env
    DATABASE_URL=postgresql://healthapi:supersecret@localhost:5432/health
    ANALYTICS_VERSION=1 # or 2
    ```
    * `DATABASE_URL`: The connection string for your local PostgreSQL database.
    * `ANALYTICS_VERSION`: Set to "1" or "2" to choose the analytics processing version.

    The `app/core/config.py` file defines how these settings are loaded.

---
## Running the Application (Local)

1.  **Activate the Pipenv Shell:**
    Navigate to your project directory (where `Pipfile` is located) and run:
    ```bash
    pipenv shell
    ```
    This activates the virtual environment managed by Pipenv.

2.  **Ensure your PostgreSQL server is running and accessible with the configured `DATABASE_URL`.**

3.  **Start the FastAPI application using Uvicorn:**
    The `app/main.py` file includes a section `if __name__ == "__main__":` which allows running the app directly.
    From the project root directory (with the `pipenv shell` activated):
    ```bash
    python app/main.py
    ```
    This will start the Uvicorn server, typically on `http://0.0.0.0:8000`.

    Alternatively, you can run uvicorn directly (which is common for development):
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    If not running `python app/main.py` directly, you might need to use `pipenv run` if the shell is not active in that specific terminal:
    ```bash
    pipenv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

* The API will be accessible at `http://localhost:8000`.
* The FastAPI interactive documentation (Swagger UI) will be at `http://localhost:8000/docs`.
* The alternative documentation (ReDoc) will be at `http://localhost:8000/redoc`.

On startup, the application will:
1.  Create database tables if they don't exist.
2.  Run the ETL process (`run_etl`) to load initial data from `data/patients.json` and `data/readings.csv`.
3.  Start the APScheduler to run hourly analytics.

---
## API Endpoints

The API is versioned under `/api/v1/`.

* **Patients (`/api/v1/patients`)**:
    * `GET /`: List patients with pagination.
* **Biometrics (`/api/v1/biometrics`)**:
    * `GET /`: Get biometric history for a patient with pagination and optional type filtering.
    * `POST /`: Upsert (insert or update) a biometric record. This also writes to the `biometrics_hourly` table.
    * `DELETE /{biometric_id}`: Delete a biometric record.
* **Analytics (`/api/v1/analytics`)**:
    * `GET /`: Get computed analytics for a patient, with optional filtering by metric name.

Refer to the Swagger UI at `/docs` for detailed request/response models and to try out the endpoints.

---
## ETL Process

The ETL (Extract, Transform, Load) process is defined in `app/etl/` and orchestrated by `app/analytics/compute.py`'s `run_etl` function. It runs on application startup.

1.  **Extract**:
    * Patient data is loaded from `data/patients.json`.
    * Biometric readings are loaded from `data/readings.csv`.
2.  **Transform**:
    * Patient data is validated (e.g., DOB format, email validity, gender normalization).
    * Biometric readings are normalized.
3.  **Load**:
    * Validated patient data is added or updated in the `patients` table.
    * Normalized biometric data is bulk-inserted into the `biometrics` table, avoiding duplicates.

---
## Analytics Computation

Hourly analytics are computed by a scheduled job. The version of the analytics job (v1 or v2) is determined by the `ANALYTICS_VERSION` environment variable.

* **`run_hourly_analytics` (Version 1)** (`app/analytics/run_hourly_analytics.py`):
    * Queries the main `biometrics` table.
    * Computes `min`, `max`, and `avg` values.
    * Saves these metrics into the `analytics` table.
* **`run_hourly_analytics_v2` (Version 2)** (`app/analytics/run_hourly_analytics_v2.py`):
    * Consumes data from the `biometrics_hourly` table.
    * Aggregates data and saves metrics to the `analytics` table.
    * Clears the processed rows from the `biometrics_hourly` buffer.

The scheduler in `app/main.py` is currently configured to run the selected analytics job frequently (e.g., every 10 seconds) for demonstration purposes.

---
## Testing

Tests are located in the `test/` directory and use `pytest`.

**Running Tests:**

1.  **Activate the Pipenv Shell:**
    If not already active, navigate to your project directory and run:
    ```bash
    pipenv shell
    ```
2.  Ensure your test dependencies (`pytest`, `httpx`) are installed (they should be if you used `pipenv install --dev pytest httpx`).
3.  Make sure a test database (or your development database if you don't mind it being modified/cleared by tests) is configured and accessible. Test setup in `test_analytics.py`, `test_biometrics.py`, and `test_patients.py` handles table creation and teardown using a `test.db` SQLite database by default (as per `app/core/config.py`'s `DATABASE_URL` for settings, which the tests might implicitly use if they instantiate the app or its components that rely on `settings`).
4.  From the project root directory (with the `pipenv shell` activated):
    ```bash
    pytest
    ```
    Or, if the shell is not active in your current terminal:
    ```bash
    pipenv run pytest
    ```
