# JobZee Infrastructure Documentation

## Table of Contents

1. [Overview](#overview)
2. [Infrastructure Architecture](#infrastructure-architecture)
3. [Kubernetes Manifests](#kubernetes-manifests)
4. [Terraform Modules](#terraform-modules)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoring & Logging](#monitoring--logging)
7. [Security](#security)
8. [Deployment](#deployment)

## Overview

The JobZee Infrastructure repository contains all infrastructure-as-code, deployment configurations, and operational tooling for the JobZee platform. It provides automated provisioning, deployment, and management of the entire platform infrastructure.

### Key Features

- **Infrastructure as Code**: Terraform modules for cloud resource provisioning
- **Kubernetes Orchestration**: Complete K8s manifests for application deployment
- **CI/CD Pipeline**: Jenkins-based automated deployment pipeline
- **Monitoring Stack**: Prometheus, Grafana, and logging infrastructure
- **Security**: RBAC, network policies, and security configurations
- **Multi-Environment**: Support for development, staging, and production

## Infrastructure Architecture

### Cloud Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLOUD INFRASTRUCTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   Load Balancer │    │   Kubernetes    │    │   Database    │ │
│  │                 │    │   Cluster       │    │   Layer       │ │
│  │ • ALB/NLB       │    │ • EKS/GKE       │    │ • RDS/Cloud   │ │
│  │ • SSL/TLS       │    │ • Node Groups   │    │   SQL         │ │
│  │ • Health Checks │    │ • Auto Scaling  │    │ • Redis       │ │
│  │ • WAF           │    │ • RBAC          │    │   Cluster     │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   Storage       │    │   Networking    │    │   Security    │ │
│  │   Layer         │    │                 │    │               │ │
│  │                 │    │ • VPC           │    │ • IAM Roles   │ │
│  │ • S3/MinIO      │    │ • Subnets       │    │ • Security    │ │
│  │ • EBS Volumes   │    │ • Route Tables  │    │   Groups      │ │
│  │ • Backup        │    │ • NAT Gateway   │    │ • KMS Keys    │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   Ingress       │    │   Services      │    │   Pods        │ │
│  │   Controller    │    │                 │    │               │ │
│  │                 │    │ • API Gateway   │    │ • Frontend    │ │
│  │ • NGINX         │    │ • Job Service   │    │ • Backend     │ │
│  │ • SSL/TLS       │    │ • Candidate     │    │ • Agents      │ │
│  │ • Rate Limiting │    │   Service       │    │ • Monitoring  │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   ConfigMaps    │    │   Secrets       │    │   Storage     │ │
│  │   & Secrets     │    │                 │    │               │ │
│  │                 │    │ • Database      │    │ • Persistent  │ │
│  │ • App Config    │    │   Credentials   │    │   Volumes     │ │
│  │ • Environment   │    │ • API Keys      │    │ • ConfigMaps  │ │
│  │   Variables     │    │ • JWT Secrets   │    │ • Secrets     │ │
│  └─────────────────┘    └─────────────────┘    └───────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Kubernetes Manifests

### Namespace Configuration

```yaml
# kubernetes/manifests/namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: jobzee
  labels:
    name: jobzee
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: jobzee-monitoring
  labels:
    name: jobzee-monitoring
    environment: production
```

### ConfigMaps and Secrets

```yaml
# kubernetes/manifests/configmaps.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: jobzee
data:
  # Database Configuration
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "jobzee"

  # Redis Configuration
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"

  # Kafka Configuration
  KAFKA_BROKERS: "kafka-service:9092"

  # Vector Database
  VECTOR_DB_URL: "http://qdrant-service:6333"

  # MinIO Configuration
  MINIO_ENDPOINT: "minio-service:9000"
  MINIO_ACCESS_KEY: "minioadmin"

  # Service Ports
  API_PORT: "8080"
  FRONTEND_PORT: "3000"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: jobzee
type: Opaque
data:
  # Base64 encoded secrets
  DB_PASSWORD: cGFzc3dvcmQ= # password
  REDIS_PASSWORD: ""
  JWT_SECRET: eW91ci1zZWNyZXQta2V5LWNoYW5nZS1pbi1wcm9kdWN0aW9u
  OPENAI_API_KEY: <base64-encoded-openai-key>
  GITHUB_TOKEN: <base64-encoded-github-token>
```

### Service Deployments

```yaml
# kubernetes/manifests/deployments.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: jobzee
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
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: DB_PASSWORD
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: JWT_SECRET
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
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
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: jobzee
spec:
  selector:
    app: api-service
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

### Ingress Configuration

```yaml
# kubernetes/manifests/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jobzee-ingress
  namespace: jobzee
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.jobzee.com
        - app.jobzee.com
      secretName: jobzee-tls
  rules:
    - host: api.jobzee.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
    - host: app.jobzee.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 3000
```

## Terraform Modules

### EKS Cluster Module

```hcl
# terraform/modules/eks_cluster/main.tf
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  cluster_endpoint_public_access = true

  vpc_id     = var.vpc_id
  subnet_ids = var.private_subnets

  eks_managed_node_groups = {
    general = {
      desired_capacity = 2
      min_capacity     = 1
      max_capacity     = 5

      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"

      labels = {
        Environment = var.environment
        NodeGroup   = "general"
      }

      tags = {
        ExtraTag = "eks-node-group"
      }
    }

    spot = {
      desired_capacity = 2
      min_capacity     = 1
      max_capacity     = 5

      instance_types = ["t3.medium"]
      capacity_type  = "SPOT"

      labels = {
        Environment = var.environment
        NodeGroup   = "spot"
      }

      taints = [{
        key    = "dedicated"
        value  = "spot"
        effect = "NO_SCHEDULE"
      }]

      tags = {
        ExtraTag = "eks-node-group"
      }
    }
  }

  tags = var.tags
}

# Outputs
output "cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}
```

### RDS Database Module

```hcl
# terraform/modules/rds/main.tf
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 5.0"

  identifier = var.identifier

  engine               = var.engine
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  allocated_storage    = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage

  db_name  = var.db_name
  username = var.username
  port     = var.port

  vpc_security_group_ids = var.vpc_security_group_ids
  subnet_ids             = var.subnet_ids

  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window

  skip_final_snapshot = var.skip_final_snapshot

  tags = var.tags
}

# Security Group
resource "aws_security_group" "rds" {
  name_prefix = "${var.identifier}-rds-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.port
    to_port         = var.port
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.identifier}-rds"
  })
}
```

## CI/CD Pipeline

### Jenkins Pipeline

```groovy
// ci-cd/Jenkinsfile
pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        KUBECONFIG = credentials('kubeconfig')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Frontend') {
            steps {
                dir('jobzee-frontend') {
                    sh 'npm ci'
                    sh 'npm run build'
                    sh 'npm run test'
                }
            }
        }

        stage('Build Backend') {
            steps {
                dir('jobzee-backend') {
                    sh 'go mod download'
                    sh 'go test ./...'
                    sh 'go build -o bin/api cmd/api/main.go'
                    sh 'go build -o bin/jobservice cmd/jobservice/main.go'
                    sh 'go build -o bin/candidateservice cmd/candidateservice/main.go'
                    sh 'go build -o bin/agentservice cmd/agentservice/main.go'
                }
            }
        }

        stage('Build Agents') {
            steps {
                dir('jobzee-agents') {
                    sh 'pip install -r requirements.txt'
                    sh 'python -m pytest tests/'
                }
            }
        }

        stage('Build Docker Images') {
            parallel {
                stage('Frontend Image') {
                    steps {
                        dir('jobzee-frontend') {
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-frontend:${IMAGE_TAG} ."
                            sh "docker push ${DOCKER_REGISTRY}/jobzee-frontend:${IMAGE_TAG}"
                        }
                    }
                }

                stage('Backend Images') {
                    steps {
                        dir('jobzee-backend') {
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-api:${IMAGE_TAG} --target api ."
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-jobservice:${IMAGE_TAG} --target jobservice ."
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-candidateservice:${IMAGE_TAG} --target candidateservice ."
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-agentservice:${IMAGE_TAG} --target agentservice ."

                            sh "docker push ${DOCKER_REGISTRY}/jobzee-api:${IMAGE_TAG}"
                            sh "docker push ${DOCKER_REGISTRY}/jobzee-jobservice:${IMAGE_TAG}"
                            sh "docker push ${DOCKER_REGISTRY}/jobzee-candidateservice:${IMAGE_TAG}"
                            sh "docker push ${DOCKER_REGISTRY}/jobzee-agentservice:${IMAGE_TAG}"
                        }
                    }
                }

                stage('Agent Images') {
                    steps {
                        dir('jobzee-agents') {
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-job-finder-agent:${IMAGE_TAG} --target job-finder ."
                            sh "docker build -t ${DOCKER_REGISTRY}/jobzee-candidate-finder-agent:${IMAGE_TAG} --target candidate-finder ."

                            sh "docker push ${DOCKER_REGISTRY}/jobzee-job-finder-agent:${IMAGE_TAG}"
                            sh "docker push ${DOCKER_REGISTRY}/jobzee-candidate-finder-agent:${IMAGE_TAG}"
                        }
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                dir('jobzee-infra') {
                    sh "kubectl config use-context staging"
                    sh "kubectl set image deployment/api-service api-service=${DOCKER_REGISTRY}/jobzee-api:${IMAGE_TAG} -n jobzee"
                    sh "kubectl set image deployment/frontend-service frontend-service=${DOCKER_REGISTRY}/jobzee-frontend:${IMAGE_TAG} -n jobzee"
                    sh "kubectl rollout status deployment/api-service -n jobzee"
                    sh "kubectl rollout status deployment/frontend-service -n jobzee"
                }
            }
        }

        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                dir('jobzee-infra') {
                    sh "kubectl config use-context production"
                    sh "kubectl set image deployment/api-service api-service=${DOCKER_REGISTRY}/jobzee-api:${IMAGE_TAG} -n jobzee"
                    sh "kubectl set image deployment/frontend-service frontend-service=${DOCKER_REGISTRY}/jobzee-frontend:${IMAGE_TAG} -n jobzee"
                    sh "kubectl rollout status deployment/api-service -n jobzee"
                    sh "kubectl rollout status deployment/frontend-service -n jobzee"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```

## Monitoring & Logging

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

scrape_configs:
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels:
          [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  - job_name: "jobzee-api"
    static_configs:
      - targets: ["api-service:8080"]
    metrics_path: "/metrics"
    scrape_interval: 30s

  - job_name: "jobzee-agents"
    static_configs:
      - targets: ["job-finder-agent:8084", "candidate-finder-agent:8085"]
    metrics_path: "/metrics"
    scrape_interval: 30s
```

### Grafana Dashboards

```json
// monitoring/grafana/dashboards/jobzee-overview.json
{
  "dashboard": {
    "id": null,
    "title": "JobZee Platform Overview",
    "tags": ["jobzee", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "id": 4,
        "title": "Agent Activity",
        "type": "stat",
        "targets": [
          {
            "expr": "agent_requests_total",
            "legendFormat": "Total Agent Requests"
          }
        ]
      }
    ]
  }
}
```

## Security

### RBAC Configuration

```yaml
# kubernetes/manifests/rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: jobzee-app-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "endpoints"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jobzee-app-binding
subjects:
  - kind: ServiceAccount
    name: jobzee-app-sa
    namespace: jobzee
roleRef:
  kind: ClusterRole
  name: jobzee-app-role
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: jobzee-app-sa
  namespace: jobzee
```

### Network Policies

```yaml
# kubernetes/manifests/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-service-policy
  namespace: jobzee
spec:
  podSelector:
    matchLabels:
      app: api-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: jobzee
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: jobzee
      ports:
        - protocol: TCP
          port: 5432 # PostgreSQL
        - protocol: TCP
          port: 6379 # Redis
        - protocol: TCP
          port: 9092 # Kafka
```

## Deployment

### Local Development Setup

```bash
# scripts/local-setup.sh
#!/bin/bash

set -e

echo "Setting up JobZee local development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create necessary directories
mkdir -p data/{postgres,redis,kafka,minio,qdrant}

# Set environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY:-"your-openai-api-key"}
export JWT_SECRET=${JWT_SECRET:-"your-secret-key-change-in-production"}

# Start infrastructure services
echo "Starting infrastructure services..."
docker-compose up -d postgres redis kafka minio qdrant

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "Running database migrations..."
docker-compose exec postgres psql -U postgres -d jobzee -f /docker-entrypoint-initdb.d/init.sql

# Start application services
echo "Starting application services..."
docker-compose up -d api-service frontend job-finder-agent candidate-finder-agent

# Wait for applications to be ready
echo "Waiting for applications to be ready..."
sleep 60

# Run health checks
echo "Running health checks..."
curl -f http://localhost:8080/health || echo "API service health check failed"
curl -f http://localhost:3000 || echo "Frontend health check failed"
curl -f http://localhost:8084/health || echo "Job finder agent health check failed"
curl -f http://localhost:8085/health || echo "Candidate finder agent health check failed"

echo "JobZee local development environment is ready!"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8080"
echo "MinIO Console: http://localhost:9001"
echo "Grafana: http://localhost:3001 (admin/admin)"
```

### Production Deployment

```bash
# scripts/deploy-production.sh
#!/bin/bash

set -e

ENVIRONMENT="production"
CLUSTER_NAME="jobzee-prod"
REGION="us-west-2"

echo "Deploying JobZee to production..."

# Initialize Terraform
cd terraform
terraform init
terraform workspace select production

# Plan and apply infrastructure
terraform plan -var-file="environments/production.tfvars" -out=production.tfplan
terraform apply production.tfplan

# Get cluster credentials
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Deploy Kubernetes manifests
kubectl apply -f kubernetes/manifests/namespaces.yaml
kubectl apply -f kubernetes/manifests/configmaps.yaml
kubectl apply -f kubernetes/manifests/secrets.yaml
kubectl apply -f kubernetes/manifests/deployments.yaml
kubectl apply -f kubernetes/manifests/services.yaml
kubectl apply -f kubernetes/manifests/ingress.yaml
kubectl apply -f kubernetes/manifests/rbac.yaml
kubectl apply -f kubernetes/manifests/network-policies.yaml

# Deploy monitoring stack
kubectl apply -f kubernetes/monitoring/

# Wait for deployments to be ready
kubectl rollout status deployment/api-service -n jobzee
kubectl rollout status deployment/frontend-service -n jobzee
kubectl rollout status deployment/job-finder-agent -n jobzee
kubectl rollout status deployment/candidate-finder-agent -n jobzee

echo "Production deployment completed successfully!"
```

---

## Conclusion

The JobZee Infrastructure repository provides:

- **Infrastructure as Code**: Complete Terraform modules for cloud resource provisioning
- **Kubernetes Orchestration**: Production-ready K8s manifests for all services
- **Automated CI/CD**: Jenkins pipeline for continuous deployment
- **Monitoring Stack**: Prometheus, Grafana, and comprehensive alerting
- **Security**: RBAC, network policies, and security best practices
- **Multi-Environment**: Support for development, staging, and production
- **Operational Excellence**: Health checks, logging, and monitoring

This infrastructure ensures the JobZee platform is deployed reliably, securely, and efficiently across all environments.
