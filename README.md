# 🚀 Task Manager API (AI-Powered with RAG)

![Backend CI](https://github.com/Bloodsoaked-hub/task-manager-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)
![AWS](https://img.shields.io/badge/AWS-EC2_%7C_RDS_%7C_S3-FF9900.svg?logo=amazon-aws)

## 📌 Overview

A production-ready RESTful API for managing projects and tasks, integrating **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)**. Built with FastAPI and strict layered architecture, it enforces resource-level authorization while enabling semantic (meaning-based) search and context-aware task generation grounded in project documentation. Containerized with Docker and configured for **AWS** deployment with automated **CI/CD**.

## ✨ Key Features

- **Context-Aware AI Task Generation (RAG):** Converts plain-language notes into structured, persisted tasks. Retrieves relevant project document chunks via vector similarity search (`pgvector`) to ground Anthropic Claude's output in actual project context, enforcing strict schema validation via LLM tool-calling and Pydantic.
- **Semantic Search:** High-precision task and document retrieval powered by OpenAI `text-embedding-3-small` and PostgreSQL `pgvector` distance operators, combined with relational SQL ownership filters.
- **Cost-Guard Security:** JWT authentication (`bcrypt` password hashing) with strict ownership verification executed *before* any external LLM or embedding API call is triggered—preventing unauthorized billing abuse.
- **Automated Testing & CI/CD:** Integration test suite (`pytest`) executed automatically on every push via GitHub Actions against an ephemeral `pgvector/pgvector:pg16` service container.
- **AWS Cloud-Ready:** Fully containerized multi-service setup engineered for deployment on AWS infrastructure (EC2, RDS for PostgreSQL, S3 for document storage).

## 🏗️ Architecture & Engineering Decisions

The codebase enforces a strict unidirectional dependency flow to decouple HTTP transport, business rules, and persistence:

`Router → Service → Repository → Model`

- **Routers (`app/api/routes/`):** HTTP request/response handling, dependency injection, and status codes. Zero business logic.
- **Services (`app/services/`):** Core business logic, ownership guards, RAG orchestration, and external LLM/Embedding API clients.
- **Repositories (`app/repositories/`):** Encapsulated `SQLAlchemy` queries and vector similarity operations.
- **Models (`app/models/`):** Relational & vector (`VECTOR(1536)`) ORM definitions managed via Alembic migrations.
- **Schemas (`app/schemas/`):** Pydantic v2 contracts for strict input/output validation.

### Key Architectural Choices

- **Single-Database Vector Strategy (`pgvector`):** Kept relational metadata and 1536-dimensional embeddings inside PostgreSQL instead of introducing a separate vector database, eliminating distributed transaction overhead and simplifying transactional consistency.
- **Deterministic LLM Outputs via Tool Calling:** Used Anthropic Claude's native tool-use interface rather than raw text/JSON parsing to guarantee type-safe task extraction.

## 📡 Core API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a new user account |
| `POST` | `/auth/login` | Authenticate and issue a JWT access token |
| `POST` | `/projects/` | Create a new project workspace |
| `POST` | `/projects/{project_id}/tasks/` | Create a task and generate its vector embedding |
| `GET` | `/projects/{project_id}/tasks/search?q=...` | Semantic search across project tasks by meaning |
| `POST` | `/projects/{project_id}/tasks/generate` | Generate structured tasks from text using project RAG context |

*(Full interactive OpenAPI/Swagger documentation covering all CRUD endpoints is available at `/docs`)*

## 🧪 Testing & CI/CD

Every push and pull request to `main` triggers the GitHub Actions workflow (`.github/workflows/ci.yml`), which spins up a `pgvector/pgvector:pg16` container, enables the `vector` extension, and runs the full `pytest` suite with mocked LLM/embedding providers.

To run tests locally against a running PostgreSQL instance:

```bash
PYTHONPATH=. pytest
```

## 🚀 Quick Start (Local Setup)

### Prerequisites

- Docker & Docker Compose
- [Anthropic API key](https://console.anthropic.com)
- [OpenAI API key](https://platform.openai.com)

### Installation & Execution

```bash
# 1. Clone the repository
git clone https://github.com/Bloodsoaked-hub/task-manager-api.git
cd task-manager-api

# 2. Configure environment variables (replace placeholder API keys)
cat <<EOF> .env
DATABASE_URL=postgresql://user:password@db:5432/task_manager
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
EOF

# 3. Build and start containers
docker compose up -d --build

# 4. Apply Alembic database migrations
sleep 5
docker compose exec api python -m alembic upgrade head
```

Once running, the API is accessible at `http://localhost:8000` and interactive Swagger UI at `http://localhost:8000/docs`.