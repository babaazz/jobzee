# JobZee - JobZee Job Application Platform

A sophisticated jobzee system for intelligent job matching and candidate recruitment using AI-powered agents, vector databases, and real-time communication.

## 🚀 Overview

JobZee is a comprehensive job application platform that leverages multiple AI agents to revolutionize the hiring process:

- **Job Finder Agent**: Assists candidates in finding the perfect job matches
- **Candidate Finder Agent**: Helps HR professionals find ideal candidates
- **AI-Powered Matching**: Uses vector similarity and LangGraph workflows for intelligent matching
- **Real-time Communication**: Agents communicate with users and each other in real-time
- **Portfolio Analysis**: Automated analysis of GitHub profiles, resumes, and portfolios
- **Interview Scheduling**: Automated interview coordination and scheduling

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Agents        │
│   (Next.js)     │◄──►│   (Go/Gin)      │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   Qdrant        │
│   (Database)    │    │   (Cache)       │    │   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kafka         │    │   MinIO         │    │   MCP Tools     │
│   (Message Q)   │    │   (Object Store)│    │   (Agent Tools) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Go, Gin, gRPC, PostgreSQL, Redis
- **Agents**: Python, LangChain, LangGraph, OpenAI
- **Infrastructure**: Docker, Kubernetes, Kafka, Qdrant, MinIO
- **Communication**: A2A Protocol, MCP Protocol, WebSockets
- **Monitoring**: Prometheus, Grafana

## 🎯 Key Features

### For Candidates

- **Intelligent Job Matching**: AI-powered job recommendations based on skills and preferences
- **Profile Building**: Guided profile creation with skill assessment
- **Portfolio Analysis**: Automated analysis of GitHub, LinkedIn, and resume
- **Real-time Chat**: Direct communication with Job Finder Agent
- **Interview Coordination**: Automated interview scheduling and reminders

### For HR Professionals

- **Smart Candidate Search**: AI-powered candidate discovery and matching
- **Job Posting Creation**: Natural language job posting creation
- **Candidate Analysis**: Comprehensive candidate assessment and scoring
- **Interview Management**: Automated interview scheduling and coordination
- **Analytics Dashboard**: Performance metrics and insights

### For Agents

- **A2A Communication**: Agent-to-agent protocol for coordination
- **MCP Integration**: Model Context Protocol for tool access
- **Vector Search**: Semantic search using Qdrant vector database
- **Workflow Automation**: LangGraph-powered workflow orchestration
- **Real-time Processing**: Kafka-based event-driven architecture

## 🛠️ Installation & Setup

### Prerequisites

- Docker & Docker Compose
- Go 1.21+
- Node.js 18+
- Python 3.9+
- OpenAI API Key
- GitHub Token (optional)

### Quick Start

For a complete step-by-step guide to running JobZee locally, see our **[Local Development Guide](docs/common/local-development-guide.md)**.

**Quick Commands:**

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/jobzee.git
   cd jobzee
   ```

2. **Set environment variables**

   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   export GITHUB_TOKEN="your-github-token-here"  # Optional
   ```

3. **Start the system**

   ```bash
   # Using the automated setup script
   chmod +x jobzee-infra/scripts/local-setup.sh
   ./jobzee-infra/scripts/local-setup.sh

   # Or manually with Docker Compose
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8080
   - MinIO Console: http://localhost:9001
   - Grafana: http://localhost:3001 (admin/admin)
   - Adminer (Database): http://localhost:8087

### Manual Setup

#### Backend Setup

```bash
cd jobzee-backend
go mod download
go run cmd/api/main.go
```

#### Frontend Setup

```bash
cd jobzee-frontend
npm install
npm run dev
```

#### Agents Setup

```bash
cd jobzee-agents
pip install -r requirements.txt
python job_finder_agent/main.py
python candidate_finder_agent/main.py
```

## 📁 Project Structure

```
jobzee/
├── jobzee-frontend/          # Next.js frontend application
│   ├── app/                      # App router pages
│   ├── components/               # React components
│   ├── hooks/                    # Custom React hooks
│   └── types/                    # TypeScript type definitions
├── jobzee-backend/          # Go backend services
│   ├── cmd/                      # Application entry points
│   ├── internal/                 # Internal packages
│   │   ├── api/                  # HTTP handlers
│   │   ├── services/             # Business logic
│   │   ├── models/               # Data models
│   │   └── repository/           # Data access layer
│   └── proto/                    # gRPC protocol definitions
├── jobzee-agents/           # Python AI agents
│   ├── job_finder_agent/         # Job finder agent
│   ├── candidate_finder_agent/   # Candidate finder agent
│   ├── common/                   # Shared utilities
│   └── workflows/                # LangGraph workflows
├── jobzee-protos/           # Protocol definitions
│   ├── grpc/                     # gRPC service definitions
│   └── asyncapi/                 # AsyncAPI specifications
├── jobzee-infra/            # Infrastructure configuration
│   ├── kubernetes/               # K8s manifests
│   ├── terraform/                # Infrastructure as code
│   └── scripts/                  # Setup and deployment scripts
└── docker-compose.yml           # Local development setup
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Kafka Configuration
KAFKA_BROKERS=localhost:9092

