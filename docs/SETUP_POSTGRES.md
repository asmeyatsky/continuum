# PostgreSQL Setup Guide

This guide shows how to set up PostgreSQL persistence for the Continuum system.

## Prerequisites

- PostgreSQL 12+ installed locally or available remotely
- Python 3.9+ with venv activated
- Continuum dependencies installed

## Quick Start (Local Development)

### 1. Install PostgreSQL

**macOS (using Homebrew)**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian**:
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**:
- Download from https://www.postgresql.org/download/windows/
- Run installer and follow prompts

### 2. Create Database and User

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE continuum;

# Create user
CREATE USER continuum_user WITH PASSWORD 'secure_password';

# Grant privileges
ALTER ROLE continuum_user SET client_encoding TO 'utf8';
ALTER ROLE continuum_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE continuum_user SET default_transaction_deferrable TO on;
ALTER ROLE continuum_user SET default_time_zone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE continuum TO continuum_user;

# Exit psql
\q
```

### 3. Update Environment Variables

Create or update `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql://continuum_user:secure_password@localhost:5432/continuum
USE_PERSISTENT_GRAPH=true

# Optional: Database connection pooling
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

### 4. Install Python Dependencies

```bash
pip install psycopg2-binary sqlalchemy alembic
```

Or update requirements.txt:
```bash
pip install -r requirements.txt
```

### 5. Create Tables

```bash
python3 -c "
from database.database import get_db_manager
db = get_db_manager()
db.create_all()
print('✅ All tables created successfully')
"
```

### 6. Verify Connection

```bash
python3 -c "
from database.database import get_db_manager
db = get_db_manager()
session = db.get_session()
print('✅ Database connection successful')
session.close()
"
```

## Using PostgreSQL in Your Application

### Option 1: Switch Knowledge Graph Engine

Update your application initialization code:

```python
from config.settings import settings
from database.database import get_db_manager

if settings.USE_PERSISTENT_GRAPH:
    # Use PostgreSQL-backed graph
    from knowledge_graph.postgres_engine import PostgreSQLKnowledgeGraphEngine
    db = get_db_manager()
    session = db.get_session()
    knowledge_graph = PostgreSQLKnowledgeGraphEngine(session)
else:
    # Use in-memory graph (default)
    from knowledge_graph.engine import InMemoryKnowledgeGraphEngine
    knowledge_graph = InMemoryKnowledgeGraphEngine()
```

### Option 2: Use Repositories Directly

```python
from database.database import get_db_manager
from database.repositories import (
    ConceptNodeRepository,
    GraphEdgeRepository,
    ExplorationRepository,
    FeedbackRepository
)

db = get_db_manager()
session = db.get_session()

# Create repositories
node_repo = ConceptNodeRepository(session)
edge_repo = GraphEdgeRepository(session)
exploration_repo = ExplorationRepository(session)
feedback_repo = FeedbackRepository(session)

# Use repositories
node = node_repo.get_by_id("node_id")
explorations = exploration_repo.list_recent(limit=10)
```

## Database Migrations with Alembic

### Initialize Alembic (First Time Only)

```bash
alembic init migrations
```

### Create Migration

```bash
# After changing models, auto-generate migration
alembic revision --autogenerate -m "Add new column"

# Manual migration
alembic revision -m "Create custom migration"
```

### Run Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade ae1027a6acf

# Downgrade one version
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Production Deployment

### Connection Pooling

For production, configure connection pooling:

```env
DATABASE_URL=postgresql://continuum_user:password@prod-db.example.com:5432/continuum
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_TIMEOUT=30
```

### SSL Connections

For secure connections:

```env
DATABASE_URL=postgresql://continuum_user:password@prod-db.example.com:5432/continuum?sslmode=require
```

### Docker Postgres

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: continuum
      POSTGRES_USER: continuum_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U continuum_user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Run with Docker Compose:
```bash
docker-compose up -d postgres
# Wait for health check to pass
docker-compose logs postgres
```

## Troubleshooting

### Connection Refused
```
Error: could not connect to server: Connection refused
```

**Solution**: Ensure PostgreSQL is running
```bash
# Check service status
pg_isready -h localhost -p 5432

# Restart service
brew services restart postgresql@15
# or
sudo systemctl restart postgresql
```

### Authentication Failed
```
Error: FATAL: password authentication failed for user
```

**Solution**: Verify credentials in DATABASE_URL and PostgreSQL user password

### Database Does Not Exist
```
Error: database "continuum" does not exist
```

**Solution**: Create database
```bash
psql -U postgres -c "CREATE DATABASE continuum;"
```

### Permission Denied
```
Error: permission denied for schema public
```

**Solution**: Grant privileges to user
```bash
psql -U postgres -d continuum -c "GRANT ALL ON SCHEMA public TO continuum_user;"
```

## Switching Between In-Memory and PostgreSQL

### Disable PostgreSQL (Use In-Memory)
```env
USE_PERSISTENT_GRAPH=false
DATABASE_URL=sqlite:///./continuum.db
```

### Enable PostgreSQL
```env
USE_PERSISTENT_GRAPH=true
DATABASE_URL=postgresql://user:password@localhost:5432/continuum
```

## Performance Tips

1. **Create Indexes**: Most common queries have indexes already
   ```sql
   CREATE INDEX idx_concept_nodes_concept ON concept_nodes(concept);
   ```

2. **Use Connection Pooling**: Configure pool size based on workload

3. **Analyze Queries**: Use `EXPLAIN ANALYZE`
   ```sql
   EXPLAIN ANALYZE SELECT * FROM concept_nodes WHERE concept LIKE '%AI%';
   ```

4. **Backup Data**:
   ```bash
   pg_dump continuum > backup.sql
   ```

5. **Restore Data**:
   ```bash
   psql continuum < backup.sql
   ```

## Testing with PostgreSQL

Run tests with PostgreSQL backend:

```bash
# Set test database
export DATABASE_URL=postgresql://continuum_user:password@localhost:5432/continuum_test

# Create test database
psql -U postgres -c "CREATE DATABASE continuum_test;"

# Run tests
pytest tests/ -v
```

## Next Steps

- Set up distributed tracing with OpenTelemetry
- Configure Redis caching layer
- Implement real web search integration
- Deploy to production with proper backups

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [psycopg2 Driver](https://www.psycopg.org/)
