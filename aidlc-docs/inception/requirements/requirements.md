# 📌 MoneyLendingManager — Requirements Document

---

## 1. Intent Analysis Summary

| Attribute        | Value                                                                 |
|------------------|-----------------------------------------------------------------------|
| Application Name | MoneyLendingManager (Chit Fund / Self-Funding Group Manager)          |
| Clarity          | Clear                                                                 |
| Request Type     | New Application                                                       |
| Scope            | Full-stack Mobile (Android) + Backend System                         |
| Complexity       | Medium-High (auction engine, role-based access, financial calculations) |
| Depth Level      | Comprehensive                                                         |
| Domain           | Financial Services — Self-Funding Group (Chit Fund) Management        |

---

## 2. Business Overview

MoneyLendingManager is an Android-first chit fund management application designed for self-funding groups of 8–15 people. A Fund Manager creates and administers the group. Each month, a portion of the pooled fund is auctioned to group members. The member who bids the highest wins the auction and receives:

**Disbursed Amount = Auction Amount − Bid Amount − Manager Fee**

### Key Financial Formulas
- **Targeting Amount** = No. of Members × Amount per Person  
- **Monthly Auction Amount** = Targeting Amount ÷ No. of Months  
- **Winner Disbursement** = Monthly Auction Amount − Winning Bid − Manager Fee  

The application supports role-based access (Fund Manager, Group Members, and an automated Bot Agent), bilingual UI (Tamil + English), and is deployed entirely on AWS.

---

## 3. Functional Requirements

### FR-01: User Management & Authentication
- Register/login via:
  - Phone number with OTP (AWS Cognito + SMS)
  - Google Social Login (OAuth2 via AWS Cognito)
  - Email + Password (AWS Cognito)
- Role assignment: Fund Manager or Group Member
- Fund Manager can invite members via phone number or link

### FR-02: Role-Based Access Control
- **Fund Manager**: Create/manage groups, configure auctions, record bids, calculate disbursements, manage fees, generate reports  
- **Group Member**: View group details, participate in auctions, view contribution history, view auction results  
- **Bot Agent**: Automated reminders, auction initiation, alerts, status updates  

### FR-03: Group Management
- Create group with:
  - Name, description
  - Members (8–15)
  - Amount per person (INR)
  - Months = number of members
  - Manager fee (fixed/percentage)
- Auto-calculations: Targeting Amount, Monthly Auction Amount

### FR-04: Member Management
- Add/remove members
- Member profile: name, phone, contribution status
- Track monthly contributions
- Members view personal history

### FR-05: Auction Engine
- One auction per group per month
- Initiated by Fund Manager or Bot Agent
- Members submit bids within window
- Highest bidder wins
- System calculates:
  - Winning bid
  - Manager fee
  - Disbursement amount
- Configurable rule: no repeat winners in same cycle

### FR-06: Financial Calculations & Ledger
- Auto-calculate disbursement
- Maintain ledger:
  - Contributions
  - Auction results
  - Disbursements
  - Manager fees
- Ledger must be tamper-evident and auditable

### FR-07: Notifications & Reminders
- Push notifications (AWS SNS) for:
  - Auction start/end
  - Bid confirmation
  - Auction results
  - Contribution reminders
- SMS notifications for critical events
- Bot Agent dispatches automated notifications

### FR-08: Reporting & Exports
- In-app reports:
  - Group summary
  - Member history
  - Auction results
- Exportable reports (PDF/Excel):
  - Group financial statement
  - Member ledger
  - Auction history

### FR-09: Bot Agent
- Sends reminders
- Initiates auctions
- Closes auctions
- Announces winners
- Flags overdue contributions

### FR-10: Dashboard & Home Screen
- **Fund Manager Dashboard**: groups overview, auction schedule, transactions, compliance summary  
- **Member Home Screen**: group summary, auction countdown, contribution status, last auction result  

### FR-11: Multi-Language Support
- English + Tamil
- Language toggle in settings
- Notifications respect language preference

### FR-12: Currency Support
- All values in INR (₹)
- Indian numbering system formatting

---

## 4. Non-Functional Requirements

- **Performance**: ≤ 500ms response, 100 concurrent users, burst handling during auctions  
- **Availability**: 99.5% uptime, graceful error handling, ACID compliance  
- **Security**: JWT via Cognito, role-based auth, encryption at rest & transit, immutable financial records  
- **Scalability**: Lambda, ECS Fargate, EC2; DynamoDB for events; RDS MySQL for structured data  
- **Maintainability**: FastAPI backend, Flutter frontend, API versioning, CloudWatch logging  
- **Usability**: Android-first, simple UI, bilingual, Material Design 3, optimized for low digital literacy  
- **Deployment**: AWS (ap-south-1), Lambda, ECS, EC2, RDS, DynamoDB, Cognito, SNS, S3, CloudWatch  
- **Data Retention**: Financial records 7 years, user data per consent/privacy norms  

---

## 5. User Roles Summary

| Role         | Description                          | Key Capabilities                                      |
|--------------|--------------------------------------|-------------------------------------------------------|
| Fund Manager | Creates/manages chit fund group      | Create groups, initiate auctions, manage members, fees, reports |
| Group Member | Participant in chit fund group       | View group, submit bids, view history, receive notifications |
| Bot Agent    | Automated system agent               | Reminders, auto-initiate auctions, close auctions, announce results |

---

## 6. Key Domain Formulas

| Formula              | Expression                                      |
|-----------------------|------------------------------------------------|
| Targeting Amount      | No. of Members × Amount per Person              |
| Monthly Auction Amount| Targeting Amount ÷ No. of Months                |
| Winner Disbursement   | Monthly Auction Amount − Winning Bid − Manager Fee |

---

## 7. Technology Stack

| Layer             | Technology / Service                               |
|-------------------|---------------------------------------------------|
| Mobile Frontend   | Flutter (Android only)                            |
| Backend API       | Python (FastAPI)                                  |
| Authentication    | AWS Cognito (OTP, Google, Email/Password)         |
| Primary Database  | AWS RDS (MySQL)                                   |
| Secondary Database| AWS DynamoDB (events, sessions, notifications)    |
| Notifications     | AWS SNS (Push via FCM + SMS)                      |
| File Storage      | AWS S3 (report exports)                           |
| Compute           | AWS Lambda, ECS Fargate, EC2                      |
| API Layer         | AWS API Gateway                                   |
| Monitoring        | AWS CloudWatch                                    |
| Region            | Single AWS Region (India — ap-south-1 recommended)|

---

## 8. Out of Scope (MVP)

- iOS application — Phase 2  
- Payment gateway integration (Razorpay/UPI) — Phase 2  
- Web admin panel — Phase 2  
- RBI chit fund compliance — Phase 2 legal review  
- Multi-region deployment — Phase 3  
