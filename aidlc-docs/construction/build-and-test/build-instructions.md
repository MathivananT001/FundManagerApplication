# Build Instructions — MoneyLendingManager

## Prerequisites
- Python 3.11+
- Terraform >= 1.5.0
- Docker & Docker Compose
- Flutter SDK >= 3.3.0
- AWS CLI configured (ap-south-1)
- Node.js (for AWS CDK if needed)

---

## 1. Infrastructure (Terraform)

```bash
cd MoneyLenderManagerApplication/infrastructure

# Update account ID in tfvars
sed -i 's/REPLACE_WITH_ACCOUNT_ID/YOUR_ACCOUNT_ID/' environments/dev.tfvars

# Initialize and deploy
terraform init
terraform plan -var-file=environments/dev.tfvars
terraform apply -var-file=environments/dev.tfvars -auto-approve

# Note outputs for service configuration
terraform output
```

---

## 2. Database Migration

```bash
# Get RDS endpoint from Terraform output
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Run schema migration
mysql -h $RDS_ENDPOINT -u mlm_admin -p moneylender < migrations/001_initial_schema.sql

# Dev seed data (optional)
mysql -h $RDS_ENDPOINT -u mlm_admin -p moneylender < migrations/seed_data.sql
```

---

## 3. Backend Services (Docker)

Each service builds independently:

```bash
# Auth Service
cd MoneyLenderManagerApplication/auth-service
docker build -t mlm-auth-service:latest .

# Group Service
cd ../group-service
docker build -t mlm-group-service:latest .

# Auction Service
cd ../auction-service
docker build -t mlm-auction-service:latest .

# Payment Service
cd ../payment-service
docker build -t mlm-payment-service:latest .

# Notification Service
cd ../notification-service
docker build -t mlm-notification-service:latest .
```

### Local Development (all services)

```bash
cd MoneyLenderManagerApplication/auth-service
docker-compose up  # Starts auth-service + MySQL
```

For full stack local, create a root docker-compose (see docker-compose.yml in project root).

---

## 4. Lambda Functions

```bash
# Report Service
cd MoneyLenderManagerApplication/report-service
pip install -r requirements.txt -t package/
cp handler.py package/
cd package && zip -r ../report-service.zip . && cd ..

# Deploy via AWS CLI
aws lambda update-function-code \
  --function-name mlm-report-service-dev \
  --zip-file fileb://report-service.zip \
  --region ap-south-1
```

Bot Agent Lambda (in notification-service/bot_agent/):
```bash
cd MoneyLenderManagerApplication/notification-service
zip -j bot-agent.zip bot_agent/handlers.py
aws lambda update-function-code \
  --function-name mlm-bot-agent-dev \
  --zip-file fileb://bot-agent.zip \
  --region ap-south-1
```

---

## 5. Flutter App

```bash
cd MoneyLenderManagerApplication/flutter-app
flutter pub get
flutter run --dart-define=API_BASE_URL=https://YOUR_API_GATEWAY_URL/dev

# Build APK for release
flutter build apk --release \
  --dart-define=API_BASE_URL=https://YOUR_API_GATEWAY_URL/dev \
  --dart-define=WS_BASE_URL=wss://YOUR_WS_API_ID.execute-api.ap-south-1.amazonaws.com/dev
```

---

## 6. Push to ECR (Production)

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO=$AWS_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com

aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_REPO

for svc in auth-service group-service auction-service payment-service notification-service; do
  docker tag mlm-$svc:latest $ECR_REPO/mlm-$svc:latest
  docker push $ECR_REPO/mlm-$svc:latest
done
```
