# n8n Workflow Popularity System

Automated system to track popularity of n8n workflows across YouTube, Discourse, and Google. Includes ingestion workers, data normalization, and a REST API.

## Project Structure

```
n8n-popularity/
├─ ingest/           # Celery workers & fetchers
│  ├─ fetchers/      # External API clients (YouTube, etc.)
│  ├─ tasks.py       # Celery task definitions
│  └─ normalize.py   # Data processing logic
├─ api/              # FastAPI application
│  ├─ models/        # Pydantic schemas
│  ├─ db/            # SQLAlchemy models & config
│  └─ main.py        # API endpoints
├─ infra/            # Infrastructure config (Docker)
├─ migrations/       # Database migrations (SQL/Alembic)
└─ tests/            # Unit & Integration tests
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local dev)

### 1. Setup Environment
Copy the example environment file and fill in API keys:
```bash
cp .env.example .env
```
Key variables:
- `YOUTUBE_API_KEY`: Required for YouTube fetcher.
- `DATABASE_URL`: Postgres connection string (defaults set for Docker).

### 2. Run with Docker Compose
Build and start all services (API, Worker, Beat, Postgres, Redis):
```bash
docker-compose --env-file .env -f infra/docker-compose.yml up -d --build
```
- **API**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Automation**: The `beat` service starts automatically and runs tasks daily/weekly.

### 3. Initialize Database
You can run the provided SQL schema or use Alembic (if configured):
```bash
# Enter the postgres container
docker-compose -f infra/docker-compose.yml exec postgres psql -U postgres -d n8n_pop -f /migrations/schema.sql
# (Note: You might need to mount the migrations folder or run psql from host)
```
Alternatively, the API attempts to create tables on startup for this MVP.

### 4. Trigger Ingestion
Manually trigger a YouTube fetch task:
```bash
docker-compose -f infra/docker-compose.yml exec worker python -c "from ingest.tasks import task_fetch_youtube; print(task_fetch_youtube.apply(args=('US',)).get())"
```

## API Endpoints

- **GET /health**: Status check.
- **GET /workflows**: List workflows with filters (`platform`, `country`, `sort`).
- **GET /workflows/{id}**: Get details for a specific workflow.
- **POST /workflows/import**: Internal Bulk Ingest.

## Development

### Running Tests
```bash
pytest tests/
```

### Adding a new Fetcher
1. Create `ingest/fetchers/new_source.py`
2. Implement fetch logic returning canonical dicts.
3. Add task in `ingest/tasks.py`.

## License
[License]