# Task Manager API 🚀

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Security](https://img.shields.io/badge/Security-JWT-blue.svg)](https://jwt.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Professional-grade REST API for task management built with FastAPI. This version includes JWT authentication, protected endpoints, structured logging, health checks, and clean request validation patterns for a more interview-ready project.

## What this project demonstrates

- FastAPI application structure
- JWT authentication with bearer tokens
- Protected routes using dependency injection
- Global HTTP and server error handling
- Health check endpoint for operational readiness
- In-memory task management suitable for demos and learning

## Architecture

```text
main.py                entry point and app wiring
src/
  auth.py              JWT creation, validation and auth dependency
  config.py            environment/settings configuration
  __init__.py          package marker
```

## Quick start

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional)

```bash
cp .env.example .env
```

### 4. Run the API

```bash
uvicorn main:app --reload
```

## Authentication flow

### Login

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

### Protected route example

```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer <jwt-token>"
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API welcome message |
| GET | `/health` | Liveness/health check |
| POST | `/login` | Create a JWT token |
| GET | `/me` | Return current authenticated user |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task |
| GET | `/tasks/{task_id}` | Get task by id |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

## Example task payload

```json
{
  "title": "Ship the first version",
  "description": "Deliver the MVP and validate the flow",
  "priority": 3,
  "completed": false
}
```

## Security notes

- JWT is used for route protection
- Token validation checks signature and expiration
- Credentials are environment-based and should be changed in production
- Replace the default secret key before deploying beyond local development

## Future improvements

- replace in-memory storage with PostgreSQL + SQLAlchemy
- add user registration and hashed password storage
- add refresh tokens and role-based access control
- add structured observability and Prometheus metrics

## License

MIT
