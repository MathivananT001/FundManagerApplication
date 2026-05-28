# 📌 Code Generation Plan — Unit 1: storage-infrastructure

**Unit:** storage-infrastructure  
**Phase:** Foundation (Build First)  
**Stories:** US-033, US-034  
**Dependencies:** None (foundation unit)  
**Target Directory:** `MoneyLenderManagerApplication/infrastructure/`  
**Technology:** AWS CDK (Python)  

---

## Unit Context

### Responsibilities
- RDS MySQL schema design (users, groups, auctions, payments)
- DynamoDB table design (sessions, auction connections, notification logs, device tokens, bot activity)
- S3 buckets (payment proofs, reports, group archives, localization)
- Database migration scripts (initial schema)
- IAM roles/policies for service access
- VPC, security groups, networking
- CloudWatch logging/monitoring setup

### Stories Implemented
- **US-033**: RDS MySQL, DynamoDB, S3 provisioning
- **US-034**: IAM, VPC, CloudWatch setup

### Interfaces Provided to Other Units
- RDS MySQL connection endpoint → auth-service, group-service, auction-service, payment-service, report-service
- DynamoDB table ARNs → auth-service (sessions), auction-service (connections/state), notification-service (logs/tokens), bot-agent (activity log)
- S3 bucket ARNs → payment-service (proofs), report-service (reports), group-service (archives), notification-service (localization)
- VPC/Subnet IDs → all ECS Fargate services
- Security Group IDs → all services
- IAM role ARNs → all services

---

## Code Generation Steps

### Step 1: Project Structure Setup
- [x] Create `MoneyLenderManagerApplication/` root folder
- [x] Create `MoneyLenderManagerApplication/infrastructure/` CDK project structure
- [x] Initialize CDK app with `app.py`, `cdk.json`, `requirements.txt`
- [x] Create stack modules directory structure

**Files to create:**
```
MoneyLenderManagerApplication/
├── infrastructure/
│   ├── app.py
│   ├── cdk.json
│   ├── requirements.txt
│   ├── stacks/
│   │   ├── __init__.py
│   │   ├── vpc_stack.py
│   │   ├── database_stack.py
│   │   ├── storage_stack.py
│   │   ├── iam_stack.py
│   │   └── monitoring_stack.py
│   └── config/
│       └── environment.py
```

### Step 2: VPC & Networking (US-034)
- [ ] Create VPC stack with public/private/isolated subnets
- [ ] Configure NAT Gateway (single for cost savings)
- [ ] Create security groups for ECS services, RDS, and Lambda
- [ ] Output VPC ID, subnet IDs, security group IDs

### Step 3: RDS MySQL Database (US-033)
- [ ] Create RDS MySQL instance (db.t3.micro for dev, parameterized for prod)
- [ ] Configure in isolated subnet with security group
- [ ] Enable KMS encryption at rest
- [ ] Configure automated backups (7-day retention)
- [ ] Store credentials in Secrets Manager
- [ ] Output connection endpoint and secret ARN

### Step 4: DynamoDB Tables (US-033)
- [ ] Create `Sessions` table (PK: user_id, SK: session_id, TTL: 30 days)
- [ ] Create `AuctionConnections` table (PK: auction_id, SK: connection_id, TTL: 4 hours)
- [ ] Create `AuctionState` table (PK: auction_id, SK: event_timestamp)
- [ ] Create `NotificationLogs` table (PK: user_id, SK: timestamp)
- [ ] Create `DeviceTokens` table (PK: user_id, SK: token)
- [ ] Create `BotActivityLog` table (PK: group_id, SK: timestamp)
- [ ] All tables: PAY_PER_REQUEST billing mode

### Step 5: S3 Buckets (US-033)
- [ ] Create `mlm-payment-proofs` bucket (private, SSE-KMS, lifecycle rules)
- [ ] Create `mlm-reports` bucket (private, SSE-KMS, 30-day expiry for temp reports)
- [ ] Create `mlm-group-archives` bucket (private, SSE-KMS, Glacier transition after 90 days)
- [ ] Create `mlm-localization` bucket (public-read via CloudFront OAI)
- [ ] Configure CORS for presigned URL uploads on payment-proofs bucket

