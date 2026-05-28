# 📌 MoneyLendingManager — Component Dependency Map
**Purpose:** Describes all dependency relationships between components, services, and data stores.

---

## Dependency Overview Diagram (Text Representation)

Flutter Mobile App
│
├──(REST HTTPS)──► AWS API Gateway (REST)
│                        │
│         ┌──────────────┼──────────────────────────────┐
│         ▼              ▼                  ▼            ▼
│    Auth Service   Group Service    Auction Service  Payment Service
│         │              │                  │              │
│         │              │                  │              │
│    AWS Cognito    RDS MySQL          RDS MySQL +    RDS MySQL +
│    DynamoDB       (groups,           DynamoDB       S3 (optional
│    (sessions)      members)          (auction        payment proofs)
│                                       state, WS
│                                      connections)
│
├──(WebSocket)──► AWS API Gateway (WebSocket)
│                        │
│                        ▼
│                 Auction Service
│                 (WS Handlers)
│                   DynamoDB
│                (AuctionConnections,
│                  AuctionState)
│
└──(HTTPS)──► AWS CloudFront ──► S3 (Localization Bundles)

Notification Service ◄──── Auction Service
◄──── Group Service
◄──── Payment Service
◄──── Bot Agent (Lambda)
│
├──► AWS SNS ──► SMS (phone numbers)
│         └──► FCM ──► Push (Flutter)
└──► AWS SQS (async queue)

Report Service (Lambda)
├──► Group Service (data fetch)
├──► Auction Service (data fetch)
├──► Payment Service (data fetch)
└──► S3 (mlm-reports bucket)
└──► Presigned URL ──► Flutter

Bot Agent (Lambda)
├──► EventBridge Scheduler (trigger)
├──► Auction Service (read schedule + attendance)
├──► Payment Service (read unconfirmed records)
├──► Group Service (read non-winners)
├──► Notification Service (dispatch reminders)
└──► DynamoDB (BotActivityLog)


---

## Detailed Dependency Table

| Component             | Depends On                        | Type              | Purpose |
|-----------------------|-----------------------------------|------------------|---------|
| Flutter Mobile App    | AWS API Gateway (REST)            | HTTP/HTTPS       | All REST API calls |
| Flutter Mobile App    | AWS API Gateway (WebSocket)       | WebSocket        | Live auction real-time updates |
| Flutter Mobile App    | AWS Cognito                       | OAuth2/OIDC      | Authentication, token management |
| Flutter Mobile App    | AWS CloudFront + S3               | HTTPS            | Fetch language bundles (Tamil/English) |
| Flutter Mobile App    | AWS SNS (via FCM)                 | Push             | Receive push notifications |
| Flutter Mobile App    | S3 (presigned URL)                | HTTPS PUT        | Upload optional payment proof |
| Flutter Mobile App    | Report Service (via API GW)       | HTTPS            | Trigger report generation, download presigned URL |
| API Gateway (REST)    | AWS Cognito                       | JWT Authorizer   | Token validation |
| API Gateway (REST)    | Auth Service (ECS)                | VPC Link         | Route /auth/* |
| API Gateway (REST)    | Group Service (ECS)               | VPC Link         | Route /groups/* |
| API Gateway (REST)    | Auction Service (ECS)             | VPC Link         | Route /auctions/* |
| API Gateway (REST)    | Payment Service (ECS)             | VPC Link         | Route /payments/* |
| API Gateway (REST)    | Notification Service (ECS)        | VPC Link         | Route /notifications/* |
| API Gateway (REST)    | Report Service (Lambda)           | Lambda Integration | Route /reports/* |
| API Gateway (WebSocket)| Auction Service (Lambda/ECS)     | Lambda Integration | WS connect/disconnect/bid handlers |
| Auth Service          | AWS Cognito, DynamoDB, RDS MySQL  | Cognito SDK, SQLAlchemy | User pool ops, sessions, profiles |
| Group Service         | RDS MySQL, S3, Notification Service | SQLAlchemy, AWS SDK | Group lifecycle, archives, notifications |
| Auction Service       | RDS MySQL, DynamoDB, Group Service, Payment Service, Notification Service | SQLAlchemy, AWS SDK | Auctions, bids, state, notifications |
| Payment Service       | RDS MySQL, S3, Notification Service | SQLAlchemy, AWS SDK | Ledger, proofs, defaulter alerts |
| Notification Service  | AWS SNS, AWS SQS, DynamoDB        | AWS SDK          | SMS, push, async queue, logs |
| Report Service (Lambda)| Group, Auction, Payment Services, S3 | Internal REST, AWS SDK | Reports, exports |
| Bot Agent (Lambda)    | EventBridge, Auction, Payment, Group, Notification, DynamoDB | Internal REST, AWS SDK | Scheduling, reminders, logs |

---

## Data Store Dependencies

| Data Store                  | Owner Service(s)         | Read-Only Consumers |
|------------------------------|--------------------------|---------------------|
| RDS MySQL                   | Auth, Group, Auction, Payment | Report Service |
| DynamoDB (Sessions)         | Auth Service             | — |
| DynamoDB (AuctionConnections)| Auction Service          | Bot Agent |
| DynamoDB (AuctionState)     | Auction Service          | Bot Agent |
| DynamoDB (DeviceTokens)     | Notification Service     | — |
| DynamoDB (NotificationLogs) | Notification Service     | — |
| DynamoDB (BotActivityLog)   | Bot Agent                | — |
| S3 (mlm-payment-proofs)     | Payment Service          | Flutter (presigned GET) |
| S3 (mlm-reports)            | Report Service           | Flutter (presigned GET) |
| S3 (mlm-group-archives)     | Group Service            | Admin tools |
| S3 (mlm-localization)       | Admin (manual upload)    | Flutter via CloudFront |

---

## External Service Dependencies

| External Service            | Used By                  | Purpose |
|-----------------------------|--------------------------|---------|
| Google OAuth 2.0            | Auth Service (via Cognito)| Social login |
| Firebase Cloud Messaging    | Notification Service (via SNS) | Push delivery |
| Apple Push Notification Service | Notification Service (via SNS) | iOS push |
| AWS DLT-registered SMS      | Notification Service (via SNS) | SMS to Indian numbers |

---

## Circular Dependency Analysis
- No circular dependencies exist.  
- Flow is strictly directional:  
  - **Flutter → API Gateway → [Auth | Group | Auction | Payment | Notification | Report]**  

  Flutter → API Gateway → [Auth | Group | Auction | Payment | Notification | Report]
                              ↘ Group ← Auction → Payment → Notification
                                        ↓
                                  Bot Agent → [Group, Auction, Payment, Notification]
  - Auction Service orchestrates core flow → calls Group, Payment, Notification  
  - Bot Agent consumes data → writes only to Notification + DynamoDB log  
  - Report Service reads only → writes to S3  
  - Notification Service is a pure sink → dispatch only, no callbacks  
