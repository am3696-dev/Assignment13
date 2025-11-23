## Assignment 13 – JWT Authentication, Frontend UI & End-to-End (E2E) Testing

This project is a secure REST API and Frontend Application built with FastAPI as part of a course assignment. It implements a complete user authentication system using JWT (JSON Web Tokens), a responsive UI for registration and login, and a full CI/CD pipeline that automatically runs End-to-End (E2E) browser tests using Playwright before deploying to Docker Hub.

---

## CI/CD & Deployment Information

This project is automatically built, tested, scanned, and deployed using GitHub Actions.

### Docker Hub Repository Link

The latest stable build of this application is available on Docker Hub at the following link:

****https://hub.docker.com/repository/docker/am3696/assignment13/tags****

---

## How to Run Locally

### 1. Prerequisites
* Python 3.10+
* Docker (for running Postgres) or a local PostgreSQL server

### 2. Setup
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/am3696-dev/Assignment13.git](https://github.com/am3696-dev/Assignment13.git)
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install Playwright Browsers:(Required for E2E tests to run):**
    ```bash
    playwright install chromium
    ```

5.  **Set Environment Variables:Create a .env file in the root of the project and add your configuration:**
    Create a `.env` file in the root of the project and add your database credentials:
    ```.env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=mysecretpassword
    POSTGRES_DB=assignment13
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    JWT_SECRET_KEY=your_super_secret_key
    JWT_REFRESH_SECRET_KEY=your_refresh_secret_key
    ```

### 3. Run the Application
```bash
uvicorn main:app --reload
```

### Once running, you can access the application at:
* Register: http://127.0.0.1:8000/register
* Login: http://127.0.0.1:8000/login

---
### How to Run Tests Locally
To run the full test suite locally, ensure your environment is set up and your test database is accessible, then run:
### Run All Tests:
```bash
pytest
```
### Run E2E Browser Tests Only:
```bash
pytest tests/e2e/test_auth.py
```
