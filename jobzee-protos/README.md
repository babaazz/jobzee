# JobZee Protos

Protocol buffer definitions and AsyncAPI specifications for the JobZee Job Application System.

## Overview

This repository contains:

- **gRPC Service Definitions** - Protocol buffer files for microservice communication
- **AsyncAPI Specifications** - Event-driven API specifications for Kafka messaging
- **Code Generation** - Templates and scripts for generating client/server code

## Structure

```
├── grpc/                    # gRPC service definitions
│   ├── job_service.proto    # Job management service
│   ├── candidate_service.proto  # Candidate management service
│   └── agent_service.proto  # Agent communication service
├── asyncapi/               # AsyncAPI specifications
│   ├── jobs-posted.yml     # Job posting events
│   └── applications-created.yml  # Application events
├── buf.yaml               # Buf configuration
├── buf.gen.go.yaml        # Go code generation template
├── buf.gen.python.yaml    # Python code generation template
├── Makefile               # Build and generation commands
└── README.md              # This file
```

## Prerequisites

- **Buf CLI** - For protocol buffer management
- **Go** - For Go code generation
- **Python** - For Python code generation
- **protoc** - Protocol buffer compiler

## Installation

### Install Dependencies

```bash
# Install buf CLI
curl -sSL "https://github.com/bufbuild/buf/releases/latest/download/buf-$(uname -s)-$(uname -m)" -o /tmp/buf
chmod +x /tmp/buf
sudo mv /tmp/buf /usr/local/bin/buf

# Install Go protoc plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Install Python protoc plugin
pip install grpcio-tools
```

### Or use the Makefile

```bash
make install-deps
```

## Usage

### Generate Code

#### Generate Go Code

```bash
make generate-go
```

This will generate Go code in `../jobzee-backend/proto/`

#### Generate Python Code

```bash
make generate-python
```

This will generate Python code in `../jobzee-agents/proto/`

#### Generate All Code

```bash
make generate-all
```

### Code Quality

#### Lint Protobuf Files

```bash
make lint
```

#### Format Protobuf Files

```bash
make format
```

#### Validate Breaking Changes

```bash
make validate
```

### Cleanup

```bash
make clean
```

## Service Definitions

### Job Service (`grpc/job_service.proto`)

Provides job management functionality:

- **CreateJob** - Create a new job posting
- **GetJob** - Retrieve a job by ID
- **ListJobs** - List jobs with filtering and pagination
- **UpdateJob** - Update an existing job
- **DeleteJob** - Delete a job
- **SearchJobs** - Search jobs by criteria
- **GetJobStats** - Get job statistics

### Candidate Service (`grpc/candidate_service.proto`)

Provides candidate management functionality:

- **CreateCandidate** - Create a new candidate profile
- **GetCandidate** - Retrieve a candidate by ID
- **ListCandidates** - List candidates with filtering
- **UpdateCandidate** - Update an existing candidate
- **DeleteCandidate** - Delete a candidate
- **SearchCandidates** - Search candidates by criteria
- **GetCandidateStats** - Get candidate statistics

### Agent Service (`grpc/agent_service.proto`)

Provides agent communication functionality:

- **SendMessage** - Send a message to an agent
- **GetAgentStatus** - Get agent status
- **GetAgentStats** - Get agent statistics
- **RegisterAgent** - Register a new agent
- **UnregisterAgent** - Unregister an agent
- **ListAgents** - List all registered agents

## Event Specifications

### Job Events (`asyncapi/jobs-posted.yml`)

Defines events for job lifecycle:

- **JobCreated** - Published when a new job is created
- **JobUpdated** - Published when a job is updated
- **JobDeleted** - Published when a job is deleted

### Application Events (`asyncapi/applications-created.yml`)

Defines events for job applications:

- **ApplicationCreated** - Published when an application is submitted
- **ApplicationUpdated** - Published when an application is updated
- **ApplicationStatusChanged** - Published when application status changes

## Code Generation Templates

### Go Template (`buf.gen.go.yaml`)

```yaml
version: v1
plugins:
  - name: go
    out: ../jobzee-backend/proto
    opt: paths=source_relative
  - name: go-grpc
    out: ../jobzee-backend/proto
    opt: paths=source_relative
```

### Python Template (`buf.gen.python.yaml`)

```yaml
version: v1
plugins:
  - name: python
    out: ../jobzee-agents/proto
  - name: grpc_python
    out: ../jobzee-agents/proto
```

## Integration

### Backend Integration

The generated Go code is used in the backend services:

```go
import (
    pb "github.com/jobzee/jobzee-backend/proto/job_service"
)

// Use the generated types
job := &pb.Job{
    Title: "Software Engineer",
    Company: "TechCorp",
    // ...
}
```

### Agents Integration

The generated Python code is used in the AI agents:

```python
from proto import job_service_pb2

# Use the generated types
job = job_service_pb2.Job(
    title="Software Engineer",
    company="TechCorp",
    # ...
)
```

## Development Workflow

1. **Define Services** - Create or update `.proto` files
2. **Lint & Format** - Ensure code quality
3. **Generate Code** - Generate client/server code
4. **Test** - Validate generated code
5. **Commit** - Commit changes with generated code

### Example Workflow

```bash
# 1. Make changes to proto files
vim grpc/job_service.proto

# 2. Lint and format
make lint
make format

# 3. Generate code
make generate-all

# 4. Test generated code
cd ../jobzee-backend && go test ./proto/...
cd ../jobzee-agents && python -m pytest tests/

# 5. Commit changes
git add .
git commit -m "Add new job service methods"
```

## Best Practices

### Protocol Buffer Design

1. **Use Semantic Versioning** - Version your APIs properly
2. **Backward Compatibility** - Maintain backward compatibility
3. **Clear Naming** - Use descriptive field and service names
4. **Documentation** - Add comprehensive comments
5. **Validation** - Use field validation rules

### AsyncAPI Design

1. **Event Naming** - Use consistent event naming conventions
2. **Schema Validation** - Define strict schemas for events
3. **Examples** - Provide comprehensive examples
4. **Documentation** - Document all event types and payloads

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure all dependencies are installed
2. **Generation Failures** - Check protoc plugin versions
3. **Linting Errors** - Fix formatting and naming issues
4. **Breaking Changes** - Validate against previous versions

### Debug Commands

```bash
# Check buf version
buf --version

# Check protoc version
protoc --version

# List installed plugins
ls $(go env GOPATH)/bin/protoc-gen-*

# Validate buf configuration
buf config ls-breaking-rules
buf config ls-lint-rules
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting and validation
5. Generate code
6. Test the generated code
7. Submit a pull request

## License

MIT License - see LICENSE file for details
