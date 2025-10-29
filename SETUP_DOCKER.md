# Docker Setup Guide

This guide provides complete instructions for running Continuum using Docker and Docker Compose.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 1.29+ installed
- 4GB RAM available
- 10GB disk space

## Quick Start

```bash
# Navigate to the project directory
cd continuum

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f continuum

# Check service health
docker-compose ps

# Access services:
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
# - Jaeger: http://localhost:16686
# - PostgreSQL: localhost:5432 (continuum_user/continuum_pass)
# - Redis: localhost:6379
```

## Service Architecture

### Continuum API Container

Main application container running FastAPI.

**Configuration**:
- Port: 8000
- Health check: /health
- Restart policy: Always
- Dependencies: postgres, redis

**Environment Variables**:
```
DATABASE_URL=postgresql://continuum_user:continuum_pass@postgres:5432/continuum
REDIS_URL=redis://redis:6379/0
CACHE_TYPE=redis
DEBUG=false
LOG_LEVEL=INFO
```

**Volume Mounts**:
- Source code: `/app` (for hot-reload during development)
- Logs: Named volume `continuum-logs`

### PostgreSQL Container

PostgreSQL 15 Alpine Linux database.

**Configuration**:
- Port: 5432
- User: continuum_user
- Password: continuum_pass
- Database: continuum
- Health check: pg_isready

**Volume Mounts**:
- Data: Named volume `postgres-data` (10GB persistent)
- Initialization scripts: ConfigMap mounted at `/docker-entrypoint-initdb.d/`

**Backup**:
```bash
# Create backup
docker-compose exec postgres pg_dump -U continuum_user continuum > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U continuum_user continuum < backup.sql
```

### Redis Container

Redis 7 Alpine Linux cache.

**Configuration**:
- Port: 6379
- No authentication (for local development)
- Persistence: RDB snapshots

**Volume Mounts**:
- Data: Named volume `redis-data` (5GB)

**Clear Cache**:
```bash
docker-compose exec redis redis-cli FLUSHALL
```

### Prometheus Container

Prometheus metrics collection and alerting.

**Configuration**:
- Port: 9090
- Scrape interval: 15 seconds
- Data retention: 30 days

**Volume Mounts**:
- Configuration: ConfigMap at `/etc/prometheus/prometheus.yml`
- Alert rules: ConfigMap at `/etc/prometheus/alert_rules.yml`
- Data: Named volume `prometheus-data`

**Access Dashboard**:
```
http://localhost:9090
```

**Example Queries**:
```
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# P95 response time
histogram_quantile(0.95, http_request_duration_seconds)

# Cache hit rate
cache_hits_total / (cache_hits_total + cache_misses_total)
```

### Grafana Container

Grafana dashboards for visualization.

**Configuration**:
- Port: 3000
- Admin user: admin
- Admin password: admin

**Initial Setup**:
1. Access http://localhost:3000
2. Log in with admin/admin
3. Change admin password
4. Add data source: Prometheus (http://prometheus:9090)
5. Import dashboards or create custom ones

**Pre-configured Dashboards**:
- Node exporter metrics (if available)
- Prometheus internal metrics
- Custom Continuum metrics (create using Grafana UI)

### Jaeger Container

Distributed tracing visualization.

**Configuration**:
- UI Port: 16686
- Agent Port (UDP): 6831
- Collector Port (HTTP): 14268

**Access UI**:
```
http://localhost:16686
```

**View Traces**:
1. Select service from dropdown
2. Choose operation
3. Adjust filters and sampling
4. View distributed trace waterfall

## Development Workflow

### Enable Hot-Reload

Code changes are automatically reflected (source is volume-mounted):

```bash
# Make code changes, restart the service
docker-compose restart continuum

# Or let it auto-reload if using FastAPI reload
```

### Running Tests in Docker

```bash
# Run tests in container
docker-compose exec continuum pytest tests/ -v

# With coverage
docker-compose exec continuum pytest tests/ --cov=. --cov-report=term
```

### Database Migrations

```bash
# Connect to database
docker-compose exec postgres psql -U continuum_user continuum

# Run migrations
docker-compose exec continuum alembic upgrade head
```

### Debugging

```bash
# Access container shell
docker-compose exec continuum /bin/bash

# View logs with timestamps
docker-compose logs --timestamps continuum

# View logs for specific service
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f
```

## Production Considerations

### Resource Limits

Configure in docker-compose.yml:

```yaml
services:
  continuum:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Networking

By default, services communicate via Docker network bridge:
- Service names are DNS resolvable
- Traffic is isolated from host network

### Secrets Management

For production, use Docker Secrets or .env files:

```bash
# Create .env file (never commit)
POSTGRES_PASSWORD=securepassword123
REDIS_PASSWORD=anotherpassword456
OPENAI_API_KEY=your-api-key-here

# Load in docker-compose.yml
env_file:
  - .env
```

### Database Backups

```bash
# Automated daily backup script
#!/bin/bash
timestamp=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U continuum_user continuum > "backups/backup_${timestamp}.sql"
```

## Common Issues & Solutions

### Issue: PostgreSQL fails to start

**Solution**:
```bash
# Remove volume and restart
docker-compose down -v
docker-compose up -d postgres

# Wait for initialization
sleep 30
docker-compose up -d
```

### Issue: Port already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Map to different port
```

### Issue: Redis connection refused

**Solution**:
```bash
# Verify Redis is running
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Test connection
docker-compose exec redis redis-cli ping
```

### Issue: Out of disk space

**Solution**:
```bash
# Check volume usage
docker system df

# Clean up unused volumes
docker volume prune

# Remove service volumes selectively
docker-compose down -v
```

## Performance Tuning

### Increase Cache Size

```yaml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Database Optimization

```bash
# Connect to database
docker-compose exec postgres psql -U continuum_user continuum

# Create indexes
CREATE INDEX idx_explorations_created ON explorations(created_at DESC);
CREATE INDEX idx_nodes_concept ON nodes(concept);

# Analyze query plans
EXPLAIN ANALYZE SELECT * FROM explorations LIMIT 10;
```

### Connection Pooling

Configure in settings:

```python
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=40
SQLALCHEMY_POOL_PRE_PING=True
```

## Monitoring

### View Metrics

```bash
# Query Prometheus from host
curl http://localhost:9090/api/v1/query?query=up

# Export metrics from API
curl http://localhost:8000/metrics
```

### Create Alerts

Edit `alert_rules.yml` to add custom alerts:

```yaml
- alert: CustomAlert
  expr: custom_metric > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Custom alert triggered"
```

## Cleanup

```bash
# Stop services (keep volumes)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove everything including volumes
docker-compose down -v

# Remove unused Docker resources
docker system prune -a
```

## Next Steps

1. Set up monitoring dashboards in Grafana
2. Configure log aggregation (ELK stack optional)
3. Set up automated backups
4. Plan scaling strategy
5. Deploy to Kubernetes for production
