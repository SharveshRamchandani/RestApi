# Project Approach & Data Sources

## 1. Goal
The system identifies popular n8n workflows by aggregating signals from three key platforms: YouTube, Discourse (Forum), and Google Trends. The goal is to provide a "popularity score" that helps users discover high-impact automation ideas.

## 2. Platform Strategy & Data Sources

### Youtube
- **Fetcher**: `ingest/fetchers/youtube.py`
- **Signals**: View count, Likes, Comments, Engagement Ratios.
- **Approach**: We search for keywords like "n8n tutorial", "n8n automation", and "n8n workflow".
- **Canonicalization**: Video titles are normalized to group similar topics.

### Discourse (n8n Forum)
- **Fetcher**: `ingest/fetchers/discourse.py`
- **Signals**: Replies, Likes, Views, Contributors.
- **Approach**: The forum is the heart of the community. We fetch "Latest" topics and filter for high-activity threads.
- **Value**: High reply counts often indicate complex or widely-needed workflows (problem-solving).

### Google Trends
- **Fetcher**: `ingest/fetchers/trends.py`
- **Signals**: Search Interest Score (0-100).
- **Approach**: We track specific keywords ("n8n", "n8n workflow") to gauge general market interest over time.
- **Usage**: Provides a baseline "trend score" to augment specific workflow data.

## 3. Technical Architecture

### Ingestion Pipeline
We chose **Celery** with **Redis** for the extraction layer because:
1.  **Async & Scalable**: Fetching from external APIs is IO-bound. Celery workers can scale horizontally.
2.  **Ratelimiting**: Celery makes it easy to handle API rate limits (e.g., YouTube quota).
3.  **Scheduling**: **Celery Beat** handles the Cron requirements (Daily/Weekly) natively.

### Database Upgrade
- **PostgreSQL**: Chosen for reliability and relational data integrity.
- **AsyncPG**: We upgraded the database driver to `asyncpg` to allow the FastAPI application to handle high concurrency without blocking on database I/O.

### API Layer
- **FastAPI**: Chosen for speed (Starlette) and automatic documentation (Swagger UI).
- **Pydantic**: Ensures strict schema validation for the "Evidence" JSON objects.

## 4. Automation
The system runs entirely on Docker Compose.
- **beat** service: Triggers tasks on a schedule.
  - `fetch_youtube`: Daily (Midnight)
  - `fetch_forum`: Daily (00:30)
  - `fetch_trends`: Weekly (Mondays)

## 5. Scoring Logic
Popularity is currently a raw count aggregation. Future versions will implement a weighted algorithm:
`Score = (Views * 0.1) + (Likes * 2) + (Replies * 5) + (TrendScore * 10)`
