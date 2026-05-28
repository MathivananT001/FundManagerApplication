output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "rds_secret_arn" {
  value = aws_secretsmanager_secret.rds_password.arn
}

output "dynamodb_sessions_arn" {
  value = aws_dynamodb_table.sessions.arn
}

output "dynamodb_auction_connections_arn" {
  value = aws_dynamodb_table.auction_connections.arn
}

output "dynamodb_auction_state_arn" {
  value = aws_dynamodb_table.auction_state.arn
}

output "dynamodb_notification_logs_arn" {
  value = aws_dynamodb_table.notification_logs.arn
}

output "dynamodb_device_tokens_arn" {
  value = aws_dynamodb_table.device_tokens.arn
}

output "dynamodb_bot_activity_log_arn" {
  value = aws_dynamodb_table.bot_activity_log.arn
}
