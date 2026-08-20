# Library Management API

A REST API for a library information system, built with **FastAPI** and **PostgreSQL**, fully containerised with Docker Compose.

It allows library staff to manage the book catalogue and track borrow status. Running `docker compose up` is all it takes to get the full stack up. No additional configuration required.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Data Model](#data-model)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [Database Migrations](#database-migrations-alembic)
- [Possible Improvements](#possible-improvements)

---

## Features

- **List books** – retrieve the full catalogue with borrow status
- **Add a book** – register a new book by its unique six-digit serial number
- **Delete a book** – permanently remove a book from the catalogue
- **Update borrow status** – mark a book as borrowed (with borrower's library card) or returned
- **Interactive documentation** – auto-generated Swagger UI at `/docs`

---

## Quick Start

### Requirements

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2 (included in Docker Desktop)

### Run the application

```bash
git clone <repo-url>
cd recruitment-task
docker compose up
```

The API will be available at **http://localhost:8000**.  
Interactive Swagger UI: **http://localhost:8000/docs**

> The application is ready when you see in the logs:  
> `api-1  | INFO:     Application startup complete.`

Run in the background:

```bash
docker compose up -d
```

Stop and remove all data:

```bash
docker compose down -v
```

---

## API Endpoints

Base URL: `http://localhost:8000`

| Method | Path | Status codes | Description |
|--------|------|--------------|-------------|
| `GET` | `/books` | 200 | List all books |
| `POST` | `/books` | 201, 409, 422 | Add a new book |
| `DELETE` | `/books/{serial_number}` | 200, 404, 422 | Delete a book |
| `PATCH` | `/books/{serial_number}/status` | 200, 404, 422 | Update borrow status |
| `GET` | `/health` | 200 | Health check |

### GET /books – list all books

```bash
curl http://localhost:8000/books/
```

Response `200`:
```json
[
  {
    "serial_number": "000001",
    "title": "The Pragmatic Programmer",
    "author": "Andrew Hunt",
    "is_borrowed": false,
    "borrowed_at": null,
    "borrowed_by": null
  }
]
```

---

### POST /books – add a new book

```bash
curl -X POST http://localhost:8000/books/ \
  -H "Content-Type: application/json" \
  -d '{"serial_number":"000001","title":"The Pragmatic Programmer","author":"Andrew Hunt"}'
```

**Request body:**

| Field | Type | Rules |
|-------|------|-------|
| `serial_number` | string | Exactly 6 digits, e.g. `"000042"` |
| `title` | string | 1–255 characters |
| `author` | string | 1–255 characters |

Response `201` – the created book object.  
Response `409` – a book with that serial number already exists.  
Response `422` – validation error (e.g. serial number is not 6 digits).

---

### DELETE /books/{serial_number} – delete a book

```bash
curl -X DELETE http://localhost:8000/books/000001
```

Response `200` – the deleted book object.  
Response `404` – book not found.  
Response `422` – serial number does not match the 6-digit format.

---

### PATCH /books/{serial_number}/status – update borrow status

**Borrow a book** (`borrower_card` is required):

```bash
curl -X PATCH http://localhost:8000/books/000001/status \
  -H "Content-Type: application/json" \
  -d '{"is_borrowed": true, "borrower_card": "042000"}'
```

**Return a book:**

```bash
curl -X PATCH http://localhost:8000/books/000001/status \
  -H "Content-Type: application/json" \
  -d '{"is_borrowed": false}'
```

**Request body:**

| Field | Type | Rules |
|-------|------|-------|
| `is_borrowed` | bool | Required |
| `borrower_card` | string | Required when `is_borrowed` is `true`; exactly 6 digits |

Response `200` – the updated book object.  
Response `404` – book not found.  
Response `422` – validation error.

---

### GET /health – health check

```bash
curl http://localhost:8000/health
```

Response `200`:
```json
{"status": "ok"}
```

---

## Data Model

```
Table: books
┌────────────────┬──────────────────────────┬──────────┬─────────────────────────────┐
│ Column         │ Type                     │ Nullable │ Notes                       │
├────────────────┼──────────────────────────┼──────────┼─────────────────────────────┤
│ serial_number  │ VARCHAR(6) PK            │ No       │ Six-digit, e.g. "000042"    │
│ title          │ VARCHAR(255)             │ No       │ Book title                  │
│ author         │ VARCHAR(255)             │ No       │ Author full name            │
│ is_borrowed    │ BOOLEAN DEFAULT false    │ No       │ True = currently on loan    │
│ borrowed_at    │ TIMESTAMPTZ              │ Yes      │ NULL when available         │
│ borrowed_by    │ VARCHAR(6)               │ Yes      │ Borrower's library card no. │
└────────────────┴──────────────────────────┴──────────┴─────────────────────────────┘
```

---

## Project Structure

```
recruitment-task/
├── app/
│   ├── __init__.py
│   ├── config.py        ← environment variables (pydantic-settings)
│   ├── database.py      ← SQLAlchemy engine, session factory, get_db
│   ├── models.py        ← ORM model Book (books table)
│   ├── schemas.py       ← Pydantic schemas (BookCreate, BookResponse, BorrowUpdate)
│   ├── crud.py          ← DB operations (get_all, get_one, create, delete, update_status)
│   ├── main.py          ← FastAPI app, lifespan, router registration
│   └── routers/
│       └── books.py     ← HTTP endpoints /books
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_create_books_table.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   HTTP Client                        │
│         (curl, Postman, Swagger UI at /docs)        │
└──────────────────────┬──────────────────────────────┘
                       │  HTTP/JSON
┌──────────────────────▼──────────────────────────────┐
│               FastAPI Application                    │
│                                                      │
│  main.py        ← entry point, lifespan hooks       │
│  routers/       ← HTTP route definitions            │
│  books.py       ← GET/POST/DELETE/PATCH /books      │
│  schemas.py     ← request validation & serialisation│
│  crud.py        ← database operations               │
│  models.py      ← ORM model (books table)           │
│  database.py    ← engine + session factory          │
│  config.py      ← settings from env vars            │
└──────────────────────┬──────────────────────────────┘
                       │  SQLAlchemy / psycopg2
┌──────────────────────▼──────────────────────────────┐
│               PostgreSQL 16                          │
│               Table: books                           │
└─────────────────────────────────────────────────────┘
```

The codebase is split into clear layers:

| Layer | Files | Responsibility |
|-------|-------|----------------|
| HTTP | `routers/books.py` | Parse requests, return HTTP responses and error codes |
| Logic / validation | `schemas.py`, `crud.py` | Validate formats, cross-field rules, execute DB queries |
| Data | `models.py`, `database.py` | ORM definitions, session lifecycle (one session per request) |
| Configuration | `config.py` | All environment-specific settings in one place |

---

## Technology Stack

| Technology | Version | Role |
|------------|---------|------|
| Python | 3.12 | Runtime |
| FastAPI | 0.111 | REST framework with auto OpenAPI documentation |
| Uvicorn | 0.29 | ASGI server |
| SQLAlchemy | 2.0 | ORM with typed columns (`Mapped`) |
| Alembic | 1.13 | Database schema migrations |
| Pydantic v2 | (via FastAPI) | Data validation and serialisation |
| pydantic-settings | 2.2 | Configuration from environment variables |
| PostgreSQL | 16 | Database |
| psycopg2-binary | 2.9 | PostgreSQL adapter for Python |
| Docker / Compose | 26 / 2.27 | Containerisation |

---

## Configuration

The application is configured via environment variables (defined in `docker-compose.yml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+psycopg2://library:library@db:5432/library` | SQLAlchemy connection string |
| `DEBUG` | `false` | Enable debug mode |

---

## Database Migrations (Alembic)

For development, the application creates tables automatically on startup using `Base.metadata.create_all`. Alembic is set up for production environments where schema changes must be tracked and applied safely without data loss.

Run migrations against a running container:

```bash
docker compose exec api alembic upgrade head
```

---

## Possible Improvements

In a full production project the following could be added:

1. **Automated tests** – pytest + httpx (`TestClient`) with an in-memory SQLite database or a dedicated PostgreSQL test container
2. **Pagination** for `GET /books` (`limit` and `offset` query parameters)
3. **Authentication** – JWT or OAuth2 (intentionally omitted per task specification)
4. **Structured logging** – e.g. `structlog`
5. **Rate limiting** – e.g. `slowapi`
6. **CI/CD** – GitHub Actions: run tests + build Docker image + push to registry
7. **Migration as a startup step** – an entrypoint script that runs `alembic upgrade head` before starting Uvicorn
