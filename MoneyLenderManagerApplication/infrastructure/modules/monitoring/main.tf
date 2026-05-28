locals {
  services = ["auth", "group", "auction", "payment", "notification", "report", "bot-agent"]
}

resource "aws_cloudwatch_log_group" "services" {
  for_each          = toset(local.services)
  name              = "/${var.project_prefix}/${var.environment}/${each.value}"
  retention_in_days = var.log_retention_days

  tags = {
    Service     = each.value
    Environment = var.environment
  }
}

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_prefix}-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# MoneyLendingManager — ${var.environment}"
        }
      }
    ]
  })
}
