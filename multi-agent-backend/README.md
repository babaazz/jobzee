# Multi-Agent Backend

A Go-based microservices backend for the Multi-Agent Job Application System with gRPC, Kafka, Redis, and PostgreSQL.

## Tech Stack

- **Language**: Go 1.21+
- **Framework**: Gin (HTTP), gRPC
- **Database**: PostgreSQL with GORM
- **Cache**: Redis
- **Message Queue**: Apache Kafka
- **Object Storage**: MinIO
- **Containerization**: Docker

## Architecture

The backend consists of three main microservices:

1. **API Service** (`cmd/api`) - HTTP REST API gateway
2. **Job Service** (`cmd/jobservice`) - gRPC service for job management
3. **Candidate Service** (`cmd/candidateservice`) - gRPC service for candidate management

## Prerequisites

- Go 1.21+
- PostgreSQL 13+
- Redis 6+
- Apache Kafka 2.8+
- MinIO (optional)

## Getting Started

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd multi-agent-backend

# Install dependencies
go mod download
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Environment
ENVIRONMENT=development

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee
DB_SSLMODE=disable

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=jobzee-events

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=jobzee
```

### Running Services

#### API Service

```bash
go run cmd/api/main.go
```

The API service will be available at `http://localhost:8080`

#### Job Service

```bash
go run cmd/jobservice/main.go
```

The Job gRPC service will be available at `localhost:9090`

#### Candidate Service

```bash
go run cmd/candidateservice/main.go
```

The Candidate gRPC service will be available at `localhost:9091`

### Docker

```bash
# Build all services
docker build -t multi-agent-backend .

# Run API service
docker run -p 8080:8080 multi-agent-backend ./api

# Run Job service
docker run -p 9090:9090 multi-agent-backend ./jobservice

# Run Candidate service
docker run -p 9091:9091 multi-agent-backend ./candidateservice
```

## API Endpoints

### Jobs

- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/:id` - Get job by ID
- `POST /api/v1/jobs` - Create new job
- `PUT /api/v1/jobs/:id` - Update job
- `DELETE /api/v1/jobs/:id` - Delete job

### Candidates

- `GET /api/v1/candidates` - List all candidates
- `GET /api/v1/candidates/:id` - Get candidate by ID
- `POST /api/v1/candidates` - Create new candidate
- `PUT /api/v1/candidates/:id` - Update candidate
- `DELETE /api/v1/candidates/:id` - Delete candidate

### Applications

- `GET /api/v1/applications` - List all applications
- `GET /api/v1/applications/:id` - Get application by ID
- `POST /api/v1/applications` - Create new application
- `PUT /api/v1/applications/:id` - Update application
- `DELETE /api/v1/applications/:id` - Delete application

## Project Structure

```
├── cmd/                    # Application entry points
│   ├── api/               # HTTP API service
│   ├── jobservice/        # Job gRPC service
│   └── candidateservice/  # Candidate gRPC service
├── internal/              # Private application code
│   ├── api/              # HTTP handlers and middleware
│   ├── config/           # Configuration management
│   ├── database/         # Database connection and models
│   ├── kafka/            # Kafka producer/consumer
│   └── services/         # Business logic services
├── proto/                # Protocol buffer definitions
└── pkg/                  # Public packages
```

## Development

### Code Generation

```bash
# Generate gRPC code from protobuf
protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    proto/*.proto
```

### Testing

```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run specific test
go test ./internal/services/jobservice
```

### Linting

```bash
# Install golangci-lint
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Run linter
golangci-lint run
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