### Step 6: IAM Roles & Policies (US-034)
- [ ] Create ECS task execution role (shared)
- [ ] Create per-service task roles with least-privilege policies:
  - Auth Service role (Cognito, DynamoDB Sessions, RDS)
  - Group Service role (RDS, S3 archives)
  - Auction Service role (RDS, DynamoDB auction tables, API Gateway WebSocket)
  - Payment Service role (RDS, S3 proofs)
  - Notification Service role (SNS, SQS, DynamoDB notification tables)
- [ ] Create Lambda execution roles:
  - Report Service role (RDS read, S3 reports write)
  - Bot Agent role (DynamoDB bot log, invoke notification)
- [ ] Output role ARNs for downstream units

### Step 7: Monitoring & Observability (US-034)
- [ ] Create CloudWatch Log Groups for each service
- [ ] Create CloudWatch Alarms (RDS CPU, RDS connections, Lambda errors)
- [ ] Enable X-Ray tracing configuration
- [ ] Create CloudWatch Dashboard (basic metrics)

### Step 8: Database Migration Scripts
- [ ] Create initial SQL migration script with full RDS schema:
  - `users` table
  - `user_roles` table
  - `chit_groups` table
  - `group_members` table
  - `auctions` table
  - `bids` table
  - `contributions` table
  - `payment_records` table
  - `attachments` table
- [ ] Create seed data script (dev environment only)

**Files to create:**
```
MoneyLenderManagerApplication/infrastructure/
├── migrations/
│   ├── 001_initial_schema.sql
│   └── seed_data.sql
```

### Step 9: Unit Testing (CDK)
- [ ] Create CDK assertion tests for all stacks
- [ ] Test VPC configuration (subnets, NAT, security groups)
- [ ] Test RDS configuration (encryption, backup, secrets)
- [ ] Test DynamoDB table configurations (keys, TTL, billing)
- [ ] Test S3 bucket configurations (encryption, lifecycle, CORS)
- [ ] Test IAM policies (least privilege validation)

**Files to create:**
```
MoneyLenderManagerApplication/infrastructure/
├── tests/
│   ├── __init__.py
│   ├── test_vpc_stack.py
│   ├── test_database_stack.py
│   ├── test_storage_stack.py
│   ├── test_iam_stack.py
│   └── test_monitoring_stack.py
```

### Step 10: Documentation & Summary
- [ ] Create infrastructure README with deployment instructions
- [ ] Create `aidlc-docs/construction/storage-infrastructure/code/code-summary.md`
- [ ] Document all stack outputs (endpoints, ARNs, IDs)
- [ ] Document environment configuration options

---

## Final File Structure

```
MoneyLenderManagerApplication/
├── infrastructure/
│   ├── app.py                          # CDK app entry point
│   ├── cdk.json                        # CDK configuration
│   ├── requirements.txt                # Python dependencies
│   ├── config/
│   │   └── environment.py              # Environment-specific config
│   ├── stacks/
│   │   ├── __init__.py
│   │   ├── vpc_stack.py                # VPC, subnets, NAT, security groups
│   │   ├── database_stack.py           # RDS MySQL + DynamoDB tables
│   │   ├── storage_stack.py            # S3 buckets
│   │   ├── iam_stack.py                # IAM roles and policies
│   │   └── monitoring_stack.py         # CloudWatch, X-Ray
│   ├── migrations/
│   │   ├── 001_initial_schema.sql      # Full RDS schema
│   │   └── seed_data.sql               # Dev seed data
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_vpc_stack.py
│   │   ├── test_database_stack.py
│   │   ├── test_storage_stack.py
│   │   ├── test_iam_stack.py
│   │   └── test_monitoring_stack.py
│   └── README.md                       # Deployment instructions
```

---

## Story Traceability

| Story | Steps Covering It |
|-------|-------------------|
| US-033 | Steps 3, 4, 5, 8 |
| US-034 | Steps 2, 6, 7 |

---

## Notes
- All resource names will use `mlm-` prefix for MoneyLendingManager
- Environment parameterization: `dev` / `staging` / `prod`
- Region: `ap-south-1` (Mumbai, India)
- CDK context values for environment-specific sizing
- Code generated into `MoneyLenderManagerApplication/` folder (NOT in aidlc-docs/)
