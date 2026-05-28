output "payment_reminder_rule_arn" {
  value = aws_cloudwatch_event_rule.payment_reminder.arn
}

output "auction_reminder_rule_arn" {
  value = aws_cloudwatch_event_rule.auction_reminder.arn
}
