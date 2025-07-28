# JobZee System - Deployment Guide

This guide provides comprehensive instructions for deploying the JobZee job application platform.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (v20.10+)
- **Git** (v2.30+)
- **OpenAI API Key** (for AI agents)
- **GitHub Token** (optional, for MCP tools)
- **At least 8GB RAM** and **20GB disk space**

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/jobzee.git
cd jobzee
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Optional: MCP Tools
GITHUB_TOKEN=your_github_token_here
EMAIL_SERVICE_API_KEY=your_email_service_key
CALENDAR_SERVICE_API_KEY=your_calendar_service_key

# Database (optional, defaults are used)
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee

# Redis (optional, defaults are used)
REDIS_HOST=redis
REDIS_PORT=6379

# Kafka (optional, defaults are used)
KAFKA_BROKERS=kafka:9092

# Vector Database (optional, defaults are used)
VECTOR_DB_URL=http://qdrant:6333
```

### 3. Start the System

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8080
- **Job Finder Agent**: http://localhost:8084
- **Candidate Finder Agent**: http://localhost:8085
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)
- **Grafana**: http://localhost:3001 (admin/admin)
- **Adminer**: http://localhost:8087
- **Prometheus**: http://localhost:9090

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Agents        │
│   (Next.js)     │◄──►│   (Go/Gin)      │◄──►│   (Python)      │
│   Port: 3000    │    │   Port: 8080    │    │   Ports: 8084-5 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   Qdrant        │
│   Port: 5432    │    │   Port: 6379    │    │   Port: 6333    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kafka         │    │   MinIO         │    │   MCP Tools     │
│   Port: 9092    │    │   Port: 9000    │    │   Port: 8086    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Service Configuration

### Frontend Configuration

The frontend is configured through environment variables:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
NEXT_PUBLIC_APP_NAME=JobZee
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Backend Configuration

The backend uses the following configuration:

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee

# Authentication
JWT_SECRET=your-secret-key
JWT_EXPIRATION=24
BCRYPT_COST=12
REFRESH_TOKEN_EXP=7

# Services
REDIS_HOST=redis
KAFKA_BROKERS=kafka:9092
MINIO_ENDPOINT=minio:9000
```

### Agent Configuration

Each agent can be configured independently:

```bash
# Job Finder Agent
AGENT_TYPE=job-finder
AGENT_HTTP_PORT=8084
KAFKA_BROKERS=kafka:9092
VECTOR_DB_URL=http://qdrant:6333
OPENAI_API_KEY=your_openai_key

# Candidate Finder Agent
AGENT_TYPE=candidate-finder
AGENT_HTTP_PORT=8085
KAFKA_BROKERS=kafka:9092
VECTOR_DB_URL=http://qdrant:6333
OPENAI_API_KEY=your_openai_key
```

## 🔐 Authentication Setup

### 1. User Registration

```bash
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe",
    "role": "candidate"
  }'
```

### 2. User Login

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 3. Using Authentication

Include the JWT token in subsequent requests:

```bash
curl -X GET http://localhost:8080/api/v1/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 Monitoring & Observability

### Prometheus Metrics

All services expose Prometheus metrics:

- **API Service**: http://localhost:8080/metrics
- **Job Finder Agent**: http://localhost:8084/metrics
- **Candidate Finder Agent**: http://localhost:8085/metrics

### Grafana Dashboards

Access Grafana at http://localhost:3001 (admin/admin) to view:

- System health metrics
- Agent performance
- User activity
- Error rates

### Health Checks

All services include health check endpoints:

```bash
# Check API health
curl http://localhost:8080/health

# Check agent health
curl http://localhost:8084/health
curl http://localhost:8085/health
```

## 🔄 Development Workflow

### 1. Local Development

```bash
# Start only required services
docker-compose up -d postgres redis kafka qdrant

# Run backend locally
cd jobzee-backend
go run cmd/api/main.go

# Run frontend locally
cd jobzee-frontend
npm run dev

