variable "project_prefix" {
  description = "Prefix for all resource names"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

# VPC
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "nat_gateway_count" {
  description = "Number of NAT gateways (1 for dev, 2 for prod)"
  type        = number
}

# RDS
variable "rds_instance_class" {
  description = "RDS instance type"
  type        = string
}

variable "rds_allocated_storage" {
  description = "RDS storage in GB"
  type        = number
}

variable "rds_db_name" {
  description = "RDS database name"
  type        = string
}

variable "rds_master_username" {
  description = "RDS master username"
  type        = string
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
}

variable "rds_backup_retention" {
  description = "RDS backup retention in days"
  type        = number
}

variable "rds_deletion_protection" {
  description = "Enable deletion protection for RDS"
  type        = bool
}

# Monitoring
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
}

variable "enable_xray" {
  description = "Enable X-Ray tracing"
  type        = bool
}

# Cognito
variable "google_client_id" {
  description = "Google OAuth Client ID for Cognito"
  type        = string
  default     = ""
}

variable "google_client_secret" {
  description = "Google OAuth Client Secret for Cognito"
  type        = string
  default     = ""
  sensitive   = true
}
