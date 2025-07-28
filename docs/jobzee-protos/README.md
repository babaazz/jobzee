# JobZee Protos Documentation

## Table of Contents

1. [Overview](#overview)
2. [Protocol Definitions](#protocol-definitions)
3. [gRPC Services](#grpc-services)
4. [AsyncAPI Specifications](#asyncapi-specifications)
5. [Code Generation](#code-generation)
6. [Versioning Strategy](#versioning-strategy)
7. [Usage Examples](#usage-examples)

## Overview

The JobZee Protos repository contains all protocol definitions for the JobZee platform, including gRPC service definitions, AsyncAPI specifications, and protocol buffer schemas. This repository serves as the single source of truth for all API contracts and message formats.

### Key Features

- **gRPC Service Definitions**: Protocol buffer definitions for all microservices
- **AsyncAPI Specifications**: Event-driven API documentation
- **Code Generation**: Automated code generation for multiple languages
- **Version Management**: Semantic versioning for API contracts
- **Documentation**: Auto-generated API documentation

## Protocol Definitions

### Repository Structure

```
jobzee-protos/
├── buf.yaml                 # Buf configuration
├── buf.gen.go.yaml         # Go code generation config
├── buf.gen.python.yaml     # Python code generation config
├── Makefile                # Build and generation scripts
├── grpc/                   # gRPC service definitions
│   ├── agent_service.proto
│   ├── candidate_service.proto
│   └── job_service.proto
├── asyncapi/               # AsyncAPI specifications
│   └── jobs-posted.yml
└── README.md
```

### Buf Configuration

```yaml
# buf.yaml
version: v1
name: jobzee-protos
deps:
  - buf.build/googleapis/googleapis
lint:
  use:
    - DEFAULT
breaking:
  use:
    - FILE
```

## gRPC Services

### Job Service

```protobuf
// grpc/job_service.proto
syntax = "proto3";

package job_service;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

service JobService {
  // Job CRUD operations
  rpc CreateJob(CreateJobRequest) returns (Job);
  rpc GetJob(GetJobRequest) returns (Job);
  rpc ListJobs(ListJobsRequest) returns (ListJobsResponse);
  rpc UpdateJob(UpdateJobRequest) returns (Job);
  rpc DeleteJob(DeleteJobRequest) returns (google.protobuf.Empty);

  // Job search and matching
  rpc SearchJobs(SearchJobsRequest) returns (SearchJobsResponse);
  rpc GetJobMatches(GetJobMatchesRequest) returns (GetJobMatchesResponse);

  // Job applications
  rpc ApplyForJob(ApplyForJobRequest) returns (Application);
  rpc GetApplications(GetApplicationsRequest) returns (GetApplicationsResponse);
  rpc UpdateApplicationStatus(UpdateApplicationStatusRequest) returns (Application);
}

message Job {
  string id = 1;
  string title = 2;
  string company = 3;
  string location = 4;
  string description = 5;
  repeated string requirements = 6;
  int32 salary_min = 7;
  int32 salary_max = 8;
  string job_type = 9;
  string experience_level = 10;
  string created_by = 11;
  google.protobuf.Timestamp created_at = 12;
  google.protobuf.Timestamp updated_at = 13;
  bool is_active = 14;
}

message CreateJobRequest {
  string title = 1;
  string company = 2;
  string location = 3;
  string description = 4;
  repeated string requirements = 5;
  int32 salary_min = 6;
  int32 salary_max = 7;
  string job_type = 8;
  string experience_level = 9;
  string created_by = 10;
}

message GetJobRequest {
  string id = 1;
}

message ListJobsRequest {
  int32 page = 1;
  int32 per_page = 2;
  string company = 3;
  string location = 4;
  string job_type = 5;
  string experience_level = 6;
}

message ListJobsResponse {
  repeated Job jobs = 1;
  int32 total = 2;
  int32 page = 3;
  int32 per_page = 4;
  int32 total_pages = 5;
}

message SearchJobsRequest {
  string query = 1;
  repeated string skills = 2;
  string location = 3;
  string job_type = 4;
  int32 page = 5;
  int32 per_page = 6;
}

message SearchJobsResponse {
  repeated Job jobs = 1;
  int32 total = 2;
  map<string, float> match_scores = 3;
}

message Application {
  string id = 1;
  string job_id = 2;
  string candidate_id = 3;
  string status = 4;
  string cover_letter = 5;
  string resume_url = 6;
  float match_score = 7;
  google.protobuf.Timestamp applied_at = 8;
  google.protobuf.Timestamp updated_at = 9;
}

message ApplyForJobRequest {
  string job_id = 1;
  string candidate_id = 2;
  string cover_letter = 3;
  string resume_url = 4;
}
```

### Candidate Service

```protobuf
// grpc/candidate_service.proto
syntax = "proto3";

package candidate_service;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

service CandidateService {
  // Candidate CRUD operations
  rpc CreateCandidate(CreateCandidateRequest) returns (Candidate);
  rpc GetCandidate(GetCandidateRequest) returns (Candidate);
  rpc ListCandidates(ListCandidatesRequest) returns (ListCandidatesResponse);
  rpc UpdateCandidate(UpdateCandidateRequest) returns (Candidate);
  rpc DeleteCandidate(DeleteCandidateRequest) returns (google.protobuf.Empty);

  // Candidate search and matching
  rpc SearchCandidates(SearchCandidatesRequest) returns (SearchCandidatesResponse);
  rpc GetCandidateMatches(GetCandidateMatchesRequest) returns (GetCandidateMatchesResponse);

  // Profile management
  rpc UpdateProfile(UpdateProfileRequest) returns (Candidate);
  rpc UploadResume(UploadResumeRequest) returns (UploadResumeResponse);
  rpc AnalyzeProfile(AnalyzeProfileRequest) returns (AnalyzeProfileResponse);
}

message Candidate {
  string id = 1;
  string user_id = 2;
  string headline = 3;
  string summary = 4;
  repeated string skills = 5;
  int32 experience_years = 6;
  repeated string education = 7;
  map<string, string> portfolio_links = 8;
  string resume_url = 9;
  string github_url = 10;
  string linkedin_url = 11;
  google.protobuf.Timestamp created_at = 12;
  google.protobuf.Timestamp updated_at = 13;
}

message CreateCandidateRequest {
  string user_id = 1;
  string headline = 2;
  string summary = 3;
  repeated string skills = 4;
  int32 experience_years = 5;
  repeated string education = 6;
  map<string, string> portfolio_links = 7;
}

message SearchCandidatesRequest {
  string query = 1;
  repeated string skills = 2;
  int32 min_experience = 3;
  int32 max_experience = 4;
  string location = 5;
  int32 page = 6;
  int32 per_page = 7;
}

message SearchCandidatesResponse {
  repeated Candidate candidates = 1;
  int32 total = 2;
  map<string, float> match_scores = 3;
}

message AnalyzeProfileResponse {
  string candidate_id = 1;
  map<string, float> skill_scores = 2;
  string experience_level = 3;
  repeated string recommendations = 4;
  float overall_score = 5;
}
```

### Agent Service

```protobuf
// grpc/agent_service.proto
syntax = "proto3";

package agent_service;

import "google/protobuf/timestamp.proto";

service AgentService {
  // Agent communication
  rpc ProcessJobRequest(JobRequest) returns (JobResponse);
  rpc ProcessCandidateRequest(CandidateRequest) returns (CandidateResponse);
  rpc StreamAgentChat(stream ChatMessage) returns (stream ChatResponse);

  // Agent management
  rpc GetAgentStatus(AgentStatusRequest) returns (AgentStatus);
  rpc UpdateAgentStatus(UpdateAgentStatusRequest) returns (AgentStatus);

  // Agent coordination
  rpc CoordinateAgents(CoordinateRequest) returns (CoordinateResponse);
}

message JobRequest {
  string request_id = 1;
  string candidate_id = 2;
  string message = 3;
  map<string, string> preferences = 4;
  google.protobuf.Timestamp timestamp = 5;
}

message JobResponse {
  string request_id = 1;
  repeated JobRecommendation recommendations = 2;
  string reasoning = 3;
  repeated string next_steps = 4;
  google.protobuf.Timestamp timestamp = 5;
}

message JobRecommendation {
  string job_id = 1;
  string title = 2;
  string company = 3;
  float match_score = 4;
  string reasoning = 5;
  repeated string highlights = 6;
}

message CandidateRequest {
  string request_id = 1;
  string job_id = 2;
  string message = 3;
  map<string, string> criteria = 4;
  google.protobuf.Timestamp timestamp = 5;
}

message CandidateResponse {
  string request_id = 1;
  repeated CandidateRecommendation candidates = 2;
  string reasoning = 3;
  repeated string next_steps = 4;
  google.protobuf.Timestamp timestamp = 5;
}

message CandidateRecommendation {
  string candidate_id = 1;
  string name = 2;
  string headline = 3;
  float match_score = 4;
  string reasoning = 5;
  repeated string strengths = 6;
}

message ChatMessage {
  string session_id = 1;
  string user_id = 2;
  string message = 3;
  string agent_type = 4;
  google.protobuf.Timestamp timestamp = 5;
}

message ChatResponse {
  string session_id = 1;
  string response = 2;
  string agent_type = 3;
  repeated string suggestions = 4;
  google.protobuf.Timestamp timestamp = 5;
}

message AgentStatus {
  string agent_id = 1;
  string agent_type = 2;
  string status = 3;
  int32 active_sessions = 4;
  float cpu_usage = 5;
  float memory_usage = 6;
  google.protobuf.Timestamp last_heartbeat = 7;
}
```

## AsyncAPI Specifications

### Jobs Posted Event

```yaml
# asyncapi/jobs-posted.yml
asyncapi: 2.6.0
info:
  title: JobZee Jobs API
  version: 1.0.0
  description: Event-driven API for job-related events

servers:
  kafka:
    url: kafka://localhost:9092
    protocol: kafka

channels:
  jobs.posted:
    publish:
      summary: Job posted event
      message:
        $ref: "#/components/messages/JobPosted"
    subscribe:
      summary: Subscribe to job posted events
      message:
        $ref: "#/components/messages/JobPosted"

  jobs.updated:
    publish:
      summary: Job updated event
      message:
        $ref: "#/components/messages/JobUpdated"

  jobs.deleted:
    publish:
      summary: Job deleted event
      message:
        $ref: "#/components/messages/JobDeleted"

  candidates.created:
    publish:
      summary: Candidate created event
      message:
        $ref: "#/components/messages/CandidateCreated"

  candidates.updated:
    publish:
      summary: Candidate updated event
      message:
        $ref: "#/components/messages/CandidateUpdated"

  matches.created:
    publish:
      summary: Job-candidate match created event
      message:
        $ref: "#/components/messages/MatchCreated"

  applications.created:
    publish:
      summary: Job application created event
      message:
        $ref: "#/components/messages/ApplicationCreated"

components:
  messages:
    JobPosted:
      payload:
        type: object
        properties:
          event_id:
            type: string
            format: uuid
          event_type:
            type: string
            enum: [job.posted]
          version:
            type: string
            pattern: '^1\.0$'
          timestamp:
            type: string
            format: date-time
          data:
            $ref: "#/components/schemas/Job"
          metadata:
            $ref: "#/components/schemas/EventMetadata"
        required:
          - event_id
          - event_type
          - version
          - timestamp
          - data
          - metadata

    JobUpdated:
      payload:
        type: object
        properties:
          event_id:
            type: string
            format: uuid
          event_type:
            type: string
            enum: [job.updated]
          version:
            type: string
            pattern: '^1\.0$'
          timestamp:
            type: string
            format: date-time
          data:
            $ref: "#/components/schemas/Job"
          metadata:
            $ref: "#/components/schemas/EventMetadata"
        required:
          - event_id
          - event_type
          - version
          - timestamp
          - data
          - metadata

    MatchCreated:
      payload:
        type: object
        properties:
          event_id:
            type: string
            format: uuid
          event_type:
            type: string
            enum: [match.created]
          version:
            type: string
            pattern: '^1\.0$'
          timestamp:
            type: string
            format: date-time
          data:
            type: object
            properties:
              match_id:
                type: string
                format: uuid
              job_id:
                type: string
                format: uuid
              candidate_id:
                type: string
                format: uuid
              match_score:
                type: number
                minimum: 0
                maximum: 1
              matched_by:
                type: string
                enum: [job-finder-agent, candidate-finder-agent]
              matched_at:
                type: string
                format: date-time
            required:
              - match_id
              - job_id
              - candidate_id
              - match_score
              - matched_by
              - matched_at
          metadata:
            $ref: "#/components/schemas/EventMetadata"
        required:
          - event_id
          - event_type
          - version
          - timestamp
          - data
          - metadata

  schemas:
    Job:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
          minLength: 1
          maxLength: 255
        company:
          type: string
          minLength: 1
          maxLength: 255
        location:
          type: string
          minLength: 1
          maxLength: 255
        description:
          type: string
          minLength: 1
        requirements:
          type: array
          items:
            type: string
        salary_min:
          type: integer
          minimum: 0
        salary_max:
          type: integer
          minimum: 0
        job_type:
          type: string
          enum: [full-time, part-time, contract, internship]
        experience_level:
          type: string
          enum: [entry, junior, mid, senior, lead, executive]
        created_by:
          type: string
          format: uuid
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
        is_active:
          type: boolean
      required:
        - id
        - title
        - company
        - location
        - description
        - requirements
        - job_type
        - experience_level
        - created_by
        - created_at
        - updated_at
        - is_active

    EventMetadata:
      type: object
      properties:
        source:
          type: string
          description: Service that generated the event
        correlation_id:
          type: string
          format: uuid
          description: Correlation ID for tracing
        user_agent:
          type: string
          description: User agent that triggered the event
      required:
        - source
        - correlation_id
```

## Code Generation

### Go Code Generation

```yaml
# buf.gen.go.yaml
version: v1
managed:
  enabled: true
  go_package_prefix:
    default: github.com/jobzee/protos/gen/go
plugins:
  - plugin: buf.build/protocolbuffers/go
    out: gen/go
    opt: paths=source_relative
  - plugin: buf.build/grpc/go
    out: gen/go
    opt: paths=source_relative
```

### Python Code Generation

```yaml
# buf.gen.python.yaml
version: v1
managed:
  enabled: true
plugins:
  - plugin: buf.build/grpc/python
    out: gen/python
  - plugin: buf.build/grpc/grpcio-tools
    out: gen/python
```

### Makefile for Code Generation

```makefile
# Makefile
.PHONY: generate clean lint breaking

# Generate code for all languages
generate: generate-go generate-python

# Generate Go code
generate-go:
	buf generate --template buf.gen.go.yaml

# Generate Python code
generate-python:
	buf generate --template buf.gen.python.yaml

# Clean generated code
clean:
	rm -rf gen/

# Lint protocol definitions
lint:
	buf lint

# Check for breaking changes
breaking:
	buf breaking --against '.git#branch=main'

# Format protocol files
format:
	buf format -w

# Install buf CLI
install-buf:
	curl -sSL \
		"https://github.com/bufbuild/buf/releases/download/v1.28.1/buf-$(uname -s)-$(uname -m)" \
		-o "$(go env GOPATH)/bin/buf" && \
	chmod +x "$(go env GOPATH)/bin/buf"

# Update dependencies
update-deps:
	buf mod update

# Generate documentation
docs:
	buf generate --template buf.gen.doc.yaml
```

## Versioning Strategy

### Semantic Versioning

The JobZee Protos repository follows semantic versioning (SemVer) for API contracts:

- **Major Version (X.0.0)**: Breaking changes that require client updates
- **Minor Version (X.Y.0)**: New features that are backward compatible
- **Patch Version (X.Y.Z)**: Bug fixes and backward compatible changes

### Breaking Change Guidelines

Breaking changes include:

- Removing fields from messages
- Changing field types
- Removing RPC methods
- Changing service names
- Modifying enum values

Non-breaking changes include:

- Adding new fields (with default values)
- Adding new RPC methods
- Adding new services
- Adding new enum values
- Adding new message types

### Migration Strategy

```protobuf
// Example of backward compatible field addition
message Job {
  string id = 1;
  string title = 2;
  string company = 3;
  // New field added in v1.1.0
  string department = 4;  // Optional field with default value
}

// Example of field deprecation
message Candidate {
  string id = 1;
  string name = 2;
  // Deprecated field - use full_name instead
  string first_name = 3 [deprecated = true];
  string full_name = 4;
}
```

## Usage Examples

### Go Client Usage

```go
// Example Go client using generated code
package main

import (
    "context"
    "log"

    "github.com/jobzee/protos/gen/go/job_service"
    "google.golang.org/grpc"
)

func main() {
    // Connect to gRPC server
    conn, err := grpc.Dial("localhost:8081", grpc.WithInsecure())
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    // Create client
    client := job_service.NewJobServiceClient(conn)

    // Create job request
    req := &job_service.CreateJobRequest{
        Title:           "Senior Software Engineer",
        Company:         "Tech Corp",
        Location:        "San Francisco, CA",
        Description:     "We are looking for a senior engineer...",
        Requirements:    []string{"Go", "Python", "Kubernetes"},
        SalaryMin:       120000,
        SalaryMax:       180000,
        JobType:         "full-time",
        ExperienceLevel: "senior",
        CreatedBy:       "user-123",
    }

    // Call service
    job, err := client.CreateJob(context.Background(), req)
    if err != nil {
        log.Fatal(err)
    }

    log.Printf("Created job: %s", job.Id)
}
```

### Python Client Usage

```python
# Example Python client using generated code
import grpc
from jobzee_protos.gen.python import job_service_pb2
from jobzee_protos.gen.python import job_service_pb2_grpc

def create_job():
    # Connect to gRPC server
    with grpc.insecure_channel('localhost:8081') as channel:
        stub = job_service_pb2_grpc.JobServiceStub(channel)

        # Create job request
        request = job_service_pb2.CreateJobRequest(
            title="Senior Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            description="We are looking for a senior engineer...",
            requirements=["Go", "Python", "Kubernetes"],
            salary_min=120000,
            salary_max=180000,
            job_type="full-time",
            experience_level="senior",
            created_by="user-123"
        )

        # Call service
        response = stub.CreateJob(request)
        print(f"Created job: {response.id}")

if __name__ == "__main__":
    create_job()
```

### Event Consumer Usage

```python
# Example Kafka event consumer
from kafka import KafkaConsumer
import json
from jobzee_protos.gen.python import job_service_pb2

def consume_job_events():
    consumer = KafkaConsumer(
        'jobs.posted',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    for message in consumer:
        event = message.value

        # Parse event data
        job_data = event['data']
        job = job_service_pb2.Job(
            id=job_data['id'],
            title=job_data['title'],
            company=job_data['company'],
            location=job_data['location'],
            description=job_data['description'],
            requirements=job_data['requirements']
        )

        print(f"New job posted: {job.title} at {job.company}")

        # Process job (e.g., update search index, notify agents)
        process_new_job(job)

def process_new_job(job):
    # Update vector database
    update_job_embeddings(job)

    # Notify agents
    notify_job_finder_agent(job)

    # Update analytics
    update_job_analytics(job)
```

---

## Conclusion

The JobZee Protos repository provides:

- **Standardized APIs**: Consistent gRPC service definitions across all microservices
- **Event Contracts**: Well-defined AsyncAPI specifications for event-driven communication
- **Code Generation**: Automated code generation for multiple programming languages
- **Version Management**: Semantic versioning with clear migration strategies
- **Documentation**: Auto-generated API documentation and examples

This repository serves as the foundation for all inter-service communication in the JobZee platform, ensuring consistency, reliability, and maintainability across the entire system.
