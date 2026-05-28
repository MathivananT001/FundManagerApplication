variable "project_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN for JWT authorizer"
  type        = string
}

variable "vpc_link_target_arns" {
  description = "NLB ARNs for VPC Link to ECS services"
  type        = list(string)
  default     = []
}

variable "report_lambda_arn" {
  description = "Report service Lambda ARN"
  type        = string
}

variable "report_lambda_invoke_arn" {
  description = "Report service Lambda invoke ARN"
  type        = string
}
