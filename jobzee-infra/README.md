# JobZee Infrastructure

Infrastructure as Code (IaC) and deployment configurations for the JobZee Job Application System using Kubernetes, Helm, Terraform, and Jenkins.

## Overview

This repository contains all infrastructure-related configurations for deploying and managing the JobZee Job Application System across different environments.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Agents        │
│   (Next.js)     │    │   (Go/gRPC)     │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Kubernetes    │
                    │   (EKS)         │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   Kafka         │
│   (RDS)         │    │   (ElastiCache) │    │   (MSK)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

- **AWS CLI** - For AWS resource management
- **Terraform** - For infrastructure provisioning
- **Helm** - For Kubernetes package management
- **kubectl** - For Kubernetes cluster management
- **Docker** - For container management
- **Jenkins** - For CI/CD pipeline

## Quick Start

### Local Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd jobzee-infra

# Run the local setup script
chmod +x scripts/local-setup.sh
./scripts/local-setup.sh
```

### Production Deployment

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan the deployment
terraform plan -var-file=environments/production.tfvars

# Apply the infrastructure
terraform apply -var-file=environments/production.tfvars
```

## Project Structure

```
├── kubernetes/              # Kubernetes manifests and Helm charts
│   ├── helm/               # Helm charts for each service
│   │   ├── backend/        # Backend service chart
│   │   ├── frontend/       # Frontend service chart
│   │   └── agents/         # Agents service chart
│   └── manifests/          # Raw Kubernetes manifests
├── terraform/              # Terraform infrastructure code
│   ├── modules/            # Reusable Terraform modules
│   │   ├── eks_cluster/    # EKS cluster module
│   │   ├── vpc/           # VPC module
│   │   └── storage/       # Storage module
│   ├── environments/       # Environment-specific configurations
│   └── main.tf            # Main Terraform configuration
├── ci-cd/                 # CI/CD pipeline configurations
│   ├── Jenkinsfile        # Jenkins pipeline
│   └── github-actions.yml # GitHub Actions workflow
├── scripts/               # Utility scripts
│   └── local-setup.sh    # Local development setup
└── README.md             # This file
```

## Infrastructure Components

### Kubernetes (EKS)

The system runs on Amazon EKS with the following components:

- **EKS Cluster** - Managed Kubernetes cluster
- **Node Groups** - Worker nodes for running pods
- **Load Balancers** - Application Load Balancers for external access
- **Ingress Controllers** - NGINX ingress for routing

### Database Layer

- **PostgreSQL** - Primary database (Amazon RDS)
- **Redis** - Caching layer (Amazon ElastiCache)
- **MinIO** - Object storage (S3-compatible)

### Message Queue

- **Apache Kafka** - Event streaming platform (Amazon MSK)
- **Zookeeper** - Kafka coordination service

### Monitoring & Logging

- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **ELK Stack** - Log aggregation and analysis

## Deployment Environments

### Development

- **Namespace**: `jobzee-dev`
- **Replicas**: 1 per service
- **Resources**: Minimal
- **Auto-scaling**: Disabled

### Staging

- **Namespace**: `jobzee-staging`
- **Replicas**: 2 per service
- **Resources**: Medium
- **Auto-scaling**: Enabled

### Production

- **Namespace**: `jobzee-prod`
- **Replicas**: 3+ per service
- **Resources**: High
- **Auto-scaling**: Enabled
- **High Availability**: Multi-AZ

## Helm Charts

### Backend Chart

```bash
# Install backend chart
helm install backend ./kubernetes/helm/backend \
  --namespace jobzee-prod \
  --set image.tag=v1.0.0 \
  --set database.host=postgres-prod \
  --set redis.host=redis-prod
```

### Frontend Chart

```bash
# Install frontend chart
helm install frontend ./kubernetes/helm/frontend \
  --namespace jobzee-prod \
  --set image.tag=v1.0.0 \
  --set ingress.enabled=true
```

### Agents Chart

```bash
# Install agents chart
helm install agents ./kubernetes/helm/agents \
  --namespace jobzee-prod \
  --set image.tag=v1.0.0 \
  --set kafka.bootstrapServers=kafka-prod:9092
```

