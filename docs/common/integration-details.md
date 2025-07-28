# JobZee Integration Details

## Table of Contents

1. [Overview](#overview)
2. [Repository Integration Map](#repository-integration-map)
3. [API Integration](#api-integration)
4. [Data Flow Integration](#data-flow-integration)
5. [Event-Driven Integration](#event-driven-integration)
6. [Real-time Communication](#real-time-communication)
7. [Authentication & Authorization](#authentication--authorization)
8. [Error Handling & Resilience](#error-handling--resilience)
9. [Deployment Integration](#deployment-integration)
10. [Monitoring Integration](#monitoring-integration)

## Overview

This document describes how all JobZee repositories integrate and communicate with each other to form a cohesive, distributed system. The integration patterns ensure loose coupling, high availability, and maintainable codebases.

## Repository Integration Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              JOBZEE ECOSYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ jobzee-frontend │    │ jobzee-backend  │    │ jobzee-agents   │         │
│  │                 │    │                 │    │                 │         │
│  │ • Next.js App   │◄──►│ • API Gateway   │◄──►│ • Job Finder    │         │
│  │ • React UI      │    │ • Microservices │    │ • Candidate     │         │
│  │ • WebSocket     │    │ • gRPC Services │    │   Finder        │         │
│  │ • i18n          │    │ • Event Bus     │    │ • LangGraph     │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│           │                       │                       │                 │
│           │                       │                       │                 │
│           ▼                       ▼                       ▼                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │ jobzee-protos   │    │ jobzee-infra    │    │ Shared Data     │         │
│  │                 │    │                 │    │                 │         │
│  │ • gRPC Defs     │    │ • K8s Manifests │    │ • PostgreSQL    │         │
│  │ • AsyncAPI      │    │ • Terraform     │    │ • Redis         │         │
│  │ • Protocol Bufs │    │ • CI/CD         │    │ • Qdrant        │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Repository Dependencies

| Repository        | Dependencies                      | Provides To                        |
| ----------------- | --------------------------------- | ---------------------------------- |
| `jobzee-protos`   | None                              | All repositories                   |
| `jobzee-backend`  | `jobzee-protos`                   | `jobzee-frontend`, `jobzee-agents` |
| `jobzee-frontend` | `jobzee-backend`                  | None                               |
| `jobzee-agents`   | `jobzee-backend`, `jobzee-protos` | `jobzee-backend`                   |
| `jobzee-infra`    | All repositories                  | None                               |

## API Integration

### Frontend ↔ Backend Integration

#### REST API Integration

```typescript
// Frontend API client (jobzee-frontend/lib/api.ts)
interface ApiClient {
  // Authentication
  login(credentials: LoginRequest): Promise<AuthResponse>;
  register(userData: RegisterRequest): Promise<AuthResponse>;
  refreshToken(): Promise<AuthResponse>;

  // Job Management
  getJobs(filters: JobFilters): Promise<Job[]>;
  getJob(id: string): Promise<Job>;
  createJob(jobData: CreateJobRequest): Promise<Job>;

  // Candidate Management
  getCandidates(filters: CandidateFilters): Promise<Candidate[]>;
  getCandidate(id: string): Promise<Candidate>;
  updateProfile(profile: ProfileUpdate): Promise<Candidate>;

  // Agent Communication
  chatWithAgent(
    agentType: "job-finder" | "candidate-finder",
    message: string
  ): Promise<AgentResponse>;
}
```

#### WebSocket Integration

```typescript
// Frontend WebSocket client (jobzee-frontend/hooks/useWebSocket.ts)
interface WebSocketClient {
  // Real-time chat with agents
  connectToAgent(agentType: string, sessionId: string): void;
  sendMessage(message: string): void;
  onMessage(callback: (message: AgentMessage) => void): void;

  // Real-time notifications
  subscribeToNotifications(userId: string): void;
  onNotification(callback: (notification: Notification) => void): void;
}
```

### Backend ↔ Agents Integration

#### gRPC Integration

```protobuf
// jobzee-protos/grpc/agent_service.proto
service AgentService {
  rpc ProcessJobRequest(JobRequest) returns (JobResponse);
  rpc ProcessCandidateRequest(CandidateRequest) returns (CandidateResponse);
  rpc StreamAgentChat(stream ChatMessage) returns (stream ChatResponse);
}
```

#### HTTP Integration

```python
# jobzee-agents/common/mcp_client.py
class MCPClient:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url
        self.session = requests.Session()

    async def get_job_details(self, job_id: str) -> Dict:
        response = await self.session.get(f"{self.backend_url}/api/v1/jobs/{job_id}")
        return response.json()

    async def get_candidate_profile(self, candidate_id: str) -> Dict:
        response = await self.session.get(f"{self.backend_url}/api/v1/candidates/{candidate_id}")
        return response.json()
```

## Data Flow Integration

### User Registration Flow

```mermaid
sequenceDiagram
    participant F as Frontend
    participant B as Backend
    participant DB as Database
    participant K as Kafka
    participant A as Agents

    F->>B: POST /api/v1/auth/register
    B->>DB: Create user record
    B->>K: Publish user.created event
    K->>A: Notify agents
    A->>B: Initialize user profile
    B->>DB: Update profile
    B->>F: Return user data + tokens
```

### Job Matching Flow

```mermaid
sequenceDiagram
    participant F as Frontend
    participant B as Backend
    participant JFA as Job Finder Agent
    participant VD as Vector DB
    participant K as Kafka

    F->>B: POST /api/v1/agents/job-finder/chat
    B->>JFA: Forward request
    JFA->>VD: Search similar jobs
    JFA->>B: Get job details via gRPC
    JFA->>K: Publish match.event
    JFA->>B: Return recommendations
    B->>F: Return job matches
```

### Agent-to-Agent Communication

```mermaid
sequenceDiagram
    participant JFA as Job Finder Agent
    participant A2A as A2A Protocol
    participant CFA as Candidate Finder Agent
    participant B as Backend
    participant K as Kafka

    JFA->>A2A: Request candidate analysis
    A2A->>CFA: Forward request
    CFA->>B: Get candidate data via gRPC
    CFA->>K: Publish analysis.event
    CFA->>A2A: Return analysis
    A2A->>JFA: Candidate insights
```

## Event-Driven Integration

### Kafka Event Schema

#### User Events

```json
{
  "event_type": "user.created",
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "profile_type": "candidate",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "metadata": {
    "source": "api-gateway",
    "correlation_id": "uuid",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### Job Events

```json
{
  "event_type": "job.created",
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "job_id": "uuid",
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "requirements": ["Python", "Go", "Kubernetes"],
    "created_by": "uuid"
  },
  "metadata": {
    "source": "job-service",
    "correlation_id": "uuid"
  }
}
```

#### Match Events

```json
{
  "event_type": "match.created",
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "match_id": "uuid",
    "job_id": "uuid",
    "candidate_id": "uuid",
    "match_score": 0.85,
    "matched_by": "job-finder-agent",
    "matched_at": "2024-01-01T00:00:00Z"
  },
  "metadata": {
    "source": "job-finder-agent",
    "correlation_id": "uuid"
  }
}
```

### Event Consumers

#### Backend Event Consumers

```go
// jobzee-backend/internal/kafka/consumer.go
type EventConsumer struct {
    consumer *kafka.Consumer
    handlers map[string]EventHandler
}

func (ec *EventConsumer) HandleUserCreated(event UserCreatedEvent) error {
    // Update user analytics
    // Send welcome email
    // Initialize user preferences
    return nil
}

func (ec *EventConsumer) HandleJobCreated(event JobCreatedEvent) error {
    // Update job analytics
    // Notify relevant agents
    // Update search index
    return nil
}
```

#### Agent Event Consumers

```python
# jobzee-agents/common/kafka_consumer.py
class AgentEventConsumer:
    def __init__(self, kafka_config: Dict):
        self.consumer = KafkaConsumer(**kafka_config)
        self.handlers = {
            'user.created': self.handle_user_created,
            'job.created': self.handle_job_created,
            'match.created': self.handle_match_created
        }

    async def handle_user_created(self, event: Dict):
        # Initialize user profile in vector DB
        # Create user embeddings
        # Set up user preferences
        pass

    async def handle_job_created(self, event: Dict):
        # Create job embeddings
        # Update job search index
        # Notify relevant candidates
        pass
```

## Real-time Communication

### WebSocket Integration

#### Frontend WebSocket Client

```typescript
// jobzee-frontend/hooks/useWebSocket.ts
export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const connect = useCallback(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      // Send authentication token
      ws.send(
        JSON.stringify({
          type: "auth",
          token: getAuthToken(),
        })
      );
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleMessage(message);
    };

    setSocket(ws);
  }, [url]);

  return { socket, isConnected, connect };
};
```

#### Backend WebSocket Handler

```go
// jobzee-backend/internal/api/websocket.go
type WebSocketHandler struct {
    upgrader websocket.Upgrader
    clients  map[string]*Client
    mu       sync.RWMutex
}

func (h *WebSocketHandler) HandleWebSocket(w http.ResponseWriter, r *http.Request) {
    conn, err := h.upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }

    client := &Client{
        conn:   conn,
        userID: getUserIDFromToken(r),
        send:   make(chan []byte, 256),
    }

    h.registerClient(client)
    go client.writePump()
    go client.readPump()
}
```

### A2A Protocol Integration

#### Agent-to-Agent Communication

```python
# jobzee-agents/common/a2a_protocol.py
class A2AProtocol:
    def __init__(self, agent_id: str, kafka_config: Dict):
        self.agent_id = agent_id
        self.producer = KafkaProducer(**kafka_config)
        self.consumer = KafkaConsumer(**kafka_config)

    async def send_request(self, target_agent: str, request: Dict) -> Dict:
        request_id = str(uuid.uuid4())
        message = {
            'request_id': request_id,
            'from_agent': self.agent_id,
            'to_agent': target_agent,
            'request': request,
            'timestamp': datetime.utcnow().isoformat()
        }

        await self.producer.send('a2a-requests', message)
        return await self.wait_for_response(request_id)

    async def handle_request(self, request: Dict) -> Dict:
        # Handle incoming A2A requests
        request_type = request.get('type')
        if request_type == 'analyze_candidate':
            return await self.analyze_candidate(request['data'])
        elif request_type == 'find_jobs':
            return await self.find_jobs(request['data'])
        else:
            raise ValueError(f"Unknown request type: {request_type}")
```

## Authentication & Authorization

### JWT Token Flow

```mermaid
sequenceDiagram
    participant F as Frontend
    participant B as Backend
    participant A as Agents

    F->>B: POST /api/v1/auth/login
    B->>F: {access_token, refresh_token}
    F->>B: API requests with Authorization header
    B->>F: Validated responses
    F->>A: WebSocket connection with token
    A->>B: Verify token via gRPC
    A->>F: Authenticated WebSocket communication
```

### Token Validation

#### Backend Token Validation

```go
// jobzee-backend/internal/middleware/auth.go
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

#### Agent Token Validation

```python
# jobzee-agents/common/auth.py
class TokenValidator:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url

    async def validate_token(self, token: str) -> Dict:
        headers = {'Authorization': f'Bearer {token}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.backend_url}/api/v1/auth/validate", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError("Invalid token")
```

## Error Handling & Resilience

### Circuit Breaker Pattern

#### Backend Circuit Breaker

```go
// jobzee-backend/internal/utils/circuit_breaker.go
type CircuitBreaker struct {
    failures    int
    threshold   int
    timeout     time.Duration
    lastFailure time.Time
    state       State
    mu          sync.RWMutex
}

func (cb *CircuitBreaker) Execute(command func() error) error {
    if !cb.canExecute() {
        return ErrCircuitBreakerOpen
    }

    err := command()
    cb.recordResult(err)
    return err
}
```

#### Agent Circuit Breaker

```python
# jobzee-agents/common/circuit_breaker.py
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'CLOSED'

    async def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenError()

        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
```

### Retry Mechanisms

#### Exponential Backoff

```python
# jobzee-agents/common/retry.py
class ExponentialBackoff:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def retry(self, func, *args, **kwargs):
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)

        raise last_exception
```

## Deployment Integration

### Docker Compose Integration

```yaml
# docker-compose.yml
version: "3.8"
services:
  # Backend services
  api-service:
    build:
      context: ./jobzee-backend
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis
      - kafka

  # Agent services
  job-finder-agent:
    build:
      context: ./jobzee-agents
      dockerfile: Dockerfile
    ports:
      - "8084:8084"
    depends_on:
      - kafka
      - qdrant

  # Frontend
  frontend:
    build:
      context: ./jobzee-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - api-service
```

### Kubernetes Integration

#### Service Discovery

```yaml
# jobzee-infra/kubernetes/manifests/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api-service
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

#### ConfigMap Integration

```yaml
# jobzee-infra/kubernetes/manifests/configmaps.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/jobzee"
  REDIS_URL: "redis://redis:6379"
  KAFKA_BROKERS: "kafka:9092"
```

## Monitoring Integration

### Distributed Tracing

#### Trace Propagation

```go
// jobzee-backend/internal/middleware/tracing.go
func TracingMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        traceID := c.GetHeader("X-Trace-ID")
        if traceID == "" {
            traceID = generateTraceID()
        }

        c.Set("trace_id", traceID)
        c.Header("X-Trace-ID", traceID)
        c.Next()
    }
}
```

#### Agent Tracing

```python
# jobzee-agents/common/tracing.py
class TracingMiddleware:
    def __init__(self):
        self.tracer = None

    async def trace_request(self, request: Dict) -> Dict:
        trace_id = request.get('trace_id', str(uuid.uuid4()))

        # Add trace context to all downstream calls
        headers = {'X-Trace-ID': trace_id}

        # Log request with trace ID
        logger.info(f"Processing request", extra={
            'trace_id': trace_id,
            'request_type': request.get('type')
        })

        return trace_id
```

### Metrics Collection

#### Backend Metrics

```go
// jobzee-backend/internal/metrics/metrics.go
var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "Duration of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    activeConnections = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "websocket_active_connections",
            Help: "Number of active WebSocket connections",
        },
    )
)
```

#### Agent Metrics

```python
# jobzee-agents/common/metrics.py
class AgentMetrics:
    def __init__(self):
        self.request_counter = Counter('agent_requests_total', 'Total requests processed')
        self.request_duration = Histogram('agent_request_duration_seconds', 'Request duration')
        self.error_counter = Counter('agent_errors_total', 'Total errors')

    def track_request(self, request_type: str):
        self.request_counter.labels(type=request_type).inc()

    def track_duration(self, duration: float):
        self.request_duration.observe(duration)

    def track_error(self, error_type: str):
        self.error_counter.labels(type=error_type).inc()
```

---

## Conclusion

This integration document provides a comprehensive overview of how all JobZee repositories work together to create a cohesive, distributed system. Key integration patterns include:

- **API-First Design**: All services expose well-defined APIs
- **Event-Driven Architecture**: Loose coupling through Kafka events
- **Real-time Communication**: WebSocket and A2A protocol for real-time interactions
- **Resilient Communication**: Circuit breakers, retries, and error handling
- **Observable System**: Distributed tracing and comprehensive metrics
- **Secure Integration**: JWT-based authentication across all services

The integration design ensures that each repository can evolve independently while maintaining system cohesion and reliability.