# Run agents locally
cd jobzee-agents
python job_finder_agent/http_server.py
python candidate_finder_agent/http_server.py
```

### 2. Testing

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

### 3. Building Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build api-service
docker-compose build job-finder-agent
```

## 🚀 Production Deployment

### 1. Environment Preparation

```bash
# Set production environment variables
export ENVIRONMENT=production
export JWT_SECRET=your-super-secure-production-secret
export OPENAI_API_KEY=your_openai_key
export DB_PASSWORD=your-secure-db-password
```

### 2. Database Migration

```bash
# Run database migrations
docker-compose exec api-service ./migrate
```

### 3. SSL/TLS Configuration

For production, configure SSL/TLS:

```yaml
# Add to docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 4. Scaling

```bash
# Scale services
docker-compose up -d --scale api-service=3
docker-compose up -d --scale job-finder-agent=2
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Check health status
docker-compose ps

# Restart service
docker-compose restart service-name
```

#### 2. Database Connection Issues

```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### 3. Kafka Issues

```bash
# Check Kafka status
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Reset Kafka
docker-compose down -v
docker-compose up -d kafka
```

#### 4. Agent Communication Issues

```bash
# Check agent logs
docker-compose logs job-finder-agent
docker-compose logs candidate-finder-agent

# Test agent endpoints
curl http://localhost:8084/health
curl http://localhost:8085/health
```

### Performance Optimization

#### 1. Resource Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  api-service:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "0.5"
        reservations:
          memory: 512M
          cpus: "0.25"
```

#### 2. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_applications_user_id ON applications(user_id);
```

#### 3. Caching Strategy

Configure Redis caching:

```bash
# Set cache TTL
export REDIS_CACHE_TTL=3600

# Enable query caching
export ENABLE_QUERY_CACHE=true
```

## 🔒 Security Considerations

### 1. Environment Variables

- Never commit `.env` files to version control
- Use strong, unique secrets for production
- Rotate secrets regularly

### 2. Network Security

```yaml
# Restrict network access
services:
  api-service:
    networks:
      jobzee-network:
        ipv4_address: 172.20.0.10
```

### 3. Database Security

```bash
# Use strong passwords
export DB_PASSWORD=$(openssl rand -base64 32)

# Enable SSL connections
export DB_SSLMODE=require
```

### 4. API Security

- Implement rate limiting
- Use HTTPS in production
- Validate all inputs
- Implement proper CORS policies

## 📈 Monitoring & Alerting

### 1. Set up Alerts

Configure Prometheus alerts:

```yaml
# prometheus/alerts.yml
groups:
  - name: jobzee
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
```

### 2. Log Aggregation

```bash
# Add ELK stack for log aggregation
docker-compose -f docker-compose.yml -f docker-compose.logging.yml up -d
```

### 3. Health Monitoring

```bash
# Set up health checks
curl -f http://localhost:8080/health || exit 1
curl -f http://localhost:8084/health || exit 1
curl -f http://localhost:8085/health || exit 1
```

## 🔄 Backup & Recovery

### 1. Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres jobzee > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres jobzee < backup.sql
```

### 2. Configuration Backup

```bash
# Backup configuration
tar -czf config-backup.tar.gz .env docker-compose.yml

# Restore configuration
tar -xzf config-backup.tar.gz
```

### 3. Disaster Recovery

```bash
# Full system backup
docker-compose down
tar -czf jobzee-backup-$(date +%Y%m%d).tar.gz data/ .env docker-compose.yml

# Full system restore
tar -xzf jobzee-backup-20231201.tar.gz
docker-compose up -d
```

## 📚 Additional Resources

- [API Documentation](http://localhost:8080/docs)
- [Agent Documentation](http://localhost:8084/docs)
- [Monitoring Dashboard](http://localhost:3001)
- [Database Admin](http://localhost:8087)

## 🆘 Support

For issues and questions:

- **GitHub Issues**: [Create an issue](https://github.com/your-org/jobzee/issues)
- **Documentation**: [Read the docs](https://docs.jobzee.com)
- **Email**: support@jobzee.com

---

**JobZee** - Revolutionizing job matching with AI-powered agents 🚀
