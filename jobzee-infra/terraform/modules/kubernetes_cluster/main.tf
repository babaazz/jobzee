# Self-Managed Kubernetes Cluster Module for OVH Cloud
# This module creates a Kubernetes cluster using OVH Cloud infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    ovh = {
      source  = "ovh/ovh"
      version = "~> 0.34"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

# OVH Cloud Project
data "ovh_cloud_project" "project" {
  service_name = var.ovh_project_id
}

# OVH Cloud Region
data "ovh_cloud_project_region" "region" {
  service_name = data.ovh_cloud_project.project.service_name
  name         = var.region
}

# VPC Network
resource "ovh_cloud_project_network_private" "vpc" {
  service_name = data.ovh_cloud_project.project.service_name
  name         = "${var.cluster_name}-vpc"
  regions      = [data.ovh_cloud_project_region.region.name]
  vlan_id      = var.vlan_id
}

# Private Subnet
resource "ovh_cloud_project_network_private_subnet" "private_subnet" {
  service_name = data.ovh_cloud_project.project.service_name
  network_id   = ovh_cloud_project_network_private.vpc.id
  region       = data.ovh_cloud_project_region.region.name
  start        = var.private_subnet_cidr
  network      = var.private_subnet_cidr
  dhcp         = true
}

# Public Subnet (for load balancers)
resource "ovh_cloud_project_network_private_subnet" "public_subnet" {
  service_name = data.ovh_cloud_project.project.service_name
  network_id   = ovh_cloud_project_network_private.vpc.id
  region       = data.ovh_cloud_project_region.region.name
  start        = var.public_subnet_cidr
  network      = var.public_subnet_cidr
  dhcp         = true
}

# SSH Key for instances
resource "ovh_cloud_project_ssh_key" "ssh_key" {
  service_name = data.ovh_cloud_project.project.service_name
  name         = "${var.cluster_name}-ssh-key"
  public_key   = var.ssh_public_key
}

# Control Plane Instances
resource "ovh_cloud_project_instance" "control_plane" {
  count        = var.control_plane_count
  service_name = data.ovh_cloud_project.project.service_name
  name         = "${var.cluster_name}-cp-${count.index + 1}"
  region       = data.ovh_cloud_project_region.region.name
  image_id     = var.image_id
  flavor_id    = var.control_plane_flavor
  ssh_key_id   = ovh_cloud_project_ssh_key.ssh_key.id

  network {
    name = ovh_cloud_project_network_private.vpc.name
  }

  user_data = base64encode(templatefile("${path.module}/templates/control-plane-init.sh", {
    cluster_name = var.cluster_name
    node_index   = count.index
    is_primary   = count.index == 0
    pod_cidr     = var.pod_cidr
    service_cidr = var.service_cidr
    kube_version = var.kubernetes_version
  }))

  tags = merge(var.tags, {
    Name        = "${var.cluster_name}-cp-${count.index + 1}"
    Role        = "control-plane"
    Environment = var.environment
  })
}

# Worker Node Instances
resource "ovh_cloud_project_instance" "worker_nodes" {
  count        = var.worker_node_count
  service_name = data.ovh_cloud_project.project.service_name
  name         = "${var.cluster_name}-worker-${count.index + 1}"
  region       = data.ovh_cloud_project_region.region.name
  image_id     = var.image_id
  flavor_id    = var.worker_node_flavor
  ssh_key_id   = ovh_cloud_project_ssh_key.ssh_key.id

  network {
    name = ovh_cloud_project_network_private.vpc.name
  }

  user_data = base64encode(templatefile("${path.module}/templates/worker-node-init.sh", {
    cluster_name = var.cluster_name
    node_index   = count.index
    pod_cidr     = var.pod_cidr
    service_cidr = var.service_cidr
    kube_version = var.kubernetes_version
    control_plane_ip = ovh_cloud_project_instance.control_plane[0].ip
  }))

  tags = merge(var.tags, {
    Name        = "${var.cluster_name}-worker-${count.index + 1}"
    Role        = "worker"
    Environment = var.environment
  })
}

# Load Balancer for API Server
resource "ovh_cloud_project_loadbalancer" "api_lb" {
  service_name = data.ovh_cloud_project.project.service_name
  region       = data.ovh_cloud_project_region.region.name
  name         = "${var.cluster_name}-api-lb"
  description  = "Load balancer for Kubernetes API server"

  network_id = ovh_cloud_project_network_private.vpc.id
  subnet_id  = ovh_cloud_project_network_private_subnet.public_subnet.id
}

# Load Balancer Backend for API Server
resource "ovh_cloud_project_loadbalancer_backend" "api_backend" {
  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.api_lb.id
  name            = "api-backend"
  protocol        = "TCP"
  algorithm       = "roundrobin"
  probe_mode      = "tcp"
  probe_port      = 6443
  probe_interval  = 30
  probe_timeout   = 5
  probe_retries   = 3
}

