# Daily payment reminder — 9:00 AM IST (3:30 AM UTC)
resource "aws_cloudwatch_event_rule" "payment_reminder" {
  name                = "${var.project_prefix}-payment-reminder-${var.environment}"
  schedule_expression = "cron(30 3 * * ? *)"
  description         = "Daily payment reminder check"

  tags = { Environment = var.environment }
}

resource "aws_cloudwatch_event_target" "payment_reminder" {
  rule = aws_cloudwatch_event_rule.payment_reminder.name
  arn  = var.bot_agent_lambda_arn
  input = jsonencode({ handler = "run_payment_reminders" })
}

resource "aws_lambda_permission" "payment_reminder" {
  statement_id  = "AllowEventBridgePaymentReminder"
  action        = "lambda:InvokeFunction"
  function_name = var.bot_agent_lambda_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.payment_reminder.arn
}

# Auction reminder — every 30 minutes
resource "aws_cloudwatch_event_rule" "auction_reminder" {
  name                = "${var.project_prefix}-auction-reminder-${var.environment}"
  schedule_expression = "rate(30 minutes)"
  description         = "Check upcoming auctions and send reminders"

  tags = { Environment = var.environment }
}

resource "aws_cloudwatch_event_target" "auction_reminder" {
  rule = aws_cloudwatch_event_rule.auction_reminder.name
  arn  = var.bot_agent_lambda_arn
  input = jsonencode({ handler = "run_auction_reminders" })
}

resource "aws_lambda_permission" "auction_reminder" {
  statement_id  = "AllowEventBridgeAuctionReminder"
  action        = "lambda:InvokeFunction"
  function_name = var.bot_agent_lambda_arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.auction_reminder.arn
}
