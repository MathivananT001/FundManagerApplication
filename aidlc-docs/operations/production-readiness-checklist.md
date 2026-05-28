# Operations — Production Readiness Checklist

## Infrastructure
- [ ] Terraform applied with `prod.tfvars`
- [ ] RDS Multi-AZ enabled
- [ ] RDS deletion protection enabled
- [ ] S3 buckets with proper lifecycle policies
- [ ] VPC with 2 NAT Gateways
- [ ] All security groups reviewed (least privilege)

## Security
- [ ] Cognito User Pool created with MFA optional
- [ ] Google OAuth configured in Cognito
- [ ] Phone OTP via SNS configured (DLT registration for India)
- [ ] RDS credentials in Secrets Manager (not hardcoded)
- [ ] All S3 buckets block public access
- [ ] API Gateway JWT authorizer configured
- [ ] IAM roles follow least privilege
- [ ] TLS 1.2+ enforced on all endpoints

## Database
- [ ] Schema migration applied
- [ ] Backup retention: 7 days
- [ ] Encryption at rest enabled (KMS)
- [ ] Connection pooling configured in services

## Services
- [ ] All Docker images built and pushed to ECR
- [ ] ECS services running with health checks
- [ ] Auto-scaling configured (CPU-based)
- [ ] Environment variables set from Secrets Manager / Parameter Store
- [ ] Service discovery configured (Cloud Map or internal DNS)

## Lambda
- [ ] report-service deployed with correct IAM role
- [ ] bot-agent deployed with correct IAM role
- [ ] EventBridge schedules active
- [ ] Lambda timeout set appropriately (30s for reports)

## API Gateway
- [ ] REST API deployed with Cognito authorizer
- [ ] WebSocket API deployed for auctions
- [ ] Rate limiting configured (50 req/s)
- [ ] CORS configured for Flutter app domain
- [ ] Custom domain (optional)

## Notifications
- [ ] SNS SMS sender ID registered (DLT for India)
- [ ] FCM server key configured
- [ ] SQS DLQ configured for failed notifications
- [ ] Localization bundles uploaded to S3 (en.json, ta.json)

## Monitoring
- [ ] CloudWatch log groups created
- [ ] CloudWatch alarms configured
- [ ] Dashboard created
- [ ] X-Ray tracing enabled (optional)

## Flutter App
- [ ] APK built with production API URLs
- [ ] App signing configured
- [ ] Crash reporting enabled (Firebase Crashlytics)
- [ ] Push notification permissions handled

## Testing
- [ ] All unit tests passing
- [ ] Integration tests passing against staging
- [ ] Load test: 100 concurrent users during auction
- [ ] Manual QA: full auction flow end-to-end