## Terraform Modules

### EKS Cluster Module

```hcl
module "eks_cluster" {
  source = "./modules/eks_cluster"

  cluster_name = "jobzee-cluster"
  kubernetes_version = "1.27"

  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  node_group_desired_size = 2
  node_group_max_size = 5
  node_group_min_size = 1
  node_group_instance_types = ["t3.medium"]
}
```

### VPC Module

```hcl
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr = "10.0.0.0/16"
  environment = "production"

  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.10.0/24", "10.0.11.0/24"]
}
```

### Storage Module

```hcl
module "storage" {
  source = "./modules/storage"

  environment = "production"

  database_name = "jobzee"
  database_username = "postgres"
  database_password = var.database_password

  redis_node_type = "cache.t3.micro"
  redis_num_cache_nodes = 1
}
```

## CI/CD Pipeline

### Jenkins Pipeline

The Jenkins pipeline includes:

1. **Code Checkout** - Clone all repositories
2. **Dependency Installation** - Install dependencies for all services
3. **Testing** - Run unit and integration tests
4. **Build** - Build Docker images
5. **Push** - Push images to registry
6. **Deploy** - Deploy to Kubernetes
7. **Health Check** - Verify deployment health
8. **Integration Tests** - Run end-to-end tests

### GitHub Actions

Alternative CI/CD using GitHub Actions:

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name jobzee-cluster
          helm upgrade --install backend ./kubernetes/helm/backend
```

## Security

### Network Security

- **VPC** - Isolated network environment
- **Security Groups** - Firewall rules for services
- **NACLs** - Network Access Control Lists
- **Private Subnets** - Services run in private subnets

### Access Control

- **IAM Roles** - Service-specific permissions
- **RBAC** - Kubernetes role-based access control
- **Secrets Management** - AWS Secrets Manager integration

### Data Protection

- **Encryption at Rest** - All data encrypted
- **Encryption in Transit** - TLS for all communications
- **Backup Strategy** - Automated backups with retention

## Monitoring & Alerting

### Metrics Collection

- **Prometheus** - Collects metrics from all services
- **Node Exporter** - System metrics from nodes
- **Custom Metrics** - Application-specific metrics

### Logging

- **Fluentd** - Log collection and forwarding
- **Elasticsearch** - Log storage and indexing
- **Kibana** - Log visualization and search

### Alerting

- **AlertManager** - Alert routing and grouping
- **Slack Integration** - Team notifications
- **PagerDuty** - Incident management

## Disaster Recovery

### Backup Strategy

- **Database Backups** - Daily automated backups
- **Configuration Backups** - Git-based configuration management
- **Data Replication** - Cross-region replication

### Recovery Procedures

1. **Infrastructure Recovery** - Terraform-based recreation
2. **Data Recovery** - Point-in-time database restoration
3. **Service Recovery** - Kubernetes deployment restoration

## Cost Optimization

### Resource Management

- **Auto-scaling** - Scale based on demand
- **Spot Instances** - Use spot instances for non-critical workloads
- **Resource Limits** - Set appropriate resource limits

### Monitoring

- **Cost Alerts** - Monitor spending and set alerts
- **Resource Utilization** - Track resource usage
- **Optimization Recommendations** - Regular cost reviews

## Troubleshooting

### Common Issues

1. **Pod Startup Failures**

   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   kubectl logs <pod-name> -n <namespace>
   ```

2. **Service Connectivity**

   ```bash
   kubectl get svc -n <namespace>
   kubectl port-forward svc/<service-name> 8080:8080
   ```

3. **Resource Issues**
   ```bash
   kubectl top pods -n <namespace>
   kubectl describe node <node-name>
   ```

### Debug Commands

```bash
# Check cluster status
kubectl cluster-info

# Check node status
kubectl get nodes

# Check pod status
kubectl get pods -A

# Check service status
kubectl get svc -A

# Check ingress status
kubectl get ingress -A
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the changes
5. Submit a pull request

## License

MIT License - see LICENSE file for details
