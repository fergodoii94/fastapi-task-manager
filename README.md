# Task Manager API 🚀

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI/CD](https://github.com/fergodoii94/fastapi-task-manager/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/fergodoii94/fastapi-task-manager/actions)

Professional-grade **REST API** for task management built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. 
Demonstrates production-ready patterns including authentication-ready architecture, comprehensive testing, Docker containerization, and CI/CD automation.

---

## 🎯 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Docker & Docker Compose (optional)
- Git

### Local Setup (Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/fergodoii94/fastapi-task-manager.git
   cd fastapi-task-manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run application**
   ```bash
   uvicorn src.main:app --reload
   ```

   API available at: `http://localhost:8000`
   Docs available at: `http://localhost:8000/docs`

### Docker Setup (Recommended)

```bash
# Build and start services
docker-compose up --build

# Run migrations (if needed)
docker-compose exec api alembic upgrade head

# Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks` | List all tasks (paginated) |
| `GET` | `/tasks/{id}` | Get task details |
| `PUT` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

### Create Task
```http
POST /api/v1/tasks
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "priority": 3,
  "status": "pending"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the API",
  "priority": 3,
  "status": "pending",
  "created_at": "2024-01-15T10:30:00+00:00",
  "updated_at": "2024-01-15T10:30:00+00:00"
}
```

### List Tasks
```http
GET /api/v1/tasks?skip=0&limit=10&status=pending
```

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 10, max: 100) - Records per page
- `status` (string, optional) - Filter by status: `pending`, `in_progress`, `completed`, `archived`

**Response (200 OK):**
```json
{
  "total": 15,
  "items": [
    {
      "id": 1,
      "title": "Task 1",
      "description": "Description",
      "priority": 1,
      "status": "pending",
      "created_at": "2024-01-15T10:30:00+00:00",
      "updated_at": "2024-01-15T10:30:00+00:00"
    }
  ],
  "page": 1,
  "page_size": 10
}
```

### Get Task by ID
```http
GET /api/v1/tasks/1
```

### Update Task
```http
PUT /api/v1/tasks/1
Content-Type: application/json

{
  "status": "completed",
  "priority": 5
}
```

### Delete Task
```http
DELETE /api/v1/tasks/1
```

---

## 🏗️ Project Architecture

### Directory Structure
```
fastapi-task-manager/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic validators
│   ├── services.py          # Business logic layer
│   └── routes/
│       ├── __init__.py
│       └── tasks.py         # Task endpoints
├── tests/
│   ├── __init__.py
│   └── test_tasks.py        # Comprehensive tests (35+ cases)
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions CI/CD
├── Dockerfile               # Production container
├── docker-compose.yml       # Local dev environment
├── pyproject.toml           # Project metadata & tools config
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
└── README.md               # This file
```

### Layered Architecture
```
HTTP Request
    ↓
Routes (Validation)
    ↓
Services (Business Logic)
    ↓
Models (Database)
    ↓
PostgreSQL Database
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

**Coverage:** 98%+ (35+ test cases covering CRUD, validation, pagination, filtering, error handling)

---

## 🚀 Deployment

### Docker Compose
```bash
docker-compose up --build
```

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@host:5432/taskmanager
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
DEBUG=False
```

---

## 🔧 Development

### Code Quality
```bash
# Format code
black src tests

# Lint
flake8 src tests --max-line-length=100

# Type checking
mypy src --ignore-missing-imports
```

### CI/CD Pipeline
Automated testing, linting, and Docker builds on every push via GitHub Actions.

---

## 📈 Features

✅ **Production-Ready Architecture**
- Layered architecture (routes → services → models)
- Type hints throughout codebase
- Comprehensive error handling

✅ **Database**
- PostgreSQL with connection pooling
- SQLAlchemy ORM with proper relationships
- Indexed fields for performance

✅ **Testing**
- 35+ test cases with 98%+ coverage
- CRUD operations, validation, pagination
- Error scenarios and edge cases

✅ **Containerization**
- Production Dockerfile with health checks
- Docker Compose for local development
- Multi-stage builds for optimization

✅ **CI/CD**
- GitHub Actions workflow
- Automated testing and code quality checks
- Docker image building and caching

✅ **Documentation**
- Interactive API docs (Swagger/OpenAPI)
- Comprehensive README with examples
- Well-documented code with docstrings

---

## 🔐 Security

- Environment variable management
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Type hints for runtime safety
- Request/response validation

**Authentication Ready:** Structure prepared for JWT implementation

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and quality checks
4. Commit changes (`git commit -m 'feat: add amazing feature'`)
5. Push to branch and open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 👨‍💻 Author

**Fernando Godoi**
- GitHub: [@fergodoii94](https://github.com/fergodoii94)
- Email: fergodoi94@gmail.com
- Python Backend Developer | FastAPI | REST APIs | Async Programming

---

**Status:** ✅ Production Ready | **Test Coverage:** 98%+ | **Latest Update:** January 2024
