# OVH Cloud Configuration
variable "ovh_project_id" {
  description = "OVH Cloud project ID"
  type        = string
}

variable "region" {
  description = "OVH Cloud region"
  type        = string
  default     = "GRA7"
}

# Cluster Configuration
variable "cluster_name" {
  description = "Name of the Kubernetes cluster"
  type        = string
  default     = "jobzee-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version to install"
  type        = string
  default     = "1.27"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

# Network Configuration
variable "vlan_id" {
  description = "VLAN ID for the VPC"
  type        = number
  default     = null
}

variable "private_subnet_cidr" {
  description = "CIDR block for private subnet"
  type        = string
  default     = "10.0.10.0/24"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.20.0/24"
}

variable "pod_cidr" {
  description = "CIDR block for Kubernetes pods"
  type        = string
  default     = "10.244.0.0/16"
}

variable "service_cidr" {
  description = "CIDR block for Kubernetes services"
  type        = string
  default     = "10.96.0.0/12"
}

# Instance Configuration
variable "image_id" {
  description = "OVH Cloud image ID (Ubuntu 22.04 recommended)"
  type        = string
  default     = "Ubuntu 22.04"
}

variable "control_plane_flavor" {
  description = "OVH Cloud flavor for control plane nodes"
  type        = string
  default     = "b2-7"  # 2 vCPUs, 7GB RAM
}

variable "worker_node_flavor" {
  description = "OVH Cloud flavor for worker nodes"
  type        = string
  default     = "b2-15" # 2 vCPUs, 15GB RAM
}

variable "control_plane_count" {
  description = "Number of control plane nodes"
  type        = number
  default     = 3
}

variable "worker_node_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 3
}

# SSH Configuration
variable "ssh_public_key" {
  description = "SSH public key for instance access"
  type        = string
}

# SSL Configuration
variable "ssl_certificate_id" {
  description = "OVH Cloud SSL certificate ID for HTTPS"
  type        = string
  default     = null
}

# Kubernetes Certificates
variable "ca_certificate" {
  description = "Kubernetes CA certificate"
  type        = string
  default     = ""
}

variable "client_certificate" {
  description = "Kubernetes client certificate"
  type        = string
  default     = ""
}

variable "client_key" {
  description = "Kubernetes client key"
  type        = string
  default     = ""
}

# Tags
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "jobzee"
    ManagedBy   = "terraform"
    Environment = "production"
  }
} 