# Vector Database
VECTOR_DB_URL=http://localhost:6333

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Service Ports
API_PORT=8080
FRONTEND_PORT=3000
```

### Agent Configuration

Each agent can be configured through environment variables:

```bash
# Job Finder Agent
AGENT_TYPE=job-finder
AGENT_PORT=8084
KAFKA_BROKERS=kafka:9092
VECTOR_DB_URL=http://qdrant:6333

# Candidate Finder Agent
AGENT_TYPE=candidate-finder
AGENT_PORT=8085
KAFKA_BROKERS=kafka:9092
VECTOR_DB_URL=http://qdrant:6333
```

## 🚀 Usage

### For Candidates

1. **Register and Create Profile**

   - Sign up with email
   - Chat with Job Finder Agent to build profile
   - Upload resume and portfolio links

2. **Find Jobs**

   - Agent analyzes your profile and preferences
   - Receives job recommendations with match scores
   - View detailed job information and apply

3. **Interview Process**
   - Agent coordinates interview scheduling
   - Receive notifications and reminders
   - Track application status

### For HR Professionals

1. **Create Job Posting**

   - Chat with Candidate Finder Agent
   - Describe job requirements in natural language
   - Agent creates structured job posting

2. **Find Candidates**

   - Agent searches for matching candidates
   - Analyzes portfolios and experience
   - Provides candidate recommendations

3. **Interview Management**
   - Schedule interviews through agent
   - Automated candidate communication
   - Track hiring pipeline

## 🔌 API Documentation

### REST API Endpoints

```bash
# Agent Communication
POST /api/v1/agents/job-finder/chat
POST /api/v1/agents/candidate-finder/chat

# Job Management
GET    /api/v1/jobs
POST   /api/v1/jobs
GET    /api/v1/jobs/:id
PUT    /api/v1/jobs/:id
DELETE /api/v1/jobs/:id

# Candidate Management
GET    /api/v1/candidates
POST   /api/v1/candidates
GET    /api/v1/candidates/:id
PUT    /api/v1/candidates/:id

# Matching
GET /api/v1/matches/jobs/:jobId/candidates
GET /api/v1/matches/candidates/:candidateId/jobs

# Interviews
POST /api/v1/interviews
GET  /api/v1/interviews
```

### gRPC Services

```protobuf
service JobService {
  rpc CreateJob(CreateJobRequest) returns (Job);
  rpc GetJob(GetJobRequest) returns (Job);
  rpc ListJobs(ListJobsRequest) returns (ListJobsResponse);
}

service CandidateService {
  rpc CreateCandidate(CreateCandidateRequest) returns (Candidate);
  rpc GetCandidate(GetCandidateRequest) returns (Candidate);
  rpc ListCandidates(ListCandidatesRequest) returns (ListCandidatesResponse);
}

service AgentService {
  rpc ProcessJobRequest(JobRequest) returns (JobResponse);
  rpc ProcessCandidateRequest(CandidateRequest) returns (CandidateResponse);
}
```

## 🔍 Monitoring & Observability

### Metrics

- Agent performance metrics
- Matching accuracy scores
- Response times and throughput
- Error rates and availability

### Dashboards

- Real-time system health
- Agent activity monitoring
- User engagement analytics
- Business metrics

### Logging

- Structured logging with correlation IDs
- Agent conversation logs
- Error tracking and alerting
- Audit trails

## 🧪 Testing

### Unit Tests

```bash
# Backend tests
cd jobzee-backend
go test ./...

# Frontend tests
cd jobzee-frontend
npm test

# Agent tests
cd jobzee-agents
pytest
```

### Integration Tests

```bash
# Run integration test suite
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Load Testing

```bash
# Run load tests
k6 run tests/load/agent-chat.js
```

## 🚀 Deployment

### Local Development

```bash
docker-compose up -d
```

### Production Deployment

```bash
# Using Kubernetes
kubectl apply -f jobzee-infra/kubernetes/

# Using Terraform
cd jobzee-infra/terraform
terraform init
terraform apply
```

### CI/CD Pipeline

The project includes Jenkins pipeline configuration for automated deployment:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Build all components
            }
        }
        stage('Test') {
            steps {
                // Run tests
            }
        }
        stage('Deploy') {
            steps {
                // Deploy to production
            }
        }
    }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow Go coding standards for backend
- Use TypeScript for frontend
- Follow PEP 8 for Python agents
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.jobzee.com](https://docs.jobzee.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/jobzee/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/jobzee/discussions)
- **Email**: support@jobzee.com

## 🙏 Acknowledgments

- OpenAI for GPT models
- LangChain for AI framework
- Qdrant for vector database
- Apache Kafka for message queuing
- The open-source community

---

**JobZee** - Revolutionizing job matching with AI-powered agents 🚀
