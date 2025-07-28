# JobZee Local Development Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Setup](#manual-setup)
4. [Environment Configuration](#environment-configuration)
5. [Running Services](#running-services)
6. [Development Workflow](#development-workflow)
7. [Troubleshooting](#troubleshooting)
8. [Useful Commands](#useful-commands)

## Prerequisites

Before setting up JobZee locally, ensure you have the following installed:

### Required Software

- **Docker** (version 20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0+) - [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git** - [Install Git](https://git-scm.com/downloads)

### Optional Software (for development)

- **Go** (version 1.21+) - [Install Go](https://golang.org/doc/install)
- **Node.js** (version 18+) - [Install Node.js](https://nodejs.org/)
- **Python** (version 3.9+) - [Install Python](https://www.python.org/downloads/)

### API Keys

- **OpenAI API Key** - [Get OpenAI API Key](https://platform.openai.com/api-keys)
- **GitHub Token** (optional) - [Create GitHub Token](https://github.com/settings/tokens)

### System Requirements

- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: At least 10GB free space
- **CPU**: Multi-core processor recommended

## Quick Start

### Method 1: Automated Setup (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/jobzee.git
   cd jobzee
   ```

2. **Set your API keys**

   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   export GITHUB_TOKEN="your-github-token-here"  # Optional
   export JWT_SECRET="your-jwt-secret-here"      # Optional
   ```

3. **Run the automated setup script**

   ```bash
   chmod +x jobzee-infra/scripts/local-setup.sh
   ./jobzee-infra/scripts/local-setup.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8080
   - MinIO Console: http://localhost:9001
   - Grafana: http://localhost:3001 (admin/admin)
   - Adminer (Database): http://localhost:8087

### Method 2: Docker Compose Only

1. **Clone and navigate to the repository**

   ```bash
   git clone https://github.com/your-org/jobzee.git
   cd jobzee
   ```

2. **Set environment variables**

   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   export GITHUB_TOKEN="your-github-token-here"  # Optional
   export JWT_SECRET="your-jwt-secret-here"      # Optional
   ```

3. **Start all services**

   ```bash
   docker-compose up -d
   ```

4. **Wait for services to be ready** (2-3 minutes)
   ```bash
   docker-compose ps
   ```

## Manual Setup

If you prefer to set up services individually or need to customize the configuration:

### Step 1: Infrastructure Services

1. **Start database and caching services**

   ```bash
   docker-compose up -d postgres redis
   ```

2. **Start message queue services**

   ```bash
   docker-compose up -d zookeeper kafka
   ```

3. **Start storage services**

   ```bash
   docker-compose up -d minio qdrant
   ```

4. **Verify infrastructure is running**
   ```bash
   docker-compose ps
   ```

### Step 2: Backend Services

1. **Start backend microservices**

   ```bash
   docker-compose up -d api-service job-service candidate-service agent-service
   ```

2. **Check backend health**
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8081/health
   curl http://localhost:8082/health
   curl http://localhost:8083/health
   ```

### Step 3: Frontend and Agents

1. **Start frontend application**

   ```bash
   docker-compose up -d frontend
   ```

2. **Start AI agents**

   ```bash
   docker-compose up -d job-finder-agent candidate-finder-agent
   ```

3. **Start MCP tools service**
   ```bash
   docker-compose up -d mcp-tools
   ```

### Step 4: Monitoring Services

1. **Start monitoring stack**

   ```bash
   docker-compose up -d prometheus grafana
   ```

2. **Start development tools**
   ```bash
   docker-compose up -d adminer
   ```

## Environment Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# GitHub Configuration (Optional)
GITHUB_TOKEN=your_github_token_here

# JWT Configuration
JWT_SECRET=your-jwt-secret-change-in-production

# Email Service (Optional)
EMAIL_SERVICE_API_KEY=your_email_service_key

# Calendar Service (Optional)
CALENDAR_SERVICE_API_KEY=your_calendar_service_key
```

### Service-Specific Configuration

#### Backend Services

Each backend service can be configured via environment variables:

```bash
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka Configuration
KAFKA_BROKERS=kafka:9092

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

#### Agent Services

Agent services require specific configuration:

```bash
# Agent Configuration
AGENT_TYPE=job-finder
AGENT_PORT=8084
KAFKA_BROKERS=kafka:9092
VECTOR_DB_URL=http://qdrant:6333
OPENAI_API_KEY=your_openai_api_key
```

## Running Services

### Starting All Services

```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis kafka
docker-compose up -d api-service frontend
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop specific services
docker-compose stop api-service frontend

# Stop and remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api-service
docker-compose logs -f job-finder-agent

# View last 100 lines
docker-compose logs --tail=100 api-service
```

### Health Checks

```bash
# Check all service health
docker-compose ps

# Manual health checks
curl http://localhost:8080/health
curl http://localhost:3000
curl http://localhost:8084/health
curl http://localhost:8085/health
```

## Development Workflow

### Making Code Changes

1. **Stop the service you're modifying**

   ```bash
   docker-compose stop api-service
   ```

2. **Make your code changes**

3. **Rebuild and restart the service**
   ```bash
   docker-compose build api-service
   docker-compose up -d api-service
   ```

### Hot Reloading (Development Mode)

For development with hot reloading:

#### Backend (Go)

```bash
cd jobzee-backend
go run cmd/api/main.go
```

#### Frontend (Next.js)

```bash
cd jobzee-frontend
npm run dev
```

#### Agents (Python)

```bash
cd jobzee-agents
python job_finder_agent/main.py
```

### Database Migrations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d jobzee

# Run migrations (if any)
# docker-compose exec api-service ./migrate up
```

### Testing

```bash
# Run backend tests
cd jobzee-backend
go test ./...

# Run frontend tests
cd jobzee-frontend
npm test

# Run agent tests
cd jobzee-agents
pytest
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts

**Problem**: Services fail to start due to port conflicts
**Solution**:

```bash
# Check what's using the port
lsof -i :8080
lsof -i :3000

# Stop conflicting services or change ports in docker-compose.yml
```

#### 2. Insufficient Memory

**Problem**: Services fail to start or crash
**Solution**:

```bash
# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory: 8GB+

# Or reduce service resources in docker-compose.yml
```

#### 3. Database Connection Issues

**Problem**: Backend services can't connect to PostgreSQL
**Solution**:

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

#### 4. Kafka Connection Issues

**Problem**: Agents can't connect to Kafka
**Solution**:

```bash
# Check Kafka status
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Restart Kafka and Zookeeper
docker-compose restart zookeeper kafka
```

#### 5. OpenAI API Issues

**Problem**: Agents fail due to OpenAI API errors
**Solution**:

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check agent logs
docker-compose logs job-finder-agent

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### Debugging Commands

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs -f [service-name]

# Access service shell
docker-compose exec [service-name] /bin/bash

# Check network connectivity
docker-compose exec api-service ping postgres

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Performance Issues

#### High Memory Usage

```bash
# Monitor resource usage
docker stats

# Restart services to free memory
docker-compose restart

# Increase swap space (Linux)
sudo swapon --show
```

#### Slow Startup

```bash
# Use cached images
docker-compose pull

# Start services in parallel
docker-compose up -d --parallel

# Optimize Docker settings
# Settings > Resources > CPUs: 4+
# Settings > Resources > Memory: 8GB+
```

## Useful Commands

### Docker Compose Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View running services
docker-compose ps

# View service logs
docker-compose logs -f [service-name]

# Rebuild specific service
docker-compose build [service-name]

# Scale services
docker-compose up -d --scale api-service=3
```

### Database Commands

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d jobzee

# Backup database
docker-compose exec postgres pg_dump -U postgres jobzee > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres jobzee < backup.sql
```

### Monitoring Commands

```bash
# Check service health
curl http://localhost:8080/health

# View Prometheus metrics
curl http://localhost:9090/metrics

# Access Grafana
# http://localhost:3001 (admin/admin)

# Access MinIO console
# http://localhost:9001 (minioadmin/minioadmin)
```

### Development Commands

```bash
# Run tests
docker-compose exec api-service go test ./...
docker-compose exec frontend npm test
docker-compose exec job-finder-agent pytest

# Generate code
cd jobzee-protos && make generate

# Format code
docker-compose exec api-service go fmt ./...
docker-compose exec frontend npm run format
docker-compose exec job-finder-agent black .
```

### Cleanup Commands

```bash
# Remove all containers and networks
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a

# Remove specific volumes
docker volume rm jobzee_postgres_data jobzee_redis_data
```

## Next Steps

After successfully running JobZee locally:

1. **Explore the Application**

   - Visit http://localhost:3000
   - Register a new account
   - Try the AI agents

2. **Review Documentation**

   - [API Documentation](./api-documentation.md)
   - [Architecture Overview](./system-design.md)
   - [Integration Details](./integration-details.md)

3. **Start Developing**

   - Pick a component to work on
   - Set up your IDE
   - Join the development workflow

4. **Contribute**
   - Report issues
   - Submit pull requests
   - Join discussions

---

**Need Help?**

- Check the [Troubleshooting](#troubleshooting) section
- Review service logs: `docker-compose logs -f [service-name]`
- Open an issue on GitHub
- Join our community discussions
