# Build & Test Summary — MoneyLendingManager

## Build Artifacts

| Component | Build Output | Deploy Target |
|-----------|-------------|---------------|
| Infrastructure | Terraform state | AWS (VPC, RDS, DynamoDB, S3, IAM, CloudWatch, API Gateway) |
| auth-service | Docker image | ECS Fargate |
| group-service | Docker image | ECS Fargate |
| auction-service | Docker image | ECS Fargate |
| payment-service | Docker image | ECS Fargate |
| notification-service | Docker image | ECS Fargate |
| report-service | Lambda zip | AWS Lambda |
| bot-agent | Lambda zip | AWS Lambda |
| flutter-app | APK / AAB | Google Play / Direct install |

## Test Summary

| Service | Unit Tests | Framework |
|---------|-----------|-----------|
| auth-service | 6 tests | pytest |
| notification-service | 6 tests | pytest |
| group-service | 4 tests | pytest |
| payment-service | 5 tests | pytest |
| auction-service | 4 tests | pytest |
| report-service | 3 tests | pytest |
| flutter-app | Widget tests | flutter_test |
| **Total** | **28+ tests** | |

## Deployment Order

1. **Infrastructure** (Terraform) — VPC, RDS, DynamoDB, S3, IAM, CloudWatch
2. **Database Migration** — Run SQL schema on RDS
3. **Backend Services** (Docker → ECR → ECS) — auth, group, auction, payment, notification
4. **Lambda Functions** — report-service, bot-agent
5. **API Gateway** (Terraform) — REST + WebSocket routing
6. **Flutter App** — Build APK with production API URLs

## Environment Variables Checklist

All services use `.env.example` as template. Key values needed:
- `DATABASE_URL` — from Terraform `rds_endpoint` output
- `COGNITO_USER_POOL_ID` / `COGNITO_CLIENT_ID` — create Cognito pool manually or add to Terraform
- `S3_*_BUCKET` — from Terraform bucket outputs
- `DYNAMODB_*_TABLE` — from Terraform (naming convention: `mlm-{table}-dev`)
- `*_SERVICE_URL` — ECS service discovery DNS or API Gateway URL
