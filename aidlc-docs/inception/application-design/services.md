# 📌 MoneyLendingManager — Services
**Defines the service layer: AWS infrastructure services, external integrations, and inter-service communication patterns.**

---

## 1. Authentication & Identity Service
**Provider:** AWS Cognito  

**Configuration:**
- User Pool — stores user accounts (email+password, phone number, Google identity federation)  
- Identity Pool — issues temporary AWS credentials for direct S3 uploads (payment proofs, profile images)  
- App Clients — Flutter mobile client (PKCE flow)  
- Triggers — Pre-signup Lambda (validation), Post-confirmation Lambda (create user record in RDS)  

**Auth Methods Supported:**

| Method          | Mechanism                                      |
|-----------------|------------------------------------------------|
| Email + Password| Cognito native auth                            |
| Phone OTP       | Cognito phone number auth + SNS OTP            |
| Google OAuth    | Cognito Hosted UI + Google Identity Federation |

**JWT Token Flow:**
- Access Token — 1 hour, validated at API Gateway  
- Refresh Token — 30 days, stored in Flutter secure storage  
- ID Token — contains user claims (role, language preference, user_id)  

---

## 2. API Gateway Services
**REST API Gateway**
- Purpose: HTTP routing from Flutter client to microservices  
- Auth: Cognito JWT Authorizer  
- Routing: Path-based → ECS Fargate services via VPC Link  
- Endpoints: `/auth/*`, `/groups/*`, `/auctions/*`, `/payments/*`, `/notifications/*`, `/reports/*`, `/localization/*`  

**WebSocket API Gateway**
- Purpose: Real-time auction sessions  
- Routes: `$connect`, `$disconnect`, `bid`, `auction-status`, `ping`  
- Backend: Auction Service Lambda handlers + ECS Fargate  
- Connection Registry: DynamoDB `AuctionConnections`  
- Auth: Cognito JWT validated on `$connect`  

---

## 3. Compute Services
| Service        | Component                                | Justification |
|----------------|------------------------------------------|---------------|
| AWS ECS Fargate| Auth, Group, Auction, Payment, Notification | Container-first, scalable |
| AWS Lambda     | Report Service, Bot Agent, WS handlers, Archival | Event-driven tasks |
| AWS EC2 (opt.) | Reserved capacity if ECS costs exceed budget | Full control option |

**ECS Fargate Configuration:**
- Separate ECS Service per microservice  
- Task definitions: FastAPI container + health check  
- Auto-scaling: CPU/request count  
- Registry: AWS ECR  

---

## 4. Database Services
**AWS RDS MySQL (Primary Relational Store)**  
- Tables: users, user_roles, chit_groups, group_members, auctions, bids, contributions, payment_records, attachments  
- Instance: `db.t3.medium` (~100 concurrent users)  
- Backups: 7-day retention  
- Encryption: AWS KMS  

**AWS DynamoDB (NoSQL — Fast State & Events)**  
- Tables: Sessions, AuctionConnections, AuctionState, NotificationLogs, DeviceTokens, BotActivityLog  
- Billing: PAY_PER_REQUEST  
- TTL: Sessions (30 days), AuctionConnections (4 hours)  

---

## 5. Object Storage Service
**Provider:** AWS S3  

| Bucket              | Contents                          | Access Pattern |
|---------------------|-----------------------------------|----------------|
| mlm-payment-proofs  | Payment proof images/docs         | Private; presigned URL |
| mlm-reports         | Generated PDF/Excel reports       | Private; presigned GET |
| mlm-group-archives  | Completed group data exports      | Private; archival Lambda |
| mlm-localization    | Language JSON bundles (en.json, ta.json) | Public-read via CloudFront |

---

## 6. Notification Services
**AWS SNS (SMS + Push)**  
- SMS: DLT-registered sender ID (India compliance)  
- Push: SNS → FCM (Android), APNs (iOS)  
- Topics: Per-group SNS topics  

**AWS SQS (Notification Queue)**  
- Queue: `NotificationQueue`  
- DLQ: `NotificationDLQ`  

**Firebase Cloud Messaging (FCM)**  
- Push delivery to Flutter clients  
- Device tokens stored in DynamoDB  

---

## 7. Content Delivery Service
**Provider:** AWS CloudFront  
- Localization CDN — serves `mlm-localization` S3 bucket  
- Static Assets CDN — serves icons/images from S3  

---

## 8. Event Scheduling Service
**Provider:** AWS EventBridge Scheduler  

| Rule                  | Schedule         | Target             | Action |
|-----------------------|-----------------|-------------------|--------|
| payment-reminder-daily| Daily 09:00 IST | Bot Agent Lambda  | Check overdue payments, send SMS |
| auction-reminder-check| Every 30 mins   | Bot Agent Lambda  | Check upcoming auctions, send reminders |

---

## 9. Networking & Security Services
- **AWS VPC**: ECS in private subnets, RDS isolated, API Gateway via VPC Link  
- **AWS IAM**: Per-service roles, least privilege  
- **AWS KMS**: RDS + S3 encryption  
- **AWS Secrets Manager**: DB credentials, FCM keys, payment gateway creds  

---

## 10. Inter-Service Communication
**Pattern:** Synchronous REST calls (internal VPC DNS)  

| Caller         | Called Service   | Purpose |
|----------------|------------------|---------|
| Auction Service| Group Service    | Fetch non-winners, mark winner |
| Auction Service| Payment Service  | Trigger contribution records |
| Auction Service| Notification     | Dispatch invites, bid alerts, results |
| Group Service  | Notification     | Membership notifications |
| Payment Service| Notification     | Payment confirmations, defaulter alerts |
| Bot Agent      | Auction Service  | Read schedule, attendance |
| Bot Agent      | Payment Service  | Read overdue payments |
| Bot Agent      | Notification     | Dispatch reminders |
| Report Service | Group/Auction/Payment | Fetch data for reports |

**Service Discovery:** AWS Cloud Map  

---

## 11. Monitoring & Observability Services
- **CloudWatch Logs** — ECS + Lambda logs  
- **CloudWatch Metrics** — CPU, memory, error rate  
- **CloudWatch Alarms** — error thresholds, Lambda timeouts, RDS exhaustion  
- **AWS X-Ray** — distributed tracing across microservices  
