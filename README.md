# testcontainers-python-ci

Automated integration test suite using **Pytest**, **Testcontainers-python**, and **Requests** for testing a containerized REST API with a PostgreSQL database, configured for execution in **GitHub Actions**.

## Project Architecture

```text
[ GitHub Actions / Local Runner ]
               │
               ▼
        [ Pytest Runner ]
               │
      (Testcontainers API)
               │
               ▼
  ┌──────────────────────────────────────────────┐
  │              Docker Engine                   │
  │                                              │
  │  ┌────────────────────┐  ┌────────────────┐ │
  │  │ REST API Container │  │ Postgres DB    │ │
  │  │ (todo-api)         │◄─┼─┤ Container      │ │
  │  └────────────────────┘  └────────────────┘ │
  └──────────────────────────────────────────────┘
```

## Project Structure

```text
testcontainers-python-ci/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI workflow
├── tests/
│   ├── conftest.py         # Testcontainers setup & Pytest fixtures
│   └── test_todo_api.py    # REST API integration tests
├── .gitignore
├── pytest.ini              # Pytest configuration
├── README.md
└── requirements.txt        # Python dependencies
```

## Prerequisities

- **Python 3.10+**
- **Docker Desktop** / **Docker Engine** running locally

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/testcontainers-python-ci.git
   cd testcontainers-python-ci
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run integration tests:**
   ```bash
   pytest -v
   ```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs automatically on `push` and `pull_request` to `main`. It provisions a runner with Docker support, installs dependencies, and runs the Pytest suite against containerized services.