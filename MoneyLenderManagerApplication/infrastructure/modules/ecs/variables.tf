variable "project_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "ecs_security_group_id" {
  type = string
}

variable "ecs_execution_role_arn" {
  type = string
}

variable "service_task_role_arns" {
  description = "Map of service name to task role ARN"
  type        = map(string)
}

variable "service_images" {
  description = "Map of service name to ECR image URI"
  type        = map(string)
}

variable "service_env_vars" {
  description = "Map of service name to list of env var objects"
  type        = map(list(object({ name = string, value = string })))
}

variable "cpu" {
  type    = number
  default = 256
}

variable "memory" {
  type    = number
  default = 512
}
