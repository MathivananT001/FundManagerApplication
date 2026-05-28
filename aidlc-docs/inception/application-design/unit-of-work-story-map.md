# 📌 Unit of Work — Story Map
**Application:** MoneyLendingManager (Chit Fund Manager)  
**Total User Stories:** 34 (US-001 – US-034)

---

## Story-to-Unit Mapping

| Story ID | Story Summary                                      | Unit                          |
|----------|----------------------------------------------------|-------------------------------|
| US-001   | User registers with email + password               | auth-service + flutter-mobile-app |
| US-002   | User logs in via phone OTP                         | auth-service + flutter-mobile-app |
| US-003   | User logs in via Google social login               | auth-service + flutter-mobile-app |
| US-004   | User manages profile and language preference       | auth-service + flutter-mobile-app |
| US-005   | Fund manager creates a new chit fund group         | group-service + flutter-mobile-app |
| US-006   | Fund manager adds/invites members to group         | group-service + flutter-mobile-app |
| US-007   | System calculates targeting amount                 | group-service |
| US-008   | System calculates monthly auction amount           | group-service |
| US-009   | Fund manager configures monthly payment deadline   | group-service + flutter-mobile-app |
| US-010   | Fund manager closes and archives a group           | group-service |
| US-011   | Fund manager opens and closes a monthly auction    | auction-service + flutter-mobile-app |
| US-012   | Members place live bids during auction             | auction-service + flutter-mobile-app |
| US-013   | System determines highest-bid winner               | auction-service |
| US-014   | System randomly selects winner when no bids placed | auction-service |
| US-015   | System calculates winner payout                    | auction-service |
| US-016   | Bot reports pre-auction member attendance          | auction-service + notification-service |
| US-017   | System tracks monthly contributions per member     | payment-service |
| US-018   | Fund manager marks payment as received             | payment-service + flutter-mobile-app |
| US-019   | Member attaches payment proof (image/camera)       | payment-service + flutter-mobile-app |
| US-020   | System stores payment proof in S3                  | payment-service |
| US-021   | Fund manager views unpaid members dashboard        | payment-service + flutter-mobile-app |
| US-022   | Fund manager calls defaulting member from app      | payment-service + flutter-mobile-app |
| US-023   | Bot sends auction deadline reminders (push + SMS)  | notification-service |
| US-024   | Bot sends payment due date reminders (push + SMS)  | notification-service |
| US-025   | System notifies fund manager of payment default    | notification-service |
| US-026   | System notifies defaulting member of missed payment| notification-service |
| US-027   | App fetches UI strings for Tamil/English from S3   | notification-service + flutter-mobile-app |
| US-028   | Fund manager views in-app group summary report     | report-service + flutter-mobile-app |
| US-029   | User views in-app member contribution history      | report-service + flutter-mobile-app |
| US-030   | User exports group report as PDF or Excel          | report-service + flutter-mobile-app |
| US-031   | REST API routes all HTTP requests to microservices | api-gateway-layer |
| US-032   | WebSocket API manages real-time auction bidding    | api-gateway-layer + auction-service |
| US-033   | Infrastructure: RDS, DynamoDB, S3 provisioning     | storage-infrastructure |
| US-034   | Infrastructure: IAM, VPC, CloudWatch setup         | storage-infrastructure |

---

## Stories by Unit

### storage-infrastructure
- US-033 — RDS MySQL, DynamoDB, S3 provisioning  
- US-034 — IAM, VPC, CloudWatch setup  

### auth-service
- US-001 — Email + password registration  
- US-002 — Phone OTP login  
- US-003 — Google social login  
- US-004 — Profile and language preference management  

### notification-service
- US-023 — Auction deadline reminders  
- US-024 — Payment due date reminders  
- US-025 — Fund manager default notification  
- US-026 — Member default notification  
- US-027 — Server-driven localization (Tamil/English)  

### group-service
- US-005 — Group creation  
- US-006 — Member enrollment  
- US-007 — Targeting amount calculation  
- US-008 — Monthly auction amount calculation  
- US-009 — Payment deadline configuration  
- US-010 — Group archival  

### payment-service
- US-017 — Monthly contribution tracking  
- US-018 — Manual payment confirmation  
- US-019 — Payment proof attachment  
- US-020 — S3 storage of payment proof  
- US-021 — Unpaid members dashboard  
- US-022 — Direct call to defaulting member  

### auction-service
- US-011 — Open/close monthly auction  
- US-012 — Live bid placement  
- US-013 — Highest-bid winner determination  
- US-014 — Random winner selection (no bids)  
- US-015 — Winner payout calculation  
- US-016 — Pre-auction attendance report  

### report-service
- US-028 — In-app group summary report  
- US-029 — In-app member history view  
- US-030 — Exportable PDF/Excel reports  

### api-gateway-layer
- US-031 — REST API routing  
- US-032 — WebSocket API for live auction  

### flutter-mobile-app
- US-001 through US-030 (all end-user-facing stories)  

---

## Story Count Summary

| Unit                  | Story Count |
|-----------------------|-------------|
| storage-infrastructure| 2 |
| auth-service          | 4 |
| notification-service  | 5 |
| group-service         | 6 |
| payment-service       | 6 |
| auction-service       | 6 |
| report-service        | 3 |
| api-gateway-layer     | 2 |
| flutter-mobile-app    | 30 (cross-cutting) |
| **Total unique stories** | **34** |
