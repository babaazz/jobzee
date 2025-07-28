# JobZee Backend Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Services](#services)
4. [API Design](#api-design)
5. [Database Design](#database-design)
6. [Authentication & Authorization](#authentication--authorization)
7. [Event-Driven Architecture](#event-driven-architecture)
8. [Testing Strategy](#testing-strategy)
9. [Deployment](#deployment)
10. [Monitoring](#monitoring)

## Overview

The JobZee Backend is a microservices-based Go application that provides the core business logic, data management, and API endpoints for the JobZee platform. It's built using Go 1.21+, Gin framework, and follows clean architecture principles.

### Key Features

- **Microservices Architecture**: Separate services for different business domains
- **gRPC Communication**: High-performance inter-service communication
- **REST API**: HTTP endpoints for frontend and external integrations
- **Event-Driven**: Kafka-based event processing
- **Authentication**: JWT-based authentication with refresh tokens
- **Database**: PostgreSQL with Redis caching
- **Monitoring**: Prometheus metrics and structured logging

## Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   API Gateway   │    │   Job Service   │    │   Candidate   │ │
│  │                 │    │                 │    │   Service     │ │
│  │ • HTTP Router   │    │ • Job CRUD      │    │ • Profile Mgmt│ │
│  │ • Auth Middleware│   │ • Job Search    │    │ • Resume Parse│ │
│  │ • Rate Limiting │    │ • Job Analytics │    │ • Portfolio   │ │
│  │ • CORS          │    │ • Job Matching  │    │ • Skills      │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   Agent Service │    │   Event Bus     │    │   Database    │ │
│  │                 │    │                 │    │   Layer       │ │
│  │ • Agent Mgmt    │    │ • Kafka Producer│    │ • PostgreSQL  │ │
│  │ • A2A Protocol  │    │ • Event Handlers│    │ • Redis Cache │ │
│  │ • Agent State   │    │ • Event Schema  │    │ • Migrations  │ │
│  │ • Coordination  │    │ • Dead Letter Q │    │ • Connection  │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
jobzee-backend/
├── cmd/                    # Application entry points
│   ├── api/               # API Gateway service
│   ├── jobservice/        # Job management service
│   ├── candidateservice/  # Candidate management service
│   └── agentservice/      # Agent coordination service
├── internal/              # Internal packages
│   ├── api/              # HTTP handlers and middleware
│   ├── services/         # Business logic layer
│   ├── models/           # Data models and DTOs
│   ├── repository/       # Data access layer
│   ├── config/           # Configuration management
│   ├── middleware/       # HTTP middleware
│   ├── kafka/            # Event handling
│   └── utils/            # Utility functions
├── proto/                # gRPC protocol definitions
└── Dockerfile           # Container configuration
```

## Services

### API Gateway Service

**Purpose**: Main entry point for all HTTP requests, handles authentication, routing, and request/response processing.

**Key Responsibilities**:

- HTTP request routing and validation
- Authentication and authorization
- Rate limiting and CORS
- Request/response logging
- Error handling and response formatting

**Endpoints**:

```go
// Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

// Job Management
GET    /api/v1/jobs
POST   /api/v1/jobs
GET    /api/v1/jobs/:id
PUT    /api/v1/jobs/:id
DELETE /api/v1/jobs/:id

// Candidate Management
GET    /api/v1/candidates
POST   /api/v1/candidates
GET    /api/v1/candidates/:id
PUT    /api/v1/candidates/:id

// Agent Communication
POST   /api/v1/agents/job-finder/chat
POST   /api/v1/agents/candidate-finder/chat
```

### Job Service

**Purpose**: Manages job-related operations including CRUD, search, and analytics.

**Key Responsibilities**:

- Job creation, updates, and deletion
- Job search and filtering
- Job analytics and metrics
- Job-candidate matching coordination

**gRPC Methods**:

```protobuf
service JobService {
  rpc CreateJob(CreateJobRequest) returns (Job);
  rpc GetJob(GetJobRequest) returns (Job);
  rpc ListJobs(ListJobsRequest) returns (ListJobsResponse);
  rpc UpdateJob(UpdateJobRequest) returns (Job);
  rpc DeleteJob(DeleteJobRequest) returns (Empty);
  rpc SearchJobs(SearchJobsRequest) returns (SearchJobsResponse);
}
```

### Candidate Service

**Purpose**: Manages candidate profiles, resumes, and portfolio data.

**Key Responsibilities**:

- Candidate profile management
- Resume parsing and analysis
- Portfolio integration
- Skills assessment and tracking

**gRPC Methods**:

```protobuf
service CandidateService {
  rpc CreateCandidate(CreateCandidateRequest) returns (Candidate);
  rpc GetCandidate(GetCandidateRequest) returns (Candidate);
  rpc ListCandidates(ListCandidatesRequest) returns (ListCandidatesResponse);
  rpc UpdateCandidate(UpdateCandidateRequest) returns (Candidate);
  rpc DeleteCandidate(DeleteCandidateRequest) returns (Empty);
  rpc SearchCandidates(SearchCandidatesRequest) returns (SearchCandidatesResponse);
}
```

### Agent Service

**Purpose**: Coordinates AI agents and manages agent-to-agent communication.

**Key Responsibilities**:

- Agent lifecycle management
- A2A protocol implementation
- Agent state management
- Agent coordination and routing

**gRPC Methods**:

```protobuf
service AgentService {
  rpc ProcessJobRequest(JobRequest) returns (JobResponse);
  rpc ProcessCandidateRequest(CandidateRequest) returns (CandidateResponse);
  rpc StreamAgentChat(stream ChatMessage) returns (stream ChatResponse);
  rpc GetAgentStatus(AgentStatusRequest) returns (AgentStatus);
}
```

## API Design

### REST API Design Principles

#### Resource-Oriented Design

- **Resources**: Nouns representing business entities (jobs, candidates, users)
- **HTTP Methods**: Standard HTTP methods for CRUD operations
- **Status Codes**: Proper HTTP status codes for responses
- **Pagination**: Cursor-based pagination for list endpoints

#### Request/Response Format

```go
// Standard Response Format
type APIResponse struct {
    Success bool        `json:"success"`
    Data    interface{} `json:"data,omitempty"`
    Error   *APIError   `json:"error,omitempty"`
    Meta    *Meta       `json:"meta,omitempty"`
}

// Error Response
type APIError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

// Pagination Meta
type Meta struct {
    Page       int   `json:"page"`
    PerPage    int   `json:"per_page"`
    Total      int64 `json:"total"`
    TotalPages int   `json:"total_pages"`
    HasNext    bool  `json:"has_next"`
    HasPrev    bool  `json:"has_prev"`
}
```

#### Authentication Headers

```http
Authorization: Bearer <access_token>
X-Refresh-Token: <refresh_token>
X-Trace-ID: <trace_id>
```

### gRPC API Design

#### Protocol Buffer Definitions

```protobuf
// jobzee-protos/grpc/job_service.proto
syntax = "proto3";

package job_service;

service JobService {
  rpc CreateJob(CreateJobRequest) returns (Job);
  rpc GetJob(GetJobRequest) returns (Job);
  rpc ListJobs(ListJobsRequest) returns (ListJobsResponse);
  rpc UpdateJob(UpdateJobRequest) returns (Job);
  rpc DeleteJob(DeleteJobRequest) returns (Empty);
  rpc SearchJobs(SearchJobsRequest) returns (SearchJobsResponse);
}

message Job {
  string id = 1;
  string title = 2;
  string company = 3;
  string location = 4;
  string description = 5;
  repeated string requirements = 6;
  string created_by = 7;
  google.protobuf.Timestamp created_at = 8;
  google.protobuf.Timestamp updated_at = 9;
}
```

#### Error Handling

```protobuf
message Error {
  string code = 1;
  string message = 2;
  string details = 3;
}

message JobResponse {
  oneof result {
    Job job = 1;
    Error error = 2;
  }
}
```

## Database Design

### PostgreSQL Schema

#### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'candidate',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### Jobs Table

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT[] NOT NULL,
    salary_min INTEGER,
    salary_max INTEGER,
    job_type VARCHAR(50) NOT NULL,
    experience_level VARCHAR(50) NOT NULL,
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_job_type ON jobs(job_type);
CREATE INDEX idx_jobs_experience_level ON jobs(experience_level);
```

#### Candidates Table

```sql
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    headline VARCHAR(255),
    summary TEXT,
    skills TEXT[] NOT NULL,
    experience_years INTEGER,
    education TEXT[],
    portfolio_links JSONB,
    resume_url VARCHAR(500),
    github_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_candidates_skills ON candidates USING GIN(skills);
CREATE INDEX idx_candidates_experience ON candidates(experience_years);
```

#### Applications Table

```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    candidate_id UUID REFERENCES candidates(id),
    status VARCHAR(50) NOT NULL DEFAULT 'applied',
    cover_letter TEXT,
    resume_url VARCHAR(500),
    match_score DECIMAL(3,2),
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_job_id ON applications(job_id);
CREATE INDEX idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX idx_applications_status ON applications(status);
```

### Redis Caching Strategy

#### Cache Keys

```go
// User session cache
const (
    UserSessionKey = "user:session:%s"  // user_id
    UserProfileKey = "user:profile:%s"  // user_id
    JobCacheKey    = "job:%s"           // job_id
    JobListKey     = "jobs:list:%s"     // filter_hash
    CandidateKey   = "candidate:%s"     // candidate_id
)
```

#### Cache TTL

```go
const (
    SessionTTL     = 24 * time.Hour
    ProfileTTL     = 1 * time.Hour
    JobTTL         = 30 * time.Minute
    JobListTTL     = 15 * time.Minute
    CandidateTTL   = 1 * time.Hour
)
```

## Authentication & Authorization

### JWT Token Structure

#### Access Token

```go
type AccessTokenClaims struct {
    UserID   string `json:"user_id"`
    Email    string `json:"email"`
    Role     string `json:"role"`
    IssuedAt int64  `json:"iat"`
    ExpiresAt int64 `json:"exp"`
}
```

#### Refresh Token

```go
type RefreshTokenClaims struct {
    UserID    string `json:"user_id"`
    TokenType string `json:"token_type"`
    IssuedAt  int64  `json:"iat"`
    ExpiresAt int64  `json:"exp"`
}
```

### Authentication Flow

```go
// Authentication middleware
func AuthMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := extractToken(c)
        if token == "" {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "No token provided"})
            c.Abort()
            return
        }

        claims, err := validateToken(token)
        if err != nil {
            c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
            c.Abort()
            return
        }

        c.Set("user_id", claims.UserID)
        c.Set("user_role", claims.Role)
        c.Next()
    }
}
```

### Role-Based Access Control

```go
// RBAC middleware
func RequireRole(roles ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRole := c.GetString("user_role")

        for _, role := range roles {
            if userRole == role {
                c.Next()
                return
            }
        }

        c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions"})
        c.Abort()
    }
}
```

## Event-Driven Architecture

### Kafka Event Schema

#### Event Structure

```go
type Event struct {
    ID          string                 `json:"event_id"`
    Type        string                 `json:"event_type"`
    Version     string                 `json:"version"`
    Timestamp   time.Time              `json:"timestamp"`
    Data        map[string]interface{} `json:"data"`
    Metadata    EventMetadata          `json:"metadata"`
}

type EventMetadata struct {
    Source        string `json:"source"`
    CorrelationID string `json:"correlation_id"`
    UserAgent     string `json:"user_agent,omitempty"`
}
```

#### Event Types

```go
const (
    // User events
    EventUserCreated     = "user.created"
    EventUserUpdated     = "user.updated"
    EventUserDeleted     = "user.deleted"

    // Job events
    EventJobCreated      = "job.created"
    EventJobUpdated      = "job.updated"
    EventJobDeleted      = "job.deleted"
    EventJobApplied      = "job.applied"

    // Candidate events
    EventCandidateCreated = "candidate.created"
    EventCandidateUpdated = "candidate.updated"

    // Match events
    EventMatchCreated    = "match.created"
    EventMatchUpdated    = "match.updated"
)
```

### Event Producers

```go
// Kafka producer
type EventProducer struct {
    producer *kafka.Producer
    config   *kafka.ConfigMap
}

func (ep *EventProducer) PublishEvent(topic string, event Event) error {
    eventJSON, err := json.Marshal(event)
    if err != nil {
        return err
    }

    message := &kafka.Message{
        TopicPartition: kafka.TopicPartition{
            Topic:     &topic,
            Partition: kafka.PartitionAny,
        },
        Value: eventJSON,
    }

    return ep.producer.Produce(message, nil)
}
```

### Event Consumers

```go
// Event consumer
type EventConsumer struct {
    consumer *kafka.Consumer
    handlers map[string]EventHandler
}

type EventHandler func(event Event) error

func (ec *EventConsumer) HandleEvent(event Event) error {
    handler, exists := ec.handlers[event.Type]
    if !exists {
        return fmt.Errorf("no handler for event type: %s", event.Type)
    }

    return handler(event)
}
```

## Testing Strategy

### Unit Testing

#### Service Layer Tests

```go
func TestJobService_CreateJob(t *testing.T) {
    // Arrange
    mockRepo := &MockJobRepository{}
    service := NewJobService(mockRepo)

    job := &Job{
        Title:       "Software Engineer",
        Company:     "Tech Corp",
        Location:    "San Francisco",
        Description: "We are looking for...",
    }

    mockRepo.On("Create", job).Return(job, nil)

    // Act
    result, err := service.CreateJob(job)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, job.Title, result.Title)
    mockRepo.AssertExpectations(t)
}
```

#### Repository Layer Tests

```go
func TestJobRepository_Create(t *testing.T) {
    // Arrange
    db, mock, err := sqlmock.New()
    require.NoError(t, err)
    defer db.Close()

    repo := NewJobRepository(db)
    job := &Job{Title: "Test Job"}

    mock.ExpectQuery("INSERT INTO jobs").
        WithArgs(job.Title, job.Company, job.Location).
        WillReturnRows(sqlmock.NewRows([]string{"id"}).AddRow("test-id"))

    // Act
    result, err := repo.Create(job)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "test-id", result.ID)
    assert.NoError(t, mock.ExpectationsWereMet())
}
```

### Integration Testing

#### API Integration Tests

```go
func TestJobAPI_CreateJob(t *testing.T) {
    // Arrange
    router := setupTestRouter()
    jobData := map[string]interface{}{
        "title":       "Test Job",
        "company":     "Test Company",
        "location":    "Test Location",
        "description": "Test Description",
    }

    // Act
    req, _ := http.NewRequest("POST", "/api/v1/jobs",
        strings.NewReader(mustMarshal(jobData)))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+testToken)

    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    // Assert
    assert.Equal(t, http.StatusCreated, w.Code)

    var response APIResponse
    err := json.Unmarshal(w.Body.Bytes(), &response)
    assert.NoError(t, err)
    assert.True(t, response.Success)
}
```

### End-to-End Testing

```go
func TestJobWorkflow_E2E(t *testing.T) {
    // Setup test environment
    setupTestEnvironment(t)

    // Test complete job workflow
    t.Run("Create Job and Apply", func(t *testing.T) {
        // 1. Create job
        job := createTestJob(t)

        // 2. Create candidate
        candidate := createTestCandidate(t)

        // 3. Apply for job
        application := applyForJob(t, job.ID, candidate.ID)

        // 4. Verify application
        assert.Equal(t, "applied", application.Status)
    })
}
```

## Deployment

### Docker Configuration

```dockerfile
# Multi-stage build
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/api

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/main .
COPY --from=builder /app/config ./config

EXPOSE 8080
CMD ["./main"]
```

### Environment Configuration

```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee
DB_SSL_MODE=disable

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Kafka
KAFKA_BROKERS=kafka:9092
KAFKA_TOPIC_PREFIX=jobzee

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION=24
REFRESH_TOKEN_EXP=7

# Server
PORT=8080
ENV=production
LOG_LEVEL=info
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
        - name: api-service
          image: jobzee/api-service:latest
          ports:
            - containerPort: 8080
          env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_HOST
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: JWT_SECRET
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
```

## Monitoring

### Health Checks

```go
// Health check endpoint
func HealthCheck(c *gin.Context) {
    health := map[string]interface{}{
        "status":    "healthy",
        "timestamp": time.Now().UTC(),
        "version":   "1.0.0",
        "services": map[string]string{
            "database": "healthy",
            "redis":    "healthy",
            "kafka":    "healthy",
        },
    }

    c.JSON(http.StatusOK, health)
}
```

### Prometheus Metrics

```go
var (
    // HTTP metrics
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "Duration of HTTP requests",
        },
        []string{"method", "endpoint"},
    )

    // Business metrics
    jobsCreatedTotal = prometheus.NewCounter(
        prometheus.CounterOpts{
            Name: "jobs_created_total",
            Help: "Total number of jobs created",
        },
    )

    applicationsTotal = prometheus.NewCounter(
        prometheus.CounterOpts{
            Name: "applications_total",
            Help: "Total number of job applications",
        },
    )
)
```

### Structured Logging

```go
// Logger configuration
func setupLogger() *zap.Logger {
    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

    logger, err := config.Build()
    if err != nil {
        log.Fatal(err)
    }

    return logger
}

// Request logging middleware
func RequestLogger(logger *zap.Logger) gin.HandlerFunc {
    return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
        logger.Info("HTTP Request",
            zap.String("method", param.Method),
            zap.String("path", param.Path),
            zap.Int("status", param.StatusCode),
            zap.Duration("latency", param.Latency),
            zap.String("client_ip", param.ClientIP),
            zap.String("user_agent", param.Request.UserAgent()),
        )
        return ""
    })
}
```

---

## Conclusion

The JobZee Backend is a robust, scalable microservices architecture that provides:

- **High Performance**: gRPC for inter-service communication
- **Scalability**: Microservices with horizontal scaling
- **Reliability**: Event-driven architecture with fault tolerance
- **Security**: JWT authentication with RBAC
- **Observability**: Comprehensive monitoring and logging
- **Maintainability**: Clean architecture with clear separation of concerns

The backend serves as the foundation for the entire JobZee platform, providing reliable APIs and business logic for job matching and recruitment automation.
