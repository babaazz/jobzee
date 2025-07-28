# Build stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build all services
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o api ./cmd/api
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o jobservice ./cmd/jobservice
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o candidateservice ./cmd/candidateservice
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o agentservice ./cmd/agentservice

# Production stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy binaries from builder
COPY --from=builder /app/api .
COPY --from=builder /app/jobservice .
COPY --from=builder /app/candidateservice .
COPY --from=builder /app/agentservice .

# Expose ports
EXPOSE 8080 8081 8082 8083

# Default command (can be overridden)
CMD ["./api"] 