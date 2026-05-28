# VPC
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

# Database
output "rds_endpoint" {
  value = module.database.rds_endpoint
}

output "rds_secret_arn" {
  value     = module.database.rds_secret_arn
  sensitive = true
}

# Storage
output "payment_proofs_bucket_id" {
  value = module.storage.payment_proofs_bucket_id
}

output "localization_bucket_id" {
  value = module.storage.localization_bucket_id
}

# Cognito
output "cognito_user_pool_id" {
  value = module.cognito.user_pool_id
}

output "cognito_client_id" {
  value = module.cognito.client_id
}

# ECS
output "ecs_cluster_id" {
  value = module.ecs.cluster_id
}

# SQS
output "notification_queue_url" {
  value = module.sqs.notification_queue_url
}

# CloudFront
output "localization_cdn_domain" {
  value = module.cloudfront.distribution_domain_name
}

# API Gateway
output "rest_api_endpoint" {
  value = module.api_gateway.rest_api_endpoint
}

output "websocket_api_endpoint" {
  value = module.api_gateway.websocket_api_endpoint
}
