resource "aws_sqs_queue" "notification_dlq" {
  name                      = "${var.project_prefix}-notification-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days

  tags = { Environment = var.environment }
}

resource "aws_sqs_queue" "notification" {
  name                       = "${var.project_prefix}-notification-queue-${var.environment}"
  visibility_timeout_seconds = 60
  message_retention_seconds  = 345600 # 4 days

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.notification_dlq.arn
    maxReceiveCount     = 3
  })

  tags = { Environment = var.environment }
}
