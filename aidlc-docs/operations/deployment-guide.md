# Operations — Deployment Guide

## Deployment Architecture

```
Flutter App (Android)
       │
       ▼
AWS API Gateway (REST + WebSocket)
       │ Cognito JWT Auth
       ▼
┌─────────────────────────────────────┐
│     AWS ECS Fargate (Private VPC)   │
│                                     │
│  auth ─ group ─ auction ─ payment   │
│            notification             │
└─────────────────────────────────────┘
       │
       ▼
AWS RDS MySQL + DynamoDB + S3
       │
AWS Lambda (report-service, bot-agent)
AWS EventBridge (scheduled triggers)
AWS SNS/SQS (notifications)
```

---

## Step-by-Step Production Deployment

### Phase 1: Infrastructure
```bash
cd MoneyLenderManagerApplication/infrastructure
terraform apply -var-file=environments/prod.tfvars
```

### Phase 2: Cognito Setup (Manual)
1. Create Cognito User Pool in ap-south-1
2. Configure app client (PKCE flow for Flutter)
3. Enable Google Identity Federation
4. Enable phone number verification (SMS via SNS)
5. Note: User Pool ID, Client ID, Client Secret

### Phase 3: Database
```bash
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
RDS_PASSWORD=$(aws secretsmanager get-secret-value --secret-id mlm-rds-password-prod --query SecretString --output text | jq -r '.password')
mysql -h $RDS_ENDPOINT -u mlm_admin -p$RDS_PASSWORD moneylender < infrastructure/migrations/001_initial_schema.sql
```

### Phase 4: ECR + ECS Deployment
```bash
# Create ECR repos
for svc in auth-service group-service auction-service payment-service notification-service; do
  aws ecr create-repository --repository-name mlm-$svc --region ap-south-1
done

# Build, tag, push
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
ECR=$ACCOUNT.dkr.ecr.ap-south-1.amazonaws.com
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR

for svc in auth-service group-service auction-service payment-service notification-service; do
  docker build -t mlm-$svc:latest ./$svc
  docker tag mlm-$svc:latest $ECR/mlm-$svc:latest
  docker push $ECR/mlm-$svc:latest
done

# Create ECS services (via Terraform or AWS Console)
# Each service: 1 task, 256 CPU, 512 MB memory (dev)
```

### Phase 5: Lambda Deployment
```bash
# Report Service
cd report-service
pip install -r requirements.txt -t package/
cp handler.py package/
cd package && zip -r ../report-service.zip .
aws lambda create-function --function-name mlm-report-service-prod \
  --runtime python3.11 --handler handler.generate_group_summary_report \
  --role $(terraform output -raw report_lambda_role_arn) \
  --zip-file fileb://report-service.zip --region ap-south-1

# Bot Agent
cd ../notification-service
zip -j bot-agent.zip bot_agent/handlers.py
aws lambda create-function --function-name mlm-bot-agent-prod \
  --runtime python3.11 --handler handlers.run_payment_reminders \
  --role $(terraform output -raw bot_agent_lambda_role_arn) \
  --zip-file fileb://bot-agent.zip --region ap-south-1
```

### Phase 6: EventBridge Schedules
```bash
# Payment reminders — daily 9:00 AM IST
aws events put-rule --name mlm-payment-reminder-daily \
  --schedule-expression "cron(30 3 * * ? *)" --region ap-south-1

aws events put-targets --rule mlm-payment-reminder-daily \
  --targets "Id"="bot-agent","Arn"="arn:aws:lambda:ap-south-1:$ACCOUNT:function:mlm-bot-agent-prod"

# Auction reminders — every 30 minutes
aws events put-rule --name mlm-auction-reminder \
  --schedule-expression "rate(30 minutes)" --region ap-south-1
```

### Phase 7: S3 Localization Upload
```bash
# Upload language bundles
aws s3 cp localization/en.json s3://mlm-localization-prod-$ACCOUNT/localization/en.json
aws s3 cp localization/ta.json s3://mlm-localization-prod-$ACCOUNT/localization/ta.json
```

### Phase 8: Flutter Release
```bash
cd flutter-app
flutter build apk --release \
  --dart-define=API_BASE_URL=https://API_GW_ID.execute-api.ap-south-1.amazonaws.com/prod \
  --dart-define=WS_BASE_URL=wss://WS_API_ID.execute-api.ap-south-1.amazonaws.com/prod \
  --dart-define=ENVIRONMENT=prod
```

---

## Service Ports (Local Dev)

| Service | Port |
|---------|------|
| auth-service | 8001 |
| group-service | 8002 |
| notification-service | 8003 |
| payment-service | 8004 |
| auction-service | 8005 |
| MySQL | 3306 |
