# MoneyLendingManager — Infrastructure (Terraform)

## Overview
Complete AWS infrastructure for MoneyLendingManager — 11 Terraform modules, fully parameterized, zero hardcoded values.

## Modules (11)

| Module | Resources |
|--------|-----------|
| `vpc` | VPC, public/private/isolated subnets, NAT Gateway, 3 security groups |
| `database` | RDS MySQL (encrypted, Secrets Manager) + 6 DynamoDB tables |
| `storage` | 4 S3 buckets (proofs, reports, archives, localization) |
| `iam` | 8 IAM roles with least-privilege policies |
| `monitoring` | CloudWatch log groups (7 services) + dashboard |
| `cognito` | User Pool, App Client, Google OAuth, SMS OTP |
| `ecs` | ECS Fargate cluster + 5 service task definitions + service discovery |
| `sqs` | Notification queue + dead-letter queue |
| `cloudfront` | CDN for localization bundles (S3 OAI) |
| `eventbridge` | Bot agent schedules (payment + auction reminders) |
| `api_gateway` | REST API (Cognito JWT auth) + WebSocket API (live auctions) |

## Deploy

```bash
cd MoneyLenderManagerApplication/infrastructure

# Update account ID
sed -i 's/REPLACE_WITH_ACCOUNT_ID/YOUR_ACCOUNT_ID/' environments/dev.tfvars

terraform init
terraform plan -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars
```

## Environments
- `environments/dev.tfvars` — Development (single NAT, small RDS, 30-day logs)
- `environments/prod.tfvars` — Production (multi-AZ RDS, 2 NATs, 90-day logs)

## Key Outputs
After `terraform apply`:
- `cognito_user_pool_id` / `cognito_client_id` — for service config
- `rds_endpoint` — MySQL connection
- `ecs_cluster_id` — ECS cluster for deployments
- `notification_queue_url` — SQS queue for async notifications
- `localization_cdn_domain` — CloudFront URL for language bundles
- `rest_api_endpoint` / `websocket_api_endpoint` — API Gateway URLs
