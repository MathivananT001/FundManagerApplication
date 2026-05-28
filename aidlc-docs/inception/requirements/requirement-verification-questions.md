# 📋 Requirements Questions

---

## Question 1 of 11  
**Who are the primary users of MoneyLendingManager?**  
- Individual lenders tracking personal loans to friends/family  
- Small business owners managing loans to customers  
- Microfinance institutions or loan officers  
- All of the above (multiple user types)  
- Other — please describe  

**Answer:** 1 and 2 — Individual lenders tracking personal loans to friends/family, and Small business owners managing loans to customers  

---

## Question 2 of 11  
**What are the core features you need in MoneyLendingManager?**  
- Loan creation, repayment tracking, and balance overview  
- Loan creation, repayment tracking, interest calculation, and notifications  
- Full lending lifecycle: loan creation, interest, payments, overdue tracking, reports, and notifications  
- Basic tracker: just record loans and mark them as paid/unpaid  
- Other — please describe  

**Answer:** Self-funding group management system (Chit Fund / Auction-based).  
Core features:  
- Group creation (8–15 members)  
- Monthly auction/bidding system  
- Targeting amount calculation (members × amount per person)  
- Monthly auction amount (targeting amount ÷ no. of months)  
- Bid winner receives (auction amount - bid amount - manager fee)  
- Roles: Fund Manager, Group Members, 1 bot agent  
- User accounts with role-based access required  

---

## Question 3 of 11  
**What type of interest calculation should the system support?**  
- Simple interest only  
- Compound interest only  
- Both simple and compound interest  
- No interest — principal-only loans  
- Other — please describe  

**Answer:** Python (FastAPI)  

---

## Question 4 of 11  
**What repayment schedule options should be supported?**  
- Lump sum (full repayment at end of term)  
- Monthly installments (EMI/fixed payments)  
- Both lump sum and installment options  
- Flexible — borrower can pay any amount at any time  
- Other — please describe  

**Answer:** Mobile application focused. Target users are not highly tech-savvy — simplicity of use is key. Flutter (Mobile — iOS & Android) recommended for smooth cross-platform experience.  

---

## Question 5 of 11  
**What is your preferred frontend / user interface type?**  
- Web application (browser-based)  
- Mobile application (iOS and/or Android)  
- Both web and mobile  
- Command-line interface (CLI) only  
- Other — please describe  

**Answer:** AWS RDS (MySQL) for relational/structured data (groups, members, auctions, transactions) + AWS DynamoDB where needed (e.g. session data, real-time events, notifications).  

---

## Question 6 of 11  
**What is your preferred backend programming language / framework?**  
- Node.js (Express or NestJS)  
- Python (FastAPI or Django)  
- Java (Spring Boot)  
- Go (Gin or Echo)  
- Other — please describe  

**Answer:** AWS Cognito with: Social login (Google), Phone number (OTP-based) login, and standard email+password. Multi-method auth.  

---

## Question 7 of 11  
**What AWS database service should be used to store loan and user data?**  
- Amazon RDS (PostgreSQL) — relational, structured data  
- Amazon RDS (MySQL) — relational, structured data  
- Amazon DynamoDB — NoSQL, serverless-friendly  
- Amazon Aurora (PostgreSQL-compatible) — high performance relational  
- Other — please describe  

**Answer:** Small scale — up to 100 concurrent users (avg 50), single AWS region.  

---

## Question 8 of 11  
**How should user authentication and authorization be handled?**  
- Amazon Cognito (managed user pools with JWT tokens)  
- Custom JWT-based auth built into the backend  
- Social login only (Google/Facebook via Cognito)  
- No authentication — single-user local tool  
- Other — please describe  

**Answer:** Flexible deployment strategy: AWS Lambda + API Gateway (serverless for lightweight operations), AWS ECS Fargate (containerized services), AWS EC2 (where full control is needed). Multi-mode deployment.  

---

## Question 9 of 11  
**What AWS deployment model should the backend use?**  
- AWS Lambda + API Gateway (serverless)  
- Amazon ECS with Fargate (containerized)  
- Amazon EC2 (traditional VM-based)  
- AWS Elastic Beanstalk (managed platform)  
- Other — please describe  

**Answer:** Push notifications + SMS notifications (via AWS SNS) confirmed.  

---

## Question 10 of 11  
**Should the system send notifications for loan events (due dates, overdue, payments)?**  
- Yes — email notifications via Amazon SES  
- Yes — SMS/push notifications via Amazon SNS  
- Yes — both email (SES) and SMS/push (SNS)  
- No — no notifications needed  
- Other — please describe  

**Answer:** Simple + Exportable reports: group summary, member history in-app, and exportable reports (PDF/Excel).  
Also updating Q9: Push + SMS notifications confirmed.  

---

## Question 11 of 11  
**What reporting and analytics features are required?**  
- Basic dashboard: total lent, total collected, outstanding balance  
- Detailed reports: per-borrower history, payment schedules, overdue summaries  
- Advanced analytics: trends, charts, export to PDF/CSV  
- No reporting — just raw data visibility  
- Other — please describe  

**Answer:** Indian Rupee (INR) currency support. Multi-language UI: Tamil + English.  
