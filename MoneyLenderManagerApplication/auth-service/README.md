# MoneyLendingManager — Auth Service

## Overview
FastAPI microservice handling authentication, authorization, and user profile management via AWS Cognito.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register with email + password |
| POST | `/auth/login/email` | Login with email + password |
| POST | `/auth/login/phone` | Initiate phone OTP |
| POST | `/auth/login/phone/verify` | Verify OTP, get tokens |
| POST | `/auth/login/google` | Google OAuth (via Cognito Hosted UI) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Revoke session |
| GET | `/auth/profile` | Get current user profile |
| PUT | `/auth/profile` | Update profile |
| PUT | `/auth/profile/language` | Set language (en/ta) |
| POST | `/auth/role` | Assign role (Fund Manager only) |

## Setup

```bash
# Copy env file and configure
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8001

# Or with Docker
docker-compose up
```

## Run Tests
```bash
pytest tests/ -v
```

## Configuration
All configuration via environment variables — see `.env.example`.
