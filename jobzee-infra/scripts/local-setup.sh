#!/bin/bash

# JobZee Multi-Agent Platform Local Setup Script
# This script sets up the complete development environment locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install it and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p ./data/postgres
    mkdir -p ./data/redis
    mkdir -p ./data/kafka
    mkdir -p ./data/minio
    mkdir -p ./data/qdrant
    mkdir -p ./logs
    
    print_success "Directories created"
}

# Create environment files
create_env_files() {
    print_status "Creating environment files..."
    
    # Backend environment
    cat > ./jobzee-backend/.env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=jobzee
DB_SSLMODE=disable

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Kafka Configuration
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=jobzee-events

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=jobzee

# Service Ports
API_PORT=8080
JOB_SERVICE_PORT=8081
CANDIDATE_SERVICE_PORT=8082
AGENT_SERVICE_PORT=8083

# Environment
ENVIRONMENT=development
EOF

    # Frontend environment
    cat > ./jobzee-frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
NEXT_PUBLIC_APP_NAME=JobZee
NEXT_PUBLIC_APP_VERSION=1.0.0
EOF

    # Agents environment
    cat > ./jobzee-agents/.env << EOF
# Agent Configuration
AGENT_ID=job-finder-agent
AGENT_NAME=Job Finder Agent
AGENT_VERSION=1.0.0

# Kafka Configuration
KAFKA_BROKERS=localhost:9092
KAFKA_GROUP_ID=job-finder-group
JOB_REQUESTS_TOPIC=job-requests
JOB_MATCHES_TOPIC=job-matches
CANDIDATE_REQUESTS_TOPIC=candidate-requests
CANDIDATE_MATCHES_TOPIC=candidate-matches

# Vector Database Configuration
VECTOR_DB_URL=http://localhost:6333
VECTOR_DB_COLLECTION=jobs

# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4
MAX_TOKENS=1000
TEMPERATURE=0.1

# Matching Configuration
MIN_MATCH_SCORE=0.7
MAX_RESULTS=10
MIN_CANDIDATE_SCORE=0.7
MAX_CANDIDATES=10

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Health Check Configuration
HEALTH_CHECK_INTERVAL=30
MAX_PROCESSING_TIME=300
EOF

    print_success "Environment files created"
    print_warning "Please update the OPENAI_API_KEY in ./jobzee-agents/.env"
}

# Create Docker Compose file
create_docker_compose() {
    print_status "Creating Docker Compose file..."
    
    cat > ./docker-compose.yml << EOF
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15
    container_name: jobzee-postgres
    environment:
      POSTGRES_DB: jobzee
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    networks:
      - jobzee-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: jobzee-redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    networks:
      - jobzee-network

  # Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    container_name: jobzee-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - jobzee-network

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    container_name: jobzee-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    volumes:
      - ./data/kafka:/var/lib/kafka/data
    networks:
      - jobzee-network

  # MinIO Object Storage
  minio:
    image: minio/minio:latest
    container_name: jobzee-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - ./data/minio:/data
    networks:
      - jobzee-network

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: jobzee-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant:/qdrant/storage
    networks:
      - jobzee-network

  # Backend Services
  api-service:
    build:
      context: ./jobzee-backend
      dockerfile: Dockerfile
      target: api
    container_name: jobzee-api
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=jobzee
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - KAFKA_BROKERS=kafka:9092
      - MINIO_ENDPOINT=minio:9000
    depends_on:
      - postgres
      - redis
      - kafka
      - minio
    networks:
      - jobzee-network

  job-service:
    build:
      context: ./jobzee-backend
      dockerfile: Dockerfile
      target: jobservice
    container_name: jobzee-job-service
    ports:
      - "8081:8081"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=jobzee
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - postgres
      - redis
      - kafka
    networks:
      - jobzee-network

  candidate-service:
    build:
      context: ./jobzee-backend
      dockerfile: Dockerfile
      target: candidateservice
    container_name: jobzee-candidate-service
    ports:
      - "8082:8082"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=jobzee
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - postgres
      - redis
      - kafka
    networks:
      - jobzee-network

  agent-service:
    build:
      context: ./jobzee-backend
      dockerfile: Dockerfile
      target: agentservice
    container_name: jobzee-agent-service
    ports:
      - "8083:8083"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=jobzee
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - postgres
      - redis
      - kafka
    networks:
      - jobzee-network

  # Frontend
  frontend:
    build:
      context: ./jobzee-frontend
      dockerfile: Dockerfile
    container_name: jobzee-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
    depends_on:
      - api-service
    networks:
      - jobzee-network

  # Agent Services
  job-finder-agent:
    build:
      context: ./jobzee-agents
      dockerfile: Dockerfile
      target: job-finder
    container_name: jobzee-job-finder-agent
    environment:
      - KAFKA_BROKERS=kafka:9092
      - VECTOR_DB_URL=http://qdrant:6333
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
    depends_on:
      - kafka
      - qdrant
    networks:
      - jobzee-network

  candidate-finder-agent:
    build:
      context: ./jobzee-agents
      dockerfile: Dockerfile
      target: candidate-finder
    container_name: jobzee-candidate-finder-agent
    environment:
      - KAFKA_BROKERS=kafka:9092
      - VECTOR_DB_URL=http://qdrant:6333
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
    depends_on:
      - kafka
      - qdrant
    networks:
      - jobzee-network

networks:
  jobzee-network:
    driver: bridge
EOF

    print_success "Docker Compose file created"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start infrastructure services first
    docker-compose up -d postgres redis zookeeper kafka minio qdrant
    
    print_status "Waiting for infrastructure services to be ready..."
    sleep 30
    
    # Start backend services
    docker-compose up -d api-service job-service candidate-service agent-service
    
    print_status "Waiting for backend services to be ready..."
    sleep 20
    
    # Start frontend and agents
    docker-compose up -d frontend job-finder-agent candidate-finder-agent
    
    print_success "All services started"
}

# Check service health
check_health() {
    print_status "Checking service health..."
    
    services=(
        "http://localhost:8080/health"
        "http://localhost:8081/health"
        "http://localhost:8082/health"
        "http://localhost:8083/health"
        "http://localhost:3000"
    )
    
    for service in "${services[@]}"; do
        if curl -f -s "$service" > /dev/null; then
            print_success "Service $service is healthy"
        else
            print_warning "Service $service is not responding"
        fi
    done
}

# Main execution
main() {
    print_status "Starting JobZee Multi-Agent Platform Local Setup..."
    
    check_docker
    check_docker_compose
    create_directories
    create_env_files
    create_docker_compose
    
    read -p "Do you want to start the services now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
        check_health
        
        print_success "Setup completed!"
        print_status "Services are running at:"
        echo "  - Frontend: http://localhost:3000"
        echo "  - API Gateway: http://localhost:8080"
        echo "  - Job Service: http://localhost:8081"
        echo "  - Candidate Service: http://localhost:8082"
        echo "  - Agent Service: http://localhost:8083"
        echo "  - MinIO Console: http://localhost:9001"
        echo "  - Qdrant: http://localhost:6333"
    else
        print_status "Setup completed! Run 'docker-compose up -d' to start services."
    fi
}

# Run main function
main 