# Code Summary — Unit 2: auth-service

## Generated Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entry point + health check |
| `app/config.py` | Environment-based settings (pydantic-settings) |
| `app/database.py` | SQLAlchemy engine + session factory |
| `app/models/user.py` | User + UserRole SQLAlchemy models |
| `app/schemas/auth.py` | Pydantic request/response schemas |
| `app/services/cognito.py` | AWS Cognito integration (register, login, OTP, refresh, logout) |
| `app/services/session.py` | DynamoDB session CRUD |
| `app/routes/auth.py` | 11 API endpoints |
| `app/middleware/auth.py` | JWT validation + role-based authorization |
| `tests/test_auth_routes.py` | Route handler tests (6 tests) |
| `tests/test_cognito_service.py` | Cognito service unit tests (3 tests) |
| `requirements.txt` | Pinned Python dependencies |
| `Dockerfile` | Container image for ECS Fargate |
| `docker-compose.yml` | Local dev with MySQL |
| `.env.example` | Environment variable template |
| `README.md` | Service documentation |

## Stories Completed
- ✅ US-001 — Email + password registration and login
- ✅ US-002 — Phone OTP login
- ✅ US-003 — Google social login (via Cognito Hosted UI)
- ✅ US-004 — Profile and language preference management
