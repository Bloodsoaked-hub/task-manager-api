# 🚀 Task Manager API (AI-Powered with RAG)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)

## 📌 Overview
A production-ready RESTful API for managing projects and tasks, integrating **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)**. Built with FastAPI and clean architecture principles, it enforces strict data ownership while allowing users to perform semantic (meaning-based) searches and natural language task generation using OpenAI embeddings and Anthropic Claude.

## ✨ Key Features
* **AI-Powered Task Generation:** Send a plain-language description and get back structured, saved tasks. Uses Claude's tool-use (structured output) and Pydantic validation.
* **Semantic Search (RAG):** Fast and accurate task retrieval using `pgvector` and OpenAI `text-embedding-3-small`. Searches rank results by meaning (cosine distance) combined with standard SQL filters.
* **Robust Security:** JWT-based authentication (bcrypt). Authorization is checked *before* any paid external API call is made, preventing billing abuse.
* **Clean Architecture:** Strict separation of concerns ensuring highly testable and maintainable code.
* **Fully Containerized:** One-click deployment with Docker, Docker Compose, and PostgreSQL 16 (pgvector preinstalled).

## 🏗️ Architecture

The project follows a rigorous layered architecture to keep responsibilities separated and code testable:

`Router → Service → Repository → Model`

* **Routers (`app/api/routes/`):** Handle HTTP requests/responses, delegate to services. No business logic.
* **Services (`app/services/`):** Business logic, authorization checks, exception handling.
* **Repositories (`app/repositories/`):** Database queries only (`SQLAlchemy`), no business logic.
* **Models (`app/models/`):** SQLAlchemy ORM definitions.
* **Schemas (`app/schemas/`):** Pydantic models for request/response validation.

## 📡 API Endpoints (Core)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Log in, returns JWT access token |
| `POST` | `/projects/` | Create a project |
| `POST` | `/projects/{project_id}/tasks/` | Create a task in a project |
| `GET` | `/projects/{project_id}/tasks/search?query=...` | Semantic search for tasks by meaning (RAG) |
| `POST` | `/projects/{project_id}/tasks/generate` | Generate tasks from a natural language description (AI) |

*(Full interactive documentation covering all CRUD operations is available at `/docs` via Swagger UI)*

## 🚀 Quick Start (One-Click Setup)

### Prerequisites
* Docker & Docker Compose
* [Anthropic API key](https://console.anthropic.com)
* [OpenAI API key](https://platform.openai.com)

### Installation & Execution (Terminal)
Copy and paste the following block into your terminal. It will clone the repository, generate the `.env` file, spin up the database and API in the background, and apply migrations:

```bash
# 1. Clone and enter the repository
git clone [https://github.com/Bloodsoaked-hub/task-manager-api.git](https://github.com/Bloodsoaked-hub/task-manager-api.git)
cd task-manager-api

# 2. Create environment variables automatically
cat <<EOF> .env
DATABASE_URL=postgresql://user:password@db:5432/task_manager
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
EOF

# 3. Build and run containers in the background
docker compose up -d --build

# 4. Wait for DB to initialize, then apply database migrations
sleep 5
docker compose exec api python -m alembic upgrade head