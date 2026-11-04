# Task Manager API

A backend portfolio project built with Python 3.12, FastAPI, SQLAlchemy 2.0 and PostgreSQL. It demonstrates REST design, persistence, validation, pagination, dependency injection, automated tests, Docker and CI.

[![CI](https://github.com/fergodoii94/fastapi-task-manager/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/fergodoii94/fastapi-task-manager/actions/workflows/ci-cd.yml)

## Features
- CRUD task endpoints with typed request and response schemas.
- SQLAlchemy 2.0 persistence; PostgreSQL in deployment and SQLite for local/tests.
- Pagination, status filtering and priority validation.
- Isolated integration tests using in-memory SQLite.
- Docker image runs as a non-root user.
- GitHub Actions executes Ruff and Pytest.
- Interactive OpenAPI documentation at /docs.

## Architecture
HTTP routes live in src/routes, application operations in src/services.py, ORM models in src/models.py, API contracts in src/schemas.py and database setup in src/database.py.

## Run locally
Requires Python 3.11+.

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    uvicorn src.main:app --reload

The default database is SQLite. Set DATABASE_URL to a PostgreSQL SQLAlchemy URL to use PostgreSQL. Copy .env.example to .env and adjust credentials.

## Run with Docker Compose

    docker compose up --build

API: http://localhost:8000 | OpenAPI: http://localhost:8000/docs | Health: http://localhost:8000/health

## API endpoints
Base path: /api/v1

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /tasks | Create task (201) |
| GET | /tasks?page=1&page_size=10&status=pending | Paginated list and optional filter |
| GET | /tasks/{id} | Retrieve task |
| PATCH | /tasks/{id} | Partial update |
| DELETE | /tasks/{id} | Delete task (204) |

Statuses: pending, in_progress, completed, archived. Priority ranges from 1 to 5. Titles are required and limited to 160 characters.

## Quality checks

    ruff check src tests
    pytest

Tests use isolated SQLite and do not require PostgreSQL. GitHub Actions runs these checks on pushes and pull requests.

## Configuration
DATABASE_URL defaults to sqlite:///./task_manager.db. APP_NAME defaults to Task Manager API. API_V1_PREFIX defaults to /api/v1. Never commit production credentials.

## License
MIT.
