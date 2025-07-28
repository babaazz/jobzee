# JobZee Protos Makefile
# This Makefile provides commands to generate code from protocol buffer definitions

.PHONY: help install-deps generate-go generate-python generate-all clean lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  install-deps     - Install required dependencies"
	@echo "  generate-go      - Generate Go code from protobuf"
	@echo "  generate-python  - Generate Python code from protobuf"
	@echo "  generate-all     - Generate code for all languages"
	@echo "  clean           - Clean generated files"
	@echo "  lint            - Lint protobuf files"
	@echo "  format          - Format protobuf files"

# Install dependencies
install-deps:
	@echo "Installing dependencies..."
	# Install buf CLI
	@if ! command -v buf &> /dev/null; then \
		echo "Installing buf CLI..."; \
		curl -sSL "https://github.com/bufbuild/buf/releases/latest/download/buf-$(shell uname -s)-$(shell uname -m)" -o /tmp/buf; \
		chmod +x /tmp/buf; \
		sudo mv /tmp/buf /usr/local/bin/buf; \
	fi
	# Install protoc plugins
	@go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
	@go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
	@pip install grpcio-tools

# Generate Go code
generate-go:
	@echo "Generating Go code..."
	@mkdir -p ../jobzee-backend/proto
	@buf generate --template buf.gen.go.yaml
	@echo "Go code generated successfully"

# Generate Python code
generate-python:
	@echo "Generating Python code..."
	@mkdir -p ../jobzee-agents/proto
	@buf generate --template buf.gen.python.yaml
	@echo "Python code generated successfully"

# Generate code for all languages
generate-all: generate-go generate-python
	@echo "All code generated successfully"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf ../jobzee-backend/proto
	@rm -rf ../jobzee-agents/proto
	@echo "Cleanup completed"

# Lint protobuf files
lint:
	@echo "Linting protobuf files..."
	@buf lint
	@echo "Linting completed"

# Format protobuf files
format:
	@echo "Formatting protobuf files..."
	@buf format -w
	@echo "Formatting completed"

# Validate protobuf files
validate:
	@echo "Validating protobuf files..."
	@buf breaking --against '.git#branch=main'
	@echo "Validation completed"

# Generate documentation
docs:
	@echo "Generating documentation..."
	@buf generate --template buf.gen.doc.yaml
	@echo "Documentation generated successfully" 