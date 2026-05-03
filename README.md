# E-commerce Backend API

**Python + AI Master Course — Epic Learn**

Practice project for the Epic Learn course: a small **FastAPI** backend that exposes REST endpoints for an e-commerce style API, with PostgreSQL configured via environment variables.

## What you will practice

- FastAPI routes and JSON responses
- Project layout (`core/`, `routes/`, `models/`, `schemas/`)
- SQLAlchemy database setup (PostgreSQL + `psycopg2`)
- Environment-based configuration with `.env`

## Requirements

- Python 3.10+ (3.12 recommended)
- A **PostgreSQL** database (local install, cloud, or Docker)

## Setup

1. **Clone or open this folder** in your editor.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   ```

   Activate it:

   - **Windows (cmd):** `.venv\Scripts\activate`
   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **macOS / Linux:** `source .venv/bin/activate`

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy the example file and edit values for your machine:

   ```bash
   cp .env.example .env
   ```

   Set at least `DATABASE_URL` to your PostgreSQL connection string, for example:

   ```env
   DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/ecommerce
   ```

   The app rewrites `postgresql://` to `postgresql+psycopg2://` for SQLAlchemy automatically.

   Optional:

   - `SECRET_KEY` — used for security helpers in `core/security.py`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` — defaults to `60`

## Run the project

From the project root (with the virtual environment activated and `.env` present):

```bash
uvicorn main:app --reload
```

Then open:

- **API root:** http://127.0.0.1:8000/
- **Interactive docs (Swagger):** http://127.0.0.1:8000/docs
- **Alternative docs (ReDoc):** http://127.0.0.1:8000/redoc

### Example: PostgreSQL with Docker

If you use Docker and want a quick database:

```bash
docker run -d --name epic-ecom-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ecommerce -p 5432:5432 postgres:16-alpine
```

Use in `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecommerce
```

## API overview

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health message |
| `GET` | `/health/db` | Checks database connectivity (`SELECT 1`) |
| `GET` | `/users/` | Sample list of users |
| `GET` | `/users/{user_id}` | Sample user by id |
| `POST` | `/users/` | Query param `name` — sample create response |
| `DELETE` | `/users/{user_id}` | Sample delete response |

## Project structure

```
e-commerce-backend/
├── main.py              # FastAPI app entry
├── requirements.txt
├── .env.example         # Copy to .env
├── core/
│   ├── config.py        # Settings from environment
│   ├── database.py      # SQLAlchemy engine and sessions
│   └── security.py
├── routes/
│   └── users.py         # User routes
├── models/
├── schemas/
└── README.md
```

## Epic Learn

This repository is part of the **Python + AI Master Course** at **Epic Learn** — use it to experiment, extend routes, connect real models to the database, and build toward a full e-commerce backend.
