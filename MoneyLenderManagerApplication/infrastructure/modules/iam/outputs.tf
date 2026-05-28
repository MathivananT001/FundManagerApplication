output "ecs_execution_role_arn" {
  value = aws_iam_role.ecs_execution.arn
}

output "auth_service_role_arn" {
  value = aws_iam_role.auth_service.arn
}

output "group_service_role_arn" {
  value = aws_iam_role.group_service.arn
}

output "auction_service_role_arn" {
  value = aws_iam_role.auction_service.arn
}

output "payment_service_role_arn" {
  value = aws_iam_role.payment_service.arn
}

output "notification_service_role_arn" {
  value = aws_iam_role.notification_service.arn
}

output "report_lambda_role_arn" {
  value = aws_iam_role.report_lambda.arn
}

output "bot_agent_lambda_role_arn" {
  value = aws_iam_role.bot_agent_lambda.arn
}
