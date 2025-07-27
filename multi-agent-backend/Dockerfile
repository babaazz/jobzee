# Build stage
FROM golang:1.21-alpine AS builder

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

# Production stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy binaries from builder
COPY --from=builder /app/api .
COPY --from=builder /app/jobservice .
COPY --from=builder /app/candidateservice .

# Expose ports
EXPOSE 8080 9090 9091

# Default command (can be overridden)
CMD ["./api"] 