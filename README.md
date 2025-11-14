# Analytics Service

A high-performance analytics service for capturing and reporting website events with asynchronous processing.

## Architecture

The service is composed of three main components:

1. **Ingestion API**: FastAPI endpoint that receives events and queues them in Redis
2. **Processor**: Background worker that processes events from Redis and stores them in PostgreSQL
3. **Reporting API**: Provides aggregated analytics data from the database

### Architecture Decision: Asynchronous Processing with Redis

We chose to implement asynchronous processing using Redis as a message queue for several reasons:

- **Decoupling**: Separates the API from the data processing, allowing each to scale independently
- **Resilience**: If the database goes down, events are still queued in Redis and will be processed when the database is back up
- **Performance**: The API can respond quickly by just queuing events rather than waiting for database writes
- **Scalability**: Multiple processor instances can consume from the queue in parallel

### Database Schema

```mermaid
erDiagram
    EVENTS {
        int id PK
        string site_id
        string event_type
        string path
        string user_id
        timestamp event_ts
        timestamp ingested_at
    }
    
    EVENTS {
        index idx_site_id "site_id"
        index idx_user_id "user_id"
        index idx_event_ts "event_ts"
    }
```

## 🚀 Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd analytics-backend
   ```

2. **Build and start services**
   ```bash
   docker-compose up --build -d
   ```

3. **Verify services are running**
   ```bash
   docker-compose ps
   ```
   You should see all services (ingestion, processor, reporting, redis, postgres) with a status of "Up"

4. **Access the APIs**
   - Ingestion API: http://localhost:8000/docs
   - Reporting API: http://localhost:8001/docs

## 📚 API Usage

### Ingest an Event

```bash
# Using curl
curl -X 'POST' \
  'http://localhost:8000/event' \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id": "test-site",
    "event_type": "page_view",
    "path": "/home",
    "user_id": "user123",
    "timestamp": "2025-11-14T13:30:01Z"
  }'

# Using PowerShell
$body = @{
    site_id = "test-site"
    event_type = "page_view"
    path = "/home"
    user_id = "user123"
    timestamp = "2025-11-14T13:30:01Z"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/event" -Method Post -Body $body -ContentType "application/json"
```

### Get Analytics

```bash
# Get all-time stats for a site
curl 'http://localhost:8001/stats?site_id=test-site'

# Get stats for a specific date (YYYY-MM-DD)
curl 'http://localhost:8001/stats?site_id=test-site&date=2025-11-14'

# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8001/stats?site_id=test-site" -Method Get
```

### Example Response

```json
{
  "site_id": "test-site",
  "date": "2025-11-14",
  "total_views": 42,
  "unique_users": 15,
  "top_paths": [
    {"path": "/home", "views": 25},
    {"path": "/products", "views": 10},
    {"path": "/about", "views": 7}
  ]
}
```

## 🛠 Development

### Running Tests
```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis server hostname | `redis` |
| `REDIS_PORT` | Redis server port | `6379` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://analytics:analytics123@postgres:5432/analytics_db` |

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.