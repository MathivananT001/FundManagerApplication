# 📌 Unit of Work — Dependency Map
**Application:** MoneyLendingManager (Chit Fund Manager)

---

## Dependency Graph (Text Representation)

storage-infrastructure
├── auth-service
│       ├── notification-service
│       ├── group-service
│       │       ├── payment-service
│       │       │       └── report-service
│       │       └── auction-service
│       │               └── api-gateway-layer
│       └── report-service
└── (all services inherit storage)

flutter-mobile-app
└── depends on ALL backend units


---

## Dependency Table

| Unit                 | Depends On                                | Depended On By |
|----------------------|-------------------------------------------|----------------|
| storage-infrastructure | —                                       | auth-service, all services |
| auth-service         | storage-infrastructure                    | group-service, auction-service, payment-service, notification-service, report-service, api-gateway-layer, flutter-mobile-app |
| notification-service | auth-service                              | auction-service, payment-service, flutter-mobile-app |
| group-service        | auth-service                              | auction-service, payment-service, report-service, flutter-mobile-app |
| payment-service      | auth-service, group-service, notification-service | report-service, flutter-mobile-app |
| auction-service      | auth-service, group-service, notification-service | api-gateway-layer, flutter-mobile-app |
| report-service       | auth-service, group-service, payment-service | flutter-mobile-app |
| api-gateway-layer    | auth-service, auction-service             | flutter-mobile-app |
| flutter-mobile-app   | All backend units                         | — |

---

## Critical Path

The critical path for sequential delivery is:

storage-infrastructure
→ auth-service
→ group-service
→ auction-service
→ api-gateway-layer
→ flutter-mobile-app


---

## Parallelism Opportunities

| After                  | Parallel Units                                |
|-------------------------|-----------------------------------------------|
| auth-service ready      | notification-service + group-service          |
| group-service + notification-service ready | payment-service + auction-service |
| payment-service ready   | report-service                                |
| All backend ready       | flutter-mobile-app screens can proceed module-by-module |

---

## External AWS Service Dependencies

| Unit                  | AWS Services Used |
|-----------------------|-------------------|
| storage-infrastructure | RDS MySQL, DynamoDB, S3, VPC, IAM, CloudWatch |
| auth-service          | Cognito, DynamoDB, ECS Fargate |
| notification-service  | SNS, Lambda, S3 |
| group-service         | RDS MySQL, S3, ECS Fargate |
| payment-service       | RDS MySQL, S3, ECS Fargate |
| auction-service       | RDS MySQL, DynamoDB, ECS Fargate, API Gateway WebSocket |
| report-service        | Lambda, S3, RDS MySQL |
| api-gateway-layer     | API Gateway REST, API Gateway WebSocket |
| flutter-mobile-app    | FCM (via SNS), S3 (presigned URLs) |
