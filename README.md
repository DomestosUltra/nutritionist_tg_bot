# Nutritionist Telegram Bot

## Database Integration

### PostgreSQL Setup

1. Environment variables needed in `.env`:
   ```
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=password
   POSTGRES_DB=nutritionist_bot
   ```

2. Database migrations:
   ```bash
   # Generate a new migration
   alembic revision --autogenerate -m "Create user interactions table"
   
   # Apply migrations
   alembic upgrade head
   ```

### User Interactions Tracking

The system now tracks user interactions in the PostgreSQL database:
- User ID
- Username 
- User message/query
- Bot response

## Running the Application

```bash
# Install dependencies
poetry install

# Create docker network
docker network create network

# Run docker containers
docker-compose -f ci-cd-files/docker-compose.yml up -d

# Create database tables
alembic upgrade head
```