<div align="center">

# Task Manager API

**A multi-user REST API built with FastAPI, SQLAlchemy 2.0 and PostgreSQL.**

[![CI](https://github.com/fergodoii94/fastapi-task-manager/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/fergodoii94/fastapi-task-manager/actions/workflows/ci-cd.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Auth](https://img.shields.io/badge/Auth-JWT-6B5CE7)
![License](https://img.shields.io/badge/License-MIT-blue)

</div>

A portfolio backend project demonstrating authenticated REST API design, per-user data isolation, password hashing, typed validation, database migrations, automated tests and containerization.

## Overview

Users can register, log in and manage their own tasks. The API uses signed JWT bearer tokens for authentication and scopes every task read/write operation to the authenticated user. SQLite is the default for local development and tests; PostgreSQL is supported through configuration and Docker Compose.

## Features

- User registration and login with email/password.
- Password hashing with Argon2 via `pwdlib`; plaintext passwords are never stored.
- JWT access tokens signed with HS256 and configurable expiration.
- Authenticated `/me` endpoint.
- Task CRUD with strict Pydantic request/response contracts.
- Per-user task ownership enforced in database queries; cross-user task access returns 404.
- SQLAlchemy 2.0 persistence and Alembic migrations.
- PostgreSQL with Docker Compose; SQLite by default for local development/tests.
- Pagination and filtering by task status.
- Input validation for titles, status, priority, partial updates and unknown request fields.
- GitHub Actions checks Ruff, applies migrations, checks ORM/migration parity and runs Pytest.
- Docker image runs as a non-root user.
- Interactive OpenAPI documentation at `/docs`.

## Tech stack

| Area | Tools |
|---|---|
| Language & API | Python, FastAPI, Pydantic |
| Authentication | JWT (PyJWT), Argon2 (pwdlib) |
| Data layer | SQLAlchemy 2.0, PostgreSQL, SQLite |
| Migrations | Alembic |
| Quality | Pytest, Ruff |
| Runtime | Docker, Docker Compose |
| Automation | GitHub Actions |

## Architecture

- `src/routes/`: authentication and task HTTP endpoints.
- `src/services.py`: user creation and owner-scoped persistence operations.
- `src/models.py`: SQLAlchemy User and Task models.
- `src/schemas.py`: Pydantic request/response contracts.
- `src/security.py`: password hashing and JWT creation/verification.
- `src/config.py`: validated environment settings.
- `src/database.py`: engine, session factory and declarative base.
- `alembic/`: versioned database migrations.

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Before running outside a disposable local environment, replace `AUTH_SECRET_KEY` in `.env` with a unique random secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Then apply migrations and start the API:

```bash
alembic upgrade head
uvicorn src.main:app --reload
```

The default database is SQLite. Set `DATABASE_URL` in `.env` to a PostgreSQL SQLAlchemy URL to use PostgreSQL. Apply schema changes through Alembic migrations; do not rely on `create_all` in application startup.

## Run with Docker Compose

```bash
docker compose up --build
```

The API container applies migrations before starting Uvicorn. Configure a strong `AUTH_SECRET_KEY` and replace all example database credentials before deployment.

| Service | Address |
|---|---|
| API | http://localhost:8000 |
| OpenAPI docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

## Authentication flow

1. Register with `POST /api/v1/auth/register`.
2. Log in with `POST /api/v1/auth/login` and copy the returned access token.
3. Send the token on protected requests using `Authorization: Bearer <token>`.
4. Use `GET /api/v1/auth/me` to retrieve the authenticated account.

Example registration:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","password":"a-long-unique-password"}'
```

Example login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","password":"a-long-unique-password"}'
```

Use the returned `access_token` for task endpoints:

```bash
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Passwords must contain at least 12 characters. Access-token lifetime is configurable with `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30 minutes).

## API endpoints

Base path: `/api/v1`

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | No | Create an account (201) |
| POST | `/auth/login` | No | Obtain a bearer token |
| GET | `/auth/me` | Yes | Get current user |
| POST | `/tasks` | Yes | Create an owned task (201) |
| GET | `/tasks?page=1&page_size=10&status=pending` | Yes | List own tasks |
| GET | `/tasks/{id}` | Yes | Retrieve an owned task |
| PATCH | `/tasks/{id}` | Yes | Update an owned task |
| DELETE | `/tasks/{id}` | Yes | Delete an owned task (204) |

Task statuses: `pending`, `in_progress`, `completed`, `archived`. Priority ranges from 1 to 5. Titles are trimmed, required and limited to 160 characters. Unknown request fields are rejected. A user cannot list, read, update or delete another user's tasks; inaccessible task IDs return 404.

## Database migrations

The user/ownership migration preserves pre-existing tasks by assigning them to a disabled legacy account (`legacy-migration@invalid.local`). Those records are not visible to newly registered users. Reassign legacy records explicitly through a controlled administrative/data-migration process if they need to be retained under a real account.

Create a new migration after changing ORM models:

```bash
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
alembic check
```

Review autogenerated migration files before applying them. To inspect the current revision, run `alembic current`.

## Quality checks

```bash
ruff check src tests alembic
alembic upgrade head
alembic check
pytest
```

Tests use isolated SQLite and do not require PostgreSQL. The GitHub Actions workflow runs linting, migration upgrade, ORM/migration parity and the test suite. Check the Actions tab for the result of the latest run.

## Security notes and limitations

This is a portfolio project, not a security-audited production service. Before handling real users or deploying publicly:

- Set a unique high-entropy `AUTH_SECRET_KEY` through a secret manager; never use the development fallback.
- Serve traffic only over HTTPS and protect database credentials.
- Add rate limiting and abuse controls to registration and login.
- Define account recovery, email verification, token revocation/refresh and operational monitoring as required by the product.
- Review database backup, migration, logging and privacy practices for the deployment environment.

Never commit production secrets or real user data.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./task_manager.db` |
| `APP_NAME` | FastAPI application title | `Task Manager API` |
| `API_V1_PREFIX` | API route prefix | `/api/v1` |
| `AUTH_SECRET_KEY` | JWT signing secret | Development-only fallback; replace it |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime | `30` |

## Related projects

- [JWT token validation example](https://github.com/fergodoii94/jwt-auth-system)
- [E-commerce API prototype](https://github.com/fergodoii94/ecommerce-backend-api)
- [WebSocket echo server](https://github.com/fergodoii94/websocket-chat-app)

---

<div align="center">
  <sub>Built as part of my Python backend engineering portfolio.</sub>
</div>

## License

MIT.
