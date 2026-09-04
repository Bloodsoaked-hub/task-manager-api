# Task Manager API

A RESTful API for managing projects and tasks, built with FastAPI, PostgreSQL, and JWT authentication. Each user manages their own projects and tasks, with ownership enforced at every level. Includes AI-powered task generation from natural language, and semantic (meaning-based) task search using embeddings and pgvector.

## Tech Stack

- **FastAPI** — web framework
- **PostgreSQL** — database
- **pgvector** — PostgreSQL extension for storing and querying vector embeddings
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **Pydantic** — data validation and serialization
- **JWT (python-jose)** — authentication
- **Passlib (bcrypt)** — password hashing
- **Anthropic API (Claude)** — structured output for natural language task extraction
- **OpenAI API** — text embeddings for semantic search
- **Docker & Docker Compose** — containerization
- **Pytest** — testing (SQLite in-memory)

## Architecture

The project follows a layered architecture to keep responsibilities separated and code testable:

```
Router → Service → Repository → Model
```

- **Routers** (`app/api/routes/`) — handle HTTP requests/responses, delegate to services. No business logic.
- **Services** (`app/services/`) — business logic, authorization checks, exception handling.
- **Repositories** (`app/repositories/`) — database queries only, no business logic.
- **Models** (`app/models/`) — SQLAlchemy ORM definitions.
- **Schemas** (`app/schemas/`) — Pydantic models for request/response validation.
- **Dependencies** (`app/api/deps/`) — reusable FastAPI dependencies (DB session, current user resolution from JWT).

Authorization is always checked *before* any paid external API call (Claude or OpenAI) is made, so unauthorized requests are rejected at the cost of a local database lookup rather than a billed API call.

## Project Structure

```
app/
├── api/
│   ├── deps/
│   │   ├── auth.py       # get_current_user dependency (JWT validation)
│   │   └── db.py         # get_db dependency (DB session)
│   ├── routes/
│   │   ├── auth.py        # /auth/register, /auth/login
│   │   ├── projects.py    # /projects CRUD
│   │   ├── tasks.py       # /projects/{project_id}/tasks CRUD + AI generation + semantic search
│   │   └── users.py       # /users/me
│   └── router.py          # aggregates all routers
├── core/
│   ├── config.py          # environment-based settings
│   ├── database.py        # SQLAlchemy engine/session setup
│   └── security.py        # password hashing, JWT creation/decoding
├── models/                 # SQLAlchemy models (User, Project, Task with vector embedding column)
├── repositories/            # DB query layer
├── schemas/                 # Pydantic request/response models
├── services/                 # business logic layer
│   ├── auth_service.py
│   ├── project_service.py
│   ├── task_service.py
│   ├── user_service.py
│   ├── llm_service.py         # Anthropic API integration, structured output
│   └── embedding_service.py   # OpenAI API integration, text embeddings
├── frontend/                # Streamlit UI
│   └── ui.py
└── main.py                   # app entrypoint

alembic/                       # database migrations (schema versioning)
tests/
├── conftest.py             # test fixtures (in-memory SQLite, test client, mocked AI services)
├── test_auth.py
├── test_projects.py
└── test_tasks.py
```

## Features

- User registration and login with JWT-based authentication
- Passwords hashed with bcrypt, never stored or returned in plain text
- Full CRUD for projects and tasks
- Tasks are scoped under their parent project (`/projects/{project_id}/tasks`)
- Ownership enforcement — users can only access their own projects and tasks (returns `404`, not `403`, to avoid leaking resource existence)
- `toggle` endpoint for marking tasks done/undone
- **AI-powered task generation** — send a plain-language description (e.g. "call the client tomorrow and send the invoice by Friday") and get back structured, saved tasks. Uses Claude's tool-use (structured output) to guarantee the response matches the app's existing `TaskCreate` schema, which is then re-validated with Pydantic before being persisted
- **Semantic task search (RAG)** — each task's title and description are embedded (OpenAI `text-embedding-3-small`) at creation time and stored in a `pgvector` column. Searching combines a normal SQL filter (project ownership) with a vector similarity search (`cosine_distance`) in a single query, so results are ranked by meaning rather than exact keyword matches — e.g. a search for "delivery problem" correctly surfaces a task titled "Call the supplier about the delayed shipment"
- Dockerized setup with PostgreSQL + pgvector
- Schema changes managed with Alembic migrations

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in, returns JWT access token |
| GET | `/users/me` | Get current user's profile |
| POST | `/projects/` | Create a project |
| GET | `/projects/` | List current user's projects |
| GET | `/projects/{project_id}` | Get a single project |
| PATCH | `/projects/{project_id}` | Update a project |
| DELETE | `/projects/{project_id}` | Delete a project |
| POST | `/projects/{project_id}/tasks/` | Create a task in a project |
| GET | `/projects/{project_id}/tasks/` | List tasks in a project |
| GET | `/projects/{project_id}/tasks/search?query=...` | Semantic search for tasks by meaning (RAG) |
| PATCH | `/projects/{project_id}/tasks/{task_id}` | Update a task |
| PATCH | `/projects/{project_id}/tasks/{task_id}/toggle` | Toggle task done status |
| DELETE | `/projects/{project_id}/tasks/{task_id}` | Delete a task |
| POST | `/projects/{project_id}/tasks/generate` | Generate tasks from a natural language description (AI) |

Full interactive documentation is available at `/docs` (Swagger UI) once the app is running.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- An [Anthropic API key](https://console.anthropic.com) (for AI task generation)
- An [OpenAI API key](https://platform.openai.com) (for embeddings / semantic search)

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@db:5432/task_manager
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### Run with Docker

```bash
docker compose up --build
```

The database image is `pgvector/pgvector:pg16` (standard PostgreSQL 16 with the pgvector extension preinstalled). On first run, apply migrations:

```bash
docker compose exec api python -m alembic upgrade head
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Running the Frontend (Streamlit)

```bash
streamlit run app/frontend/ui.py
```

### Usage Flow

1. `POST /auth/register` — create an account
2. `POST /auth/login` — log in, copy the `access_token` from the response
3. In Swagger UI, click **Authorize** and paste the token
4. `POST /projects/` — create a project
5. `POST /projects/{project_id}/tasks/` — add tasks to it manually, or
6. `POST /projects/{project_id}/tasks/generate` — describe what needs doing in plain language and let AI break it into tasks
7. `GET /projects/{project_id}/tasks/search?query=...` — find tasks by meaning, not just exact words

## Running Tests

Tests run against an isolated in-memory SQLite database (no Docker required). Calls to Claude and OpenAI are mocked out (`unittest.mock.patch`), so the test suite runs free of charge and doesn't depend on network access:

```bash
pip install -r requirements.txt --break-system-packages
python -m pytest tests/ -v
```

Test coverage includes:
- Registration and login (success and failure cases)
- Full CRUD for projects and tasks
- Authorization checks — verifying users cannot access or modify resources belonging to other users
- AI task generation, including that it respects project ownership like every other endpoint
- Semantic search authorization (that a non-owner cannot search another user's project)

**Note:** actual vector similarity ranking (`cosine_distance`) requires a real PostgreSQL instance with pgvector — SQLite can't execute it. That behavior is verified manually against the Docker/Postgres setup rather than in the automated suite, which instead focuses on the parts that are environment-independent: authorization, request/response handling, and data persistence.

## Code Style

Code is formatted with [Black](https://github.com/psf/black):

```bash
python -m black app/
```