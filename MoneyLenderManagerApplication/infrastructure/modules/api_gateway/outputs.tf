output "rest_api_endpoint" {
  value = aws_apigatewayv2_api.rest.api_endpoint
}

output "rest_api_id" {
  value = aws_apigatewayv2_api.rest.id
}

output "websocket_api_endpoint" {
  value = "wss://${aws_apigatewayv2_api.websocket.id}.execute-api.${var.aws_region}.amazonaws.com/${var.environment}"
}

output "websocket_api_id" {
  value = aws_apigatewayv2_api.websocket.id
}
