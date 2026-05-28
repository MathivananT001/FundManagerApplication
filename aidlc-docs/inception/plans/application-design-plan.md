# 📌 MoneyLendingManager — Application Design
**Version:** 1.1  
**Stage:** Inception — Application Design  
**Currency:** INR  
**Languages:** Tamil, English  

---

## 1. Executive Summary
MoneyLendingManager is a mobile-first chit fund (self-funding group) management platform targeting individual fund managers and their member groups. The system manages the complete lifecycle of a chit fund group: formation, monthly live auctions, contribution payment tracking, and group archival.

### Core Business Rules
- Groups have 8–15 members + 1 bot agent (management-only, non-financial)  
- Monthly live auction: open bidding, highest bidder wins the pot  
- If no bids → random selection from members who have never won before  
- Monthly contribution per member = auction amount won ÷ total members (excluding bot)  
- Fund manager sets a configurable payment deadline; defaulters receive SMS alerts  
- Fund manager can initiate a phone call to defaulting members directly from the app  
- Payment confirmation is mandatory (fund manager marks as received); proof attachments optional  
- Completed groups are archived to S3 and purged from active RDS tables  

---

## 2. Architecture Style

| Property              | Decision                                      |
|-----------------------|-----------------------------------------------|
| Architecture Pattern  | Microservices (container-first, Kubernetes-ready) |
| Backend Language      | Python 3.11 + FastAPI                         |
| Mobile Client         | Flutter (iOS & Android)                       |
| API Communication     | REST (AWS API Gateway) + WebSocket (AWS API Gateway WebSocket API) |
| Deployment            | AWS ECS Fargate (primary) + AWS Lambda (async/event-driven tasks) |
| Region                | ap-south-1 (Mumbai, India)                    |
| Scale Target          | Up to 100 concurrent users (avg 50)           |

---

## 3. System Architecture Overview

┌─────────────────────────────────────────────────────────────────┐
│                     Flutter Mobile App                          │
│         (iOS & Android — Tamil/English, INR, Role-based UI)     │
└────────────┬──────────────────────────────┬────────────────────┘
│ REST (HTTPS)                 │ WebSocket
▼                              ▼
┌─────────────────────┐        ┌──────────────────────────┐
│  AWS API Gateway    │        │ AWS API Gateway          │
│  (REST API)         │        │ (WebSocket API)          │
│  Cognito Authorizer │        │ Cognito Auth on $connect │
└────────┬────────────┘        └──────────┬───────────────┘
│                                │
│ VPC Link                       │ Lambda Integration
▼                                ▼
┌────────────────────────────────────────────────────────────────┐
│                    AWS ECS Fargate Cluster                     │
│                    (Private Subnets, VPC)                      │
│                                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Auth        │  │ Group       │  │ Auction Service     │   │
│  │ Service     │  │ Service     │  │ (REST + WS handler) │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
│  ┌─────────────┐  ┌──────────────────────────────────────┐    │
│  │ Payment     │  │ Notification Service                 │    │
│  │ Service     │  │ (REST + SQS consumer)                │    │
│  └─────────────┘  └──────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘


Additional integrations:
- AWS Lambda: Report Service, Bot Agent, Archival Trigger  
- AWS RDS MySQL: relational data  
- AWS DynamoDB: session, WS state, notifications  
- AWS S3: proofs, reports, archives, localization  
- AWS Cognito: authentication  
- AWS SNS + FCM: notifications  
- AWS SQS: queue  
- AWS EventBridge: scheduling  
- AWS CloudFront: localization CDN  

---

## 4. Microservice Inventory

| Service              | Runtime        | Deployment       | Responsibility |
|----------------------|----------------|-----------------|----------------|
| Auth Service         | Python/FastAPI | ECS Fargate      | Cognito integration, JWT, user profiles, roles |
| Group Service        | Python/FastAPI | ECS Fargate      | Group lifecycle, member management, archival |
| Auction Service      | Python/FastAPI | ECS Fargate + Lambda | Live auction, bidding, winner logic, WebSocket |
| Payment Service      | Python/FastAPI | ECS Fargate      | Contribution tracking, manual confirmation, proof uploads |
| Notification Service | Python/FastAPI | ECS Fargate + Lambda | SMS (SNS), push (FCM), SQS consumer |
| Report Service       | Python         | Lambda           | PDF/Excel generation, S3 storage |
| Bot Agent            | Python         | Lambda           | EventBridge-triggered reminders, attendance tracking |
| Localization         | JSON on S3/CDN | Static           | Tamil/English string bundles |

