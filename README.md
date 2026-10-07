# tailored_test_task

FastAPI service that transforms and caches string payloads in PostgreSQL. Built from [fastapi_template](https://github.com/s3rius/fastapi-template).

Given two lists of strings, each value is passed through a transformer (uppercased). Results are interleaved and stored so repeated inputs reuse the cached output instead of calling the transformer again.

## Features

- **Caching API** — `POST /payload` and `GET /payload/{id}`
- **PostgreSQL persistence** via SQLAlchemy (async) and Alembic migrations
- **CLI client** (`cache-cli`) to create and fetch payloads against a running server

### Example

Request:

```json
{
  "list_1": ["hello", "world"],
  "list_2": ["foo", "bar"]
}
```

Response:

```json
{
  "id": 1,
  "output": "HELLO, FOO, WORLD, BAR"
}
```

## UV

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync --locked
uv run -m tailored_test_task
```

This starts the server on the configured host (default `127.0.0.1:8000`).

Swagger docs are available at `/api/docs`.

## Docker

Start the API and PostgreSQL with:

```bash
docker compose up --build
```

This exposes the app on port 8000, mounts the current directory, and enables autoreload.

Rebuild whenever you change `uv.lock` or `pyproject.toml`:

```bash
docker compose build
```

## API

| Method | Path            | Description                                      |
|--------|-----------------|--------------------------------------------------|
| `POST` | `/payload`      | Transform and cache two input lists              |
| `GET`  | `/payload/{id}` | Return a previously cached payload by id         |
| `GET`  | `/api/health`   | Health check                                     |
| `POST` | `/api/echo`     | Echo endpoint (template sample)                  |

OpenAPI / Swagger: `/api/docs`

## CLI

After `uv sync`, the `cache-cli` entry point talks to a running server.

```bash
# Inline JSON
cache-cli --host http://localhost:8000 --json '{"list_1":["hello","world"],"list_2":["foo","bar"]}'

# From a file (or "-" for stdin)
cache-cli -i payload.json -o result.json

# Repeat create/read cycles
cache-cli -j '{"list_1":["a"],"list_2":["b"]}' -r 3
```

| Flag | Short | Description |
|------|-------|-------------|
| `--host` | | Base URL of the service (default `http://localhost:8000`) |
| `--json` | `-j` | Inline JSON payload |
| `--input` | `-i` | Input file path, or `-` for stdin |
| `--output` | `-o` | Output file path, or `-` for stdout |
| `--repeat` | `-r` | Number of create/read iterations (default `1`) |

Exactly one of `--json` or `--input` is required.

## Project structure

```
tailored_test_task/
├── cli/                          # cache-cli client
│   ├── client.py                 # HTTP client for /payload
│   ├── main.py                   # CLI entry point
│   └── settings.py               # CLI arguments / settings
├── tailored_test_task/
│   ├── __main__.py               # Startup script (uvicorn)
│   ├── settings.py               # App configuration
│   ├── db/
│   │   ├── crud/                 # Data access for cached rows
│   │   ├── models/               # SQLAlchemy models
│   │   └── migrations/           # Alembic migrations
│   ├── external_services/
│   │   └── transformer.py        # String transformer (uppercase)
│   └── web/
│       ├── application.py        # FastAPI app factory
│       ├── lifespan.py           # Startup / shutdown hooks
│       └── api/
│           ├── caching/          # Payload cache endpoints
│           ├── echo/             # Sample echo router
│           └── monitoring/       # Health check
└── tests/
    ├── cached/                   # Caching unit / integration tests
    └── ...
```

## Configuration

Configure the app with environment variables (or a `.env` file in the project root).

All app variables use the `TAILORED_TEST_TASK_` prefix. For example, `port` in `settings.py` maps to `TAILORED_TEST_TASK_PORT`.

Copy [`.env.sample`](.env.sample) to `.env` and fill in the values:

```bash
cp .env.sample .env
```

See [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for more on `BaseSettings`.

## Pre-commit

```bash
pre-commit install
```

Configured via `.pre-commit-config.yaml`. By default it runs:

- **mypy** — type checking
- **ruff** — linting

More info: https://pre-commit.com/

## Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Upgrade up to a specific revision
alembic upgrade "<revision_id>"
```

### Reverting migrations

```bash
# Downgrade to a revision
alembic downgrade <revision_id>

# Revert everything
alembic downgrade base
```

### Generating migrations

```bash
# Autodetect model changes
alembic revision --autogenerate -m "description"

# Empty migration file
alembic revision -m "description"
```

## Running tests

With Docker:

```bash
docker compose run --build --rm api pytest -vv .
docker compose down
```

Locally (with a test database available):

```bash
pytest -vv .
```
