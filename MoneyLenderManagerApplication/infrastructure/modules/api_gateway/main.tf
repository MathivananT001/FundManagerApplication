# ============================================
# REST API Gateway (US-031)
# ============================================

resource "aws_apigatewayv2_api" "rest" {
  name          = "${var.project_prefix}-rest-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Authorization", "Content-Type", "X-User-Id"]
    max_age       = 3600
  }

  tags = {
    Environment = var.environment
  }
}

# Cognito JWT Authorizer
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.rest.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "${var.project_prefix}-cognito-authorizer"

  jwt_configuration {
    audience = ["${var.project_prefix}-client-${var.environment}"]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${var.cognito_user_pool_arn}"
  }
}

# Stage
resource "aws_apigatewayv2_stage" "rest" {
  api_id      = aws_apigatewayv2_api.rest.id
  name        = var.environment
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = 100
    throttling_rate_limit  = 50
  }
}

# --- Service Integrations (VPC Link to ECS) ---

# Auth Service routes
resource "aws_apigatewayv2_integration" "auth" {
  api_id             = aws_apigatewayv2_api.rest.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://auth-service.internal:8000/{proxy}"
  integration_method = "ANY"
}

resource "aws_apigatewayv2_route" "auth" {
  api_id    = aws_apigatewayv2_api.rest.id
  route_key = "ANY /auth/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.auth.id}"
}

# Group Service routes
resource "aws_apigatewayv2_integration" "groups" {
  api_id             = aws_apigatewayv2_api.rest.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://group-service.internal:8000/{proxy}"
  integration_method = "ANY"
}

resource "aws_apigatewayv2_route" "groups" {
  api_id             = aws_apigatewayv2_api.rest.id
  route_key          = "ANY /groups/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.groups.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# Auction Service routes
resource "aws_apigatewayv2_integration" "auctions" {
  api_id             = aws_apigatewayv2_api.rest.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://auction-service.internal:8000/{proxy}"
  integration_method = "ANY"
}

resource "aws_apigatewayv2_route" "auctions" {
  api_id             = aws_apigatewayv2_api.rest.id
  route_key          = "ANY /auctions/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.auctions.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# Payment Service routes
resource "aws_apigatewayv2_integration" "payments" {
  api_id             = aws_apigatewayv2_api.rest.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://payment-service.internal:8000/{proxy}"
  integration_method = "ANY"
}

resource "aws_apigatewayv2_route" "payments" {
  api_id             = aws_apigatewayv2_api.rest.id
  route_key          = "ANY /payments/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.payments.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# Notification Service routes
resource "aws_apigatewayv2_integration" "notifications" {
  api_id             = aws_apigatewayv2_api.rest.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://notification-service.internal:8000/{proxy}"
  integration_method = "ANY"
}

resource "aws_apigatewayv2_route" "notifications" {
  api_id             = aws_apigatewayv2_api.rest.id
  route_key          = "ANY /notifications/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.notifications.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

# Report Service (Lambda integration)
resource "aws_apigatewayv2_integration" "reports" {
  api_id                 = aws_apigatewayv2_api.rest.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.report_lambda_invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "reports" {
  api_id             = aws_apigatewayv2_api.rest.id
  route_key          = "ANY /reports/{proxy+}"
  target             = "integrations/${aws_apigatewayv2_integration.reports.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_lambda_permission" "apigw_reports" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.report_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.rest.execution_arn}/*/*"
}

# ============================================
# WebSocket API Gateway (US-032)
# ============================================

resource "aws_apigatewayv2_api" "websocket" {
  name                       = "${var.project_prefix}-ws-api-${var.environment}"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

  tags = {
    Environment = var.environment
  }
}

# WebSocket routes
resource "aws_apigatewayv2_integration" "ws_auction" {
  api_id             = aws_apigatewayv2_api.websocket.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = "http://auction-service.internal:8000/auctions/ws/{proxy}"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "ws_connect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.ws_auction.id}"
}

resource "aws_apigatewayv2_route" "ws_disconnect" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.ws_auction.id}"
}

resource "aws_apigatewayv2_route" "ws_bid" {
  api_id    = aws_apigatewayv2_api.websocket.id
  route_key = "bid"
  target    = "integrations/${aws_apigatewayv2_integration.ws_auction.id}"
}

resource "aws_apigatewayv2_stage" "websocket" {
  api_id      = aws_apigatewayv2_api.websocket.id
  name        = var.environment
  auto_deploy = true
}