---

## 5. Key Domain Flows

### 5.1 Monthly Live Auction Flow
- Fund Manager sets auction time  
- Auction Service schedules → Notification Service sends invites  
- Auction opens → WebSocket room activated  
- Bot Agent checks attendance/non-winners  
- Members bid → highest wins (else random selection)  
- Winner declared → contributions calculated  
- Payment Service creates records  
- Notification Service announces results  

### 5.2 Monthly Contribution Payment Flow
- Fund Manager sets deadline  
- Members pay (offline/own channel) → optional proof upload  
- Fund Manager confirms payments  
- Bot Agent checks defaulters → sends SMS alerts  
- Fund Manager can call defaulters directly  

### 5.3 Group Archival Flow
- All members have won → group complete  
- Fund Manager marks complete  
- Archival Lambda serializes data → uploads to S3 → purges RDS  

---

## 6. Data Architecture

| Layer        | Technology       | Data Hosted |
|--------------|-----------------|-------------|
| Relational   | AWS RDS MySQL   | Users, groups, auctions, payments |
| Key-Value    | AWS DynamoDB    | Sessions, WS state, notifications |
| Object Store | AWS S3          | Proofs, reports, archives, localization |
| CDN          | AWS CloudFront  | Localization bundles |

---

## 7. Security Design

- **Authentication**: AWS Cognito (Google, Phone OTP, Email+Password)  
- **Authorization**: JWT claims-based RBAC validated at API Gateway  
- **Transport**: TLS 1.2+ enforced  
- **Data at Rest**: RDS KMS encryption, S3 SSE-KMS  
- **Network**: ECS in private subnets, RDS isolated, API Gateway public ingress only  
- **Secrets**: AWS Secrets Manager  
- **S3 Upload Auth**: Cognito Identity Pool temporary credentials  

---

## 8. Localization Design
- Server-driven JSON bundles on S3, served via CloudFront  
- Languages: English (`en.json`), Tamil (`ta.json`)  
- Update: Upload → Invalidate cache → Clients fetch on next launch  
- Coverage: UI strings, notifications, reports  
- User preference stored in Cognito attributes  

---

## 9. Notification Strategy

| Event                  | Channel       | Recipient |
|-------------------------|---------------|-----------|
| Auction join invite     | Push + SMS    | All members |
| Auction live opened     | Push          | All members |
| New highest bid         | Push          | Auction participants |
| Winner announced        | Push + SMS    | All members |
| Payment deadline reminder | SMS         | Members with outstanding payments |
| Payment defaulter alert | SMS           | Defaulter + Fund Manager |
| Payment confirmed       | Push          | Member |

---

## 10. Report Capabilities
- **Group Summary**: In-app + PDF/Excel export  
- **Member Contribution History**: In-app + PDF/Excel export  
- **Auction History**: In-app + PDF/Excel export  
- Exports stored in S3 with 15-min presigned URLs  

---

## 11. Future Roadmap (Out of Scope)
- Kubernetes migration (EKS)  
- Payment gateway integration (Razorpay/UPI)  
- Multiple group types (extensible model)  
- Web admin panel  
- RBI compliance review  
- Multi-region deployment  

---

## 12. Technology Stack Summary

| Layer          | Technology |
|----------------|------------|
| Mobile         | Flutter (Dart) — iOS & Android |
| Backend        | Python 3.11 + FastAPI |
| API            | AWS API Gateway (REST + WebSocket) |
| Auth           | AWS Cognito |
| Compute        | AWS ECS Fargate + AWS Lambda |
| Relational DB  | AWS RDS MySQL |
| NoSQL DB       | AWS DynamoDB |
| Storage        | AWS S3 |
| CDN            | AWS CloudFront |
| Notifications  | AWS SNS + FCM |
| Queuing        | AWS SQS |
| Scheduling     | AWS EventBridge |
| Observability  | AWS CloudWatch + AWS X-Ray |
| Secrets        | AWS Secrets Manager |
| Container Reg. | AWS ECR