# Load Balancer Backend Members (Control Plane Nodes)
resource "ovh_cloud_project_loadbalancer_backend_member" "api_backend_members" {
  count = var.control_plane_count

  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.api_lb.id
  backend_id      = ovh_cloud_project_loadbalancer_backend.api_backend.id
  name            = "cp-${count.index + 1}"
  address         = ovh_cloud_project_instance.control_plane[count.index].ip
  port            = 6443
  weight          = 1
}

# Load Balancer Frontend for API Server
resource "ovh_cloud_project_loadbalancer_frontend" "api_frontend" {
  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.api_lb.id
  name            = "api-frontend"
  protocol        = "TCP"
  port            = 6443
  default_backend_id = ovh_cloud_project_loadbalancer_backend.api_backend.id
}

# Load Balancer for Ingress
resource "ovh_cloud_project_loadbalancer" "ingress_lb" {
  service_name = data.ovh_cloud_project.project.service_name
  region       = data.ovh_cloud_project_region.region.name
  name         = "${var.cluster_name}-ingress-lb"
  description  = "Load balancer for Kubernetes ingress"

  network_id = ovh_cloud_project_network_private.vpc.id
  subnet_id  = ovh_cloud_project_network_private_subnet.public_subnet.id
}

# Load Balancer Backend for Ingress
resource "ovh_cloud_project_loadbalancer_backend" "ingress_backend" {
  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.ingress_lb.id
  name            = "ingress-backend"
  protocol        = "HTTP"
  algorithm       = "roundrobin"
  probe_mode      = "http"
  probe_port      = 80
  probe_interval  = 30
  probe_timeout   = 5
  probe_retries   = 3
  probe_url       = "/healthz"
}

# Load Balancer Backend Members (Worker Nodes)
resource "ovh_cloud_project_loadbalancer_backend_member" "ingress_backend_members" {
  count = var.worker_node_count

  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.ingress_lb.id
  backend_id      = ovh_cloud_project_loadbalancer_backend.ingress_backend.id
  name            = "worker-${count.index + 1}"
  address         = ovh_cloud_project_instance.worker_nodes[count.index].ip
  port            = 80
  weight          = 1
}

# Load Balancer Frontend for Ingress
resource "ovh_cloud_project_loadbalancer_frontend" "ingress_frontend" {
  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.ingress_lb.id
  name            = "ingress-frontend"
  protocol        = "HTTP"
  port            = 80
  default_backend_id = ovh_cloud_project_loadbalancer_backend.ingress_backend.id
}

# HTTPS Frontend for Ingress
resource "ovh_cloud_project_loadbalancer_frontend" "ingress_https_frontend" {
  service_name = data.ovh_cloud_project.project.service_name
  loadbalancer_id = ovh_cloud_project_loadbalancer.ingress_lb.id
  name            = "ingress-https-frontend"
  protocol        = "HTTPS"
  port            = 443
  default_backend_id = ovh_cloud_project_loadbalancer_backend.ingress_backend.id
  ssl_certificate_id = var.ssl_certificate_id
}

# Generate kubeconfig file
resource "local_file" "kubeconfig" {
  content = templatefile("${path.module}/templates/kubeconfig.tpl", {
    cluster_name = var.cluster_name
    api_server   = ovh_cloud_project_loadbalancer.api_lb.vip_address
    ca_cert      = var.ca_certificate
    client_cert  = var.client_certificate
    client_key   = var.client_key
  })
  filename = "${path.module}/kubeconfig"
}

# Outputs
output "cluster_name" {
  description = "Name of the Kubernetes cluster"
  value       = var.cluster_name
}

output "api_server_endpoint" {
  description = "Kubernetes API server endpoint"
  value       = ovh_cloud_project_loadbalancer.api_lb.vip_address
}

output "ingress_endpoint" {
  description = "Kubernetes ingress endpoint"
  value       = ovh_cloud_project_loadbalancer.ingress_lb.vip_address
}

output "control_plane_ips" {
  description = "IP addresses of control plane nodes"
  value       = ovh_cloud_project_instance.control_plane[*].ip
}

output "worker_node_ips" {
  description = "IP addresses of worker nodes"
  value       = ovh_cloud_project_instance.worker_nodes[*].ip
}

output "kubeconfig_path" {
  description = "Path to the generated kubeconfig file"
  value       = local_file.kubeconfig.filename
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = ovh_cloud_project_network_private.vpc.id
}

output "private_subnet_id" {
  description = "ID of the private subnet"
  value       = ovh_cloud_project_network_private_subnet.private_subnet.id
}

output "public_subnet_id" {
  description = "ID of the public subnet"
  value       = ovh_cloud_project_network_private_subnet.public_subnet.id
} 