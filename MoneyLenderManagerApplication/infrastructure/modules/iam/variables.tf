variable "project_prefix" {
  type = string
}

variable "environment" {
  type = string
}

variable "rds_secret_arn" {
  type = string
}

variable "dynamodb_sessions_arn" {
  type = string
}

variable "dynamodb_auction_connections_arn" {
  type = string
}

variable "dynamodb_auction_state_arn" {
  type = string
}

variable "dynamodb_notification_logs_arn" {
  type = string
}

variable "dynamodb_device_tokens_arn" {
  type = string
}

variable "dynamodb_bot_activity_log_arn" {
  type = string
}

variable "payment_proofs_bucket_arn" {
  type = string
}

variable "reports_bucket_arn" {
  type = string
}

variable "archives_bucket_arn" {
  type = string
}
