variable "project_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "isolated_subnet_ids" {
  type = list(string)
}

variable "rds_security_group_id" {
  type = string
}

variable "rds_instance_class" {
  type = string
}

variable "rds_allocated_storage" {
  type = number
}

variable "rds_db_name" {
  type = string
}

variable "rds_master_username" {
  type = string
}

variable "rds_multi_az" {
  type = bool
}

variable "rds_backup_retention" {
  type = number
}

variable "rds_deletion_protection" {
  type = bool
}
