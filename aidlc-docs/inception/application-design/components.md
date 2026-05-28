# 📌 MoneyLendingManager — Components
**Architecture Style:** Microservices  
**Platform:** Flutter (iOS/Android) + FastAPI (Python)  
**Cloud:** AWS  
**Target Scale:** ~100 concurrent users  

---

## 1. Mobile Client Application
**Type:** Flutter Mobile App (iOS & Android)  

**Responsibility:**
- Primary user interface for Fund Managers and Group Members  
- Screens: authentication, group management, live auction, payment tracking, reports, notifications  
- Server-driven localization (Tamil/English) via S3/backend  
- Maintains WebSocket connection during live auctions  
- Native phone dialer integration for fund manager to call defaulters  
- Camera & gallery picker for optional payment proof attachments  

**Sub-Components:**
- **AuthModule** — Login (Google OAuth, Phone OTP, Email+Password) via AWS Cognito  
- **GroupModule** — Group creation, member management, dashboard  
- **AuctionModule** — Live auction screen, WebSocket updates, bid submission, attendance tracking  
- **PaymentModule** — Payment confirmation, optional proof attachments  
- **NotificationModule** — Push notification handling (AWS SNS/FCM), in-app feed  
- **ReportModule** — In-app summaries + PDF/Excel export (via S3 presigned URL)  
- **LocalizationModule** — Fetch Tamil/English bundles from S3  

---

## 2. API Gateway Layer
**Type:** AWS API Gateway (REST + WebSocket)  

**Responsibility:**
- REST API routing to microservices (auth, group, auction, payment, notification, report)  
- WebSocket API for persistent auction connections  
- JWT validation via AWS Cognito  
- Rate limiting, throttling, CORS configuration  

---

## 3. Auth Service
**Type:** FastAPI microservice (ECS Fargate)  

**Responsibility:**
- Integrates with AWS Cognito (Google OAuth, Phone OTP, Email+Password)  
- JWT issuance and validation  
- Role management (Fund Manager, Group Member, Bot Agent)  
- User profile management (name, phone, language preference)  
- Session data in DynamoDB  

---

## 4. Group Service
**Type:** FastAPI microservice (ECS Fargate)  

**Responsibility:**
- Group lifecycle: create, configure, activate, archive  
- Parameters: member count (8–15), contribution amount, manager fee  
- Member enrollment and role assignment  
- Bot agent slot management (non-financial)  
- Tracks member status (active, won, defaulted)  
- Payment deadline configuration  
- Archival: export to S3, purge from RDS  

**Data Store:** RDS MySQL, S3 archives  

---

## 5. Auction Service
**Type:** FastAPI microservice (ECS Fargate + Lambda)  

**Responsibility:**
- Auction lifecycle: open, join, bid, close, declare winner  
- Scheduling: stores datetime, sends invites (SMS + push)  
- Attendance tracking via WebSocket registry  
- Live bid management via WebSocket API  
- Winner determination: highest bid OR random non-winner  
- Contribution calculation per member  
- Notifies Group + Payment Service  

**Data Store:** RDS MySQL, DynamoDB (connections, auction state)  

---

## 6. Payment Service
**Type:** FastAPI microservice (ECS Fargate)  

**Responsibility:**
- Tracks monthly contributions per member  
- Mandatory: fund manager confirms payments  
- Optional: members upload proof (images/docs to S3)  
- Enforces deadlines → SMS alerts for defaulters  
- Defaulter dashboard for fund manager  
- Native phone dialer integration for calls  
- Future: Razorpay/UPI integration  

**Data Store:** RDS MySQL, S3 proofs  

---

## 7. Notification Service
**Type:** FastAPI microservice (ECS Fargate + Lambda)  

**Responsibility:**
- SMS notifications via AWS SNS  
- Push notifications via SNS + FCM  
- Bot-triggered reminders (auctions, payments)  
- Async delivery via SQS queue  

**Data Store:** DynamoDB (logs, device tokens)  

---

## 8. Report Service
**Type:** AWS Lambda (Python)  

**Responsibility:**
- Generates group/member/auction reports  
- Formats: PDF + Excel (ReportLab, openpyxl)  
- Stores in S3, returns presigned URL to Flutter  

**Data Store:** S3 reports  

---

## 9. Localization Service
**Type:** AWS S3 + CloudFront  

**Responsibility:**
- Hosts Tamil/English JSON bundles  
- Flutter fetches bundles on startup or switch  
- Updates via S3 without app release  
- CDN delivery for low latency  

**Data Store:** S3 bundles  

---

## 10. Bot Agent Component
**Type:** AWS Lambda (Python, scheduled + event-driven)  

**Responsibility:**
- Registered as non-financial group member  
- Pre-auction: attendance summary via Notification Service  
- Payment reminders via EventBridge Scheduler  
- Auction deadline reminders  
- Logs bot actions per group  

**Data Store:** DynamoDB (bot logs), reads via Group/Payment services  

---

## 11. Storage Layer

| Store          | Service         | Usage |
|----------------|-----------------|-------|
| Relational DB  | AWS RDS MySQL   | Groups, members, auctions, bids, payments, users |
| NoSQL          | AWS DynamoDB    | Sessions, WebSocket state, notifications, bot logs |
| Object Storage | AWS S3          | Proofs, archives, reports, localization bundles |
| CDN            | AWS CloudFront  | Language bundles, static assets |
| Message Queue  | AWS SQS         | Async notifications |
| Event Scheduling | AWS EventBridge | Bot reminders, payment deadline checks |
