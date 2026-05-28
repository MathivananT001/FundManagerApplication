# 📌 Code Generation Plan — Unit 2: auth-service

**Unit:** auth-service  
**Phase:** Core Backend Services  
**Stories:** US-001, US-002, US-003, US-004  
**Dependencies:** storage-infrastructure (RDS, DynamoDB Sessions, Cognito)  
**Target Directory:** `MoneyLenderManagerApplication/auth-service/`  
**Technology:** Python 3.11 + FastAPI + AWS Cognito  

---

## Unit Context

### Responsibilities
- User registration (email+password, phone OTP, Google OAuth)
- Login and JWT token issuance via AWS Cognito
- Token refresh and revocation
- Role-based access control (FUND_MANAGER, MEMBER, BOT)
- User profile CRUD (name, phone, language preference)
- Session management (DynamoDB)

### Stories Implemented
- **US-001**: User registers with email + password
- **US-002**: User logs in via phone OTP
- **US-003**: User logs in via Google social login
- **US-004**: User manages profile and language preference

### Interfaces Provided to Other Units
- JWT token validation middleware (used by all downstream services)
- User profile lookup (used by group-service, payment-service)
- Role validation (used by all services for authorization)

### Dependencies
- AWS Cognito User Pool (external)
- RDS MySQL `users` + `user_roles` tables
- DynamoDB `sessions` table

---

## Code Generation Steps

### Step 1: Project Structure Setup
- [ ] Create FastAPI project with standard layout
- [ ] Create `requirements.txt` with pinned dependencies
- [ ] Create `Dockerfile` for ECS Fargate deployment
- [ ] Create configuration module (env-based, no hardcoded values)

### Step 2: Database Models & Schemas
- [ ] Create SQLAlchemy models for `users` and `user_roles`
- [ ] Create Pydantic request/response schemas
- [ ] Create database connection utility

### Step 3: Cognito Integration Service
- [ ] Create Cognito client wrapper (register, login, verify OTP, Google auth)
- [ ] Create token validation utility
- [ ] Create session management (DynamoDB read/write)

### Step 4: API Routes
- [ ] POST `/auth/register` — email+password registration (US-001)
- [ ] POST `/auth/login/email` — email+password login (US-001)
- [ ] POST `/auth/login/phone` — initiate phone OTP (US-002)
- [ ] POST `/auth/login/phone/verify` — verify OTP (US-002)
- [ ] POST `/auth/login/google` — Google OAuth token exchange (US-003)
- [ ] POST `/auth/refresh` — refresh access token
- [ ] POST `/auth/logout` — revoke session
- [ ] GET `/auth/profile` — get current user profile (US-004)
- [ ] PUT `/auth/profile` — update profile (US-004)
- [ ] PUT `/auth/profile/language` — set language preference (US-004)
- [ ] POST `/auth/role` — assign role (admin only)

### Step 5: Middleware & Dependencies
- [ ] Create JWT validation dependency (FastAPI Depends)
- [ ] Create role-based authorization dependency
- [ ] Create error handling middleware

### Step 6: Unit Tests
- [ ] Test registration flow
- [ ] Test login flows (email, phone, Google)
- [ ] Test profile CRUD
- [ ] Test token validation
- [ ] Test role authorization

### Step 7: Documentation & Deployment
- [ ] Create service README
- [ ] Create `docker-compose.yml` for local development
- [ ] Create code summary in aidlc-docs

---

## Final File Structure

```
MoneyLenderManagerApplication/auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment-based configuration
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py             # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cognito.py          # AWS Cognito integration
│   │   └── session.py          # DynamoDB session management
│   ├── routes/
│   │   ├── __init__.py
│   │   └── auth.py             # API route handlers
│   └── middleware/
│       ├── __init__.py
│       └── auth.py             # JWT validation + role check
├── tests/
│   ├── __init__.py
│   ├── test_auth_routes.py
│   └── test_cognito_service.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Story Traceability

| Story | Steps Covering It |
|-------|-------------------|
| US-001 | Steps 2, 3, 4 (register + email login) |
| US-002 | Steps 3, 4 (phone OTP initiate + verify) |
| US-003 | Steps 3, 4 (Google OAuth exchange) |
| US-004 | Steps 2, 4 (profile GET/PUT + language) |

---

## Configuration (Environment Variables)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | RDS MySQL connection string |
| `AWS_REGION` | AWS region (ap-south-1) |
| `COGNITO_USER_POOL_ID` | Cognito User Pool ID |
| `COGNITO_CLIENT_ID` | Cognito App Client ID |
| `COGNITO_CLIENT_SECRET` | Cognito App Client Secret |
| `DYNAMODB_SESSIONS_TABLE` | DynamoDB sessions table name |
| `JWT_SECRET_KEY` | Secret for internal token signing |
| `ENVIRONMENT` | dev / staging / prod |
