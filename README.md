# n8n Workflow Popularity System

Automated system to identify and track the popularity of n8n workflows by aggregating signals from YouTube, Discourse, and Google Trends. This project provides a "popularity score" to help users discover high-impact automation ideas.

## Project Structure

```
n8n-popularity/
├─ ingest/           # Celery workers & fetchers
│  ├─ fetchers/      # External API clients (YouTube, Discourse, Google Trends)
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

## Features

- **Multi-Source Ingestion**: Fetches data from YouTube (tutorials), Discourse (community discussions), and Google Trends (search interest).
- **Asynchronous Processing**: Uses Celery workers with Redis for scalable data fetching.
- **Data Persistence**: Stores normalized data in PostgreSQL.
- **Search & Analytics**: Integrates OpenSearch for full-text search capabilities.
- **REST API**: FastAPI service to expose workflow data and popularity scores.
- **Automated Scheduling**: periodic tasks handled by Celery Beat (Daily/Weekly).

## Data Signals & Scoring

The system aggregates signals to calculate a popularity score:

1.  **YouTube**: View count, Likes, Comments.
    - *Keywords*: "n8n tutorial", "n8n automation", "n8n workflow".
2.  **Discourse**: Replies, Likes, Views.
    - *Focus*: High-activity threads indicating complex or widely-needed workflows.
3.  **Google Trends**: Search Interest Score (0-100).
    - *Usage*: Provides a baseline market interest trend.

**Scoring Logic (Planned):**
`Score = (Views * 0.1) + (Likes * 2) + (Replies * 5) + (TrendScore * 10)`

## Quick Start

### Prerequisites
- Docker & Docker Compose
- YouTube API Key

### 1. Setup Environment
Copy the example environment file and configure your keys:
```bash
cp .env.example .env
```
Update `.env` with your `YOUTUBE_API_KEY`.

### 2. Run with Docker Compose
Build and start all services (API, Worker, Beat, Postgres, Redis, OpenSearch):
```bash
docker-compose --env-file .env -f infra/docker-compose.yml up -d --build
```

- **API**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`
- **Dashboards**: OpenSearch Dashboards (if enabled) at `http://localhost:5601`

### 3. Trigger Ingestion
Manually trigger a task if needed (tasks run automatically via schedule):
```bash
docker-compose -f infra/docker-compose.yml exec worker python -c "from ingest.tasks import task_fetch_youtube; print(task_fetch_youtube.apply(args=('US',)).get())"
```

## Development

### Running Tests
```bash
pytest tests/
```

### API Endpoints
- `GET /workflows`: List workflows with filtering (platform, country) and sorting.
- `GET /workflows/{id}`: Detailed view of a workflow.
- `POST /workflows/import`: Internal bulk ingestion endpoint.
- `GET /metrics`: Prometheus metrics.

## License
[License]
